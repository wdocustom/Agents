# Construction Lead Finder - Simple Usage Guide

**For: Omaha Construction Company Owner**
**Purpose: Find homeowners looking for tile work, remodeling, and construction services**

---

## 📋 What You Have

A complete AI-powered system that:
1. Scrapes Reddit and Craigslist automatically
2. Finds people asking for contractors in Omaha
3. Scores each post on relevance (0-100)
4. Generates personalized responses for you
5. Saves everything to a CSV file you can open in Excel

**Important:** The system does NOT post for you - you review and post manually. This keeps you safe from platform bans!

---

## 🚀 How to Run It (Simple Instructions)

### Step 1: Open Command Prompt (Windows)

1. Click the Windows Start button
2. Type `cmd` and press Enter
3. You'll see a black window (command prompt)

### Step 2: Navigate to Your Folder

```bash
cd C:\Users\camac\OneDrive\Documents\Agents
```

### Step 3: Run the Program

**Option A - Multi-Platform (RECOMMENDED):**
```bash
python main_all_platforms.py
```

This checks Reddit + Craigslist + gives you Nextdoor instructions.

**Option B - Just Reddit:**
```bash
python main_simple.py
```

This only checks Reddit (faster, simpler).

### Step 4: Wait for Results

The program will:
- Show you what it's doing (scraping Reddit, etc.)
- Analyze posts with AI
- Save results to a CSV file

Takes about 1-2 minutes to complete.

### Step 5: Review the Results

1. Look for the output file name in the results:
   ```
   ✓ Saved to: data/opportunities_2025-12-23_143022.csv
   ```

2. Open that CSV file in Excel

3. You'll see columns like:
   - **Title** - What the post is about
   - **Relevance Score** - How good the match is (0-100)
   - **URL** - Link to the post
   - **Suggested Response** - AI-generated response you can use
   - **Keywords** - What they're looking for

### Step 6: Engage with Opportunities

For posts with **score > 70**:

1. **Click the URL** - Opens the Reddit/Craigslist post
2. **Read the full post** - Make sure it's really relevant
3. **Copy the suggested response** - From the CSV file
4. **Customize it** - Add personal touches, specific details
5. **Post your response** - On Reddit or reply to the Craigslist ad
6. **Track it** - Note which ones you responded to

---

## 📅 Daily Routine (Recommended)

### Morning (8:00 AM) - 5 minutes
```bash
cd C:\Users\camac\OneDrive\Documents\Agents
python main_all_platforms.py
```

- Opens the new CSV file
- Reviews opportunities with score > 70
- Posts responses to 2-3 best matches

### Lunch (12:00 PM) - 2 minutes
- Check Nextdoor app for new posts
- Search: "contractor", "tile", "remodel"
- Respond to any new requests

### Evening (5:00 PM) - 2 minutes
- Check Nextdoor again
- Follow up on morning responses

**Total time per day: 10-15 minutes max**

---

## 🎯 What Results to Expect

### Realistic Expectations:

**Good days:**
- Find 5-10 relevant posts
- 2-3 are highly relevant (score > 80)
- You respond to 2-3 opportunities

**Slow days:**
- Find 0-2 relevant posts
- That's normal! Not everyone posts every day
- Keep running daily to catch opportunities

**Best source:**
- **Nextdoor** = Best for local leads (manual check required)
- **Reddit** = Some good leads, worth checking
- **Craigslist** = Hit or miss, occasional gems

### Success Rate:
- Respond to 10 posts → 2-3 will reply back
- Get 5 replies → 1-2 may become quotes
- Get 3 quotes → 1 may become a job

**This is a numbers game - consistency wins!**

---

## 🔧 Adjusting the System

### If you're getting TOO FEW results:

```bash
# Lower the minimum score (shows more posts)
python main_simple.py --min-score 40

# Look back further in time
python main_simple.py --hours-back 72
```

### If you're getting TOO MANY irrelevant results:

Edit the file: `agents/keyword_detector.py`
- Increase the minimum score threshold
- Or just ignore posts below 70 in the CSV

---

## 📁 File Organization

### Important Files:

**Programs you run:**
- `main_all_platforms.py` - Multi-platform scraper (RECOMMENDED)
- `main_simple.py` - Reddit-only scraper

**Output files:**
- `data/opportunities_*.csv` - Your leads (open in Excel)
- `logs/social_monitor.log` - Technical logs (for debugging)

**Configuration:**
- `.env` - Your business info and API key (KEEP SECRET!)

### Backing Up Your Data:

Once a week, copy the `data` folder:
```
C:\Users\camac\OneDrive\Documents\Agents\data
```

Save it somewhere safe so you don't lose past leads.

---

## 🛠️ Common Issues and Fixes

### Issue: "Python is not recognized"

**Fix:**
1. Reinstall Python from python.org
2. During installation, CHECK the box "Add Python to PATH"
3. Restart your computer
4. Try again

### Issue: "No module named 'agents'"

**Fix:**
```bash
# Make sure you're in the right folder
cd C:\Users\camac\OneDrive\Documents\Agents

# Install requirements
pip install -r requirements.txt
```

### Issue: "Anthropic API Error"

**Fix:**
1. Open `.env` file in Notepad
2. Check that `ANTHROPIC_API_KEY=sk-ant-...` has your real API key
3. Go to https://console.anthropic.com/ to verify key is valid
4. Make sure you have credits ($5-10 should last months)

### Issue: "No relevant opportunities found"

**This is NORMAL!** Try:
- Run every day (new posts appear daily)
- Lower the score: `--min-score 40`
- Check Nextdoor manually (best source!)

### Issue: "All results are not in Omaha"

**Fix:** The system now focuses on local subreddits only:
- r/Omaha
- r/Nebraska
- r/lincolnne
- r/councilbluffs

