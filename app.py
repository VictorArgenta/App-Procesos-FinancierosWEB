import os
import io
import json
import re
import time
import uuid
import markdown
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
import yfinance as yf
import anthropic
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem, Image as RLImage,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

load_dotenv()

import sys as _sys

# Ticker fijado al arrancar la aplicación. Uso: `python app.py META`. Si se
# pasa, el flujo de análisis individual salta el paso de selección de ticker
# y trabaja siempre con esa compañía durante toda la sesión.
TICKER_FIJO = (_sys.argv[1].strip().upper() if len(_sys.argv) > 1 and _sys.argv[1].strip() else None)

app = Flask(__name__)

# Branding mutable: arranca con el ticker (o el genérico) y se rellena con el
# nombre real de la compañía cuando se cargan datos de Yahoo por primera vez.
_BRANDING = {
    "empresa": TICKER_FIJO or "Vainilla Corp",
    "tenant_sufijo": TICKER_FIJO or "Vainilla Corp",
}


@app.context_processor
def _inyectar_branding():
    return {
        "TICKER_FIJO": TICKER_FIJO,
        "EMPRESA_NOMBRE": _BRANDING["empresa"],
        "TENANT_NOMBRE": _BRANDING["tenant_sufijo"],
    }

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

MODELOS_ANTHROPIC = {
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
}
MODELOS_GOOGLE = {
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
}
MODELOS_DISPONIBLES = MODELOS_ANTHROPIC | MODELOS_GOOGLE
MODELO_POR_DEFECTO = "claude-sonnet-4-6"

# Regex compartidas para detectar tablas Markdown producidas por la IA
_RE_TABLA_SEP_MD = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")
_RE_TABLA_FILA_MD = re.compile(r"^\s*\|.+\|\s*$")

# Cache en memoria para evitar re-llamar a las APIs al descargar Word
_download_cache = {}


def _normalizar_modelo(modelo):
    """Devuelve el modelo si es válido, o el modelo por defecto."""
    if modelo in MODELOS_DISPONIBLES:
        return modelo
    return MODELO_POR_DEFECTO


def _extraer_respuesta_claude(message):
    """Extrae el texto concatenado y las citas (si web_search) de Claude."""
    partes = []
    citas = []
    for block in getattr(message, "content", []) or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            t = getattr(block, "text", "") or ""
            if t:
                partes.append(t)
            for cit in getattr(block, "citations", None) or []:
                url = getattr(cit, "url", None)
                title = getattr(cit, "title", None) or url
                if url:
                    entrada = {"url": url, "title": title}
                    if entrada not in citas:
                        citas.append(entrada)
    return "".join(partes).strip(), citas


def llamar_claude_con_reintentos(prompt, max_tokens, modelo, max_reintentos=4,
                                  permitir_busqueda=False):
    """Llama a la API de Anthropic con reintentos y backoff exponencial.

    Si `permitir_busqueda` es True, activa la herramienta `web_search` nativa
    (server-side managed) para que el modelo pueda consultar internet. Devuelve
    una tupla `(texto, citas)` donde `citas` es una lista de dicts con url/title.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=0)
    errores_reintentables = (
        anthropic.APIStatusError,
        anthropic.APIConnectionError,
        anthropic.RateLimitError,
    )
    status_reintentables = {429, 500, 502, 503, 504, 529}

    extra_kwargs = {}
    if permitir_busqueda:
        extra_kwargs["tools"] = [{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
        }]

    ultimo_error = None
    for intento in range(max_reintentos):
        try:
            message = client.messages.create(
                model=modelo,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **extra_kwargs,
            )
            return _extraer_respuesta_claude(message)
        except errores_reintentables as e:
            ultimo_error = e
            status = getattr(e, "status_code", None)
            if status is not None and status not in status_reintentables:
                raise
            if intento < max_reintentos - 1:
                espera = 2 ** intento
                time.sleep(espera)
                continue
            break

    if ultimo_error is not None:
        status = getattr(ultimo_error, "status_code", None)
        if status == 529:
            raise RuntimeError(
                "El servicio de IA está sobrecargado en este momento. "
                "Por favor, inténtalo de nuevo en unos segundos."
            )
        if status == 429:
            raise RuntimeError(
                "Se ha superado el límite de peticiones a la IA. "
                "Por favor, espera un momento antes de volver a intentarlo."
            )
        raise RuntimeError(
            f"Error al comunicar con el servicio de IA: {str(ultimo_error)}"
        )


def _extraer_texto_gemini(respuesta):
    """Extrae texto de una respuesta Gemini, o relanza un error legible.

    Maneja los casos en que `response.text` falla por bloqueo de seguridad,
    truncado por `MAX_TOKENS`, o candidatos vacíos.
    """
    candidatos = getattr(respuesta, "candidates", None) or []
    if not candidatos:
        prompt_feedback = getattr(respuesta, "prompt_feedback", None)
        raise RuntimeError(
            f"Gemini no devolvió respuesta. Detalle: {prompt_feedback}"
        )

    candidato = candidatos[0]
    partes = []
    contenido = getattr(candidato, "content", None)
    if contenido and getattr(contenido, "parts", None):
        for parte in contenido.parts:
            texto_parte = getattr(parte, "text", None)
            if texto_parte:
                partes.append(texto_parte)

    texto = "".join(partes).strip()
    if texto:
        return texto

    finish_reason = getattr(candidato, "finish_reason", None)
    if finish_reason and str(finish_reason).endswith("MAX_TOKENS"):
        raise RuntimeError(
            "Gemini agotó el presupuesto de tokens antes de producir texto "
            "(probablemente por el proceso de razonamiento interno). "
            "Inténtalo de nuevo o selecciona otro modelo."
        )
    raise RuntimeError(
        f"Gemini no generó texto (finish_reason={finish_reason})."
    )


def _extraer_citas_gemini(respuesta):
    """Extrae las fuentes usadas en grounding de Google Search (Gemini)."""
    citas = []
    candidatos = getattr(respuesta, "candidates", None) or []
    if not candidatos:
        return citas
    gm = getattr(candidatos[0], "grounding_metadata", None)
    if not gm:
        return citas
    for chunk in getattr(gm, "grounding_chunks", None) or []:
        web = getattr(chunk, "web", None)
        if not web:
            continue
        url = getattr(web, "uri", None)
        title = getattr(web, "title", None) or url
        if url:
            entrada = {"url": url, "title": title}
            if entrada not in citas:
                citas.append(entrada)
    return citas


def llamar_gemini_con_reintentos(prompt, max_tokens, modelo, max_reintentos=4,
                                  permitir_busqueda=False):
    """Llama a la API de Google Gemini con reintentos y backoff exponencial.

    Si `permitir_busqueda` es True, activa grounding con Google Search para
    que Gemini consulte internet. Devuelve `(texto, citas)`.
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "No se ha configurado GOOGLE_API_KEY en el archivo .env. "
            "Añádela para usar los modelos de Google Gemini."
        )

    errores_reintentables = (
        google_exceptions.ResourceExhausted,
        google_exceptions.ServiceUnavailable,
        google_exceptions.InternalServerError,
        google_exceptions.DeadlineExceeded,
        google_exceptions.Aborted,
    )

    max_output_tokens = max(max_tokens * 4, 8192)

    # Gemini 2.5 usa `google_search`; 1.5 usaba `google_search_retrieval`.
    # Configuramos ambos como fallback silencioso.
    tools_config = None
    if permitir_busqueda:
        tools_config = [{"google_search": {}}]

    def _ejecutar(tools):
        kwargs = dict(
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": 0.7,
            },
        )
        if tools is not None:
            kwargs["tools"] = tools
        cliente = genai.GenerativeModel(modelo)
        return cliente.generate_content(prompt, **kwargs)

    ultimo_error = None
    for intento in range(max_reintentos):
        try:
            try:
                respuesta = _ejecutar(tools_config)
            except Exception as primary_err:
                # Fallback: probar el otro identificador del tool antes de reintentar
                if permitir_busqueda and "google_search_retrieval" not in str(primary_err):
                    respuesta = _ejecutar([{"google_search_retrieval": {}}])
                else:
                    raise
            texto = _extraer_texto_gemini(respuesta)
            citas = _extraer_citas_gemini(respuesta) if permitir_busqueda else []
            return texto, citas
        except errores_reintentables as e:
            ultimo_error = e
            if intento < max_reintentos - 1:
                espera = 2 ** intento
                time.sleep(espera)
                continue
            break

    if isinstance(ultimo_error, google_exceptions.ResourceExhausted):
        raise RuntimeError(
            "Se ha superado el límite de peticiones a la IA. "
            "Por favor, espera un momento antes de volver a intentarlo."
        )
    if isinstance(ultimo_error, google_exceptions.ServiceUnavailable):
        raise RuntimeError(
            "El servicio de IA está sobrecargado en este momento. "
            "Por favor, inténtalo de nuevo en unos segundos."
        )
    raise RuntimeError(
        f"Error al comunicar con el servicio de IA: {str(ultimo_error)}"
    )


def llamar_ia_con_reintentos(prompt, max_tokens, modelo, permitir_busqueda=False):
    """Despacha la llamada al proveedor de IA y devuelve (texto, citas).

    `citas` es una lista de `{'url', 'title'}`. Si `permitir_busqueda` es False
    (por defecto) la lista siempre vendrá vacía.
    """
    modelo = _normalizar_modelo(modelo)
    if modelo in MODELOS_ANTHROPIC:
        return llamar_claude_con_reintentos(
            prompt, max_tokens, modelo, permitir_busqueda=permitir_busqueda,
        )
    return llamar_gemini_con_reintentos(
        prompt, max_tokens, modelo, permitir_busqueda=permitir_busqueda,
    )


def _append_fuentes_consultadas(texto_md, citas):
    """No-op: la sección 'Fuentes consultadas' se ha retirado del informe."""
    return texto_md


def _limpiar_respuesta_ia(texto):
    """Saneamiento post-hoc de la respuesta del modelo.

    Elimina bloques de código y convierte cualquier tabla Markdown que el
    modelo haya emitido (pese a las instrucciones) en una lista con
    etiquetas claras, preservando los datos sin los caracteres `|` y `---`.
    """
    if not texto:
        return texto

    # Si el modelo introdujo una sección final de fuentes / enlaces pese a
    # las instrucciones, la eliminamos antes de seguir saneando.
    texto = re.sub(
        r"\n#{1,6}\s*(Fuentes consultadas|Fuentes|Referencias|Enlaces consultados|Bibliograf[íi]a)[^\n]*\n.*\Z",
        "",
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )

    texto = re.sub(r"```[^\n`]*\n?", "", texto)
    texto = texto.replace("```", "")

    lineas = texto.split("\n")
    resultado = []
    encabezados_tabla = None

    for linea in lineas:
        stripped = linea.strip()

        if _RE_TABLA_SEP_MD.match(stripped):
            # Fila separadora: descarta y marca que lo siguiente es cuerpo
            continue

        if _RE_TABLA_FILA_MD.match(stripped) and stripped.count("|") >= 2:
            celdas = [c.strip() for c in stripped.strip("|").split("|")]
            celdas = [c for c in celdas if c]
            if not celdas:
                continue
            if encabezados_tabla is None:
                encabezados_tabla = celdas
                continue
            if len(celdas) == len(encabezados_tabla):
                partes = [
                    f"**{h}:** {v}" for h, v in zip(encabezados_tabla, celdas)
                ]
                resultado.append("- " + " — ".join(partes))
            else:
                resultado.append("- " + " · ".join(celdas))
            continue

        # Línea fuera de tabla: reinicia el tracking de encabezados
        encabezados_tabla = None
        resultado.append(linea)

    # Colapsa múltiples líneas en blanco a una sola
    limpio = "\n".join(resultado)
    limpio = re.sub(r"\n{3,}", "\n\n", limpio).strip()
    return limpio


def obtener_datos_financieros(ticker_symbol):
    """Obtiene datos financieros de mercado para un ticker dado."""
    ticker = yf.Ticker(ticker_symbol)

    # Inicializar sesión con history antes de obtener fundamentales
    ticker.history(period="1d")

    income_stmt = ticker.income_stmt
    if income_stmt is None or income_stmt.empty:
        return None

    nombre = ticker.info.get("shortName", ticker_symbol.upper())
    moneda = (
        ticker.info.get("financialCurrency")
        or ticker.info.get("currency")
        or ""
    )
    moneda = str(moneda).upper().strip() if moneda else ""

    datos = {
        "ticker": ticker_symbol.upper(),
        "nombre": nombre,
        "moneda": moneda,
        "periodos": [],
    }

    columnas = income_stmt.columns[:4]  # Últimos 4 periodos disponibles

    for col in columnas:
        periodo = str(col.date()) if hasattr(col, "date") else str(col)

        def safe_get(df, keys):
            for key in keys:
                if key in df.index:
                    val = df.loc[key, col]
                    if val is not None and str(val) != "nan":
                        return float(val)
            return 0.0

        ingresos = safe_get(income_stmt, ["Total Revenue", "Revenue"])
        coste_ventas = safe_get(
            income_stmt,
            ["Cost Of Revenue", "Cost of Revenue", "Cost Of Goods Sold"],
        )
        margen_bruto = ingresos - coste_ventas
        gastos_operativos = safe_get(
            income_stmt,
            ["Operating Expense", "Total Operating Expenses", "Selling General And Administration"],
        )
        ebitda = safe_get(income_stmt, ["EBITDA", "Normalized EBITDA"])
        beneficio_neto = safe_get(
            income_stmt,
            ["Net Income", "Net Income Common Stockholders"],
        )

        # PyG ampliada
        ebit = safe_get(
            income_stmt,
            ["EBIT", "Operating Income", "Total Operating Income As Reported"],
        )
        da = safe_get(
            income_stmt,
            [
                "Reconciled Depreciation",
                "Depreciation And Amortization",
                "Depreciation Amortization Depletion Income Statement",
            ],
        )
        sga = safe_get(
            income_stmt,
            ["Selling General And Administration", "Selling General Administrative"],
        )
        rd = safe_get(income_stmt, ["Research And Development"])
        ingresos_financieros = safe_get(income_stmt, ["Interest Income"])
        gastos_financieros = safe_get(
            income_stmt, ["Interest Expense", "Interest Expense Non Operating"],
        )
        resultado_financiero_neto = safe_get(
            income_stmt,
            ["Net Non Operating Interest Income Expense"],
        )
        if not resultado_financiero_neto:
            resultado_financiero_neto = ingresos_financieros - gastos_financieros
        resultado_antes_impuestos = safe_get(
            income_stmt, ["Pretax Income", "Income Before Tax"],
        )
        impuestos = safe_get(
            income_stmt, ["Tax Provision", "Income Tax Expense Benefit"],
        )
        bpa_basico = safe_get(income_stmt, ["Basic EPS"])
        bpa_diluido = safe_get(income_stmt, ["Diluted EPS"])

        pct = lambda parte: round((parte / ingresos) * 100, 2) if ingresos else 0.0
        tasa_impositiva = (
            round((impuestos / resultado_antes_impuestos) * 100, 2)
            if resultado_antes_impuestos else 0.0
        )

        datos["periodos"].append(
            {
                "periodo": periodo,
                "ingresos": ingresos,
                "coste_ventas": coste_ventas,
                "margen_bruto": margen_bruto,
                "gastos_operativos": gastos_operativos,
                "ebitda": ebitda,
                "beneficio_neto": beneficio_neto,
                "pct_margen_bruto": pct(margen_bruto),
                "pct_gastos_operativos": pct(gastos_operativos),
                "pct_ebitda": pct(ebitda),
                "pct_beneficio_neto": pct(beneficio_neto),
                # Ampliación PyG
                "ebit": ebit,
                "pct_ebit": pct(ebit),
                "da": da,
                "pct_da": pct(da),
                "sga": sga,
                "pct_sga": pct(sga),
                "rd": rd,
                "pct_rd": pct(rd),
                "ingresos_financieros": ingresos_financieros,
                "gastos_financieros": gastos_financieros,
                "resultado_financiero_neto": resultado_financiero_neto,
                "resultado_antes_impuestos": resultado_antes_impuestos,
                "pct_rai": pct(resultado_antes_impuestos),
                "impuestos": impuestos,
                "tasa_impositiva": tasa_impositiva,
                "bpa_basico": bpa_basico,
                "bpa_diluido": bpa_diluido,
            }
        )

    datos["estados"] = _serializar_estados_yahoo(ticker)
    return datos


