# -*- coding: utf-8 -*-
"""
Maquetas de módulos adicionales — sólo para la entidad META.

Cada entrada del diccionario describe un módulo que se renderiza con la
plantilla `templates/mock_modulo.html`. El objetivo es presentar al usuario
una visión completa del ecosistema DFin AI con datos y argumentos realistas
pero *fijos*, como si el panel estuviera conectado al stack EPM corporativo
(Oracle EPM Cloud, OneStream, SAP Group Reporting, SAP S/4HANA, Workday,
Snowflake, etc.). No hay llamadas reales a ningún backend.

Las cifras provienen de las últimas cuentas anuales publicadas de META
Platforms, Inc. (FY2024) y las guías/consenso de analistas disponibles a
cierre de 2025, redondeadas y simplificadas para fines de demostración.

Esquema de cada módulo
----------------------
    slug: {
        "titulo":   str,
        "subtitulo": str,
        "vision":   "ceo" | "cfo" | "equipo",
        "fuente":   str,          # texto del chip "origen EPM"
        "ultima":   str,          # timestamp mostrado
        "kpis":     [ {label, valor, delta?, tono?}, ... ],
        "grafico":  {
            "tipo": "line" | "bar" | "waterfall" | "mixed" | "donut",
            "titulo": str,
            "serie": [...],
        },
        "grafico_sec": opcional, mismo formato que `grafico`,
        "bloques":  [ {titulo, bullets: [...]}, ... ],
        "cta":      opcional lista de accesos secundarios,
    }
"""

MOCK_MONEDA = "USD"


def _kpi(label, valor, delta=None, tono=None):
    d = {"label": label, "valor": valor}
    if delta is not None:
        d["delta"] = delta
    if tono is not None:
        d["tono"] = tono
    return d


# ---------------------------------------------------------------------------
# CEO · dirección general
# ---------------------------------------------------------------------------

