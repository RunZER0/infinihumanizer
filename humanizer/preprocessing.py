"""
Pre-Processing Stage: Comprehensive Analysis & Preparation

This module analyzes raw AI-generated text to identify patterns, extract constraints,
and prepare for safe humanization while preserving critical content.
"""

import re
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple, Set

class TextPreprocessor:
    """
    Comprehensive text analysis for safe humanization
    """
    
    def __init__(self):
        """Initialize the preprocessor"""
        self.ai_transitions = [
            'however', 'therefore', 'additionally', 'furthermore', 
            'moreover', 'consequently', 'thus', 'hence', 'nevertheless',
            'nonetheless', 'meanwhile', 'accordingly'
        ]
    
    def preprocess_text(self, text: str, domain: str = "general") -> Dict:
        """
        Comprehensive pre-processing analysis of input text
        
        Args:
            text: The input text to analyze
            domain: Text domain (legal, medical, technical, academic, business, creative, general)
        
        Returns:
            Dict containing analysis results and safe humanization guidelines
        """
        analysis = {
            'original_text': text,
            'domain': domain,
            'preservation_map': self._extract_preservation_elements(text),
            'ai_patterns': self._detect_ai_patterns(text),
            'safe_variation_zones': self._identify_safe_variation_zones(text),
            'humanization_guidelines': {},
            'risk_assessment': {}
        }
        
        # Generate guidelines after initial analysis
        analysis['humanization_guidelines'] = self._generate_humanization_guidelines(
            text, domain, analysis['ai_patterns'], analysis['preservation_map']
        )
        analysis['risk_assessment'] = self._assess_risks(text, domain, analysis['preservation_map'])
        
        return analysis
    
    def _extract_preservation_elements(self, text: str) -> Dict:
        """Extract elements that must be preserved during humanization"""
        preservation = {
            'technical_terms': set(),
            'proper_nouns': set(),
            'numbers_dates': [],
            'acronyms': set(),
            'key_arguments': [],
            'quotes_citations': []
        }
        
        # Extract technical terms (words with capital letters in middle of sentences)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words[1:], 1):  # Skip first word
                if word and len(word) > 3 and word[0].isupper() and not word.isupper():
                    # Not start of sentence
                    if i > 0 and words[i-1] and not words[i-1].endswith(('.', '!', '?')):
                        preservation['technical_terms'].add(word)
        
        # Extract proper nouns using simple pattern matching
        proper_noun_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        preservation['proper_nouns'] = set(re.findall(proper_noun_pattern, text))
        
        # Extract numbers, dates, percentages
        number_patterns = [
            r'\b\d+(?:\.\d+)?%?\b',  # Numbers and percentages
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # Dates
            r'\$\d+(?:,\d+)*(?:\.\d+)?\b'  # Currency
        ]
        for pattern in number_patterns:
            preservation['numbers_dates'].extend(re.findall(pattern, text))
        
        # Extract acronyms (2-5 capital letters)
        acronym_pattern = r'\b[A-Z]{2,5}\b'
        preservation['acronyms'] = set(re.findall(acronym_pattern, text))
        
        # Extract quotes and citations
        quote_pattern = r'"[^"]*"'
        preservation['quotes_citations'] = re.findall(quote_pattern, text)
        
        return preservation
    
    def _detect_ai_patterns(self, text: str) -> Dict:
        """Detect patterns that indicate AI-generated content"""
        patterns = {
            'sentence_length_consistency': self._analyze_sentence_consistency(text),
            'transition_overuse': self._check_transition_overuse(text),
            'vocabulary_repetition': self._analyze_vocabulary_variety(text),
            'perfection_indicators': self._detect_perfection_indicators(text),
            'structural_patterns': self._analyze_structural_patterns(text)
        }
        
        return patterns
    
    def _analyze_sentence_consistency(self, text: str) -> Dict:
        """Analyze sentence length and structure consistency"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if len(sentence_lengths) < 2:
            return {'score': 0, 'issues': [], 'mean_length': 0, 'std_length': 0}
        
        mean_length = np.mean(sentence_lengths)
        std_length = np.std(sentence_lengths)
        
        # AI text tends to have very consistent sentence lengths
        consistency_score = min(std_length / mean_length if mean_length > 0 else 0, 1.0)
        
        issues = []
        if consistency_score < 0.3:  # Very consistent lengths
            issues.append("overly_consistent_sentence_lengths")
        if std_length < 3:  # Very low variation
            issues.append("low_sentence_length_variance")
        
        return {
            'score': consistency_score,
            'mean_length': mean_length,
            'std_length': std_length,
            'issues': issues
        }
    
    def _check_transition_overuse(self, text: str) -> Dict:
        """Check for overuse of AI-favored transition words"""
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {'transition_density': {}, 'overused_transitions': {}, 'issues': []}
        
        transition_counts = {}
        for transition in self.ai_transitions:
            count = words.count(transition)
            if count > 0:
                transition_counts[transition] = count / total_words
        
        overused = {k: v for k, v in transition_counts.items() if v > 0.005}  # >0.5% density
        
        return {
            'transition_density': transition_counts,
            'overused_transitions': overused,
            'issues': list(overused.keys()) if overused else []
        }
    
    def _analyze_vocabulary_variety(self, text: str) -> Dict:
        """Analyze vocabulary repetition and variety"""
        words = [word.lower() for word in re.findall(r'\b\w+\b', text) if len(word) > 3]
        word_freq = Counter(words)
        total_words = len(words)
        unique_words = len(word_freq)
        
        if total_words == 0:
            return {'type_token_ratio': 0, 'repeated_words': {}, 'issues': []}
        
        # Type-token ratio (vocabulary diversity)
        ttr = unique_words / total_words
        
        # Find repeated words (potential AI patterns)
        repeated = {word: count for word, count in word_freq.items() 
                   if count > 2 and count/total_words > 0.02}
        
        issues = []
        if ttr < 0.5:  # Low vocabulary variety
            issues.append("low_vocabulary_diversity")
        if repeated:
            issues.append("word_repetition_patterns")
        
        return {
            'type_token_ratio': ttr,
            'repeated_words': repeated,
            'issues': issues
        }
    
    def _detect_perfection_indicators(self, text: str) -> Dict:
        """Detect linguistic patterns that indicate 'too perfect' writing"""
        # Perfect parallel structure indicators
        parallel_indicators = [
            r'\bnot only.*but also\b',
            r'\bboth.*and\b',
            r'\beither.*or\b',
            r'\bneither.*nor\b'
        ]
        
        perfect_patterns = []
        for pattern in parallel_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                perfect_patterns.append(pattern)
        
        # Overly balanced sentence structures
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        balanced_count = 0
        for sentence in sentences:
            if self._is_overly_balanced(sentence):
                balanced_count += 1
        
        balance_ratio = balanced_count / len(sentences) if sentences else 0
        
        issues = []
        if perfect_patterns:
            issues.append("perfect_parallel_structures")
        if balance_ratio > 0.3:
            issues.append("overly_balanced_sentences")
        
        return {
            'perfect_patterns': perfect_patterns,
            'balance_ratio': balance_ratio,
            'issues': issues
        }
    
    def _is_overly_balanced(self, sentence: str) -> bool:
        """Check if sentence has overly balanced structure"""
        words = sentence.split()
        if len(words) < 8:
            return False
        
        # Check for symmetrical clause structures (simplified)
        comma_count = sentence.count(',')
        if comma_count == 1:
            parts = sentence.split(',')
            if len(parts) == 2:
                left_words = len(parts[0].split())
                right_words = len(parts[1].split())
                # If clauses are very similar in length
                return abs(left_words - right_words) <= 2
        return False
    
    def _analyze_structural_patterns(self, text: str) -> Dict:
        """Analyze paragraph and document structure patterns"""
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        
        issues = []
        
        if len(paragraph_lengths) > 1:
            mean_para_length = np.mean(paragraph_lengths)
            std_para_length = np.std(paragraph_lengths)
            
            if mean_para_length > 0 and std_para_length / mean_para_length < 0.4:
                issues.append("consistent_paragraph_lengths")
        
        # Check for repetitive opening patterns
        sentence_starts = []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        for sentence in sentences[:10]:  # First 10 sentences
            first_word = sentence.split()[0] if sentence.split() else ""
            if first_word:
                sentence_starts.append(first_word.lower())
        
        start_variety = len(set(sentence_starts)) / len(sentence_starts) if sentence_starts else 1.0
        if start_variety < 0.6:
            issues.append("repetitive_sentence_starts")
        
        return {
            'paragraph_analysis': {
                'count': len(paragraphs),
                'length_variance': np.std(paragraph_lengths) if paragraph_lengths else 0,
                'issues': issues
            },
            'sentence_start_variety': start_variety,
            'issues': issues
        }
    
    def _identify_safe_variation_zones(self, text: str) -> List[Dict]:
        """Identify areas where humanization can be safely applied"""
        safe_zones = []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        for i, sentence in enumerate(sentences):
            zone_analysis = {
                'sentence_index': i,
                'sentence': sentence,
                'safe_for_variation': True,
                'variation_types': [],
                'risk_level': 'low',
                'reasoning': []
            }
            
            words = sentence.split()
            
            # High risk if contains technical terms, numbers, or proper nouns
            preservation_elements = self._extract_preservation_elements(sentence)
            if (preservation_elements['technical_terms'] or 
                preservation_elements['numbers_dates'] or
                len(preservation_elements['proper_nouns']) > 2):
                zone_analysis['safe_for_variation'] = False
                zone_analysis['risk_level'] = 'high'
                zone_analysis['reasoning'].append('contains_preservation_elements')
            else:
                # Suggest variation types based on sentence characteristics
                if len(words) > 15:
                    zone_analysis['variation_types'].append('sentence_splitting')
                if len(words) < 25:
                    zone_analysis['variation_types'].append('sentence_combining')
                
                zone_analysis['variation_types'].extend([
                    'transition_variation',
                    'vocabulary_enhancement', 
                    'structural_reordering'
                ])
            
            safe_zones.append(zone_analysis)
        
        return safe_zones
    
    def _generate_humanization_guidelines(self, text: str, domain: str, 
                                         ai_patterns: Dict, preservation: Dict) -> Dict:
        """Generate specific guidelines for humanization based on analysis"""
        guidelines = {
            'preservation_rules': self._create_preservation_rules(preservation),
            'variation_recommendations': self._create_variation_recommendations(ai_patterns),
            'intensity_settings': self._calculate_intensity_settings(ai_patterns, domain),
            'model_specific_instructions': self._generate_model_instructions(ai_patterns)
        }
        
        return guidelines
    
    def _create_preservation_rules(self, preservation: Dict) -> List[str]:
        """Create specific rules for what must be preserved"""
        rules = []
        
        if preservation['technical_terms']:
            terms = ', '.join(list(preservation['technical_terms'])[:5])
            rules.append(f"PRESERVE these technical terms: {terms}")
        
        if preservation['proper_nouns']:
            nouns = ', '.join(list(preservation['proper_nouns'])[:5])
            rules.append(f"NEVER change proper nouns: {nouns}")
        
        if preservation['numbers_dates']:
            nums = ', '.join(preservation['numbers_dates'][:3])
            rules.append(f"Maintain exact numbers/dates: {nums}")
        
        if preservation['acronyms']:
            acr = ', '.join(list(preservation['acronyms']))
            rules.append(f"Keep acronyms unchanged: {acr}")
        
        return rules
    
    def _create_variation_recommendations(self, ai_patterns: Dict) -> List[str]:
        """Create specific recommendations for humanization"""
        recommendations = []
        
        # Based on detected AI patterns
        if 'overly_consistent_sentence_lengths' in ai_patterns['sentence_length_consistency']['issues']:
            recommendations.append("Vary sentence lengths dramatically")
        
        if ai_patterns['transition_overuse']['overused_transitions']:
            overused = list(ai_patterns['transition_overuse']['overused_transitions'].keys())
            recommendations.append(f"Reduce overuse of: {', '.join(overused[:3])}")
        
        if 'low_vocabulary_diversity' in ai_patterns['vocabulary_repetition']['issues']:
            recommendations.append("Increase vocabulary variety and synonyms")
        
        if 'perfect_parallel_structures' in ai_patterns['perfection_indicators']['issues']:
            recommendations.append("Break up perfect parallel structures occasionally")
        
        if 'repetitive_sentence_starts' in ai_patterns['structural_patterns']['issues']:
            recommendations.append("Vary sentence beginnings more")
        
        return recommendations
    
    def _calculate_intensity_settings(self, ai_patterns: Dict, domain: str) -> Dict:
        """Calculate appropriate humanization intensity levels"""
        base_intensity = 0.5  # Default medium
        
        # Adjust based on AI pattern strength
        ai_indicators = 0
        for category in ai_patterns.values():
            ai_indicators += len(category.get('issues', []))
        
        # More AI patterns = higher intensity needed
        if ai_indicators > 3:
            base_intensity = 0.8
        elif ai_indicators < 2:
            base_intensity = 0.3
        
        # Domain-based adjustments
        domain_intensity = {
            'legal': 0.3,
            'medical': 0.2,
            'technical': 0.4,
            'academic': 0.6,
            'business': 0.7,
            'creative': 0.9,
            'general': 0.5
        }
        
        final_intensity = min(base_intensity, domain_intensity.get(domain, 0.5))
        
        return {
            'overall_intensity': final_intensity,
            'sentence_variation_intensity': min(final_intensity * 1.2, 1.0),  # Higher for sentences
            'vocabulary_intensity': final_intensity * 0.8,  # Lower for vocabulary
            'structural_intensity': final_intensity
        }
    
    def _generate_model_instructions(self, ai_patterns: Dict) -> Dict:
        """Generate model-specific instructions based on analysis"""
        instructions = {
            'chatgpt': self._chatgpt_instructions(ai_patterns),
            'deepseek': self._deepseek_instructions(ai_patterns),
            'claude': self._claude_instructions(ai_patterns)
        }
        return instructions
    
    def _chatgpt_instructions(self, ai_patterns: Dict) -> str:
        """GPT-specific instructions (more explicit)"""
        instructions = "Focus on breaking perfect patterns while maintaining professionalism. "
        
        if 'overly_consistent_sentence_lengths' in ai_patterns['sentence_length_consistency']['issues']:
            instructions += "Specifically vary sentence lengths more dramatically. "
        
        if ai_patterns['transition_overuse']['overused_transitions']:
            instructions += "Use alternative transition words and phrases. "
        
        return instructions
    
    def _deepseek_instructions(self, ai_patterns: Dict) -> str:
        """DeepSeek-specific instructions (more flexible)"""
        instructions = "Introduce natural human writing patterns including slight imperfections. "
        instructions += "Focus on making it sound authentically human rather than perfectly optimized. "
        return instructions

    def _claude_instructions(self, ai_patterns: Dict) -> str:
        """Claude-specific instructions"""
        instructions = "Preserve nuance and intent while loosening overly formal phrasing. "
        overused = ai_patterns.get('transition_overuse', {}).get('overused_transitions')
        if overused:
            instructions += "Use more grounded connectors instead of repetitive transitions. "
        instructions += "Keep the tone conversational-professional with slight personal voice. "
        return instructions
    
    def _assess_risks(self, text: str, domain: str, preservation: Dict) -> Dict:
        """Assess potential risks in humanization"""
        risks = {
            'high_risk_elements': [],
            'medium_risk_elements': [],
            'recommended_precautions': []
        }
        
        # High risk: Technical content, legal terms, medical information
        if domain in ['legal', 'medical', 'technical']:
            risks['high_risk_elements'].append(f"{domain}_specific_terminology")
            risks['recommended_precautions'].append("Minimal semantic changes in high-risk domains")
        
        if preservation['technical_terms']:
            risks['medium_risk_elements'].append("technical_terms_present")
            risks['recommended_precautions'].append("Preserve technical terms exactly")
        
        if preservation['numbers_dates']:
            risks['high_risk_elements'].append("numerical_data_present")
            risks['recommended_precautions'].append("Never alter numbers, dates, or statistical data")
        
        if preservation['quotes_citations']:
            risks['high_risk_elements'].append("quotes_present")
            risks['recommended_precautions'].append("Keep all quoted material unchanged")
        
        return risks
    
    def generate_summary_report(self, analysis: Dict) -> str:
        """Generate a human-readable summary of the analysis"""
        report = []
        report.append("=== PRE-PROCESSING ANALYSIS REPORT ===\n")
        report.append(f"Domain: {analysis['domain']}")
        report.append(f"Text length: {len(analysis['original_text'].split())} words\n")
        
        # Preservation elements
        pres = analysis['preservation_map']
        report.append("PRESERVATION ELEMENTS:")
        report.append(f"  - Technical terms: {len(pres['technical_terms'])}")
        report.append(f"  - Proper nouns: {len(pres['proper_nouns'])}")
        report.append(f"  - Numbers/dates: {len(pres['numbers_dates'])}")
        report.append(f"  - Acronyms: {len(pres['acronyms'])}\n")
        
        # AI patterns
        total_issues = sum(len(v.get('issues', [])) for v in analysis['ai_patterns'].values())
        report.append(f"AI PATTERNS DETECTED: {total_issues} issues")
        for category, data in analysis['ai_patterns'].items():
            if data.get('issues'):
                report.append(f"  - {category}: {', '.join(data['issues'])}")
        report.append("")
        
        # Safe zones
        safe_zones = analysis['safe_variation_zones']
        safe_count = len([z for z in safe_zones if z['safe_for_variation']])
        report.append(f"SAFE VARIATION ZONES: {safe_count}/{len(safe_zones)} sentences")
        
        # Intensity
        intensity = analysis['humanization_guidelines']['intensity_settings']
        report.append(f"RECOMMENDED INTENSITY: {intensity['overall_intensity']:.2f}\n")
        
        # Recommendations
        if analysis['humanization_guidelines']['variation_recommendations']:
            report.append("RECOMMENDATIONS:")
            for rec in analysis['humanization_guidelines']['variation_recommendations']:
                report.append(f"  • {rec}")
        
        return '\n'.join(report)


# Demo usage
def demonstrate_preprocessing():
    """Demonstrate the preprocessor with sample text"""
    preprocessor = TextPreprocessor()
    
    sample_text = """
    Artificial intelligence systems have revolutionized numerous industries. However, these systems require substantial computational resources. Additionally, they must be trained on extensive datasets. Therefore, organizations should carefully consider implementation costs. Furthermore, ethical considerations remain paramount in AI deployment.
    """
    
    analysis = preprocessor.preprocess_text(sample_text, domain="business")
    report = preprocessor.generate_summary_report(analysis)
    
    print(report)
    print("\n=== DETAILED ANALYSIS STRUCTURE ===")
    print(f"Available keys: {list(analysis.keys())}")
    
    return analysis


if __name__ == "__main__":
    demonstrate_preprocessing()