# Mapeo de orden + traducción a español por estado, alineado con la presentación
# de Yahoo Finance (es.finance.yahoo.com). Cada lista es el orden de aparición
# canónico; las filas que yfinance devuelva fuera de este mapeo se añaden al
# final manteniendo su nombre original.
_ORDEN_INCOME_STATEMENT = [
    ("Total Revenue", "Ingresos totales"),
    ("Operating Revenue", "Ingresos operativos"),
    ("Cost Of Revenue", "Coste de los ingresos"),
    ("Gross Profit", "Beneficio bruto"),
    ("Operating Expense", "Gastos operativos"),
    ("Research And Development", "Investigación y desarrollo"),
    ("Selling General And Administration", "Gastos generales y de administración"),
    ("Selling And Marketing Expense", "Gastos de ventas y marketing"),
    ("General And Administrative Expense", "Gastos generales y administrativos"),
    ("Other Operating Expenses", "Otros gastos operativos"),
    ("Operating Income", "Beneficio operativo"),
    ("Total Operating Income As Reported", "Beneficio operativo (declarado)"),
    ("Net Non Operating Interest Income Expense", "Resultado financiero neto"),
    ("Interest Income", "Ingresos por intereses"),
    ("Interest Expense", "Gastos por intereses"),
    ("Interest Income Non Operating", "Ingresos por intereses no operativos"),
    ("Interest Expense Non Operating", "Gastos por intereses no operativos"),
    ("Other Income Expense", "Otros ingresos / gastos"),
    ("Other Non Operating Income Expenses", "Otros ingresos / gastos no operativos"),
    ("Special Income Charges", "Cargos / ingresos especiales"),
    ("Gain On Sale Of Security", "Beneficio por venta de inversiones"),
    ("Pretax Income", "Beneficio antes de impuestos"),
    ("Tax Provision", "Provisión para impuestos sobre la renta"),
    ("Tax Effect Of Unusual Items", "Efecto fiscal de partidas inusuales"),
    ("Tax Rate For Calcs", "Tasa impositiva (para cálculos)"),
    ("Net Income Common Stockholders", "Beneficio neto para los accionistas comunes"),
    ("Net Income", "Beneficio neto"),
    ("Net Income Continuous Operations", "Beneficio neto de operaciones continuadas"),
    ("Net Income Discontinuous Operations", "Beneficio neto de operaciones discontinuadas"),
    ("Net Income From Continuing And Discontinued Operation", "Beneficio neto de operaciones continuadas y discontinuadas"),
    ("Net Income From Continuing Operation Net Minority Interest", "Beneficio neto de operación continua (interés minoritario neto)"),
    ("Net Income Including Noncontrolling Interests", "Beneficio neto incluyendo intereses minoritarios"),
    ("Minority Interests", "Intereses minoritarios"),
    ("Diluted NI Available To Com Stockholders", "Beneficio neto diluido para accionistas comunes"),
    ("Basic EPS", "BPA básico"),
    ("Diluted EPS", "BPA diluido"),
    ("Basic Average Shares", "Acciones medias básicas"),
    ("Diluted Average Shares", "Acciones medias diluidas"),
    ("Total Expenses", "Total gastos"),
    ("Normalized Income", "Beneficio normalizado"),
    ("Reconciled Cost Of Revenue", "Coste de los ingresos reconciliado"),
    ("Reconciled Depreciation", "Amortización reconciliada"),
    ("Total Unusual Items Excluding Goodwill", "Partidas inusuales (excl. fondo de comercio)"),
    ("Total Unusual Items", "Total partidas inusuales"),
    ("EBIT", "EBIT"),
    ("EBITDA", "EBITDA"),
    ("Normalized EBITDA", "EBITDA normalizado"),
]

_ORDEN_BALANCE_SHEET = [
    ("Total Assets", "Activos totales"),
    ("Current Assets", "Activos corrientes"),
    ("Cash Cash Equivalents And Short Term Investments", "Efectivo, equivalentes e inversiones a corto plazo"),
    ("Cash And Cash Equivalents", "Efectivo y equivalentes de efectivo"),
    ("Cash Financial", "Efectivo (financiero)"),
    ("Cash Equivalents", "Equivalentes de efectivo"),
    ("Other Short Term Investments", "Otras inversiones a corto plazo"),
    ("Receivables", "Cuentas por cobrar"),
    ("Accounts Receivable", "Cuentas por cobrar comerciales"),
    ("Other Receivables", "Otras cuentas por cobrar"),
    ("Inventory", "Existencias"),
    ("Prepaid Assets", "Pagos anticipados"),
    ("Other Current Assets", "Otros activos corrientes"),
    ("Total Non Current Assets", "Activos no corrientes"),
    ("Net PPE", "Inmovilizado material neto"),
    ("Gross PPE", "Inmovilizado material bruto"),
    ("Accumulated Depreciation", "Amortización acumulada"),
    ("Goodwill And Other Intangible Assets", "Fondo de comercio y otros intangibles"),
    ("Goodwill", "Fondo de comercio"),
    ("Other Intangible Assets", "Otros activos intangibles"),
    ("Investments And Advances", "Inversiones y anticipos"),
    ("Long Term Equity Investment", "Inversiones a largo plazo en patrimonio"),
    ("Other Non Current Assets", "Otros activos no corrientes"),
    ("Total Liabilities Net Minority Interest", "Pasivos totales (neto de intereses minoritarios)"),
    ("Current Liabilities", "Pasivos corrientes"),
    ("Payables And Accrued Expenses", "Cuentas por pagar y gastos devengados"),
    ("Payables", "Cuentas por pagar"),
    ("Accounts Payable", "Cuentas por pagar comerciales"),
    ("Current Debt And Capital Lease Obligation", "Deuda a corto plazo y arrendamientos"),
    ("Current Debt", "Deuda a corto plazo"),
    ("Current Capital Lease Obligation", "Arrendamientos a corto plazo"),
    ("Current Deferred Revenue", "Ingresos diferidos a corto plazo"),
    ("Other Current Liabilities", "Otros pasivos corrientes"),
    ("Total Non Current Liabilities Net Minority Interest", "Pasivos no corrientes (neto de intereses minoritarios)"),
    ("Long Term Debt And Capital Lease Obligation", "Deuda a largo plazo y arrendamientos"),
    ("Long Term Debt", "Deuda a largo plazo"),
    ("Long Term Capital Lease Obligation", "Arrendamientos a largo plazo"),
    ("Non Current Deferred Revenue", "Ingresos diferidos a largo plazo"),
    ("Non Current Deferred Taxes Liabilities", "Pasivos por impuestos diferidos a largo plazo"),
    ("Tradeand Other Payables Non Current", "Otras cuentas por pagar no corrientes"),
    ("Other Non Current Liabilities", "Otros pasivos no corrientes"),
    ("Total Equity Gross Minority Interest", "Patrimonio neto total"),
    ("Stockholders Equity", "Fondos propios"),
    ("Capital Stock", "Capital social"),
    ("Common Stock", "Acciones ordinarias"),
    ("Additional Paid In Capital", "Prima de emisión"),
    ("Retained Earnings", "Reservas / Beneficios acumulados"),
    ("Treasury Stock", "Acciones propias en cartera"),
    ("Gains Losses Not Affecting Retained Earnings", "Ganancias / pérdidas no afectan reservas"),
    ("Minority Interest", "Intereses minoritarios"),
    ("Total Capitalization", "Capitalización total"),
    ("Common Stock Equity", "Patrimonio en acciones ordinarias"),
    ("Net Tangible Assets", "Activos netos tangibles"),
    ("Working Capital", "Capital circulante"),
    ("Invested Capital", "Capital invertido"),
    ("Tangible Book Value", "Valor en libros tangible"),
    ("Total Debt", "Deuda total"),
    ("Net Debt", "Deuda neta"),
    ("Share Issued", "Acciones emitidas"),
    ("Ordinary Shares Number", "Número de acciones ordinarias"),
]

_ORDEN_CASHFLOW = [
    ("Operating Cash Flow", "Flujo de caja operativo"),
    ("Cash Flow From Continuing Operating Activities", "Flujo de caja de actividades operativas continuadas"),
    ("Net Income From Continuing Operations", "Beneficio neto de operaciones continuadas"),
    ("Depreciation Amortization Depletion", "Amortizaciones (D&A)"),
    ("Depreciation And Amortization", "Amortizaciones"),
    ("Deferred Income Tax", "Impuesto sobre la renta diferido"),
    ("Stock Based Compensation", "Retribución basada en acciones"),
    ("Change In Working Capital", "Variación del capital circulante"),
    ("Change In Receivables", "Variación de cuentas por cobrar"),
    ("Change In Inventory", "Variación de existencias"),
    ("Change In Payables And Accrued Expense", "Variación de cuentas por pagar y devengos"),
    ("Change In Other Current Assets", "Variación de otros activos corrientes"),
    ("Change In Other Current Liabilities", "Variación de otros pasivos corrientes"),
    ("Change In Other Working Capital", "Variación de otro capital circulante"),
    ("Other Non Cash Items", "Otras partidas no monetarias"),
    ("Investing Cash Flow", "Flujo de caja de inversión"),
    ("Cash Flow From Continuing Investing Activities", "Flujo de caja de actividades de inversión continuadas"),
    ("Capital Expenditure", "Inversiones en inmovilizado (CAPEX)"),
    ("Net PPE Purchase And Sale", "Compra / venta neta de inmovilizado"),
    ("Purchase Of PPE", "Compras de inmovilizado"),
    ("Sale Of PPE", "Ventas de inmovilizado"),
    ("Net Investment Purchase And Sale", "Compra / venta neta de inversiones"),
    ("Purchase Of Investment", "Compras de inversiones"),
    ("Sale Of Investment", "Ventas de inversiones"),
    ("Net Business Purchase And Sale", "Compra / venta neta de negocios"),
    ("Purchase Of Business", "Compras de negocios"),
    ("Sale Of Business", "Ventas de negocios"),
    ("Net Other Investing Changes", "Otras variaciones netas de inversión"),
    ("Financing Cash Flow", "Flujo de caja de financiación"),
    ("Cash Flow From Continuing Financing Activities", "Flujo de caja de actividades de financiación continuadas"),
    ("Net Issuance Payments Of Debt", "Emisiones / amortizaciones netas de deuda"),
    ("Net Long Term Debt Issuance", "Emisión neta de deuda a largo plazo"),
    ("Long Term Debt Issuance", "Emisión de deuda a largo plazo"),
    ("Long Term Debt Payments", "Amortización de deuda a largo plazo"),
    ("Net Short Term Debt Issuance", "Emisión neta de deuda a corto plazo"),
    ("Net Common Stock Issuance", "Emisión neta de acciones ordinarias"),
    ("Common Stock Issuance", "Emisión de acciones ordinarias"),
    ("Common Stock Payments", "Recompra de acciones ordinarias"),
    ("Cash Dividends Paid", "Dividendos pagados en efectivo"),
    ("Common Stock Dividend Paid", "Dividendos ordinarios pagados"),
    ("Net Other Financing Charges", "Otros cargos netos de financiación"),
    ("End Cash Position", "Saldo final de efectivo"),
    ("Beginning Cash Position", "Saldo inicial de efectivo"),
    ("Changes In Cash", "Variación neta de efectivo"),
    ("Effect Of Exchange Rate Changes", "Efecto del tipo de cambio"),
    ("Income Tax Paid Supplemental Data", "Impuesto sobre la renta pagado (info. complementaria)"),
    ("Interest Paid Supplemental Data", "Intereses pagados (info. complementaria)"),
    ("Free Cash Flow", "Flujo de caja libre"),
    ("Repurchase Of Capital Stock", "Recompra de capital social"),
    ("Issuance Of Capital Stock", "Emisión de capital social"),
    ("Issuance Of Debt", "Emisión de deuda"),
    ("Repayment Of Debt", "Amortización de deuda"),
]


def _ordenar_y_traducir_filas(df_index_to_valores, orden):
    """Devuelve la lista de filas {concepto, valores} ordenadas según `orden`.

    `df_index_to_valores` es un dict concepto_en_inglés → lista de valores.
    `orden` es la lista de tuplas (clave_yfinance, traducción_es).
    Las filas no presentes en `orden` se añaden al final con su nombre original.
    """
    en_orden = set()
    filas = []
    for clave, traduccion in orden:
        if clave in df_index_to_valores:
            filas.append({"concepto": traduccion, "valores": df_index_to_valores[clave]})
            en_orden.add(clave)
    for clave, valores in df_index_to_valores.items():
        if clave not in en_orden:
            filas.append({"concepto": clave, "valores": valores})
    return filas


def _serializar_estados_yahoo(ticker):
    """Devuelve los 3 estados financieros, traducidos al español y reordenados.

    Estructura: {nombre_estado: {"periodos": [str], "filas": [{"concepto", "valores": [float|None]}]}}.
    """
    import math
    fuentes = {
        "income_statement": (getattr(ticker, "income_stmt", None), _ORDEN_INCOME_STATEMENT),
        "balance_sheet": (getattr(ticker, "balance_sheet", None), _ORDEN_BALANCE_SHEET),
        "cashflow": (getattr(ticker, "cashflow", None), _ORDEN_CASHFLOW),
    }
    salida = {}
    for clave, (df, orden) in fuentes.items():
        if df is None or df.empty:
            salida[clave] = {"periodos": [], "filas": []}
            continue
        cols = list(df.columns[:4])
        periodos = [str(c.date()) if hasattr(c, "date") else str(c) for c in cols]
        crudo = {}
        for concepto in df.index:
            valores = []
            for col in cols:
                v = df.loc[concepto, col]
                if v is None:
                    valores.append(None)
                    continue
                try:
                    vf = float(v)
                    valores.append(None if math.isnan(vf) else vf)
                except (TypeError, ValueError):
                    valores.append(None)
            if any(v is not None for v in valores):
                crudo[str(concepto)] = valores
        filas = _ordenar_y_traducir_filas(crudo, orden)
        salida[clave] = {"periodos": periodos, "filas": filas}
    return salida


def _texto_datos_para_prompt(datos):
    """Genera el bloque de datos financieros para inyectar en prompts."""
    moneda = datos.get("moneda") or ""
    etiqueta_moneda = f" (moneda de reporting: {moneda})" if moneda else ""
    texto = f"Empresa: {datos['nombre']} ({datos['ticker']}){etiqueta_moneda}\n\n"
    for p in datos["periodos"]:
        texto += (
            f"Periodo: {p['periodo']}\n"
            f"  Ingresos: {p['ingresos']:,.0f}\n"
            f"  Coste de ventas: {p['coste_ventas']:,.0f}\n"
            f"  Margen bruto: {p['margen_bruto']:,.0f} ({p['pct_margen_bruto']}%)\n"
            f"  Gastos operativos: {p['gastos_operativos']:,.0f} ({p['pct_gastos_operativos']}%)\n"
            f"    - SG&A: {p.get('sga', 0):,.0f} ({p.get('pct_sga', 0)}%)\n"
            f"    - I+D: {p.get('rd', 0):,.0f} ({p.get('pct_rd', 0)}%)\n"
            f"  EBITDA: {p['ebitda']:,.0f} ({p['pct_ebitda']}%)\n"
            f"  D&A (amortizaciones): {p.get('da', 0):,.0f} ({p.get('pct_da', 0)}%)\n"
            f"  EBIT (resultado de explotación): {p.get('ebit', 0):,.0f} ({p.get('pct_ebit', 0)}%)\n"
            f"  Resultado financiero neto: {p.get('resultado_financiero_neto', 0):,.0f}"
            f" (ingresos fin.: {p.get('ingresos_financieros', 0):,.0f}, gastos fin.: {p.get('gastos_financieros', 0):,.0f})\n"
            f"  Resultado antes de impuestos: {p.get('resultado_antes_impuestos', 0):,.0f} ({p.get('pct_rai', 0)}%)\n"
            f"  Impuesto sobre beneficios: {p.get('impuestos', 0):,.0f}"
            f" (tasa efectiva: {p.get('tasa_impositiva', 0)}%)\n"
            f"  Beneficio neto: {p['beneficio_neto']:,.0f} ({p['pct_beneficio_neto']}%)\n"
            f"  BPA básico: {p.get('bpa_basico', 0)} | BPA diluido: {p.get('bpa_diluido', 0)}\n"
        )

    estados = datos.get("estados") or {}
    nombres = {
        "income_statement": "Estado de Ingresos (income statement)",
        "balance_sheet": "Balance General (balance sheet)",
        "cashflow": "Flujo de Caja (cashflow)",
    }
    for clave, titulo in nombres.items():
        bloque = estados.get(clave) or {}
        filas = bloque.get("filas") or []
        periodos = bloque.get("periodos") or []
        if not filas or not periodos:
            continue
        texto += f"\n--- {titulo} (datos brutos de Yahoo Finance) ---\n"
        texto += "Concepto | " + " | ".join(periodos) + "\n"
        for fila in filas:
            valores_txt = []
            for v in fila["valores"]:
                if v is None:
                    valores_txt.append("n/d")
                elif abs(v) >= 1:
                    valores_txt.append(f"{v:,.0f}")
                else:
                    valores_txt.append(f"{v:.4f}")
            texto += f"{fila['concepto']} | " + " | ".join(valores_txt) + "\n"
    return texto


