"""
Advanced Copyright protection and content filtering with AI/ML
"""

import json
import logging
import re
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from telegram import Update
from telegram.ext import ContextTypes

try:
    import nltk
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import pickle
    import os
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("AI/ML libraries not available. Using basic filtering only.")

from .admin import is_admin
from .ai_copyright import ai_detector

logger = logging.getLogger(__name__)

def load_copyright_keywords():
    """Load copyright keywords from file"""
    try:
        with open('data/copyright_keywords.json', 'r') as f:
            data = json.load(f)
            return data.get('keywords', [])
    except (FileNotFoundError, json.JSONDecodeError):
        # Default copyright keywords
        return [
            'piracy', 'illegal download', 'torrent', 'crack', 'keygen',
            'warez', 'leaked movie', 'cam rip', 'dvd rip', 'blu-ray rip'
        ]

def save_copyright_keywords(keywords):
    """Save copyright keywords to file"""
    try:
        data = {
            'keywords': keywords,
            'last_updated': datetime.now().isoformat()
        }
        with open('data/copyright_keywords.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving copyright keywords: {e}")
        return False

def add_copyright_keyword(keyword):
    """Add a new copyright keyword"""
    keywords = load_copyright_keywords()
    keyword_lower = keyword.lower().strip()
    
    if keyword_lower not in [k.lower() for k in keywords]:
        keywords.append(keyword_lower)
        return save_copyright_keywords(keywords)
    return False

def remove_copyright_keyword(keyword):
    """Remove a copyright keyword"""
    keywords = load_copyright_keywords()
    keyword_lower = keyword.lower().strip()
    
    # Find and remove the keyword (case-insensitive)
    for i, k in enumerate(keywords):
        if k.lower() == keyword_lower:
            keywords.pop(i)
            return save_copyright_keywords(keywords)
    return False

def check_copyright_violation(text: str) -> dict:
    """
    Advanced copyright violation detection using AI/ML + keyword matching
    Returns: {
        'violation': bool,
        'matched_keywords': list,
        'severity': str,
        'action': str,
        'ai_analysis': dict,
        'confidence': float
    }
    """
    if not text:
        return {
            'violation': False, 
            'matched_keywords': [], 
            'severity': 'none', 
            'action': 'none',
            'ai_analysis': {},
            'confidence': 0.0
        }
    
    # Traditional keyword matching
    keywords = load_copyright_keywords()
    text_lower = text.lower()
    matched_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched_keywords.append(keyword)
    
    # AI/ML Risk Assessment
    ai_risk = ai_detector.risk_assessment(text)
    
    # Combine traditional and AI results
    keyword_score = len(matched_keywords) * 15  # 15 points per keyword
    ai_score = ai_risk['risk_score']
    
    # Combined violation score
    total_score = keyword_score + ai_score
    
    # Determine final violation status
    violation = total_score >= 40  # Threshold for violation
    
    # Determine severity and action based on combined score
    if total_score >= 90:
        severity = 'critical'
        action = 'ban'
    elif total_score >= 70:
        severity = 'high'
        action = 'delete'
    elif total_score >= 40:
        severity = 'medium'
        action = 'warn'
    else:
        severity = 'low'
        action = 'monitor'
    
    return {
        'violation': violation,
        'matched_keywords': matched_keywords,
        'severity': severity,
        'action': action,
        'ai_analysis': ai_risk,
        'confidence': min(total_score / 100.0, 1.0),
        'total_score': total_score
    }

def check_spam_patterns(text: str) -> dict:
    """Check for spam patterns in text"""
    if not text:
        return {'spam': False, 'patterns': [], 'confidence': 0}
    
    spam_patterns = [
        r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/\S*)?',  # URLs
        r'@[a-zA-Z0-9_]+',  # Mentions
        r'#[a-zA-Z0-9_]+',  # Hashtags
        r'\b(?:FREE|DOWNLOAD|CLICK|NOW|URGENT|LIMITED)\b',  # Spam words
        r'(?:[\u1F600-\u1F64F]|[\u1F300-\u1F5FF]|[\u1F680-\u1F6FF]|[\u1F1E0-\u1F1FF]){3,}',  # Excessive emojis
    ]
    
    matched_patterns = []
    text_upper = text.upper()
    
    for pattern in spam_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            matched_patterns.extend(matches)
    
    # Check for excessive caps
    caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
    if caps_ratio > 0.7 and len(text) > 20:
        matched_patterns.append('EXCESSIVE_CAPS')
    
    # Check for repeated characters
    if re.search(r'(.)\1{4,}', text):
        matched_patterns.append('REPEATED_CHARS')
    
    spam_score = len(matched_patterns)
    confidence = min(spam_score * 20, 100)  # Max 100% confidence
    
    return {
        'spam': spam_score >= 2,
        'patterns': matched_patterns,
        'confidence': confidence
    }

