# Construction Lead Finder for Omaha, Nebraska

**AI-Powered Social Media Lead Generation System**

Automatically finds homeowners asking for construction services (tile work, bathroom remodeling, kitchen renovation, flooring) in the Omaha area across multiple platforms.

## ✨ Key Features

- ✅ **NO REDDIT CREDENTIALS NEEDED** - Uses web scraping instead
- ✅ **Multi-Platform Monitoring** - Reddit + Craigslist + Nextdoor instructions
- ✅ **AI-Powered Analysis** - Claude AI scores relevance (0-100)
- ✅ **Automatic Response Generation** - Creates personalized replies
- ✅ **Monitor-Only Mode** - You manually post (safe from ToS violations)
- ✅ **CSV Export** - Review opportunities in Excel

---

## 🚀 Quick Start

### Option 1: Simple Reddit Monitoring (Recommended for beginners)

```bash
python main_simple.py
```

This will:
- Scrape Reddit for construction-related posts in Omaha
- Analyze relevance using AI
- Generate suggested responses
- Export results to CSV

### Option 2: Multi-Platform Monitoring (Best results)

```bash
python main_all_platforms.py
```

This combines:
- ✅ **Reddit** - Automated scraping (no credentials needed!)
- ✅ **Craigslist** - Automated scraping of services wanted
- 📋 **Nextdoor** - Manual monitoring (provides instructions)

---

## 📋 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Business Information

Edit the `.env` file with your details:

```bash
# Required: Anthropic API key for AI analysis
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# Your business information
BUSINESS_NAME=Your Construction Company
BUSINESS_PHONE=(402) 555-1234
BUSINESS_EMAIL=info@yourcompany.com
BUSINESS_WEBSITE=https://www.yourwebsite.com
SERVICES=tile work, bathroom remodeling, kitchen renovation, flooring installation
TARGET_LOCATION=Omaha, Nebraska
SERVICE_RADIUS_MILES=35

# Optional: Adjust thresholds
MIN_LEAD_SCORE=50
MAX_DAILY_ENGAGEMENTS=10
```

**Note:** You only need an Anthropic API key. NO Reddit credentials needed!

---

## 📊 Monitored Platforms

### Reddit (Automated ✅)
- r/Omaha - Local Omaha discussions
- r/Nebraska - State-wide posts
- r/lincolnne - Lincoln area
- r/councilbluffs - Council Bluffs area
- r/HomeImprovement - DIY projects
- r/Renovations - Home renovations
- r/Tile - Tile-specific questions
- r/Flooring - Flooring projects

### Craigslist (Automated ✅)
- Services Wanted - General service requests
- Housing Wanted - Remodeling-related posts

### Nextdoor (Manual 📋)
System provides detailed instructions for manual monitoring. **This is your BEST source for local leads!**

### Target Keywords

The AI automatically detects posts about:
- Contractor recommendations
- Tile work, flooring installation
- Bathroom/kitchen remodeling
- Home renovation projects
- Handyman services
- And 50+ construction-related variations

---

## 💡 How It Works

### 1. **Discovery**
The system scrapes multiple platforms for posts mentioning:
- Contractor recommendations
- Tile work, flooring, remodeling
- Bathroom or kitchen renovations
- Omaha and surrounding areas

### 2. **AI Analysis**
Each post is analyzed by Claude AI to determine:
- **Relevance Score** (0-100): How well it matches your services
- **Keywords Matched**: Which services they mentioned
- **Location**: Whether they're in your service area
- **Project Type**: What kind of work they need

### 3. **Response Generation**
For relevant opportunities, AI generates personalized responses:
- Professional and friendly tone
- Mentions relevant experience
- Includes your contact information
- Customized to the specific post

### 4. **Export Results**
All opportunities are saved to CSV files:
```
data/opportunities_2025-12-23_143022.csv
```

Open in Excel to review, prioritize, and engage!

---

## 🎯 Example Output

```
======================================================================
  MULTI-PLATFORM CONSTRUCTION LEAD FINDER
  Reddit + Craigslist + Nextdoor
======================================================================

[1/3] Scraping Reddit...
  ✓ Found 41 Reddit posts

[2/3] Scraping Craigslist...
  ✓ Found 8 Craigslist posts

[3/3] Nextdoor (manual monitoring)
  ℹ Nextdoor requires manual monitoring

[ANALYSIS] Analyzing 49 total posts...
  ✓ Found 7 relevant opportunities

[RESPONSES] Generating responses...
  ✓ Responses generated

[EXPORT] Saving results...
  ✓ Saved to: data/opportunities_2025-12-23_143022.csv

TOP OPPORTUNITIES:
----------------------------------------------------------------------

1. [REDDIT] Looking for tile installer in Bellevue
   Score: 92/100
   Location: r/Omaha
   Keywords: tile, installer, bathroom

2. [CRAIGSLIST] Need bathroom remodel - Papillion area
   Score: 88/100
   Location: Craigslist Omaha
   Keywords: bathroom, remodel, contractor
```