# Bloque compartido con el ALCANCE del documento. Fija la perspectiva
# (memoria explicativa de la PyG para accionistas) y veta contenido de tesis
# de inversión.
_ALCANCE_MEMORIA = """ALCANCE Y PÚBLICO DEL DOCUMENTO (fundamental, no te desvíes):
- Eres un analista financiero que redacta la NOTA EXPLICATIVA de la cuenta
  de Pérdidas y Ganancias (PyG) que forma parte de las cuentas anuales que
  la compañía publica para sus accionistas.
- El lector es un accionista que quiere entender cómo ha ido la compañía
  en los ejercicios presentados y qué cabe esperar cualitativamente en los
  próximos ejercicios (drivers de negocio, tendencias, riesgos operativos).
- ESTO NO ES UNA TESIS DE INVERSIÓN. Está PROHIBIDO incluir:
  · Recomendaciones de compra, venta o mantenimiento.
  · Objetivos de precio o rangos de valoración.
  · Múltiplos de mercado (P/E, EV/EBITDA…), DCF, comparables cotizados.
  · Análisis técnico, rating, price target ni opinión bursátil.
- SÍ debes incluir: evolución interanual de ingresos, márgenes y resultado;
  drivers cualitativos que explican la variación; perspectivas cualitativas
  sobre el comportamiento del negocio; riesgos y fortalezas operativas."""


# Reglas de formato compartidas entre generación inicial y chat.
_REGLAS_FORMATO_MEMORIA = """Reglas de formato OBLIGATORIAS (bajo ningún concepto las infrinjas):
- PROHIBIDO usar tablas Markdown: no escribas NUNCA los caracteres `|`, `---` o `:---:`.
- En lugar de tablas, usa listas con guion `-` y negritas para las etiquetas, por ejemplo:
  `- **FY2024:** ingresos de 60.922 M USD (+125,8% interanual).`
- NO uses bloques de código ni acentos graves triples.
- PROHIBIDO incluir gráficos, charts, dashboards, diagramas, esquemas visuales,
  ASCII art o cualquier representación visual de datos. Tampoco uses frases del
  tipo "ver gráfico", "como muestra el dashboard", "véase la figura", "según el
  panel". La nota es ÚNICAMENTE texto en prosa profesional: todo análisis
  cuantitativo debe expresarse con cifras dentro del párrafo o en listas con guion.
- Estructura el contenido con encabezados Markdown `## Sección` y `### Subsección`.
- Usa párrafos en prosa profesional; resalta términos clave con `**negrita**` (uno o dos por párrafo).
- Cifras siempre con separadores de miles y unidades (millones / %).
- Asegúrate de cerrar todas las secciones de forma natural. Si NO hay un enfoque
  estricto definido por el usuario, cierra con una sección "## Conclusión". Si
  hay un enfoque estricto, NO añadas conclusión genérica ni secciones extra:
  el cierre debe ser una o dos frases finales sobre el enfoque pedido y nada más."""


_TIPOS_INFORME = {
    "nota_memoria": (
        "NOTA DE MEMORIA contable: documento formal que acompaña a las cuentas "
        "anuales para los accionistas, lenguaje técnico-contable pero accesible, "
        "evita opiniones de inversión."
    ),
    "consejo": (
        "INFORME AL CONSEJO de Administración: tono ejecutivo, foco en decisiones "
        "y palancas de gestión, destaca riesgos y oportunidades; estructura tipo "
        "executive summary + análisis + recomendaciones implícitas (no inversión)."
    ),
    "interno": (
        "INFORME INTERNO de management: orientado al equipo financiero, tono "
        "operativo y directo, sin perífrasis; puede entrar en detalle de variaciones "
        "y métricas operativas."
    ),
    "accionista": (
        "EXPLICACIÓN AL ACCIONISTA minorista: lenguaje claro y didáctico, evita "
        "jerga contable salvo definiéndola, foco en ‘qué significa esto para mí’ "
        "sin convertirse en recomendación de inversión."
    ),
}

_EXTENSIONES = {
    "breve": ("aproximadamente 400-500 palabras", 1800),
    "estandar": ("aproximadamente 800-1000 palabras", 4000),
    "extensa": ("aproximadamente 1500-2000 palabras", 6500),
}


def _bloque_configuracion_informe(tipo_informe, enfoque, extension):
    partes = []
    if tipo_informe and tipo_informe in _TIPOS_INFORME:
        partes.append(f"TIPO DE INFORME REQUERIDO: {_TIPOS_INFORME[tipo_informe]}")
    if enfoque and enfoque.strip():
        partes.append(
            "ENFOQUE ESTRICTO DEL INFORME (CRÍTICO, no lo amplíes):\n"
            f"{enfoque.strip()}\n\n"
            "REGLAS DE ALCANCE — son OBLIGATORIAS y prevalecen sobre cualquier\n"
            "convención de estructura habitual de notas de memoria o informes:\n"
            "- El documento debe limitarse EXCLUSIVAMENTE al enfoque indicado arriba.\n"
            "- NO añadas secciones como 'Perspectivas cualitativas', 'Riesgos',\n"
            "  'Resumen ejecutivo', 'Evolución general del negocio', 'Contexto sectorial',\n"
            "  'Conclusión', 'Recomendaciones' u otras secciones genéricas, salvo que\n"
            "  el propio enfoque las pida.\n"
            "- NO traigas magnitudes financieras ajenas al enfoque (p. ej. si el enfoque\n"
            "  es BPA, no hables de margen bruto, deuda, caja ni de operaciones que no\n"
            "  afecten directamente al BPA), salvo cuando sean estrictamente necesarias\n"
            "  para explicar el enfoque, y siempre en una sola frase de contexto.\n"
            "- El cierre del documento es una o dos frases finales sobre el enfoque\n"
            "  pedido; NO abras nuevos temas en el cierre.\n"
            "- Si la información disponible sobre el enfoque es escasa, redacta un\n"
            "  documento más breve antes que rellenarlo con apartados fuera de alcance."
        )
    if extension and extension in _EXTENSIONES:
        descripcion, _ = _EXTENSIONES[extension]
        partes.append(
            f"EXTENSIÓN OBJETIVO: {descripcion}. Si el enfoque no da para esa "
            "extensión, prioriza la regla de alcance sobre la de extensión y "
            "entrega un documento más corto."
        )
    if not partes:
        return ""
    return "\n\n" + "\n\n".join(partes) + "\n"


def generar_nota_memoria(datos, modelo, instrucciones_usuario=None,
                          permitir_busqueda=False,
                          tipo_informe=None, enfoque=None, extension=None):
    """Genera el informe narrativo a partir de los estados financieros.

    - `instrucciones_usuario`: texto libre que el usuario añade para orientar
      el tono, las secciones o el foco del informe.
    - `permitir_busqueda`: si es True, la IA puede consultar noticias recientes
      del sector en internet y citarlas en una sección final.
    - `tipo_informe`: clave de `_TIPOS_INFORME` que ajusta el registro y la
      audiencia objetivo del documento.
    - `enfoque`: texto libre que describe en qué parte de los estados se debe
      concentrar el análisis (puede mezclar selecciones predefinidas y texto
      libre del usuario).
    - `extension`: clave de `_EXTENSIONES` (breve / estandar / extensa).
    """
    tabla_texto = _texto_datos_para_prompt(datos)

    bloque_config = _bloque_configuracion_informe(tipo_informe, enfoque, extension)

    bloque_instrucciones = ""
    if instrucciones_usuario and instrucciones_usuario.strip():
        bloque_instrucciones = (
            "\n\nIndicaciones específicas del usuario (tienen PRIORIDAD sobre las "
            "decisiones por defecto, siempre que no contradigan el alcance ni las "
            "reglas de formato):\n"
            f"{instrucciones_usuario.strip()}\n"
        )

    bloque_busqueda = ""
    if permitir_busqueda:
        bloque_busqueda = (
            "\nCONTEXTO EXTERNO: tienes disponible una herramienta de búsqueda web. "
            "Úsala con criterio para localizar noticias relevantes de los últimos 12 "
            "meses sobre la compañía o su sector que ayuden a explicar la evolución "
            "del negocio. Incorpóralas en el cuerpo del informe como **hechos** "
            "(no como opinión), y asegúrate de que el análisis financiero siga "
            "siendo el centro del documento.\n"
        )

    max_tokens = _EXTENSIONES.get(extension or "", (None, 4000))[1]

    prompt = f"""{_ALCANCE_MEMORIA}

{_REGLAS_FORMATO_MEMORIA}{bloque_config}{bloque_instrucciones}{bloque_busqueda}
Datos financieros sobre los que elaborar el informe:
{tabla_texto}"""

    texto, citas = llamar_ia_con_reintentos(
        prompt, max_tokens=max_tokens, modelo=modelo,
        permitir_busqueda=permitir_busqueda,
    )
    memoria = _limpiar_respuesta_ia(texto)
    return _append_fuentes_consultadas(memoria, citas)


_RE_BLOQUE_RESPUESTA = re.compile(r"\[RESPUESTA\]\s*\n(.+?)(?=\n\[MEMORIA\]|\Z)", re.DOTALL)
_RE_BLOQUE_MEMORIA = re.compile(r"\[MEMORIA\]\s*\n(.+)", re.DOTALL)


def _parsear_respuesta_chat(texto_crudo):
    """Separa la respuesta conversacional y la memoria actualizada."""
    if not texto_crudo:
        return "", None
    m_mem = _RE_BLOQUE_MEMORIA.search(texto_crudo)
    memoria_nueva = None
    if m_mem:
        memoria_nueva = _limpiar_respuesta_ia(m_mem.group(1).strip())
        texto_restante = texto_crudo[: m_mem.start()]
    else:
        texto_restante = texto_crudo

    m_resp = _RE_BLOQUE_RESPUESTA.search(texto_restante)
    if m_resp:
        respuesta = m_resp.group(1).strip()
    else:
        # Sin etiquetas: si no hay memoria nueva lo tratamos todo como chat
        respuesta = texto_restante.strip()
    # Truncamos la respuesta conversacional a algo razonable
    if len(respuesta) > 1200:
        respuesta = respuesta[:1200].rsplit(".", 1)[0] + "…"
    return respuesta, memoria_nueva


def refinar_memoria_con_chat(datos, memoria_actual, historial, mensaje_usuario,
                              instrucciones_iniciales, modelo,
                              permitir_busqueda=False):
    """Ejecuta un turno de chat para refinar la memoria.

    Devuelve `(respuesta_chat, memoria_nueva_o_None, citas)`.
    """
    tabla_texto = _texto_datos_para_prompt(datos)

    historial_txt = ""
    for turno in historial:
        rol = "Usuario" if turno.get("role") == "user" else "Asistente"
        historial_txt += f"\n{rol}: {turno.get('content', '').strip()}"

    instrucciones_bloque = ""
    if instrucciones_iniciales and instrucciones_iniciales.strip():
        instrucciones_bloque = (
            "\nInstrucciones iniciales del usuario (al generar la memoria por primera vez):\n"
            f"{instrucciones_iniciales.strip()}\n"
        )

    bloque_busqueda = ""
    if permitir_busqueda:
        bloque_busqueda = (
            "\nEn este turno el usuario te permite consultar noticias recientes en "
            "internet. Úsalo si aporta a la memoria (p. ej. noticias del sector de "
            "los últimos 12 meses relevantes para explicar la evolución).\n"
        )

    prompt = f"""{_ALCANCE_MEMORIA}

Colaboras con el usuario para refinar la NOTA EXPLICATIVA de la PyG ya
generada. El usuario te pide ajustes, ampliaciones o cambios de enfoque;
aplica esos cambios CONSERVANDO el alcance descrito arriba.

{_REGLAS_FORMATO_MEMORIA}
{bloque_busqueda}
Datos financieros de referencia:
{tabla_texto}
{instrucciones_bloque}
MEMORIA ACTUAL:
---
{memoria_actual.strip()}
---
{historial_txt}

Nueva petición del usuario:
{mensaje_usuario.strip()}

RESPONDE ESTRICTAMENTE con este formato exacto (sin texto adicional fuera de las etiquetas):

[RESPUESTA]
(1 o 2 frases en español explicando qué cambios has aplicado a la memoria.)

[MEMORIA]
(la MEMORIA COMPLETA ACTUALIZADA en markdown, respetando las reglas de formato.
Si el usuario no pide cambios en la memoria, repite la memoria actual tal cual.
NO añadas una sección de fuentes / enlaces al final: el informe debe terminar
en la conclusión narrativa, sin listado de URLs ni "Fuentes consultadas".)"""

    texto, citas = llamar_ia_con_reintentos(
        prompt, max_tokens=4500, modelo=modelo,
        permitir_busqueda=permitir_busqueda,
    )
    respuesta, memoria_nueva = _parsear_respuesta_chat(texto)
    if not respuesta:
        respuesta = "Memoria actualizada."
    return respuesta, memoria_nueva, citas


# Nombre del sistema externo simulado para la detección de incoherencias.
SISTEMA_NOTA_OFICIAL = "Workiva"


def _extraer_json_incoherencias(texto_crudo):
    """Localiza el primer array JSON en la respuesta y lo parsea.

    El LLM a veces envuelve el JSON en prosa o en un bloque ```json```;
    aceptamos cualquiera de esas variantes.
    """
    if not texto_crudo:
        return []
    texto = texto_crudo.strip()
    # Bloque ```json ... ```
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", texto, re.DOTALL)
    if m:
        candidato = m.group(1)
    else:
        # Primer array que aparezca en el texto
        m2 = re.search(r"\[\s*\{.*\}\s*\]", texto, re.DOTALL)
        candidato = m2.group(0) if m2 else texto
    try:
        data = json.loads(candidato)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    incoherencias = []
    for item in data:
        if not isinstance(item, dict):
            continue
        incoherencias.append({
            "tipo": str(item.get("tipo", "")).strip() or "Discrepancia",
            "severidad": str(item.get("severidad", "")).strip().lower() or "media",
            "informe": str(item.get("informe", "")).strip() or "Informe corporativo",
            "extracto_ia": str(item.get("extracto_ia", "")).strip(),
            "extracto_oficial": str(item.get("extracto_oficial", "")).strip(),
            "explicacion": str(item.get("explicacion", "")).strip(),
        })
    return incoherencias


# Catálogo de informes narrativos simulados disponibles en el repositorio
# corporativo. El LLM debe atribuir cada incoherencia a uno de estos
# documentos para que la simulación sea coherente.
_INFORMES_WORKIVA = [
    "Informe de gestión",
    "Informe al consejo de administración",
    "Informe de evolución del negocio",
    "Informe trimestral de resultados",
    "Memoria abreviada de cuentas anuales",
    "Presentación a inversores",
    "Informe de auditoría interna",
    "Comentario de la dirección sobre los resultados (MD&A)",
]


