#!/usr/bin/env python3
"""
Financial Planner Setup and Installation Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def create_directory_structure():
    """Create the required directory structure"""
    print("Creating directory structure...")
    
    directories = [
        "src",
        "src/database",
        "src/services", 
        "src/pages",
        "src/components",
        "src/utils",
        "src/static",
        "data",
        "exports",
        "logs",
        "tests",
        "docs",
        "migrations"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/database/__init__.py",
        "src/services/__init__.py",
        "src/pages/__init__.py", 
        "src/components/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"Created: {init_file}")

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Install requirements
    if Path("requirements.txt").exists():
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    else:
        print("requirements.txt not found. Installing basic dependencies...")
        basic_deps = [
            "streamlit>=1.28.0",
            "sqlalchemy>=2.0.0", 
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "plotly>=5.15.0",
            "python-dotenv>=1.0.0"
        ]
        for dep in basic_deps:
            run_command(f"{sys.executable} -m pip install {dep}")

def create_environment_file():
    """Create .env file with default settings"""
    print("Creating environment file...")
    
    env_content = """# Financial Planner Environment Configuration

# Database Configuration
DATABASE_URL=sqlite:///financial_planner.db
DATABASE_ECHO=False

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ENCRYPTION_KEY=your-encryption-key-here

# AI Service Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=10MB

# Feature Flags
ENABLE_AI_ADVISOR=True
ENABLE_OCR=True
ENABLE_EMAIL_REPORTS=False
ENABLE_CLOUD_BACKUP=False

# External API Keys (Optional)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINANCIAL_DATA_API_KEY=your-financial-data-key
"""
    
    if not Path(".env").exists():
        with open(".env", "w") as f:
            f.write(env_content)
        print("Created .env file")
    else:
        print(".env file already exists - skipping")

def create_config_file():
    """Create application configuration file"""
    print("Creating configuration file...")
    
    config_content = '''"""
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
'''
    
    config_path = Path("src/config.py")
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write(config_content)
        print("Created config.py")
    else:
        print("config.py already exists - skipping")

def initialize_database():
    """Initialize the database with tables"""
    print("Initializing database...")
    
    init_script = '''
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.db_utils import init_database

if __name__ == "__main__":
    try:
        init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
'''
    
    # Write and run the database initialization script
    with open("init_db.py", "w") as f:
        f.write(init_script)
    
    result = run_command(f"{sys.executable} init_db.py")
    
    # Clean up the temporary script
    Path("init_db.py").unlink(missing_ok=True)
    
    if result and result.returncode == 0:
        print("Database initialized successfully!")
    else:
        print("Database initialization may have failed - check manually")

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    sample_script = '''
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.db_utils import get_database_session, save_retirement_profile

def create_sample_retirement_profile():
    session = get_database_session()
    
    sample_profile = {
        'current_age': 35,
        'retirement_age': 65,
        'life_expectancy': 85,
        'current_annual_income': 75000,
        'desired_retirement_income_ratio': 0.8,
        'current_savings': 50000,
        'monthly_contribution': 800,
        'employer_match_rate': 0.5,
        'employer_match_limit': 0.06,
        'pre_retirement_return_rate': 0.07,
        'post_retirement_return_rate': 0.05,
        'inflation_rate': 0.03,
        'estimated_social_security': 18000
    }
    
    try:
        profile = save_retirement_profile(session, 'demo_user', sample_profile)
        print("✅ Sample retirement profile created!")
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_retirement_profile()
'''
    
    with open("create_sample.py", "w") as f:
        f.write(sample_script)
    
    run_command(f"{sys.executable} create_sample.py", check=False)
    
    # Clean up
    Path("create_sample.py").unlink(missing_ok=True)

def create_run_script():
    """Create script to run the application"""
    print("Creating run script...")
    
    run_script_content = '''#!/usr/bin/env python3
