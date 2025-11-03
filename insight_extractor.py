"""
AI-Powered Insight Extractor for Long-term Memory

This module analyzes chat messages and automatically extracts key insights
that should be remembered long-term (beyond the 10-message context window).

Insight Types:
- stressor: New stress sources mentioned (teacher, exam, conflict, etc.)
- breakthrough: Positive moments, realizations, improvements
- support_need: Explicit requests for help or concerning patterns
- milestone: Important achievements or progress markers
- crisis: Urgent situations requiring immediate attention
"""

from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime


class InsightExtractor:
    """
    Extracts key insights from chat messages for long-term memory.
    """
    
    def __init__(self):
        """Initialize with keyword patterns for different insight types"""
        
        # Stressor detection patterns
        self.stressor_patterns = {
            'academic': ['exam', 'test', 'quiz', 'deadline', 'assignment', 'homework', 'study', 'grade', 'fail'],
            'social': ['fight', 'argument', 'lonely', 'isolated', 'bullied', 'rejected', 'broke up', 'breakup'],
            'authority': ['teacher', 'professor', 'parent', 'boss', 'scolded', 'yelled', 'criticized'],
            'health': ['sick', 'pain', 'injury', 'hospital', 'doctor', 'medication'],
            'sleep': ['insomnia', 'can\'t sleep', 'no sleep', 'sleepless', 'tired', 'exhausted'],
            'financial': ['money', 'broke', 'debt', 'can\'t afford', 'expensive', 'bills']
        }
        
        # Breakthrough detection patterns
        self.breakthrough_patterns = [
            'i understand', 'i realize', 'i get it now', 'makes sense',
            'feeling better', 'helped me', 'worked', 'progress',
            'breakthrough', 'clarity', 'clearer now'
        ]
        
        # Support need detection patterns
        self.support_need_patterns = [
            'help me', 'i need', 'struggling', 'don\'t know what to do',
            'lost', 'confused', 'overwhelmed', 'too much', 'can\'t handle',
            'giving up', 'want to quit'
        ]
        
        # Milestone detection patterns
        self.milestone_patterns = [
            'completed', 'finished', 'achieved', 'accomplished', 'succeeded',
            'first time', 'milestone', 'proud', 'celebration', 'victory'
        ]
        
        # Crisis detection patterns (HIGH PRIORITY)
        self.crisis_patterns = [
            'hurt myself', 'harm myself', 'kill myself', 'suicide', 'end it',
            'want to die', 'better off dead', 'can\'t go on', 'no point',
            'self harm', 'cutting'
        ]
    
    def extract_insights(
        self,
        user_message: str,
        ai_response: str,
        timestamp: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Extract all relevant insights from a conversation exchange.
        
        Args:
            user_message: Message from user
            ai_response: AI's response
            timestamp: When this conversation happened (defaults to now)
        
        Returns:
            List of insights: [{"type": "stressor", "content": "...", "original_message": "..."}, ...]
        """
        timestamp = timestamp or datetime.utcnow().isoformat()
        insights = []
        
        message_lower = user_message.lower()
        
        # 1. CRISIS DETECTION (HIGHEST PRIORITY)
        crisis_insight = self._detect_crisis(user_message, message_lower, timestamp)
        if crisis_insight:
            insights.append(crisis_insight)
            return insights  # Return immediately for crisis situations
        
        # 2. STRESSOR DETECTION
        stressor_insights = self._detect_stressors(user_message, message_lower, timestamp)
        insights.extend(stressor_insights)
        
        # 3. BREAKTHROUGH DETECTION
        breakthrough_insight = self._detect_breakthrough(user_message, message_lower, timestamp)
        if breakthrough_insight:
            insights.append(breakthrough_insight)
        
        # 4. SUPPORT NEED DETECTION
        support_insight = self._detect_support_need(user_message, message_lower, timestamp)
        if support_insight:
            insights.append(support_insight)
        
        # 5. MILESTONE DETECTION
        milestone_insight = self._detect_milestone(user_message, message_lower, timestamp)
        if milestone_insight:
            insights.append(milestone_insight)
        
        return insights
    
    def _detect_crisis(self, message: str, message_lower: str, timestamp: str) -> Optional[Dict[str, str]]:
        """Detect crisis situations requiring immediate attention"""
        for pattern in self.crisis_patterns:
            if pattern in message_lower:
                return {
                    'type': 'crisis',
                    'content': f'CRISIS: User expressed concerning thoughts - immediate support needed',
                    'original_message': message,
                    'timestamp': timestamp,
                    'priority': 'URGENT'
                }
        return None
    
    def _detect_stressors(self, message: str, message_lower: str, timestamp: str) -> List[Dict[str, str]]:
        """Detect new stressors mentioned in the message"""
        insights = []
        
        for category, keywords in self.stressor_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Extract context around the keyword (30 chars before/after)
                    match = re.search(rf'.{{0,30}}{re.escape(keyword)}.{{0,30}}', message_lower)
                    if match:
                        context = match.group(0).strip()
                        
                        # Create insight
                        insight = {
                            'type': 'stressor',
                            'content': f'{category.title()} stress detected: {context}',
                            'original_message': message,
                            'timestamp': timestamp,
                            'category': category
                        }
                        insights.append(insight)
                        break  # Only one insight per category per message
        
        return insights
    
    def _detect_breakthrough(self, message: str, message_lower: str, timestamp: str) -> Optional[Dict[str, str]]:
        """Detect positive breakthroughs or realizations"""
        for pattern in self.breakthrough_patterns:
            if pattern in message_lower:
                # Extract the sentence containing the breakthrough
                sentences = message.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        return {
                            'type': 'breakthrough',
                            'content': f'Positive realization: {sentence.strip()}',
                            'original_message': message,
                            'timestamp': timestamp
                        }
        return None
    
    def _detect_support_need(self, message: str, message_lower: str, timestamp: str) -> Optional[Dict[str, str]]:
        """Detect when user explicitly needs support"""
        for pattern in self.support_need_patterns:
            if pattern in message_lower:
                return {
                    'type': 'support_need',
                    'content': f'User expressed need for support',
                    'original_message': message,
                    'timestamp': timestamp
                }
        return None
    
    def _detect_milestone(self, message: str, message_lower: str, timestamp: str) -> Optional[Dict[str, str]]:
        """Detect achievements and milestones"""
        for pattern in self.milestone_patterns:
            if pattern in message_lower:
                # Extract the achievement context
                sentences = message.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        return {
                            'type': 'milestone',
                            'content': f'Achievement: {sentence.strip()}',
                            'original_message': message,
                            'timestamp': timestamp
                        }
        return None
    
    def should_save_insight(self, insight: Dict[str, str]) -> bool:
        """
        Determine if an insight is significant enough to save.
        
        Args:
            insight: The extracted insight
        
        Returns:
            bool: True if insight should be saved to Firebase
        """
        # Always save crisis insights
        if insight.get('type') == 'crisis':
            return True
        
        # Always save milestones and breakthroughs
        if insight.get('type') in ['milestone', 'breakthrough']:
            return True
        
        # Save stressors if they seem significant
        if insight.get('type') == 'stressor':
            content = insight.get('content', '').lower()
            # Filter out very common/generic stressors
            generic_terms = ['a little', 'bit stressed', 'kinda', 'slightly']
            if any(term in content for term in generic_terms):
                return False
            return True
        
        # Save support needs
        if insight.get('type') == 'support_need':
            return True
        
        return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    extractor = InsightExtractor()
    
    # Test messages
    test_cases = [
        "My teacher scolded me in front of everyone today. I felt so embarrassed.",
        "I finally understand why I get so anxious before exams!",
        "I don't know what to do anymore. I'm really struggling.",
        "I completed my first week of daily meditation!",
        "I can't sleep because of my exam tomorrow. I'm so worried.",
    ]
    
    print("🧠 Insight Extraction Test\n")
    for message in test_cases:
        print(f"Message: {message}")
        insights = extractor.extract_insights(message, "AI response here")
        
        for insight in insights:
            if extractor.should_save_insight(insight):
                print(f"  ✅ [{insight['type'].upper()}] {insight['content']}")
            else:
                print(f"  ⏭️  Skipped (not significant)")
        print()