def detectar_incoherencias_memoria(datos, memoria, modelo):
    """Simula la detección de incoherencias entre la nota IA y un conjunto
    de informes narrativos corporativos almacenados en Workiva.

    Los informes no existen: pedimos al LLM que invente entre 4 y 6
    discrepancias verosímiles, ancladas en los datos y el texto reales,
    y atribuya cada una a un informe distinto del catálogo simulado.
    """
    tabla_texto = _texto_datos_para_prompt(datos)
    memoria_trunc = (memoria or "").strip()
    if len(memoria_trunc) > 6000:
        memoria_trunc = memoria_trunc[:6000] + "\n[...]"

    catalogo_informes = "\n".join(f"  - {n}" for n in _INFORMES_WORKIVA)

    prompt = f"""Eres un revisor financiero senior. Estás comparando la NOTA EXPLICATIVA
de la cuenta de Pérdidas y Ganancias generada automáticamente por IA contra
un CONJUNTO DE INFORMES NARRATIVOS CORPORATIVOS almacenados en el repositorio
{SISTEMA_NOTA_OFICIAL}. Cada informe del repositorio aborda, total o
parcialmente, la misma información financiera que la nota IA, pero ha sido
redactado por equipos distintos (dirección financiera, auditoría, relaciones
con inversores, etc.), por lo que es habitual encontrar pequeñas
divergencias entre ellos.

CATÁLOGO DE INFORMES DEL REPOSITORIO (SIMULADO — escoge entre estos nombres
literales para el campo "informe", usa AL MENOS 3 informes distintos a lo
largo de las incoherencias que reportes):
{catalogo_informes}

Tu tarea: identificar entre 4 y 6 incoherencias VEROSÍMILES entre la nota
IA y los distintos informes del repositorio. Cada incoherencia debe estar
ANCLADA en los datos financieros y en el texto real de la versión IA (cita
extractos cortos exactos de la versión IA). La redacción del informe
corporativo es SIMULADA: invéntala con sentido financiero — cifras parecidas
pero ligeramente distintas, otro número de decimales, otro driver atribuido,
otro año destacado, otro signo de tendencia, otro reparto del margen, etc.
Asegúrate de que el extracto del informe es ESTILÍSTICAMENTE COHERENTE con
el tipo de informe del que procede (p. ej. el "Informe al consejo" usa tono
ejecutivo y agregado; la "Presentación a inversores" es más promocional;
el "Informe de auditoría interna" es más técnico y prudente).

Tipos de incoherencia que debes cubrir (al menos 3 tipos distintos entre las
4-6 que reportes):
- "Cifra": las dos versiones reportan un importe diferente para la misma
  métrica (p. ej. ingresos FY2024).
- "Decimales": misma magnitud con distinta precisión (1 vs 2 decimales, o
  redondeo distinto).
- "Driver": ambas atribuyen la variación a causas distintas (p. ej. la IA
  habla de tipo de cambio y el informe corporativo de volumen).
- "Periodo": una destaca otro ejercicio como pico o valle.
- "Signo/tendencia": una habla de mejora interanual y la otra de empeoramiento
  marginal.
- "Unidad/escala": miles vs millones, o moneda local vs reporting.

DEVUELVE EXCLUSIVAMENTE un array JSON válido (sin texto fuera del array, sin
bloques de código markdown). Cada elemento del array tiene exactamente estas
claves:
  - "tipo": una de las categorías de arriba (string corto).
  - "severidad": "alta" | "media" | "baja".
  - "informe": nombre LITERAL del informe del catálogo de arriba.
  - "extracto_ia": fragmento literal (máx 220 caracteres) de la versión IA.
  - "extracto_oficial": fragmento inventado (máx 220 caracteres) tal como
    aparecería en el informe corporativo indicado.
  - "explicacion": 1-2 frases explicando por qué difieren y qué implicación
    tiene para el lector.

Datos financieros (referencia común a todos los documentos):
{tabla_texto}

VERSIÓN IA (íntegra):
{memoria_trunc}
"""

    texto, _citas = llamar_ia_con_reintentos(
        prompt, max_tokens=2500, modelo=modelo, permitir_busqueda=False,
    )
    return _extraer_json_incoherencias(texto)


def generar_analisis_comparativo(datos_empresas, modelo):
    """Genera un análisis comparativo de hasta 3 empresas con el modelo elegido."""
    texto = ""
    for datos in datos_empresas:
        texto += f"\n{'='*50}\nEmpresa: {datos['nombre']} ({datos['ticker']})\n"
        for p in datos["periodos"][:1]:  # Último periodo para comparar
            texto += f"""Periodo más reciente: {p['periodo']}
  Ingresos: {p['ingresos']:,.0f}
  Coste de ventas: {p['coste_ventas']:,.0f}
  Margen bruto: {p['margen_bruto']:,.0f} ({p['pct_margen_bruto']}%)
  Gastos operativos: {p['gastos_operativos']:,.0f} ({p['pct_gastos_operativos']}%)
  EBITDA: {p['ebitda']:,.0f} ({p['pct_ebitda']}%)
  Beneficio neto: {p['beneficio_neto']:,.0f} ({p['pct_beneficio_neto']}%)
"""

    prompt = f"""Eres un analista financiero experto. Genera un análisis comparativo detallado
en español de las siguientes empresas. Compara sus métricas financieras, identifica
cuál tiene mejor rendimiento en cada categoría, analiza las diferencias en márgenes
y rentabilidad, y ofrece una conclusión sobre cuál presenta mejor salud financiera.

Reglas de formato OBLIGATORIAS (bajo ningún concepto las infrinjas):
- PROHIBIDO usar tablas Markdown: no escribas NUNCA los caracteres `|`, `---` o `:---:`.
- En lugar de tablas, usa listas con guion `-` y negritas para las etiquetas, por ejemplo:
  `- **Margen bruto:** Empresa A 45,2% vs Empresa B 38,1%.`
- NO uses bloques de código ni acentos graves triples.
- Estructura el contenido con encabezados Markdown `## Sección` y `### Subsección`.
- Usa párrafos en prosa profesional; resalta términos clave con `**negrita**` (uno o dos por párrafo).
- Cifras siempre con separadores de miles y unidades (millones / %).
- Asegúrate de cerrar todas las secciones: termina con una sección final de "## Conclusión".

Datos financieros comparativos:
{texto}"""

    texto, _citas = llamar_ia_con_reintentos(prompt, max_tokens=5000, modelo=modelo)
    return _limpiar_respuesta_ia(texto)


_RE_INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def _añadir_runs_con_formato(paragraph, texto):
    """Añade runs al párrafo aplicando **negrita**, *cursiva* y `código`."""
    for parte in _RE_INLINE.split(texto):
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**") and len(parte) > 4:
            run = paragraph.add_run(parte[2:-2])
            run.bold = True
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            run = paragraph.add_run(parte[1:-1])
            run.italic = True
        elif parte.startswith("`") and parte.endswith("`") and len(parte) > 2:
            run = paragraph.add_run(parte[1:-1])
            run.font.name = "Consolas"
        else:
            paragraph.add_run(parte)


# ---------------------------------------------------------------------------
# Segmentación de la nota y asignación de gráficos por sección.
# Los documentos Word/PDF (y la vista web) intercalan los gráficos después de
# la sección ## cuyos títulos contengan determinadas palabras clave.
# ---------------------------------------------------------------------------

# Paleta corporativa Deloitte (matplotlib)
_MPL_GREEN = "#86BC25"
_MPL_GREEN_DARK = "#43B02A"
_MPL_BLACK = "#000000"
_MPL_GRAY = "#53565A"
_MPL_ORANGE = "#ED8B00"

_CHART_KEYWORDS = {
    "ingresos": ("ingresos", "facturación", "revenue", "ventas", "volumen de negocio", "cifra de negocio"),
    "margenes": ("margen", "márgenes", "rentabilidad", "ebitda", "beneficio"),
    "estructura": ("coste", "costes", "estructura", "gasto"),
    "metricas": ("métrica", "ratios", "clave", "kpi", "resumen", "magnitudes", "indicadores"),
}

_RE_H2 = re.compile(r"^\s*##\s+(.*?)\s*$")


def _segmentar_memoria(texto):
    """Divide la nota de memoria en secciones por encabezados `## `.

    Devuelve una lista de dicts `{title, body}`. Si el texto contiene
    contenido previo al primer `##`, ese bloque se agrupa como preámbulo
    sin título.
    """
    if not texto:
        return []

    lineas = texto.replace("\r\n", "\n").split("\n")
    secciones = []
    preambulo = []
    actual_title = None
    actual_body = []

    def _cerrar():
        nonlocal actual_title, actual_body
        if actual_title is not None:
            secciones.append({
                "title": actual_title,
                "body": "\n".join(actual_body).strip(),
            })
        actual_title = None
        actual_body = []

    for linea in lineas:
        m = _RE_H2.match(linea)
        if m:
            _cerrar()
            actual_title = m.group(1).strip(" *")
            actual_body = []
        else:
            if actual_title is None:
                preambulo.append(linea)
            else:
                actual_body.append(linea)
    _cerrar()

    resultado = []
    preambulo_txt = "\n".join(preambulo).strip()
    if preambulo_txt:
        resultado.append({"title": None, "body": preambulo_txt})
    resultado.extend(secciones)
    return resultado


def _asignar_graficos_a_secciones(secciones, graficos_disponibles):
    """Asocia cada gráfico a la sección cuyo título encaja mejor por keywords.

    Se puntúa cada sección por número de coincidencias de palabras clave y
    se asigna el gráfico a la de mayor score. De este modo "Métricas clave"
    gana a "Resumen ejecutivo" para el gráfico de métricas porque acumula
    más palabras clave específicas.
    """
    asignaciones = {i: [] for i in range(len(secciones))}

    for key in graficos_disponibles:
        palabras = _CHART_KEYWORDS.get(key, ())
        mejor_idx = None
        mejor_score = 0
        for i, sec in enumerate(secciones):
            titulo = (sec.get("title") or "").lower()
            if not titulo:
                continue
            score = sum(1 for pal in palabras if pal in titulo)
            if score > mejor_score:
                mejor_score = score
                mejor_idx = i
        if mejor_idx is not None:
            asignaciones[mejor_idx].append(key)

    resultado = [
        {**sec, "charts": asignaciones[i]}
        for i, sec in enumerate(secciones)
    ]
    asignados_total = {ch for lst in asignaciones.values() for ch in lst}
    pendientes = [k for k in graficos_disponibles if k not in asignados_total]
    return resultado, pendientes


def segmentar_y_asignar(nota):
    """Wrapper pensado para usarse desde las vistas y los exportadores."""
    secciones = _segmentar_memoria(nota)
    orden = ["ingresos", "margenes", "estructura", "metricas"]
    return _asignar_graficos_a_secciones(secciones, orden)


# ---------------------------------------------------------------------------
# Renderizado de gráficos a PNG para Word/PDF (matplotlib, paleta Deloitte).
# ---------------------------------------------------------------------------

def _formato_eje_cifra(v, _pos=None):
    abs_v = abs(v)
    if abs_v >= 1e9:
        return f"{v/1e9:,.1f}B"
    if abs_v >= 1e6:
        return f"{v/1e6:,.1f}M"
    if abs_v >= 1e3:
        return f"{v/1e3:,.0f}K"
    return f"{v:,.0f}"


def _figura_a_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _chart_png_ingresos(graficos):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(graficos["labels"], graficos["ingresos"], color=_MPL_GREEN, edgecolor=_MPL_GREEN_DARK)
    moneda = graficos.get("moneda", "")
    titulo = "Evolución de ingresos" + (f" ({moneda})" if moneda else "")
    ax.set_title(titulo, fontsize=11, fontweight="bold", loc="left", color=_MPL_BLACK)
    ax.yaxis.set_major_formatter(FuncFormatter(_formato_eje_cifra))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E4E4E2", linewidth=0.6)
    ax.set_axisbelow(True)
    return _figura_a_bytes(fig)


def _chart_png_margenes(graficos):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    labels = graficos["labels"]
    ax.plot(labels, graficos["margenes"]["margen_bruto"], marker="o", color=_MPL_GREEN_DARK, label="Margen bruto (%)")
    ax.plot(labels, graficos["margenes"]["ebitda"], marker="o", color=_MPL_BLACK, label="EBITDA (%)")
    ax.plot(labels, graficos["margenes"]["neto"], marker="o", color=_MPL_ORANGE, label="Margen neto (%)")
    ax.set_title("Evolución de márgenes", fontsize=11, fontweight="bold", loc="left", color=_MPL_BLACK)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _=None: f"{v:.0f}%"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E4E4E2", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False, fontsize=9)
    return _figura_a_bytes(fig)


def _chart_png_estructura(graficos):
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    etiquetas = graficos["estructura_costes"]["labels"]
    valores = [max(v, 0) for v in graficos["estructura_costes"]["values"]]
    colores = [_MPL_BLACK, _MPL_GRAY, _MPL_ORANGE, _MPL_GREEN]
    if sum(valores) <= 0:
        valores = [1] * len(etiquetas)
    wedges, _texts, autotexts = ax.pie(
        valores, labels=None, colors=colores, startangle=90,
        autopct=lambda p: f"{p:.1f}%", pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(9)
    moneda = graficos.get("moneda", "")
    sufijo_moneda = f" — {moneda}" if moneda else ""
    ax.set_title(
        f"Estructura de costes — {graficos['estructura_costes']['periodo']}{sufijo_moneda}",
        fontsize=11, fontweight="bold", loc="left", color=_MPL_BLACK,
    )
    ax.legend(wedges, etiquetas, loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=8.5)
    return _figura_a_bytes(fig)


def _chart_png_metricas(graficos):
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    labels = graficos["metricas_clave"]["labels"]
    valores = graficos["metricas_clave"]["values"]
    colores = [_MPL_BLACK, _MPL_GREEN_DARK, _MPL_GREEN, _MPL_ORANGE][: len(labels)]
    bars = ax.barh(labels, valores, color=colores, edgecolor="white")
    ax.invert_yaxis()
    moneda = graficos.get("moneda", "")
    sufijo_moneda = f" — {moneda}" if moneda else ""
    ax.set_title(
        f"Métricas clave — {graficos['metricas_clave']['periodo']}{sufijo_moneda}",
        fontsize=11, fontweight="bold", loc="left", color=_MPL_BLACK,
    )
    ax.xaxis.set_major_formatter(FuncFormatter(_formato_eje_cifra))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#E4E4E2", linewidth=0.6)
    ax.set_axisbelow(True)
    for bar, v in zip(bars, valores):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
                "  " + _formato_eje_cifra(v), va="center", fontsize=9, color=_MPL_BLACK)
    return _figura_a_bytes(fig)


_CHART_RENDERERS = {
    "ingresos": _chart_png_ingresos,
    "margenes": _chart_png_margenes,
    "estructura": _chart_png_estructura,
    "metricas": _chart_png_metricas,
}

_CHART_TITULOS = {
    "ingresos": "Evolución de ingresos",
    "margenes": "Evolución de márgenes",
    "estructura": "Estructura de costes",
    "metricas": "Métricas clave del último ejercicio",
}


def añadir_markdown_a_docx(doc, texto):
    """Convierte texto Markdown ligero a párrafos Word con encabezados y listas.

    Soporta encabezados `#`/`##`/`###`, listas con `-`/`*`/numeradas, y
    formato inline `**negrita**`, `*cursiva*` y `` `código` ``. Las filas de
    tablas Markdown se transforman en líneas legibles separadas por ` · `.
    """
    if not texto:
        return

    lineas = texto.replace("\r\n", "\n").split("\n")
    for linea in lineas:
        stripped = linea.strip()
        if not stripped:
            continue
        # Filas separadoras de tabla Markdown: |---|---|
        if _RE_TABLA_SEP_MD.match(stripped):
            continue
        # Filas de tabla Markdown: convertir a "celda1 · celda2 · celda3"
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            celdas = [c.strip() for c in stripped.strip("|").split("|")]
            celdas = [c for c in celdas if c]
            if celdas:
                p = doc.add_paragraph()
                _añadir_runs_con_formato(p, " · ".join(celdas))
            continue
        # Encabezados
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:].strip(" *"), level=3)
            continue
        if stripped.startswith("## "):
            doc.add_heading(stripped[3:].strip(" *"), level=2)
            continue
        if stripped.startswith("# "):
            doc.add_heading(stripped[2:].strip(" *"), level=1)
            continue
        # Listas con viñetas
        m = re.match(r"^[-*]\s+(.*)", stripped)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            _añadir_runs_con_formato(p, m.group(1))
            continue
        # Listas numeradas
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            _añadir_runs_con_formato(p, m.group(1))
            continue
        # Párrafo normal
        p = doc.add_paragraph()
        _añadir_runs_con_formato(p, stripped)


