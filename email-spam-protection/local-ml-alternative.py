#!/usr/bin/env python3
"""
Local ML-based Email Spam Detection (Privacy-Preserving Alternative)

This script demonstrates a privacy-first approach using local machine learning
models instead of sending email content to external APIs.

Advantages:
- Complete privacy (no data leaves local machine)
- No API costs
- Fast inference (<1 second per email)
- Works offline

Requirements:
    pip install transformers torch scikit-learn email-validator
"""

import re
import json
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse


@dataclass
class EmailAnalysis:
    """Results of email spam analysis"""
    is_spam: bool
    confidence: float
    classification: str  # legitimate, marketing, phishing, scam, fraud
    risk_level: str  # low, medium, high, critical
    indicators_found: List[str]
    explanation_for_senior: str
    recommended_action: str  # delete, move_to_spam, flag_for_review, safe
    educational_note: str


class LocalSpamDetector:
    """Local spam detection using rule-based and ML approaches"""

    # Senior-targeted scam indicators
    SCAM_KEYWORDS = {
        'urgency': [
            r'\b(urgent|immediately|act now|limited time|expires today|last chance)\b',
            r'\b(suspended|locked|verify now|confirm immediately)\b',
        ],
        'authority': [
            r'\b(IRS|Social Security|Medicare|SSA|government)\b',
            r'\b(Amazon|Microsoft|Apple|Google|PayPal)\b',
            r'\b(bank|credit union|financial institution)\b',
        ],
        'money_request': [
            r'\b(gift card|wire transfer|send money|payment required)\b',
            r'\b(refund|tax return|stimulus|benefits)\b',
            r'\b(won|winner|prize|lottery|inheritance)\b',
        ],
        'info_request': [
            r'\b(verify account|confirm identity|update information)\b',
            r'\b(SSN|social security number|password|PIN)\b',
            r'\b(click here|verify now|confirm here)\b',
        ],
        'emotional': [
            r'\b(help|emergency|urgent help needed)\b',
            r'\b(grandson|granddaughter|family emergency)\b',
            r'\b(arrest|warrant|legal action|lawsuit)\b',
        ],
    }

    # Suspicious patterns
    SUSPICIOUS_PATTERNS = {
        'poor_grammar': r'(\w+\s+\w+\s+\w+)\s+\1',  # Repeated phrases
        'excessive_caps': r'[A-Z\s]{20,}',  # Long stretches of caps
        'suspicious_urls': r'(bit\.ly|tinyurl|shorturl|t\.co|goo\.gl)',
        'number_heavy': r'\d{4,}',  # Long number sequences
    }

    def __init__(self):
        """Initialize the detector"""
        # In a production system, load a pre-trained model here
        # For this demo, we use rule-based detection
        self.model_loaded = False

    def analyze_email(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> EmailAnalysis:
        """
        Analyze an email for spam/scam indicators

        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address

        Returns:
            EmailAnalysis object with detection results
        """
        combined_text = f"{subject} {body}".lower()
        indicators = []
        score = 0.0

        # Check sender domain
        sender_score, sender_indicators = self._check_sender(sender)
        score += sender_score
        indicators.extend(sender_indicators)

        # Check for scam keywords
        keyword_score, keyword_indicators = self._check_keywords(combined_text)
        score += keyword_score
        indicators.extend(keyword_indicators)

        # Check for suspicious patterns
        pattern_score, pattern_indicators = self._check_patterns(combined_text)
        score += pattern_score
        indicators.extend(pattern_indicators)

        # Check for senior-specific targeting
        senior_score, senior_indicators = self._check_senior_targeting(combined_text)
        score += senior_score * 2  # Weight this higher
        indicators.extend(senior_indicators)

        # Normalize score (0-1 range)
        confidence = min(score / 10.0, 1.0)

        # Determine classification and risk
        is_spam, classification, risk_level = self._classify(confidence, indicators)

        # Generate explanation
        explanation = self._generate_explanation(indicators, is_spam)

        # Determine action
        action = self._recommend_action(risk_level, confidence)

        # Generate educational note
        educational_note = self._generate_educational_note(indicators)

        return EmailAnalysis(
            is_spam=is_spam,
            confidence=round(confidence, 2),
            classification=classification,
            risk_level=risk_level,
            indicators_found=indicators,
            explanation_for_senior=explanation,
            recommended_action=action,
            educational_note=educational_note
        )

    def _check_sender(self, sender: str) -> Tuple[float, List[str]]:
        """Check sender email for suspicious patterns"""
        indicators = []
        score = 0.0

        # Check for Gmail/Yahoo/Hotmail claiming to be official
        if re.search(r'@(gmail|yahoo|hotmail|outlook)\.com', sender, re.I):
            if any(org in sender.lower() for org in ['irs', 'ssa', 'social', 'medicare', 'bank']):
                indicators.append("Official organization using free email service")
                score += 3.0

        # Check for suspicious TLDs
        if re.search(r'\.(xyz|top|tk|ml|ga|cf|work|click)$', sender, re.I):
            indicators.append("Suspicious email domain")
            score += 2.0

        return score, indicators

    def _check_keywords(self, text: str) -> Tuple[float, List[str]]:
        """Check for scam keyword patterns"""
        indicators = []
        score = 0.0

        for category, patterns in self.SCAM_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    indicators.append(f"Contains {category} language")
                    score += 1.5
                    break  # Only count each category once

        return score, indicators

    def _check_patterns(self, text: str) -> Tuple[float, List[str]]:
        """Check for suspicious patterns"""
        indicators = []
        score = 0.0

        for pattern_name, pattern in self.SUSPICIOUS_PATTERNS.items():
            if re.search(pattern, text, re.I):
                indicators.append(f"Suspicious pattern: {pattern_name}")
                score += 1.0

        return score, indicators

    def _check_senior_targeting(self, text: str) -> Tuple[float, List[str]]:
        """Check for patterns specifically targeting seniors"""
        indicators = []
        score = 0.0

        senior_patterns = [
            (r'(grandchild|grandson|granddaughter)', "Grandparent scam pattern"),
            (r'(social security.*suspend|ssa.*benefit)', "Social Security scam"),
            (r'(medicare.*refund|health.*benefit)', "Medicare scam"),
            (r'(senior.*discount|retirement.*benefit)', "Senior-targeted offer"),
            (r'(reverse mortgage|estate.*planning)', "Financial targeting"),
        ]

        for pattern, description in senior_patterns:
            if re.search(pattern, text, re.I):
                indicators.append(description)
                score += 2.0

        return score, indicators

    def _classify(
        self,
        confidence: float,
        indicators: List[str]
    ) -> Tuple[bool, str, str]:
        """Classify the email and determine risk level"""

        # Determine if spam
        is_spam = confidence > 0.5

        # Determine classification
        if confidence > 0.8:
            classification = "fraud"
            risk_level = "critical"
        elif confidence > 0.6:
            classification = "scam"
            risk_level = "high"
        elif confidence > 0.4:
            classification = "phishing"
            risk_level = "medium"
        elif confidence > 0.2:
            classification = "marketing"
            risk_level = "low"
        else:
            classification = "legitimate"
            risk_level = "low"

        # Adjust based on specific indicators
        if any("Social Security" in ind or "Medicare" in ind for ind in indicators):
            risk_level = "critical"

        return is_spam, classification, risk_level

    def _generate_explanation(self, indicators: List[str], is_spam: bool) -> str:
        """Generate a simple explanation for seniors"""
        if not is_spam:
            return "This email appears to be legitimate and safe."

        if not indicators:
            return "This email has some suspicious characteristics. Be cautious."

        explanation = "⚠️ This email is likely a SCAM. Here's why:\n\n"
        for i, indicator in enumerate(indicators[:3], 1):  # Top 3 indicators
            explanation += f"{i}. {indicator}\n"

        if len(indicators) > 3:
            explanation += f"\n...and {len(indicators) - 3} other warning signs."

        return explanation

    def _recommend_action(self, risk_level: str, confidence: float) -> str:
        """Recommend what action to take"""
        if risk_level == "critical" or confidence > 0.8:
            return "delete"
        elif risk_level == "high" or confidence > 0.6:
            return "move_to_spam"
        elif risk_level == "medium" or confidence > 0.4:
            return "flag_for_review"
        else:
            return "safe"

    def _generate_educational_note(self, indicators: List[str]) -> str:
        """Generate educational content about this scam type"""
        if not indicators:
            return ""

        # Map indicators to education
        education = {
            "urgency": "Scammers create fake urgency to pressure you into acting without thinking.",
            "authority": "Scammers impersonate trusted organizations. Real organizations won't contact you this way.",
            "money": "Never send money (especially gift cards) to someone who contacts you unexpectedly.",
            "personal": "Legitimate organizations already have your information and won't ask for it via email.",
        }

        # Find the most relevant education
        for indicator in indicators:
            for key, edu in education.items():
                if key in indicator.lower():
                    return f"💡 Remember: {edu}"

        return "💡 Remember: When in doubt, contact the organization directly using a phone number you look up yourself (not one in the email)."


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Local ML-based email spam detection for seniors"
    )
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--sender", required=True, help="Sender email address")
    parser.add_argument("--output", help="Output JSON file path")

    args = parser.parse_args()

    # Initialize detector
    detector = LocalSpamDetector()

    # Analyze email
    result = detector.analyze_email(
        subject=args.subject,
        body=args.body,
        sender=args.sender
    )

    # Convert to dict
    result_dict = asdict(result)
    result_dict['timestamp'] = datetime.now().isoformat()
    result_dict['email_subject'] = args.subject
    result_dict['email_sender'] = args.sender

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result_dict, f, indent=2)
        print(f"Analysis saved to {args.output}")
    else:
        print(json.dumps(result_dict, indent=2))

    # Print summary to stderr
    import sys
    print("\n" + "="*50, file=sys.stderr)
    print("SPAM DETECTION RESULT", file=sys.stderr)
    print("="*50, file=sys.stderr)
    print(f"Is Spam: {result.is_spam}", file=sys.stderr)
    print(f"Confidence: {result.confidence}", file=sys.stderr)
    print(f"Risk Level: {result.risk_level}", file=sys.stderr)
    print(f"Action: {result.recommended_action}", file=sys.stderr)
    print(f"\n{result.explanation_for_senior}", file=sys.stderr)
    print(f"\n{result.educational_note}", file=sys.stderr)
    print("="*50, file=sys.stderr)

    # Exit with code based on action
    exit_codes = {
        'delete': 10,
        'move_to_spam': 10,
        'flag_for_review': 5,
        'safe': 0
    }
    sys.exit(exit_codes.get(result.recommended_action, 1))


if __name__ == "__main__":
    main()
