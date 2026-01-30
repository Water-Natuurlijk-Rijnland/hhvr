# Peilbeheer HHVR

Dit project bevat tools en simulaties voor peilbeheer van Hoogheemraadschap van Rijnland.

## 📁 Project Structuur

```
peilbeheer/
├── src/                        # Python modules
│   ├── data_processing/       # Data verwerking en download
│   ├── realtime/              # Realtime data collectie
│   ├── utils/                 # Utility functies
│   └── skills/                # Gespecialiseerde processing
├── web/                        # Vue web applicatie
│   ├── src/                   # Vue componenten en code
│   ├── public/                # Statische assets
│   └── scripts/               # Build scripts
├── data/                       # Data directories (niet in git)
│   ├── kaartlagen/            # GeoJSON kaartlagen
│   ├── realtime/              # Realtime gemaal data
│   ├── cache/                 # Cache bestanden
│   └── temp/                  # Tijdelijke bestanden
├── tests/                      # Test bestanden
├── docs/                       # Documentatie
├── scripts/                    # Utility scripts
├── setup.py                    # Python package configuratie
├── pyproject.toml             # Modern Python project config
└── requirements.txt           # Python dependencies
```

## 🌐 Live Demo

De simulatie applicatie is live beschikbaar op GitHub Pages:  
**https://water-natuurlijk-rijnland.github.io/hhvr/**

## 🚀 Installatie

### Python Package

Installeer het project als een Python package (editable mode voor development):

```bash
# Maak een virtual environment (aanbevolen)
python -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate

# Installeer het package
pip install -e .
```

Nu kun je de modules importeren vanuit je Python scripts:

```python
from src.data_processing import download_layers
from src.realtime import poll_gemaal
from src.utils import pick_random_gemaal
```

### Web Applicatie

```bash
cd web
npm install
```

## 🏃 Lokaal Draaien

### Web Applicatie (Development)

```bash
cd web
npm run dev
```

Open http://localhost:5173/simulatie-peilbeheer/ in je browser.

### Python Scripts

Na installatie van het package kun je de scripts direct uitvoeren:

```bash
# Bijvoorbeeld: download kaartlagen
python -m src.data_processing.download_layers

# Of: poll realtime gemaal data
python -m src.realtime.poll_gemaal
```

## 🔨 Bouwen voor Productie

### Web Applicatie

```bash
cd web
npm run build        # Lokale build
npm run build:github # GitHub Pages build
```

De build output komt in `web/dist/`.

## 📦 Deployment

De web applicatie wordt automatisch gedeployed naar GitHub Pages bij elke push naar de `main` branch via GitHub Actions.

## 🧪 Testing

```bash
# Python tests
pytest tests/

# Web applicatie tests
cd web
npm test
```

## 📝 Modules

### `src/data_processing/`
- **download_layers.py** - Download Rijnland kaartlagen van WFS services
- **fetch_hydronet.py** - Haal data op van Hydronet API
- **sliding_window.py** - Verwerk tijdreeks data met sliding windows

### `src/realtime/`
- **poll_gemaal.py** - Poll realtime gemaal data
- **generate_status.py** - Genereer status rapporten
- **update_dynamic.py** - Update dynamische data

### `src/utils/`
- **pick_random_gemaal.py** - Selecteer willekeurig gemaal voor testing

### `src/skills/`
Gespecialiseerde processing skills en algoritmes.

## ⚠️ Belangrijk

- Grote GeoJSON kaartlagen worden niet in git opgeslagen (zie `.gitignore`)
- Data directories (`data/kaartlagen/`, `data/realtime/`, etc.) zijn lokaal
- De `dist/` folder is build output en wordt niet gecommit
- Gebruik altijd een virtual environment voor Python development

## 🛠️ Development Workflow

1. **Clone het project**
   ```bash
   git clone <repository-url>
   cd peilbeheer
   ```

2. **Setup Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. **Setup web applicatie**
   ```bash
   cd web
   npm install
   ```

4. **Start development**
   ```bash
   # Terminal 1: Web app
   cd web && npm run dev
   
   # Terminal 2: Python scripts
   python -m src.realtime.poll_gemaal
   ```

## 📄 Licentie

Copyright © Hoogheemraadschap van Rijnland
