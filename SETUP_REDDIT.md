# How to Set Up Reddit API Access

To use the Reddit monitoring features, you need to create a Reddit app and get API credentials.

## Step-by-Step Guide

### 1. Create a Reddit Account

If you don't have one already, create a Reddit account at https://www.reddit.com/register

### 2. Create a Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click "create another app..."
3. Fill out the form:
   - **name**: Give it a name (e.g., "Construction Lead Monitor")
   - **App type**: Select "script"
   - **description**: Optional description
   - **about url**: Leave blank or add your website
   - **redirect uri**: Enter `http://localhost:8080`
4. Click "create app"

### 3. Get Your Credentials

After creating the app, you'll see:
- **client_id**: The string under "personal use script" (14 characters)
- **client_secret**: The "secret" field

### 4. Add to .env File

Edit your `.env` file and add:

```bash
REDDIT_CLIENT_ID=your_14_char_client_id_here
REDDIT_CLIENT_SECRET=your_27_char_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

**Important:**
- Use your actual Reddit username and password
- Keep these credentials secure and never share them
- Don't commit the `.env` file to git (it's already in .gitignore)

### 5. Test the Connection

Run a simple test:

```bash
python -c "from agents.reddit_monitor import RedditMonitor; rm = RedditMonitor(); print('✓ Connected!' if rm.authenticated else '✗ Failed')"
```

## Important Notes

### Rate Limits

Reddit's API has rate limits:
- 60 requests per minute for OAuth apps
- The system respects these limits automatically

### Reddit API Rules

Follow Reddit's API Terms:
- Don't spam or post excessively
- Respect subreddit rules
- Don't use automation to manipulate votes
- Be transparent about being a business/service provider
- Full terms: https://www.reddit.com/wiki/api-terms

### Best Practices

1. **Start with monitoring only** - Don't enable auto-engagement initially
2. **Review opportunities manually** - Check the CSV output and engage manually
3. **Be authentic** - Provide genuine value in your responses
4. **Follow subreddit rules** - Each subreddit has its own rules
5. **Don't oversell** - Be helpful first, promotional second

## Troubleshooting

### "Invalid credentials" error

- Double-check your client_id and client_secret
- Make sure there are no extra spaces in the .env file
- Verify your username and password are correct

### "403 Forbidden" error

- Your app might not be properly configured
- Make sure you selected "script" as the app type
- Try creating a new app

### No results found

- Try different subreddits
- Adjust the time range (--hours-back)
- Lower the minimum score (--min-score)

## Security Tips

1. **Never share your credentials** - Keep .env file private
2. **Use a strong Reddit password** - Preferably unique to this app
3. **Enable 2FA on your Reddit account** - Extra security layer
4. **Rotate credentials periodically** - Create new app if compromised
5. **Monitor your app usage** - Check https://www.reddit.com/prefs/apps regularly

## Next Steps

Once you have Reddit API access set up:

1. Test with monitor-only mode:
   ```bash
   python main.py --mode monitor --platforms reddit
   ```

2. Review the results in `output/opportunities_[timestamp].csv`

3. Manually engage with high-quality opportunities

4. Only enable auto-engage if you understand the risks and have tested thoroughly

## Support

For Reddit API issues:
- Check /r/redditdev for API questions
- Review the PRAW documentation: https://praw.readthedocs.io/
- Reddit API docs: https://www.reddit.com/dev/api

For issues with this tool:
- Check the logs in `logs/lead_generation.log`
- Review the README.md for usage instructions
