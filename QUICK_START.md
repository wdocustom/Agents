# Quick Start - Construction Lead Finder

## ⚡ Run It Now (3 Steps)

### 1. Open Command Prompt
- Press `Windows + R`
- Type `cmd` and press Enter

### 2. Navigate to folder
```bash
cd C:\Users\camac\OneDrive\Documents\Agents
```

### 3. Run the program
```bash
python main_all_platforms.py
```

---

## 📊 What Happens Next

**You'll see:**
```
======================================================================
  MULTI-PLATFORM CONSTRUCTION LEAD FINDER
  Reddit + Craigslist + Nextdoor
======================================================================

[1/3] Scraping Reddit...
  ✓ Found 41 Reddit posts

[2/3] Scraping Craigslist...
  ✓ Found 8 Craigslist posts

[ANALYSIS] Analyzing 49 total posts...
  ✓ Found 7 relevant opportunities

✓ Saved to: data/opportunities_2025-12-23_143022.csv
```

**Then:**
1. Open the CSV file in Excel
2. Look for rows with **relevance_score > 70**
3. Click the **url** to view the post
4. Copy the **suggested_response** and customize it
5. Post your response manually on the platform

---

## 🎯 Daily Routine (5 minutes)

**Every morning:**
```bash
cd C:\Users\camac\OneDrive\Documents\Agents
python main_all_platforms.py
```

**Then:**
- Open the new CSV file
- Respond to top 2-3 opportunities
- Check Nextdoor app manually (BEST source!)

---

## ⚙️ Configuration (One-Time Setup)

**Edit `.env` file** with your information:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
BUSINESS_NAME=Your Construction Company
BUSINESS_PHONE=(402) 555-1234
BUSINESS_EMAIL=info@yourcompany.com
BUSINESS_WEBSITE=https://yourwebsite.com
SERVICES=tile work, bathroom remodeling, kitchen renovation, flooring
```

---

## 🔧 Common Commands

**Basic run:**
```bash
python main_all_platforms.py
```

**Look back 3 days:**
```bash
python main_simple.py --hours-back 72
```

**Lower the score threshold:**
```bash
python main_simple.py --min-score 40
```

**Debug mode:**
```bash
python main_simple.py --log-level DEBUG
```

---

## 📁 Important Files

**Run these programs:**
- `main_all_platforms.py` ← Multi-platform (RECOMMENDED)
- `main_simple.py` ← Reddit only

**Output files:**
- `data/opportunities_*.csv` ← Your leads (open in Excel)

**Configuration:**
- `.env` ← Your API key and business info

**Help:**
- `README.md` ← Full documentation
- `USAGE_GUIDE.md` ← Beginner step-by-step guide
- `QUICK_START.md` ← This file

---

## 🆘 Troubleshooting

**"Python is not recognized"**
→ Reinstall Python, check "Add to PATH" during installation

**"No module named 'agents'"**
→ Run: `pip install -r requirements.txt`

**"Anthropic API Error"**
→ Check your `.env` file has valid API key

**"No relevant opportunities found"**
→ This is NORMAL! Try running daily, or lower score: `--min-score 40`

---

## ✅ Next Steps

1. **Configure** your `.env` file (one-time)
2. **Run** the program today
3. **Review** results in CSV file
4. **Post** responses to good matches
5. **Set up Nextdoor** account (your best source!)
6. **Run daily** for consistent leads

---

## 💡 Pro Tips

✅ **Respond fast** - First responder often wins
✅ **Customize responses** - Don't copy/paste exactly
✅ **Check Nextdoor** - Best platform for local leads
✅ **Run daily** - New posts appear every day
✅ **Track results** - Note which platforms work best

---

## 📞 Expected Results

**Good days:** 5-10 relevant posts, 2-3 high-quality leads
**Slow days:** 0-2 posts (normal, keep running daily!)
**Best source:** Nextdoor > Reddit > Craigslist

**Success rate:**
- 10 responses → 2-3 replies
- 5 replies → 1-2 quotes
- 3 quotes → 1 job

**This is a numbers game - consistency wins!**

---

**Ready? Run it now!**

```bash
cd C:\Users\camac\OneDrive\Documents\Agents
python main_all_platforms.py
```

🎯 **Happy lead hunting!**
