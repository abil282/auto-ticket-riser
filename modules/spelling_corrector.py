"""
Spelling Correction and Keyword Normalization Module
Handles auto-correction of IT-related spelling mistakes and keyword normalization
"""

import re
from difflib import SequenceMatcher


class SpellingCorrector:
    """Auto-correct common IT-related spelling mistakes"""
    
    # Dictionary of common IT spelling mistakes and corrections
    IT_CORRECTIONS = {
        # Network-related
        'netwrok': 'network',
        'network': 'network',
        'conection': 'connection',
        'conecton': 'connection',
        'connetion': 'connection',
        'connectoin': 'connection',
        'connection': 'connection',
        'wifi': 'WiFi',
        'wi-fi': 'WiFi',
        'wifi': 'WiFi',
        'internet': 'internet',
        'internett': 'internet',
        'conectivity': 'connectivity',
        'connectivity': 'connectivity',
        
        # Login-related
        'login': 'login',
        'logon': 'logon',
        'loggin': 'login',
        'loging': 'login',
        'authentification': 'authentication',
        'autentication': 'authentication',
        'authentcation': 'authentication',
        'authentcaton': 'authentication',
        'authetication': 'authentication',
        'password': 'password',
        'pasword': 'password',
        'passwd': 'password',
        'pwd': 'password',
        'crendentials': 'credentials',
        'credentials': 'credentials',
        
        # Windows-related
        'windows': 'Windows',
        'windos': 'Windows',
        'windwos': 'Windows',
        'wndows': 'Windows',
        'activedirectory': 'Active Directory',
        'active directory': 'Active Directory',
        'activedirectroy': 'Active Directory',
        'ad': 'Active Directory',
        
        # Email-related
        'email': 'email',
        'emai': 'email',
        'emial': 'email',
        'outlook': 'Outlook',
        'outlok': 'Outlook',
        'exchnage': 'Exchange',
        'exchange': 'Exchange',
        'excahnge': 'Exchange',
        
        # Hardware-related
        'monnitor': 'monitor',
        'monitor': 'monitor',
        'mouse': 'mouse',
        'keybord': 'keyboard',
        'keyboard': 'keyboard',
        'prnnter': 'printer',
        'printer': 'printer',
        'hardwre': 'hardware',
        'hardware': 'hardware',
        
        # Software-related
        'sofware': 'software',
        'softwre': 'software',
        'software': 'software',
        'instalation': 'installation',
        'installation': 'installation',
        'uninstal': 'uninstall',
        'uninstall': 'uninstall',
        'applicaton': 'application',
        'aplication': 'application',
        'application': 'application',
        'update': 'update',
        'updaet': 'update',
        'updat': 'update',
        
        # Access-related
        'permision': 'permission',
        'permisison': 'permission',
        'permission': 'permission',
        'acces': 'access',
        'acess': 'access',
        'access': 'access',
        'authoriztion': 'authorization',
        'authorization': 'authorization',
        'authorisation': 'authorization',
        
        # Performance-related
        'perfomance': 'performance',
        'performence': 'performance',
        'performance': 'performance',
        'speed': 'speed',
        'sped': 'speed',
        'slow': 'slow',
        'crash': 'crash',
        'crashing': 'crashing',
        'freezing': 'freezing',
        'hang': 'hang',
        'hanging': 'hanging',
        
        # Database-related
        'databse': 'database',
        'database': 'database',
        'sql': 'SQL',
        'backend': 'backend',
        'bacend': 'backend',
        
        # Error-related
        'erorr': 'error',
        'errror': 'error',
        'error': 'error',
        'warning': 'warning',
        'issue': 'issue',
        'isue': 'issue',
        'problm': 'problem',
        'problem': 'problem',
        'bug': 'bug',
        'crash': 'crash',
        
        # Support-related
        'tickt': 'ticket',
        'tikket': 'ticket',
        'ticket': 'ticket',
        'support': 'support',
        'supoprt': 'support',
        'requrest': 'request',
        'request': 'request',
        'servcie': 'service',
        'service': 'service',
    }
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        'urgent': 'P1 - Critical',
        'critical': 'P1 - Critical',
        'critical': 'P1 - Critical',
        'emergency': 'P1 - Critical',
        'asap': 'P1 - Critical',
        'high': 'P2 - High',
        'urgent': 'P2 - High',
        'moderate': 'P3 - Medium',
        'normal': 'P3 - Medium',
        'routine': 'P4 - Low',
        'low': 'P4 - Low',
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        'network': ['network', 'internet', 'connection', 'connectivity', 'wifi', 'lan', 'vpn'],
        'email': ['email', 'outlook', 'exchange', 'mail', 'smtp', 'imap'],
        'login': ['login', 'authentication', 'access', 'credentials', 'password', 'logon', 'ad'],
        'hardware': ['monitor', 'keyboard', 'mouse', 'printer', 'hardware', 'device', 'laptop', 'desktop'],
        'software': ['software', 'application', 'installation', 'update', 'patch', 'license'],
        'database': ['database', 'sql', 'backend', 'data', 'query'],
        'security': ['security', 'antivirus', 'firewall', 'vpn', 'encryption', 'malware'],
        'performance': ['slow', 'crash', 'freeze', 'hang', 'performance', 'speed', 'lag'],
    }

    def __init__(self):
        """Initialize the spelling corrector"""
        self.corrections_applied = []

    def correct_spelling(self, text):
        """
        Correct common IT spelling mistakes
        
        Args:
            text (str): The text to correct
            
        Returns:
            tuple: (corrected_text, list_of_corrections)
        """
        if not isinstance(text, str) or not text.strip():
            return text, []
        
        words = text.split()
        corrected_words = []
        corrections = []
        
        for word in words:
            # Remove punctuation from word for matching
            clean_word = re.sub(r'[^\w\s]', '', word).lower()
            
            if clean_word in self.IT_CORRECTIONS:
                corrected = self.IT_CORRECTIONS[clean_word]
                corrected_words.append(corrected)
                corrections.append({
                    'original': word,
                    'corrected': corrected,
                    'type': 'spelling'
                })
            else:
                # Try fuzzy matching for similar words
                fuzzy_match = self._fuzzy_match(clean_word)
                if fuzzy_match:
                    corrected_words.append(fuzzy_match)
                    corrections.append({
                        'original': word,
                        'corrected': fuzzy_match,
                        'type': 'fuzzy_match'
                    })
                else:
                    corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        return corrected_text, corrections

    def _fuzzy_match(self, word, threshold=0.85):
        """
        Fuzzy match a word against known corrections
        
        Args:
            word (str): The word to match
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            str: Best matching correction or None
        """
        best_match = None
        best_score = threshold
        
        for key, value in self.IT_CORRECTIONS.items():
            score = SequenceMatcher(None, word, key).ratio()
            if score > best_score:
                best_score = score
                best_match = value
        
        return best_match

    def normalize_keywords(self, text):
        """
        Normalize IT keywords to standard formats
        
        Args:
            text (str): The text to normalize
            
        Returns:
            dict: Normalized text and detected category/priority
        """
        if not isinstance(text, str):
            text = str(text)
        
        text_lower = text.lower()
        
        # Detect priority
        priority = 'P3 - Medium'  # Default priority
        for keyword, priority_level in self.PRIORITY_KEYWORDS.items():
            if keyword in text_lower:
                priority = priority_level
                break
        
        # Detect category
        detected_category = 'General'
        word_set = set(text_lower.split())
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in word_set or keyword in text_lower for keyword in keywords):
                detected_category = category.title()
                break
        
        return {
            'priority': priority,
            'category': detected_category,
            'normalized_text': text
        }

    def process_ticket_description(self, description):
        """
        Full processing pipeline for ticket description
        
        Args:
            description (str): Raw ticket description
            
        Returns:
            dict: Processed ticket data with corrections and normalizations
        """
        # Step 1: Correct spelling
        corrected_text, corrections = self.correct_spelling(description)
        
        # Step 2: Normalize keywords
        normalization = self.normalize_keywords(corrected_text)
        
        return {
            'original_description': description,
            'corrected_description': corrected_text,
            'spelling_corrections': corrections,
            'priority': normalization['priority'],
            'category': normalization['category'],
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }


# Global instance
spelling_corrector = SpellingCorrector()
