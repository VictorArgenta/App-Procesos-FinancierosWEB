"""Diccionario funcional corporativo + resolver seguro de fórmulas.

Alimenta la funcionalidad "Habla con tus datos":

- Parsea Empresas/{TICKER}/diccionario.txt (formato bloque plano).
- Resuelve fórmulas entre corchetes (`[X] + [Y] * 100`) sobre los datos
  estructurados obtenidos de la API financiera, con un visitor AST seguro
  (solo + - * / ( )).
- Soporta prefijos pyg. / balance. / cashflow. para desambiguar partidas
  presentes en varios estados.
- Soporta fórmulas que referencian a otras entradas del diccionario
  (recursividad), con detección de ciclos.
"""

from __future__ import annotations

import ast
import operator
import re
import unicodedata
from pathlib import Path
from typing import Any

# --- Config --------------------------------------------------------------

NOMBRE_FICHERO = "diccionario.txt"
CLAVES_PERMITIDAS = {
    "definicion", "sinonimos", "formula", "presentacion", "tags",
}
PREFIJOS_ESTADO = {"pyg", "balance", "cashflow", "income", "income_statement", "balance_sheet"}
_MAPEO_PREFIJOS = {
    "pyg": "income_statement",
    "income": "income_statement",
    "income_statement": "income_statement",
    "balance": "balance_sheet",
    "balance_sheet": "balance_sheet",
    "cashflow": "cashflow",
}


# --- Normalización de texto para lookup tolerante ------------------------

def _normalizar(texto: str) -> str:
    """Normaliza para comparaciones: lower, sin acentos, trim de espacios dobles.

    Conserva signos como `/`, `&`, paréntesis porque son significativos
    (ej. "Compra / venta neta de inversiones" vs "Compra venta neta").
    """
    if texto is None:
        return ""
    s = unicodedata.normalize("NFKD", str(texto))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


# --- Parser del fichero --------------------------------------------------

def parsear_diccionario(texto: str) -> dict[str, dict[str, Any]]:
    """Convierte el texto crudo del diccionario a un dict por nombre canónico.

    Formato esperado (ejemplo):

        EBITDA
        Definicion: Resultado operativo antes de amortizaciones...
        Sinonimos: margen de maniobra; EBIT + D&A
        Tags: pyg, rentabilidad

    Devuelve `{nombre_canonico: {"nombre": ..., "clave_norm": ..., "campos": {...}}}`.
    Líneas que empiezan por "#" son comentarios y se ignoran.
    """
    entradas: dict[str, dict[str, Any]] = {}
    bloque_actual: dict[str, Any] | None = None

    lineas = (texto or "").splitlines()
    i = 0
    while i < len(lineas):
        raw = lineas[i]
        linea = raw.rstrip()
        stripped = linea.strip()

        # Comentario o separador
        if not stripped or stripped.startswith("#"):
            # Línea en blanco cierra el bloque en curso
            if not stripped and bloque_actual is not None:
                _registrar_bloque(bloque_actual, entradas)
                bloque_actual = None
            i += 1
            continue

        # ¿Es una clave campo "Clave: valor"?
        campo_match = re.match(r"^([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]+)\s*:\s*(.*)$", stripped)
        es_clave = False
        if campo_match and bloque_actual is not None:
            clave_lower = _sin_acentos(campo_match.group(1).lower())
            if clave_lower in CLAVES_PERMITIDAS:
                es_clave = True
                valor = campo_match.group(2).strip()
                # Soporte continuación: líneas siguientes sangradas (empiezan por espacio)
                # se consideran continuación del valor.
                j = i + 1
                while j < len(lineas):
                    nxt = lineas[j]
                    if not nxt.strip() or nxt.strip().startswith("#"):
                        break
                    # Nueva clave? → fin de continuación
                    nxt_match = re.match(r"^([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]+)\s*:\s*", nxt.strip())
                    if nxt_match and _sin_acentos(nxt_match.group(1).lower()) in CLAVES_PERMITIDAS:
                        break
                    if nxt.startswith((" ", "\t")):
                        valor = (valor + " " + nxt.strip()).strip()
                        j += 1
                        continue
                    break
                bloque_actual["campos"][clave_lower] = valor
                i = j
                continue

        if not es_clave:
            # Línea que NO es clave conocida → cabecera de un nuevo bloque
            # (cerramos el anterior si existe)
            if bloque_actual is not None:
                _registrar_bloque(bloque_actual, entradas)
            nombre = stripped
            bloque_actual = {
                "nombre": nombre,
                "clave_norm": _normalizar(nombre),
                "campos": {},
            }
            i += 1
            continue

    if bloque_actual is not None:
        _registrar_bloque(bloque_actual, entradas)

    return entradas