async def message_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle message filtering for copyright and spam"""
    if not update.message or not update.message.text or not update.effective_user:
        return
    
    # Skip admin messages
    if is_admin(update.effective_user.id):
        return
    
    message_text = update.message.text
    user_id = update.effective_user.id
    
    # Check for copyright violations
    copyright_check = check_copyright_violation(message_text)
    
    if copyright_check['violation']:
        logger.warning(
            f"Copyright violation detected from user {user_id}: "
            f"matched keywords: {copyright_check['matched_keywords']}"
        )
        
        # Take action based on severity
        if copyright_check['action'] in ['delete', 'ban']:
            try:
                await update.message.delete()
                
                # Enhanced warning message with AI analysis
                ai_analysis = copyright_check.get('ai_analysis', {})
                confidence = copyright_check.get('confidence', 0.0)
                total_score = copyright_check.get('total_score', 0)
                
                warning_msg = f"""
🚨 **Advanced Copyright Violation Detected**

Your message has been removed for containing copyrighted content.

**Detection Details:**
• **Severity:** {copyright_check['severity'].upper()}
• **Confidence:** {confidence:.1%}
• **Risk Score:** {total_score}/100

**Matched Keywords:** {', '.join(copyright_check['matched_keywords']) if copyright_check['matched_keywords'] else 'None'}

**AI Analysis:**
• **ML Prediction:** {'Violation' if ai_analysis.get('ml_result', {}).get('violation') else 'Clean'}
• **Risk Level:** {ai_analysis.get('risk_level', 'Unknown').title()}
• **Detected Patterns:** {len(ai_analysis.get('patterns', {}))} pattern(s)

Please respect copyright laws and our community guidelines.
"""
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=warning_msg,
                    parse_mode='Markdown'
                )
                
                # Log detailed analysis for admins
                logger.warning(
                    f"Advanced copyright violation detected from user {user_id}: "
                    f"Score: {total_score}, Severity: {copyright_check['severity']}, "
                    f"AI Risk: {ai_analysis.get('risk_level')}, "
                    f"Keywords: {copyright_check['matched_keywords']}, "
                    f"Patterns: {ai_analysis.get('patterns', {})}"
                )
                
            except Exception as e:
                logger.error(f"Error deleting copyright violation message: {e}")
        
        elif copyright_check['action'] == 'warn':
            ai_analysis = copyright_check.get('ai_analysis', {})
            confidence = copyright_check.get('confidence', 0.0)
            
            warning_msg = f"""
⚠️ **AI-Powered Copyright Warning**

Your message contains potentially copyrighted content.

**Detection Details:**
• **Confidence:** {confidence:.1%}
• **AI Risk Level:** {ai_analysis.get('risk_level', 'Unknown').title()}
• **Matched Keywords:** {', '.join(copyright_check['matched_keywords']) if copyright_check['matched_keywords'] else 'Pattern-based detection'}

**Recommendation:** {ai_analysis.get('recommendation', 'Please be mindful of copyright laws')}

