# AI-Powered Cold Email Personalization Tool | Smart Outreach & Engagement

This application enables users to send highly personalized cold emails to potential clients using AI. It streamlines the email drafting process by generating customized content based on real-time data, ensuring better engagement and higher response rates.

## Key Features

- **Custom Email Generation**: The app drafts personalized emails using AI, tailoring content based on the recipient's details.

- **CSV Upload & Website Analysis**: Users can upload a CSV file with target data and provide a website URL. The app retrieves website content in real time to craft relevant emails.

- **Location-Based Personalization**: If the recipient's location is available, the app adds real-time weather information to make the email more engaging.

- **Business & Contact Customization**: Users can input their business details and contact information, which are considered while drafting emails.

- **Single & Bulk Email Generation**: Users can generate a single test email or create emails for all contacts in the list.

- **Download & Edit**: The generated emails can be downloaded as a text file for further customization and editing.

This solution helps businesses enhance their outreach efforts by making cold emails more relevant, engaging, and impactful.

## Technical Stack

- **AI Integration**: OpenAI GPT models for intelligent content generation
- **Web Framework**: Streamlit for interactive UI
- **Web Scraping**: Playwright for real-time website analysis
- **Data Processing**: BeautifulSoup4 for HTML parsing
- **Weather Data**: Integration with weather API for location-based personalization

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Internet connection for real-time data retrieval

## Quick Start

1. **Setup Environment**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd marketing-email-generator

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # or
   .\venv\Scripts\activate  # On Windows

   # Install dependencies
   pip install -r requirements.txt
   playwright install
   ```

2. **Configure Settings**
   ```bash
   # Set up environment variables
   cp .env.template .env
   # Edit .env with your OpenAI API key

   # Configure business information
   cp config.template.py config.py
   # Edit config.py with your business details
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

## Configuration

1. Create `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

2. Update `config.py` with your personal and company information:
- Name and designation
- Company details
- Contact information
- Company profile

## Usage

1. **Initial Setup**
   - Launch the application using `streamlit run app.py`
   - Open the Configuration section to customize your:
     - Name and designation
     - Company details
     - Contact information
     - Company profile and expertise

2. **Prepare Your Data**
   Create a CSV file with these columns:
   ```csv
   Company Name,Company URL,Location
   Acme Corp,www.acme.com,New York
   Tech Solutions,www.techsolutions.com,San Francisco
   ```
   The Location column is optional but enables weather-based personalization.

3. **Generate Emails**
   - Upload your CSV file
   - Choose specific companies or process all at once
   - Click "Generate Emails" to start
   - Preview generated emails in the UI
   - Download as text file for further editing

## CSV Format

Your CSV file should follow this format:
```csv
Company Name,Company URL,Location
Acme Corp,www.acme.com,New York
Tech Solutions,www.techsolutions.com,San Francisco
```

## Development

### Project Structure
```
marketing-email-generator/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration settings
├── cold_email_generator.py # Email generation logic
├── ai_profile_generator.py # AI profile generation
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
└── README.md            # Documentation
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security Notes

- Never commit `.env` file or any API keys
- Keep `config.py` with sensitive information private
- Use environment variables for sensitive data
- Regularly update dependencies

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## License

MIT License

## Support

For issues and feature requests, please create an issue in the repository.
