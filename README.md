# ProjectCompass

An intelligent agent-based system for prioritizing and routing vendor email inquiries using Robocorp automation.

## System Overview

ProjectCompass is an intelligent logistics prioritization and routing system that handles inbound vendor email inquiries related to pre-qualification, finance, contracts, bidding processes, technical issues, and information requests.

The system uses an agent-based architecture to:
1. Analyze incoming emails to understand their content and intent
2. Categorize inquiries into relevant business categories
3. Prioritize inquiries based on urgency, content, and vendor relationship
4. Route inquiries to the appropriate department and personnel
5. Provide notifications and tracking of inquiry status

## Core Components

### Agent-Based System
- **Agent Manager** - Coordinates the specialized agents and overall workflow
- **Analysis Agent** - Uses NLP to categorize and extract key information from emails
- **Prioritization Agent** - Determines the urgency and importance of inquiries
- **Routing Agent** - Assigns inquiries to appropriate departments and personnel
- **Notification Agent** - Sends alerts and updates about inquiry status
- **Monitoring Agent** - Tracks system health and performance metrics

### Services
- **Email Processor** - Handles email parsing and extraction
- **Prioritization Service** - Manages vendor relationship and scoring algorithms
- **Routing Service** - Manages department and personnel workloads and assignments

### Data Components
- **Data Repository** - Stores and retrieves vendor and inquiry information
- **Models** - Defines data structures for vendors and inquiries

### User Interfaces
- **Web Dashboard** - Interactive dashboard for system monitoring and management
- **RESTful API** - Endpoints for external system integration

## Architecture Diagram

```
┌───────────────────┐      ┌───────────────────┐
│   Web Dashboard   │      │   External Email   │
└────────┬──────────┘      └─────────┬─────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────────┐
│                 API Layer                    │
│        (api.py, RESTful Endpoints)           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│            Agent Manager                     │
│        (Coordination & Workflow)             │
└───┬─────┬───────┬─────────┬────────┬────────┘
    │     │       │         │        │
    ▼     ▼       ▼         ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Analysis│ │Prioriti│ │Routing│ │Notific│ │Monitor│
│ Agent  │ │zation  │ │ Agent │ │ation  │ │ing    │
│        │ │ Agent  │ │       │ │ Agent │ │ Agent │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │         │
    └─────────┼─────────┼─────────┼─────────┘
              │         │         │
              ▼         ▼         ▼
┌─────────────────────────────────────────────┐
│            Core Services                     │
│  (Email, Prioritization, Routing Services)   │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│              Data Repository                 │
│      (Vendor & Inquiry Data Storage)         │
└─────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.9+ 
- Virtual environment

### Setup
1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Or install packages directly:
   ```
   pip install robocorp robocorp-tasks rpaframework rpaframework-core rpaframework-email fastapi uvicorn jinja2 pandas scikit-learn nltk spacy pydantic python-dotenv
   ```

4. Download required NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. Download required spaCy model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

### Running the System
To run the main email inquiry processor:
```
python -m tasks email_inquiry_processor
```

To run the web dashboard:
```
python -m tasks run_dashboard
```

To run the API:
```
python api.py
```

### Configuration
The system can be configured using environment variables or a .env file:
- `API_HOST` - Host to bind the API server (default: 127.0.0.1)
- `API_PORT` - Port for the API server (default: 8080)
- `DASHBOARD_HOST` - Host for the dashboard server (default: 127.0.0.1)
- `DASHBOARD_PORT` - Port for the dashboard server (default: 8000)

## Inquiry Categories

The system recognizes and processes the following types of vendor inquiries:

### Pre-qualification
- Application status inquiries
- Document submission questions
- Eligibility criteria questions

### Finance
- Payment status inquiries
- Invoice issues
- Tax documentation questions

### Contract
- Contract terms questions
- Renewal inquiries
- Amendment requests

### Bidding Process
- Bid submission inquiries
- Bid clarification requests
- Bid results inquiries

### Technical Issues
- Portal access problems
- System errors
- Login issues

### Information Requests
- Process information
- Documentation requests
- Contact information requests

## Extending the System

The modular design of ProjectCompass allows for easy extension of its capabilities:

1. Add new inquiry categories and types in `models/inquiry.py`
2. Extend the analysis logic in `agent_system/analysis_agent.py`
3. Add new prioritization rules in `agent_system/prioritization_agent.py`
4. Modify routing logic in `agent_system/routing_agent.py`

## Future Enhancements

- **Advanced NLP with Custom Models**: Train domain-specific models to better understand industry-specific terminology and vendor inquiries
- **Machine Learning Classification**: Implement ML models to improve categorization accuracy based on historical inquiry data
- **Sentiment Analysis**: Integrate sentiment analysis to detect urgent or dissatisfied vendor communications
- **Automated Response Generation**: Create intelligent response templates and suggestion system for faster inquiry resolution
- **Multi-language Support**: Add capabilities to process and respond to inquiries in multiple languages
- **Chatbot Integration**: Develop a vendor-facing chatbot to handle common inquiries automatically
- **Integration with CRM Systems**: Connect with customer relationship management systems for comprehensive vendor history
- **Mobile App**: Create a mobile application for staff to handle inquiries on-the-go
- **Voice Processing**: Add capability to transcribe and process voicemail inquiries
- **Predictive Analytics**: Implement predictive models to anticipate vendor inquiry volumes and resource needs
- **SLA Monitoring & Alerting**: Advanced service level agreement tracking with automated escalations
- **Vendor Portal Integration**: Connect directly with vendor portals to provide self-service information

## License

This project is licensed under the MIT License - see the LICENSE file for details.