def _añadir_tabla_datos_word(doc, datos, escala):
    """Añade la tabla de datos con anchuras fijas para que no se corte."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    headers = ["Métrica"] + [p["periodo"] for p in datos["periodos"]]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.autofit = False
    # Layout fijo: fuerza al word a respetar los anchos de columna.
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)

    ancho_metrica = Inches(1.8)
    n_periodos = max(len(datos["periodos"]), 1)
    ancho_periodo = Inches((6.3 - 1.8) / n_periodos)

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.width = ancho_metrica if i == 0 else ancho_periodo
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(9.5)

    metricas = [
        ("Ingresos", "ingresos", None),
        ("Coste de ventas", "coste_ventas", None),
        ("Margen bruto", "margen_bruto", "pct_margen_bruto"),
        ("Gastos operativos", "gastos_operativos", "pct_gastos_operativos"),
        ("EBITDA", "ebitda", "pct_ebitda"),
        ("Beneficio neto", "beneficio_neto", "pct_beneficio_neto"),
    ]
    for nombre_metrica, key, pct_key in metricas:
        row = table.add_row()
        row.cells[0].text = nombre_metrica
        row.cells[0].width = ancho_metrica
        for i, p in enumerate(datos["periodos"]):
            valor = formatear_importe_escalado(p[key], escala)
            if pct_key:
                valor += f" ({formatear_pct_es(p[pct_key])})"
            row.cells[i + 1].text = valor
            row.cells[i + 1].width = ancho_periodo
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)


def _añadir_seccion_markdown_docx(doc, texto):
    """Añade a Word un bloque de Markdown *sin* encabezado (el body de una sección)."""
    if not texto:
        return
    lineas = texto.replace("\r\n", "\n").split("\n")
    for linea in lineas:
        stripped = linea.strip()
        if not stripped:
            continue
        if _RE_TABLA_SEP_MD.match(stripped):
            continue
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            celdas = [c.strip() for c in stripped.strip("|").split("|") if c.strip()]
            if celdas:
                p = doc.add_paragraph()
                _añadir_runs_con_formato(p, " · ".join(celdas))
            continue
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:].strip(" *"), level=3)
            continue
        if stripped.startswith("# "):
            doc.add_heading(stripped[2:].strip(" *"), level=2)
            continue
        m = re.match(r"^[-*]\s+(.*)", stripped)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            _añadir_runs_con_formato(p, m.group(1))
            continue
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            _añadir_runs_con_formato(p, m.group(1))
            continue
        p = doc.add_paragraph()
        _añadir_runs_con_formato(p, stripped)


def _insertar_grafico_docx(doc, chart_key, graficos):
    renderer = _CHART_RENDERERS.get(chart_key)
    if renderer is None:
        return
    buf = renderer(graficos)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(buf, width=Inches(5.8))


def crear_documento_word(datos, nota):
    """Crea un documento Word con los datos financieros, gráficos y memoria."""
    doc = Document()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    # Márgenes algo más estrechos para tablas anchas
    for section in doc.sections:
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)

    titulo = doc.add_heading(f"Informe Financiero — {datos['nombre']}", level=0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in titulo.runs:
        run.font.color.rgb = RGBColor(0x43, 0xB0, 0x2A)

    escala = determinar_escala_tabla(datos)
    moneda = datos.get("moneda") or ""
    subtitulo = doc.add_paragraph()
    run = subtitulo.add_run(f"Ticker: {datos['ticker']}")
    run.font.bold = True
    if moneda:
        subtitulo.add_run(f"  ·  Moneda de reporting: {moneda}")
    doc.add_paragraph("")

    doc.add_heading("Datos Financieros", level=1)
    etiqueta = etiqueta_unidad(escala, moneda)
    if etiqueta:
        p = doc.add_paragraph()
        r = p.add_run(etiqueta)
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x53, 0x56, 0x5A)
    _añadir_tabla_datos_word(doc, datos, escala)
    doc.add_paragraph("")

    doc.add_heading("Nota de Memoria Explicativa", level=1)

    graficos = preparar_datos_graficos(datos)
    secciones_asignadas, pendientes = segmentar_y_asignar(nota)

    for sec in secciones_asignadas:
        if sec.get("title"):
            doc.add_heading(sec["title"], level=2)
        _añadir_seccion_markdown_docx(doc, sec["body"])
        for ch in sec.get("charts", []):
            _insertar_grafico_docx(doc, ch, graficos)

    if pendientes:
        doc.add_heading("Resumen visual", level=2)
        for ch in pendientes:
            _insertar_grafico_docx(doc, ch, graficos)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def crear_documento_comparativo(datos_empresas, analisis):
    """Crea un documento Word con el análisis comparativo."""
    doc = Document()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    for section in doc.sections:
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)

    titulo = doc.add_heading("Informe Comparativo Financiero", level=0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in titulo.runs:
        run.font.color.rgb = RGBColor(0x43, 0xB0, 0x2A)

    empresas_nombres = ", ".join([d["nombre"] for d in datos_empresas])
    doc.add_paragraph(f"Empresas comparadas: {empresas_nombres}")

    # Escala y moneda para el comparativo: se elige la escala a partir del
    # máximo entre todas las empresas para que la tabla sea comparable.
    datos_combinados = {
        "periodos": [d["periodos"][0] for d in datos_empresas if d.get("periodos")]
    }
    escala = determinar_escala_tabla(datos_combinados)
    monedas = sorted({d.get("moneda", "") for d in datos_empresas if d.get("moneda")})
    moneda_display = ", ".join(monedas) if monedas else ""
    etiqueta = etiqueta_unidad(escala, moneda_display)
    if etiqueta:
        p = doc.add_paragraph()
        r = p.add_run(etiqueta)
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x53, 0x56, 0x5A)
        if len(monedas) > 1:
            warn = doc.add_paragraph()
            wr = warn.add_run(
                "Atención: las empresas comparadas reportan en monedas distintas; "
                "las cifras no se han convertido a una moneda única."
            )
            wr.italic = True
            wr.font.size = Pt(9)
            wr.font.color.rgb = RGBColor(0xED, 0x8B, 0x00)
    doc.add_paragraph("")

    doc.add_heading("Tabla Comparativa", level=1)

    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    headers = ["Métrica"] + [d["nombre"] for d in datos_empresas]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)

    ancho_metrica = Inches(1.8)
    n_empresas = max(len(datos_empresas), 1)
    ancho_empresa = Inches((6.3 - 1.8) / n_empresas)

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.width = ancho_metrica if i == 0 else ancho_empresa
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(9.5)

    metricas = [
        ("Ingresos", "ingresos", None),
        ("Coste de ventas", "coste_ventas", None),
        ("Margen bruto", "margen_bruto", "pct_margen_bruto"),
        ("Gastos operativos", "gastos_operativos", "pct_gastos_operativos"),
        ("EBITDA", "ebitda", "pct_ebitda"),
        ("Beneficio neto", "beneficio_neto", "pct_beneficio_neto"),
    ]

    for nombre_metrica, key, pct_key in metricas:
        row = table.add_row()
        row.cells[0].text = nombre_metrica
        row.cells[0].width = ancho_metrica
        for i, datos in enumerate(datos_empresas):
            p = datos["periodos"][0]  # Último periodo
            valor = formatear_importe_escalado(p[key], escala)
            if pct_key:
                valor += f" ({formatear_pct_es(p[pct_key])})"
            row.cells[i + 1].text = valor
            row.cells[i + 1].width = ancho_empresa
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)

    doc.add_paragraph("")
    doc.add_heading("Análisis Comparativo", level=1)
    añadir_markdown_a_docx(doc, analisis)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def _md_inline_a_html(texto):
    """Convierte **negrita**, *cursiva* y `código` a tags reportlab/HTML seguros."""
    if not texto:
        return ""
    seguro = (
        texto.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
    )
    seguro = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", seguro)
    seguro = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<i>\1</i>", seguro)
    seguro = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", seguro)
    return seguro


def _markdown_a_flowables_pdf(texto, estilos):
    """Convierte texto Markdown ligero a una lista de flowables para ReportLab."""
    flow = []
    if not texto:
        return flow

    lineas = texto.replace("\r\n", "\n").split("\n")
    bullets = []

    def _volcar_bullets():
        if not bullets:
            return
        items = [
            ListItem(Paragraph(_md_inline_a_html(b), estilos["Body"]), leftIndent=10)
            for b in bullets
        ]
        flow.append(ListFlowable(items, bulletType="bullet", start="•",
                                 leftIndent=14, bulletFontSize=9))
        flow.append(Spacer(1, 4))
        bullets.clear()

    for linea in lineas:
        stripped = linea.strip()
        if not stripped:
            _volcar_bullets()
            flow.append(Spacer(1, 4))
            continue
        if _RE_TABLA_SEP_MD.match(stripped):
            continue
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            _volcar_bullets()
            celdas = [c.strip() for c in stripped.strip("|").split("|") if c.strip()]
            if celdas:
                flow.append(Paragraph(_md_inline_a_html(" · ".join(celdas)), estilos["Body"]))
            continue
        if stripped.startswith("### "):
            _volcar_bullets()
            flow.append(Paragraph(_md_inline_a_html(stripped[4:].strip(" *")), estilos["H3"]))
            continue
        if stripped.startswith("## "):
            _volcar_bullets()
            flow.append(Paragraph(_md_inline_a_html(stripped[3:].strip(" *")), estilos["H2"]))
            continue
        if stripped.startswith("# "):
            _volcar_bullets()
            flow.append(Paragraph(_md_inline_a_html(stripped[2:].strip(" *")), estilos["H1"]))
            continue
        m = re.match(r"^[-*]\s+(.*)", stripped)
        if m:
            bullets.append(m.group(1))
            continue
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            bullets.append(m.group(1))
            continue
        _volcar_bullets()
        flow.append(Paragraph(_md_inline_a_html(stripped), estilos["Body"]))

    _volcar_bullets()
    return flow


DELOITTE_GREEN = colors.HexColor("#86BC25")
DELOITTE_GREEN_DARK = colors.HexColor("#43B02A")
DELOITTE_BLACK = colors.HexColor("#000000")
DELOITTE_GRAY_11 = colors.HexColor("#53565A")
DELOITTE_GRAY_BORDER = colors.HexColor("#D0D0CE")
DELOITTE_GRAY_BG = colors.HexColor("#F5F5F4")


def _estilos_pdf():
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "DFTitle", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=20, leading=24,
            textColor=DELOITTE_BLACK, alignment=TA_LEFT, spaceAfter=6,
        ),
        "Eyebrow": ParagraphStyle(
            "DFEyebrow", fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=DELOITTE_GREEN_DARK, spaceAfter=2,
        ),
        "Subtitle": ParagraphStyle(
            "DFSub", fontName="Helvetica", fontSize=10, leading=14,
            textColor=DELOITTE_GRAY_11, spaceAfter=14,
        ),
        "H1": ParagraphStyle(
            "DFH1", fontName="Helvetica-Bold", fontSize=14, leading=18,
            textColor=DELOITTE_BLACK, spaceBefore=12, spaceAfter=6,
        ),
        "H2": ParagraphStyle(
            "DFH2", fontName="Helvetica-Bold", fontSize=12, leading=16,
            textColor=DELOITTE_BLACK, spaceBefore=10, spaceAfter=5,
        ),
        "H3": ParagraphStyle(
            "DFH3", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
            textColor=DELOITTE_GRAY_11, spaceBefore=8, spaceAfter=3,
        ),
        "Body": ParagraphStyle(
            "DFBody", fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=DELOITTE_BLACK, alignment=TA_JUSTIFY, spaceAfter=4,
        ),
    }


def _dibujar_branding_pdf(canvas, doc):
    canvas.saveState()
    # Barra lateral verde Deloitte
    canvas.setFillColor(DELOITTE_GREEN)
    canvas.rect(0, 0, 6, A4[1], stroke=0, fill=1)
    # Cabecera
    canvas.setFillColor(DELOITTE_BLACK)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(18 * mm, A4[1] - 12 * mm, "DFin AI")
    canvas.setFillColor(DELOITTE_GREEN_DARK)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(18 * mm + 18, A4[1] - 12 * mm, "· Financial Intelligence")
    canvas.setStrokeColor(DELOITTE_GREEN)
    canvas.setLineWidth(1)
    canvas.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
    # Pie
    canvas.setFillColor(DELOITTE_GRAY_11)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 10 * mm, "DFin AI · Informe confidencial")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {canvas.getPageNumber()}")
    canvas.restoreState()


def _construir_tabla_datos_pdf(datos, ancho_total, escala):
    """Construye la tabla de datos financieros para PDF ajustada al ancho dado."""
    headers = ["Métrica"] + [p["periodo"] for p in datos["periodos"]]
    filas_metricas = [
        ("Ingresos", "ingresos", None),
        ("Coste de ventas", "coste_ventas", None),
        ("Margen bruto", "margen_bruto", "pct_margen_bruto"),
        ("Gastos operativos", "gastos_operativos", "pct_gastos_operativos"),
        ("EBITDA", "ebitda", "pct_ebitda"),
        ("Beneficio neto", "beneficio_neto", "pct_beneficio_neto"),
    ]
    body_rows = []
    for nombre_metrica, key, pct_key in filas_metricas:
        fila = [nombre_metrica]
        for p in datos["periodos"]:
            valor = formatear_importe_escalado(p[key], escala)
            if pct_key:
                valor += f" ({formatear_pct_es(p[pct_key])})"
            fila.append(valor)
        body_rows.append(fila)

    # Anchuras fijas para evitar cortes en la tabla
    n_periodos = max(len(datos["periodos"]), 1)
    ancho_metrica = min(42 * mm, ancho_total * 0.28)
    ancho_periodo = (ancho_total - ancho_metrica) / n_periodos
    col_widths = [ancho_metrica] + [ancho_periodo] * n_periodos

    tabla = Table([headers] + body_rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DELOITTE_BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (1, 0), (-1, 0), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, DELOITTE_GREEN),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, DELOITTE_GRAY_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, DELOITTE_GRAY_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabla


def _flowable_chart_pdf(chart_key, graficos, ancho_disponible):
    renderer = _CHART_RENDERERS.get(chart_key)
    if renderer is None:
        return []
    buf = renderer(graficos)
    img = RLImage(buf)
    # Escala manteniendo aspecto para ocupar como máximo el 90% del ancho.
    max_w = ancho_disponible * 0.92
    w, h = img.drawWidth, img.drawHeight
    escala = min(max_w / w, 1)
    img.drawWidth = w * escala
    img.drawHeight = h * escala
    return [Spacer(1, 6), img, Spacer(1, 10)]


def crear_documento_pdf(datos, nota):
    """Crea un PDF de la nota de memoria con branding DFin AI / paleta Deloitte."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=22 * mm, bottomMargin=18 * mm,
        title=f"Informe DFin AI — {datos['nombre']}",
        author="DFin AI",
    )
    ancho_disponible = A4[0] - 36 * mm
    estilos = _estilos_pdf()
    story = []

    escala = determinar_escala_tabla(datos)
    moneda = datos.get("moneda") or ""

    story.append(Paragraph("INFORME FINANCIERO · NOTA DE MEMORIA", estilos["Eyebrow"]))
    story.append(Paragraph(datos["nombre"], estilos["Title"]))
    sub = f"Ticker <b>{datos['ticker']}</b> &nbsp;·&nbsp; {len(datos['periodos'])} ejercicios analizados"
    if moneda:
        sub += f" &nbsp;·&nbsp; Moneda: <b>{moneda}</b>"
    story.append(Paragraph(sub, estilos["Subtitle"]))

    story.append(Paragraph("Datos financieros — serie histórica", estilos["H1"]))
    etiqueta = etiqueta_unidad(escala, moneda)
    if etiqueta:
        story.append(Paragraph(f"<i>{etiqueta}</i>", estilos["Body"]))
        story.append(Spacer(1, 4))
    story.append(_construir_tabla_datos_pdf(datos, ancho_disponible, escala))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Nota de memoria explicativa", estilos["H1"]))

    graficos = preparar_datos_graficos(datos)
    secciones_asignadas, pendientes = segmentar_y_asignar(nota)

    for sec in secciones_asignadas:
        if sec.get("title"):
            story.append(Paragraph(_md_inline_a_html(sec["title"]), estilos["H2"]))
        story.extend(_markdown_a_flowables_pdf(sec["body"], estilos))
        for ch in sec.get("charts", []):
            story.extend(_flowable_chart_pdf(ch, graficos, ancho_disponible))

    if pendientes:
        story.append(Paragraph("Resumen visual", estilos["H2"]))
        for ch in pendientes:
            story.extend(_flowable_chart_pdf(ch, graficos, ancho_disponible))

    doc.build(story, onFirstPage=_dibujar_branding_pdf, onLaterPages=_dibujar_branding_pdf)
    buffer.seek(0)
    return buffer


