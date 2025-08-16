# Financial Analysis Application

This project is a financial analysis application that runs locally, stores data in a local database, and integrates with an AI model for predictions and advice. The application provides users with tools to manage their financial data, analyze their financial situation, and receive AI-generated insights.

## Features

- **Dashboard**: View financial summaries, including total expenses, income, and net worth.
- **Data Entry**: Manually enter financial data such as expenses, liabilities, and assets.
- **Image Upload**: Upload images of financial documents for Optical Character Recognition (OCR) to extract financial data.
- **AI Advisor**: Ask financial questions and receive advice from an integrated AI model based on your financial data.

## Project Structure

```
financial-analysis-app/
├── src/
│   ├── app.py                # Main entry point of the application
│   ├── database/             # Database models and utilities
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── db_utils.py
│   │   └── seed_data.py
│   ├── services/             # Services for AI and OCR
│   │   ├── ai_service.py
│   │   ├── ocr_service.py
│   │   └── financial_analysis.py
│   ├── pages/                # Application pages
│   │   ├── dashboard.py
│   │   ├── data_entry.py
│   │   ├── image_upload.py
│   │   └── ai_advisor.py
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── static/               # Static files (CSS)
│       └── styles.css
├── requirements.txt          # Project dependencies
└── .gitignore                # Files to ignore in version control
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd financial-analysis-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database and seed initial data:
   ```
   python src/app.py
   ```

## Usage

- Run the application:
  ```
  streamlit run src/app.py
  ```

- Open your web browser and navigate to `http://localhost:8501` to access the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.