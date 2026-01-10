#!/bin/bash
#
# Example: Claude Code Email Spam Detection Integration
# WARNING: This is for DEMONSTRATION purposes - see ANALYSIS.md for why this
# approach is NOT recommended as a primary solution
#
# Usage: ./example-claude-integration.sh "email_subject" "email_body" "sender_email"
#

set -e

# Configuration
CLAUDE_CLI="claude"
MAX_TURNS=2
OUTPUT_DIR="./spam-analysis-results"
LOG_FILE="$OUTPUT_DIR/detection.log"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Input parameters
EMAIL_SUBJECT="$1"
EMAIL_BODY="$2"
SENDER_EMAIL="$3"

if [ -z "$EMAIL_SUBJECT" ] || [ -z "$EMAIL_BODY" ] || [ -z "$SENDER_EMAIL" ]; then
    echo "Usage: $0 <subject> <body> <sender_email>"
    exit 1
fi

# Create timestamp for this analysis
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="$OUTPUT_DIR/analysis_$TIMESTAMP.json"

# Log the incoming email
echo "[$(date)] Analyzing email from: $SENDER_EMAIL" >> "$LOG_FILE"

# Construct the analysis prompt
PROMPT="You are analyzing an email to protect a senior citizen from spam and scams.

## Email Details:
- **From:** $SENDER_EMAIL
- **Subject:** $EMAIL_SUBJECT
- **Body:**
$EMAIL_BODY

## Your Task:
Analyze this email for spam/scam indicators that commonly target seniors. Look for:

1. **Urgency tactics** (\"act now\", \"limited time\", \"account suspended\")
2. **Authority impersonation** (IRS, Social Security, Medicare, banks, tech support)
3. **Requests for personal information** (SSN, passwords, account numbers)
4. **Requests for money** (gift cards, wire transfers, \"help\" requests)
5. **Emotional manipulation** (fear, greed, sympathy)
6. **Suspicious links or attachments**
7. **Poor grammar/spelling** inconsistent with legitimate organizations
8. **AI-generated patterns** (overly polished but generic language)
9. **Too-good-to-be-true offers** (prizes, inheritance, refunds)
10. **Spoofed email addresses** (looks official but domain is wrong)

## Required Output:
Respond with ONLY a JSON object (no other text):

{
  \"is_spam\": true or false,
  \"confidence\": 0.0 to 1.0,
  \"classification\": \"legitimate\" | \"marketing\" | \"phishing\" | \"scam\" | \"fraud\",
  \"risk_level\": \"low\" | \"medium\" | \"high\" | \"critical\",
  \"indicators_found\": [\"list of specific red flags found\"],
  \"explanation_for_senior\": \"Simple, clear explanation a senior can understand\",
  \"recommended_action\": \"delete\" | \"move_to_spam\" | \"flag_for_review\" | \"safe\",
  \"educational_note\": \"What can the senior learn from this to recognize similar scams?\"
}
"

# Run Claude Code in headless mode
echo "[$(date)] Running Claude Code analysis..." >> "$LOG_FILE"

RESULT=$($CLAUDE_CLI -p "$PROMPT" \
    --output-format json \
    --max-turns $MAX_TURNS \
    2>> "$LOG_FILE")

# Save the full result
echo "$RESULT" > "$RESULT_FILE"

# Parse the key fields
IS_SPAM=$(echo "$RESULT" | jq -r '.structured_output.is_spam // .response.is_spam // false')
CONFIDENCE=$(echo "$RESULT" | jq -r '.structured_output.confidence // .response.confidence // 0')
RISK_LEVEL=$(echo "$RESULT" | jq -r '.structured_output.risk_level // .response.risk_level // "unknown"')
RECOMMENDED_ACTION=$(echo "$RESULT" | jq -r '.structured_output.recommended_action // .response.recommended_action // "flag_for_review"')
EXPLANATION=$(echo "$RESULT" | jq -r '.structured_output.explanation_for_senior // .response.explanation_for_senior // "Unable to analyze"')

# Log the result
echo "[$(date)] Result - Spam: $IS_SPAM, Confidence: $CONFIDENCE, Risk: $RISK_LEVEL, Action: $RECOMMENDED_ACTION" >> "$LOG_FILE"

# Output summary
echo "=================================="
echo "SPAM DETECTION RESULT"
echo "=================================="
echo "Email: $SENDER_EMAIL"
echo "Subject: $EMAIL_SUBJECT"
echo ""
echo "Is Spam: $IS_SPAM"
echo "Confidence: $CONFIDENCE"
echo "Risk Level: $RISK_LEVEL"
echo "Recommended Action: $RECOMMENDED_ACTION"
echo ""
echo "Explanation for Senior:"
echo "$EXPLANATION"
echo ""
echo "Full analysis saved to: $RESULT_FILE"
echo "=================================="

# Return exit code based on recommendation
case "$RECOMMENDED_ACTION" in
    delete|move_to_spam)
        exit 10  # Spam detected
        ;;
    flag_for_review)
        exit 5   # Uncertain
        ;;
    safe)
        exit 0   # Safe
        ;;
    *)
        exit 1   # Error
        ;;
esac
