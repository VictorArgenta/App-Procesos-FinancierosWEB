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
        "grafico_sec": {
            "tipo": "line",
            "titulo": "Pipeline agregado (EV, USD B, últimos 12 meses)",
            "serie": [6.2, 6.8, 7.1, 7.9, 8.4, 9.0, 9.6, 10.1, 10.5, 10.9, 11.2, 11.4],
        },
        "tabla": {
            "titulo": "Pipeline de oportunidades priorizadas",
            "columnas": ["Target", "Vertical", "Geografía",
                         "EV (USD M)", "Fase", "Fit estratégico"],
            "filas": [
                ["Photonix Compute",     "AI Infra",      "Europa",        "1.200", "Due diligence", "Alto"],
                ["AdPrecision Labs",     "AdTech",        "EEUU",          "420",   "Term sheet",    "Alto"],
                ["XR Perception Inc.",   "Hardware XR",   "Israel",        "780",   "LoI firmada",   "Alto"],
                ["GenMedia Studios",     "Gen AI apps",   "Reino Unido",   "310",   "Screening",     "Medio"],
                ["EdgePay",              "Payments",      "Latinoamérica", "190",   "Screening",     "Medio"],
                ["ShopMetrics",          "Commerce",      "EEUU",          "260",   "Screening",     "Bajo"],
                ["DeepRanker",           "AI Infra",      "Canadá",        "540",   "Due diligence", "Alto"],
            ],
        },
        "acciones": [
            {
                "label": "Lanzar screening automático",
                "icono": "search",
                "titulo": "Screening M&A · ventana últimos 90 días",
                "pasos": [
                    "Consultando PitchBook y CB Insights…",
                    "Filtrando por tesis estratégica (AI Infra, Gen AI, XR)…",
                    "Aplicando criterios de tamaño, geografía y tecnología…",
                    "Scoring por fit estratégico y financiero…",
                ],
                "resultado": [
                    "5 oportunidades nuevas incorporadas al radar.",
                    "2 oportunidades reclasificadas de medio a alto fit.",
                    "Pipeline total · USD 11,9 B (de 11,4 B).",
                ],
            },
            {
                "label": "Simular impacto de adquisición",
                "icono": "calculator",
                "titulo": "Simulación · adquisición Photonix Compute",
                "pasos": [
                    "Modelando sinergias de producto (10 % hit rate conservador)…",
                    "Modelando sinergias de coste (-120 M/año desde año 2)…",
                    "Calculando ROIC esperado a 7 años…",
                    "Evaluando impacto en capex y en el programa de recompra…",
                ],
                "resultado": [
                    "ROIC esperado año 7 · 19,4 % (umbral interno 15 %).",
                    "Impacto FCF año 1 · USD -1,1 B (año 3 · neutro).",
                    "No afecta al rating actual (A1 / A+).",
                ],
            },
        ],
        "bloques": [
            {
                "titulo": "Señales recientes",
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
        ("plan-estrategico",     "Plan estratégico"),
        ("preparacion-reuniones","Preparación reuniones"),
        ("alertas-proactivas",   "Alertas financieras"),
        ("mapa-riesgos",         "Mapa riesgos financieros"),
        ("guidance-tracker",     "Expectativas al mercado"),
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
            _m("ma-radar",              "Radar M&A",
               "Oportunidades, screening y simulación de deals."),
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
            _m("conciliacion-ic",        "Conciliación intercompany",
               "Diferencias abiertas entre entidades del grupo."),
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
