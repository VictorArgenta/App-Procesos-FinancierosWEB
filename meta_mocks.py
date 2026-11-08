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
    "plan-estrategico": {
        "titulo": "Seguimiento del plan estratégico",
        "subtitulo": "Objetivos 2024-2026 y avance por iniciativa",
        "vision": "ceo",
        "fuente": "Oracle EPM · Workday Adaptive Planning",
        "ultima": "Actualizado · 2026-11-06",
        "layout": ["stat_ribbon", "semaforos", "action_hero", "tabla", "grafico_split", "grafico_sec", "bloques"],
        "stat_ribbon": [
            {"label": "OKR corporativo", "valor": "0,74", "desc": "+0,06 vs Q3", "tono": "pos"},
            {"label": "Iniciativas",     "valor": "24",   "desc": "17 en objetivo"},
            {"label": "En riesgo",       "valor": "5",    "desc": "ámbar", "tono": "warn"},
            {"label": "Fuera de plan",   "valor": "2",    "desc": "rojas", "tono": "neg"},
            {"label": "Hitos Q4",        "valor": "18",   "desc": "13 cumplidos"},
            {"label": "Presupuesto",     "valor": "68 %", "desc": "ejecutado YTD"},
        ],
        "semaforos": [
            {"label": "AI Platform",      "color": "verde", "valor": "82 %",  "desc": "Llama 4 Enterprise en pre-GA, adopción interna por delante del plan."},
            {"label": "Reality Labs",     "color": "rojo",  "valor": "54 %",  "desc": "Reducción de pérdidas por debajo del objetivo FY (-18 % vs -25 %)."},
            {"label": "Family of Apps",   "color": "verde", "valor": "91 %",  "desc": "Instagram Reels y Threads muy por encima de plan."},
            {"label": "Business Messaging","color": "verde","valor": "76 %",  "desc": "Monetización WhatsApp +41 % YoY."},
            {"label": "Infra & Capex",    "color": "ambar", "valor": "68 %",  "desc": "Capex AI por encima de plan; supervisado por el CFO."},
            {"label": "Regulación",       "color": "ambar", "valor": "63 %",  "desc": "DMA/DSA · adaptación en marcha, pero por detrás de plan."},
        ],
        "action_hero": {
            "id": "re-okr",
            "titulo": "Recalcular OKR corporativo",
            "desc": "Vuelve a puntuar las 24 iniciativas con los últimos datos de progreso cargados desde Oracle EPM y Workday Adaptive Planning.",
            "boton": "Lanzar recálculo",
            "act_index": 0,
        },
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
        "grafico_sec": {
            "tipo": "line",
            "titulo": "Evolución del OKR corporativo (0-1, últimos 12 meses)",
            "serie": [0.58, 0.60, 0.62, 0.63, 0.65, 0.66, 0.68, 0.69, 0.70, 0.72, 0.73, 0.74],
        },
        "tabla": {
            "titulo": "Iniciativas estratégicas priorizadas",
            "columnas": ["Iniciativa", "Pilar", "Avance", "Presupuesto",
                         "Owner", "Estado"],
            "filas": [
                ["Despliegue Llama 4 Enterprise",      "AI Platform",       "68 %",
                 "USD 1,4 B", "CTO",              "Alta"],
                ["Monetización WhatsApp Business",     "Business Msg.",     "102 %",
                 "USD 0,9 B", "CPO WhatsApp",     "Baja"],
                ["Cloud GPU · 1,2 M aceleradores",     "Infra & Capex",     "73 %",
                 "USD 32 B",  "SVP Infra",        "Media"],
                ["Reels · share of time 35 %",         "Family of Apps",    "91 %",
                 "USD 0,4 B", "Head of IG",       "Baja"],
                ["Reality Labs · reducir pérdidas 25 %","Reality Labs",     "54 %",
                 "USD 12 B",  "VP RL",            "Alta"],
                ["Programa cumplimiento DMA/DSA",      "Regulación",        "63 %",
                 "USD 0,2 B", "Chief Compliance", "Media"],
            ],
        },
        "acciones": [
            {
                "label": "Recalcular OKR corporativo",
                "icono": "refresh",
                "titulo": "Recalcular OKR corporativo",
                "pasos": [
                    "Consolidando progreso de 24 iniciativas…",
                    "Aplicando ponderaciones estratégicas…",
                    "Normalizando resultados…",
                ],
                "resultado": [
                    "OKR corporativo recalculado · 0,74 (de 0,73).",
                    "2 iniciativas pasan de amarillo a verde.",
                    "1 iniciativa pasa a rojo (Reality Labs · reducir pérdidas).",
                ],
            },
        ],
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

    "preparacion-reuniones": {
        "titulo": "Preparación de reuniones",
        "subtitulo": "Dossier ejecutivo generado para cada cita de la agenda",
        "vision": "ceo",
        "fuente": "Google Calendar · Salesforce · LinkedIn Sales Navigator",
        "ultima": "Sincronizado · hace 12 min",
        "layout": ["picker", "kpis", "timeline", "acciones", "grafico", "bloques"],
        "picker": {
            "id": "mtg",
            "campos": [
                {"label": "Reunión", "name": "reunion", "tipo": "select", "opciones": [
                    "Satya Nadella (Microsoft) · hoy 15:00",
                    "Consejo asesor AI safety · hoy 17:30",
                    "Analistas sell-side top-5 · mañana 09:30",
                    "CNIL (Francia) · mañana 14:00",
                    "Comité capital allocation · jueves 11:00",
                ]},
                {"label": "Profundidad", "name": "nivel", "tipo": "select", "opciones": [
                    "Briefing · 1 página",
                    "Dossier estándar · 4 páginas",
                    "Dossier ejecutivo · 8 páginas",
                ]},
            ],
            "boton": "Generar dossier",
            "accion": {
                "titulo": "Generando dossier ejecutivo",
                "pasos": [
                    "Consultando CRM e histórico de interacciones…",
                    "Recuperando últimos resultados y comunicados de la contraparte…",
                    "Agregando puntos abiertos y notas de reuniones previas…",
                    "Dando formato al briefing ejecutivo…",
                ],
                "resultado": [
                    "Dossier disponible en la base documental.",
                    "3 puntos clave de negociación destacados.",
                    "Enviado al asistente del CEO para revisión final.",
                ],
            },
        },
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
        "timeline": {
            "titulo": "Agenda próximos 3 días",
            "eventos": [
                {"cuando": "Hoy · 15:00", "titulo": "Satya Nadella (Microsoft)",
                 "desc": "Follow-up acuerdo Azure/Llama hosting — pricing GPU, SLAs, cláusulas de salida.",
                 "estado": "now"},
                {"cuando": "Hoy · 17:30", "titulo": "Consejo asesor de AI safety",
                 "desc": "Revisión del marco de red-teaming para Llama 5."},
                {"cuando": "Mañana · 09:30", "titulo": "Analistas sell-side top-5",
                 "desc": "Revisión de forecast Q4 y pipeline capex 2027."},
                {"cuando": "Mañana · 14:00", "titulo": "CNIL (Francia)",
                 "desc": "Audiencia preliminar sobre tratamiento de datos de menores."},
                {"cuando": "Jueves · 11:00", "titulo": "Comité ejecutivo capital allocation",
                 "desc": "Validación programa de recompra ampliado."},
            ],
        },
        "acciones": [
            {
                "label": "Generar dossier reunión seleccionada",
                "icono": "file",
                "titulo": "Generando dossier · Satya Nadella (Microsoft) · hoy 15:00",
                "pasos": [
                    "Consultando CRM e histórico de interacciones…",
                    "Recuperando últimos resultados y comunicaciones de Microsoft…",
                    "Agregando puntos abiertos y notas de reuniones previas…",
                    "Dando formato al briefing ejecutivo de 1 página…",
                ],
                "resultado": [
                    "Dossier de 4 páginas disponible en la base documental.",
                    "3 puntos clave de negociación destacados automáticamente.",
                    "Enviado al asistente del CEO para revisión final.",
                ],
            },
            {
                "label": "Sincronizar agenda",
                "icono": "calendar",
                "titulo": "Sincronizando con Google Calendar",
                "pasos": [
                    "Conectando con Google Calendar vía OAuth…",
                    "Revisando citas de los próximos 14 días…",
                    "Marcando reuniones sin dossier preparado…",
                ],
                "resultado": [
                    "4 reuniones nuevas detectadas · dossier en cola.",
                    "1 reunión reasignada al EA (presencial a remoto).",
                ],
            },
        ],
        "bloques": [
            {
                "titulo": "Preparación destacada",
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

    "alertas-proactivas": {
        "titulo": "Alertas financieras proactivas",
        "subtitulo": "Señales con impacto en resultados, caja o cumplimiento",
        "vision": "ceo",
        "fuente": "Oracle EPM · SAP S/4HANA · Kyriba · Snowflake",
        "ultima": "Motor de alertas · hace 3 min",
        "layout": ["stat_ribbon", "semaforos", "tabla", "acciones", "grafico", "bloques"],
        "stat_ribbon": [
            {"label": "Impacto P&L estimado", "valor": "USD -214 M", "desc": "últimas 24 h", "tono": "neg"},
            {"label": "Severidad alta",       "valor": "3",          "desc": "ingresos, capex, tesorería", "tono": "neg"},
            {"label": "Severidad media",      "valor": "6",          "desc": "márgenes, FX, impuestos", "tono": "warn"},
            {"label": "Silenciadas",          "valor": "2",          "desc": "auto-cerradas por el motor"},
            {"label": "Fuente principal",     "valor": "Oracle EPM", "desc": "+ SAP S/4HANA"},
            {"label": "SLA respuesta",        "valor": "< 2 h",      "desc": "para severidad alta"},
        ],
        "semaforos": [
            {"label": "Ingresos",   "color": "rojo",  "valor": "USD -72 M MTD", "desc": "Caída CPM Shop ads -8 % w/w. Probable regresión del ranker."},
            {"label": "Capex",      "color": "rojo",  "valor": "USD -84 M",     "desc": "Desvío +11 % vs plan octubre. Mayor presión FCF."},
            {"label": "Tesorería",  "color": "rojo",  "valor": "USD -38 M",     "desc": "Saldo cuenta Meta Brasil por debajo del umbral."},
            {"label": "Márgenes",   "color": "ambar", "valor": "USD -28 M",     "desc": "Coste GPU hora +6,2 % vs plan."},
            {"label": "FX",         "color": "ambar", "valor": "USD -22 M",     "desc": "EUR/USD -2,4 % desde el hedge dinámico."},
            {"label": "Covenants",  "color": "verde", "valor": "Sin breach",    "desc": "Net debt/EBITDA Q3 0,21x (vs 0,19 estimado)."},
        ],
        "kpis": [
            _kpi("Alertas abiertas", "11"),
            _kpi("Impacto estimado P&L", "USD -214 M", None, "neg"),
            _kpi("Severidad alta", "3", None, "neg"),
            _kpi("Severidad media", "6", None, "warn"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Alertas financieras por categoría (últimos 30 días)",
            "categorias": ["Ingresos", "Márgenes", "Capex", "Tesorería",
                           "Impuestos", "Covenants", "FX"],
            "serie": [18, 14, 9, 11, 6, 2, 8],
        },
        "tabla": {
            "titulo": "Alertas abiertas priorizadas",
            "columnas": ["Severidad", "Área", "Alerta",
                         "Impacto", "Responsable", "Edad"],
            "filas": [
                ["Alta",  "Ingresos",  "Caída CPM Shop ads -8 % w/w — regresión ranker",
                 "USD -72 M MTD",  "Monetization",        "2 días"],
                ["Alta",  "Capex",     "Desvío capex AI infra +11 % vs plan octubre",
                 "USD -84 M",      "FP&A Infra",          "4 días"],
                ["Alta",  "Tesorería", "Saldo cuenta Meta Brasil por debajo del umbral",
                 "USD -38 M",      "Treasury LatAm",      "1 día"],
                ["Media", "Márgenes", "Coste GPU hora +6,2 % vs plan",
                 "USD -28 M",      "Cost Mgmt",           "5 días"],
                ["Media", "FX",       "EUR/USD -2,4 % desde hedge dinámico",
                 "USD -22 M",      "Treasury",            "3 días"],
                ["Media", "Ingresos", "Reels fill-rate -1,1 pts en India",
                 "USD -14 M",      "Monetization APAC",   "6 días"],
                ["Media", "Impuestos","Nueva resolución Hacienda IE sobre royalties",
                 "USD -11 M est.",  "Tax",                 "2 días"],
                ["Media", "Covenants","Net debt/EBITDA Q3 0,21x (vs 0,19 estimado)",
                 "Sin breach",      "Treasury",            "1 día"],
                ["Baja",  "G&A",      "Consultores legales +9 % vs forecast",
                 "USD -6 M",        "Legal",               "8 días"],
            ],
        },
        "acciones": [
            {
                "label": "Lanzar diagnóstico ejecutivo",
                "icono": "zap",
                "titulo": "Diagnóstico financiero · últimas 24 h",
                "pasos": [
                    "Cruzando movimientos del DWH con el forecast activo…",
                    "Reconsultando SAP S/4HANA para cuentas con variación > 5 %…",
                    "Priorizando alertas por impacto en EBIT estimado…",
                ],
                "resultado": [
                    "7 nuevas alertas candidatas detectadas · 3 elevadas a severidad alta.",
                    "Impacto neto estimado a cierre de mes · USD -214 M (de -198 M).",
                    "Recomendación: convocar war room ingresos LatAm en 48 h.",
                ],
            },
            {
                "label": "Preparar nota para CFO",
                "icono": "file-text",
                "titulo": "Nota ejecutiva · impacto P&L estimado",
                "pasos": [
                    "Compilando alertas de severidad alta y media…",
                    "Agregando por línea P&L y responsable…",
                    "Dando formato al briefing CFO…",
                ],
                "resultado": [
                    "Nota de 2 páginas lista en la base documental.",
                    "Enviada notificación a CFO, Controller y Head of FP&A.",
                ],
            },
        ],
        "bloques": [
            {
                "titulo": "Alertas que requieren decisión del CEO",
                "bullets": [
                    "Revisión del plan capex AI infra · comité convocado para el 14-nov.",
                    "Lanzar hedge adicional EUR/USD por 2 B según memo del tesorero.",
                    "Validar comunicación al mercado sobre el ritmo de recompras.",
                ],
            },
        ],
    },

    "mapa-riesgos": {
        "titulo": "Mapa de riesgos financieros",
        "subtitulo": "Matriz 5×5 de probabilidad × impacto económico",
        "vision": "ceo",
        "fuente": "ServiceNow GRC · Oracle EPM · SAP TRM",
        "ultima": "Revisión mensual · 2026-11-03",
        "kpis": [
            _kpi("Riesgos financieros registrados", "72"),
            _kpi("Zona roja (alto × alto)", "6", None, "neg"),
            _kpi("Impacto esperado agregado", "USD 1,8 B"),
            _kpi("Cobertura mitigada", "68 %", "+4 pts YoY", "pos"),
        ],
        "grafico": {
            "tipo": "bar",
            "titulo": "Exposición financiera por categoría (USD M, ponderada por impacto)",
            "categorias": ["Mercado (FX, tipos)", "Crédito y contraparte",
                           "Liquidez y caja", "Fiscal y transfer pricing",
                           "Reporting y cierre", "Capex y proyectos"],
            "serie": [540, 320, 290, 410, 180, 340],
        },
        "tabla": {
            "titulo": "Top riesgos financieros priorizados",
            "columnas": ["Riesgo", "Categoría", "Probabilidad",
                         "Impacto estimado", "Mitigación", "Owner"],
            "filas": [
                ["Devaluación brusca BRL / INR",      "Mercado (FX)",      "Media",
                 "USD 320 M",    "Hedge dinámico 70 % exposure", "Tesorero"],
                ["Sostenibilidad del capex AI infra", "Capex",             "Media-alta",
                 "USD 450 M",    "Stage-gate trimestral",        "CFO"],
                ["Reclasificación fiscal royalties IE", "Fiscal",          "Media",
                 "USD 280 M",    "Defensa BEPS 2 + AP Legal",    "Head of Tax"],
                ["Concentración en 1 banco (18 % caja)","Crédito",         "Baja",
                 "USD 180 M",    "Diversificación a 5 bancos",   "Tesorería"],
                ["Error material en consolidación",   "Reporting",         "Baja",
                 "USD 120 M",    "Doble validación + 32 controles", "Controller"],
                ["Subida tipos y refinanciación 2028","Liquidez",          "Media",
                 "USD 160 M",    "Prefinanciación con bonos 7y", "Tesorero"],
            ],
        },
        "acciones": [
            {
                "label": "Recalcular exposición global",
                "icono": "refresh",
                "titulo": "Recalculo de exposición financiera",
                "pasos": [
                    "Consolidando posiciones en Kyriba y SAP TRM…",
                    "Aplicando shocks de mercado (±5 %, ±10 %, ±15 %)…",
                    "Agregando por entidad y divisa…",
                ],
                "resultado": [
                    "Exposición agregada actualizada · USD 1,82 B (de 1,78 B).",
                    "VaR 1D (95 %) · USD 44 M (+2 M).",
                    "Nueva exposición superior al umbral en: BRL, INR.",
                ],
            },
            {
                "label": "Simular stress-test de mercado",
                "icono": "activity",
                "titulo": "Stress-test · escenario adverso",
                "pasos": [
                    "Cargando curvas de tipos y spot FX al cierre…",
                    "Aplicando escenario crisis 2008 / COVID-20 / shock IR…",
                    "Calculando impacto en P&L y FCF a 12 meses…",
                ],
                "resultado": [
                    "Impacto estimado P&L bajo escenario crisis 2008 · USD -2,1 B.",
                    "Impacto estimado P&L bajo shock de tipos (+300 pb) · USD -0,8 B.",
                    "Capital ratio resultante · holgado (>18 pts sobre umbral).",
                ],
            },
        ],
        "bloques": [
            {
                "titulo": "Riesgos con acción pendiente del Consejo",
                "bullets": [
                    "Aumentar ratio de cobertura FX hasta el 80 % — propuesta ya elevada.",
                    "Pre-financiar vencimientos 2028 vía emisión bonos 10y.",
                    "Validar el apetito de riesgo fiscal post sentencia CJUE.",
                ],
            },
        ],
    },

    "guidance-tracker": {
        "titulo": "Seguimiento de expectativas al mercado",
        "subtitulo": "Comparación entre guidance interno, consenso de analistas y real",
        "vision": "ceo",
        "fuente": "Visible Alpha · Refinitiv · Oracle EPM",
        "ultima": "Último cierre · Q3 2026",
        "kpis": [
            _kpi("Guidance ingresos Q4", "USD 48-51 B"),
            _kpi("Consenso ingresos Q4", "USD 49,4 B", "+2,1 %", "pos"),
            _kpi("Guidance Capex FY", "USD 72-75 B"),
            _kpi("Analistas dentro del rango", "7 / 10", "70 %", "pos"),
        ],
        "grafico": {
            "tipo": "mixed",
            "titulo": "Guidance vs consenso vs real (ingresos trimestrales, USD B)",
            "categorias": ["Q2-24","Q3-24","Q4-24","Q1-25","Q2-25","Q3-25",
                           "Q4-25","Q1-26","Q2-26","Q3-26","Q4-26E"],
            "series": [
                {"name": "Guidance (medio)",  "type": "bar",  "data": [28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 49.5]},
                {"name": "Consenso analistas","type": "line", "data": [28.4, 31.8, 32.5, 34.4, 36.9, 38.5, 40.0, 42.3, 45.1, 47.0, 49.4]},
                {"name": "Real",              "type": "line", "data": [28.6, 32.0, 32.2, 34.1, 36.5, 38.3, 40.1, 42.0, 44.8, 47.5, None]},
            ],
        },
        "tabla": {
            "titulo": "Guidance vs consenso · métricas clave FY2026",
            "columnas": ["Métrica", "Guidance (rango)", "Consenso", "Real / YTD",
                         "Analistas dentro", "Estado"],
            "filas": [
                ["Ingresos (USD B)",        "180 - 192", "187,2", "174 YTD",      "8 / 10", "Baja"],
                ["Margen operativo (%)",    "42 - 45",   "43,8",   "44,2 YTD",     "9 / 10", "Baja"],
                ["Capex (USD B)",           "72 - 75",   "73,8",   "61 YTD",       "6 / 10", "Media"],
                ["Headcount FY (miles)",    "74 - 76",   "74,8",   "74,2",         "9 / 10", "Baja"],
                ["Tax rate efectivo (%)",   "17 - 19",   "18,1",   "17,8 YTD",     "9 / 10", "Baja"],
                ["FCF (USD B)",             "22 - 28",   "24,1",   "19 YTD",       "6 / 10", "Media"],
            ],
        },
        "acciones": [
            {
                "label": "Sincronizar consenso de analistas",
                "icono": "download",
                "titulo": "Sincronizando consenso Visible Alpha · Refinitiv",
                "pasos": [
                    "Conectando con Visible Alpha…",
                    "Descargando estimaciones de 32 analistas sell-side…",
                    "Reconciliando con últimos resultados publicados…",
                    "Agregando por métrica y trimestre…",
                ],
                "resultado": [
                    "Consenso actualizado al 2026-11-07 08:12.",
                    "3 analistas han movido su estimación Q4 a la baja.",
                    "Consenso ingresos FY2026 · USD 187,2 B (de 186,8 B).",
                ],
            },
        ],
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
        "grafico_sec": {
            "tipo": "bar",
            "titulo": "Rotación voluntaria por función (%)",
            "categorias": ["AI Research", "AI Infra", "Ventas", "Producto",
                           "Operaciones", "Finanzas", "G&A"],
            "serie": [9.4, 8.1, 7.2, 6.8, 5.9, 4.2, 3.6],
        },
        "tabla": {
            "titulo": "Plantilla y eNPS por región",
            "columnas": ["Región", "Plantilla", "YTD", "Rotación",
                         "eNPS", "Posiciones críticas abiertas"],
            "filas": [
                ["EEUU/Canadá",    "41.820", "+1,8 %", "6,2 %",   "36", "62"],
                ["Europa (EMEA)",  "15.960", "+2,6 %", "5,9 %",   "38", "28"],
                ["Asia-Pacífico",  "11.240", "+3,8 %", "9,1 %",   "27", "24"],
                ["Latinoamérica",  "5.193",  "+1,1 %", "7,4 %",   "33", "14"],
            ],
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
        "timeline": {
            "titulo": "Línea de tiempo del cierre · octubre 2026",
            "eventos": [
                {"cuando": "D+1 · lunes", "titulo": "Carga automática de datos SAP S/4HANA", "desc": "47 entidades (de 49) carga completa.", "estado": "done"},
                {"cuando": "D+2 · martes", "titulo": "Validaciones automáticas (32 controles)", "desc": "28 controles OK · 4 en revisión.", "estado": "now"},
                {"cuando": "D+3 · miércoles", "titulo": "Ajustes top-side y eliminaciones IC", "desc": "32 ajustes previstos — 6 con comentario pendiente."},
                {"cuando": "D+5 · viernes", "titulo": "Revisión controller + firma CFO", "desc": "Hora objetivo 14:00 CET."},
                {"cuando": "D+8 · lunes +1", "titulo": "Publicación cierre consolidado", "desc": "Hora objetivo 09:00 CET."},
            ],
        },
        "acciones": [
            {
                "label": "Lanzar validación automática",
                "icono": "check",
                "titulo": "Validación automática · 32 controles",
                "pasos": [
                    "Recuperando saldos preliminares de 47 entidades…",
                    "Aplicando reglas de variación material (>5 %)…",
                    "Cruzando posiciones intercompany…",
                    "Verificando reconciliaciones automáticas en BlackLine…",
                ],
                "resultado": [
                    "28 de 32 controles OK. 4 en revisión manual.",
                    "Incidencias detectadas · Meta Brasil (devengos), Oculus HW (inventario).",
                    "Tiempo medio por control · 11 s.",
                ],
            },
            {
                "label": "Recalcular estimación a D+2",
                "icono": "refresh",
                "titulo": "Recalculo rápido · EBIT estimado",
                "pasos": [
                    "Recuperando datos actualizados hasta las 23:59 de ayer…",
                    "Aplicando devengos preliminares…",
                    "Ajustando por FX a tipo medio mensual…",
                ],
                "resultado": [
                    "EBIT estimado octubre · USD 5,745 B (+USD 165 M vs plan).",
                    "Beneficio neto estimado · USD 4,62 B.",
                    "Caja operativa estimada · USD 6,1 B.",
                ],
            },
        ],
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
        "grafico_sec": {
            "tipo": "bar",
            "titulo": "Capex planificado por trimestre (USD B)",
            "categorias": ["Q1-26","Q2-26","Q3-26","Q4-26E",
                           "Q1-27E","Q2-27E","Q3-27E","Q4-27E"],
            "serie": [17.2, 18.6, 20.1, 22.1, 23.2, 24.4, 25.6, 26.8],
        },
        "tabla": {
            "titulo": "Previsión por trimestre · ingresos y EBIT (USD B)",
            "columnas": ["Trimestre", "Ingresos", "YoY", "EBIT",
                         "Margen EBIT", "FCF estimado"],
            "filas": [
                ["Q1-26",  "42,0",  "+16 %", "17,9", "42,6 %", "6,8"],
                ["Q2-26",  "44,8",  "+18 %", "19,6", "43,8 %", "5,2"],
                ["Q3-26",  "47,5",  "+19 %", "21,1", "44,4 %", "4,1"],
                ["Q4-26E", "50,2",  "+22 %", "22,4", "44,6 %", "3,8"],
                ["Q1-27E", "52,1",  "+24 %", "22,8", "43,8 %", "3,2"],
                ["Q2-27E", "54,3",  "+21 %", "24,0", "44,2 %", "4,6"],
                ["Q3-27E", "56,8",  "+20 %", "25,1", "44,2 %", "5,8"],
                ["Q4-27E", "59,1",  "+18 %", "26,4", "44,7 %", "6,1"],
            ],
        },
        "acciones": [
            {
                "label": "Recalcular con drivers actualizados",
                "icono": "refresh",
                "titulo": "Recalculando forecast con drivers vivos",
                "pasos": [
                    "Recuperando valores de los 88 drivers principales…",
                    "Aplicando modelos driver-based (volumen × precio × mix)…",
                    "Propagando por trimestre a 18 meses…",
                    "Agregando por línea P&L y entidad…",
                ],
                "resultado": [
                    "Forecast FY2026 ingresos · USD 189 B (de 186 B).",
                    "Forecast FY2026 EBIT · USD 76 B (+2 B).",
                    "FCF revisado · USD 24 B (-1 B por mayor capex AI infra).",
                ],
            },
            {
                "label": "Simular escenario +10 % GPU",
                "icono": "activity",
                "titulo": "Sensibilidad · +10 % coste GPU",
                "pasos": [
                    "Aplicando shock de +10 % al coste GPU hora…",
                    "Propagando por volumen de computación proyectado…",
                    "Recalculando margen y FCF…",
                ],
                "resultado": [
                    "Opex AI infra FY2026 · +USD 1,6 B.",
                    "Margen EBIT · -0,9 pts (de 44,2 % a 43,3 %).",
                    "FCF · -USD 1,1 B (ajustado por crédito fiscal esperado).",
                ],
            },
        ],
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
        "grafico_sec": {
            "tipo": "mixed",
            "titulo": "Cobros y pagos semanales (USD B)",
            "categorias": ["S46","S47","S48","S49","S50",
                           "S51","S52","S1","S2","S3","S4","S5","S6"],
            "series": [
                {"name": "Cobros", "type": "bar",  "data": [4.1, 4.4, 4.6, 4.8, 4.9, 5.2, 5.4, 4.2, 4.3, 4.5, 4.7, 5.1, 5.6]},
                {"name": "Pagos",  "type": "bar",  "data": [4.3, 7.8, 4.5, 6.2, 4.2, 6.1, 4.4, 4.1, 4.2, 4.1, 4.3, 4.5, 4.4]},
            ],
        },
        "tabla": {
            "titulo": "Movimientos semanales previstos (USD B)",
            "columnas": ["Semana", "Cobros", "Pagos", "Flujo neto",
                         "Saldo final", "Hito"],
            "filas": [
                ["S46 · 10-nov", "4,1", "4,3", "-0,2", "43,9", "—"],
                ["S47 · 17-nov", "4,4", "7,8", "-3,4", "40,5", "Pago impuestos USA · 7,3 B"],
                ["S48 · 24-nov", "4,6", "4,5", "+0,1", "40,6", "—"],
                ["S49 · 01-dic", "4,8", "6,2", "-1,4", "39,2", "Vencimiento bono senior · 2,5 B"],
                ["S50 · 08-dic", "4,9", "4,2", "+0,7", "39,9", "—"],
                ["S51 · 15-dic", "5,2", "6,1", "-0,9", "39,0", "Dividendo trimestral · 1,3 B"],
                ["S52 · 22-dic", "5,4", "4,4", "+1,0", "40,0", "Emisión bonos EMTN · +1,5 B"],
                ["S1-6 · ene-feb", "27,9", "26,5", "+1,4", "48,6", "—"],
            ],
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
        "layout": ["semaforos", "stat_ribbon", "grafico", "acciones", "bloques"],
        "semaforos": [
            {"label": "Net debt / EBITDA", "color": "verde", "valor": "0,21x", "desc": "Covenant ≤ 2,0x · holgura de 1,79x."},
            {"label": "EBITDA / Intereses","color": "verde", "valor": "28,4x", "desc": "Covenant ≥ 4,0x · amplio margen."},
            {"label": "Deuda / Patrimonio","color": "verde", "valor": "0,28",  "desc": "Covenant ≤ 1,0 · sin tensiones."},
            {"label": "Liquidez (RCF + caja)","color": "verde", "valor": "USD 58 B", "desc": "Holgura > 18 meses de servicio."},
            {"label": "Vencimientos 12m",  "color": "ambar", "valor": "USD 3,0 B", "desc": "Refinanciación pre-aprobada vía EMTN."},
            {"label": "Alertas abiertas",  "color": "verde", "valor": "0",        "desc": "Último trimestre sin incidencias."},
        ],
        "stat_ribbon": [
            {"label": "Covenants revisados", "valor": "12/12", "desc": "cada contrato", "tono": "pos"},
            {"label": "Próximo test",        "valor": "31-12", "desc": "RCF trimestral"},
            {"label": "Próximo test EMTN",   "valor": "30-06-27"},
            {"label": "Buffer EBITDA",       "valor": "USD 72 B"},
            {"label": "Buffer intereses",    "valor": "USD 2,6 B"},
        ],
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
        "tabla": {
            "titulo": "Buckets de inversión · plan FY vs YTD vs retorno esperado",
            "columnas": ["Bucket", "Plan FY (USD B)", "YTD (USD B)",
                         "% ejecución", "Retorno esperado", "Horizonte"],
            "filas": [
                ["Capex AI Infra",           "48,0", "38,4", "80 %", "IRR 18-22 %", "7 años"],
                ["Capex Reality Labs",       "14,0", "10,5", "75 %", "IRR 10-14 %", "10 años"],
                ["Capex productividad FoA",  "17,0", "12,1", "71 %", "IRR 20-28 %", "5 años"],
                ["Programa recompras",       "36,0", "29,0", "81 %", "ROE 26 %",     "continuo"],
                ["Dividendos",               "6,5",  "5,2",  "80 %", "Yield 0,5 %",   "trimestral"],
                ["M&A estratégico",          "4,0",  "1,8",  "45 %", "IRR > 15 %",    "variable"],
            ],
        },
        "acciones": [
            {
                "label": "Simular nueva asignación",
                "icono": "activity",
                "titulo": "Simulación · re-asignación de capital 2027",
                "pasos": [
                    "Cargando plan de capital 2026 como base…",
                    "Aplicando nuevas cuotas por bucket (AI +15 %, RL -8 %)…",
                    "Recalculando IRR ponderado y FCF…",
                    "Evaluando impacto en rating y en recompras…",
                ],
                "resultado": [
                    "IRR ponderado del portfolio sube de 17,2 % a 18,4 %.",
                    "FCF año 1 · -USD 1,8 B · año 2 · +USD 1,1 B.",
                    "Sin impacto en rating según modelo interno.",
                ],
            },
        ],
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
        "layout": ["checklist", "stat_ribbon", "tabla", "acciones", "grafico"],
        "checklist": {
            "titulo": "Cierre octubre · estado por fase",
            "items": [
                {"texto": "D+0 · bloqueo de documentos nuevos",                    "hecho": True},
                {"texto": "D+1 · carga automática de datos SAP S/4HANA (49 entidades)", "hecho": True},
                {"texto": "D+2 · validaciones automáticas (32 controles de calidad)",    "hecho": True},
                {"texto": "D+3 · ajustes top-side y eliminaciones intercompany",  "hecho": False},
                {"texto": "D+4 · conciliación de operaciones intercompany",       "hecho": False},
                {"texto": "D+5 · revisión controller y firma CFO",                "hecho": False},
                {"texto": "D+6 · generación estatutaria vs gestión",              "hecho": False},
                {"texto": "D+8 · publicación cierre consolidado al grupo",        "hecho": False},
            ],
        },
        "stat_ribbon": [
            {"label": "Entidades reportando",  "valor": "47/49", "desc": "96 %", "tono": "warn"},
            {"label": "Journal entries",       "valor": "12.418","desc": "+6 % YoY"},
            {"label": "Ajustes top-side",      "valor": "32"},
            {"label": "Horas medias cierre",   "valor": "68 h",  "desc": "-8 h vs 2025", "tono": "pos"},
            {"label": "Controles OK",          "valor": "28/32", "desc": "4 en revisión"},
        ],
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
        "vision": "equipo",
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
        "tabla": {
            "titulo": "Diferencias intercompany prioritarias",
            "columnas": ["Severidad", "Par", "Concepto",
                         "Importe", "Edad", "Owner"],
            "filas": [
                ["Alta",  "Meta Ireland ↔ Meta Platforms Inc.",   "Royalties licencias IP",
                 "USD 3,2 M", "11 días", "Controller IE"],
                ["Alta",  "Meta Singapore ↔ Meta APAC Services",  "Servicios compartidos",
                 "USD 1,1 M", "9 días",  "Controller SG"],
                ["Media", "Meta Brasil ↔ Meta Platforms Inc.",    "Pagos de ads buyback",
                 "USD 0,8 M", "7 días",  "Controller BR"],
                ["Media", "Meta UK ↔ Meta Ireland",               "Facturación servicios IT",
                 "USD 0,6 M", "5 días",  "Controller UK"],
                ["Baja",  "Meta Japón ↔ Meta APAC Services",      "Reimbursements",
                 "USD 0,3 M", "4 días",  "Controller JP"],
                ["Baja",  "Oculus HW ↔ Meta Platforms Inc.",      "Precio transfer HW",
                 "USD 0,2 M", "3 días",  "Controller RL"],
            ],
        },
        "acciones": [
            {
                "label": "Lanzar matching automático",
                "icono": "zap",
                "titulo": "Matching intercompany · 420 pares",
                "pasos": [
                    "Conectando con SAP Group Reporting…",
                    "Cargando movimientos pendientes…",
                    "Aplicando reglas de matcheo (tolerancia ±0,5 %)…",
                    "Enviando a BlackLine para validación…",
                ],
                "resultado": [
                    "412 pares conciliados automáticamente (de 420).",
                    "8 diferencias por encima del umbral material (USD 100 k).",
                    "Tiempo total · 2 min 14 s.",
                ],
            },
        ],
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
        "subtitulo": "Margen por negocio, canal, producto, país y tipología de cliente",
        "vision": "cfo",
        "fuente": "Snowflake · Oracle EPM",
        "ultima": "YTD octubre",
        "layout": ["kpis", "dim_switcher", "acciones", "bloques"],
        "dim_switcher": {
            "titulo": "Análisis de rentabilidad — selecciona dimensión",
            "pestanas": [
                {
                    "key": "negocio", "label": "Por negocio",
                    "grafico": {"tipo": "bar", "titulo": "Margen operativo por segmento (%)",
                                "categorias": ["Family of Apps", "Reality Labs", "Business Messaging"],
                                "serie": [48, -74, 22]},
                    "narrativa_titulo": "Lectura por negocio",
                    "narrativa": [
                        "FoA concentra >95 % del margen operativo del grupo.",
                        "Reality Labs sigue en inversión; mejora 4 pts YoY.",
                        "Business Messaging empieza a aportar margen positivo.",
                    ],
                    "tabla": {"columnas": ["Negocio", "Ingresos (USD B)", "EBIT (USD B)", "Margen", "YoY"],
                              "filas": [
                                  ["Family of Apps",    "143,0", "68,6",  "48 %",  "+2 pts"],
                                  ["Reality Labs",      "2,1",   "-1,6",  "-74 %", "+4 pts"],
                                  ["Business Messaging","4,9",   "1,1",   "22 %",  "+9 pts"],
                              ]},
                },
                {
                    "key": "canal", "label": "Por canal",
                    "grafico": {"tipo": "bar", "titulo": "Margen operativo por canal publicitario (%)",
                                "categorias": ["Instagram Reels", "Instagram Feed", "Facebook Feed",
                                               "WhatsApp Business", "Messenger", "Audience Network"],
                                "serie": [55, 52, 50, 38, 44, 29]},
                    "narrativa_titulo": "Lectura por canal",
                    "narrativa": [
                        "Reels es el canal de mayor margen absoluto y crece deprisa.",
                        "Audience Network · margen más bajo, saturación de inventario fuera-plataforma.",
                    ],
                    "tabla": {"columnas": ["Canal", "Ingresos (USD B)", "Margen", "Variación YoY"],
                              "filas": [
                                  ["Instagram Reels",    "46,1", "55 %", "+5 pts"],
                                  ["Instagram Feed",     "28,4", "52 %", "+1 pt"],
                                  ["Facebook Feed",      "34,2", "50 %", "flat"],
                                  ["WhatsApp Business",  "4,9",  "38 %", "+8 pts"],
                                  ["Messenger",          "6,1",  "44 %", "-1 pt"],
                                  ["Audience Network",   "23,3", "29 %", "-2 pts"],
                              ]},
                },
                {
                    "key": "producto", "label": "Por producto",
                    "grafico": {"tipo": "bar_h", "titulo": "Margen contribución por producto (%)",
                                "categorias": ["Reels", "Feed IG", "Feed FB", "Stories",
                                               "Shops", "Threads", "WhatsApp", "Messenger"],
                                "serie": [62, 58, 56, 54, 32, 24, 42, 46]},
                    "narrativa_titulo": "Lectura por producto",
                    "narrativa": [
                        "Shops y Threads todavía en fase de inversión.",
                        "Reels aporta el mayor margen contribución absoluto.",
                    ],
                    "tabla": {"columnas": ["Producto", "Margen contribución", "Fase"],
                              "filas": [
                                  ["Reels",    "62 %", "Escalar"],
                                  ["Feed IG",  "58 %", "Maduro"],
                                  ["Feed FB",  "56 %", "Maduro"],
                                  ["Stories",  "54 %", "Maduro"],
                                  ["Shops",    "32 %", "Inversión"],
                                  ["Threads",  "24 %", "Inversión"],
                                  ["WhatsApp", "42 %", "Escalar"],
                                  ["Messenger","46 %", "Optimizar"],
                              ]},
                },
                {
                    "key": "pais", "label": "Por país",
                    "grafico": {"tipo": "bar", "titulo": "Margen operativo por región (%)",
                                "categorias": ["EEUU/CA", "Europa", "Asia-Pacífico", "Latinoamérica", "Oriente Medio/África"],
                                "serie": [61, 51, 42, 38, 36]},
                    "narrativa_titulo": "Lectura por país / región",
                    "narrativa": [
                        "EEUU/CA mantiene el liderazgo en ARPU y margen.",
                        "APAC y LatAm con mayor crecimiento pero menor monetización.",
                    ],
                    "tabla": {"columnas": ["Región", "Ingresos (USD B)", "ARPU (USD)", "Margen", "Crec. YoY"],
                              "filas": [
                                  ["EEUU/CA",            "72,1", "72,4", "61 %", "+11 %"],
                                  ["Europa",             "38,4", "25,8", "51 %", "+16 %"],
                                  ["Asia-Pacífico",      "22,8", "7,9",  "42 %", "+21 %"],
                                  ["Latinoamérica",      "10,2", "6,2",  "38 %", "+24 %"],
                                  ["Oriente Medio/África","6,5", "4,4",  "36 %", "+19 %"],
                              ]},
                },
                {
                    "key": "cliente", "label": "Por tipo de cliente",
                    "grafico": {"tipo": "bar", "titulo": "Margen contribución por tipología de anunciante (%)",
                                "categorias": ["Top 100 global", "Direct brand", "Direct performance",
                                               "Agencias", "Mid-market", "SMB"],
                                "serie": [61, 58, 55, 52, 46, 42]},
                    "narrativa_titulo": "Lectura por tipo de cliente",
                    "narrativa": [
                        "Top 100 globales aportan el 38 % de los ingresos a un margen >60 %.",
                        "SMB es el segmento con mayor volumen de cuentas pero menor margen.",
                    ],
                    "tabla": {"columnas": ["Segmento", "Cuentas", "Ingresos (USD B)", "Margen", "ARPA (USD)"],
                              "filas": [
                                  ["Top 100 global",     "100",         "58,2", "61 %",  "582 M"],
                                  ["Direct brand",       "3.420",       "32,1", "58 %",  "9,4 M"],
                                  ["Direct performance", "11.800",      "28,9", "55 %",  "2,4 M"],
                                  ["Agencias",           "2.840",       "12,6", "52 %",  "4,4 M"],
                                  ["Mid-market",         "48.600",      "14,8", "46 %",  "304 k"],
                                  ["SMB",                "1.240.000",   "3,4",  "42 %",  "2,7 k"],
                              ]},
                },
            ],
        },
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
        "grafico_sec": {
            "tipo": "bar",
            "titulo": "Margen contribución por tipología de anunciante (%)",
            "categorias": ["Top 100 global", "Direct (brand)", "Direct (perf.)",
                           "Agencias", "Mid-market", "SMB"],
            "serie": [61, 58, 55, 52, 46, 42],
        },
        "tabla": {
            "titulo": "Margen por canal y región (%)",
            "columnas": ["Canal", "Global", "EEUU/CA", "Europa",
                         "APAC", "RoW"],
            "filas": [
                ["Instagram Reels",    "55", "61", "54", "48", "41"],
                ["Instagram Feed",     "52", "58", "51", "46", "39"],
                ["Facebook Feed",      "50", "56", "49", "44", "37"],
                ["Messenger",          "44", "49", "43", "39", "33"],
                ["WhatsApp Business",  "38", "42", "40", "36", "31"],
                ["Audience Network",   "29", "32", "28", "26", "22"],
            ],
        },
        "acciones": [
            {
                "label": "Cruzar canal × segmento × geografía",
                "icono": "grid",
                "titulo": "Cruce de dimensiones · canal × segmento × geografía",
                "pasos": [
                    "Cargando datos consolidados desde Snowflake…",
                    "Pivotando por canal, segmento y geografía…",
                    "Aplicando ABC costing para asignar costes directos…",
                    "Calculando margen contribución por celda…",
                ],
                "resultado": [
                    "16.280 celdas analizadas en 2,4 s.",
                    "Mayor margen · Reels · Top 100 · EEUU/CA · 72 %.",
                    "Menor margen · Audience Network · SMB · APAC · 11 %.",
                ],
            },
        ],
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
        "tabla": {
            "titulo": "Desviaciones YTD por línea P&L",
            "columnas": ["Línea", "Plan YTD (USD B)", "Real YTD",
                         "Var. abs.", "Var. %", "Responsable"],
            "filas": [
                ["Ingresos",      "148,0", "154,2", "+6,2",  "+4,2 %",   "CRO"],
                ["Coste ventas",  "36,4",  "37,3",  "+0,9",  "+2,5 %",   "COO"],
                ["I+D",           "32,8",  "34,2",  "+1,4",  "+4,3 %",   "CTO"],
                ["Marketing",     "9,6",   "10,2",  "+0,6",  "+6,3 %",   "CMO"],
                ["G&A",           "8,2",   "8,4",   "+0,2",  "+2,4 %",   "COO"],
                ["Capex",         "56,9",  "61,0",  "+4,1",  "+7,2 %",   "SVP Infra"],
                ["EBIT",          "61,0",  "64,6",  "+3,6",  "+5,9 %",   "—"],
            ],
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
        "layout": ["kpis", "grafico_lg", "acciones", "bloques"],
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

    "reparto-costes-abc": {
        "titulo": "Reparto de costes ABC",
        "subtitulo": "Activity-based costing con análisis multidimensional",
        "vision": "cfo",
        "fuente": "Oracle EPM Cost Management",
        "ultima": "Último recálculo · 2026-11-01",
        "layout": ["stat_ribbon", "dim_switcher", "acciones", "bloques"],
        "stat_ribbon": [
            {"label": "Actividades modelizadas", "valor": "214"},
            {"label": "Drivers activos",         "valor": "88"},
            {"label": "Costes asignados",        "valor": "USD 46 B", "desc": "100 %", "tono": "pos"},
            {"label": "Sin asignar",             "valor": "USD 0",    "desc": "conservación OK", "tono": "pos"},
            {"label": "Pool de infra",           "valor": "USD 18,4 B"},
            {"label": "Pool de moderación",      "valor": "USD 7,1 B"},
        ],
        "dim_switcher": {
            "titulo": "Reparto de costes — selecciona dimensión",
            "pestanas": [
                {
                    "key": "negocio", "label": "Por negocio",
                    "grafico": {"tipo": "bar", "titulo": "Coste asignado por segmento (USD B)",
                                "categorias": ["Family of Apps", "Reality Labs", "Business Messaging"],
                                "serie": [38.2, 5.4, 2.4]},
                    "narrativa_titulo": "Reparto por negocio",
                    "narrativa": [
                        "FoA concentra el 83 % de los costes asignados.",
                        "Reality Labs sigue siendo intensivo en I+D y hardware.",
                    ],
                    "tabla": {"columnas": ["Negocio", "Coste (USD B)", "% total", "Driver principal"],
                              "filas": [
                                  ["Family of Apps",     "38,2", "83 %", "Horas GPU"],
                                  ["Reality Labs",       "5,4",  "12 %", "I+D hardware"],
                                  ["Business Messaging", "2,4",  "5 %",  "Moderación"],
                              ]},
                },
                {
                    "key": "producto", "label": "Por producto",
                    "grafico": {"tipo": "bar_h", "titulo": "Coste total por producto (USD B)",
                                "categorias": ["Reels", "Feed IG", "Feed FB", "WhatsApp Business",
                                               "Messenger", "Threads", "Reality Labs HW"],
                                "serie": [11.7, 7.5, 6.6, 4.5, 2.7, 1.8, 2.8]},
                    "narrativa_titulo": "Reparto por producto",
                    "narrativa": [
                        "Reels es el producto con mayor consumo absoluto (38 % del coste de infra).",
                        "WhatsApp Business sigue en fase de inversión agresiva.",
                    ],
                    "tabla": {"columnas": ["Producto", "Infra", "Moderación", "Producto & diseño", "Total"],
                              "filas": [
                                  ["Instagram Reels",    "7,0", "1,2", "2,1", "11,7"],
                                  ["Instagram Feed",     "3,8", "1,1", "1,6", "7,5"],
                                  ["Facebook Feed",      "3,2", "1,0", "1,4", "6,6"],
                                  ["WhatsApp Business",  "1,6", "1,0", "0,9", "4,5"],
                                  ["Messenger",          "1,2", "0,6", "0,5", "2,7"],
                                  ["Threads",            "0,8", "0,4", "0,4", "1,8"],
                                  ["Reality Labs HW",    "0,8", "0,3", "0,9", "2,8"],
                              ]},
                },
                {
                    "key": "pais", "label": "Por país",
                    "grafico": {"tipo": "bar", "titulo": "Coste asignado por región (USD B)",
                                "categorias": ["EEUU/CA", "Europa", "Asia-Pacífico",
                                               "Latinoamérica", "Oriente Medio/África"],
                                "serie": [22.4, 10.1, 7.8, 3.2, 2.5]},
                    "narrativa_titulo": "Reparto por país / región",
                    "narrativa": [
                        "EEUU/CA concentra el grueso del coste por localización de clusters.",
                        "APAC y LatAm al alza por despliegue de data centers.",
                    ],
                    "tabla": {"columnas": ["Región", "Coste (USD B)", "% total", "Ingresos cubiertos"],
                              "filas": [
                                  ["EEUU/CA",             "22,4", "49 %", "USD 72,1 B"],
                                  ["Europa",              "10,1", "22 %", "USD 38,4 B"],
                                  ["Asia-Pacífico",       "7,8",  "17 %", "USD 22,8 B"],
                                  ["Latinoamérica",       "3,2",  "7 %",  "USD 10,2 B"],
                                  ["Oriente Medio/África","2,5",  "5 %",  "USD 6,5 B"],
                              ]},
                },
                {
                    "key": "cliente", "label": "Por tipo de cliente",
                    "grafico": {"tipo": "bar", "titulo": "Coste atribuible por segmento de cliente (USD B)",
                                "categorias": ["Top 100 global", "Direct brand", "Direct performance",
                                               "Agencias", "Mid-market", "SMB"],
                                "serie": [12.1, 9.4, 8.0, 4.2, 6.1, 6.2]},
                    "narrativa_titulo": "Reparto por tipo de cliente",
                    "narrativa": [
                        "SMB consume más coste de moderación y soporte por ticket.",
                        "Top 100 global sigue siendo el segmento más eficiente en coste por USD ingreso.",
                    ],
                    "tabla": {"columnas": ["Segmento", "Coste (USD B)", "Ingresos (USD B)", "Coste / USD ingreso"],
                              "filas": [
                                  ["Top 100 global",      "12,1", "58,2", "0,21"],
                                  ["Direct brand",        "9,4",  "32,1", "0,29"],
                                  ["Direct performance",  "8,0",  "28,9", "0,28"],
                                  ["Agencias",            "4,2",  "12,6", "0,33"],
                                  ["Mid-market",          "6,1",  "14,8", "0,41"],
                                  ["SMB",                 "6,2",  "3,4",  "1,82"],
                              ]},
                },
                {
                    "key": "actividad", "label": "Por actividad",
                    "grafico": {"tipo": "donut", "titulo": "Reparto por tipo de actividad (USD B)",
                                "serie": [
                                    {"name": "Infra computing",      "value": 18.4},
                                    {"name": "Content moderation",   "value": 7.1},
                                    {"name": "Producto & diseño",    "value": 7.8},
                                    {"name": "Sales & partner",      "value": 6.3},
                                    {"name": "Soporte anunciante",   "value": 3.6},
                                    {"name": "Legal & compliance",   "value": 2.8},
                                ]},
                    "narrativa_titulo": "Reparto por actividad",
                    "narrativa": [
                        "Infra computing es la actividad dominante y crece al ritmo del capex AI.",
                        "Legal & compliance al alza por fragmentación regulatoria.",
                    ],
                    "tabla": {"columnas": ["Actividad", "Coste (USD B)", "Driver", "YoY"],
                              "filas": [
                                  ["Infra computing",    "18,4", "Horas GPU",        "+22 %"],
                                  ["Content moderation", "7,1",  "Items revisados",  "+8 %"],
                                  ["Producto & diseño",  "7,8",  "FTE producto",     "+4 %"],
                                  ["Sales & partner",    "6,3",  "Cuentas gestionadas","+6 %"],
                                  ["Soporte anunciante", "3,6",  "Tickets atendidos","+9 %"],
                                  ["Legal & compliance", "2,8",  "Casos activos",    "+14 %"],
                              ]},
                },
            ],
        },
        "grafico": {
            "tipo": "bar",
            "titulo": "Reparto por tipo de actividad (USD B)",
            "categorias": ["Infra computing", "Content moderation",
                           "Sales & partner", "Producto & diseño",
                           "Soporte anunciante", "Legal & compliance"],
            "serie": [18.4, 7.1, 6.3, 7.8, 3.6, 2.8],
        },
        "tabla": {
            "titulo": "Reparto de costes por producto (USD B, YTD)",
            "columnas": ["Producto", "Infra", "Moderación",
                         "Producto", "Sales & partner", "Total"],
            "filas": [
                ["Instagram Reels",   "7,0",  "1,2",  "2,1",  "1,4",  "11,7"],
                ["Instagram Feed",    "3,8",  "1,1",  "1,6",  "1,0",  "7,5"],
                ["Facebook Feed",     "3,2",  "1,0",  "1,4",  "1,0",  "6,6"],
                ["WhatsApp Business", "1,6",  "1,0",  "0,9",  "1,0",  "4,5"],
                ["Messenger",         "1,2",  "0,6",  "0,5",  "0,4",  "2,7"],
                ["Threads",           "0,8",  "0,4",  "0,4",  "0,2",  "1,8"],
                ["Reality Labs HW",   "0,8",  "0,3",  "0,9",  "0,8",  "2,8"],
            ],
        },
        "acciones": [
            {
                "label": "Lanzar nuevo reparto ABC",
                "icono": "refresh",
                "titulo": "Reparto ABC · ciclo mensual completo",
                "pasos": [
                    "Recopilando drivers (horas GPU, impresiones, tickets)…",
                    "Aplicando mapas de actividad a 214 centros de coste…",
                    "Asignando costes directos e indirectos por producto…",
                    "Validando conservación · suma = total pool…",
                ],
                "resultado": [
                    "USD 46 B asignados · 0 sin asignar (reconciliación OK).",
                    "Reels incrementa consumo infra +4 % mes a mes.",
                    "Modelo listo para publicar en reporting interno.",
                ],
            },
            {
                "label": "Simular cambio de driver clave",
                "icono": "activity",
                "titulo": "Simulación · cambio driver infra (horas GPU → inferencia tokens)",
                "pasos": [
                    "Recalculando reparto por nuevo driver…",
                    "Comparando contra base actual…",
                    "Identificando productos que cambian de posición…",
                ],
                "resultado": [
                    "Reels asume +USD 0,4 B adicional por intensidad de inferencia.",
                    "Messenger reduce -USD 0,2 B al medir mejor su uso real.",
                    "Modelo listo para revisión por el Controller.",
                ],
            },
        ],
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
        "layout": ["picker", "dual_chart", "semaforos", "acciones", "bloques"],
        "picker": {
            "id": "treasury",
            "campos": [
                {"label": "Banco",    "name": "banco", "tipo": "select",
                 "opciones": ["Todos", "JP Morgan", "Bank of America", "Citi", "HSBC", "MUFG"]},
                {"label": "Divisa",   "name": "divisa", "tipo": "select",
                 "opciones": ["USD", "EUR", "GBP", "JPY", "BRL", "INR", "KRW"]},
            ],
            "boton": "Consultar posición",
            "accion": {
                "titulo": "Consultando posición consolidada",
                "pasos": [
                    "Conectando con Kyriba…",
                    "Agregando saldos intradía por banco…",
                    "Convirtiendo a moneda funcional al tipo de cambio actual…",
                    "Validando contra límites por contraparte…",
                ],
                "resultado": [
                    "Saldo consolidado · USD 48,2 B.",
                    "Exposición dentro de los límites por banco (máx. 40 %).",
                    "Sin movimientos pendientes de validación superiores a USD 100 M.",
                ],
            },
        },
        "grafico_sec": {
            "tipo": "line",
            "titulo": "Saldo de caja consolidado (USD B · últimos 90 días)",
            "serie": [41.2, 42.1, 42.8, 43.6, 44.0, 43.9, 44.5, 45.0, 45.4, 45.9,
                      46.4, 46.8, 47.1, 47.5, 47.8, 48.0, 48.2],
        },
        "semaforos": [
            {"label": "Exposición JP Morgan",   "color": "ambar", "valor": "37,5 %", "desc": "Cerca del límite por contraparte (40 %)."},
            {"label": "Exposición Bank of America","color": "verde","valor": "19,5 %", "desc": "Dentro del rango."},
            {"label": "Rating medio ponderado", "color": "verde", "valor": "A+",     "desc": "Umbral mínimo política: A-/A3."},
            {"label": "Rentabilidad caja",      "color": "verde", "valor": "4,8 %",   "desc": "+0,3 pts vs trimestre anterior."},
        ],
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
        "tabla": {
            "titulo": "Instrumentos activos",
            "columnas": ["Instrumento", "Divisa", "Nominal",
                         "Cupón", "Vencimiento", "Covenant"],
            "filas": [
                ["Bono senior 2030",             "USD", "6,0 B", "3,85 %",  "2030-06-15", "ND/EBITDA ≤ 2x"],
                ["Bono senior 2033",             "USD", "5,0 B", "4,55 %",  "2033-11-10", "ND/EBITDA ≤ 2x"],
                ["Bono senior 2035",             "USD", "4,5 B", "4,75 %",  "2035-02-22", "ND/EBITDA ≤ 2x"],
                ["Programa EMTN · tramo A",      "EUR", "1,5 B", "3,65 %",  "2032-05-18", "EBITDA/Int ≥ 4x"],
                ["Programa EMTN · tramo B",      "EUR", "1,0 B", "3,45 %",  "2029-09-30", "EBITDA/Int ≥ 4x"],
                ["Revolving credit facility",    "USD", "10,0 B","SOFR+85", "2028-12-01", "ND/EBITDA ≤ 2x"],
                ["Bono convertible 2028",        "USD", "2,5 B", "0,75 %",  "2028-08-15", "—"],
            ],
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

    "qa-analistas": {
        "titulo": "Q&A de analistas",
        "subtitulo": "Preguntas previsibles y respuestas tipo",
        "vision": "cfo",
        "fuente": "Oracle EPM · Visible Alpha",
        "ultima": "Última actualización · hoy",
        "layout": ["picker", "tabla", "acciones", "grafico", "bloques"],
        "picker": {
            "id": "qa",
            "campos": [
                {"label": "Bloque", "name": "bloque", "tipo": "select",
                 "opciones": ["Todos", "Capex AI", "Monetización WhatsApp",
                              "Reality Labs", "Regulación", "Recompras", "Headcount"]},
                {"label": "Analista", "name": "analista", "tipo": "select",
                 "opciones": ["Todos", "Morgan Stanley", "GS", "JPM", "BofA", "Barclays",
                              "UBS", "Deutsche Bank", "Credit Suisse", "Wells Fargo", "Citi"]},
            ],
            "boton": "Buscar preguntas",
            "accion": {
                "titulo": "Buscando preguntas preparadas",
                "pasos": [
                    "Filtrando por bloque y analista…",
                    "Priorizando por frecuencia histórica…",
                    "Comprobando si existe respuesta tipo aprobada…",
                ],
                "resultado": [
                    "12 preguntas devueltas · 9 con respuesta aprobada.",
                    "2 preguntas sin respuesta — asignadas automáticamente al Head of IR.",
                    "1 pregunta con dato sensible — revisión legal pendiente.",
                ],
            },
        },
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
        "tabla": {
            "titulo": "Preguntas top esperadas · próxima earnings call",
            "columnas": ["Prioridad", "Pregunta", "Bloque",
                         "Respuesta tipo", "Analistas interesados", "Estado"],
            "filas": [
                ["Alta",  "¿Cómo justificáis la aceleración del capex frente al FCF a 2 años?",
                 "Capex AI", "Lista — 2 páginas", "Morgan Stanley, GS, JPM", "Baja"],
                ["Alta",  "¿Momento en que Reality Labs reduce pérdidas de forma material?",
                 "Reality Labs", "En revisión", "BofA, Barclays", "Media"],
                ["Alta",  "¿Pricing de WhatsApp Business en los próximos 12 meses?",
                 "Monetización WhatsApp", "Lista — 1 página", "UBS, DB", "Baja"],
                ["Media", "¿Impacto esperado de DMA/DSA en revenue EMEA?",
                 "Regulación", "Lista — ½ página", "Credit Suisse", "Baja"],
                ["Media", "¿Plan de ejecución del programa de recompra ampliado?",
                 "Recompras", "En revisión", "Wells Fargo", "Media"],
                ["Media", "¿Ritmo de contratación en AI Research?",
                 "Headcount", "Sin respuesta", "Citi", "Alta"],
            ],
        },
        "acciones": [
            {
                "label": "Generar respuesta tipo",
                "icono": "zap",
                "titulo": "Generando respuesta · Pricing WhatsApp Business",
                "pasos": [
                    "Consultando últimos pricings publicados por región…",
                    "Recuperando guidance pasado sobre monetización WhatsApp…",
                    "Alineando con posición corporativa aprobada…",
                    "Dando formato a 150 palabras + puntos de respaldo…",
                ],
                "resultado": [
                    "Respuesta lista en la base documental.",
                    "Validación Legal pendiente (24 h).",
                    "Puntos de respaldo con datos auditados cargados.",
                ],
            },
        ],
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

    "calendario-regulatorio": {
        "titulo": "Calendario regulatorio",
        "subtitulo": "Hitos SEC, UE, estados y mercados",
        "vision": "cfo",
        "fuente": "ServiceNow GRC · Oracle EPM",
        "ultima": "Actualizado · hoy",
        "layout": ["picker", "timeline", "stat_ribbon", "grafico", "acciones", "bloques"],
        "picker": {
            "id": "reg",
            "campos": [
                {"label": "Regulador", "name": "reg", "tipo": "select",
                 "opciones": ["Todos", "SEC", "Comisión Europea", "CNIL", "ICO", "Ofcom", "TRAI (India)"]},
                {"label": "Ventana",   "name": "ventana", "tipo": "select",
                 "opciones": ["Próximos 30 días", "Próximos 90 días", "Resto del FY", "FY completo"]},
            ],
            "boton": "Filtrar hitos",
            "accion": {
                "titulo": "Filtrando calendario regulatorio",
                "pasos": [
                    "Aplicando filtros a ServiceNow GRC…",
                    "Priorizando por obligatoriedad y severidad…",
                    "Cruzando con propietarios y cadencia de reporting…",
                ],
                "resultado": [
                    "12 hitos en los próximos 30 días (5 obligatorios).",
                    "2 hitos marcados como críticos por el Chief Compliance.",
                    "Notificaciones programadas a los responsables correspondientes.",
                ],
            },
        },
        "stat_ribbon": [
            {"label": "Hitos a tiempo",  "valor": "92 %", "desc": "+3 pts vs trimestre", "tono": "pos"},
            {"label": "Obligatorios 30d","valor": "5",    "tono": "warn"},
            {"label": "Externos",        "valor": "7"},
            {"label": "Con sanción",     "valor": "1",    "desc": "CNIL — Francia", "tono": "neg"},
            {"label": "Próximo hito",    "valor": "Hoy",  "desc": "10-Q Q3 2026"},
        ],
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
        "timeline": {
            "titulo": "Próximos hitos regulatorios",
            "eventos": [
                {"cuando": "Hoy", "titulo": "10-Q · Q3 2026", "desc": "Envío a la SEC · firma CFO pendiente.", "estado": "now"},
                {"cuando": "2026-12-05", "titulo": "Reporte CSRD doble materialidad · borrador", "desc": "Revisión del auditor (Big-4)."},
                {"cuando": "2027-01-18", "titulo": "Audiencia CNIL (Francia)", "desc": "Procedimiento formal sobre datos de menores."},
                {"cuando": "2027-02-14", "titulo": "10-K FY2026", "desc": "Auditoría cerrada el 12-02."},
                {"cuando": "2027-03-15", "titulo": "Reporte CSRD definitivo", "desc": "Publicación obligatoria."},
                {"cuando": "2027-04-30", "titulo": "Proxy Statement · Junta Accionistas"},
            ],
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
        "layout": ["stat_ribbon", "checklist", "tabla", "acciones"],
        "stat_ribbon": [
            {"label": "Completadas", "valor": "33", "desc": "69 %", "tono": "pos"},
            {"label": "En curso",    "valor": "9"},
            {"label": "Vencidas",    "valor": "2", "desc": "revisar", "tono": "neg"},
            {"label": "Mi SLA",      "valor": "96 %", "desc": "en objetivo"},
            {"label": "Próxima a vencer","valor": "Hoy 17:00", "desc": "devengos marketing LatAm"},
        ],
        "checklist": {
            "titulo": "Mis tareas de hoy",
            "items": [
                {"texto": "Cargar devengos marketing LatAm (42 OC pendientes)", "hecho": False},
                {"texto": "Revisar conciliación banco JPMC NY",                 "hecho": True},
                {"texto": "Validar asientos automáticos cuenta 47x",            "hecho": True},
                {"texto": "Preparar soporte revisión cuenta 51x (mañana)",     "hecho": False},
                {"texto": "Responder solicitud auditor · inventario RL HW",    "hecho": False},
            ],
        },
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
        "tabla": {
            "titulo": "Tareas pendientes para esta semana",
            "columnas": ["Severidad", "Tarea", "Área",
                         "Vencimiento", "Estado", "Dependencias"],
            "filas": [
                ["Alta",  "Cargar devengos marketing LatAm",     "Devengos",       "Hoy 17:00",     "En curso",     "Facturación AR"],
                ["Alta",  "Conciliación Meta BR ↔ Meta Inc.",    "Conciliaciones", "Mañana 10:00",  "Pendiente",    "Cierre BR"],
                ["Media", "Revisión final cuentas 51x",          "Revisión",       "Mañana 15:00",  "Pendiente",    "—"],
                ["Media", "Devengo bonus anual Q4",              "Devengos",       "Jueves 12:00",  "Pendiente",    "HR data"],
                ["Media", "Ajuste IC royalties IE ↔ Inc.",       "Ajustes IC",     "Jueves 16:00",  "En revisión",  "Legal"],
                ["Baja",  "Revisión provisión litigios",         "Revisión",       "Viernes 10:00", "Pendiente",    "Legal"],
                ["Baja",  "Reconciliación banco JPMC Nueva York","Conciliaciones", "Viernes 14:00", "En curso",     "Statement banco"],
            ],
        },
        "acciones": [
            {
                "label": "Marcar lote como completado",
                "icono": "check",
                "titulo": "Marcando lote · tareas de hoy",
                "pasos": [
                    "Verificando controles automáticos en BlackLine…",
                    "Actualizando estado en ServiceNow…",
                    "Notificando a reviewer asignado…",
                ],
                "resultado": [
                    "3 tareas marcadas como completadas.",
                    "1 tarea requiere revisión del reviewer.",
                    "Progreso general del cierre · 73 % (de 69 %).",
                ],
            },
        ],
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
        "tabla": {
            "titulo": "Items pendientes de revisión (muestra)",
            "columnas": ["Severidad", "Fuente", "Referencia",
                         "Importe", "Posible match", "Confianza"],
            "filas": [
                ["Media", "SAP S/4HANA",  "IC-2026-10-8421",   "USD 1,2 M",  "IC-IE-2026-10-7812",    "88 %"],
                ["Media", "BlackLine",    "AR-NY-918344",      "USD 240 k",  "AR-NY-918344-partial",  "76 %"],
                ["Media", "SAP S/4HANA",  "AP-EMEA-77012",     "USD 180 k",  "AP-EMEA-77012-rev",     "81 %"],
                ["Baja",  "BlackLine",    "PR-APAC-112",       "USD 42 k",   "PR-APAC-112-v2",        "64 %"],
                ["Baja",  "SAP S/4HANA",  "TAX-US-33091",      "USD 64 k",   "— (sin candidato)",      "—"],
            ],
        },
        "acciones": [
            {
                "label": "Lanzar matcheo masivo",
                "icono": "zap",
                "titulo": "Matcheo masivo · 412 items pendientes",
                "pasos": [
                    "Cargando items de la cola…",
                    "Aplicando reglas heurísticas (fecha, importe, referencia)…",
                    "Aplicando patrón aprendido (royalties lag 2 d)…",
                    "Solicitando confirmación en BlackLine…",
                ],
                "resultado": [
                    "398 matcheos automáticos realizados.",
                    "14 items quedan para revisión manual.",
                    "Tiempo medio por item · 98 ms.",
                ],
            },
            {
                "label": "Entrenar con nuevo patrón",
                "icono": "activity",
                "titulo": "Entrenamiento · nuevo patrón de referencia",
                "pasos": [
                    "Cargando últimos 12 meses de conciliaciones manuales…",
                    "Identificando patrón candidato…",
                    "Validando sobre muestra retenida…",
                ],
                "resultado": [
                    "Patrón añadido · 'pagos partners referencias truncadas'.",
                    "Precisión sobre muestra · 94,2 %.",
                    "Despliegue programado para el próximo cierre.",
                ],
            },
        ],
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
        "layout": ["form", "tabla", "acciones", "grafico"],
        "form": {
            "id": "qna",
            "titulo": "Nueva consulta a la base normativa",
            "sub": "La consulta se resuelve sobre la última versión vigente de la norma correspondiente; cada respuesta cita párrafo y enlace.",
            "campos": [
                {"label": "Pregunta", "name": "preg", "tipo": "textarea", "wide": True,
                 "valor": "¿Cómo tratar un hedge FX forward cuando se anticipa la posición cubierta?"},
                {"label": "Marco", "name": "marco", "tipo": "select",
                 "opciones": ["IFRS", "US GAAP", "PGC"], "valor": "IFRS"},
                {"label": "Norma concreta (opcional)", "name": "norma", "tipo": "text",
                 "valor": "IFRS 9"},
                {"label": "Jurisdicción", "name": "pais", "tipo": "select",
                 "opciones": ["Internacional", "EEUU", "Reino Unido", "España", "Irlanda", "Brasil"]},
                {"label": "Ámbito", "name": "ambito", "tipo": "select",
                 "opciones": ["Reconocimiento", "Medición", "Presentación", "Revelación"]},
            ],
            "boton": "Consultar",
            "accion": {
                "titulo": "Consultando base normativa",
                "pasos": [
                    "Buscando párrafos relevantes en el corpus IFRS 9…",
                    "Puntuando coincidencias semánticas…",
                    "Validando versión vigente de la norma…",
                    "Componiendo respuesta con citas…",
                ],
                "resultado": [
                    "Respuesta generada · 3 párrafos citados.",
                    "Enlace al documento original añadido.",
                    "Precisión estimada 94 % en casos similares.",
                ],
            },
        },
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
        "tabla": {
            "titulo": "Consultas recientes · equipo",
            "columnas": ["Cuándo", "Usuario", "Pregunta", "Norma",
                         "Respuesta", "Útil"],
            "filas": [
                ["Hoy 09:14", "A. Pérez (Controller IE)",
                 "¿Cómo registrar un contrato con precio variable y restitución condicional?",
                 "IFRS 15 §§50-59", "Lista", "Sí"],
                ["Hoy 08:42", "L. Oh (Reporting SG)",
                 "Diferencia reconocimiento lease < 12 meses",
                 "IFRS 16 §5", "Lista", "Sí"],
                ["Ayer 17:22", "K. Müller (Tax EMEA)",
                 "Tratamiento Pillar 2 en jurisdicción con top-up tax",
                 "IAS 12 (amendment 2023)", "Lista", "Parcial"],
                ["Ayer 15:18", "R. López (Treasury)",
                 "¿Se puede aplicar hedge accounting a cobertura parcial de posición neta?",
                 "IFRS 9 §§6.5-6.6", "Lista", "Sí"],
                ["Ayer 11:05", "M. Nair (Audit internal)",
                 "Perímetro de consolidación de JV con control conjunto",
                 "IFRS 10 §B35", "Lista", "Sí"],
            ],
        },
        "acciones": [
            {
                "label": "Ejecutar nueva consulta",
                "icono": "search",
                "titulo": "Consulta · 'tratamiento hedge FX forward anticipado'",
                "pasos": [
                    "Buscando párrafos relevantes en el corpus IFRS 9…",
                    "Puntuando coincidencias semánticas…",
                    "Validando versión vigente de la norma…",
                    "Componiendo respuesta con citas…",
                ],
                "resultado": [
                    "Respuesta generada · 3 párrafos citados.",
                    "Enlace a documento original añadido.",
                    "Marcada como útil por el solicitante en 94 % de casos similares.",
                ],
            },
        ],
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
        "subtitulo": "Habla con los manuales de EPM y con la documentación interna",
        "vision": "equipo",
        "fuente": "SharePoint · Alation · Confluence · Manuales Oracle / OneStream / SAP / Workday / Kyriba",
        "ultima": "Última ingesta · ayer 02:00",
        "layout": ["chat", "stat_ribbon", "bloques"],
        "chat": {
            "titulo": "Habla con los manuales",
            "sub": "Prioriza los manuales EPM conectados, la documentación interna del cliente y las políticas publicadas en Alation. Cada respuesta incluye las citas al documento original.",
            "fuentes": [
                "Manuales Oracle EPM Cloud",
                "Manuales OneStream",
                "Manuales SAP Group Reporting",
                "Manuales SAP S/4HANA",
                "Manuales Workday Adaptive",
                "Manuales Kyriba",
                "Base documental cliente (Confluence, SharePoint, Alation)",
            ],
            "sugerencias": [
                "¿Cómo configuro un ajuste top-side en SAP Group Reporting?",
                "¿Qué pasos tengo que seguir para publicar un cube en OneStream?",
                "Dame el procedimiento interno para conciliar una cuenta 51x.",
                "¿Dónde está la política de doble materialidad CSRD?",
                "¿Cómo lanzo un forecast de caja a 13 semanas en Kyriba?",
            ],
            "historia": [
                {"rol": "usuario", "texto": "¿Cómo configuro un ajuste top-side en SAP Group Reporting?"},
                {"rol": "bot",
                 "texto": "Los ajustes top-side en SAP Group Reporting se configuran desde la transacción FINCS-GRP · Journal Entries, seleccionando el periodo y la versión. Debes elegir un tipo de documento con la marca «Top-side only» y asegurarte de que el flag de conservación de perímetro está activo. Luego introduces la pareja débito/crédito y el sistema valida automáticamente con la regla de consolidación.",
                 "citas": [
                     {"fuente": "SAP Group Reporting · User Guide 2026",
                      "seccion": "§4.2 Journal entry types", "pagina": "p. 148"},
                     {"fuente": "Manual interno · cómo registrar ajustes de consolidación",
                      "seccion": "v3.1", "pagina": "p. 12"},
                 ]},
                {"rol": "usuario", "texto": "¿Y si quiero que el ajuste no afecte al reporting estatutario?"},
                {"rol": "bot",
                 "texto": "Para que un ajuste afecte sólo a la vista de gestión y no al reporting estatutario, hay que marcar el documento con un tipo que tenga el perímetro «Management reporting only» y seleccionar el escenario correspondiente antes de grabar. El libro estatutario queda intacto porque SAP no propaga los asientos marcados de gestión. Si lo necesitas para una revisión posterior, también existe la versión «Management - Sim» para pruebas en escenarios.",
                 "citas": [
                     {"fuente": "SAP Group Reporting · Config Guide",
                      "seccion": "§7.1 Management vs Statutory", "pagina": "p. 76"},
                     {"fuente": "Política interna · estatutario vs gestión",
                      "seccion": "v2.4", "pagina": "p. 5"},
                 ]},
            ],
            "accion": {
                "titulo": "Consultando los manuales conectados",
                "pasos": [
                    "Enrutando la pregunta al corpus EPM + documentación interna…",
                    "Recuperando fragmentos relevantes del manual oficial…",
                    "Cruzando con las políticas internas publicadas en Alation…",
                    "Componiendo respuesta con citas y versiones…",
                ],
                "resultado": [
                    "Respuesta elaborada con 3 citas verificables.",
                    "Enlaces a los documentos añadidos a tu workspace.",
                    "Fuentes consultadas: 2 manuales oficiales + 1 política interna.",
                ],
            },
        },
        "stat_ribbon": [
            {"label": "Fuentes conectadas",  "valor": "7"},
            {"label": "Páginas indexadas",   "valor": "128.420"},
            {"label": "Precisión top-1",     "valor": "91 %",  "tono": "pos"},
            {"label": "Consultas / día",     "valor": "840"},
            {"label": "Latencia media",      "valor": "1,8 s"},
            {"label": "Más consultado",      "valor": "Política pagos a terceros"},
        ],
        "bloques": [
            {
                "titulo": "Fuentes más utilizadas esta semana",
                "bullets": [
                    "Manual oficial SAP Group Reporting 2026 · 184 consultas.",
                    "Política interna de doble materialidad CSRD · 128 consultas.",
                    "Manual Oracle EPM Cloud · 96 consultas.",
                    "Procedimiento interno de cierre mensual · 72 consultas.",
                ],
            },
        ],
    },

    "report-builder": {
        "titulo": "Constructor de informes",
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
        "tabla": {
            "titulo": "Plantillas más usadas",
            "columnas": ["Plantilla", "Destinatario", "Última ejecución",
                         "Frecuencia", "Páginas", "Tiempo medio"],
            "filas": [
                ["Informe mensual de cierre",         "Dir. financiera", "Ayer 18:00", "Mensual",     "34", "28 min"],
                ["Dossier Consejo",                   "Consejo",         "01-nov",     "Trimestral",  "48", "1 h 20 min"],
                ["Informe margen por canal",          "Dir. financiera", "Hoy 09:40",  "Semanal",     "12", "9 min"],
                ["Informe operativo regional",        "Operaciones",     "Hoy 08:12",  "Semanal",     "18", "14 min"],
                ["Reporte CSRD (doble materialidad)", "Reguladores",     "02-nov",     "Anual",       "96", "4 h"],
                ["One-pager comercial top anunciantes","Comercial",      "Hoy 10:14",  "Diario",      "2",  "3 min"],
            ],
        },
        "acciones": [
            {
                "label": "Generar informe mensual de cierre",
                "icono": "file",
                "titulo": "Montaje · Informe mensual de cierre · octubre 2026",
                "pasos": [
                    "Cargando datos consolidados desde Oracle EPM…",
                    "Aplicando plantilla Workiva (34 páginas)…",
                    "Importando narrativa reutilizable (bloques certificados)…",
                    "Generando PDF y versión navegable…",
                ],
                "resultado": [
                    "Informe disponible en la base documental.",
                    "32 bloques reutilizados · 2 bloques nuevos añadidos al catálogo.",
                    "Tiempo total · 24 min (vs 28 min media).",
                ],
            },
        ],
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
        "layout": ["semaforos", "stat_ribbon", "tabla", "acciones", "grafico"],
        "semaforos": [
            {"label": "Integridad datos SAP S/4HANA", "color": "verde", "desc": "420/420 controles OK."},
            {"label": "Variaciones materiales",       "color": "ambar", "valor": "2 abiertos", "desc": "Variación coste ventas Meta Brasil."},
            {"label": "Cuentas sin conciliar",        "color": "verde", "desc": "0 cuentas con saldo material pendiente."},
            {"label": "Autorizaciones duales",        "color": "rojo",  "valor": "1 fallo", "desc": "Asiento top-side sin segundo firmante."},
            {"label": "Documentación soporte",        "color": "verde", "desc": "98 % soportes digitalizados."},
            {"label": "Reporting a holding",          "color": "verde", "desc": "Formato y plazos OK."},
        ],
        "stat_ribbon": [
            {"label": "Controles ejecutados", "valor": "1.420"},
            {"label": "OK",                   "valor": "1.392", "desc": "98 %", "tono": "pos"},
            {"label": "Advertencia",          "valor": "22",    "tono": "warn"},
            {"label": "Error bloqueante",     "valor": "6",     "tono": "neg"},
            {"label": "Tiempo medio",         "valor": "11 s / control"},
        ],
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
        "layout": ["picker", "stat_ribbon", "enlaces", "acciones", "bloques"],
        "enlaces": {
            "titulo": "Material formativo recomendado",
            "items": [
                {"tipo": "video", "titulo": "Introducción a Oracle EPM Cloud (FCCS + PBCS)",
                 "duracion": "48 min", "fuente": "Oracle University",
                 "url": "https://education.oracle.com/epm-cloud"},
                {"tipo": "video", "titulo": "OneStream · modelado de un cubo de consolidación",
                 "duracion": "1 h 12", "fuente": "OneStream Academy",
                 "url": "https://academy.onestream.com/consolidation"},
                {"tipo": "video", "titulo": "SAP Group Reporting · nuevos ajustes top-side",
                 "duracion": "36 min", "fuente": "SAP Learning Hub",
                 "url": "https://learning.sap.com/group-reporting"},
                {"tipo": "doc",   "titulo": "Manual interno · cómo subir ficheros planos a Oracle FCCS",
                 "paginas": "22 páginas", "fuente": "Base documental interna",
                 "url": "/docs/manuales/oracle-fccs-ficheros-planos.pdf"},
                {"tipo": "doc",   "titulo": "Guía rápida · publicación de cubes en OneStream",
                 "paginas": "9 páginas", "fuente": "Base documental interna",
                 "url": "/docs/manuales/onestream-publicar-cubes.pdf"},
                {"tipo": "doc",   "titulo": "Plantilla · reporting Narrative Reporting (Oracle)",
                 "paginas": "16 páginas", "fuente": "Base documental interna",
                 "url": "/docs/plantillas/oracle-narrative-reporting.pdf"},
                {"tipo": "video", "titulo": "Workday Adaptive · diseño de drivers financieros",
                 "duracion": "54 min", "fuente": "Workday Learning",
                 "url": "https://learning.workday.com/adaptive-drivers"},
                {"tipo": "doc",   "titulo": "Manual interno · reconciliación banco–SAP S/4HANA",
                 "paginas": "28 páginas", "fuente": "Base documental interna",
                 "url": "/docs/manuales/sap-s4-conciliacion-bancos.pdf"},
                {"tipo": "video", "titulo": "Kyriba · configuración de forecast de caja 13s",
                 "duracion": "41 min", "fuente": "Kyriba Learning",
                 "url": "https://training.kyriba.com/cashforecast"},
            ],
        },
        "picker": {
            "id": "epm",
            "campos": [
                {"label": "Herramienta", "name": "epm", "tipo": "select",
                 "opciones": ["Oracle EPM Cloud", "OneStream", "SAP Group Reporting",
                              "SAP S/4HANA", "Workday Adaptive", "Kyriba"]},
                {"label": "Nivel", "name": "nivel", "tipo": "select",
                 "opciones": ["Introducción", "Intermedio", "Avanzado", "Administrador"]},
                {"label": "Formato", "name": "fmt", "tipo": "select",
                 "opciones": ["Vídeo", "Manual", "Taller presencial"]},
            ],
            "boton": "Buscar formación",
            "accion": {
                "titulo": "Buscando contenido formativo",
                "pasos": [
                    "Interrogando el catálogo interno…",
                    "Aplicando filtros (herramienta, nivel, formato)…",
                    "Puntuando por disponibilidad y calificación interna…",
                ],
                "resultado": [
                    "7 cursos disponibles · 2 marcados como recomendados.",
                    "1 curso agendado para la próxima semana.",
                    "Material teórico sincronizado con la base documental.",
                ],
            },
        },
        "stat_ribbon": [
            {"label": "Cursos disponibles",  "valor": "28"},
            {"label": "Manuales indexados",  "valor": "182"},
            {"label": "Consultas / día",     "valor": "420"},
            {"label": "Formación YTD",       "valor": "6.820 h"},
            {"label": "Mi último curso",     "valor": "Oracle Narrative Reporting"},
        ],
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
        ("plan-estrategico",     "Plan estratégico"),
        ("preparacion-reuniones","Preparación reuniones"),
        ("alertas-proactivas",   "Alertas financieras"),
        ("mapa-riesgos",         "Mapa riesgos financieros"),
        ("guidance-tracker",     "Expectativas al mercado"),
        ("panel-personas",       "Panel de personas"),
    ],
    "cfo": [
        ("cierre-rapido",          "Cuadro cierre rápido"),
        ("prevision-continua",     "Previsión continua"),
        ("prevision-caja-13s",     "Previsión caja 13s"),
        ("covenants",              "Covenants"),
        ("asignacion-capital",     "Asignación capital"),
        ("flujo-cierre",           "Flujo cierre consolidado"),
        ("eliminaciones",          "Eliminaciones"),
        ("estatutario-vs-gestion", "Estatutario vs gestión"),
        ("impacto-fx",             "Impacto FX"),
        ("rentabilidad-dimension", "Rentabilidad por dimensión"),
        ("presupuesto-vs-real",    "Presupuesto vs real"),
        ("prevision-drivers",      "Previsión por drivers"),
        ("cascada-margen",         "Cascada de margen"),
        ("reparto-costes-abc",     "Reparto costes ABC"),
        ("posicion-tesoreria",     "Posición tesorería"),
        ("exposicion-divisa",      "Exposición divisa"),
        ("deuda",                  "Instrumentos de deuda"),
        ("qa-analistas",           "Q&A analistas"),
        ("calendario-regulatorio", "Calendario regulatorio"),
    ],
    "equipo": [
        ("tareas-cierre",           "Mis tareas de cierre"),
        ("conciliacion-inteligente","Conciliación inteligente"),
        ("conciliacion-ic",         "Conciliación intercompany"),
        ("extraccion-documentos",   "Extracción documentos"),
        ("asientos-contables",      "Asientos contables"),
        ("conciliacion-cuentas",    "Conciliación cuentas"),
        ("consulta-normativa",      "Consulta normativa"),
        ("base-documental",         "Base documental"),
        ("report-builder",          "Constructor de informes"),
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


# ---------------------------------------------------------------------------
# Bloques intuitivos para el home.
#
# Agrupan los módulos accesibles en categorías temáticas, con un icono
# ligero (nombre interpretado por index.html) y un pequeño texto de apoyo.
# Las entradas se pintan en el home debajo de los dashboards.
# ---------------------------------------------------------------------------

def _it(slug, titulo, desc):
    return {"slug": slug, "titulo": titulo, "desc": desc}


# Bloques comunes a cualquier entidad activa (no requieren mocks META).
HOME_BLOCKS_BASE = [
    {
        "titulo": "Analítica y lectura ejecutiva",
        "icono":  "bar-chart",
        "color":  "blue",
        "visiones": ["ceo", "cfo", "equipo"],
        "items": [
            _it("/panel-ejecutivo", "Panel ejecutivo",
                "One-pager con los indicadores clave del negocio."),
            _it("/benchmark", "Benchmark sectorial",
                "Compara tus métricas con las de los principales competidores."),
            _it("/analisis", "Informe narrativo",
                "Genera el informe de resultados listo para comunicar."),
            _it("/escenarios", "Simulación de escenarios",
                "Calcula el cierre proyectado con los drivers que elijas."),
        ],
    },
    {
        "titulo": "Relación con el mercado",
        "icono":  "mail",
        "color":  "violet",
        "visiones": ["ceo", "cfo", "equipo"],
        "items": [
            _it("/relacion-inversores", "Relación con Stakeholders",
                "Bandeja de correos y respuestas sugeridas para IR."),
            _it("/noticias", "Noticias del sector",
                "Lectura diaria de prensa relevante para la empresa."),
            _it("/informes-generados", "Informes generados",
                "Histórico de informes Word / PDF descargables."),
        ],
    },
    {
        "titulo": "Habla con tus datos",
        "icono":  "sparkles",
        "color":  "green",
        "visiones": ["ceo", "cfo", "equipo"],
        "items": [
            _it("/habla-con-tus-datos", "Habla con tus datos",
                "Pregunta a tu base de datos en lenguaje natural."),
        ],
    },
]


# Bloques adicionales que sólo existen para la entidad META (mocks).
def _m(slug, titulo, desc):
    return _it("/modulo/" + slug, titulo, desc)


HOME_BLOCKS_META = [
    {
        "titulo": "Dirección general",
        "icono":  "compass",
        "color":  "amber",
        "visiones": ["ceo"],
        "items": [
            _m("plan-estrategico",      "Plan estratégico",
               "Avance de iniciativas por pilar estratégico."),
            _m("preparacion-reuniones", "Preparación de reuniones",
               "Dossier ejecutivo para tus próximas reuniones."),
            _m("alertas-proactivas",    "Alertas financieras",
               "Señales con impacto en P&L, caja o cumplimiento."),
            _m("mapa-riesgos",          "Mapa de riesgos financieros",
               "Matriz de exposición y mitigaciones por categoría."),
            _m("guidance-tracker",      "Expectativas al mercado",
               "Guidance interno vs consenso de analistas."),
            _m("panel-personas",        "Panel de personas",
               "Plantilla, rotación y eNPS por región y función."),
        ],
    },

    {
        "titulo": "Planificación y cierre",
        "icono":  "calendar",
        "color":  "blue",
        "visiones": ["cfo"],
        "items": [
            _m("cierre-rapido",          "Cuadro de cierre rápido",
               "Posición de cierre estimada a D+2."),
            _m("prevision-continua",     "Previsión continua",
               "Rolling forecast a 18 meses actualizado con drivers vivos."),
            _m("prevision-drivers",      "Previsión por drivers",
               "Volumen × precio × mix con elasticidades modeladas."),
            _m("presupuesto-vs-real",    "Presupuesto vs real",
               "Variaciones YTD y explicaciones por responsable."),
            _m("flujo-cierre",           "Flujo de cierre consolidado",
               "Estado y ritmo del cierre mensual del grupo."),
            _m("eliminaciones",          "Eliminaciones",
               "Automatización vs ajuste manual del perímetro."),
            _m("estatutario-vs-gestion", "Estatutario vs gestión",
               "Reconciliación de perímetro y métricas."),
        ],
    },
    {
        "titulo": "Rentabilidad y costes",
        "icono":  "pie",
        "color":  "green",
        "visiones": ["cfo"],
        "items": [
            _m("rentabilidad-dimension", "Rentabilidad por dimensión",
               "Margen por negocio, canal, segmento y cliente."),
            _m("cascada-margen",         "Cascada de margen",
               "De ingresos a margen de contribución."),
            _m("reparto-costes-abc",     "Reparto de costes ABC",
               "Activity-based costing por actividad y producto."),
        ],
    },
    {
        "titulo": "Tesorería y riesgo",
        "icono":  "coins",
        "color":  "violet",
        "visiones": ["cfo"],
        "items": [
            _m("prevision-caja-13s",     "Previsión de caja 13s",
               "Cobros, pagos y liquidez neta semanal."),
            _m("posicion-tesoreria",     "Posición de tesorería",
               "Saldos, cuentas y disponibilidad por banco."),
            _m("exposicion-divisa",      "Exposición en divisa",
               "Posición neta y cobertura vigente."),
            _m("impacto-fx",             "Impacto FX",
               "Efecto de tipo de cambio en resultados."),
            _m("covenants",              "Covenants",
               "Umbrales contractuales y holgura actual."),
            _m("deuda",                  "Instrumentos de deuda",
               "Perfil, vencimientos y rating."),
            _m("asignacion-capital",     "Asignación de capital",
               "Despliegue de capital YTD vs plan."),
        ],
    },
    {
        "titulo": "Relación con el mercado (dirección financiera)",
        "icono":  "mail",
        "color":  "amber",
        "visiones": ["cfo"],
        "items": [
            _m("qa-analistas",           "Q&A de analistas",
               "Preguntas previsibles y respuestas tipo."),
            _m("calendario-regulatorio", "Calendario regulatorio",
               "Hitos SEC, UE, mercados y estados."),
        ],
    },

    {
        "titulo": "Mi operativa del cierre",
        "icono":  "clipboard",
        "color":  "blue",
        "visiones": ["equipo"],
        "items": [
            _m("tareas-cierre",           "Mis tareas de cierre",
               "Checklist operativa del cierre contable."),
            _m("asientos-contables",      "Asientos contables",
               "Propuestas de asiento sugeridas listas para validar."),
            _m("conciliacion-cuentas",    "Conciliación de cuentas",
               "Estado del cierre cuenta a cuenta."),
            _m("conciliacion-inteligente","Conciliación inteligente",
               "Matching asistido por el motor de conciliación."),
            _m("conciliacion-ic",         "Conciliación intercompany",
               "Diferencias abiertas entre entidades del grupo."),
            _m("extraccion-documentos",   "Extracción de documentos",
               "Facturas, contratos y soportes digitalizados."),
            _m("controles-calidad",       "Controles de calidad",
               "Chequeos automáticos antes de cerrar."),
        ],
    },
    {
        "titulo": "Conocimiento y reporting",
        "icono":  "book",
        "color":  "green",
        "visiones": ["equipo"],
        "items": [
            _m("consulta-normativa",      "Consulta normativa",
               "RAG sobre normativa contable y fiscal."),
            _m("base-documental",         "Base documental",
               "Catálogo unificado y buscable."),
            _m("report-builder",          "Constructor de informes",
               "Plantillas y bloques reutilizables."),
            _m("formacion-epm",           "Formación EPM",
               "Cómo trabajar con Oracle, OneStream, SAP y afines."),
        ],
    },
]


def home_blocks_para(empresa_es_meta):
    """Devuelve la lista completa de bloques del home, en orden de lectura."""
    bloques = list(HOME_BLOCKS_BASE)
    if empresa_es_meta:
        bloques = bloques + HOME_BLOCKS_META
    return bloques
