import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"

# Intenta leer una ruta externa del .env, si no, usa la local
SOURCE_DATA_ENV = os.getenv('SOURCE_DATA_PATH')
SOURCE_DATA_DIR = Path(SOURCE_DATA_ENV) if SOURCE_DATA_ENV else BASE_DIR / "source_data"

# Solo creamos de forma automática las carpetas internas del proyecto
for folder in [LOGS_DIR, EXPORTS_DIR, ASSETS_DIR]:
    folder.mkdir(exist_ok=True)

if not SOURCE_DATA_ENV:
    SOURCE_DATA_DIR.mkdir(exist_ok=True)

COLOR_MUSTARD = '#F5A800'
COLOR_GRAY = '#6F7271'
COLOR_GRAY_LIGHT = '#EAECF0'
COLOR_BLACK = '#000000'
FONT_PRIMARY = 'Arial Black'
FONT_SECONDARY = 'Arial'
LOGO_PATH = ASSETS_DIR / "banco_logo.png"

MAIL_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'user': os.getenv('MAIL_USER'),
    'pass': os.getenv('MAIL_PASS'),
    'business_recipients': [os.getenv('BUSINESS_EMAIL')],
    'support_recipients': [os.getenv('SUPPORT_EMAIL')]
}