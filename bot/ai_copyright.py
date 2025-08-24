"""
Advanced AI/ML Copyright Detection System
"""

import logging
import re
import os
import pickle
from typing import Dict, List
from datetime import datetime

try:
    import nltk
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("AI/ML libraries not available. Using basic filtering only.")

logger = logging.getLogger(__name__)

class AdvancedCopyrightDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        self.model_path = 'data/copyright_model.pkl'
        self.vectorizer_path = 'data/copyright_vectorizer.pkl'
        self.training_data = self._get_training_data()
        
        if AI_AVAILABLE:
            self._initialize_nltk()
            self._load_or_train_model()
    
    def _initialize_nltk(self):
        """Initialize NLTK data"""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
        except Exception as e:
            logger.error(f"Error downloading NLTK data: {e}")
    
    def _get_training_data(self):
        """Get training data for copyright detection"""
        # Positive samples (copyright violations)
        positive_samples = [
            'download this movie for free',
            'pirated version available here',
            'get latest movies without paying',
            'cracked software download',
            'leaked film before release',
            'torrent magnet link',
            'free premium content',
            'bypass subscription',
            'stolen content alert',
            'unauthorized distribution',
            'bootleg copy available',
            'ripped from dvd',
            'cam quality recording',
            'share copyrighted material',
            'illegal streaming site',
            'warez download link',
            'keygen for activation',
            'crack for premium software',
            'serial key generator',
            'hacked version download',
            'watch movies without subscription',
            'free netflix account',
            'bypass paywall',
            'stolen movie link'
        ]
        
        # Negative samples (legitimate content)
        negative_samples = [
            'official movie trailer',
            'buy tickets online',
            'subscribe to streaming service',
            'legal movie review',
            'cinema showtimes',
            'movie recommendation',
            'official soundtrack',
            'director interview',
            'behind the scenes footage',
            'movie discussion',
            'film analysis',
            'cast information',
            'movie news update',
            'official poster release',
            'theater booking',
            'rental service',
            'purchase digital copy',
            'official merchandise',
            'movie quotes',
            'trivia and facts',
            'legitimate streaming platform',
            'official website',
            'cinema experience',
            'movie awards ceremony'
        ]
        
        # Create labeled dataset
        training_texts = positive_samples + negative_samples
        training_labels = [1] * len(positive_samples) + [0] * len(negative_samples)
        
        return list(zip(training_texts, training_labels))
    
    def _load_or_train_model(self):
        """Load existing model or train new one"""
        try:
            # Try to load existing model
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                self.is_trained = True
                logger.info("Loaded existing copyright detection model")
            else:
                self._train_model()
        except Exception as e:
            logger.error(f"Error loading/training model: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train the copyright detection model"""
        try:
            texts, labels = zip(*self.training_data)
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True
            )
            
            # Transform texts to features
            X = self.vectorizer.fit_transform(texts)
            
            # Train Naive Bayes classifier
            self.model = MultinomialNB(alpha=0.1)
            self.model.fit(X, labels)
            
            self.is_trained = True
            
            # Save model
            os.makedirs('data', exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            logger.info("Trained and saved new copyright detection model")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            self.is_trained = False
    
    def predict_copyright_violation(self, text: str) -> Dict:
        """Predict if text contains copyright violation using AI/ML"""
        if not AI_AVAILABLE or not self.is_trained:
            return {'violation': False, 'confidence': 0.0, 'method': 'unavailable'}
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Transform to features
            features = self.vectorizer.transform([processed_text])
            
            # Predict
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            # Get confidence (probability of positive class)
            confidence = probability[1] if len(probability) > 1 else probability[0]
            
            return {
                'violation': bool(prediction),
                'confidence': float(confidence),
                'method': 'machine_learning'
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return {'violation': False, 'confidence': 0.0, 'method': 'error'}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for ML analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob"""
        if not AI_AVAILABLE:
            return {'polarity': 0.0, 'subjectivity': 0.0}
        
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        if not AI_AVAILABLE:
            return 'unknown'
        
        try:
            blob = TextBlob(text)
            return blob.detect_language()
        except:
            return 'unknown'
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not AI_AVAILABLE or not self.is_trained:
            return []
        
        try:
            # Use TF-IDF to extract keywords
            features = self.vectorizer.transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get feature scores
            scores = features.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores[:num_keywords] if score > 0]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def advanced_pattern_detection(self, text: str) -> Dict:
        """Advanced pattern detection for copyright violations"""
        patterns = {
            'download_links': r'(?:https?://)?(?:www\.)?(?:mega|mediafire|drive\.google|dropbox|torrent)',
            'streaming_fraud': r'(?:free|crack|hack|bypass)\s+(?:netflix|hulu|disney|amazon|premium)',
            'piracy_terms': r'(?:cam|ts|dvdrip|brrip|webrip|hdtv|xvid|x264)',
            'illegal_sharing': r'(?:share|upload|leak|distribute)\s+(?:movie|film|content)',
            'monetization_fraud': r'(?:without\s+pay|no\s+subscription|free\s+premium)'
        }
        
        detected_patterns = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text.lower())
            if matches:
                detected_patterns[pattern_name] = matches
        
        return detected_patterns
    
    def content_fingerprinting(self, text: str) -> str:
        """Generate content fingerprint for duplicate detection"""
        import hashlib
        
        # Normalize text
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Generate hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def risk_assessment(self, text: str) -> Dict:
        """Comprehensive risk assessment"""
        ml_result = self.predict_copyright_violation(text)
        sentiment = self.analyze_sentiment(text)
        patterns = self.advanced_pattern_detection(text)
        
        # Calculate risk score
        risk_score = 0
        
        # ML prediction weight (40%)
        if ml_result['violation']:
            risk_score += ml_result['confidence'] * 40
        
        # Pattern detection weight (35%)
        pattern_count = len(patterns)
        if pattern_count > 0:
            risk_score += min(pattern_count * 10, 35)
        
        # Sentiment analysis weight (15%)
        if sentiment['polarity'] < -0.3:
            risk_score += 15
        elif sentiment['polarity'] < 0:
            risk_score += 8
        
        # Subjectivity weight (10%)
        if sentiment['subjectivity'] > 0.8:
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = 'critical'
        elif risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        elif risk_score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'ml_result': ml_result,
            'sentiment': sentiment,
            'patterns': patterns,
            'recommendation': self._get_recommendation(risk_level)
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommended action based on risk level"""
        recommendations = {
            'critical': 'Immediately delete message and ban user',
            'high': 'Delete message and warn user',
            'medium': 'Flag for manual review',
            'low': 'Monitor user activity',
            'minimal': 'No action required'
        }
        return recommendations.get(risk_level, 'No action required')

# Initialize the AI detector
ai_detector = AdvancedCopyrightDetector()