Please ensure your content respects copyright guidelines.
"""
            try:
                await update.message.reply_text(warning_msg, parse_mode='Markdown')
                
                # Log warning for monitoring
                logger.info(
                    f"Copyright warning issued to user {user_id}: "
                    f"Confidence: {confidence:.1%}, Risk: {ai_analysis.get('risk_level')}"
                )
            except Exception as e:
                logger.error(f"Error sending copyright warning: {e}")
    
    # Check for spam patterns
    spam_check = check_spam_patterns(message_text)
    
    if spam_check['spam'] and spam_check['confidence'] > 70:
        logger.warning(
            f"Spam detected from user {user_id}: "
            f"confidence: {spam_check['confidence']}%, patterns: {spam_check['patterns']}"
        )
        
        try:
            # Delete high-confidence spam
            if spam_check['confidence'] > 90:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text="🚫 Your message was removed for appearing to be spam."
                )
            else:
                # Just warn for medium confidence spam
                await update.message.reply_text(
                    "⚠️ Your message appears to contain spam-like content. "
                    "Please follow our community guidelines."
                )
        except Exception as e:
            logger.error(f"Error handling spam message: {e}")

async def add_keyword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addkeyword command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/addkeyword [keyword]`", parse_mode='Markdown')
        return

    keyword = ' '.join(context.args).strip()
    
    if add_copyright_keyword(keyword):
        await update.message.reply_text(f"✅ Copyright keyword `{keyword}` added successfully.", parse_mode='Markdown')
        logger.info(f"Admin {update.effective_user.id} added copyright keyword: {keyword}")
    else:
        await update.message.reply_text(f"❌ Keyword `{keyword}` already exists.", parse_mode='Markdown')

async def remove_keyword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removekeyword command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/removekeyword [keyword]`", parse_mode='Markdown')
        return

    keyword = ' '.join(context.args).strip()
    
    if remove_copyright_keyword(keyword):
        await update.message.reply_text(f"✅ Copyright keyword `{keyword}` removed successfully.", parse_mode='Markdown')
        logger.info(f"Admin {update.effective_user.id} removed copyright keyword: {keyword}")
    else:
        await update.message.reply_text(f"❌ Keyword `{keyword}` not found.", parse_mode='Markdown')

async def list_keywords_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listkeywords command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    keywords = load_copyright_keywords()
    
    if not keywords:
        await update.message.reply_text("📋 No copyright keywords configured.")
        return
    
    message = "🚫 **Copyright Keywords**\n\n"
    for i, keyword in enumerate(keywords, 1):
        message += f"{i}. `{keyword}`\n"
    
    message += f"\n**Total Keywords:** {len(keywords)}"
    message += f"\n\nUse `/addkeyword [keyword]` to add more keywords."
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def test_ai_detection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /testai command - test AI copyright detection"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/testai [text to analyze]`\n\n"
            "Example: `/testai download this movie for free`",
            parse_mode='Markdown'
        )
        return

    test_text = ' '.join(context.args)
    
    # Run advanced analysis
    copyright_result = check_copyright_violation(test_text)
    ai_analysis = copyright_result.get('ai_analysis', {})
    
    message = f"""
🧠 **AI Copyright Detection Test**

**Input Text:** `{test_text}`

**🎯 Overall Results:**
• **Violation Detected:** {'✅ YES' if copyright_result['violation'] else '❌ NO'}
• **Severity:** {copyright_result['severity'].upper()}
• **Action:** {copyright_result['action'].upper()}
• **Confidence:** {copyright_result.get('confidence', 0):.1%}
• **Total Score:** {copyright_result.get('total_score', 0)}/100

**🔍 Keyword Analysis:**
• **Matched Keywords:** {', '.join(copyright_result['matched_keywords']) if copyright_result['matched_keywords'] else 'None'}

**🤖 AI/ML Analysis:**
• **ML Prediction:** {'Violation' if ai_analysis.get('ml_result', {}).get('violation') else 'Clean'}
• **ML Confidence:** {ai_analysis.get('ml_result', {}).get('confidence', 0):.1%}
• **Risk Level:** {ai_analysis.get('risk_level', 'Unknown').title()}
• **Risk Score:** {ai_analysis.get('risk_score', 0):.1f}/100

**📊 Sentiment Analysis:**
• **Polarity:** {ai_analysis.get('sentiment', {}).get('polarity', 0):.2f} (-1 to 1)
• **Subjectivity:** {ai_analysis.get('sentiment', {}).get('subjectivity', 0):.2f} (0 to 1)

**🔎 Pattern Detection:**
• **Detected Patterns:** {len(ai_analysis.get('patterns', {}))}
• **Patterns:** {', '.join(ai_analysis.get('patterns', {}).keys()) if ai_analysis.get('patterns') else 'None'}

**💡 Recommendation:** {ai_analysis.get('recommendation', 'No recommendation')}
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
