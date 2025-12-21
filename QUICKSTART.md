# Quick Start Guide

Get your construction lead generation system up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- An Anthropic API key (get one at https://console.anthropic.com/)
- (Optional) A Serper API key for enhanced web search (get one at https://serper.dev/)

## Installation

### 1. Clone or Download the Repository

If you haven't already, navigate to the project directory:

```bash
cd /path/to/Agents
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional but recommended
SERPER_API_KEY=your_serper_api_key_here
```

## Usage

### Quick Start - Generate 10 Leads

```bash
python main.py --max-leads 10
```

This will:
- Discover construction projects in Omaha, NE (35-mile radius)
- Qualify leads with minimum score of 60/100
- Enrich leads with contact information
- Save results to `./output/construction_leads_[timestamp].csv`

### Common Options

**Generate more leads:**
```bash
python main.py --max-leads 50
```

**Change search radius:**
```bash
python main.py --radius 50
```

**Lower qualification threshold:**
```bash
python main.py --min-score 50
```

**Skip enrichment (faster):**
```bash
python main.py --no-enrich
```

**Export to JSON:**
```bash
python main.py --format json
```

**Verbose logging:**
```bash
python main.py --log-level DEBUG
```

### Full Command Example

```bash
python main.py \
  --max-leads 30 \
  --min-score 65 \
  --radius 40 \
  --format both \
  --log-level INFO
```

## Python API Usage

You can also use the system programmatically:

```python
from agents.orchestrator import ConstructionLeadOrchestrator

# Initialize
orchestrator = ConstructionLeadOrchestrator()

# Generate leads
leads = orchestrator.run(max_leads=25)

# Access results
for lead in leads:
    print(f"{lead.company_name}: {lead.score.total_score}/100")
    print(f"  Project: {lead.project.description}")
    print(f"  Budget: ${lead.project.estimated_budget:,.0f}")
```

## Understanding the Output

Your leads CSV will include:

| Column | Description |
|--------|-------------|
| company_name | Name of the company/organization |
| contact_name | Contact person name |
| contact_email | Email address |
| contact_phone | Phone number |
| project_type | Type of construction project |
| project_description | Details about the project |
| estimated_budget | Project budget estimate |
| location_address | Project address |
| distance_miles | Distance from Omaha center |
| total_score | Lead quality score (0-100) |
| status | Lead status (qualified, new, etc.) |

## Lead Scoring System

Leads are scored on a 100-point scale:

- **Project Size (30 pts)**: Based on budget and square footage
- **Timeline (20 pts)**: Urgency of the project
- **Location (20 pts)**: Proximity to Omaha
- **Contact Quality (15 pts)**: Availability of contact info
- **Company Fit (15 pts)**: Type of project fit

Default minimum score for qualification: **60/100**

## Next Steps

1. **Review your leads** in the CSV file
2. **Sort by score** to prioritize high-quality leads
3. **Filter by distance** to find local projects
4. **Contact leads** using the provided contact information
5. **Track results** to refine your lead criteria

## Troubleshooting

### "No API key found"

Make sure you've created a `.env` file and added your `ANTHROPIC_API_KEY`.

### "No qualified leads found"

Try:
- Lowering the minimum score: `--min-score 50`
- Increasing the search radius: `--radius 50`
- Generating more leads: `--max-leads 50`

### Slow performance

Use `--no-enrich` to skip the enrichment step for faster results.

### Import errors

Make sure you've activated your virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Examples

Check the `examples/` directory for more usage examples:

- `simple_usage.py` - Basic usage example
- `custom_filtering.py` - Filter leads by custom criteria

## Support

For issues or questions:
1. Check this guide first
2. Review the main README.md
3. Check your API keys and environment setup
4. Review the logs in `./logs/lead_generation.log`

## Tips for Best Results

1. **API Keys**: Get a Serper API key for better search results
2. **Run Regularly**: Set up a cron job to run daily/weekly
3. **Customize Scoring**: Modify `agents/lead_qualifier.py` to match your priorities
4. **Save Results**: Keep historical CSV files to track trends
5. **Follow Up**: Contact high-scoring leads promptly

Happy lead hunting! 🏗️
