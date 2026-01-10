# Step-by-Step Setup Guide for Senior Email Protection

This guide walks you through setting up email protection for a senior citizen. Choose the approach that best fits your technical comfort level and privacy requirements.

---

## 🎯 Option 1: Quick & Easy Setup (30 minutes)
**Best for:** Most families
**Cost:** $0-20/month
**Privacy:** Good
**Technical Level:** Basic

### Step 1: Enable Gmail Enhanced Safe Browsing

1. Log into the senior's Gmail account
2. Click the **Settings** gear icon (top right)
3. Select **"See all settings"**
4. Go to **"General"** tab
5. Scroll to **"Enhanced Safe Browsing"**
6. Check **"Enable Enhanced Safe Browsing"**
7. Click **"Save Changes"**

**What this does:** Uses Google's AI to detect 38% more spam with 19% fewer false positives.

### Step 2: Create Custom Gmail Filters

#### Filter 1: Flag Urgent/Suspicious Keywords

1. In Gmail settings, go to **"Filters and Blocked Addresses"**
2. Click **"Create a new filter"**
3. In **"Has the words"** field, enter:
   ```
   urgent OR suspended OR verify OR "act now" OR "limited time" OR "account locked" OR "confirm immediately"
   ```
4. Click **"Create filter"**
5. Check:
   - ✅ **"Apply label"** → Create new label: **"⚠️ REVIEW NEEDED"**
   - ✅ **"Forward it to"** → Your email address (the child's email)
6. Click **"Create filter"**

#### Filter 2: Flag Money Requests

1. Create another filter
2. **"Has the words":**
   ```
   "gift card" OR "wire transfer" OR "send money" OR "payment required" OR winner OR prize OR inheritance
   ```
3. Check:
   - ✅ **"Apply label"** → **"⚠️ POTENTIAL SCAM"**
   - ✅ **"Forward it to"** → Your email
   - ✅ **"Star it"**
4. Click **"Create filter"**

#### Filter 3: Auto-Archive Obvious Spam

1. Create another filter
2. **"Has the words":**
   ```
   "enlarge" OR "pharmacy" OR "weight loss" OR "casino" OR "viagra"
   ```
3. Check:
   - ✅ **"Skip Inbox (Archive it)"**
   - ✅ **"Mark as read"**
4. Click **"Create filter"**

### Step 3: Set Up Jortty (Optional but Recommended)

1. Go to [jortty.com](https://www.jortty.com)
2. Sign up for free account (or $19.99/month for unlimited)
3. Get your Jortty forwarding address (e.g., `analyze-xyz@jortty.com`)
4. Add to Gmail filter from Step 2:
   - Also forward "⚠️ REVIEW NEEDED" emails to Jortty
5. Jortty will analyze and send results to your (child's) email

### Step 4: Educate the Senior

**Create a simple guide for them:**

```
📧 EMAIL SAFETY CHECKLIST

Before responding to ANY email asking for information or money:

✅ DO:
- Hover over links to see the REAL destination (don't click!)
- Check the sender's email address carefully
- Call the company directly using a number YOU look up (not from the email)
- Ask me (your child) if you're unsure

❌ DON'T:
- Click links in unexpected emails
- Give personal information (SSN, passwords, account numbers)
- Send money via gift cards or wire transfers
- Feel pressured to act "immediately"

🚨 RED FLAGS:
- "Urgent" or "Act now" language
- Requests for gift cards
- Claims your account is "suspended"
- Emails from government agencies (they mail letters, not emails)
- Too-good-to-be-true offers

WHEN IN DOUBT → Forward to me or delete it!
```

**Print this and put it near their computer.**

---

## 🔒 Option 2: Privacy-First Local Setup (2-3 hours)
**Best for:** Privacy-conscious families
**Cost:** $0
**Privacy:** Maximum (nothing sent externally)
**Technical Level:** Intermediate

### Prerequisites

- Python 3.8+ installed
- Senior's email uses IMAP (Gmail, Outlook, most email providers)
- Always-on computer or Raspberry Pi

### Step 1: Install Dependencies

```bash
# Create project directory
mkdir ~/senior-email-protection
cd ~/senior-email-protection

# Download the local ML script
# (Copy local-ml-alternative.py from this repo)

# Install Python dependencies
pip install transformers torch scikit-learn email-validator
```

### Step 2: Create IMAP Monitor Script

Create `monitor_email.py`:

```python
#!/usr/bin/env python3
"""
Monitor senior's email inbox and auto-filter spam locally
"""
import imaplib
import email
import time
import subprocess
import json
from datetime import datetime

# Configuration
IMAP_SERVER = "imap.gmail.com"  # Change for other providers
EMAIL_ACCOUNT = "senior@example.com"
EMAIL_PASSWORD = "app-password-here"  # Use app-specific password
CHECK_INTERVAL = 60  # seconds
SPAM_FOLDER = "Spam_Auto"  # Will be created if doesn't exist

def connect_imap():
    """Connect to IMAP server"""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    return mail

def analyze_email_locally(subject, body, sender):
    """Call local ML script to analyze email"""
    result = subprocess.run(
        [
            'python', 'local-ml-alternative.py',
            '--subject', subject,
            '--body', body,
            '--sender', sender
        ],
        capture_output=True,
        text=True
    )

    # Parse JSON output
    try:
        analysis = json.loads(result.stdout)
        return analysis
    except:
        return None

def move_to_spam(mail, email_id):
    """Move email to spam folder"""
    # Create spam folder if doesn't exist
    try:
        mail.create(SPAM_FOLDER)
    except:
        pass

    # Move email
    mail.copy(email_id, SPAM_FOLDER)
    mail.store(email_id, '+FLAGS', '\\Deleted')
    mail.expunge()

def monitor_inbox():
    """Main monitoring loop"""
    print(f"Starting email monitor for {EMAIL_ACCOUNT}")
    print(f"Checking every {CHECK_INTERVAL} seconds...")

    while True:
        try:
            mail = connect_imap()
            mail.select('INBOX')

            # Search for unseen emails
            _, message_ids = mail.search(None, 'UNSEEN')

            for msg_id in message_ids[0].split():
                # Fetch email
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)

                # Extract details
                subject = message['subject'] or ""
                sender = message['from'] or ""
                body = ""

                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = message.get_payload(decode=True).decode()

                # Analyze locally
                print(f"\n[{datetime.now()}] Analyzing: {subject}")
                analysis = analyze_email_locally(subject, body, sender)

                if analysis and analysis.get('recommended_action') in ['delete', 'move_to_spam']:
                    print(f"  ⚠️  SPAM DETECTED (confidence: {analysis.get('confidence')})")
                    print(f"  📁 Moving to {SPAM_FOLDER}")
                    move_to_spam(mail, msg_id)

                    # Log for review
                    with open('spam_log.txt', 'a') as f:
                        f.write(f"\n{datetime.now()}\n")
                        f.write(f"From: {sender}\n")
                        f.write(f"Subject: {subject}\n")
                        f.write(f"Risk: {analysis.get('risk_level')}\n")
                        f.write(f"Reason: {analysis.get('explanation_for_senior')}\n")
                        f.write("-" * 50 + "\n")
                else:
                    print(f"  ✅ Email appears safe")

            mail.close()
            mail.logout()

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_inbox()
```

### Step 3: Set Up Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Generate app password for "Mail"
3. Copy the 16-character password
4. Add to `monitor_email.py` configuration

### Step 4: Run as Background Service

**On Linux/Mac (systemd service):**

Create `/etc/systemd/system/senior-email-monitor.service`:

```ini
[Unit]
Description=Senior Email Protection Monitor
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/senior-email-protection
ExecStart=/usr/bin/python3 monitor_email.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable senior-email-monitor
sudo systemctl start senior-email-monitor
sudo systemctl status senior-email-monitor
```

**On Raspberry Pi:**
Same as above, perfect use case for always-on monitoring.

**On Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program → `python monitor_email.py`
5. Conditions: Start only if on AC power (laptops)

### Step 5: Set Up Weekly Reports

Create `generate_report.sh`:

```bash
#!/bin/bash
# Generate weekly spam report

REPORT_FILE="weekly_report_$(date +%Y%m%d).txt"

echo "Weekly Spam Protection Report" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Count spam caught this week
SPAM_COUNT=$(grep -c "$(date +%Y-%m)" spam_log.txt)
echo "Spam emails blocked: $SPAM_COUNT" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "Recent blocked emails:" >> $REPORT_FILE
tail -n 50 spam_log.txt >> $REPORT_FILE

# Email to yourself
mail -s "Senior Email Protection - Weekly Report" your@email.com < $REPORT_FILE
```

Add to crontab (runs every Monday at 9am):
```bash
crontab -e
0 9 * * 1 /path/to/generate_report.sh
```

---

## 🔬 Option 3: Advanced Hybrid Setup (1-2 days)
**Best for:** Tech enthusiasts who want the best of both worlds
**Cost:** $5-20/month (Claude API for edge cases)
**Privacy:** Good (most processing local, edge cases to Claude)
**Technical Level:** Advanced

### Architecture

```
Gmail IMAP
    ↓
Local ML (free, fast, private)
    ↓
Confidence > 80%? → Auto-filter
    ↓
Confidence 40-80%? → Send to Claude Code for nuanced analysis
    ↓
Claude provides detailed explanation + final decision
    ↓
Auto-filter + send explanation to child for review
```

### Step 1: Follow Option 2 setup

Complete the privacy-first local setup first.

### Step 2: Add Claude Code integration

Modify `monitor_email.py` to add Claude Code fallback:

```python
def analyze_with_claude(subject, body, sender):
    """Use Claude Code for edge cases requiring nuanced analysis"""
    result = subprocess.run(
        [
            './example-claude-integration.sh',
            subject,
            body,
            sender
        ],
        capture_output=True,
        text=True
    )

    # Parse results from spam-analysis-results/
    # Return enhanced analysis with explanations
    return json.loads(result.stdout)

def analyze_email_hybrid(subject, body, sender):
    """Hybrid: local ML first, Claude for edge cases"""

    # First pass: local ML (free, fast, private)
    local_result = analyze_email_locally(subject, body, sender)
    confidence = local_result.get('confidence', 0)

    # High confidence? Trust local ML
    if confidence > 0.8 or confidence < 0.3:
        return local_result

    # Edge case (40-80% confidence)? Use Claude for nuanced analysis
    print(f"  🤔 Edge case detected (confidence: {confidence})")
    print(f"  🔍 Requesting Claude Code analysis...")

    claude_result = analyze_with_claude(subject, body, sender)

    # Claude provides better explanation for seniors
    return claude_result
```

### Step 3: Set up cost controls

In `monitor_email.py`, add limits:

```python
# Configuration
MAX_CLAUDE_CALLS_PER_DAY = 10  # Limit API costs
CLAUDE_CALLS_TODAY = 0
LAST_RESET = datetime.now().date()

def should_use_claude():
    """Check if we should use Claude (cost control)"""
    global CLAUDE_CALLS_TODAY, LAST_RESET

    # Reset counter daily
    if datetime.now().date() > LAST_RESET:
        CLAUDE_CALLS_TODAY = 0
        LAST_RESET = datetime.now().date()

    return CLAUDE_CALLS_TODAY < MAX_CLAUDE_CALLS_PER_DAY
```

### Step 4: Set up monitoring dashboard (optional)

Use Grafana or simple web dashboard to track:
- Emails processed
- Spam blocked
- Claude API calls made
- Cost tracking
- False positive rate (from manual reviews)

---

## 📊 Testing Your Setup

### Test with Real Spam Examples

Create `test_detection.sh`:

```bash
#!/bin/bash
# Test spam detection with known scam patterns

echo "Testing spam detection..."

# Test 1: Social Security Scam
python local-ml-alternative.py \
  --subject "URGENT: Your Social Security Benefits Suspended" \
  --body "Your SSA account has been suspended due to suspicious activity. Click here immediately to verify your identity and restore benefits. Provide your SSN and date of birth." \
  --sender "noreply@ssa-verify.xyz"

echo "\nExpected: HIGH risk, SPAM detected\n"

# Test 2: Legitimate Email
python local-ml-alternative.py \
  --subject "Your Amazon Order #123-456" \
  --body "Your order has shipped and will arrive on Tuesday. Track your package using the link in your Amazon account." \
  --sender "ship-confirm@amazon.com"

echo "\nExpected: LOW risk, SAFE\n"

# Test 3: Edge Case
python local-ml-alternative.py \
  --subject "Security Alert: New Sign-In" \
  --body "We noticed a new sign-in to your account from Chicago, IL. If this wasn't you, please review your account security settings." \
  --sender "no-reply@accounts.google.com"

echo "\nExpected: MEDIUM risk, needs review\n"
```

Run tests:
```bash
chmod +x test_detection.sh
./test_detection.sh
```

### Measure False Positives

After 1 week, review the `spam_log.txt`:

1. Check how many emails were blocked
2. Review if any were legitimate (false positives)
3. Adjust thresholds in `local-ml-alternative.py` if needed

Target: <5% false positive rate

---

## 🛡️ Ongoing Maintenance

### Weekly Tasks (5 minutes)
- [ ] Review spam log for false positives
- [ ] Check if senior reported any missed spam
- [ ] Verify monitoring service is running

### Monthly Tasks (15 minutes)
- [ ] Update scam keywords based on new patterns
- [ ] Review Claude API costs (if using hybrid)
- [ ] Generate monthly report for senior education

### Quarterly Tasks (30 minutes)
- [ ] Update Python dependencies
- [ ] Review and tune ML thresholds
- [ ] Update senior's cheat sheet with new scam types

---

## 🆘 Troubleshooting

### "Monitor script stopped running"

```bash
# Check service status
sudo systemctl status senior-email-monitor

# Check logs
journalctl -u senior-email-monitor -n 50

# Restart service
sudo systemctl restart senior-email-monitor
```

### "Too many false positives"

Edit `local-ml-alternative.py`, lower the spam threshold:

```python
# In _classify method, adjust thresholds
if confidence > 0.9:  # Was 0.8, now more conservative
    classification = "fraud"
```

### "Gmail app password not working"

1. Ensure 2FA is enabled on Gmail account
2. Generate new app password
3. Use the exact 16-character password (no spaces)
4. Check IMAP is enabled in Gmail settings

### "High Claude API costs"

1. Check `MAX_CLAUDE_CALLS_PER_DAY` setting
2. Review which emails triggered Claude analysis
3. Adjust confidence thresholds to reduce edge cases
4. Consider switching to local-only mode

---

## 📱 Mobile App Integration (Future)

For advanced setups, integrate with mobile notifications:

```bash
# Install ntfy for mobile notifications
pip install ntfy

# In monitor_email.py, add:
import ntfy

def notify_spam_blocked(subject, risk_level):
    ntfy.notify(
        f"Spam blocked: {subject}",
        f"Risk level: {risk_level}",
        priority='low'
    )
```

---

## ✅ Success Criteria

Your setup is working well if:

- [ ] Spam is being caught automatically (check spam_log.txt)
- [ ] Senior hasn't reported seeing obvious scams in inbox
- [ ] False positive rate is <5%
- [ ] Monitoring service runs reliably 24/7
- [ ] You receive weekly reports
- [ ] Costs are within budget
- [ ] Senior feels more confident with email

---

## 🎓 Senior Education Template

**Create this as a laminated card near their computer:**

```
┌─────────────────────────────────────────┐
│       EMAIL SAFETY QUICK GUIDE          │
├─────────────────────────────────────────┤
│                                         │
│ ❌ NEVER CLICK if email asks for:      │
│   • Social Security Number              │
│   • Passwords or PINs                   │
│   • Bank account numbers                │
│   • Gift card purchases                 │
│   • Wire transfers                      │
│                                         │
│ 🚨 RED FLAGS (DELETE IMMEDIATELY):     │
│   • "Your account is suspended"         │
│   • "Act now or else"                   │
│   • "You won a prize" (you didn't enter)│
│   • "IRS/Social Security urgent email"  │
│   • "Tech support detected virus"       │
│                                         │
│ ✅ WHEN UNSURE:                         │
│   1. Don't click anything               │
│   2. Close the email                    │
│   3. Call me: [YOUR PHONE]              │
│   4. Or forward to: [YOUR EMAIL]        │
│                                         │
│ REMEMBER: Real companies will never     │
│ ask for passwords or personal info      │
│ via email!                              │
└─────────────────────────────────────────┘
```

---

## 📞 Emergency Contacts

Add these to the senior's contact list:

- **You (child):** [phone]  [email]
- **Local Police (non-emergency):** [phone]
- **FTC Fraud Hotline:** 1-877-FTC-HELP
- **Jortty Support:** support@jortty.com
- **Gmail Support:** support.google.com/mail

---

**You're all set! The senior's inbox is now protected.** 🛡️

For questions or improvements, see `ANALYSIS.md` or open an issue in this repository.
