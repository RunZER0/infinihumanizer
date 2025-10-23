"""
Post-processing module to add natural human imperfections to LLM output.
Handles cases where LLMs over-smooth text and removes human-like errors.
"""
import random
import re
from typing import List, Tuple


class HumanImperfectionPostProcessor:
    """
    Adds contextually appropriate grammatical quirks and word variations
    to make text feel more authentically human-written.
    """
    
    # Common academic phrases that can be replaced with less formal alternatives
    PHRASE_VARIATIONS = {
        "in order to": ["to", "in order to"],  # 60% chance of simplification
        "due to the fact that": ["because", "since", "due to the fact that"],
        "at this point in time": ["now", "currently", "at this point in time"],
        "in the event that": ["if", "in the event that"],
        "for the purpose of": ["to", "for", "for the purpose of"],
        "with regard to": ["about", "regarding", "with regard to"],
        "in spite of the fact that": ["although", "even though", "in spite of the fact that"],
        "it is important to note that": ["note that", "importantly", "it is important to note that"],
        "it should be noted that": ["notably", "it should be noted that"],
    }
    
    # Words that can occasionally have articles dropped (natural human error)
    ARTICLE_DROP_CONTEXTS = [
        (r'\bthe (same|similar|different)\b', r'\1'),  # "the same" -> "same"
        (r'\ba (very|more|less)\b', r'\1'),  # "a very" -> "very" 
    ]
    
    # Common academic words that can be varied
    WORD_VARIATIONS = {
        "utilize": ["use", "utilize"],
        "demonstrate": ["show", "demonstrate"],
        "facilitate": ["help", "enable", "facilitate"],
        "however": ["but", "however", "yet"],
        "furthermore": ["also", "furthermore", "moreover"],
        "therefore": ["so", "therefore", "thus"],
        "subsequently": ["then", "later", "subsequently"],
        "approximately": ["about", "around", "approximately"],
        "numerous": ["many", "numerous", "several"],
    }
    
    # Contractions to occasionally introduce (more casual/human)
    CONTRACTION_RULES = {
        r'\bit is\b': ["it is", "it's"],
        r'\bthat is\b': ["that is", "that's"],
        r'\bwhat is\b': ["what is", "what's"],
        r'\bdo not\b': ["do not", "don't"],
        r'\bcannot\b': ["cannot", "can't"],
        r'\bwill not\b': ["will not", "won't"],
        r'\bshould not\b': ["should not", "shouldn't"],
    }
    
    def __init__(self, 
                 imperfection_rate: float = 0.15,
                 contraction_rate: float = 0.20,
                 article_error_rate: float = 0.05):
        """
        Args:
            imperfection_rate: Probability of applying phrase/word variations (0.0-1.0)
            contraction_rate: Probability of adding contractions (0.0-1.0)
            article_error_rate: Probability of dropping articles (0.0-1.0, keep low!)
        """
        self.imperfection_rate = imperfection_rate
        self.contraction_rate = contraction_rate
        self.article_error_rate = article_error_rate
    
    def process(self, text: str) -> str:
        """
        Apply contextual imperfections to text.
        
        Args:
            text: Input text to process
            
        Returns:
            Text with natural imperfections added
        """
        if not text or len(text.strip()) < 20:
            return text
        
        # Step 1: Replace overly formal phrases with variations
        text = self._vary_phrases(text)
        
        # Step 2: Vary academic vocabulary
        text = self._vary_vocabulary(text)
        
        # Step 3: Add occasional contractions (casual tone)
        text = self._add_contractions(text)
        
        # Step 4: Rarely drop articles (subtle human error)
        text = self._drop_articles(text)
        
        # Step 5: Add occasional comma splices or run-ons (very rarely)
        text = self._add_comma_variation(text)
        
        return text
    
    def _vary_phrases(self, text: str) -> str:
        """Replace formal phrases with more natural variations."""
        for formal_phrase, variations in self.PHRASE_VARIATIONS.items():
            if formal_phrase in text.lower():
                # Find all case-preserving instances
                pattern = re.compile(re.escape(formal_phrase), re.IGNORECASE)
                
                def replace_with_variation(match):
                    if random.random() < self.imperfection_rate:
                        # Pick a variation (weighted toward simpler forms)
                        weights = [2] + [1] * (len(variations) - 1)  # Favor first option
                        choice = random.choices(variations, weights=weights)[0]
                        
                        # Preserve original capitalization
                        original = match.group(0)
                        if original[0].isupper():
                            choice = choice[0].upper() + choice[1:]
                        return choice
                    return match.group(0)
                
                text = pattern.sub(replace_with_variation, text)
        
        return text
    
    def _vary_vocabulary(self, text: str) -> str:
        """Replace academic words with more common alternatives occasionally."""
        for formal_word, variations in self.WORD_VARIATIONS.items():
            pattern = re.compile(r'\b' + re.escape(formal_word) + r'\b', re.IGNORECASE)
            
            def replace_with_variation(match):
                if random.random() < self.imperfection_rate:
                    choice = random.choice(variations)
                    original = match.group(0)
                    if original[0].isupper():
                        choice = choice[0].upper() + choice[1:]
                    return choice
                return match.group(0)
            
            text = pattern.sub(replace_with_variation, text)
        
        return text
    
    def _add_contractions(self, text: str) -> str:
        """Add contractions to make text less formal."""
        for pattern_str, variations in self.CONTRACTION_RULES.items():
            pattern = re.compile(pattern_str, re.IGNORECASE)
            
            def replace_with_contraction(match):
                if random.random() < self.contraction_rate:
                    choice = random.choice(variations[1:])  # Skip the formal version
                    original = match.group(0)
                    if original[0].isupper():
                        choice = choice[0].upper() + choice[1:]
                    return choice
                return match.group(0)
            
            text = pattern.sub(replace_with_contraction, text)
        
        return text
    
    def _drop_articles(self, text: str) -> str:
        """Occasionally drop articles (subtle human error, use sparingly)."""
        if random.random() > self.article_error_rate:
            return text  # Only apply to some texts
        
        for pattern_str, replacement in self.ARTICLE_DROP_CONTEXTS:
            if random.random() < 0.3:  # Only 30% chance even if enabled
                text = re.sub(pattern_str, replacement, text, count=1)  # Only once
        
        return text
    
    def _add_comma_variation(self, text: str) -> str:
        """
        Add natural comma variation:
        - Occasionally remove comma before 'and' in lists
        - Rarely add comma splice (two independent clauses with just comma)
        """
        # Remove oxford comma occasionally
        if random.random() < 0.15:
            text = re.sub(r',\s+and\s+(\w+)\s*\.', r' and \1.', text, count=1)
        
        # Very rarely create comma splice (human error)
        if random.random() < 0.05:
            # Find period between short sentences and replace with comma
            pattern = r'(\w+)\.\s+([A-Z]\w+\s+\w+)'
            match = re.search(pattern, text)
            if match:
                text = re.sub(pattern, r'\1, \2', text, count=1)
        
        return text
    
    def get_stats(self, original: str, processed: str) -> dict:
        """
        Return statistics about what was changed.
        
        Returns:
            Dictionary with change counts and types
        """
        return {
            "original_length": len(original),
            "processed_length": len(processed),
            "original_words": len(original.split()),
            "processed_words": len(processed.split()),
            "length_diff": len(processed) - len(original),
            "changes_made": original != processed,
        }


def add_natural_imperfections(text: str, 
                              intensity: str = "medium") -> Tuple[str, dict]:
    """
    Convenience function to add natural imperfections to text.
    
    Args:
        text: Text to process
        intensity: "light", "medium", or "heavy" - controls how many changes to make
        
    Returns:
        Tuple of (processed_text, stats_dict)
    """
    intensity_settings = {
        "light": {"imperfection_rate": 0.10, "contraction_rate": 0.10, "article_error_rate": 0.02},
        "medium": {"imperfection_rate": 0.15, "contraction_rate": 0.20, "article_error_rate": 0.05},
        "heavy": {"imperfection_rate": 0.25, "contraction_rate": 0.30, "article_error_rate": 0.08},
    }
    
    settings = intensity_settings.get(intensity, intensity_settings["medium"])
    processor = HumanImperfectionPostProcessor(**settings)
    
    processed_text = processor.process(text)
    stats = processor.get_stats(text, processed_text)
    
    return processed_text, stats
