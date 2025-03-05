# Marketing Email Generator - Deployment Guide

## Prerequisites

1. Python 3.10 or higher
2. pip (Python package installer)
3. OpenAI API key
4. Playwright for web scraping

## System Requirements

- Memory: Minimum 4GB RAM (8GB recommended)
- Storage: At least 1GB free space
- OS: Linux (Ubuntu/Debian recommended) or macOS

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd marketing
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install  # Install browser executables
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Configure Personal Information**
   Update `config.py` with your information:
   ```python
   MY_NAME = "Your Name"
   MY_DESIGNATION = "Your Designation"
   MY_COMPANY_NAME = "Your Company Name"
   MY_LINKEDIN = "Your LinkedIn URL"
   MY_PHONE = "Your Phone Number"
   MY_EMAIL = "Your Email"
   MY_COMPANY_PROFILE = """Your company profile"""
   ```

## Running the Application

1. **Development Mode**
   ```bash
   streamlit run app.py
   ```

2. **Production Deployment**

   ### Using systemd (Recommended for Linux servers)
   
   Create a systemd service file `/etc/systemd/system/marketing-app.service`:
   ```ini
   [Unit]
   Description=Marketing Email Generator
   After=network.target

   [Service]
   User=your_user
   WorkingDirectory=/path/to/marketing
   Environment="PATH=/path/to/marketing/venv/bin"
   Environment="OPENAI_API_KEY=your_openai_api_key"
   ExecStart=/path/to/marketing/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0

   [Install]
   WantedBy=multi-user.target
   ```

   Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start marketing-app
   sudo systemctl enable marketing-app  # Start on boot
   ```

   ### Using Screen (Alternative method)
   ```bash
   screen -S marketing
   source venv/bin/activate
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   # Press Ctrl+A, then D to detach
   ```

## Security Considerations

1. **API Key Protection**
   - Never commit the `.env` file
   - Use environment variables for sensitive data
   - Consider using a secrets manager in production

2. **Server Security**
   - Configure firewall rules (allow only ports 80, 443, and SSH)
   - Use HTTPS in production
   - Keep system and packages updated

3. **Rate Limiting**
   - Monitor OpenAI API usage
   - Implement rate limiting if needed

## Monitoring and Maintenance

1. **Log Files**
   - Application logs are in the application directory
   - System logs: `journalctl -u marketing-app`

2. **Updates**
   ```bash
   # Update dependencies
   pip install -r requirements.txt --upgrade
   
   # Update Playwright
   playwright install --with-deps
   ```

3. **Backup**
   ```bash
   # Backup configuration
   cp config.py config.py.backup
   cp .env .env.backup
   ```

## Troubleshooting

1. **Common Issues**

   - **Playwright Browser Missing**
     ```bash
     playwright install
     ```

   - **OpenAI API Issues**
     - Verify API key in `.env`
     - Check API quota and billing

   - **Permission Issues**
     ```bash
     # Fix directory permissions
     sudo chown -R your_user:your_user /path/to/marketing
     chmod 600 .env
     ```

2. **Checking Status**
   ```bash
   # Check service status
   sudo systemctl status marketing-app
   
   # Check logs
   sudo journalctl -u marketing-app -f
   ```

## Support

For any issues or questions, please:
1. Check the troubleshooting section
2. Review application logs
3. Contact system administrator

## Updating the Application

1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Update Dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```

3. **Restart Service**
   ```bash
   sudo systemctl restart marketing-app
   ```
