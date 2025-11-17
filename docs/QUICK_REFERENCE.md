# EngageAI - Quick Reference Guide

## 🚀 Quick Setup Commands

### Developer Setup
```bash
# Clone and setup
git clone <repository-url>
cd marketing
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
playwright install

# Configure
cp .env.template .env
cp config.template.py config.py
nano .env  # Add your OpenAI API key
nano config.py  # Add your business info

# Run
streamlit run app.py
```

### Production Deployment
```bash
# Quick systemd service
sudo nano /etc/systemd/system/marketing-app.service
sudo systemctl daemon-reload
sudo systemctl enable marketing-app
sudo systemctl start marketing-app
```

## 📝 Configuration Quick Edit

### Essential Files to Configure

#### 1. `.env` - API Keys
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini-2024-07-18
```

#### 2. `temp_config.py` - Your Business Info
```python
MY_NAME = "Your Name"
MY_DESIGNATION = "Your Title" 
MY_COMPANY_NAME = "Your Company"
MY_EMAIL = "your@email.com"
MY_PHONE = "+1 (555) 123-4567"
MY_LINKEDIN = "https://linkedin.com/in/yourprofile"

MY_COMPANY_PROFILE = """
We specialize in [YOUR SPECIALIZATION].

With [X] years of experience in [INDUSTRY], our team of [Y]+ expert [PROFESSIONALS] excels in [KEY SERVICES].

Our expertise spans:
- [Service 1] – [Description]
- [Service 2] – [Description]  
- [Service 3] – [Description]

We empower businesses with [YOUR VALUE PROPOSITION].
"""
```

## 🎯 Persona Configuration Locations

### Where to Define Your Business Persona

**Primary Location**: `temp_config.py` (currently used by app)
- Personal information (name, title, contact)
- Company profile and description
- Business value proposition

**Alternative**: `config.py` (backup configuration)
- Same structure as temp_config.py
- Can be used by modifying import in app.py

**Environment**: `.env`
- API keys and sensitive data
- Model preferences
- SMTP settings

## 🔧 Common Configuration Tasks

### Update Your Business Description
1. Edit `temp_config.py`
2. Modify `MY_COMPANY_PROFILE` section
3. Restart the application
4. Test with sample emails

### Change AI Model
1. Edit `.env` file
2. Update `OPENAI_MODEL` value
3. Options: `gpt-4o-mini-2024-07-18`, `gpt-4o`, `gpt-4`
4. Restart application

### Add Email Sending
1. Edit `.env` file
2. Add SMTP configuration:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🚨 Troubleshooting Quick Fixes

### App Won't Start
```bash
# Check API key
grep OPENAI_API_KEY .env

# Reinstall dependencies
pip install -r requirements.txt
playwright install

# Check logs
streamlit run app.py --logger.level debug
```

### Generic Email Output
1. Check `MY_COMPANY_PROFILE` in `temp_config.py`
2. Add more specific industry details
3. Include quantifiable achievements
4. Test with different company profiles

### Permission Issues
```bash
# Fix ownership (Linux)
sudo chown -R $USER:$USER /path/to/marketing
chmod 600 .env
```

## 📊 Testing Your Configuration

### Quick Test Process
1. Start application: `streamlit run app.py`
2. Upload sample CSV with test companies
3. Generate test emails
4. Review output for:
   - Accurate personal information
   - Appropriate company representation
   - Professional tone and style
   - Relevant value proposition

### Sample Test CSV
```csv
Company Name,Company URL,Location
Test Corp,www.testcorp.com,New York
Sample Inc,www.sampleinc.com,San Francisco
Demo LLC,www.demolLC.com,Chicago
```

## 🔄 Regular Maintenance

### Monthly Tasks
- [ ] Review generated email samples
- [ ] Update company achievements/metrics
- [ ] Check API usage and costs
- [ ] Test email delivery (if configured)

### Quarterly Tasks  
- [ ] Update company profile description
- [ ] Review and update contact information
- [ ] Test different persona variations
- [ ] Analyze email performance metrics

### Annual Tasks
- [ ] Comprehensive configuration review
- [ ] Update all business information
- [ ] Security audit (API keys, permissions)
- [ ] Performance optimization review

## 📞 Quick Support

### Check These First
1. **Logs**: Application console output
2. **API Key**: Valid and has credits
3. **Configuration**: All required fields filled
4. **Dependencies**: All packages installed
5. **Permissions**: Proper file access

### Common File Locations
- Configuration: `temp_config.py`
- Environment: `.env`
- Dependencies: `requirements.txt`
- Main app: `app.py`
- Logs: Console output or systemd logs

---

**💡 Pro Tip**: Keep a backup of your working configuration files before making changes!