def formatear_numero(valor):
    """Formatea números grandes en formato europeo (miles con `.`, decimales con `,`).

    Escala el número a la unidad más cómoda visualmente:
    - < 1.000        → entero o 2 decimales según haya parte decimal
    - < 1.000.000    → entero con separadores de miles
    - < mil millones → millones con 2 decimales y sufijo "M"
    - < 1 billón     → miles de millones con 2 decimales y sufijo "mil M"
    - resto          → billones con 2 decimales y sufijo "B" (1 B = 10^12)
    """
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return ""
    abs_v = abs(v)
    if abs_v >= 1e12:
        return _fmt_es(v / 1e12, 2) + " B"
    if abs_v >= 1e9:
        return _fmt_es(v / 1e9, 2) + " mil M"
    if abs_v >= 1e6:
        return _fmt_es(v / 1e6, 2) + " M"
    if abs_v >= 1000:
        return _fmt_es(v, 0)
    if abs_v == 0 or float(v).is_integer():
        return _fmt_es(v, 0)
    return _fmt_es(v, 2)


def _fmt_es(valor, decimales):
    """Aplica formato español: punto como separador de miles, coma como decimal."""
    s = f"{valor:,.{decimales}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def determinar_escala_tabla(datos):
    """Escoge una escala común para toda la tabla según la cifra máxima.

    Devuelve un dict con `divisor`, `sufijo` (unidad legible) y `decimales`.
    Usa la misma escala para todas las filas/columnas para garantizar que
    los importes caben en la tabla y son comparables entre sí.
    """
    vals = []
    for p in datos.get("periodos", []):
        for k in ("ingresos", "coste_ventas", "margen_bruto",
                  "gastos_operativos", "ebitda", "beneficio_neto"):
            v = p.get(k, 0) or 0
            vals.append(abs(float(v)))
    max_v = max(vals) if vals else 0

    if max_v >= 1e12:
        return {"divisor": 1e9, "sufijo": "miles de millones", "decimales": 2}
    if max_v >= 1e9:
        return {"divisor": 1e6, "sufijo": "millones", "decimales": 0}
    if max_v >= 1e6:
        return {"divisor": 1e6, "sufijo": "millones", "decimales": 1}
    if max_v >= 1e3:
        return {"divisor": 1e3, "sufijo": "miles", "decimales": 0}
    return {"divisor": 1, "sufijo": "", "decimales": 0}


def escala_para_estado(bloque):
    """Elige una escala común para un estado financiero completo.

    `bloque` es la entrada de `datos["estados"][clave]` con `periodos` y `filas`.
    Devuelve la misma estructura que `determinar_escala_tabla`. Las filas que
    parecen ratios o porcentajes (`Tax Rate`, `EPS`, `Acciones medias`) se
    excluyen del cálculo para no falsear la escala con valores pequeños o
    enormes según el caso.
    """
    EXCLUIDOS = (
        "BPA", "EPS", "Acciones medias", "Tasa impositiva", "Number", "Acciones emitidas",
    )
    vals = []
    for fila in bloque.get("filas", []):
        nombre = fila.get("concepto", "")
        if any(t.lower() in nombre.lower() for t in EXCLUIDOS):
            continue
        for v in fila.get("valores", []):
            if v is None:
                continue
            try:
                vals.append(abs(float(v)))
            except (TypeError, ValueError):
                pass
    max_v = max(vals) if vals else 0
    if max_v >= 1e12:
        return {"divisor": 1e9, "sufijo": "miles de millones", "decimales": 2}
    if max_v >= 1e9:
        return {"divisor": 1e6, "sufijo": "millones", "decimales": 0}
    if max_v >= 1e6:
        return {"divisor": 1e6, "sufijo": "millones", "decimales": 1}
    if max_v >= 1e3:
        return {"divisor": 1e3, "sufijo": "miles", "decimales": 0}
    return {"divisor": 1, "sufijo": "", "decimales": 0}


def formatear_celda_estado(valor, escala, concepto=""):
    """Aplica la escala del estado y devuelve la cadena formateada en español.

    Las filas tipo BPA/EPS, tasas impositivas o número de acciones se muestran
    SIN aplicar la escala (no son magnitudes monetarias en millones).
    """
    if valor is None:
        return ""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return ""
    nombre = (concepto or "").lower()
    if any(t in nombre for t in ("bpa", "eps", "acciones medias", "tasa impositiva", "acciones emitidas", "ordinary shares number")):
        # Magnitudes per-share o conteos: sin escala, hasta 2 decimales.
        decimales = 2 if abs(v) < 1000 else 0
        return _fmt_es(v, decimales)
    divisor = escala.get("divisor", 1) or 1
    decimales = escala.get("decimales", 0)
    return _fmt_es(v / divisor, decimales)



def formatear_importe_escalado(valor, escala):
    """Formatea un importe aplicando una escala y formato español."""
    divisor = escala.get("divisor", 1) or 1
    decimales = escala.get("decimales", 0)
    return _fmt_es(valor / divisor, decimales)


def formatear_pct_es(pct):
    """Formatea un porcentaje con un decimal y formato español."""
    return _fmt_es(pct, 1) + "%"


def etiqueta_unidad(escala, moneda):
    """Etiqueta legible del tipo 'Cifras en millones de USD'."""
    sufijo = escala.get("sufijo", "")
    moneda = (moneda or "").strip()
    if sufijo and moneda:
        return f"Cifras en {sufijo} de {moneda}"
    if sufijo:
        return f"Cifras en {sufijo}"
    if moneda:
        return f"Cifras en {moneda}"
    return ""


# KPIs por defecto (siempre se muestran en el cuadro de "Datos relevantes").
_KPI_BASE = [
    {"label": "Ingresos", "fuente": ("pyg", "ingresos"), "tipo": "moneda"},
    {"label": "Margen bruto", "fuente": ("pyg", "margen_bruto"), "pct": "pct_margen_bruto", "tipo": "moneda"},
    {"label": "EBITDA", "fuente": ("pyg", "ebitda"), "pct": "pct_ebitda", "tipo": "moneda"},
    {"label": "EBIT", "fuente": ("pyg", "ebit"), "pct": "pct_ebit", "tipo": "moneda"},
    {"label": "Beneficio neto", "fuente": ("pyg", "beneficio_neto"), "pct": "pct_beneficio_neto", "tipo": "moneda"},
    {"label": "BPA básico", "fuente": ("pyg", "bpa_basico"), "tipo": "per_share"},
]

# KPIs adicionales por enfoque (texto literal del chip seleccionado).
_KPI_POR_ENFOQUE = {
    "Estructura de costes": [
        {"label": "Coste de ventas", "fuente": ("pyg", "coste_ventas"), "tipo": "moneda"},
        {"label": "SG&A", "fuente": ("pyg", "sga"), "pct": "pct_sga", "tipo": "moneda"},
        {"label": "I+D", "fuente": ("pyg", "rd"), "pct": "pct_rd", "tipo": "moneda"},
        {"label": "Amortizaciones (D&A)", "fuente": ("pyg", "da"), "pct": "pct_da", "tipo": "moneda"},
    ],
    "Fiscalidad y resultado financiero": [
        {"label": "Resultado financiero neto", "fuente": ("pyg", "resultado_financiero_neto"), "tipo": "moneda"},
        {"label": "Resultado antes de impuestos", "fuente": ("pyg", "resultado_antes_impuestos"), "pct": "pct_rai", "tipo": "moneda"},
        {"label": "Impuesto sobre beneficios", "fuente": ("pyg", "impuestos"), "tipo": "moneda"},
        {"label": "Tasa impositiva efectiva", "fuente": ("pyg", "tasa_impositiva"), "tipo": "porcentaje"},
    ],
    "Retorno al accionista (BPA, dividendos)": [
        {"label": "BPA diluido", "fuente": ("pyg", "bpa_diluido"), "tipo": "per_share"},
        {"label": "Dividendos pagados", "fuente": ("cashflow", "Dividendos pagados en efectivo"), "tipo": "moneda"},
    ],
    "Endeudamiento y solvencia": [
        {"label": "Deuda total", "fuente": ("balance_sheet", "Deuda total"), "tipo": "moneda"},
        {"label": "Deuda neta", "fuente": ("balance_sheet", "Deuda neta"), "tipo": "moneda"},
        {"label": "Patrimonio neto", "fuente": ("balance_sheet", "Patrimonio neto total"), "tipo": "moneda"},
        {"label": "Activos totales", "fuente": ("balance_sheet", "Activos totales"), "tipo": "moneda"},
    ],
    "Generación de caja": [
        {"label": "Flujo de caja operativo", "fuente": ("cashflow", "Flujo de caja operativo"), "tipo": "moneda"},
        {"label": "CAPEX", "fuente": ("cashflow", "Inversiones en inmovilizado (CAPEX)"), "tipo": "moneda"},
        {"label": "Flujo de caja libre", "fuente": ("cashflow", "Flujo de caja libre"), "tipo": "moneda"},
    ],
    "Capital circulante": [
        {"label": "Capital circulante", "fuente": ("balance_sheet", "Capital circulante"), "tipo": "moneda"},
        {"label": "Existencias", "fuente": ("balance_sheet", "Existencias"), "tipo": "moneda"},
        {"label": "Cuentas por cobrar", "fuente": ("balance_sheet", "Cuentas por cobrar comerciales"), "tipo": "moneda"},
        {"label": "Cuentas por pagar", "fuente": ("balance_sheet", "Cuentas por pagar comerciales"), "tipo": "moneda"},
    ],
    "Inversiones (CAPEX)": [
        {"label": "CAPEX", "fuente": ("cashflow", "Inversiones en inmovilizado (CAPEX)"), "tipo": "moneda"},
        {"label": "Inmovilizado material neto", "fuente": ("balance_sheet", "Inmovilizado material neto"), "tipo": "moneda"},
    ],
    # "Evolución de ingresos" y "Margen y rentabilidad" se cubren con los KPIs base.
}


def _buscar_fila_estado(datos, estado_key, concepto):
    """Busca una fila por concepto exacto en datos['estados'][estado_key]."""
    estado = (datos.get("estados") or {}).get(estado_key) or {}
    for fila in estado.get("filas", []):
        if fila.get("concepto") == concepto:
            return fila.get("valores", [])
    return []


def _valores_kpi(datos, fuente):
    """Devuelve [valor_ultimo, valor_anterior] para una fuente declarada en un KPI."""
    origen, clave = fuente
    if origen == "pyg":
        periodos = datos.get("periodos", []) or []
        ultimo = periodos[0].get(clave) if len(periodos) > 0 else None
        anterior = periodos[1].get(clave) if len(periodos) > 1 else None
        return ultimo, anterior
    valores = _buscar_fila_estado(datos, origen, clave)
    ultimo = valores[0] if len(valores) > 0 else None
    anterior = valores[1] if len(valores) > 1 else None
    return ultimo, anterior


def construir_metricas_relevantes(datos, enfoques_pred):
    """Selecciona las métricas a destacar en función del enfoque del informe.

    `enfoques_pred` es la lista de chips seleccionados por el usuario en el
    configurador. Si está vacía, devolvemos sólo los KPIs base.
    """
    seleccion = list(_KPI_BASE)
    vistos = {(k["fuente"][0], k["fuente"][1]) for k in seleccion}
    for enfoque in enfoques_pred or []:
        for kpi in _KPI_POR_ENFOQUE.get(enfoque, []):
            firma = (kpi["fuente"][0], kpi["fuente"][1])
            if firma in vistos:
                continue
            seleccion.append(kpi)
            vistos.add(firma)

    periodos = datos.get("periodos", []) or []
    label_ult = periodos[0]["periodo"] if periodos else ""
    label_ant = periodos[1]["periodo"] if len(periodos) > 1 else ""

    # Escala común para todas las cifras monetarias del cuadro, basada en el
    # mayor importe presente (igual criterio que las pestañas de Yahoo).
    vals_mon = []
    for kpi in seleccion:
        if kpi["tipo"] not in ("moneda",):
            continue
        u, a = _valores_kpi(datos, kpi["fuente"])
        for v in (u, a):
            if v is not None:
                try:
                    vals_mon.append(abs(float(v)))
                except (TypeError, ValueError):
                    pass
    max_v = max(vals_mon) if vals_mon else 0
    if max_v >= 1e9:
        escala = {"divisor": 1e6, "sufijo": "millones", "decimales": 0}
    elif max_v >= 1e6:
        escala = {"divisor": 1e6, "sufijo": "millones", "decimales": 1}
    elif max_v >= 1e3:
        escala = {"divisor": 1e3, "sufijo": "miles", "decimales": 0}
    else:
        escala = {"divisor": 1, "sufijo": "", "decimales": 0}

    def _fmt_valor(v, tipo):
        if v is None:
            return "—"
        try:
            vf = float(v)
        except (TypeError, ValueError):
            return "—"
        if tipo == "moneda":
            return _fmt_es(vf / escala["divisor"], escala["decimales"])
        if tipo == "per_share":
            return _fmt_es(vf, 2)
        if tipo == "porcentaje":
            return _fmt_es(vf, 1) + "%"
        return _fmt_es(vf, 0)

    def _fmt_variacion(ult, ant):
        if ult is None or ant is None:
            return "—", "neutro"
        try:
            u = float(ult); a = float(ant)
        except (TypeError, ValueError):
            return "—", "neutro"
        if a == 0:
            return "—", "neutro"
        var = ((u - a) / abs(a)) * 100
        sentido = "positivo" if var >= 0 else "negativo"
        signo = "+" if var >= 0 else "−"
        return f"{signo}{_fmt_es(abs(var), 1)}%", sentido

    filas = []
    for kpi in seleccion:
        u, a = _valores_kpi(datos, kpi["fuente"])
        # No mostrar la fila si ambos valores faltan.
        if u is None and a is None:
            continue
        fila = {
            "label": kpi["label"],
            "valor_ultimo": _fmt_valor(u, kpi["tipo"]),
            "valor_anterior": _fmt_valor(a, kpi["tipo"]),
            "tipo": kpi["tipo"],
        }
        pct_clave = kpi.get("pct")
        if pct_clave and periodos:
            pct_ult = periodos[0].get(pct_clave)
            pct_ant = periodos[1].get(pct_clave) if len(periodos) > 1 else None
            fila["pct_ultimo"] = (_fmt_es(pct_ult, 1) + "%") if pct_ult is not None else ""
            fila["pct_anterior"] = (_fmt_es(pct_ant, 1) + "%") if pct_ant is not None else ""
        var_txt, var_sentido = _fmt_variacion(u, a)
        fila["variacion"] = var_txt
        fila["variacion_sentido"] = var_sentido
        filas.append(fila)

    return {
        "filas": filas,
        "periodo_ultimo": label_ult,
        "periodo_anterior": label_ant,
        "escala": escala,
        "moneda": datos.get("moneda", ""),
        "etiqueta_unidad": etiqueta_unidad(escala, datos.get("moneda", "")),
    }


