import os
import io
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

load_dotenv()

app = Flask(__name__)

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

# Cache en memoria para evitar re-llamar a las APIs al descargar Word
_download_cache = {}


def _normalizar_modelo(modelo):
    """Devuelve el modelo si es válido, o el modelo por defecto."""
    if modelo in MODELOS_DISPONIBLES:
        return modelo
    return MODELO_POR_DEFECTO


def llamar_claude_con_reintentos(prompt, max_tokens, modelo, max_reintentos=4):
    """Llama a la API de Anthropic con reintentos y backoff exponencial.

    Reintenta automáticamente en errores transitorios (529 overloaded, 429
    rate limit, 500, 503). En el último intento relanza la excepción con
    un mensaje amigable en español.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=0)
    errores_reintentables = (
        anthropic.APIStatusError,
        anthropic.APIConnectionError,
        anthropic.RateLimitError,
    )
    status_reintentables = {429, 500, 502, 503, 504, 529}

    ultimo_error = None
    for intento in range(max_reintentos):
        try:
            message = client.messages.create(
                model=modelo,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except errores_reintentables as e:
            ultimo_error = e
            status = getattr(e, "status_code", None)
            if status is not None and status not in status_reintentables:
                raise
            if intento < max_reintentos - 1:
                espera = 2 ** intento  # 1s, 2s, 4s, 8s
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


def llamar_gemini_con_reintentos(prompt, max_tokens, modelo, max_reintentos=4):
    """Llama a la API de Google Gemini con reintentos y backoff exponencial.

    Reintenta en errores transitorios (429 rate limit, 500, 503, timeouts).
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

    ultimo_error = None
    for intento in range(max_reintentos):
        try:
            cliente = genai.GenerativeModel(modelo)
            respuesta = cliente.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens},
            )
            return respuesta.text
        except errores_reintentables as e:
            ultimo_error = e
            if intento < max_reintentos - 1:
                espera = 2 ** intento  # 1s, 2s, 4s, 8s
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


def llamar_ia_con_reintentos(prompt, max_tokens, modelo):
    """Despacha la llamada al proveedor de IA según el modelo elegido."""
    modelo = _normalizar_modelo(modelo)
    if modelo in MODELOS_ANTHROPIC:
        return llamar_claude_con_reintentos(prompt, max_tokens, modelo)
    return llamar_gemini_con_reintentos(prompt, max_tokens, modelo)


def obtener_datos_financieros(ticker_symbol):
    """Obtiene datos financieros de Yahoo Finance para un ticker dado."""
    ticker = yf.Ticker(ticker_symbol)

    # Inicializar sesión con history antes de obtener fundamentales
    ticker.history(period="1d")

    income_stmt = ticker.income_stmt
    if income_stmt is None or income_stmt.empty:
        return None

    nombre = ticker.info.get("shortName", ticker_symbol.upper())

    datos = {"ticker": ticker_symbol.upper(), "nombre": nombre, "periodos": []}

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

        pct = lambda parte: round((parte / ingresos) * 100, 2) if ingresos else 0.0

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
            }
        )

    return datos


def generar_nota_memoria(datos, modelo):
    """Genera nota de memoria explicativa usando el modelo de IA elegido."""
    tabla_texto = f"Empresa: {datos['nombre']} ({datos['ticker']})\n\n"
    for p in datos["periodos"]:
        tabla_texto += f"""Periodo: {p['periodo']}
  Ingresos: {p['ingresos']:,.0f}
  Coste de ventas: {p['coste_ventas']:,.0f}
  Margen bruto: {p['margen_bruto']:,.0f} ({p['pct_margen_bruto']}%)
  Gastos operativos: {p['gastos_operativos']:,.0f} ({p['pct_gastos_operativos']}%)
  EBITDA: {p['ebitda']:,.0f} ({p['pct_ebitda']}%)
  Beneficio neto: {p['beneficio_neto']:,.0f} ({p['pct_beneficio_neto']}%)
"""

    prompt = f"""Eres un analista financiero experto. Genera una nota de memoria explicativa
en español sobre los resultados financieros de la siguiente empresa.
La nota debe ser profesional, incluir análisis de tendencias entre periodos,
destacar fortalezas y debilidades, y ofrecer una conclusión.

Datos financieros:
{tabla_texto}"""

    return llamar_ia_con_reintentos(prompt, max_tokens=2000, modelo=modelo)


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

Datos financieros comparativos:
{texto}"""

    return llamar_ia_con_reintentos(prompt, max_tokens=2500, modelo=modelo)


def crear_documento_word(datos, nota):
    """Crea un documento Word con los datos financieros y la nota de memoria."""
    doc = Document()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    titulo = doc.add_heading(f"Informe Financiero — {datos['nombre']}", level=0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in titulo.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)

    doc.add_paragraph(f"Ticker: {datos['ticker']}")
    doc.add_paragraph("")

    doc.add_heading("Datos Financieros", level=1)

    headers = ["Métrica"] + [p["periodo"] for p in datos["periodos"]]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True

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
        for i, p in enumerate(datos["periodos"]):
            valor = f"{p[key]:,.0f}"
            if pct_key:
                valor += f" ({p[pct_key]}%)"
            row.cells[i + 1].text = valor

    doc.add_paragraph("")
    doc.add_heading("Nota de Memoria Explicativa", level=1)
    doc.add_paragraph(nota)

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

    titulo = doc.add_heading("Informe Comparativo Financiero", level=0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in titulo.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)

    empresas_nombres = ", ".join([d["nombre"] for d in datos_empresas])
    doc.add_paragraph(f"Empresas comparadas: {empresas_nombres}")
    doc.add_paragraph("")

    doc.add_heading("Tabla Comparativa", level=1)

    headers = ["Métrica"] + [d["nombre"] for d in datos_empresas]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True

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
        for i, datos in enumerate(datos_empresas):
            p = datos["periodos"][0]  # Último periodo
            valor = f"{p[key]:,.0f}"
            if pct_key:
                valor += f" ({p[pct_key]}%)"
            row.cells[i + 1].text = valor

    doc.add_paragraph("")
    doc.add_heading("Análisis Comparativo", level=1)
    doc.add_paragraph(analisis)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def formatear_numero(valor):
    """Formatea números grandes para mostrar en la UI."""
    if abs(valor) >= 1_000_000_000:
        return f"{valor / 1_000_000_000:,.2f}B"
    elif abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:,.2f}M"
    else:
        return f"{valor:,.0f}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analisis", methods=["GET", "POST"])
def analisis():
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

            nota = generar_nota_memoria(datos, modelo)
            nota_html = markdown.markdown(nota)

            cache_id = str(uuid.uuid4())
            _download_cache[cache_id] = {"datos": datos, "nota": nota}

            return render_template(
                "resultado.html",
                datos=datos,
                nota=nota_html,
                cache_id=cache_id,
                formatear=formatear_numero,
            )
        except Exception as e:
            return render_template(
                "analisis.html",
                error=f"Error: {str(e)}",
                modelo_seleccionado=modelo,
            )

    return render_template("analisis.html", modelo_seleccionado=MODELO_POR_DEFECTO)


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
            analisis_html = markdown.markdown(analisis)

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
