import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"

for folder in [LOGS_DIR, EXPORTS_DIR, ASSETS_DIR]:
    folder.mkdir(exist_ok=True)

COLOR_MUSTARD = '#F5A800'
COLOR_GRAY = '#6F7271'
COLOR_GRAY_LIGHT = '#EAECF0'
COLOR_BLACK = '#000000'
FONT_PRIMARY = 'Arial Black'
FONT_SECONDARY = 'Arial'
LOGO_PATH = ASSETS_DIR / "banco_logo.png"

DB_CONFIG = {
    'url': f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    'chunk_size': 5000
}

MAIL_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'user': os.getenv('MAIL_USER'),
    'pass': os.getenv('MAIL_PASS'),
    'business_recipients': [os.getenv('BUSINESS_EMAIL')],
    'support_recipients': [os.getenv('SUPPORT_EMAIL')]
}