If you're still seeing non-local results, they're likely scored low (<50) and filtered out.

---

## 🎓 Understanding the Output

### Example CSV Row:

| Field | Example | What It Means |
|-------|---------|---------------|
| **platform** | reddit | Where it was found |
| **title** | Looking for tile installer | What they posted |
| **relevance_score** | 85 | AI's rating (0-100) |
| **keywords_matched** | tile, installer, bathroom | What matched |
| **url** | https://reddit.com/... | Link to post |
| **suggested_response** | Hi! I'm a local contractor... | AI-generated reply |
| **created_at** | 2025-12-23 08:15 | When they posted |

### How to prioritize:

1. **Score > 90:** Drop everything, respond NOW
2. **Score 70-89:** Respond within 2-4 hours
3. **Score 50-69:** Review carefully, maybe respond
4. **Score < 50:** Usually filtered out automatically

---

## 📞 Nextdoor - Your Secret Weapon

While Reddit and Craigslist are automated, **Nextdoor is your BEST source** for leads but requires manual checking.

### Why Nextdoor is the Best:

1. **Hyper-local** - Same neighborhood = instant trust
2. **High intent** - People actively looking to hire NOW
3. **Less competition** - Not on Google where everyone looks
4. **Direct messaging** - Can chat with homeowner directly
5. **Reviews matter** - Build reputation in your neighborhood

### How to Use Nextdoor:

**One-time setup (10 minutes):**
1. Go to https://nextdoor.com
2. Create account with your Omaha address
3. Verify your address (postcard or phone)
4. Turn on notifications for "Recommendations" and "Services"

**Daily routine (2 minutes, 3x per day):**
1. Open Nextdoor app or website
2. Click search icon
3. Search for: "contractor" or "tile" or "remodel"
4. Look for posts from today
5. Respond within 1-2 hours (first responder often wins!)

**Response template:**
```
Hi [Name]! I'm a local contractor here in [neighborhood] specializing
in [tile work/remodeling/etc]. I'd be happy to give you a free quote.
You can call/text me at [phone] or check out my work at [website].
I've done several projects right here in the neighborhood!
```

---

## 💰 Cost Breakdown

### What you pay for:

**Anthropic API (Claude AI):**
- Cost per run: $0.02 - $0.10
- Run daily for a month: ~$3-5 total
- Very affordable!

**What's FREE:**
- Reddit scraping
- Craigslist scraping
- All the Python code
- Your time (5-10 min/day)

### ROI Calculation:

If you get **1 job per month** from this system:
- Job value: $500 - $5,000+
- System cost: $5/month
- **ROI: 100x to 1000x**

Even finding one small job pays for the system for years!

---

## 🎯 Success Tips

### 1. Be Fast
People hire the first contractor who responds professionally. Check 2-3 times daily.

### 2. Customize Responses
Don't copy/paste the AI response exactly:
- ❌ Generic: "I can help with that project"
- ✅ Personal: "I just finished a bathroom remodel on Maple St with similar tile work"

### 3. Build Trust
- Mention you're local (same neighborhood/city)
- Reference similar projects you've done
- Include link to your website or photos
- Offer free quote/estimate

### 4. Track Everything
Keep a spreadsheet:
- Date found
- Platform (Reddit/Craigslist/Nextdoor)
- Did you respond?
- Did they reply?
- Did it become a quote?
- Did it become a job?

This helps you see which platforms work best for YOU.

### 5. Focus on Nextdoor
While the automated Reddit/Craigslist scraping is helpful, Nextdoor requires manual checking but has the BEST conversion rate. Don't skip it!

---

## 📈 Scaling Up (Advanced)

### Once you're comfortable:

**Run automatically every morning:**

Windows Scheduled Task:
1. Open Task Scheduler (search in Start menu)
2. Create Basic Task
3. Name: "Lead Finder"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
6. Program: `C:\Users\camac\AppData\Local\Programs\Python\Python311\python.exe`
7. Arguments: `main_all_platforms.py`
8. Start in: `C:\Users\camac\OneDrive\Documents\Agents`

Now it runs automatically every morning, and you just check the CSV file!

---

## ✅ Daily Checklist

Print this out and follow it daily:

**☐ Morning (8 AM):**
- [ ] Run: `python main_all_platforms.py`
- [ ] Open new CSV file in Excel
- [ ] Review posts with score > 70
- [ ] Post 2-3 responses (customize them!)

**☐ Lunch (12 PM):**
- [ ] Check Nextdoor app
- [ ] Search: "contractor", "tile", "remodel"
- [ ] Respond to new posts

**☐ Evening (5 PM):**
- [ ] Check Nextdoor again
- [ ] Follow up on morning responses

**☐ End of week:**
- [ ] Review what worked
- [ ] Track which leads became quotes/jobs
- [ ] Adjust strategy as needed

---

## 🆘 Getting Help

**If something breaks:**

1. Check the logs: `logs/social_monitor.log`
2. Look at the error message
3. Check the Troubleshooting section above
4. Try with debug mode: `--log-level DEBUG`

**Can't figure it out?**
- Review the README.md file
- Check that your .env file is configured correctly
- Make sure all dependencies are installed: `pip install -r requirements.txt`

---

## 🎊 You're Ready!

You now have:
- ✅ Automatic Reddit scraping (no credentials needed!)
- ✅ Automatic Craigslist scraping
- ✅ AI-powered relevance scoring
- ✅ Personalized response generation
- ✅ Instructions for Nextdoor (your best source!)
- ✅ Daily workflow that takes 10-15 minutes

**Next step:** Run it today and find your first lead!

```bash
cd C:\Users\camac\OneDrive\Documents\Agents
python main_all_platforms.py
```

**Good luck! You're going to find great local leads!** 🎯