"""
Financial Planner Application Runner
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment variables
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

def main():
    """Main function to run the Streamlit app"""
    
    # Import and run the app
    import subprocess
    
    app_file = src_path / "app.py"
    
    if not app_file.exists():
        print("❌ app.py not found in src directory")
        sys.exit(1)
    
    try:
        print("🚀 Starting Financial Planner Application...")
        print("📍 Open your browser to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.port=8501",
            "--server.address=localhost"
        ])
        
    except KeyboardInterrupt:
        print("\\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("run.py", "w") as f:
        f.write(run_script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("run.py", 0o755)
    
    print("Created run.py")

def create_readme():
    """Create comprehensive README file"""
    print("Creating README...")
    
    readme_content = '''# Financial Planning Assistant

A comprehensive retirement planning application built with Streamlit that helps users plan their financial future with AI-powered insights.

## Features

### 🏖️ Retirement Planning
- **Comprehensive Analysis**: Calculate retirement corpus needed, savings projections, and success probability
- **Scenario Planning**: Compare conservative, aggressive, and custom retirement scenarios
- **Monte Carlo Simulation**: Statistical analysis of retirement plan success rates
- **Withdrawal Strategies**: Compare 4% rule, dynamic withdrawal, and bond ladder strategies
- **Goal Tracking**: Set and monitor retirement milestones
- **Tax Analysis**: Understand tax implications of different account types

### 🤖 AI-Powered Insights
- **Personalized Recommendations**: Get AI-generated advice based on your financial situation
- **Gap Analysis**: Identify shortfalls and receive specific strategies to address them
- **Risk Assessment**: Understand the risks in your retirement plan
- **Interactive Chat**: Ask specific questions about your retirement strategy

### 📊 Advanced Analytics
- **Sensitivity Analysis**: See how changes in key variables affect your plan
- **Year-by-Year Projections**: Detailed breakdown of savings growth and withdrawals
- **Interactive Charts**: Visualize your retirement journey with dynamic charts
- **Multiple Account Types**: Track 401(k), IRA, Roth accounts, and more

### 📄 Reporting & Export
- **Comprehensive Reports**: Generate detailed retirement planning reports
- **Data Export**: Export projections to CSV and Excel formats
- **Progress Tracking**: Monitor your progress toward retirement goals

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd financial-planner
```

2. **Run the setup script**
```bash
python setup.py
```

3. **Start the application**
```bash
python run.py
```

4. **Open your browser to http://localhost:8501**

### Manual Installation

If you prefer to set up manually:

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database**
```bash
python -c "from src.database.db_utils import init_database; init_database()"
```

4. **Run the application**
```bash
streamlit run src/app.py
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- **Database**: SQLite by default, can use PostgreSQL/MySQL
- **AI Services**: OpenAI/Anthropic API keys for enhanced features
- **Email**: SMTP settings for report delivery
- **Security**: Encryption keys for sensitive data

### Feature Flags

Enable/disable features in `.env`:
- `ENABLE_AI_ADVISOR=True` - AI-powered recommendations
- `ENABLE_OCR=True` - Document processing capabilities
- `ENABLE_EMAIL_REPORTS=True` - Email report delivery

## Usage

### Getting Started

1. **Create Your Profile**: Set up your retirement planning profile with current age, income, and savings
2. **Review Dashboard**: See your retirement readiness score and key metrics
3. **Analyze Projections**: View detailed year-by-year savings projections
4. **Explore Scenarios**: Compare different retirement scenarios
5. **Get Recommendations**: Receive AI-powered advice to improve your plan

### Key Concepts

- **Retirement Corpus**: Total amount needed for retirement
- **Success Rate**: Probability your plan will last through retirement
- **Savings Rate**: Percentage of income saved for retirement
- **Withdrawal Rate**: Annual withdrawal percentage in retirement

### Best Practices

1. **Regular Updates**: Review and update your plan annually
2. **Scenario Planning**: Consider multiple economic scenarios
3. **Diversification**: Use mix of traditional and Roth accounts
4. **Employer Match**: Maximize free employer matching contributions
5. **Professional Advice**: Consult financial advisor for personalized guidance

## Architecture

### Directory Structure
```
financial-planner/
├── src/
│   ├── app.py                 # Main application
│   ├── database/              # Database models and utilities
│   ├── services/              # Business logic and calculations
│   ├── pages/                 # Streamlit page components
│   ├── components/            # Reusable UI components
│   └── utils/                 # Helper functions
├── data/                      # Data storage
├── exports/                   # Generated reports
├── tests/                     # Test files
└── docs/                      # Documentation
```

### Technology Stack

- **Frontend**: Streamlit with Plotly for interactive charts
- **Backend**: Python with SQLAlchemy for database operations
- **Database**: SQLite (default), PostgreSQL/MySQL supported
- **AI Integration**: OpenAI GPT and Anthropic Claude APIs
- **Analytics**: NumPy, Pandas, SciPy for financial calculations

## Advanced Features

### Monte Carlo Simulation

Runs 1000+ scenarios with varying market returns to assess plan robustness:
- Success probability calculation
- Risk assessment and mitigation strategies
- Confidence intervals for projections

### Tax Optimization

Analyzes tax implications:
- Traditional vs Roth account strategies
- Tax-efficient withdrawal sequences
- Current vs future tax rate planning

### Sensitivity Analysis

Shows impact of changing key variables:
- Investment return assumptions
- Inflation rates
- Retirement timeline
- Savings contributions

## API Integration

### Financial Data APIs (Optional)
- **Alpha Vantage**: Market data and economic indicators
- **Yahoo Finance**: Stock and fund information
- **Federal Reserve**: Interest rates and economic data

### AI Services
- **OpenAI**: GPT models for financial advice generation
- **Anthropic**: Claude models for analysis and recommendations

## Security & Privacy

- **Data Encryption**: Sensitive financial data encrypted at rest
- **Local Storage**: Data stored locally by default
- **No Data Sharing**: No financial data shared with third parties
- **Secure APIs**: Encrypted communication with external services

## Troubleshooting

### Common Issues

1. **Database Errors**: Run `python setup.py` to reinitialize
2. **Import Errors**: Ensure all dependencies installed with `pip install -r requirements.txt`
3. **Permission Errors**: Check file permissions and run as appropriate user
4. **Port Conflicts**: Change port in run.py if 8501 is in use

### Support

- Check logs in `logs/app.log`
- Validate configuration in `.env` file
- Ensure Python 3.8+ is installed
- Verify all required dependencies are installed

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This application provides general financial planning guidance and should not be considered as professional financial advice. Always consult with a qualified financial advisor for personalized investment and retirement planning advice.

## Changelog

### Version 1.0.0
- Initial release with comprehensive retirement planning
- AI-powered recommendations and analysis
- Monte Carlo simulation and sensitivity analysis
- Interactive charts and reporting capabilities
'''
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("Created README.md")

def create_gitignore():
    """Create .gitignore file"""
    print("Creating .gitignore...")
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
.venv/
.env/

# Environment Variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# MacOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Data Files
data/uploads/
data/temp/
exports/
backups/

# API Keys and Secrets
secrets/
keys/
credentials/

# Test Coverage
.coverage
htmlcov/
.pytest_cache/

# Jupyter Notebooks
.ipynb_checkpoints/

# Streamlit
.streamlit/

# Temporary Files
tmp/
temp/
*.tmp
'''
    
    if not Path(".gitignore").exists():
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print("Created .gitignore")
    else:
        print(".gitignore already exists - skipping")

def main():
    """Main setup function"""
    print("🚀 Financial Planner Setup Starting...")
    print("=" * 50)
    
    try:
        # Create directory structure
        create_directory_structure()
        
        # Install dependencies
        install_dependencies()
        
        # Create configuration files
        create_environment_file()
        create_config_file()
        create_gitignore()
        
        # Initialize database
        initialize_database()
        
        # Create sample data
        create_sample_data()
        
        # Create run script
        create_run_script()
        
        # Create documentation
        create_readme()
        
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Review and update .env file with your settings")
        print("2. Run 'python run.py' to start the application")
        print("3. Open http://localhost:8501 in your browser")
        print()
        print("For help, see README.md")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()