def preparar_datos_graficos(datos):
    """Construye un dict JSON-serializable para renderizar gráficos Chart.js.

    Ordena los periodos cronológicamente (más antiguo → más reciente) para
    que la serie temporal se lea de izquierda a derecha en los gráficos.
    """
    # `periodos[0]` es el más reciente; se invierte para series temporales.
    periodos_ord = list(reversed(datos["periodos"]))

    def _etiqueta_anio(periodo_str):
        return periodo_str[:4] if len(periodo_str) >= 4 else periodo_str

    labels = [_etiqueta_anio(p["periodo"]) for p in periodos_ord]

    ultimo = datos["periodos"][0]
    # Residual = impuestos, intereses, D&A (para cuadrar estructura de costes).
    residual = (
        ultimo["ingresos"]
        - ultimo["coste_ventas"]
        - ultimo["gastos_operativos"]
        - ultimo["beneficio_neto"]
    )
    if residual < 0:
        residual = 0.0

    return {
        "labels": labels,
        "moneda": datos.get("moneda", ""),
        "ingresos": [p["ingresos"] for p in periodos_ord],
        "margenes": {
            "margen_bruto": [p["pct_margen_bruto"] for p in periodos_ord],
            "ebitda": [p["pct_ebitda"] for p in periodos_ord],
            "neto": [p["pct_beneficio_neto"] for p in periodos_ord],
        },
        "estructura_costes": {
            "labels": [
                "Coste de ventas",
                "Gastos operativos",
                "Otros gastos (impuestos, intereses, D&A)",
                "Beneficio neto",
            ],
            "values": [
                ultimo["coste_ventas"],
                ultimo["gastos_operativos"],
                residual,
                ultimo["beneficio_neto"],
            ],
            "periodo": ultimo["periodo"],
        },
        "metricas_clave": {
            "labels": ["Ingresos", "Margen bruto", "EBITDA", "Beneficio neto"],
            "values": [
                ultimo["ingresos"],
                ultimo["margen_bruto"],
                ultimo["ebitda"],
                ultimo["beneficio_neto"],
            ],
            "periodo": ultimo["periodo"],
        },
    }


@app.route("/")
def index():
    return render_template("index.html")


def _render_secciones_para_resultado(nota):
    """Convierte una memoria Markdown en la estructura que espera la plantilla."""
    secciones_asignadas, pendientes = segmentar_y_asignar(nota)
    secciones_html = []
    for sec in secciones_asignadas:
        body_html = markdown.markdown(
            sec.get("body", ""),
            extensions=["tables", "fenced_code", "sane_lists"],
        )
        secciones_html.append({
            "title": sec.get("title"),
            "body_html": body_html,
            "charts": sec.get("charts", []),
        })
    return secciones_html, pendientes


# Cache (a nivel proceso) de los datos de Yahoo del TICKER_FIJO, para evitar
# pegar a yfinance en cada navegación dentro de la misma sesión.
_TICKER_FIJO_DATOS = {"ticker": None, "datos": None}


def _cargar_datos_ticker_fijo():
    if not TICKER_FIJO:
        return None
    if _TICKER_FIJO_DATOS.get("ticker") == TICKER_FIJO and _TICKER_FIJO_DATOS.get("datos"):
        return _TICKER_FIJO_DATOS["datos"]
    datos = obtener_datos_financieros(TICKER_FIJO)
    _TICKER_FIJO_DATOS["ticker"] = TICKER_FIJO
    _TICKER_FIJO_DATOS["datos"] = datos
    if datos and datos.get("nombre"):
        _BRANDING["empresa"] = datos["nombre"]
        _BRANDING["tenant_sufijo"] = datos["nombre"]
    return datos


def _render_datos_yahoo(datos, modelo, error=None):
    cache_id = str(uuid.uuid4())
    _download_cache[cache_id] = {
        "datos": datos,
        "nota": None,
        "modelo": modelo,
        "instrucciones": "",
        "chat_historial": [],
    }
    return render_template(
        "datos_yahoo.html",
        datos=datos,
        cache_id=cache_id,
        modelo_actual=modelo,
        formatear=formatear_numero,
        escala_para_estado=escala_para_estado,
        formatear_celda_estado=formatear_celda_estado,
        error=error,
    )


@app.route("/analisis", methods=["GET", "POST"])
def analisis():
    """Si hay TICKER_FIJO, salta directamente al paso 2 con esa compañía.

    En caso contrario mantiene el flujo en dos pasos: el GET muestra el form
    de selección de ticker y el POST procesa el ticker introducido.
    """
    modelo_default = MODELO_POR_DEFECTO

    if TICKER_FIJO:
        try:
            datos = _cargar_datos_ticker_fijo()
            if datos is None:
                return render_template(
                    "analisis.html",
                    error=(f"No se encontraron datos financieros para el ticker "
                           f"fijado '{TICKER_FIJO}'. Revisa el símbolo bursátil "
                           f"con el que arrancaste la app."),
                    modelo_seleccionado=modelo_default,
                )
            return _render_datos_yahoo(datos, modelo_default)
        except Exception as e:
            return render_template(
                "analisis.html",
                error=f"Error al cargar datos de {TICKER_FIJO}: {e}",
                modelo_seleccionado=modelo_default,
            )

    if request.method == "POST":
        ticker_symbol = request.form.get("ticker", "").strip().upper()
        modelo = _normalizar_modelo(request.form.get("modelo", MODELO_POR_DEFECTO))
        if not ticker_symbol:
            return render_template(
                "analisis.html",
                error="Introduce un ticker válido.",
                modelo_seleccionado=modelo,
            )

        try:
            datos = obtener_datos_financieros(ticker_symbol)
            if datos is None:
                return render_template(
                    "analisis.html",
                    error=f"No se encontraron datos financieros para '{ticker_symbol}'.",
                    modelo_seleccionado=modelo,
                )
            return _render_datos_yahoo(datos, modelo)
        except Exception as e:
            return render_template(
                "analisis.html",
                error=f"Error: {str(e)}",
                modelo_seleccionado=modelo,
            )

    return render_template(
        "analisis.html",
        modelo_seleccionado=MODELO_POR_DEFECTO,
    )


@app.route("/generar_informe", methods=["POST"])
def generar_informe():
    """Paso 2: recibe el configurador y genera el informe narrativo."""
    cache_id = request.form.get("cache_id", "").strip()
    cache_entry = _download_cache.get(cache_id) if cache_id else None
    if not cache_entry:
        return render_template(
            "analisis.html",
            error="La sesión ha expirado. Vuelve a introducir el ticker.",
            modelo_seleccionado=MODELO_POR_DEFECTO,
        )

    datos = cache_entry["datos"]
    modelo = _normalizar_modelo(
        request.form.get("modelo", cache_entry.get("modelo", MODELO_POR_DEFECTO))
    )
    tipo_informe = request.form.get("tipo_informe", "nota_memoria").strip()
    enfoques_pred = request.form.getlist("enfoque_predefinido")
    enfoque_libre = request.form.get("enfoque_libre", "").strip()
    extension = request.form.get("extension", "estandar").strip()
    buscar_noticias = request.form.get("buscar_noticias") in ("1", "on", "true")
    instrucciones = request.form.get("instrucciones", "").strip()

    enfoque_partes = []
    if enfoques_pred:
        enfoque_partes.append("Áreas seleccionadas: " + ", ".join(enfoques_pred) + ".")
    if enfoque_libre:
        enfoque_partes.append(enfoque_libre)
    enfoque = "\n".join(enfoque_partes)

    try:
        nota = generar_nota_memoria(
            datos, modelo,
            instrucciones_usuario=instrucciones,
            permitir_busqueda=buscar_noticias,
            tipo_informe=tipo_informe,
            enfoque=enfoque,
            extension=extension,
        )
    except Exception as e:
        return render_template(
            "datos_yahoo.html",
            datos=datos,
            cache_id=cache_id,
            modelo_actual=modelo,
            formatear=formatear_numero,
            escala_para_estado=escala_para_estado,
            formatear_celda_estado=formatear_celda_estado,
            error=f"Error generando el informe: {e}",
        )

    secciones_html, pendientes = _render_secciones_para_resultado(nota)

    metricas_relevantes = construir_metricas_relevantes(datos, enfoques_pred)

    cache_entry.update({
        "nota": nota,
        "modelo": modelo,
        "instrucciones": instrucciones,
        "chat_historial": [],
        "tipo_informe": tipo_informe,
        "enfoque": enfoque,
        "extension": extension,
    })

    return render_template(
        "resultado.html",
        datos=datos,
        cache_id=cache_id,
        formatear=formatear_numero,
        graficos=preparar_datos_graficos(datos),
        secciones=secciones_html,
        pendientes=pendientes,
        chart_titulos=_CHART_TITULOS,
        modelo_actual=modelo,
        instrucciones_iniciales=instrucciones,
        busqueda_activa_inicial=buscar_noticias,
        metricas_relevantes=metricas_relevantes,
        meta_informe={
            "tipo": tipo_informe,
            "enfoques": enfoques_pred,
            "enfoque_libre": enfoque_libre,
            "extension": extension,
        },
    )


@app.route("/chat_memoria", methods=["POST"])
def chat_memoria():
    """Recibe un turno de chat y devuelve la memoria actualizada."""
    from flask import jsonify, render_template

    data = request.get_json(silent=True) or {}
    cache_id = (data.get("cache_id") or "").strip()
    mensaje = (data.get("mensaje") or "").strip()

    cached = _download_cache.get(cache_id)
    if not cached or "datos" not in cached:
        return jsonify({"error": "La sesión ha caducado. Genera la memoria de nuevo."}), 400
    if not mensaje:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400
    if len(mensaje) > 4000:
        return jsonify({"error": "El mensaje es demasiado largo (máx. 4000 caracteres)."}), 400

    modelo = _normalizar_modelo(data.get("modelo") or cached.get("modelo") or MODELO_POR_DEFECTO)
    buscar_noticias = bool(data.get("buscar_noticias"))
    datos = cached["datos"]
    memoria_actual = cached["nota"]
    historial = cached.setdefault("chat_historial", [])
    instrucciones_iniciales = cached.get("instrucciones", "")

    # Limitar historial a los últimos 10 turnos para contener tokens
    historial_acotado = historial[-10:]

    try:
        respuesta_chat, memoria_nueva, _citas = refinar_memoria_con_chat(
            datos, memoria_actual, historial_acotado, mensaje,
            instrucciones_iniciales, modelo,
            permitir_busqueda=buscar_noticias,
        )
    except Exception as e:
        return jsonify({"error": f"Error al consultar la IA: {str(e)}"}), 500

    # Actualiza el estado en cache
    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": respuesta_chat})
    if memoria_nueva:
        cached["nota"] = memoria_nueva

    memoria_para_render = cached["nota"]
    secciones_html, pendientes = _render_secciones_para_resultado(memoria_para_render)

    memoria_fragmento = render_template(
        "_memoria_fragmento.html",
        datos=datos,
        secciones=secciones_html,
        pendientes=pendientes,
        chart_titulos=_CHART_TITULOS,
    )

    return jsonify({
        "chat_reply": respuesta_chat,
        "memoria_html": memoria_fragmento,
        "memoria_updated": memoria_nueva is not None,
    })


@app.route("/detectar_incoherencias", methods=["POST"])
def detectar_incoherencias():
    """Simula la conexión con Workiva y devuelve incoherencias inventadas
    entre la nota IA y la supuesta nota oficial del equipo financiero.
    """
    from flask import jsonify

    data = request.get_json(silent=True) or {}
    cache_id = (data.get("cache_id") or "").strip()
    cached = _download_cache.get(cache_id)
    if not cached or "datos" not in cached or "nota" not in cached:
        return jsonify({
            "error": "La sesión ha caducado. Genera la memoria de nuevo.",
        }), 400

    modelo = _normalizar_modelo(
        data.get("modelo") or cached.get("modelo") or MODELO_POR_DEFECTO
    )

    try:
        incoherencias = detectar_incoherencias_memoria(
            cached["datos"], cached["nota"], modelo,
        )
    except Exception as e:
        return jsonify({"error": f"Error consultando {SISTEMA_NOTA_OFICIAL}: {str(e)}"}), 500

    if not incoherencias:
        return jsonify({
            "sistema": SISTEMA_NOTA_OFICIAL,
            "incoherencias": [],
            "mensaje": (
                f"No se han detectado incoherencias relevantes entre la nota IA y "
                f"la versión oficial recuperada de {SISTEMA_NOTA_OFICIAL}."
            ),
        })

    return jsonify({
        "sistema": SISTEMA_NOTA_OFICIAL,
        "incoherencias": incoherencias,
    })


@app.route("/comparador", methods=["GET", "POST"])
def comparador():
    if request.method == "POST":
        tickers = []
        for i in range(1, 4):
            t = request.form.get(f"ticker{i}", "").strip().upper()
            if t:
                tickers.append(t)
        modelo = _normalizar_modelo(request.form.get("modelo", MODELO_POR_DEFECTO))

        if len(tickers) < 2:
            return render_template(
                "comparador.html",
                error="Introduce al menos 2 tickers para comparar.",
                modelo_seleccionado=modelo,
            )

        try:
            datos_empresas = []
            errores = []
            for t in tickers:
                datos = obtener_datos_financieros(t)
                if datos is None:
                    errores.append(f"No se encontraron datos para '{t}'")
                else:
                    datos_empresas.append(datos)

            if len(datos_empresas) < 2:
                return render_template(
                    "comparador.html",
                    error="No se pudieron obtener datos suficientes. " + "; ".join(errores),
                    modelo_seleccionado=modelo,
                )

            analisis = generar_analisis_comparativo(datos_empresas, modelo)
            analisis_html = markdown.markdown(analisis, extensions=["tables", "fenced_code", "sane_lists"])

            cache_id = str(uuid.uuid4())
            _download_cache[cache_id] = {
                "datos_empresas": datos_empresas,
                "analisis": analisis,
            }

            return render_template(
                "comparador_resultado.html",
                datos_empresas=datos_empresas,
                analisis=analisis_html,
                errores=errores,
                cache_id=cache_id,
                formatear=formatear_numero,
            )
        except Exception as e:
            return render_template(
                "comparador.html",
                error=f"Error: {str(e)}",
                modelo_seleccionado=modelo,
            )

    return render_template("comparador.html", modelo_seleccionado=MODELO_POR_DEFECTO)


# =============================================================================
# Módulo: Relación con Inversores
# Cuatro correos simulados de inversores (minoristas y mayoristas). El usuario
# pide a la IA un borrador de respuesta; la IA decide si puede resolver con
# datos públicos de Yahoo Finance + búsqueda web, o si tiene que dejar el
# correo medio hecho para que el equipo humano de IR lo complete.
# =============================================================================
_CORREOS_IR = [
    {
        "id": "minorista_bpa",
        "remitente_nombre": "Laura Méndez",
        "remitente_email": "laura.mendez88@gmail.com",
        "remitente_perfil": "Inversora minorista particular",
        "asunto": "Duda sobre la evolución del beneficio por acción",
        "categoria": "Minorista · Datos públicos",
        "cuerpo": """Buenos días,

Soy una pequeña inversora particular y estoy pensando en abrir una posición en {empresa}. Antes de dar el paso me gustaría entender cómo ha evolucionado el beneficio por acción de la compañía en los últimos 3-4 años y si la tendencia es estable o ha habido saltos relevantes que conviene tener en cuenta.

¿Podríais darme un resumen rápido? No soy profesional del sector y necesito entenderlo sin tecnicismos.

Muchas gracias por vuestro tiempo.

Un saludo,
Laura Méndez""",
    },
    {
        "id": "fondo_ratios",
        "remitente_nombre": "Carlos Ferrer, CFA",
        "remitente_email": "c.ferrer@altea-capital.es",
        "remitente_perfil": "Senior Portfolio Manager — Altea Capital Partners",
        "asunto": "Apalancamiento y conversión de caja — solicitud de aclaración",
        "categoria": "Mayorista · Cálculo sobre datos públicos",
        "cuerpo": """Estimado equipo de Relación con Inversores,

Les escribo desde Altea Capital Partners. En el marco de la revisión anual de nuestra exposición a {ticker} necesitaríamos confirmar tres puntos relativos al último ejercicio cerrado:

  1. Ratio Deuda Neta / EBITDA.
  2. Porcentaje de conversión de EBITDA a Flujo de Caja Libre.
  3. Evolución del CAPEX como porcentaje de ingresos en los últimos tres ejercicios.

Si pudieran adjuntar también el comparable del ejercicio anterior se lo agradeceríamos, así como cualquier matiz que consideren relevante (efectos extraordinarios, partidas no recurrentes, etc.) que pueda distorsionar la lectura de los ratios.

Quedo a su disposición para cualquier aclaración.

Atentamente,

Carlos Ferrer, CFA
Senior Portfolio Manager — Altea Capital Partners""",
    },
    {
        "id": "minorista_noticias",
        "remitente_nombre": "Andrés Vega",
        "remitente_email": "vegaandres74@hotmail.com",
        "remitente_perfil": "Accionista minorista veterano",
        "asunto": "¿Hay alguna novedad reciente que me deba preocupar?",
        "categoria": "Minorista · Requiere búsqueda web",
        "cuerpo": """Hola,

Llevo varios años con acciones de {empresa} y últimamente he leído algunos titulares hablando de novedades del sector y de la propia compañía. Como no soy inversor profesional, no tengo tiempo de seguir todo lo que se publica y me genera bastante incertidumbre.

¿Podríais resumirme en pocas líneas si en los últimos meses ha habido alguna noticia relevante —resultados, regulación, adquisiciones, cambios en la dirección, etc.— que pueda afectar a la cotización a medio plazo? Me ayudaría mucho tener una visión clara directamente de la fuente oficial para no quedarme solo con lo que dice la prensa.

Gracias por vuestra atención.

Saludos,
Andrés Vega""",
    },
    {
        "id": "institucional_kpis",
        "remitente_nombre": "Marina Solé",
        "remitente_email": "marina.sole@horizon-asset.com",
        "remitente_perfil": "Equity Analyst — Horizon Asset Management",
        "asunto": "Petición de KPIs operativos internos del Q4",
        "categoria": "Mayorista · Datos no públicos",
        "cuerpo": """Buenos días, equipo de Relación con Inversores,

Soy analista de renta variable en Horizon Asset Management y actualmente estamos modelando {empresa} de cara a la próxima revisión de nuestro fondo sectorial. Necesitaríamos disponer de los siguientes datos del cuarto trimestre cerrado, que no aparecen desglosados en el informe trimestral público:

  1. Margen EBITDA desglosado por línea de negocio.
  2. Porcentaje de ingresos recurrentes vs no recurrentes por segmento geográfico.
  3. Tasa de churn de clientes corporativos durante el trimestre.
  4. Coste medio de adquisición de cliente (CAC) y, si disponen del dato, LTV/CAC del último ejercicio.

Si alguno de estos datos puede facilitarse bajo NDA o como guidance no público, agradeceríamos poder agendar una llamada de 30 minutos con el equipo de IR a su mejor conveniencia durante las próximas dos semanas.

Quedamos a la espera de su respuesta.

Saludos cordiales,

Marina Solé
Equity Analyst — Horizon Asset Management""",
    },
]


