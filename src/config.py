"""
Application Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///financial_planner.db")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# Application Settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_UPLOAD_SIZE = os.getenv("MAX_UPLOAD_SIZE", "10MB")

# Feature Flags
FEATURE_FLAGS = {
    "ai_advisor": os.getenv("ENABLE_AI_ADVISOR", "True").lower() == "true",
    "ocr_processing": os.getenv("ENABLE_OCR", "True").lower() == "true", 
    "email_reports": os.getenv("ENABLE_EMAIL_REPORTS", "False").lower() == "true",
    "cloud_backup": os.getenv("ENABLE_CLOUD_BACKUP", "False").lower() == "true"
}

# AI Service Configuration
AI_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
    "default_model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7
}

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", ""),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "use_tls": True
}

# File Storage
STORAGE_CONFIG = {
    "upload_folder": BASE_DIR / "data" / "uploads",
    "export_folder": BASE_DIR / "exports", 
    "log_folder": BASE_DIR / "logs",
    "backup_folder": BASE_DIR / "backups"
}

# Ensure storage directories exist
for folder in STORAGE_CONFIG.values():
    folder.mkdir(parents=True, exist_ok=True)

# Retirement Planning Defaults
RETIREMENT_DEFAULTS = {
    "default_return_rate": 0.07,
    "default_inflation_rate": 0.03,
    "default_withdrawal_rate": 0.04,
    "default_life_expectancy": 85,
    "monte_carlo_simulations": 1000
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": STORAGE_CONFIG["log_folder"] / "app.log",
            "formatter": "default"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["file", "console"]
    }
}
