# Social Media Lead Scraper for Construction Services

AI-powered social media monitoring system that finds potential clients looking for construction, remodeling, and tile work services in Omaha, Nebraska.

## Overview

This system monitors social media platforms (Reddit, Facebook groups, etc.) to find people actively looking for construction services in the Omaha area. It can either notify you of opportunities or automatically engage on your behalf.

## Features

- **Reddit Monitoring**: Scans subreddits for posts about home remodeling, tile work, construction
- **Facebook Group Monitoring**: Monitors local Omaha groups for service requests
- **Intelligent Keyword Detection**: Finds posts where people are asking for contractors
- **Location Filtering**: Only shows opportunities in Omaha/surrounding areas
- **AI-Powered Response Generation**: Creates personalized, natural responses
- **Auto-Engagement** (optional): Can automatically comment on posts
- **Real-time Notifications**: Get alerted when new opportunities are found

## Monitored Platforms

### Reddit
- r/Omaha
- r/HomeImprovement
- r/DIY
- r/Renovations
- r/TileWork
- r/Flooring
- Custom subreddit list

### Facebook
- Omaha Buy/Sell/Trade groups
- Omaha Home Improvement groups
- Local neighborhood groups
- Custom group list

## Target Keywords

The system looks for posts containing:
- "looking for contractor"
- "need tile work"
- "bathroom remodel"
- "kitchen renovation"
- "flooring installation"
- "handyman needed"
- "contractor recommendations"
- And 50+ more variations

## Installation

```bash
# Run setup script
./setup.sh

# Configure your settings
cp .env.example .env
# Edit .env with your credentials and business info
```

## Configuration

Edit `.env` to configure:

```bash
# Your Business Information
BUSINESS_NAME="Your Construction Company"
BUSINESS_PHONE="(402) 555-1234"
BUSINESS_EMAIL="info@yourcompany.com"
BUSINESS_WEBSITE="https://yourcompany.com"
SERVICES="tile work, bathroom remodeling, kitchen renovation, flooring"

# Social Media Credentials (Reddit)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_key

# Target Location
TARGET_CITY=Omaha
TARGET_STATE=NE
TARGET_RADIUS_MILES=35

# Engagement Settings
AUTO_ENGAGE=false  # Set to true to enable automatic commenting
ENGAGEMENT_DELAY_MIN=30  # Minutes between engagements
ENGAGEMENT_DAILY_LIMIT=10  # Max engagements per day
```

## Usage

### Monitor Only (Recommended)

```bash
# Monitor and report opportunities without auto-posting
python main.py --mode monitor
```

This will scan platforms, identify opportunities, and save them to `opportunities.csv` without posting.

### Continuous Monitoring

```bash
# Run continuously (checks every 15 minutes)
python main.py --mode monitor --continuous --interval 15
```

### Platform-Specific Monitoring

```bash
# Reddit only
python main.py --platforms reddit

# Both platforms
python main.py --platforms reddit,facebook
```

## Important Warnings

### ⚠️ Terms of Service Compliance

**AUTO-ENGAGEMENT RISKS:**
- May violate Reddit's automation rules
- May violate Facebook's Terms of Service
- Could result in account suspension or ban
- **Use "monitor-only" mode to stay safe**

**Recommended Approach:**
1. Start with `--mode monitor` (no auto-posting)
2. Manually review opportunities in the CSV output
3. Manually engage to build authentic relationships
4. Only use auto-engage if you fully understand the risks

### Ethical Usage

✅ **DO:**
- Provide genuine, helpful responses
- Only engage on truly relevant posts
- Follow platform community guidelines

❌ **DON'T:**
- Spam irrelevant posts
- Use deceptive practices
- Over-promote your services

## Output Format

Each opportunity found includes:
- Platform (Reddit, Facebook)
- Post title and content
- Author and post URL
- Location information
- Keywords matched
- Relevance score (0-100)
- AI-generated suggested response

## How It Works

1. **Reddit Monitor** scans configured subreddits for new posts
2. **Facebook Monitor** checks groups for relevant posts
3. **Keyword Detector** uses AI to identify relevant posts
4. **Location Filter** verifies posts are about Omaha area
5. **Response Generator** creates personalized replies using Claude AI
6. **Engagement Manager** handles posting (if enabled) with rate limiting
7. **Report System** logs all opportunities for review

## Support & Legal

- This tool finds legitimate business opportunities
- Always follow platform Terms of Service
- Manual engagement is safer than automation
- You are responsible for your account actions

## License

MIT License - Use at your own risk. See LICENSE file.