_CEO = {
    "briefing-diario": {
        "titulo": "Briefing diario del CEO",
        "subtitulo": "Lo que necesitas saber antes de las 9:00",
        "vision": "ceo",
        "fuente": "Oracle EPM · Snowflake · Factiva",
        "ultima": "Hoy · 07:45",
        "kpis": [
            _kpi("Ingresos MTD", "USD 11,8 B", "+6,4 % vs plan", "pos"),
            _kpi("EBIT MTD", "USD 4,9 B", "+3,1 % vs plan", "pos"),
            _kpi("DAU Family of Apps", "3,47 B", "+0,8 % w/w", "pos"),
            _kpi("Reality Labs — pérdida MTD", "USD 1,4 B", "+USD 0,2 B vs plan", "neg"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Ingresos diarios de publicidad · últimas 4 semanas (USD M)",
            "serie": [412, 418, 421, 408, 425, 431, 429, 438, 441, 436, 450, 462,
                      458, 465, 471, 468, 480, 492, 489, 497, 504, 510, 518, 515,
                      528, 533, 541, 538],
        },
        "bloques": [
            {
                "titulo": "Lo imprescindible",
                "bullets": [
                    "Instagram Reels CPM sube 11 % interanual, impulsado por mejoras del ranker Llama-RT.",
                    "WhatsApp Business cierra 42 k nuevas cuentas pagadas en EMEA la última semana.",
                    "Capex trimestral acumulado 12,3 B (+34 % YoY) — mayor presión sobre FCF.",
                ],
            },
            {
                "titulo": "Agenda de hoy",
                "bullets": [
                    "09:30 · Comité de capital allocation (revisión pipeline AI infra).",
                    "11:00 · Llamada con analistas sell-side top-5.",
                    "15:00 · Reunión con regulador CMA (UK) — paquete DMA/DSA.",
                ],
            },
        ],
    },

    "plan-estrategico": {
        "titulo": "Seguimiento del plan estratégico",
        "subtitulo": "Objetivos 2024-2026 y avance por iniciativa",
        "vision": "ceo",
        "fuente": "Oracle EPM · Workday Adaptive Planning",
        "ultima": "Actualizado · 2026-11-06",
        "kpis": [
            _kpi("Iniciativas en objetivo", "17 de 24", "71 %", "pos"),
            _kpi("Iniciativas en riesgo", "5 de 24", None, "warn"),
            _kpi("Iniciativas fuera de plan", "2 de 24", None, "neg"),
            _kpi("OKR corporativo cumplido", "0,74", "+0,06 vs Q3", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Avance de iniciativas por pilar estratégico (%)",
            "categorias": ["AI Platform", "Reality Labs", "Family of Apps",
                           "Business Messaging", "Infra & Capex", "Regulación"],
            "serie": [82, 54, 91, 76, 68, 63],
        },
        "bloques": [
            {
                "titulo": "Alto riesgo",
                "bullets": [
                    "Llama 4 Enterprise · go-to-market retrasado 1 trimestre por disponibilidad GPU.",
                    "Reality Labs · reducción de pérdidas por debajo del objetivo FY (-18 % vs -25 %).",
                ],
            },
            {
                "titulo": "Progreso destacado",
                "bullets": [
                    "Monetización WhatsApp +41 % YoY (objetivo 2026 ya alcanzado).",
                    "Reels · share of time 32 % (+6 pts YoY).",
                ],
            },
        ],
    },

    "dossier-consejo": {
        "titulo": "Dossier para el Consejo",
        "subtitulo": "Preparación para la próxima sesión del Board",
        "vision": "ceo",
        "fuente": "Oracle EPM · DocuSign CLM · SharePoint",
        "ultima": "Próxima sesión · 2026-11-19",
        "kpis": [
            _kpi("Papeles preparados", "14 / 18", "78 %", "warn"),
            _kpi("Comentarios abiertos", "7", None, "warn"),
            _kpi("Decisiones pendientes", "3", None, "neg"),
            _kpi("Horas estimadas", "4 h 10", None),
        ],
        "grafico": {
            "tipo": "donut",
            "titulo": "Reparto del tiempo de sesión",
            "serie": [
                {"name": "Resultados Q3", "value": 60},
                {"name": "Plan 2027", "value": 55},
                {"name": "Decisiones M&A", "value": 40},
                {"name": "Riesgos y auditoría", "value": 35},
                {"name": "Gobierno", "value": 20},
                {"name": "Varios", "value": 40},
            ],
        },
        "bloques": [
            {
                "titulo": "Decisiones a elevar",
                "bullets": [
                    "Aprobación programa de recompra ampliado hasta USD 60 B.",
                    "Luz verde al CAPEX 2027 — rango USD 95-105 B.",
                    "Nombramiento Chair Comité Tecnología.",
                ],
            },
            {
                "titulo": "Lectura previa recomendada",
                "bullets": [
                    "Nota de riesgos regulatorios (DMA, DSA, SEC AI disclosure).",
                    "Memoria sostenibilidad — doble materialidad CSRD.",
                ],
            },
        ],
    },

    "preparacion-reuniones": {
        "titulo": "Preparación de reuniones",
        "subtitulo": "Dossier ejecutivo generado para cada cita de la agenda",
        "vision": "ceo",
        "fuente": "Google Calendar · Salesforce · LinkedIn Sales Navigator",
        "ultima": "Sincronizado · hace 12 min",
        "kpis": [
            _kpi("Reuniones próximas 7 días", "23"),
            _kpi("Con dossier listo", "19", "83 %", "pos"),
            _kpi("Pendientes de preparación", "4", None, "warn"),
            _kpi("Tiempo ahorrado estimado", "6 h 30"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Reuniones por tipo (próximas 2 semanas)",
            "categorias": ["Consejo", "Clientes top", "Inversores",
                           "Regulador", "Equipo interno", "Prensa"],
            "serie": [2, 7, 5, 3, 11, 2],
        },
        "bloques": [
            {
                "titulo": "Próxima reunión",
                "bullets": [
                    "15:00 · Satya Nadella (Microsoft) — follow-up Azure/Llama hosting.",
                    "Puntos clave: pricing GPU, SLAs, cláusulas de salida.",
                    "Antecedentes: 3 llamadas previas, último MoU 2025-09-14.",
                ],
            },
            {
                "titulo": "Material disponible",
                "bullets": [
                    "Briefing · 1 página",
                    "Dossier contraparte · 4 páginas",
                    "Últimos resultados y noticias · 2 páginas",
                ],
            },
        ],
    },

    "speechwriter": {
        "titulo": "Redactor de intervenciones",
        "subtitulo": "Borradores de discursos y mensajes clave",
        "vision": "ceo",
        "fuente": "Oracle EPM · DocuSign CLM · Grammarly Business",
        "ultima": "Último borrador · hace 1 h",
        "kpis": [
            _kpi("Borradores activos", "4"),
            _kpi("Mensajes clave aprobados", "11"),
            _kpi("Revisión Legal", "3 pendientes", None, "warn"),
            _kpi("Tono promedio", "Confiado", "+0,12", "pos"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Sentimiento audiencia (últimas 10 intervenciones)",
            "serie": [0.58, 0.61, 0.59, 0.65, 0.68, 0.71, 0.69, 0.74, 0.77, 0.79],
        },
        "bloques": [
            {
                "titulo": "En redacción",
                "bullets": [
                    "Keynote Connect 2026 · apertura (12 min).",
                    "Carta anual a accionistas FY2026.",
                    "Testimonio comisión del Senado (AI safety).",
                ],
            },
            {
                "titulo": "Mensajes clave corporativos",
                "bullets": [
                    "Reality Labs como inversión a 10 años.",
                    "Eficiencia operativa compatible con liderazgo en AI.",
                    "Confianza, seguridad y bienestar de los adolescentes.",
                ],
            },
        ],
    },

    "alertas-proactivas": {
        "titulo": "Alertas proactivas",
        "subtitulo": "Señales que requieren atención ejecutiva",
        "vision": "ceo",
        "fuente": "Snowflake · Datadog · Factiva · Oracle EPM",
        "ultima": "Actualizado · hace 3 min",
        "kpis": [
            _kpi("Alertas abiertas", "9"),
            _kpi("Severidad alta", "3", None, "neg"),
            _kpi("Severidad media", "4", None, "warn"),
            _kpi("Severidad baja", "2", None),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Alertas por origen (últimos 30 días)",
            "categorias": ["Finanzas", "Operaciones", "Regulación",
                           "Reputación", "Seguridad", "Talento"],
            "serie": [14, 9, 21, 7, 11, 5],
        },
        "bloques": [
            {
                "titulo": "Alertas críticas",
                "bullets": [
                    "Caída conversión Shop ads -8 % w/w — probable regresión del ranker.",
                    "Investigación formal CNIL · tratamiento de datos menores.",
                    "Churn de 3 ingenieros senior de AI Infra en 2 semanas.",
                ],
            },
        ],
    },

    "mapa-riesgos": {
        "titulo": "Mapa de riesgos corporativo",
        "subtitulo": "Matriz 5×5 de probabilidad × impacto",
        "vision": "ceo",
        "fuente": "ServiceNow GRC · Oracle EPM",
        "ultima": "Revisión mensual · 2026-11-03",
        "kpis": [
            _kpi("Riesgos registrados", "148"),
            _kpi("Zona roja (alto × alto)", "7", None, "neg"),
            _kpi("Zona ámbar", "34", None, "warn"),
            _kpi("Controles vigentes", "412"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Riesgos por categoría (ponderado por impacto)",
            "categorias": ["Regulatorio", "Ciber", "Operacional",
                           "Financiero", "Reputacional", "Estratégico"],
            "serie": [92, 78, 61, 44, 57, 69],
        },
        "bloques": [
            {
                "titulo": "Top 5 riesgos elevados al Consejo",
                "bullets": [
                    "Fragmentación regulatoria global de AI (UE, US, India).",
                    "Dependencia de un único proveedor GPU.",
                    "Riesgos de litigio class action en EEUU.",
                    "Modelos generativos y contenido infractor.",
                    "Ataque supply-chain sobre entorno MLOps.",
                ],
            },
        ],
    },

    "guidance-tracker": {
        "titulo": "Seguimiento de guidance al mercado",
        "subtitulo": "Comparación entre guidance, consenso y real",
        "vision": "ceo",
        "fuente": "Visible Alpha · Refinitiv · Oracle EPM",
        "ultima": "Último cierre · Q3 2026",
        "kpis": [
            _kpi("Guidance ingresos Q4", "USD 48-51 B"),
            _kpi("Consenso ingresos Q4", "USD 49,4 B", "+2,1 %", "pos"),
            _kpi("Guidance Capex FY", "USD 72-75 B"),
            _kpi("Consenso Capex FY", "USD 73,8 B", None),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Guidance vs real (ingresos trimestrales, USD B)",
            "serie": [28.6, 32.0, 32.2, 34.1, 36.5, 38.3, 40.1, 42.0, 44.8, 47.5],
        },
        "bloques": [
            {
                "titulo": "Lectura analistas",
                "bullets": [
                    "7 de 10 analistas top sitúan su estimación dentro del rango de guidance.",
                    "Riesgo al alza en ingresos — estacionalidad Q4 publicidad.",
                    "Riesgo a la baja en margen por intensificación capex.",
                ],
            },
        ],
    },

    "ma-radar": {
        "titulo": "Radar M&A",
        "subtitulo": "Oportunidades y señales de mercado",
        "vision": "ceo",
        "fuente": "PitchBook · CB Insights · Oracle EPM",
        "ultima": "Última ingesta · hoy 06:00",
        "kpis": [
            _kpi("Oportunidades activas", "27"),
            _kpi("En due diligence", "4", None, "pos"),
            _kpi("Tamaño pipeline (EV)", "USD 11,4 B"),
            _kpi("Deals cerrados YTD", "2"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Oportunidades por vertical",
            "categorias": ["AI Infra", "Gen AI apps", "Hardware XR",
                           "AdTech", "Payments", "Commerce"],
            "serie": [9, 6, 4, 3, 3, 2],
        },
        "bloques": [
            {
                "titulo": "Deals destacados",
                "bullets": [
                    "Startup europea de GPUs ópticos · EV 1,2 B · señal fuerte de ronda Series D.",
                    "Scale-up de personalización publicitaria · EV 0,4 B · interés de Google reportado.",
                    "Compañía israelí de perception XR · EV 0,8 B · fundadores ex-Meta.",
                ],
            },
        ],
    },

    "panel-personas": {
        "titulo": "Panel de personas",
        "subtitulo": "Salud organizativa, talento y cultura",
        "vision": "ceo",
        "fuente": "Workday · Culture Amp · Oracle EPM",
        "ultima": "Última medición · 2026-10-31",
        "kpis": [
            _kpi("Plantilla global", "74.213", "+2,1 % YTD", "pos"),
            _kpi("Rotación anualizada", "6,8 %", "-0,4 pts", "pos"),
            _kpi("eNPS", "34", "+3", "pos"),
            _kpi("Posiciones críticas abiertas", "128", None, "warn"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Plantilla y rotación (últimos 12 meses)",
            "serie": [72700, 72950, 73120, 73300, 73450, 73580, 73700, 73810,
                      73950, 74060, 74150, 74213],
        },
        "bloques": [
            {
                "titulo": "Alertas de talento",
                "bullets": [
                    "Rotación voluntaria en AI Research +3 pts vs media compañía.",
                    "DE&I · promoción femenina a nivel D+ 29 % (objetivo 32 %).",
                    "Mánager scores al alza en todas las regiones salvo APAC.",
                ],
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# CFO y directores financieros
# ---------------------------------------------------------------------------

_CFO = {
    "cierre-rapido": {
        "titulo": "Cuadro de cierre rápido",
        "subtitulo": "Posición de cierre estimada a D+2",
        "vision": "cfo",
        "fuente": "Oracle EPM Cloud · SAP S/4HANA",
        "ultima": "Pre-cierre octubre · D+2",
        "kpis": [
            _kpi("Ingresos MTD", "USD 13,9 B", "+5,1 % vs plan", "pos"),
            _kpi("EBIT MTD", "USD 5,7 B", "+2,3 %", "pos"),
            _kpi("Beneficio neto MTD", "USD 4,6 B", "+1,8 %", "pos"),
            _kpi("Diferencia vs plan", "+USD 118 M", None, "pos"),
        ],
        "grafico": {
            "tipo": "waterfall",
            "titulo": "De EBIT plan a EBIT estimado octubre (USD M)",
            "etiquetas": ["Plan", "Volumen", "Precio", "Mix",
                          "Opex", "FX", "Estimado"],
            "serie": [5580, 180, 95, -60, -75, 25, 5745],
        },
        "bloques": [
            {
                "titulo": "Puntos abiertos",
                "bullets": [
                    "Devengos marketing LatAm — pendiente conciliación de 42 OC.",
                    "Pérdida por obsolescencia hardware RL · 38 M en revisión.",
                ],
            },
        ],
    },

    "prevision-continua": {
        "titulo": "Previsión continua (rolling forecast)",
        "subtitulo": "Horizonte 18 meses rodante",
        "vision": "cfo",
        "fuente": "Workday Adaptive Planning · Oracle EPM",
        "ultima": "Último driver actualizado · hoy",
        "kpis": [
            _kpi("Ingresos FY26E", "USD 189 B", "+18 % YoY", "pos"),
            _kpi("EBIT FY26E", "USD 76 B", "+16 %", "pos"),
            _kpi("Capex FY26E", "USD 78 B", "+27 %", "warn"),
            _kpi("FCF FY26E", "USD 24 B", "-11 %", "neg"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Ingresos trimestrales rolling (USD B)",
            "serie": [34.1, 36.5, 38.3, 40.1, 42.0, 44.8, 47.5, 50.2,
                      52.1, 54.3, 56.8, 59.1],
        },
        "bloques": [
            {
                "titulo": "Drivers con mayor sensibilidad",
                "bullets": [
                    "CPM Reels (±5 % → ±USD 2,1 B ingresos anuales).",
                    "Coste GPU hora (±10 % → ±USD 1,6 B opex).",
                    "Headcount AI Infra (±500 FTE → ±USD 180 M opex).",
                ],
            },
        ],
    },

    "prevision-caja-13s": {
        "titulo": "Previsión de caja a 13 semanas",
        "subtitulo": "Cobros, pagos y liquidez neta semanal",
        "vision": "cfo",
        "fuente": "Kyriba · SAP TRM",
        "ultima": "Semana 45 · 2026-11-03",
        "kpis": [
            _kpi("Caja inicial", "USD 44,1 B"),
            _kpi("Caja final 13s", "USD 48,6 B", "+10 %", "pos"),
            _kpi("Cobros previstos", "USD 61 B"),
            _kpi("Pagos previstos", "USD 56,5 B"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Saldo de caja semanal (USD B)",
            "serie": [44.1, 43.2, 43.9, 44.8, 45.2, 44.9, 45.6, 46.1,
                      46.7, 47.0, 47.6, 48.1, 48.6],
        },
        "bloques": [
            {
                "titulo": "Semanas críticas",
                "bullets": [
                    "Semana 47 · pago impuestos federales USD 7,3 B.",
                    "Semana 49 · vencimiento bono senior USD 2,5 B.",
                    "Semana 51 · dividendo trimestral USD 1,3 B.",
                ],
            },
        ],
    },

    "covenants": {
        "titulo": "Seguimiento de covenants",
        "subtitulo": "Umbrales contractuales y holgura actual",
        "vision": "cfo",
        "fuente": "SAP TRM · DocuSign CLM",
        "ultima": "Pre-cierre octubre",
        "kpis": [
            _kpi("Net debt / EBITDA", "0,21x", "Covenant ≤ 2,0x", "pos"),
            _kpi("EBITDA / Intereses", "28,4x", "Covenant ≥ 4,0x", "pos"),
            _kpi("Covenants revisados", "12/12", None, "pos"),
            _kpi("Alertas abiertas", "0", None, "pos"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Evolución net debt / EBITDA (últimos 12 trimestres)",
            "serie": [0.11, 0.09, 0.14, 0.18, 0.22, 0.26, 0.29, 0.28,
                      0.25, 0.24, 0.22, 0.21],
        },
        "bloques": [
            {
                "titulo": "Próximos tests",
                "bullets": [
                    "RCF USD 10 B · test trimestral 31-dic-2026.",
                    "Programa EMTN · test semestral 30-jun-2027.",
                ],
            },
        ],
    },

    "asignacion-capital": {
        "titulo": "Asignación de capital",
        "subtitulo": "Despliegue de capital YTD vs plan",
        "vision": "cfo",
        "fuente": "Oracle EPM · SAP TRM",
        "ultima": "YTD octubre 2026",
        "kpis": [
            _kpi("Capex YTD", "USD 61 B", "77 % plan FY", "pos"),
            _kpi("Recompras YTD", "USD 29 B", "81 % plan FY", "pos"),
            _kpi("Dividendos YTD", "USD 5,2 B", "80 % plan FY", "pos"),
            _kpi("M&A YTD", "USD 1,8 B", "45 % plan FY", "warn"),
        ],
        "grafico": {
            "tipo": "donut",
            "titulo": "Reparto del capital YTD (USD B)",
            "serie": [
                {"name": "Capex", "value": 61.0},
                {"name": "Recompras", "value": 29.0},
                {"name": "Dividendos", "value": 5.2},
                {"name": "M&A", "value": 1.8},
                {"name": "Amortización deuda", "value": 3.5},
            ],
        },
        "bloques": [
            {
                "titulo": "Retornos esperados por bucket",
                "bullets": [
                    "Capex AI infra · IRR objetivo 18-22 % a 7 años.",
                    "Capex RL · IRR objetivo 10-14 % a 10 años.",
                    "Recompras · ROE efectivo ~26 %.",
                ],
            },
        ],
    },

    "flujo-cierre": {
        "titulo": "Flujo de cierre consolidado",
        "subtitulo": "Estado del cierre mensual del grupo",
        "vision": "cfo",
        "fuente": "SAP Group Reporting",
        "ultima": "Cierre octubre · día 4 de 8",
        "kpis": [
            _kpi("Entidades reportando", "47/49", "96 %", "warn"),
            _kpi("Journal entries revisadas", "12.418", "+6 % YoY", "pos"),
            _kpi("Ajustes top-side", "32", None),
            _kpi("Horas medias cierre", "68 h", "-8 h vs 2025", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Días de cierre por entidad (top 10 lentas)",
            "categorias": ["Meta Brasil", "Meta Japón", "Meta Alemania",
                           "Meta India", "Meta MX", "Oculus HW",
                           "Meta FR", "Meta UK", "Meta IE", "Meta AU"],
            "serie": [7, 7, 6, 6, 5, 5, 5, 4, 4, 4],
        },
        "bloques": [
            {
                "titulo": "Entidades en retraso",
                "bullets": [
                    "Meta Brasil · dependencia de ERP legacy Omega.",
                    "Oculus Hardware · conciliación inventario FGP pendiente.",
                ],
            },
        ],
    },

    "conciliacion-ic": {
        "titulo": "Conciliación intercompany",
        "subtitulo": "Diferencias abiertas entre entidades del grupo",
        "vision": "cfo",
        "fuente": "SAP Group Reporting · BlackLine",
        "ultima": "Hoy 08:12",
        "kpis": [
            _kpi("Pares conciliados", "412 / 420", "98 %", "pos"),
            _kpi("Diferencias > 100 k", "8", None, "warn"),
            _kpi("Importe en disputa", "USD 11,4 M"),
            _kpi("Edad media pendientes", "7 días"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Diferencias por entidad origen (USD M)",
            "categorias": ["Meta Ireland", "Meta Platforms Inc.",
                           "Meta Singapore", "Meta Brasil", "Meta UK"],
            "serie": [4.1, 2.8, 1.9, 1.5, 1.1],
        },
        "bloques": [
            {
                "titulo": "Casos prioritarios",
                "bullets": [
                    "Royalties Meta Ireland ↔ Meta Platforms Inc. · USD 3,2 M.",
                    "Servicios compartidos Meta Singapore ↔ APAC · USD 1,1 M.",
                ],
            },
        ],
    },

    "eliminaciones": {
        "titulo": "Eliminaciones de consolidación",
        "subtitulo": "Automatización vs ajuste manual",
        "vision": "cfo",
        "fuente": "SAP Group Reporting",
        "ultima": "Pre-cierre octubre",
        "kpis": [
            _kpi("Eliminaciones automáticas", "USD 22,4 B", "94 %", "pos"),
            _kpi("Eliminaciones manuales", "USD 1,4 B", "6 %", "warn"),
            _kpi("Reglas activas", "84"),
            _kpi("Horas de ajuste", "22 h", "-9 h vs 2025", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Tipos de eliminación (USD B)",
            "categorias": ["Ventas IC", "Royalties IC", "Dividendos IC",
                           "Préstamos IC", "Servicios IC"],
            "serie": [11.2, 6.4, 3.1, 1.3, 1.8],
        },
        "bloques": [
            {
                "titulo": "Mejoras recientes",
                "bullets": [
                    "Automatización reglas royalties → -340 h/cierre.",
                    "Nueva regla de capital IC → reducción de ajustes top-side.",
                ],
            },
        ],
    },

    "estatutario-vs-gestion": {
        "titulo": "Estatutario vs gestión",
        "subtitulo": "Reconciliación de perímetro y métricas",
        "vision": "cfo",
        "fuente": "SAP Group Reporting · Oracle EPM",
        "ultima": "Cierre Q3 2026",
        "kpis": [
            _kpi("Ingresos estatutarios", "USD 149 B"),
            _kpi("Ingresos gestión", "USD 151,3 B"),
            _kpi("Diferencia", "USD +2,3 B", "+1,5 %"),
            _kpi("Partidas conciliadas", "127 / 128", "99 %", "pos"),
        ],
        "grafico": {
            "tipo": "waterfall",
            "titulo": "De ingresos estatutarios a ingresos de gestión (USD B)",
            "etiquetas": ["Estatutario", "Royalties IC",
                          "Ajuste moneda funcional", "Reclasificaciones",
                          "Gestión"],
            "serie": [149.0, 1.1, 0.7, 0.5, 151.3],
        },
        "bloques": [
            {
                "titulo": "Diferencias recurrentes",
                "bullets": [
                    "Royalties IC reconocidos como ingreso en gestión.",
                    "Capitalización de costes de desarrollo (estatutario vs gestión).",
                ],
            },
        ],
    },

    "impacto-fx": {
        "titulo": "Impacto FX",
        "subtitulo": "Efecto tipo de cambio sobre resultados",
        "vision": "cfo",
        "fuente": "Kyriba · SAP TRM",
        "ultima": "Cierre octubre",
        "kpis": [
            _kpi("Impacto FX en ingresos", "USD -0,9 B", "-0,5 %", "neg"),
            _kpi("Impacto FX en EBIT", "USD -0,4 B", "-0,6 %", "neg"),
            _kpi("Translation exposure", "USD 18,2 B"),
            _kpi("Hedge ratio", "68 %", "+6 pts YoY", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Impacto FX por divisa en ingresos (USD M, YTD)",
            "categorias": ["EUR", "JPY", "BRL", "INR", "GBP", "KRW"],
            "serie": [-320, -210, -175, -98, 60, -50],
        },
        "bloques": [
            {
                "titulo": "Sensibilidad",
                "bullets": [
                    "EUR/USD ±5 % → ±USD 0,6 B ingresos anuales.",
                    "JPY/USD ±5 % → ±USD 0,3 B ingresos anuales.",
                ],
            },
        ],
    },

    "rentabilidad-dimension": {
        "titulo": "Rentabilidad por dimensión",
        "subtitulo": "Margen por negocio, canal, segmento y tipología de cliente",
        "vision": "cfo",
        "fuente": "Snowflake · Oracle EPM",
        "ultima": "YTD octubre",
        "kpis": [
            _kpi("Margen operativo FoA", "48 %", "+2 pts YoY", "pos"),
            _kpi("Margen operativo RL", "-74 %", "+4 pts YoY", "warn"),
            _kpi("Margen top 100 anunciantes", "61 %"),
            _kpi("Margen SMB", "42 %"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Margen operativo por canal (%)",
            "categorias": ["Instagram Reels", "Instagram Feed", "Facebook Feed",
                           "WhatsApp Business", "Messenger", "Audience Network"],
            "serie": [55, 52, 50, 38, 44, 29],
        },
        "bloques": [
            {
                "titulo": "Reparto y análisis de costes por negocio",
                "bullets": [
                    "ABC activity-based costing desplegado en 92 % de centros de coste.",
                    "Drivers: horas GPU, impresiones servidas, tickets soporte.",
                    "Modelo reconstruible por canal, segmento y tipología de cliente.",
                ],
            },
        ],
    },

    "presupuesto-vs-real": {
        "titulo": "Presupuesto vs real",
        "subtitulo": "Variaciones y explicación por responsable",
        "vision": "cfo",
        "fuente": "Workday Adaptive · Oracle EPM",
        "ultima": "YTD octubre",
        "kpis": [
            _kpi("Ingresos vs plan", "+4,2 %", None, "pos"),
            _kpi("Opex vs plan", "+1,8 %", None, "warn"),
            _kpi("Capex vs plan", "+6,7 %", None, "warn"),
            _kpi("EBIT vs plan", "+5,9 %", None, "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Variación YTD por línea (USD B)",
            "categorias": ["Ingresos", "Coste ventas", "I+D",
                           "Marketing", "G&A", "Capex"],
            "serie": [6.2, 0.9, 1.4, 0.6, 0.2, 4.1],
        },
        "bloques": [
            {
                "titulo": "Top explicadores",
                "bullets": [
                    "CPM Reels por encima de plan → +USD 2,8 B ingresos.",
                    "GPU superior a plan por aceleración de clusters → +USD 1,1 B capex.",
                    "Headcount AI Infra +12 % vs plan → +USD 0,5 B opex.",
                ],
            },
        ],
    },

    "prevision-drivers": {
        "titulo": "Previsión por drivers",
        "subtitulo": "Modelo driver-based: volumen × precio × mix",
        "vision": "cfo",
        "fuente": "Oracle EPM · Snowflake",
        "ultima": "Último recálculo · hoy",
        "kpis": [
            _kpi("DAU FoA", "3,47 B", "+5,2 % YoY", "pos"),
            _kpi("Impresiones", "+22 % YoY", None, "pos"),
            _kpi("Precio por anuncio", "+7 % YoY", None, "pos"),
            _kpi("Mix Reels", "32 %", "+6 pts", "pos"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Proyección de ingresos por descomposición de drivers (USD B)",
            "serie": [140, 145, 151, 156, 162, 168, 174, 180, 186, 192, 198, 204],
        },
        "bloques": [
            {
                "titulo": "Elasticidades modeladas",
                "bullets": [
                    "Elasticidad precio · -0,4 (impresiones ante subida CPM).",
                    "Elasticidad tiempo · +0,25 (ingresos ante tiempo en Reels).",
                    "Elasticidad mix · +0,18 (margen ante subida share Reels).",
                ],
            },
        ],
    },

    "cascada-margen": {
        "titulo": "Cascada de margen de contribución",
        "subtitulo": "De ingresos a margen de contribución por producto",
        "vision": "cfo",
        "fuente": "Oracle EPM · Snowflake",
        "ultima": "YTD octubre",
        "kpis": [
            _kpi("Ingresos FoA", "USD 143 B"),
            _kpi("Coste variable", "USD 27 B", "19 % ingresos"),
            _kpi("Costes directos fijos", "USD 32 B", "22 %"),
            _kpi("Margen contribución", "USD 84 B", "59 %"),
        ],
        "grafico": {
            "tipo": "waterfall",
            "titulo": "Cascada margen FoA (USD B)",
            "etiquetas": ["Ingresos", "Coste variable",
                          "Costes directos fijos", "Opex atribuible",
                          "Margen contribución"],
            "serie": [143, -27, -32, -8, 76],
        },
        "bloques": [
            {
                "titulo": "Lectura clave",
                "bullets": [
                    "Instagram Reels pasa a ser el canal con mayor margen de contribución absoluto.",
                    "WhatsApp Business sigue en fase de inversión — margen de contribución 24 %.",
                ],
            },
        ],
    },

    "economia-unitaria": {
        "titulo": "Economía unitaria",
        "subtitulo": "ARPU, CAC, LTV, pay-back",
        "vision": "cfo",
        "fuente": "Oracle EPM · Snowflake",
        "ultima": "Último recálculo · hoy",
        "kpis": [
            _kpi("ARPU global", "USD 42,1", "+6,8 % YoY", "pos"),
            _kpi("ARPU EEUU/Canadá", "USD 72,4"),
            _kpi("CAC publicitario (USD)", "USD 1,42"),
            _kpi("LTV/CAC", "18x"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "ARPU por región (USD)",
            "categorias": ["US/CA", "Europa", "Asia-Pacífico",
                           "Resto del mundo"],
            "serie": [72.4, 25.8, 7.9, 4.4],
        },
        "bloques": [
            {
                "titulo": "Lectura",
                "bullets": [
                    "La diferencia US/CA vs RoW sigue siendo el principal gap de monetización.",
                    "Modelo WhatsApp Business paga CAC en 7 meses (vs 11 FY2025).",
                ],
            },
        ],
    },

    "analitica-adhoc": {
        "titulo": "Analítica ad-hoc sobre el DWH",
        "subtitulo": "Consulta libre sobre Snowflake y catálogo",
        "vision": "cfo",
        "fuente": "Snowflake · dbt · Alation",
        "ultima": "Última consulta · hace 2 min",
        "kpis": [
            _kpi("Datasets certificados", "648"),
            _kpi("Consultas / día (dpto Finanzas)", "1.420"),
            _kpi("Tiempo medio respuesta", "3,4 s"),
            _kpi("% consultas con glosario", "87 %", "+9 pts", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Consultas por tipología (últimos 30 días)",
            "categorias": ["Ingresos", "Costes", "Capex", "Tesorería",
                           "Impuestos", "Personas"],
            "serie": [2140, 1680, 940, 820, 410, 320],
        },
        "bloques": [
            {
                "titulo": "Casos de uso frecuentes",
                "bullets": [
                    "Análisis cohortes publicitarias por geografía.",
                    "Simulación de impacto de cambios de pricing.",
                    "Auditoría de márgenes por partner publicitario.",
                ],
            },
        ],
    },

    "reparto-costes-abc": {
        "titulo": "Reparto de costes ABC",
        "subtitulo": "Activity-based costing por actividad y producto",
        "vision": "cfo",
        "fuente": "Oracle EPM Cost Management",
        "ultima": "Último recálculo · 2026-11-01",
        "kpis": [
            _kpi("Actividades modelizadas", "214"),
            _kpi("Drivers activos", "88"),
            _kpi("Costes asignados", "USD 46 B", "100 %", "pos"),
            _kpi("Sin asignar", "USD 0", None, "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Reparto por tipo de actividad (USD B)",
            "categorias": ["Infra computing", "Content moderation",
                           "Sales & partner", "Producto & diseño",
                           "Soporte anunciante", "Legal & compliance"],
            "serie": [18.4, 7.1, 6.3, 7.8, 3.6, 2.8],
        },
        "bloques": [
            {
                "titulo": "Consumo por producto",
                "bullets": [
                    "Reels concentra el 38 % de infra computing — tendencia al alza.",
                    "WhatsApp aporta 14 % del coste content moderation y crece deprisa.",
                ],
            },
        ],
    },

    "posicion-tesoreria": {
        "titulo": "Posición de tesorería",
        "subtitulo": "Saldos, cuentas y disponibilidad por banco",
        "vision": "cfo",
        "fuente": "Kyriba · SAP TRM",
        "ultima": "Hoy 08:00",
        "kpis": [
            _kpi("Caja total", "USD 48,2 B"),
            _kpi("Inversiones corto plazo", "USD 24,1 B"),
            _kpi("Disponibilidad RCF", "USD 10 B"),
            _kpi("Rentabilidad media caja", "4,8 %"),
        ],
        "grafico": {
            "tipo": "donut",
            "titulo": "Caja por bloque bancario (USD B)",
            "serie": [
                {"name": "JP Morgan", "value": 18.1},
                {"name": "Bank of America", "value": 9.4},
                {"name": "Citi", "value": 7.3},
                {"name": "HSBC", "value": 4.8},
                {"name": "MUFG", "value": 3.6},
                {"name": "Otros", "value": 5.0},
            ],
        },
        "bloques": [
            {
                "titulo": "Política",
                "bullets": [
                    "Exposición máxima por banco: 40 % del total.",
                    "Rating mínimo contraparte: A- S&P / A3 Moody's.",
                ],
            },
        ],
    },

    "exposicion-divisa": {
        "titulo": "Exposición en divisa",
        "subtitulo": "Posición neta y cobertura",
        "vision": "cfo",
        "fuente": "Kyriba · SAP TRM",
        "ultima": "Hoy 07:30",
        "kpis": [
            _kpi("Exposición total neta", "USD 18,2 B"),
            _kpi("Cobertura vigente", "USD 12,4 B", "68 %", "pos"),
            _kpi("VaR 1D (95 %)", "USD 42 M"),
            _kpi("Beneficio/pérdida FX YTD", "USD -340 M", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Posición neta por divisa (USD B, negativo = ventas futuras)",
            "categorias": ["EUR", "GBP", "JPY", "BRL", "INR", "KRW"],
            "serie": [-4.8, -2.1, -3.5, -1.2, -0.9, -0.7],
        },
        "bloques": [
            {
                "titulo": "Decisiones recientes",
                "bullets": [
                    "Aumento del ratio de cobertura EUR hasta 80 %.",
                    "Apertura forwards JPY 6M por 2 B.",
                ],
            },
        ],
    },

    "aprobacion-pagos": {
        "titulo": "Aprobación de pagos",
        "subtitulo": "Workflow y SLA",
        "vision": "cfo",
        "fuente": "SAP S/4HANA · Kyriba",
        "ultima": "Hoy 08:12",
        "kpis": [
            _kpi("Pagos del día", "4.218"),
            _kpi("Importe del día", "USD 1,74 B"),
            _kpi("Pendientes CFO", "9", None, "warn"),
            _kpi("SLA aprobación", "99,2 %", "+0,3 pts", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Pagos por tipología (USD M, YTD)",
            "categorias": ["Infra & GPU", "Content partners",
                           "Nómina", "Impuestos", "Marketing",
                           "Legal & professional"],
            "serie": [41800, 9200, 22800, 11400, 6800, 3100],
        },
        "bloques": [
            {
                "titulo": "Reglas activas",
                "bullets": [
                    "Pagos > USD 100 M requieren aprobación CFO + Tesorero.",
                    "Pagos a terceros no listados requieren KYC renovado.",
                ],
            },
        ],
    },

    "deuda": {
        "titulo": "Instrumentos de deuda",
        "subtitulo": "Perfil y vencimientos",
        "vision": "cfo",
        "fuente": "Bloomberg DMS · SAP TRM",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Deuda bruta", "USD 42,6 B"),
            _kpi("Vida media", "6,4 años"),
            _kpi("Coste medio", "4,7 %"),
            _kpi("Rating actual", "A1 / A+"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Vencimientos por año (USD B)",
            "categorias": ["2027", "2028", "2029", "2030", "2031",
                           "2032", "2033+"],
            "serie": [3.0, 5.5, 4.2, 6.8, 5.1, 7.4, 10.6],
        },
        "bloques": [
            {
                "titulo": "Emisiones recientes",
                "bullets": [
                    "Emisión senior USD 5 B · 10y · cupón 4,55 %.",
                    "Programa EMTN · tramo EUR 1,5 B · 7y · cupón 3,65 %.",
                ],
            },
        ],
    },

    "borrador-nota": {
        "titulo": "Borrador de nota de resultados",
        "subtitulo": "Q3 2026 · pre-publicación",
        "vision": "cfo",
        "fuente": "Oracle EPM · Workiva",
        "ultima": "Último borrador · hoy",
        "kpis": [
            _kpi("Páginas revisadas", "28 / 36"),
            _kpi("Comentarios Legal", "14", "6 abiertos", "warn"),
            _kpi("Comentarios Auditor", "8", "2 abiertos", "warn"),
            _kpi("Fecha publicación", "2026-11-19"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Sentimiento media sobre borrador (0-1)",
            "serie": [0.58, 0.62, 0.65, 0.66, 0.68, 0.71, 0.73, 0.75],
        },
        "bloques": [
            {
                "titulo": "Secciones críticas",
                "bullets": [
                    "Discusión capex y márgenes FY25 vs FY26E.",
                    "Riesgos regulatorios AI y menores.",
                    "Nota de recompras y política dividendos.",
                ],
            },
        ],
    },

    "qa-analistas": {
        "titulo": "Q&A de analistas",
        "subtitulo": "Preguntas previsibles y respuestas tipo",
        "vision": "cfo",
        "fuente": "Oracle EPM · Visible Alpha",
        "ultima": "Última actualización · hoy",
        "kpis": [
            _kpi("Preguntas modeladas", "182"),
            _kpi("Respuestas aprobadas", "148", "81 %", "pos"),
            _kpi("Respuestas en revisión", "22", None, "warn"),
            _kpi("Sin respuesta", "12", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Preguntas por bloque",
            "categorias": ["Capex AI", "Monetización WhatsApp",
                           "Reality Labs", "Regulación", "Recompras",
                           "Headcount"],
            "serie": [48, 32, 27, 24, 21, 18],
        },
        "bloques": [
            {
                "titulo": "Preguntas top esperadas",
                "bullets": [
                    "¿Cómo justificáis la aceleración del capex frente al FCF a 2 años?",
                    "¿Momento en que Reality Labs reduce pérdidas de forma material?",
                    "¿Pricing de WhatsApp Business en los próximos 12 meses?",
                ],
            },
        ],
    },

    "registro-accionistas": {
        "titulo": "Registro de accionistas",
        "subtitulo": "Composición accionarial y movimientos",
        "vision": "cfo",
        "fuente": "Broadridge · Nasdaq IR Insight",
        "ultima": "Actualizado · ayer",
        "kpis": [
            _kpi("Institucional", "62 %"),
            _kpi("Insiders", "13 %"),
            _kpi("Retail", "20 %"),
            _kpi("Índices", "5 %"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Top 10 inversores institucionales (% capital)",
            "categorias": ["Vanguard", "BlackRock", "State Street",
                           "Fidelity", "T. Rowe Price", "Capital Research",
                           "Geode", "Morgan Stanley AM", "Invesco", "BNY"],
            "serie": [8.4, 7.1, 4.6, 3.8, 2.9, 2.4, 2.1, 1.7, 1.4, 1.1],
        },
        "bloques": [
            {
                "titulo": "Movimientos recientes",
                "bullets": [
                    "Entrada nueva por un fondo soberano de Oriente Medio · 0,8 %.",
                    "Salida parcial de hedge fund activista top-50.",
                ],
            },
        ],
    },

    "calendario-regulatorio": {
        "titulo": "Calendario regulatorio",
        "subtitulo": "Hitos SEC, UE, estados y mercados",
        "vision": "cfo",
        "fuente": "ServiceNow GRC · Oracle EPM",
        "ultima": "Actualizado · hoy",
        "kpis": [
            _kpi("Hitos próximos 30 días", "12"),
            _kpi("Hitos obligatorios", "5", None, "warn"),
            _kpi("Hitos pendientes de revisión", "3", None, "neg"),
            _kpi("Hitos a tiempo", "92 %", "+3 pts", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Hitos por regulador (próximos 12 meses)",
            "categorias": ["SEC", "Comisión Europea", "CNIL", "ICO",
                           "Ofcom", "Autoridad India TRAI"],
            "serie": [28, 24, 11, 9, 7, 5],
        },
        "bloques": [
            {
                "titulo": "Próximos hitos clave",
                "bullets": [
                    "10-Q · 7 noviembre 2026.",
                    "Reporte CSRD doble materialidad · 15 marzo 2027.",
                    "Audiencia CNIL · 18 enero 2027.",
                ],
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Equipo operativo (miembros de equipo)
# ---------------------------------------------------------------------------

_EQUIPO = {
    "tareas-cierre": {
        "titulo": "Mi lista de tareas de cierre",
        "subtitulo": "Checklist operativa del cierre contable",
        "vision": "equipo",
        "fuente": "BlackLine · ServiceNow",
        "ultima": "Hoy 08:12",
        "kpis": [
            _kpi("Tareas totales", "48"),
            _kpi("Completadas", "33", "69 %", "pos"),
            _kpi("En curso", "9"),
            _kpi("Vencidas", "2", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Tareas por área funcional",
            "categorias": ["Devengos", "Conciliaciones", "Ajustes IC",
                           "Impuestos", "Tesorería", "Revisión"],
            "serie": [12, 10, 9, 7, 5, 5],
        },
        "bloques": [
            {
                "titulo": "Próximas",
                "bullets": [
                    "Cargar devengos marketing LatAm · hoy 17:00.",
                    "Conciliación Meta Brasil ↔ Meta Platforms Inc. · mañana 10:00.",
                    "Revisión final cuentas 51x · mañana 15:00.",
                ],
            },
        ],
    },

    "conciliacion-inteligente": {
        "titulo": "Conciliación inteligente",
        "subtitulo": "Matching asistido por el motor de conciliación",
        "vision": "equipo",
        "fuente": "BlackLine · SAP S/4HANA",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Items analizados", "128.420"),
            _kpi("Matcheo automático", "96 %", "+2 pts", "pos"),
            _kpi("Match sugerido", "3 %"),
            _kpi("Items en cola", "412", None, "warn"),
        ],
        "grafico": {
            "tipo": "line",
            "titulo": "Tasa de match automático (últimos 12 meses)",
            "serie": [0.88, 0.89, 0.90, 0.91, 0.92, 0.93,
                      0.94, 0.94, 0.95, 0.95, 0.96, 0.96],
        },
        "bloques": [
            {
                "titulo": "Patrones aprendidos recientemente",
                "bullets": [
                    "Reconocimiento de royalties IC con lag de 2 días.",
                    "Pagos a partners publicitarios con referencias truncadas.",
                ],
            },
        ],
    },

    "extraccion-documentos": {
        "titulo": "Extracción de documentos",
        "subtitulo": "Facturas, contratos y soportes digitalizados",
        "vision": "equipo",
        "fuente": "SAP Document Information Extraction",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Documentos procesados hoy", "1.842"),
            _kpi("Precisión campos clave", "98,4 %", "+0,6 pts", "pos"),
            _kpi("Tiempo medio", "11 s"),
            _kpi("En cola de revisión", "27", None, "warn"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Documentos por tipo (últimos 30 días)",
            "categorias": ["Facturas", "Albaranes", "Contratos",
                           "Resoluciones fiscales", "Certificados",
                           "Otros"],
            "serie": [34200, 18400, 4800, 2100, 1300, 2600],
        },
        "bloques": [
            {
                "titulo": "Reglas de extracción",
                "bullets": [
                    "Facturas en PDF escaneado · OCR Tesseract 5 + revisión.",
                    "Contratos marco · extracción de cláusulas clave.",
                    "Validación cruzada contra maestro proveedores.",
                ],
            },
        ],
    },

    "asientos-contables": {
        "titulo": "Asientos contables",
        "subtitulo": "Propuestas de asiento sugeridas",
        "vision": "equipo",
        "fuente": "SAP S/4HANA · Oracle EPM",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Asientos propuestos", "214"),
            _kpi("Aceptados sin cambio", "192", "90 %", "pos"),
            _kpi("Corregidos por usuario", "18"),
            _kpi("Rechazados", "4", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Asientos por naturaleza",
            "categorias": ["Devengos", "Reclasif.", "Ajustes IC",
                           "Provisiones", "Amortizaciones",
                           "Otros"],
            "serie": [62, 48, 36, 28, 22, 18],
        },
        "bloques": [
            {
                "titulo": "Reglas de autocompletado",
                "bullets": [
                    "Cuenta contable por patrón de descripción.",
                    "Centro de coste por entidad origen.",
                    "Elemento de IVA por tipología de proveedor.",
                ],
            },
        ],
    },

    "conciliacion-cuentas": {
        "titulo": "Conciliación de cuentas",
        "subtitulo": "Estado del cierre cuenta a cuenta",
        "vision": "equipo",
        "fuente": "BlackLine",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Cuentas a conciliar", "612"),
            _kpi("Conciliadas", "548", "90 %", "pos"),
            _kpi("Con incidencia", "37", None, "warn"),
            _kpi("Sin empezar", "27", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Conciliaciones por propietario",
            "categorias": ["Equipo A", "Equipo B", "Equipo C",
                           "Equipo D", "Equipo E"],
            "serie": [112, 128, 134, 116, 122],
        },
        "bloques": [
            {
                "titulo": "Cuentas de mayor exposición",
                "bullets": [
                    "Cuenta 5100 · deuda a corto plazo.",
                    "Cuenta 4700 · HP acreedora IVA.",
                    "Cuenta 4100 · acreedores comerciales terceros.",
                ],
            },
        ],
    },

    "consulta-normativa": {
        "titulo": "Consulta normativa",
        "subtitulo": "RAG sobre normativa contable y fiscal",
        "vision": "equipo",
        "fuente": "Base documental interna · IFRS Foundation · SEC",
        "ultima": "Última consulta · hace 2 min",
        "kpis": [
            _kpi("Consultas / día", "248"),
            _kpi("Acierto top-1", "84 %", "+4 pts", "pos"),
            _kpi("Documentos indexados", "11.420"),
            _kpi("Marcos cubiertos", "IFRS · US GAAP · PGC"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Consultas por tipo de norma",
            "categorias": ["Ingresos (IFRS 15)", "Arrendamientos (IFRS 16)",
                           "Instrumentos (IFRS 9)", "Impuestos (IAS 12)",
                           "Deterioro (IAS 36)", "Consolidación (IFRS 10)"],
            "serie": [820, 520, 690, 410, 340, 290],
        },
        "bloques": [
            {
                "titulo": "Ejemplo de respuesta",
                "bullets": [
                    "«Según IFRS 15 §31, el ingreso se reconoce cuando se satisface la obligación...»",
                    "Se cita siempre párrafo, enlace al documento original y versión vigente.",
                ],
            },
        ],
    },

    "base-documental": {
        "titulo": "Base documental",
        "subtitulo": "Catálogo unificado y buscable",
        "vision": "equipo",
        "fuente": "SharePoint · Alation · Confluence",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Documentos", "42.108"),
            _kpi("Políticas vigentes", "286"),
            _kpi("Manuales de proceso", "412"),
            _kpi("Vencidos", "18", None, "warn"),
        ],
        "grafico": {
            "tipo": "donut",
            "titulo": "Documentos por categoría",
            "serie": [
                {"name": "Políticas", "value": 286},
                {"name": "Manuales", "value": 412},
                {"name": "Plantillas", "value": 820},
                {"name": "Notas técnicas", "value": 1340},
                {"name": "Legal & regulatorio", "value": 2050},
                {"name": "Otros", "value": 37200},
            ],
        },
        "bloques": [
            {
                "titulo": "Más consultados",
                "bullets": [
                    "Política de pagos a terceros · 128 vistas / semana.",
                    "Manual cierre mensual · 96 vistas / semana.",
                    "Plantilla reporting a inversores · 72 vistas / semana.",
                ],
            },
        ],
    },

    "report-builder": {
        "titulo": "Report builder",
        "subtitulo": "Montaje de informes recurrentes",
        "vision": "equipo",
        "fuente": "Workiva · Oracle EPM",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Plantillas activas", "48"),
            _kpi("Informes publicados YTD", "612"),
            _kpi("Tiempo medio montaje", "22 min"),
            _kpi("Reutilización bloques", "74 %", "+6 pts", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Informes por destinatario",
            "categorias": ["Dir. financiera", "Consejo", "Reguladores",
                           "Operaciones", "Comercial", "Externo"],
            "serie": [142, 72, 56, 128, 112, 102],
        },
        "bloques": [
            {
                "titulo": "Novedades",
                "bullets": [
                    "Plantilla «Informe de margen por canal» certificada.",
                    "Bloques reutilizables de narrativa por región.",
                ],
            },
        ],
    },

    "controles-calidad": {
        "titulo": "Controles de calidad",
        "subtitulo": "Chequeos automáticos antes de cerrar",
        "vision": "equipo",
        "fuente": "Oracle EPM · BlackLine",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Controles ejecutados hoy", "1.420"),
            _kpi("OK", "1.392", "98 %", "pos"),
            _kpi("Advertencia", "22", None, "warn"),
            _kpi("Error bloqueante", "6", None, "neg"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Controles por naturaleza",
            "categorias": ["Integridad", "Variación", "Conciliación",
                           "Autorización", "Documentación",
                           "Reporting"],
            "serie": [420, 340, 280, 160, 130, 90],
        },
        "bloques": [
            {
                "titulo": "Reglas activas",
                "bullets": [
                    "Variación > 10 % mes a mes → alerta.",
                    "Cuenta IC sin conciliar → bloqueo del cierre.",
                    "Cuenta de reserva con movimiento → revisión obligatoria.",
                ],
            },
        ],
    },

    "formacion-epm": {
        "titulo": "Formación EPM",
        "subtitulo": "Cómo trabajar con las aplicaciones EPM conectadas",
        "vision": "equipo",
        "fuente": "Base documental interna · RAG manuales Oracle / OneStream / SAP",
        "ultima": "Hoy",
        "kpis": [
            _kpi("Cursos disponibles", "28"),
            _kpi("Manuales indexados", "182"),
            _kpi("Consultas / día", "420"),
            _kpi("Horas de formación YTD", "6.820"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Formación por herramienta",
            "categorias": ["Oracle EPM", "OneStream",
                           "SAP Group Reporting", "SAP S/4HANA",
                           "Workday Adaptive", "Kyriba"],
            "serie": [142, 96, 78, 110, 88, 46],
        },
        "bloques": [
            {
                "titulo": "Casos resueltos esta semana",
                "bullets": [
                    "Cómo cargar un formulario FCCS con intercompañía.",
                    "Cómo publicar un cube en OneStream con escenarios.",
                    "Cómo personalizar una plantilla de reporting en Oracle Narrative Reporting.",
                ],
            },
        ],
    },
}


MOCK_MODULOS = {}
MOCK_MODULOS.update(_CEO)
MOCK_MODULOS.update(_CFO)
MOCK_MODULOS.update(_EQUIPO)


# Orden canónico para el sidebar.
MOCK_NAV = {
    "ceo": [
        ("briefing-diario",      "Briefing diario"),
        ("plan-estrategico",     "Plan estratégico"),
        ("dossier-consejo",      "Dossier Consejo"),
        ("preparacion-reuniones","Preparación reuniones"),
        ("speechwriter",         "Speechwriter"),
        ("alertas-proactivas",   "Alertas proactivas"),
        ("mapa-riesgos",         "Mapa de riesgos"),
        ("guidance-tracker",     "Guidance tracker"),
        ("ma-radar",             "Radar M&A"),
        ("panel-personas",       "Panel de personas"),
    ],
    "cfo": [
        ("cierre-rapido",          "Cuadro cierre rápido"),
        ("prevision-continua",     "Previsión continua"),
        ("prevision-caja-13s",     "Previsión caja 13s"),
        ("covenants",              "Covenants"),
        ("asignacion-capital",     "Asignación capital"),
        ("flujo-cierre",           "Flujo cierre consolidado"),
        ("conciliacion-ic",        "Conciliación IC"),
        ("eliminaciones",          "Eliminaciones"),
        ("estatutario-vs-gestion", "Estatutario vs gestión"),
        ("impacto-fx",             "Impacto FX"),
        ("rentabilidad-dimension", "Rentabilidad por dimensión"),
        ("presupuesto-vs-real",    "Presupuesto vs real"),
        ("prevision-drivers",      "Previsión por drivers"),
        ("cascada-margen",         "Cascada de margen"),
        ("economia-unitaria",      "Economía unitaria"),
        ("analitica-adhoc",        "Analítica ad-hoc"),
        ("reparto-costes-abc",     "Reparto costes ABC"),
        ("posicion-tesoreria",     "Posición tesorería"),
        ("exposicion-divisa",      "Exposición divisa"),
        ("aprobacion-pagos",       "Aprobación pagos"),
        ("deuda",                  "Instrumentos de deuda"),
        ("borrador-nota",          "Borrador nota resultados"),
        ("qa-analistas",           "Q&A analistas"),
        ("registro-accionistas",   "Registro accionistas"),
        ("calendario-regulatorio", "Calendario regulatorio"),
    ],
    "equipo": [
        ("tareas-cierre",           "Mis tareas de cierre"),
        ("conciliacion-inteligente","Conciliación inteligente"),
        ("extraccion-documentos",   "Extracción documentos"),
        ("asientos-contables",      "Asientos contables"),
        ("conciliacion-cuentas",    "Conciliación cuentas"),
        ("consulta-normativa",      "Consulta normativa"),
        ("base-documental",         "Base documental"),
        ("report-builder",          "Report builder"),
        ("controles-calidad",       "Controles calidad"),
        ("formacion-epm",           "Formación EPM"),
    ],
}


def get_modulo(slug):
    """Devuelve la definición del módulo o None si no existe."""
    return MOCK_MODULOS.get(slug)


def iter_nav():
    """Itera sobre (visión, [(slug, label), ...]) para el sidebar."""
    return MOCK_NAV.items()
