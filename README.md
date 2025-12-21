# Construction Lead Generation AI Agents

AI-powered lead generation system specifically designed for construction companies targeting potential clients within 35 miles of Omaha, Nebraska.

## Overview

This system uses multiple AI agents working together to discover, qualify, and manage construction leads in the Omaha metropolitan area.

## Features

- **Geographic Targeting**: Automatically filters leads within 35-mile radius of Omaha, NE
- **Multi-Agent System**: Coordinated agents for lead discovery, qualification, and enrichment
- **Lead Scoring**: Intelligent scoring based on project size, timeline, and fit
- **Data Enrichment**: Automatically gathers contact information and project details
- **CRM Integration**: Export leads to CSV or integrate with your existing CRM

## Agent Roles

1. **Lead Discovery Agent**: Searches for construction projects and opportunities
2. **Lead Qualifier Agent**: Evaluates and scores leads based on criteria
3. **Data Enrichment Agent**: Gathers additional information about prospects
4. **Lead Manager Agent**: Organizes and exports qualified leads

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Edit `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your_key_here
SERPER_API_KEY=your_key_here  # For Google search
OPENAI_API_KEY=your_key_here  # Optional, for embeddings
```

## Usage

### Basic Usage

```bash
# Run the lead generation system
python main.py

# Run with custom parameters
python main.py --max-leads 50 --output ./leads.csv
```

### Python API

```python
from agents.orchestrator import ConstructionLeadOrchestrator

# Initialize the system
orchestrator = ConstructionLeadOrchestrator(
    target_location="Omaha, NE",
    radius_miles=35
)

# Generate leads
leads = orchestrator.run(max_leads=25)

# Access qualified leads
for lead in leads:
    print(f"Company: {lead['company_name']}")
    print(f"Score: {lead['score']}/100")
    print(f"Project: {lead['project_type']}")
```

## Lead Sources

The system searches multiple sources:
- Building permits and construction permits
- Commercial real estate developments
- Government contract opportunities
- Local business expansions
- Property development projects

## Lead Qualification Criteria

Leads are scored (0-100) based on:
- **Project Size** (30 points): Budget and scope
- **Timeline** (20 points): Project start date and urgency
- **Location** (20 points): Distance from Omaha center
- **Contact Quality** (15 points): Availability of decision-maker info
- **Company Fit** (15 points): Type of construction needed

## Output Format

Leads are exported with the following information:
- Company name and contact information
- Project type and description
- Estimated budget and timeline
- Location and distance from Omaha
- Lead score and qualification notes
- Discovery date and source

## Directory Structure

```
Agents/
├── agents/                 # Agent implementations
│   ├── lead_discovery.py  # Finds potential leads
│   ├── lead_qualifier.py  # Qualifies and scores leads
│   ├── data_enrichment.py # Enriches lead data
│   └── orchestrator.py    # Coordinates all agents
├── tools/                  # Agent tools
│   ├── location_filter.py # Geographic filtering
│   ├── web_search.py      # Web search capabilities
│   └── data_parser.py     # Data extraction
├── models/                 # Data models
│   └── lead.py            # Lead data structure
├── config/                 # Configuration
│   └── settings.py        # System settings
├── output/                 # Generated leads
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Requirements

- Python 3.9+
- Internet connection for API access
- API keys for Claude (Anthropic) and search services

## Support

For issues or questions about this lead generation system, please create an issue in the repository.

## License

MIT License - See LICENSE file for details
