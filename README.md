# App-Procesos-FinancierosWEB

Plataforma web de análisis financiero con inteligencia artificial. Obtén datos financieros de empresas cotizadas desde Yahoo Finance y genera informes profesionales con análisis explicativos potenciados por Claude (Anthropic).

## Funcionalidades

### Análisis Individual
- Introduce un ticker bursátil (ej: AAPL, MSFT, GOOGL)
- Visualiza una tabla con métricas financieras: ingresos, coste de ventas, margen bruto, gastos operativos, EBITDA y beneficio neto con sus porcentajes
- Genera una nota de memoria explicativa en español con IA (Claude)
- Descarga el informe completo en formato Word (.docx)

### Comparador de Empresas
- Compara hasta 3 empresas lado a lado
- Tabla comparativa con métricas financieras principales del último periodo
- Análisis comparativo detallado generado por Claude en español
- Descarga del informe comparativo en Word

## Requisitos previos

- Python 3.9 o superior
- API key de [Anthropic](https://console.anthropic.com/)

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/victorargenta/app-procesos-financierosweb.git
cd app-procesos-financierosweb
```

2. Crea y activa un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:

```bash
cp .env.example .env
```

Edita el archivo `.env` y añade tu API key de Anthropic:

```
ANTHROPIC_API_KEY=tu_api_key_aqui
```

5. (Opcional) Reemplaza `static/logo.png` con tu logo corporativo.

## Uso

Ejecuta la aplicación:

```bash
python app.py
```

La aplicación estará disponible en [http://localhost:5000](http://localhost:5000).

## Estructura del proyecto

```
App-Procesos-FinancierosWEB/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Archivos ignorados por git
├── README.md              # Este archivo
├── static/
│   └── logo.png           # Logo de la aplicación
└── templates/
    ├── base.html           # Template base con navegación
    ├── index.html          # Página de inicio
    ├── analisis.html       # Formulario de análisis individual
    ├── resultado.html      # Resultados del análisis
    ├── comparador.html     # Formulario del comparador
    └── comparador_resultado.html  # Resultados de la comparación
```

## Tecnologías

- **Flask** — Framework web
- **yfinance** — Datos financieros de Yahoo Finance
- **Anthropic Claude** — Generación de análisis con IA (claude-sonnet-4-20250514)
- **python-docx** — Generación de documentos Word
- **python-dotenv** — Gestión de variables de entorno