def _sin_acentos(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _registrar_bloque(bloque: dict, entradas: dict) -> None:
    clave = bloque["clave_norm"]
    if not clave:
        return
    entradas[clave] = bloque


# --- Resolver de fórmulas ------------------------------------------------

class ResolverError(ValueError):
    """Error controlado del resolver (se puede mostrar al usuario)."""


# Operadores permitidos en el AST
_OPERADORES_BIN = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_OPERADORES_UN = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _construir_lookup_dataset(datos: dict) -> dict[str, dict[str, Any]]:
    """Convierte el dict de `obtener_datos_financieros` en un lookup normalizado.

    Devuelve:
        {
            "<nombre_normalizado>": {
                "fuente": "pyg|balance|cashflow|resumen",
                "valor_ultimo": float | None,
                "serie": {<periodo>: float|None, ...},
                "nombre_original": str,
            },
            ...
        }

    Reglas de precedencia cuando un nombre aparece en varios sitios:
      - El lookup almacena la primera ocurrencia encontrada por orden
        "resumen" (campos normalizados de PyG) → income_statement →
        balance_sheet → cashflow.
      - Las ocurrencias posteriores se guardan en "duplicados" con su
        fuente, permitiendo desambiguar con prefijos.
    """
    lookup: dict[str, dict[str, Any]] = {}

    # 1) Campos del "resumen" (datos.periodos) — PyG de alto nivel
    periodos = datos.get("periodos") or []
    if periodos:
        ultimo = periodos[0]  # Yahoo entrega del más reciente al más antiguo
        _ETIQUETAS_RESUMEN = {
            "ingresos": "Ingresos totales",
            "coste_ventas": "Coste de los ingresos",
            "margen_bruto": "Beneficio bruto",
            "gastos_operativos": "Gastos operativos",
            "ebitda": "EBITDA",
            "ebit": "EBIT",
            "da": "Amortizaciones (D&A)",
            "sga": "Gastos generales y de administración",
            "rd": "Investigación y desarrollo",
            "ingresos_financieros": "Ingresos por intereses",
            "gastos_financieros": "Gastos por intereses",
            "resultado_financiero_neto": "Resultado financiero neto",
            "resultado_antes_impuestos": "Beneficio antes de impuestos",
            "impuestos": "Provisión para impuestos sobre la renta",
            "beneficio_neto": "Beneficio neto",
            "bpa_basico": "BPA básico",
            "bpa_diluido": "BPA diluido",
        }
        for clave, etiqueta in _ETIQUETAS_RESUMEN.items():
            if clave not in ultimo:
                continue
            serie = {}
            for p in periodos:
                v = p.get(clave)
                serie[str(p.get("periodo", ""))] = v
            registro = {
                "fuente": "resumen",
                "valor_ultimo": ultimo.get(clave),
                "serie": serie,
                "nombre_original": etiqueta,
                "duplicados": [],
            }
            lookup[_normalizar(etiqueta)] = registro

    # 2) Filas crudas de los tres estados
    estados = datos.get("estados") or {}
    for clave_estado in ("income_statement", "balance_sheet", "cashflow"):
        bloque = estados.get(clave_estado) or {}
        periodos_estado = bloque.get("periodos") or []
        if not periodos_estado:
            continue
        filas = bloque.get("filas") or []
        for fila in filas:
            concepto = fila.get("concepto") or ""
            valores = fila.get("valores") or []
            if not concepto:
                continue
            # Saltar TTM: si el primer periodo es TTM, consideramos valor_ultimo
            # como el siguiente ejercicio cerrado.
            idxs_validos = [
                i for i, p in enumerate(periodos_estado)
                if str(p).strip().upper() != "TTM"
                and not str(p).strip().upper().startswith("TTM ")
            ]
            if not idxs_validos:
                continue
            serie = {
                str(periodos_estado[i]): valores[i] if i < len(valores) else None
                for i in idxs_validos
            }
            # Valor último = primer índice válido (Yahoo ordena del más
            # reciente al más antiguo).
            valor_ult = valores[idxs_validos[0]] if idxs_validos[0] < len(valores) else None

            nombre_norm = _normalizar(concepto)
            registro = {
                "fuente": clave_estado,
                "valor_ultimo": valor_ult,
                "serie": serie,
                "nombre_original": concepto,
            }
            existente = lookup.get(nombre_norm)
            if not existente:
                registro["duplicados"] = []
                lookup[nombre_norm] = registro
            else:
                existente.setdefault("duplicados", []).append(registro)

    return lookup


class _EvalSeguro(ast.NodeVisitor):
    """AST visitor que solo acepta + - * / (), literales numéricos y
    nombres pre-sustituidos por valores."""

    def __init__(self, variables: dict[str, float]):
        self.variables = variables

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ResolverError(f"Constante no numérica: {node.value!r}")

    def visit_Num(self, node):  # Py<3.8 compat
        return float(node.n)

    def visit_BinOp(self, node):
        op_fn = _OPERADORES_BIN.get(type(node.op))
        if op_fn is None:
            raise ResolverError("Operador no permitido")
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left is None or right is None:
            raise ResolverError("Operando no disponible (None)")
        if op_fn is operator.truediv and right == 0:
            raise ResolverError("División por cero")
        return op_fn(left, right)

    def visit_UnaryOp(self, node):
        op_fn = _OPERADORES_UN.get(type(node.op))
        if op_fn is None:
            raise ResolverError("Operador unario no permitido")
        val = self.visit(node.operand)
        if val is None:
            raise ResolverError("Operando unario no disponible")
        return op_fn(val)

    def visit_Name(self, node):
        if node.id not in self.variables:
            raise ResolverError(f"Variable desconocida: {node.id}")
        v = self.variables[node.id]
        if v is None:
            raise ResolverError("Partida sin valor en este periodo")
        return float(v)

    def visit_Paren(self, node):  # defensivo
        return self.visit(node.body)

    def generic_visit(self, node):
        raise ResolverError(f"Nodo no permitido: {type(node).__name__}")


def resolver_formula(
    formula: str,
    datos: dict,
    diccionario: dict | None = None,
    _stack: set | None = None,
) -> dict:
    """Evalúa una fórmula con corchetes `[X]` contra el dataset estructurado.

    Devuelve un dict:
        {
            "ok": bool,
            "valor": float | None,
            "trace": [(etiqueta_original, valor_numerico), ...],
            "error": str | None,
        }

    Si una referencia `[X]` no se encuentra como partida, intenta como
    entrada del diccionario con `Formula:` (recursión con detección de
    ciclos).
    """
    if not formula or not formula.strip():
        return {"ok": False, "valor": None, "trace": [], "error": "Fórmula vacía"}

    diccionario = diccionario or {}
    _stack = _stack if _stack is not None else set()
    lookup = _construir_lookup_dataset(datos)

    # 1) Extraer referencias [X] y sustituirlas por variables únicas.
    partes = re.findall(r"\[([^\]]+)\]", formula)
    if not partes:
        return {"ok": False, "valor": None, "trace": [],
                "error": "La fórmula no contiene referencias [Nombre]"}

    variables: dict[str, float] = {}
    trace: list[tuple[str, float | None]] = []
    sustituciones: dict[str, str] = {}  # ref original → nombre_variable

    for idx, ref in enumerate(partes):
        if ref in sustituciones:
            continue
        valor, etiqueta = _resolver_referencia(
            ref, lookup, diccionario, datos, _stack
        )
        var_name = f"v_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', ref)[:32]}"
        sustituciones[ref] = var_name
        variables[var_name] = valor
        trace.append((etiqueta, valor))

    # 2) Reemplazar [X] por el nombre de variable en la fórmula.
    expr = formula
    # Reemplazamos por orden de longitud descendente para evitar colisiones.
    for ref in sorted(sustituciones, key=len, reverse=True):
        expr = expr.replace(f"[{ref}]", sustituciones[ref])

    # 3) Parsear y evaluar con el visitor seguro.
    try:
        tree = ast.parse(expr, mode="eval")
        resultado = _EvalSeguro(variables).visit(tree)
    except ResolverError as e:
        return {"ok": False, "valor": None, "trace": trace, "error": str(e)}
    except SyntaxError as e:
        return {"ok": False, "valor": None, "trace": trace,
                "error": f"Sintaxis inválida: {e.msg}"}
    except ZeroDivisionError:
        return {"ok": False, "valor": None, "trace": trace,
                "error": "División por cero"}

    return {"ok": True, "valor": float(resultado), "trace": trace, "error": None}


def _resolver_referencia(
    ref: str,
    lookup: dict,
    diccionario: dict,
    datos: dict,
    stack: set,
) -> tuple[float | None, str]:
    """Resuelve una referencia `[X]` a (valor_ultimo, etiqueta_original).

    Orden de resolución:
      1. Prefijo explícito `pyg.X` / `balance.X` / `cashflow.X`.
      2. Lookup directo en el dataset estructurado.
      3. Sinónimo del diccionario que apunte a una partida real.
      4. Otra entrada del diccionario con `Formula:` → recursión.
    """
    ref_limpia = ref.strip()
    prefijo = None
    cuerpo = ref_limpia

    if "." in ref_limpia:
        p, _, resto = ref_limpia.partition(".")
        if _normalizar(p).replace(" ", "") in PREFIJOS_ESTADO:
            prefijo = _MAPEO_PREFIJOS[_normalizar(p).replace(" ", "")]
            cuerpo = resto.strip()

    clave_norm = _normalizar(cuerpo)
    registro = lookup.get(clave_norm)

    if registro:
        if prefijo:
            if registro.get("fuente") != prefijo:
                # Buscar en los duplicados
                for dup in registro.get("duplicados", []):
                    if dup.get("fuente") == prefijo:
                        return dup.get("valor_ultimo"), dup.get("nombre_original", cuerpo)
                return None, cuerpo
        return registro.get("valor_ultimo"), registro.get("nombre_original", cuerpo)

    # No está como partida directa. Probar sinónimos del diccionario.
    for _k, entrada in diccionario.items():
        campos = entrada.get("campos", {})
        sinonimos_raw = campos.get("sinonimos") or ""
        sinonimos = [s.strip() for s in re.split(r"[;,]", sinonimos_raw) if s.strip()]
        if any(_normalizar(s) == clave_norm for s in sinonimos):
            # El sinónimo apunta al nombre canónico de la entrada
            canonico = entrada.get("nombre", "")
            canonico_norm = _normalizar(canonico)
            if canonico_norm in lookup:
                reg = lookup[canonico_norm]
                return reg.get("valor_ultimo"), reg.get("nombre_original", canonico)
            # El canónico tampoco está en el dataset; quizá tiene Formula
            if (campos.get("formula") or "").strip():
                return _resolver_entrada_diccionario(
                    entrada, lookup, diccionario, datos, stack,
                )

    # Última oportunidad: la referencia es el nombre de otra entrada con Formula
    entrada = diccionario.get(clave_norm)
    if entrada and (entrada.get("campos", {}).get("formula") or "").strip():
        return _resolver_entrada_diccionario(
            entrada, lookup, diccionario, datos, stack,
        )

    return None, cuerpo


def _resolver_entrada_diccionario(
    entrada: dict,
    lookup: dict,
    diccionario: dict,
    datos: dict,
    stack: set,
) -> tuple[float | None, str]:
    nombre = entrada.get("nombre", "")
    clave = entrada.get("clave_norm", "")
    if clave in stack:
        raise ResolverError(f"Ciclo detectado al resolver '{nombre}'")
    stack_nuevo = set(stack) | {clave}
    formula = (entrada.get("campos", {}).get("formula") or "").strip()
    if not formula:
        return None, nombre
    res = resolver_formula(formula, datos, diccionario, _stack=stack_nuevo)
    if res.get("ok"):
        return res.get("valor"), nombre
    return None, nombre


# --- IO: carga y guardado por empresa -----------------------------------

def _ruta_diccionario(ticker: str, raiz_empresas: Path) -> Path:
    return raiz_empresas / ticker / NOMBRE_FICHERO


def cargar_diccionario_empresa(ticker: str, raiz_empresas: Path) -> tuple[dict, str]:
    """Devuelve (entradas_parseadas, texto_crudo). Si no existe el fichero,
    devuelve (dict vacío, cadena vacía)."""
    if not ticker:
        return {}, ""
    ruta = _ruta_diccionario(ticker, raiz_empresas)
    if not ruta.exists():
        return {}, ""
    try:
        texto = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}, ""
    return parsear_diccionario(texto), texto


def guardar_diccionario_empresa(ticker: str, texto: str, raiz_empresas: Path) -> Path:
    if not ticker:
        raise ValueError("ticker vacío")
    ruta = _ruta_diccionario(ticker, raiz_empresas)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto or "", encoding="utf-8")
    return ruta


def diccionario_a_texto_prompt(entradas: dict) -> str:
    """Serializa el diccionario a un bloque compacto para inyectar en prompts."""
    if not entradas:
        return ""
    partes = []
    for _k, e in entradas.items():
        nombre = e.get("nombre", "")
        campos = e.get("campos", {})
        linea = [f"- {nombre}"]
        if campos.get("definicion"):
            linea.append(f"  · def: {campos['definicion']}")
        if campos.get("sinonimos"):
            linea.append(f"  · aliases: {campos['sinonimos']}")
        if campos.get("formula"):
            linea.append(f"  · fórmula: {campos['formula']}")
        if campos.get("presentacion"):
            linea.append(f"  · presentar: {campos['presentacion']}")
        partes.append("\n".join(linea))
    return "\n".join(partes)