---

## 🔧 Advanced Options

### Customize Search Parameters

```bash
# Search further back in time
python main_simple.py --hours-back 72

# Lower the relevance threshold
python main_simple.py --min-score 40

# Enable debug logging
python main_simple.py --log-level DEBUG
```

### Run on a Schedule

**Windows:** Create a scheduled task
```bash
schtasks /create /tn "Lead Finder" /tr "C:\path\to\python.exe C:\path\to\main_all_platforms.py" /sc daily /st 08:00
```

**macOS/Linux:** Use cron
```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/Agents && python3 main_all_platforms.py
```

---

## ⚠️ Important: Terms of Service Compliance

### Monitor-Only Mode (Safe ✅)

This system uses **monitor-only mode** by default:
- ✅ Reads public posts (allowed)
- ✅ Saves opportunities to CSV
- ✅ Generates suggested responses
- ❌ Does NOT auto-post (you post manually)

**This keeps you safe from platform violations!**

### Manual Engagement Recommended

1. Review opportunities in the CSV file
2. Click URLs to read full posts
3. Customize the AI-generated response
4. Manually post your response
5. Build authentic relationships

### Platform Guidelines

✅ **DO:**
- Provide genuine, helpful responses
- Only engage on truly relevant posts
- Follow platform community guidelines
- Be professional and courteous

❌ **DON'T:**
- Spam irrelevant posts
- Use deceptive practices
- Auto-post (violates ToS)
- Over-promote your services

---

## ❓ FAQ

### Q: Do I need Reddit credentials?
**A:** No! The system uses web scraping and doesn't require any Reddit account or API keys.

### Q: Will this post automatically?
**A:** No. The system only finds opportunities and suggests responses. YOU manually review and post. This keeps you safe from platform violations.

### Q: How many leads should I expect?
**A:** Varies by day. Sometimes 0-2, sometimes 5-10. Run daily for best results. Not everyone posts every day, but when they do, you'll catch them!

### Q: Why aren't there more Omaha results?
**A:** The Omaha market is smaller. The system focuses on local subreddits (r/Omaha, r/Nebraska) for better targeting.

### Q: Can I add Facebook?
**A:** Facebook is difficult to automate due to their security measures. Manual monitoring of local groups is recommended.

### Q: What about Nextdoor?
**A:** Nextdoor is the BEST platform for local leads but requires manual monitoring. The system provides detailed instructions.

### Q: How much does it cost?
**A:** You only pay for Anthropic API usage. Typical cost: $0.02-$0.10 per run (analyzing 50 posts). Very affordable!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure you installed dependencies
pip install -r requirements.txt
```

### "No relevant opportunities found"
This is normal! Try:
- Run daily (new posts appear every day)
- Lower the score threshold: `--min-score 40`
- Check more hours back: `--hours-back 72`

### "Anthropic API Error"
- Check your `.env` file has valid `ANTHROPIC_API_KEY`
- Verify your API key at https://console.anthropic.com/
- Make sure you have credits available

### "Connection errors"
- Check your internet connection
- Reddit or Craigslist might be temporarily down
- Try again in a few minutes

---

## 📞 Daily Workflow

### Recommended Routine (5-10 minutes per day):

**Morning (8-9 AM):**
```bash
python main_all_platforms.py
```

**Actions:**
1. Open the generated CSV file
2. Look at high-scoring opportunities (>70)
3. Click URLs to view original posts
4. Customize the suggested response
5. Post your response on the platform

**Manual Nextdoor Check (2-3 times per day):**
- Open Nextdoor app/website
- Search for: "contractor", "tile", "remodel"
- Respond within 1-2 hours (people hire fast!)

---

## 🎯 Understanding Relevance Scores

**90-100:** Perfect match - Respond immediately!
**70-89:** Good match - Respond within 24 hours
**50-69:** Potential match - Review carefully
**Below 50:** Filtered out - Not relevant

---

## 📝 License & Disclaimer

**Use Responsibly:**
- Respect platform terms of service
- Don't spam or auto-post
- Be helpful and professional
- Manual engagement only

**No Warranty:**
This tool is provided as-is. Results will vary. Always verify information before engaging.

---

**Built for Omaha contractors** 🎯

*Happy lead hunting!*
