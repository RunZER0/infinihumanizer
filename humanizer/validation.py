"""
POST-PROCESSING & QUALITY VALIDATION ENGINE
Aggressive quality control that ensures humanized text maintains professional standards while beating AI detection.
This stage acts as the "gatekeeper" to catch any humanization that went too far.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter


class HumanizationValidator:
    """Comprehensive validation system for humanized text quality"""
    
    def __init__(self):
        self.quality_thresholds = self._define_quality_standards()
    
    def _define_quality_standards(self) -> Dict:
        """Define what constitutes acceptable humanized text"""
        return {
            'readability_score': {'min': 40, 'max': 80},  # Flesch reading ease
            'grammar_errors': {'max_per_100_words': 2},
            'preservation_violations': {'max': 0},
            'professional_tone': {'min_score': 8},  # 1-10 scale
            'logical_consistency': {'min_score': 9},
            'ai_detection_risk': {'max_probability': 0.3}  # 30% max AI probability
        }
    
    def validate_humanization(
        self,
        original: str,
        humanized: str,
        preservation_map: Dict | None,
    ) -> Dict:
        """
        Comprehensive validation of humanized text
        Returns: Validation report with pass/fail and fixes needed
        """
        preservation_map = preservation_map or {}

        validation_report = {
            'overall_score': 0,
            'passed_validation': False,
            'quality_metrics': {},
            'detected_issues': [],
            'required_fixes': [],
            'final_text': humanized,
            'risk_assessment': {}
        }
        
        # Run all validation checks
        quality_metrics = self._calculate_quality_metrics(humanized)
        validation_report['quality_metrics'] = quality_metrics
        
        # Check 1: Preservation Compliance
        preservation_issues = self._check_preservation_compliance(original, humanized, preservation_map)
        if preservation_issues:
            validation_report['detected_issues'].extend(preservation_issues)
            validation_report['required_fixes'].append("RESTORE_PRESERVED_ELEMENTS")
        
        # Check 2: Grammar & Readability
        grammar_issues = self._check_grammar_readability(humanized, quality_metrics)
        if grammar_issues:
            validation_report['detected_issues'].extend(grammar_issues)
            validation_report['required_fixes'].append("FIX_GRAMMAR_READABILITY")
        
        # Check 3: Professional Tone
        tone_issues = self._check_professional_tone(humanized, original)
        if tone_issues:
            validation_report['detected_issues'].extend(tone_issues)
            validation_report['required_fixes'].append("ADJUST_TONE")
        
        # Check 4: Logical Consistency
        logic_issues = self._check_logical_consistency(original, humanized)
        if logic_issues:
            validation_report['detected_issues'].extend(logic_issues)
            validation_report['required_fixes'].append("RESTORE_LOGIC")
        
        # Check 5: AI Detection Risk
        detection_risk = self._assess_detection_risk(humanized, original)
        validation_report['risk_assessment'] = detection_risk
        if detection_risk['ai_probability'] > 0.3:
            validation_report['detected_issues'].append("HIGH_AI_DETECTION_RISK")
            validation_report['required_fixes'].append("ENHANCE_HUMANIZATION")
        
        # Calculate overall score
        validation_report['overall_score'] = self._calculate_overall_score(validation_report)
        validation_report['passed_validation'] = self._determine_pass_fail(validation_report)
        
        # Apply fixes if needed
        if not validation_report['passed_validation'] and validation_report['required_fixes']:
            validation_report['final_text'] = self._apply_automated_fixes(
                original, humanized, validation_report['required_fixes'], preservation_map
            )
        
        return validation_report
    
    def _check_preservation_compliance(self, original: str, humanized: str, preservation_map: Dict) -> List[str]:
        """Check if critical elements were preserved"""
        issues = []
        
        # Check technical terms
        for term in preservation_map.get('technical_terms', []):
            if term in original and term not in humanized:
                issues.append(f"Technical term missing: {term}")
        
        # Check proper nouns
        for noun in preservation_map.get('proper_nouns', []):
            if noun in original and noun not in humanized:
                issues.append(f"Proper noun missing: {noun}")
        
        # Check numbers and dates
        for number in preservation_map.get('numbers_dates', []):
            if str(number) in original and str(number) not in humanized:
                issues.append(f"Number/date altered: {number}")
        
        # Check acronyms
        for acronym in preservation_map.get('acronyms', []):
            if acronym in original and acronym not in humanized:
                issues.append(f"Acronym missing: {acronym}")
        
        return issues
    
    def _check_grammar_readability(self, text: str, metrics: Dict) -> List[str]:
        """Check for grammar issues and readability problems"""
        issues = []
        
        # Check for obvious grammar errors
        grammar_errors = self._detect_obvious_grammar_errors(text)
        word_count = metrics.get('word_count', 1)
        error_rate = (grammar_errors / word_count) * 100
        
        if error_rate > self.quality_thresholds['grammar_errors']['max_per_100_words']:
            issues.append(f"Excessive grammar errors: {error_rate:.1f} per 100 words")
        
        # Check readability
        readability_score = self._calculate_readability(text)
        if readability_score < self.quality_thresholds['readability_score']['min']:
            issues.append(f"Poor readability: score {readability_score:.1f}")
        if readability_score > self.quality_thresholds['readability_score']['max']:
            issues.append(f"Overly simplistic: score {readability_score:.1f}")
        
        # Check sentence structure issues
        structure_issues = self._check_sentence_structure(text)
        if structure_issues:
            issues.extend(structure_issues)
        
        return issues
    
    def _check_professional_tone(self, humanized: str, original: str) -> List[str]:
        """Ensure professional tone is maintained"""
        issues = []
        
        # Check for overly casual language
        casual_indicators = [
            'like', 'you know', 'i mean', 'sort of', 'kind of', 
            'pretty much', 'basically', 'actually', 'stuff', 'things',
            'gonna', 'wanna', 'gotta', 'yeah', 'yep', 'nope'
        ]
        
        humanized_lower = humanized.lower()
        original_lower = original.lower()
        
        casual_count = sum(1 for word in casual_indicators if f' {word} ' in f' {humanized_lower} ')
        original_casual_count = sum(1 for word in casual_indicators if f' {word} ' in f' {original_lower} ')
        
        if casual_count > original_casual_count + 2:  # Allow some increase but not too much
            issues.append(f"Overly casual language introduced: {casual_count - original_casual_count} casual phrases")
        
        # Check tone consistency
        tone_score = self._assess_tone_consistency(original, humanized)
        if tone_score < self.quality_thresholds['professional_tone']['min_score']:
            issues.append(f"Professional tone compromised: score {tone_score}/10")
        
        return issues
    
    def _check_logical_consistency(self, original: str, humanized: str) -> List[str]:
        """Ensure logical flow and argument structure are preserved"""
        issues = []
        
        # Check if key arguments are maintained
        original_key_points = self._extract_key_arguments(original)
        humanized_key_points = self._extract_key_arguments(humanized)
        
        # Calculate semantic similarity (simplified)
        missing_points = []
        for orig_point in original_key_points:
            if not any(self._calculate_similarity(orig_point, hum_point) > 0.5 
                      for hum_point in humanized_key_points):
                missing_points.append(orig_point[:50] + "...")
        
        if missing_points:
            issues.append(f"Key arguments missing or altered: {len(missing_points)} points")
        
        # Check logical flow
        flow_issues = self._assess_logical_flow(humanized)
        if flow_issues:
            issues.append(f"Logical flow disruptions: {', '.join(flow_issues[:2])}")
        
        return issues
    
    def _assess_detection_risk(self, humanized: str, original: str) -> Dict:
        """Assess risk of AI detection using pattern analysis"""
        
        risk_factors = {
            'perplexity_score': self._calculate_perplexity_score(humanized),
            'burstiness_score': self._calculate_burstiness_score(humanized),
            'consistency_patterns': self._check_consistency_patterns(humanized),
            'transition_patterns': self._analyze_transition_patterns(humanized),
            'vocabulary_variety': self._calculate_vocabulary_variety(humanized)
        }
        
        # Calculate overall AI probability
        ai_probability = self._calculate_ai_probability(risk_factors)
        
        return {
            'ai_probability': ai_probability,
            'risk_factors': risk_factors,
            'risk_level': 'HIGH' if ai_probability > 0.3 else 'MEDIUM' if ai_probability > 0.15 else 'LOW'
        }
    
    def _calculate_perplexity_score(self, text: str) -> float:
        """Calculate perplexity (word predictability) - lower is more AI-like"""
        words = text.lower().split()
        if len(words) < 10:
            return 0.5
        
        # Count AI-common phrases
        ai_phrases = [
            'in order to', 'it is important', 'additionally', 'furthermore',
            'moreover', 'in conclusion', 'it should be noted', 'it is worth noting'
        ]
        
        ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text.lower())
        
        # Calculate vocabulary diversity
        unique_words = len(set(words))
        vocabulary_diversity = unique_words / len(words)
        
        # Lower score = more predictable (AI-like)
        return vocabulary_diversity - (ai_phrase_count * 0.05)
    
    def _calculate_burstiness_score(self, text: str) -> float:
        """Calculate sentence length variation (burstiness) - higher is more human"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 3:
            return 0.5
        
        sentence_lengths = [len(s.split()) for s in sentences]
        mean_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Calculate standard deviation
        variance = sum((x - mean_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5
        
        # Coefficient of variation (normalized standard deviation)
        cv = std_dev / mean_length if mean_length > 0 else 0
        
        return min(cv, 1.0)  # Cap at 1.0
    
    def _check_consistency_patterns(self, text: str) -> List[str]:
        """Check for patterns that indicate AI consistency"""
        patterns = []
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 5:
            return patterns
        
        # Check sentence start diversity
        sentence_starts = [s.split()[0].lower() if s.split() else '' for s in sentences[:10]]
        start_variety = len(set(sentence_starts)) / len(sentence_starts) if sentence_starts else 1.0
        
        if start_variety < 0.6:
            patterns.append("repetitive_sentence_starts")
        
        # Check for overly consistent sentence structure
        sentence_structures = []
        for sent in sentences[:10]:
            words = sent.split()
            if len(words) > 3:
                structure = f"{words[0].lower()}_{len(words)}"
                sentence_structures.append(structure)
        
        structure_variety = len(set(sentence_structures)) / len(sentence_structures) if sentence_structures else 1.0
        if structure_variety < 0.5:
            patterns.append("repetitive_structure")
        
        return patterns
    
    def _analyze_transition_patterns(self, text: str) -> List[str]:
        """Analyze transition word usage patterns"""
        ai_transitions = [
            'however', 'therefore', 'additionally', 'furthermore', 
            'moreover', 'consequently', 'nevertheless', 'thus'
        ]
        
        text_lower = text.lower()
        transition_counts = {trans: text_lower.count(trans) for trans in ai_transitions}
        
        # Flag transitions used more than twice
        overused = [trans for trans, count in transition_counts.items() if count > 2]
        
        return overused
    
    def _calculate_vocabulary_variety(self, text: str) -> float:
        """Calculate vocabulary variety (Type-Token Ratio)"""
        words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words
    
    def _calculate_ai_probability(self, risk_factors: Dict) -> float:
        """Calculate overall AI detection probability"""
        score = 0.0
        
        # Low burstiness increases AI probability
        burstiness = risk_factors['burstiness_score']
        if burstiness < 0.3:
            score += 0.3
        elif burstiness < 0.5:
            score += 0.15
        
        # High consistency patterns increase AI probability
        consistency_issues = len(risk_factors['consistency_patterns'])
        score += consistency_issues * 0.1
        
        # Overused transitions increase AI probability
        overused_transitions = len(risk_factors['transition_patterns'])
        score += min(overused_transitions * 0.05, 0.15)
        
        # Low vocabulary variety increases AI probability
        vocab_variety = risk_factors['vocabulary_variety']
        if vocab_variety < 0.4:
            score += 0.2
        elif vocab_variety < 0.5:
            score += 0.1
        
        # Low perplexity increases AI probability
        perplexity = risk_factors['perplexity_score']
        if perplexity < 0.3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _apply_automated_fixes(self, original: str, humanized: str, fixes_needed: List[str], 
                               preservation_map: Dict) -> str:
        """Apply automated fixes to address validation issues"""
        fixed_text = humanized
        
        for fix_type in fixes_needed:
            if fix_type == "RESTORE_PRESERVED_ELEMENTS":
                fixed_text = self._restore_preserved_elements(original, fixed_text, preservation_map)
            elif fix_type == "FIX_GRAMMAR_READABILITY":
                fixed_text = self._fix_grammar_readability(fixed_text)
            elif fix_type == "ADJUST_TONE":
                fixed_text = self._adjust_tone(fixed_text, original)
            elif fix_type == "RESTORE_LOGIC":
                fixed_text = self._restore_logic(original, fixed_text)
            elif fix_type == "ENHANCE_HUMANIZATION":
                fixed_text = self._enhance_humanization(fixed_text)
        
        return fixed_text
    
    def _restore_preserved_elements(self, original: str, humanized: str, preservation_map: Dict) -> str:
        """Restore critical elements that were incorrectly modified"""
        fixed_text = humanized
        
        # Restore technical terms
        for term in preservation_map.get('technical_terms', []):
            if term in original and term not in fixed_text:
                # Try to find and replace similar terms
                term_lower = term.lower()
                words = fixed_text.split()
                for i, word in enumerate(words):
                    if word.lower() == term_lower or self._calculate_similarity(word.lower(), term_lower) > 0.8:
                        words[i] = term
                fixed_text = ' '.join(words)
        
        # Restore numbers and dates
        original_numbers = re.findall(r'\b\d+(?:\.\d+)?(?:%|°|km|kg|m|cm|mm)?\b', original)
        humanized_numbers = re.findall(r'\b\d+(?:\.\d+)?(?:%|°|km|kg|m|cm|mm)?\b', fixed_text)
        
        # If numbers are missing, try to restore them from context
        if len(original_numbers) > len(humanized_numbers):
            for num in original_numbers:
                if num not in fixed_text:
                    # Find approximate location and restore
                    fixed_text = fixed_text  # Simplified - would need more sophisticated restoration
        
        return fixed_text
    
    def _fix_grammar_readability(self, text: str) -> str:
        """Fix obvious grammar and readability issues"""
        fixes = [
            (r'\bthey is\b', 'they are'),
            (r'\bwe has\b', 'we have'),
            (r'\bhe don\'t\b', 'he doesn\'t'),
            (r'\bshe don\'t\b', 'she doesn\'t'),
            (r'\bit don\'t\b', 'it doesn\'t'),
            (r', ,', ','),
            (r'\.\.\.\.+', '...'),
            (r'\s+([,.!?])', r'\1'),  # Remove space before punctuation
            (r'([,.!?])([A-Za-z])', r'\1 \2'),  # Add space after punctuation
            (r'\s+', ' '),  # Multiple spaces to single space
            (r'^\s+|\s+$', ''),  # Trim whitespace
        ]
        
        fixed_text = text
        for pattern, replacement in fixes:
            fixed_text = re.sub(pattern, replacement, fixed_text)
        
        return fixed_text
    
    def _adjust_tone(self, text: str, original: str) -> str:
        """Adjust tone to be more professional if needed"""
        casual_replacements = {
            ' like,': ',',
            ' you know,': ',',
            ' i mean,': ',',
            ' sort of ': ' somewhat ',
            ' kind of ': ' rather ',
            ' stuff ': ' elements ',
            ' things ': ' aspects ',
            ' gonna ': ' going to ',
            ' wanna ': ' want to ',
            ' gotta ': ' must ',
        }
        
        fixed_text = text
        for casual, professional in casual_replacements.items():
            fixed_text = fixed_text.replace(casual, professional)
        
        return fixed_text
    
    def _restore_logic(self, original: str, humanized: str) -> str:
        """Restore logical consistency - simplified implementation"""
        # This would need more sophisticated NLP to truly restore logic
        # For now, just ensure key sentences are present
        return humanized
    
    def _enhance_humanization(self, text: str) -> str:
        """Apply additional humanization to beat detectors"""
        sentences = [s.strip() for s in re.split(r'([.!?]+)', text) if s.strip()]
        
        # Rebuild with punctuation
        rebuilt = []
        for i in range(0, len(sentences), 2):
            sent = sentences[i]
            punct = sentences[i+1] if i+1 < len(sentences) else '.'
            rebuilt.append(sent + punct)
        
        # Add burstiness by varying sentence combinations
        if len(rebuilt) > 3:
            # Occasionally merge short sentences
            for i in range(len(rebuilt) - 1):
                words_current = len(rebuilt[i].split())
                words_next = len(rebuilt[i+1].split())
                if words_current < 8 and words_next < 8 and i % 3 == 0:
                    rebuilt[i] = rebuilt[i].rstrip('.!?') + ', ' + rebuilt[i+1][0].lower() + rebuilt[i+1][1:]
                    rebuilt[i+1] = ''
        
        return ' '.join([s for s in rebuilt if s])
    
    # Helper methods
    
    def _calculate_quality_metrics(self, text: str) -> Dict:
        """Calculate comprehensive quality metrics"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        return {
            'readability_score': self._calculate_readability(text),
            'grammar_errors': self._detect_obvious_grammar_errors(text),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0
        }
    
    def _detect_obvious_grammar_errors(self, text: str) -> int:
        """Detect obvious grammar errors"""
        error_count = 0
        
        # Common grammar errors
        error_patterns = [
            r'\bthey is\b', r'\bwe has\b', r'\bhe don\'t\b', r'\bshe don\'t\b',
            r'\bit don\'t\b', r'\bi is\b', r'\byou is\b', r',  ,', r'\.\.',
            r'\s+[,.!?]', r'[,.!?][A-Za-z]'
        ]
        
        for pattern in error_patterns:
            error_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return error_count
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate Flesch Reading Ease score (simplified)"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return 50.0
        
        # Count syllables (simplified - count vowel groups)
        syllables = 0
        for word in words:
            syllables += max(1, len(re.findall(r'[aeiouy]+', word.lower())))
        
        # Flesch Reading Ease formula
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0, min(100, score))
    
    def _check_sentence_structure(self, text: str) -> List[str]:
        """Check for sentence structure issues"""
        issues = []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Check for overly long sentences
        for sent in sentences:
            words = sent.split()
            if len(words) > 50:
                issues.append(f"Overly long sentence: {len(words)} words")
        
        # Check for sentence fragments (very short)
        fragment_count = sum(1 for sent in sentences if len(sent.split()) < 3)
        if fragment_count > len(sentences) * 0.2:  # More than 20% fragments
            issues.append(f"Too many sentence fragments: {fragment_count}")
        
        return issues
    
    def _assess_tone_consistency(self, original: str, humanized: str) -> int:
        """Assess tone consistency on 1-10 scale"""
        # Simplified tone assessment based on formality markers
        formal_markers = ['however', 'therefore', 'furthermore', 'consequently']
        casual_markers = ['like', 'you know', 'sort of', 'kind of', 'stuff']
        
        orig_formal = sum(1 for marker in formal_markers if marker in original.lower())
        orig_casual = sum(1 for marker in casual_markers if marker in original.lower())
        
        hum_formal = sum(1 for marker in formal_markers if marker in humanized.lower())
        hum_casual = sum(1 for marker in casual_markers if marker in humanized.lower())
        
        # Calculate tone shift
        formal_shift = abs(orig_formal - hum_formal)
        casual_shift = abs(orig_casual - hum_casual)
        
        # Score: 10 = perfect consistency, 0 = completely different tone
        tone_score = 10 - min(10, (formal_shift + casual_shift) * 2)
        
        return max(1, tone_score)
    
    def _extract_key_arguments(self, text: str) -> List[str]:
        """Extract key arguments/sentences from text"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Return sentences longer than 10 words (likely substantive)
        key_sentences = [s for s in sentences if len(s.split()) >= 10]
        
        return key_sentences[:5]  # Top 5 key sentences
    
    def _assess_logical_flow(self, text: str) -> List[str]:
        """Assess logical flow issues"""
        issues = []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Check for contradictory transitions
        contradiction_patterns = [
            ('however', 'and also'),
            ('but', 'therefore'),
            ('although', 'thus')
        ]
        
        for sent in sentences:
            sent_lower = sent.lower()
            for pattern1, pattern2 in contradiction_patterns:
                if pattern1 in sent_lower and pattern2 in sent_lower:
                    issues.append("contradictory_transitions")
        
        return issues
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts (0-1)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_overall_score(self, report: Dict) -> float:
        """Calculate overall validation score"""
        base_score = 85.0
        
        # Deduct for issues
        issue_penalty = len(report['detected_issues']) * 5
        
        # Bonus for good metrics
        metrics = report['quality_metrics']
        if 50 <= metrics.get('readability_score', 0) <= 70:
            base_score += 5
        if metrics.get('vocabulary_diversity', 0) > 0.5:
            base_score += 5
        
        # Penalty for high AI risk
        risk_level = report['risk_assessment'].get('risk_level', 'LOW')
        if risk_level == 'HIGH':
            base_score -= 15
        elif risk_level == 'MEDIUM':
            base_score -= 5
        
        final_score = max(0, base_score - issue_penalty)
        return min(100, final_score)
    
    def _determine_pass_fail(self, report: Dict) -> bool:
        """Determine if validation passes"""
        # Must meet all critical criteria
        passes = (
            report['overall_score'] >= 70 and
            not any(issue.startswith('HIGH_') for issue in report['detected_issues']) and
            'RESTORE_PRESERVED_ELEMENTS' not in report['required_fixes'] and
            report['risk_assessment'].get('risk_level') != 'HIGH'
        )
        
        return passes


# FINAL QUALITY CONTROL PROMPT FOR LLM-BASED REPAIR
QUALITY_CONTROL_PROMPT = """
YOU ARE THE FINAL QUALITY GATE. FIX ANY HUMANIZATION THAT WENT TOO FAR.

# MISSION: REPAIR OVER-HUMANIZED TEXT WHILE PRESERVING HUMAN-LIKE QUALITIES

## CRITICAL REPAIR COMMANDS:

1. **GRAMMAR & CLARITY FIXES:**
   - FIX ANY GRAMMAR ERRORS THAT BREAK READABILITY
   - REPAIR SENTENCE FRAGMENTS THAT CREATE CONFUSION
   - ENSURE ALL SENTENCES ARE COMPREHENSIBLE
   - MAINTAIN PROFESSIONAL SENTENCE STRUCTURE

2. **LOGICAL FLOW REPAIR:**
   - ENSURE ARGUMENTS FLOW LOGICALLY
   - FIX ANY CONTRADICTIONS INTRODUCED DURING HUMANIZATION
   - MAINTAIN COHERENT PARAGRAPH STRUCTURE
   - PRESERVE ORIGINAL DOCUMENT INTENT

3. **TONE ADJUSTMENT:**
   - REMOVE OVERLY CASUAL LANGUAGE THAT BREAKS PROFESSIONALISM
   - ENSURE TONE MATCHES ORIGINAL INTENT
   - KEEP HUMAN-LIKE QUALITIES BUT MAINTAIN STANDARDS
   - BALANCE AUTHENTICITY WITH PROFESSIONALISM

4. **PRESERVATION VERIFICATION:**
   - VERIFY ALL TECHNICAL TERMS ARE CORRECT
   - ENSURE NUMBERS AND DATES ARE ACCURATE
   - CHECK PROPER NOUNS ARE UNCHANGED
   - CONFIRM CORE ARGUMENTS ARE INTACT

## DETECTED ISSUES:
{issues}

## TEXT TO REPAIR:
{text}

## ORIGINAL REFERENCE (for context):
{original}

## OUTPUT:
RETURN ONLY THE REPAIRED TEXT THAT BALANCES HUMAN-LIKE QUALITIES WITH PROFESSIONAL STANDARDS.
DO NOT ADD EXPLANATIONS OR META-COMMENTARY.
"""


def demonstrate_validation():
    """Demonstration of validation system"""
    validator = HumanizationValidator()
    
    original = "AI systems require substantial computational resources. However, they provide significant benefits for data analysis and pattern recognition."
    
    # Example of over-humanized text
    humanized = "AI systems need lots of computing power, you know? But like, they're really good for analyzing data and stuff and finding patterns."
    
    preservation_map = {
        'technical_terms': ['AI', 'data analysis', 'pattern recognition'],
        'proper_nouns': [],
        'numbers_dates': [],
        'acronyms': ['AI']
    }
    
    report = validator.validate_humanization(original, humanized, preservation_map)
    
    print("=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    print(f"Passed: {report['passed_validation']}")
    print(f"Overall Score: {report['overall_score']}/100")
    print(f"\nQuality Metrics:")
    for key, value in report['quality_metrics'].items():
        print(f"  {key}: {value}")
    print(f"\nDetected Issues: {len(report['detected_issues'])}")
    for issue in report['detected_issues']:
        print(f"  - {issue}")
    print(f"\nRequired Fixes: {report['required_fixes']}")
    print(f"\nAI Detection Risk: {report['risk_assessment']['risk_level']} "
          f"({report['risk_assessment']['ai_probability']:.1%})")
    print(f"\nOriginal Text:\n{original}")
    print(f"\nHumanized Text:\n{humanized}")
    print(f"\nFixed Text:\n{report['final_text']}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    demonstrate_validation()
