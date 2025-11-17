# EngageAI - Business Configuration Guide

## Table of Contents
1. [Overview](#overview)
2. [Initial Setup](#initial-setup)
3. [Personal & Company Information](#personal--company-information)
4. [Business Persona Configuration](#business-persona-configuration)
5. [Email Templates & Tone](#email-templates--tone)
6. [API Configuration](#api-configuration)
7. [Advanced Settings](#advanced-settings)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

EngageAI is an AI-powered cold email personalization tool that helps businesses create highly personalized outreach campaigns. This guide will help you configure the application to match your business needs, persona, and communication style.

### What You Can Configure
- **Personal Information**: Your name, designation, contact details
- **Company Profile**: Business description, services, expertise areas
- **Communication Style**: Tone, approach, and messaging preferences
- **Email Settings**: SMTP configuration for sending emails
- **AI Behavior**: How the AI represents your business

## Initial Setup

### Step 1: Access Configuration Files

The main configuration is stored in two files:
- **`.env`**: Environment variables and API keys
- **`config.py`**: Personal and business information

### Step 2: Basic Environment Setup

Edit the `.env` file with your API credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini-2024-07-18

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@company.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@company.com
TO_EMAILS=recipient1@company.com,recipient2@company.com
```

## Personal & Company Information

### Configuring Your Profile

Edit the `config.py` file to set up your business persona:

```python
# Personal Information
MY_NAME = "John Smith"                    # Your full name
MY_DESIGNATION = "Business Development Manager"  # Your job title
MY_COMPANY_NAME = "TechSolutions Inc."    # Your company name
MY_LINKEDIN = "https://www.linkedin.com/in/johnsmith/"  # Your LinkedIn profile
MY_PHONE = "+1 (555) 123-4567"          # Your contact number
MY_EMAIL = "john.smith@techsolutions.com" # Your business email
```

### Key Guidelines:
- **Name**: Use your professional name as it appears on business cards
- **Designation**: Choose a title that reflects your role in business development/sales
- **Company Name**: Use the official registered business name
- **LinkedIn**: Ensure your LinkedIn profile is professional and up-to-date
- **Phone**: Use a business number with proper formatting
- **Email**: Use your professional business email address

## Business Persona Configuration

### Company Profile Template

The `MY_COMPANY_PROFILE` section is crucial for AI-generated emails. Here's how to structure it:

```python
MY_COMPANY_PROFILE = """
[COMPANY SPECIALIZATION STATEMENT]

With [X] years of experience in [INDUSTRY], our team of [Y]+ expert [PROFESSIONALS] excels in [KEY SERVICES].

Our expertise spans:

[SERVICE 1] – [Detailed description with benefits]
[SERVICE 2] – [Detailed description with benefits]  
[SERVICE 3] – [Detailed description with benefits]
[SERVICE 4] – [Detailed description with benefits]
[SERVICE 5] – [Detailed description with benefits]

We empower businesses with [YOUR VALUE PROPOSITION].
"""
```

### Real-World Examples

#### Example 1: AI/Tech Company
```python
MY_COMPANY_PROFILE = """
We specialize in cutting-edge AI-based solutions, leveraging the latest advancements in Generative AI, Retrieval-Augmented Generation (RAG), fine-tuning, and Large Language Models (LLMs).

With 18 years of experience in software development, our team of 50+ expert developers excels in crafting AI-driven applications tailored for diverse industries.

Our expertise spans:

Generative AI – Custom AI applications powered by LLMs for text, image, and multimodal generation
Retrieval-Augmented Generation (RAG) – Enhanced AI responses through optimized retrieval and knowledge integration
LLM Fine-Tuning & Customization – Adapting models to specific business needs for superior accuracy and performance
Machine Learning & Deep Learning – Developing robust AI systems using state-of-the-art architectures
Reinforcement Learning – AI models capable of adaptive learning and decision-making

We empower businesses with AI-driven automation, intelligent assistants, and cutting-edge machine learning models, delivering high-performance solutions tailored to industry-specific challenges.
"""
```

#### Example 2: Marketing Agency
```python
MY_COMPANY_PROFILE = """
We specialize in data-driven digital marketing strategies that deliver measurable results for B2B and B2C companies.

With 12 years of experience in digital marketing, our team of 25+ expert marketers excels in creating personalized campaigns that drive engagement and conversions.

Our expertise spans:

Performance Marketing – ROI-focused campaigns across Google Ads, Facebook, LinkedIn, and emerging platforms
Content Marketing – SEO-optimized content strategies that build authority and drive organic traffic
Marketing Automation – Sophisticated workflows that nurture leads and maximize customer lifetime value
Social Media Marketing – Engaging campaigns that build communities and drive brand awareness
Analytics & Optimization – Advanced tracking and optimization strategies that improve campaign performance

We empower businesses with data-driven marketing strategies that turn prospects into loyal customers and maximize marketing ROI.
"""
```

#### Example 3: Consulting Firm
```python
MY_COMPANY_PROFILE = """
We specialize in strategic business consulting, helping mid-market companies optimize operations and accelerate growth.

With 15 years of experience in management consulting, our team of 30+ expert consultants excels in delivering actionable strategies that drive sustainable business transformation.

Our expertise spans:

Strategic Planning – Comprehensive business strategy development and execution roadmaps
Operational Excellence – Process optimization and efficiency improvements that reduce costs by 20-40%
Digital Transformation – Technology adoption strategies that modernize business operations
Change Management – Structured approaches to organizational change that ensure successful adoption
Performance Analytics – Data-driven insights that identify growth opportunities and operational bottlenecks

We empower businesses with strategic guidance and practical solutions that deliver measurable improvements in performance and profitability.
"""
```

### Persona Configuration Best Practices

#### 1. Industry-Specific Language
- Use terminology familiar to your target audience
- Include relevant industry buzzwords and concepts
- Mention specific technologies, methodologies, or frameworks

#### 2. Quantifiable Achievements
- Include years of experience
- Mention team size
- Add specific metrics (e.g., "reduce costs by 20-40%")
- Reference client success stories when possible

#### 3. Value Proposition Clarity
- Clearly state what makes you different
- Focus on business outcomes, not just features
- Address common pain points in your industry

#### 4. Professional Tone
- Maintain a confident but not arrogant tone
- Use active voice
- Keep sentences concise and impactful

## Email Templates & Tone

### Customizing Communication Style

The AI uses your company profile to determine the appropriate tone and style. You can influence this by:

#### 1. Tone Indicators in Profile
```python
# Professional and consultative
"We partner with businesses to..."

# Technical and expert-focused  
"We leverage cutting-edge technologies to..."

# Results-oriented and direct
"We deliver measurable improvements in..."

# Relationship-focused and collaborative
"We work closely with teams to..."
```

#### 2. Industry-Specific Approaches

**B2B Technology**:
- Focus on technical capabilities and innovation
- Mention specific technologies and frameworks
- Emphasize scalability and performance

**Professional Services**:
- Highlight expertise and experience
- Focus on strategic outcomes
- Mention industry certifications or partnerships

**Marketing/Creative**:
- Showcase creativity and results
- Include case studies or portfolio highlights
- Focus on brand building and engagement

## API Configuration

### OpenAI Settings

Configure AI behavior through environment variables:

```env
# Model Selection
OPENAI_MODEL=gpt-4o-mini-2024-07-18  # Cost-effective option
# OPENAI_MODEL=gpt-4                  # Higher quality, more expensive

# API Usage Limits (Optional)
OPENAI_MAX_TOKENS=1000               # Limit response length
OPENAI_TEMPERATURE=0.7               # Creativity level (0.0-1.0)
```

### Model Selection Guide

| Model | Best For | Cost | Quality |
|-------|----------|------|---------|
| gpt-4o-mini | High volume, cost-conscious | Low | Good |
| gpt-4o | Balanced performance | Medium | Very Good |
| gpt-4 | Highest quality output | High | Excellent |

## Advanced Settings

### Email Sending Configuration

For direct email sending from the application:

```env
# Gmail Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Use App Password, not regular password

# Outlook/Office 365
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your_email@outlook.com
SMTP_PASSWORD=your_password

# Custom SMTP Server
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USER=your_email@yourdomain.com
SMTP_PASSWORD=your_password
```

### Database Configuration

The application uses SQLite by default. For production use:

```python
# In config.py
DATABASE_NAME = "csv_manager.db"  # Default SQLite
# DATABASE_URL = "postgresql://user:pass@localhost/dbname"  # PostgreSQL option
```

### Crawling & Scraping Settings

```python
# In config.py
MAX_RETRIES = 3      # Number of retry attempts for failed requests
TIMEOUT = 30         # Timeout in seconds for web requests
```

## Best Practices

### 1. Profile Optimization

**Do:**
- Keep descriptions concise but comprehensive
- Use specific, measurable achievements
- Update regularly as your business evolves
- Test different versions to see what works best

**Don't:**
- Use generic, vague descriptions
- Include outdated information
- Make unsubstantiated claims
- Use overly technical jargon for general audiences

### 2. Contact Information

**Do:**
- Use professional email addresses
- Include direct phone numbers
- Keep LinkedIn profiles updated
- Use consistent branding across all touchpoints

**Don't:**
- Use personal email addresses for business
- Include outdated contact information
- Use unprofessional social media profiles

### 3. Testing & Optimization

**Regular Testing:**
- Generate test emails monthly
- Review AI output for accuracy
- Update profiles based on feedback
- Monitor email performance metrics

**A/B Testing:**
- Test different company descriptions
- Try various value propositions
- Experiment with different tones
- Measure response rates

### 4. Compliance & Ethics

**Legal Considerations:**
- Ensure GDPR/CAN-SPAM compliance
- Include proper unsubscribe mechanisms
- Respect recipient preferences
- Maintain accurate contact lists

**Ethical Guidelines:**
- Be honest about your capabilities
- Respect recipient time and attention
- Provide genuine value in communications
- Follow industry best practices

## Troubleshooting

### Common Configuration Issues

#### 1. AI Not Reflecting Your Business Properly
**Problem**: Generated emails don't match your business style
**Solution**: 
- Review and refine your `MY_COMPANY_PROFILE`
- Add more specific industry terminology
- Include concrete examples of your work
- Test with different profile versions

#### 2. Email Tone Issues
**Problem**: Emails are too formal/informal
**Solution**:
- Adjust language in company profile
- Add tone indicators ("We partner with..." vs "We deliver...")
- Review sample outputs and iterate

#### 3. Technical Information Missing
**Problem**: AI doesn't mention specific technologies
**Solution**:
- Add technical details to company profile
- Include specific tools, frameworks, or methodologies
- Mention certifications or partnerships

#### 4. Generic Output
**Problem**: Emails feel generic despite configuration
**Solution**:
- Add more unique value propositions
- Include specific metrics and achievements
- Mention unique methodologies or approaches
- Add industry-specific pain points you solve

### Configuration Validation

Use this checklist to ensure proper setup:

- [ ] All personal information is accurate and professional
- [ ] Company profile reflects current capabilities
- [ ] Contact information is up-to-date
- [ ] LinkedIn profile is professional and current
- [ ] Email configuration is tested and working
- [ ] API keys are valid and have sufficient credits
- [ ] Test emails generate appropriate content
- [ ] Tone and style match your brand

### Getting Help

If you need assistance with configuration:

1. **Review Generated Samples**: Generate test emails to see current output
2. **Check Logs**: Look for error messages in application logs
3. **Validate API Keys**: Ensure OpenAI API key is working
4. **Test Email Settings**: Send test emails to verify SMTP configuration
5. **Contact Support**: Reach out to your technical team or administrator

---

**Remember**: The quality of your AI-generated emails directly depends on the quality and specificity of your configuration. Take time to craft detailed, accurate profiles that truly represent your business value proposition.