def _correos_ir_renderizados():
    """Sustituye los placeholders {empresa} y {ticker} con el branding actual."""
    empresa = _BRANDING.get("empresa") or TICKER_FIJO or "la compañía"
    ticker = TICKER_FIJO or ""
    out = []
    for c in _CORREOS_IR:
        cuerpo = c["cuerpo"].replace("{empresa}", empresa).replace("{ticker}", ticker)
        out.append({**c, "cuerpo": cuerpo})
    return out


def _resolver_correo_ir(correo, datos):
    """Pide al modelo un borrador de respuesta para un correo de IR.

    Devuelve un dict con `puede_resolver`, `asunto_respuesta`, `cuerpo_respuesta`
    y `nota_interna`.
    """
    empresa = _BRANDING.get("empresa") or TICKER_FIJO or "la compañía"
    ticker = TICKER_FIJO or ""
    tabla = _texto_datos_para_prompt(datos) if datos else "(no hay datos financieros disponibles en este momento)"

    prompt = f"""Eres el equipo de Relación con Inversores de {empresa} ({ticker}).
Acabas de recibir el siguiente correo electrónico de un inversor.

[CORREO RECIBIDO]
De: {correo['remitente_nombre']} <{correo['remitente_email']}>
Perfil del remitente: {correo['remitente_perfil']}
Asunto: {correo['asunto']}

Cuerpo:
{correo['cuerpo']}
[FIN DEL CORREO]

Tu tarea:
1. Analiza si puedes responder a la consulta con (a) los datos financieros
   PÚBLICOS de Yahoo Finance que se adjuntan más abajo, o (b) información
   pública que puedas localizar mediante búsqueda web sobre {empresa}.
2. Si puedes responder, redacta un BORRADOR PROFESIONAL adecuado al perfil
   del remitente:
   - Minorista → lenguaje claro y didáctico, evita tecnicismos.
   - Profesional / institucional → tono técnico, conciso, cifras exactas.
   Usa cifras CONCRETAS y EXACTAS de los datos provistos cuando aplique.
   Formato europeo: separador de miles ".", decimal ",".
   No incluyas en el cuerpo ningún listado de URLs ni "Fuentes consultadas":
   la información debe estar integrada en la respuesta como hechos.
3. Si NO puedes responder porque los datos solicitados son internos, no
   públicos o no están disponibles ni en Yahoo ni en internet, marca
   `puede_resolver` = false. El borrador alternativo debe:
   (a) reconocer cortésmente la solicitud,
   (b) explicar honestamente que esa información no es pública o no se
       desglosa a ese nivel,
   (c) ofrecer lo que sí está disponible o proponer un canal alternativo
       (call con IR, reunión, próximo earnings call),
   (d) marcar entre corchetes [PENDIENTE: ...] los datos concretos que el
       equipo humano de IR deberá completar antes de enviar.

FORMATO DE SALIDA OBLIGATORIO — devuelve EXCLUSIVAMENTE un objeto JSON
válido, sin comentarios, sin texto antes ni después, sin acentos graves:

{{
  "puede_resolver": true,
  "asunto_respuesta": "Re: {correo['asunto']}",
  "cuerpo_respuesta": "Estimado/a ...\\n\\n[respuesta completa]\\n\\nUn saludo,\\nEquipo de Relación con Inversores — {empresa}",
  "nota_interna": "1-2 frases para el usuario: qué he podido resolver, qué datos he usado, qué he dejado pendiente."
}}
"""

    if datos:
        prompt += f"\nDatos financieros de Yahoo Finance disponibles:\n{tabla}\n"

    texto, _citas = llamar_ia_con_reintentos(
        prompt, max_tokens=2500, modelo=MODELO_POR_DEFECTO, permitir_busqueda=True,
    )

    import json as _json
    bloque = re.search(r"\{.*\}", texto or "", re.DOTALL)
    if not bloque:
        return {
            "puede_resolver": False,
            "asunto_respuesta": f"Re: {correo['asunto']}",
            "cuerpo_respuesta": (texto or "").strip() or "[La IA no devolvió respuesta]",
            "nota_interna": "La IA no devolvió JSON válido; se muestra el texto bruto.",
        }
    try:
        parsed = _json.loads(bloque.group(0), strict=False)
    except _json.JSONDecodeError:
        return {
            "puede_resolver": False,
            "asunto_respuesta": f"Re: {correo['asunto']}",
            "cuerpo_respuesta": bloque.group(0),
            "nota_interna": "JSON no parseable; se muestra el bloque tal cual.",
        }
    # Saneo defensivo
    parsed.setdefault("puede_resolver", False)
    parsed.setdefault("asunto_respuesta", f"Re: {correo['asunto']}")
    parsed.setdefault("cuerpo_respuesta", "")
    parsed.setdefault("nota_interna", "")
    return parsed


@app.route("/relacion-inversores")
def relacion_inversores():
    correos = _correos_ir_renderizados()
    return render_template("relacion_inversores.html", correos=correos)


@app.route("/relacion-inversores/resolver", methods=["POST"])
def relacion_inversores_resolver():
    from flask import jsonify
    data = request.get_json(silent=True) or {}
    correo_id = (data.get("correo_id") or "").strip()
    correo = next((c for c in _correos_ir_renderizados() if c["id"] == correo_id), None)
    if not correo:
        return jsonify({"ok": False, "error": "Correo no encontrado"}), 404

    datos = _cargar_datos_ticker_fijo() if TICKER_FIJO else None
    try:
        resultado = _resolver_correo_ir(correo, datos)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al resolver: {e}"}), 500

    return jsonify({
        "ok": True,
        "correo_id": correo_id,
        "destinatario_nombre": correo["remitente_nombre"],
        "destinatario_email": correo["remitente_email"],
        **resultado,
    })


@app.route("/relacion-inversores/enviar", methods=["POST"])
def relacion_inversores_enviar():
    from flask import jsonify
    from datetime import datetime as _dt
    data = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "timestamp": _dt.now().strftime("%d/%m/%Y %H:%M"),
        "destinatario_nombre": data.get("destinatario_nombre", ""),
        "destinatario_email": data.get("destinatario_email", ""),
        "asunto": data.get("asunto", ""),
    })


@app.route("/descargar_word", methods=["POST"])
def descargar_word():
    cache_id = request.form.get("cache_id", "")
    cached = _download_cache.get(cache_id)
    if not cached:
        return "Sesión expirada. Por favor, realiza el análisis de nuevo.", 400

    datos = cached["datos"]
    nota = cached["nota"]
    try:
        buffer = crear_documento_word(datos, nota)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"informe_{datos['ticker']}.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return f"Error generando documento: {str(e)}", 500


@app.route("/descargar_comparativo", methods=["POST"])
def descargar_comparativo():
    cache_id = request.form.get("cache_id", "")
    cached = _download_cache.get(cache_id)
    if not cached:
        return "Sesión expirada. Por favor, realiza la comparación de nuevo.", 400

    datos_empresas = cached["datos_empresas"]
    analisis = cached["analisis"]
    try:
        buffer = crear_documento_comparativo(datos_empresas, analisis)
        nombre = "_vs_".join([d["ticker"] for d in datos_empresas])
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"comparativo_{nombre}.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return f"Error generando documento: {str(e)}", 500


@app.route("/descargar_pdf", methods=["POST"])
def descargar_pdf():
    cache_id = request.form.get("cache_id", "")
    cached = _download_cache.get(cache_id)
    if not cached or "datos" not in cached:
        return "Sesión expirada. Por favor, realiza el análisis de nuevo.", 400

    datos = cached["datos"]
    nota = cached["nota"]
    try:
        buffer = crear_documento_pdf(datos, nota)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"informe_{datos['ticker']}.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        return f"Error generando documento: {str(e)}", 500


# --- Funcionalidades mock (navegación completa, sin lógica productiva) ---

@app.route("/presupuesto")
def presupuesto():
    return render_template("presupuesto.html")


@app.route("/conciliacion")
def conciliacion():
    return render_template("conciliacion.html")


@app.route("/radar-normativo")
def radar_normativo():
    alertas = [
        {
            "categoria": "Fiscal",
            "tag": "tag-red",
            "color": "#DA291C",
            "jurisdiccion": "España",
            "impacto": "Alto",
            "fecha": "18/04/2026",
            "fuente": "BOE",
            "titulo": "Nueva obligación de reporte trimestral para pagos internacionales",
            "resumen": (
                "La AEAT publica la Orden HAC/392/2026 que amplía el Modelo 349 e introduce "
                "un reporte trimestral obligatorio para operaciones de servicios intragrupo "
                "por encima de 50.000 €. Entrada en vigor: 1 de julio de 2026."
            ),
        },
        {
            "categoria": "Contable",
            "tag": "tag-blue",
            "color": "#00A3E0",
            "jurisdiccion": "Unión Europea",
            "impacto": "Medio",
            "fecha": "15/04/2026",
            "fuente": "EFRAG / DOUE",
            "titulo": "Revisión de NIIF 18 — presentación y desglose de estados financieros",
            "resumen": (
                "La EFRAG emite dictamen favorable a la adopción de NIIF 18, que redefine "
                "subtotales obligatorios (operativo, financiación, inversión) y amplía las "
                "medidas definidas por la dirección. Primera aplicación: ejercicios 2027."
            ),
        },
        {
            "categoria": "Laboral",
            "tag": "tag-orange",
            "color": "#ED8B00",
            "jurisdiccion": "España",
            "impacto": "Medio",
            "fecha": "11/04/2026",
            "fuente": "BOE",
            "titulo": "Actualización del SMI y cotizaciones sociales para 2026",
            "resumen": (
                "Real Decreto 298/2026 que fija el SMI en 1.230 €/mes y actualiza los "
                "topes máximos de cotización. Revisar masa salarial y provisiones laborales."
            ),
        },
        {
            "categoria": "ESG",
            "tag": "tag-green",
            "color": "#86BC25",
            "jurisdiccion": "Unión Europea",
            "impacto": "Alto",
            "fecha": "08/04/2026",
            "fuente": "DOUE",
            "titulo": "CSRD — publicación de las NEIS sector specific para el ejercicio 2026",
            "resumen": (
                "La Comisión Europea publica los estándares sectoriales de la CSRD, que "
                "serán de aplicación obligatoria a partir del ejercicio 2026 para empresas "
                "cotizadas del sector financiero y energético."
            ),
        },
        {
            "categoria": "Financiera",
            "tag": "tag-black",
            "color": "#000000",
            "jurisdiccion": "Unión Europea",
            "impacto": "Bajo",
            "fecha": "03/04/2026",
            "fuente": "BCE",
            "titulo": "Guía técnica sobre el uso de LLMs en procesos KYC y AML",
            "resumen": (
                "El BCE publica principios supervisores para la utilización de modelos de "
                "lenguaje en procesos antiblanqueo, con foco en explicabilidad, trazabilidad "
                "y supervisión humana sobre las decisiones automatizadas."
            ),
        },
    ]
    return render_template("radar_normativo.html", alertas=alertas)


@app.route("/noticias")
def noticias():
    noticias_lista = [
        {
            "categoria": "M&A", "tag": "tag-green", "banner": "#43B02A",
            "fecha": "20/04/2026", "fuente": "Reuters",
            "titular": "BlackRock lidera el consorcio que adquiere Klarna por 14,2B USD",
            "resumen": "La operación convierte a la fintech sueca en la mayor OPA del sector BNPL en la última década.",
        },
        {
            "categoria": "Regulación", "tag": "tag-blue", "banner": "#00A3E0",
            "fecha": "19/04/2026", "fuente": "Bloomberg",
            "titular": "La EBA publica la guía definitiva sobre el uso de IA en procesos KYC",
            "resumen": "El marco europeo establece requisitos de auditabilidad, explicabilidad y supervisión humana sobre modelos generativos.",
        },
        {
            "categoria": "Mercados", "tag": "tag-black", "banner": "#000000",
            "fecha": "19/04/2026", "fuente": "Financial Times",
            "titular": "Las fintechs europeas cierran la semana con un rally del 4,2%",
            "resumen": "Adyen, Nu Holdings y Wise lideran las subidas tras los resultados del primer trimestre por encima del consenso.",
        },
        {
            "categoria": "Tecnología", "tag": "tag-orange", "banner": "#ED8B00",
            "fecha": "18/04/2026", "fuente": "Expansión",
            "titular": "CaixaBank firma un acuerdo con Anthropic para generalizar Claude en su banca privada",
            "resumen": "El despliegue cubrirá 3.200 gestores y se integrará con la plataforma propia de asesoramiento del banco.",
        },
        {
            "categoria": "Corporate", "tag": "tag-green", "banner": "#86BC25",
            "fecha": "17/04/2026", "fuente": "Cinco Días",
            "titular": "Endesa presenta un plan ESG de 4,5B € hasta 2030 centrado en hidrógeno verde",
            "resumen": "La compañía prevé triplicar su capacidad instalada renovable y emitir bonos verdes por 1,2B € en 2026.",
        },
        {
            "categoria": "M&A", "tag": "tag-green", "banner": "#43B02A",
            "fecha": "16/04/2026", "fuente": "Reuters",
            "titular": "Telefónica y Orange exploran una fusión de sus redes móviles en España",
            "resumen": "Fuentes próximas a la negociación indican que un eventual acuerdo se someterá a revisión por la CNMC.",
        },
    ]
    return render_template("noticias.html", noticias=noticias_lista)


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    enviado = False
    if request.method == "POST":
        # Mock: no se persiste ni envía el mensaje, solo se reconoce la acción.
        enviado = True
    return render_template("contacto.html", enviado=enviado)


if __name__ == "__main__":
    if TICKER_FIJO:
        print(f"\n[DFin AI] Precargando datos de Yahoo Finance para {TICKER_FIJO}…")
        try:
            _cargar_datos_ticker_fijo()
            nombre = _BRANDING["empresa"]
            print(f"[DFin AI] Aplicación dedicada a: {nombre} ({TICKER_FIJO})\n")
        except Exception as _e:
            print(f"[DFin AI] AVISO: no se pudieron precargar datos de {TICKER_FIJO}: {_e}\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
