# Financial Planning Assistant

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
