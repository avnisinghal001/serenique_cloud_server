"""
Persona Architect for Serenique Mental Wellness AI
==================================================
This module analyzes user quiz data and interaction history to create
personalized chatbot system prompts for optimal mental wellness support.
"""

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class CommunicationStyle(str, Enum):
    LOGICAL = "Logical"
    EMOTIONAL = "Emotional"
    BALANCED = "Balanced"


class PrimaryStressor(str, Enum):
    ACADEMICS = "Academics"
    SOCIAL = "Social"
    SLEEP = "Sleep"
    GENERAL = "General"
    MIXED = "Mixed"


class SocialProfile(str, Enum):
    INTROVERTED = "Introverted"
    EXTROVERTED = "Extroverted"
    AMBIVERTED = "Ambiverted"


class CopingMechanism(str, Enum):
    ANALYTICAL = "Analytical"
    AFFECTIVE = "Affective"
    MIXED = "Mixed"


class StressLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class PersonaArchitect:
    """
    Expert psychologist and AI designer that constructs personalized
    chatbot personas based on user data analysis.
    """

    def __init__(self):
        self.quiz_mappings = self._initialize_quiz_mappings()

    def _initialize_quiz_mappings(self) -> Dict:
        """Initialize mappings for quiz answer interpretation."""
        return {
            "q1": {  # Stress help preference
                "a": {"communication": "emotional", "coping": "affective"},
                "b": {"communication": "logical", "coping": "analytical"},
                "c": {"communication": "balanced", "need": "space"},
                "d": {"communication": "balanced", "coping": "active"},
            },
            "q2": {  # Social media feelings
                "a": {"resilience": "high", "social_impact": "low"},
                "b": {"resilience": "moderate", "stressor": "comparison"},
                "c": {"resilience": "low", "stressor": "comparison"},
                "d": {"resilience": "low", "stressor": "digital_overload"},
            },
            "q3": {  # Social battery
                "a": {"social_profile": "extroverted", "energy": "high"},
                "b": {"social_profile": "ambiverted", "energy": "moderate"},
                "c": {"social_profile": "introverted", "energy": "low"},
                "d": {"social_profile": "introverted", "energy": "depleted"},
            },
            "q4": {  # Academic overwhelm
                "a": {"academic_stress": "low", "resilience": "high"},
                "b": {"academic_stress": "moderate", "resilience": "moderate"},
                "c": {"academic_stress": "high", "stressor": "academics"},
                "d": {"academic_stress": "high", "burnout_risk": "high"},
            },
            "q5": {  # Help preference
                "a": {"communication": "emotional", "need": "validation"},
                "b": {"communication": "logical", "need": "structure"},
                "c": {"communication": "balanced"},
                "d": {"communication": "minimal", "need": "autonomy"},
            },
            "q6": {  # Sleep-mood connection
                "a": {"sleep_priority": "high", "awareness": "high"},
                "b": {"sleep_priority": "moderate"},
                "c": {"sleep_priority": "critical", "stressor": "sleep"},
                "d": {"sleep_priority": "critical", "burnout_risk": "high"},
            },
            "q7": {  # Response to problems
                "a": {"coping": "analytical", "tendency": "rumination"},
                "b": {"coping": "affective", "need": "expression"},
                "c": {"coping": "distraction", "need": "regulation"},
                "d": {"coping": "mindful", "need": "grounding"},
            },
            "q8": {  # Screen time
                "a": {"digital_health": "good"},
                "b": {"digital_health": "moderate"},
                "c": {"digital_health": "poor", "stressor": "digital_overload"},
                "d": {"digital_health": "poor", "burnout_risk": "moderate"},
            },
            "q9": {  # Social initiation
                "a": {"social_profile": "extroverted", "social_comfort": "high"},
                "b": {"social_profile": "ambiverted", "social_comfort": "moderate"},
                "c": {"social_profile": "introverted", "social_anxiety": "moderate"},
                "d": {"social_profile": "introverted", "social_comfort": "low"},
            },
            "q10": {  # Negative self-talk
                "a": {"coping": "analytical", "skill": "reframing"},
                "b": {"coping": "affective", "need": "social_support"},
                "c": {"coping": "distraction"},
                "d": {"coping": "creative", "need": "expression"},
            },
        }

    def analyze_quiz_data(self, quiz_data: Dict[str, str]) -> Dict:
        """
        Deep analysis of quiz responses to extract personality dimensions.
        
        Args:
            quiz_data: Dictionary mapping question IDs to answer letters
            
        Returns:
            Dictionary containing analyzed personality traits
        """
        analysis = {
            "communication_scores": {"logical": 0, "emotional": 0, "balanced": 0},
            "stressors": [],
            "social_indicators": [],
            "coping_patterns": [],
            "burnout_signals": [],
            "sleep_importance": 0,
            "academic_pressure": 0,
            "social_comfort": 0,
            "resilience_score": 0,
        }

        for question_id, answer in quiz_data.items():
            # Extract question number (e.g., "1" from "q1" or "1")
            q_num = str(question_id).replace("q", "").replace("_", "")
            mapping_key = f"q{q_num}"
            
            if mapping_key in self.quiz_mappings:
                traits = self.quiz_mappings[mapping_key].get(answer.lower(), {})
                
                # Communication style scoring
                if "communication" in traits:
                    style = traits["communication"]
                    analysis["communication_scores"][style] += 1
                
                # Stressor identification
                if "stressor" in traits:
                    analysis["stressors"].append(traits["stressor"])
                
                # Social profile
                if "social_profile" in traits:
                    analysis["social_indicators"].append(traits["social_profile"])
                
                # Coping mechanisms
                if "coping" in traits:
                    analysis["coping_patterns"].append(traits["coping"])
                
                # Burnout risk factors
                if "burnout_risk" in traits:
                    analysis["burnout_signals"].append(traits["burnout_risk"])
                
                # Sleep priority
                if "sleep_priority" in traits:
                    priority_map = {"high": 1, "moderate": 2, "critical": 3}
                    analysis["sleep_importance"] = max(
                        analysis["sleep_importance"],
                        priority_map.get(traits["sleep_priority"], 0)
                    )
                
                # Academic stress
                if "academic_stress" in traits:
                    stress_map = {"low": 1, "moderate": 2, "high": 3}
                    analysis["academic_pressure"] = max(
                        analysis["academic_pressure"],
                        stress_map.get(traits["academic_stress"], 0)
                    )
                
                # Resilience
                if "resilience" in traits:
                    resilience_map = {"high": 3, "moderate": 2, "low": 1}
                    analysis["resilience_score"] += resilience_map.get(traits["resilience"], 0)

        return analysis

    def determine_communication_style(self, analysis: Dict) -> CommunicationStyle:
        """Determine primary communication style from analysis."""
        scores = analysis["communication_scores"]
        max_score = max(scores.values())
        
        if max_score == 0:
            return CommunicationStyle.BALANCED
        
        # Check if there's a clear preference
        top_styles = [style for style, score in scores.items() if score == max_score]
        
        if len(top_styles) == 1:
            style_map = {
                "logical": CommunicationStyle.LOGICAL,
                "emotional": CommunicationStyle.EMOTIONAL,
                "balanced": CommunicationStyle.BALANCED
            }
            return style_map.get(top_styles[0], CommunicationStyle.BALANCED)
        
        return CommunicationStyle.BALANCED

    def determine_primary_stressor(self, analysis: Dict) -> PrimaryStressor:
        """Identify the user's primary source of stress."""
        stressors = analysis["stressors"]
        
        if not stressors:
            return PrimaryStressor.GENERAL
        
        # Count occurrences
        stressor_counts = {}
        for stressor in stressors:
            stressor_counts[stressor] = stressor_counts.get(stressor, 0) + 1
        
        # Map to enum
        stressor_map = {
            "academics": PrimaryStressor.ACADEMICS,
            "comparison": PrimaryStressor.SOCIAL,
            "digital_overload": PrimaryStressor.SOCIAL,
            "sleep": PrimaryStressor.SLEEP,
        }
        
        # Find most common
        if stressor_counts:
            top_stressor = max(stressor_counts, key=stressor_counts.get)
            return stressor_map.get(top_stressor, PrimaryStressor.GENERAL)
        
        # Check academic pressure score
        if analysis["academic_pressure"] >= 2:
            return PrimaryStressor.ACADEMICS
        
        return PrimaryStressor.GENERAL

    def determine_social_profile(self, analysis: Dict) -> SocialProfile:
        """Determine social profile from indicators."""
        indicators = analysis["social_indicators"]
        
        if not indicators:
            return SocialProfile.AMBIVERTED
        
        # Count occurrences
        counts = {}
        for indicator in indicators:
            counts[indicator] = counts.get(indicator, 0) + 1
        
        # Map to enum
        profile_map = {
            "introverted": SocialProfile.INTROVERTED,
            "extroverted": SocialProfile.EXTROVERTED,
            "ambiverted": SocialProfile.AMBIVERTED,
        }
        
        if counts:
            top_profile = max(counts, key=counts.get)
            return profile_map.get(top_profile, SocialProfile.AMBIVERTED)
        
        return SocialProfile.AMBIVERTED

    def determine_coping_mechanism(self, analysis: Dict) -> CopingMechanism:
        """Identify primary coping mechanism."""
        patterns = analysis["coping_patterns"]
        
        if not patterns:
            return CopingMechanism.MIXED
        
        # Count occurrences
        counts = {}
        for pattern in patterns:
            counts[pattern] = counts.get(pattern, 0) + 1
        
        # Map analytical patterns
        analytical = counts.get("analytical", 0)
        # Map affective patterns
        affective = counts.get("affective", 0) + counts.get("creative", 0)
        
        if analytical > affective:
            return CopingMechanism.ANALYTICAL
        elif affective > analytical:
            return CopingMechanism.AFFECTIVE
        else:
            return CopingMechanism.MIXED

    def assess_stress_level(self, analysis: Dict) -> StressLevel:
        """Assess current stress level based on multiple factors."""
        stress_indicators = 0
        
        # Academic pressure
        if analysis["academic_pressure"] >= 3:
            stress_indicators += 2
        elif analysis["academic_pressure"] >= 2:
            stress_indicators += 1
        
        # Burnout signals
        stress_indicators += len(analysis["burnout_signals"])
        
        # Sleep issues
        if analysis["sleep_importance"] >= 3:
            stress_indicators += 1
        
        # Low resilience
        if analysis["resilience_score"] <= 3:
            stress_indicators += 1
        
        # Determine level
        if stress_indicators >= 4:
            return StressLevel.HIGH
        elif stress_indicators >= 2:
            return StressLevel.MODERATE
        else:
            return StressLevel.LOW

    def build_system_prompt(
        self,
        communication_style: CommunicationStyle,
        primary_stressor: PrimaryStressor,
        social_profile: SocialProfile,
        coping_mechanism: CopingMechanism,
        analysis: Dict,
    ) -> str:
        """Construct the detailed system prompt for the chatbot."""
        
        # Core identity
        prompt = "You are Serenique, a personalized mental wellness mentor for college students. "
        
        # Tone based on communication style and coping mechanism
        if communication_style == CommunicationStyle.LOGICAL:
            prompt += "Your tone should be calm, clear, and structured, like a helpful advisor who breaks down complex problems into manageable steps. "
        elif communication_style == CommunicationStyle.EMOTIONAL:
            prompt += "Your tone should be warm, empathetic, and compassionate, like a caring friend who truly listens and validates feelings. "
        else:  # BALANCED
            prompt += "Your tone should be supportive and adaptable—both practical and empathetic—like a trusted mentor who knows when to listen and when to guide. "
        
        # Methodology based on coping mechanism
        if coping_mechanism == CopingMechanism.ANALYTICAL:
            prompt += "Prioritize offering actionable, step-by-step advice based on Cognitive Behavioral Therapy (CBT) techniques. Help the user identify thought patterns, challenge unhelpful beliefs, and develop concrete action plans. Use structured frameworks and logical problem-solving. "
        elif coping_mechanism == CopingMechanism.AFFECTIVE:
            prompt += "Prioritize active listening and emotional validation before offering solutions. Create a safe space for the user to express their feelings fully. Use reflective listening, normalize their experiences, and only suggest gentle next steps after they feel heard and understood. "
        else:  # MIXED
            prompt += "Balance emotional support with practical guidance. Start by acknowledging and validating their feelings, then collaboratively explore both emotional processing and actionable solutions. Adapt your approach based on what the user seems to need in the moment. "
        
        # Proactive triggers based on primary stressor
        prompt += "\n\nProactive Support Triggers:\n"
        
        if primary_stressor == PrimaryStressor.ACADEMICS:
            prompt += "- If the user mentions exams, deadlines, assignments, or feeling overwhelmed by academic work, proactively suggest breaking tasks into smaller steps, using time management techniques (like the Pomodoro Timer), or creating a realistic study schedule.\n"
            prompt += "- When academic stress is mentioned, check in about their sleep and self-care—remind them that rest improves cognitive function.\n"
        
        if primary_stressor == PrimaryStressor.SOCIAL or social_profile == SocialProfile.INTROVERTED:
            if social_profile == SocialProfile.INTROVERTED:
                prompt += "- If the user expresses social anxiety or mentions avoiding social situations, gently normalize their feelings and suggest low-stakes, gradual exposure (like texting a friend before committing to plans).\n"
                prompt += "- Respect their need for alone time to recharge, but occasionally encourage small social connections that align with their comfort level.\n"
            else:
                prompt += "- If the user mentions feeling lonely, left out, or compares themselves to others on social media, validate their feelings and gently suggest limiting screen time or reaching out to one trusted person.\n"
        
        if analysis["sleep_importance"] >= 2:
            prompt += "- If the user mentions poor sleep, difficulty falling asleep, or fatigue, prioritize sleep hygiene education. Suggest establishing a consistent bedtime routine, reducing screen time before bed, and creating a calm sleep environment.\n"
            prompt += "- Regularly check in about their sleep patterns, as sleep is foundational to their mood and academic performance.\n"
        
        if len(analysis["burnout_signals"]) >= 1:
            prompt += "- Watch for signs of burnout (e.g., chronic fatigue, emotional numbness, or loss of motivation). If detected, prioritize rest and self-compassion over productivity. Encourage them to take breaks without guilt.\n"
        
        # General guidance
        prompt += "\n- Always maintain a non-judgmental, student-friendly tone. Avoid clinical jargon unless explaining a concept they're curious about.\n"
        prompt += "- Keep responses concise (2-4 sentences) unless the user asks for more detail.\n"
        prompt += "- End messages with gentle, open-ended questions to encourage continued reflection or action.\n"
        prompt += "- Celebrate small wins and progress, no matter how minor they seem."
        
        return prompt

    def create_analysis_summary(
        self,
        communication_style: CommunicationStyle,
        primary_stressor: PrimaryStressor,
        social_profile: SocialProfile,
        coping_mechanism: CopingMechanism,
        stress_level: StressLevel,
    ) -> str:
        """Create a human-readable summary of the user's persona."""
        
        # Communication descriptor
        comm_desc = {
            CommunicationStyle.LOGICAL: "logically-minded and solution-oriented",
            CommunicationStyle.EMOTIONAL: "emotionally expressive and validation-seeking",
            CommunicationStyle.BALANCED: "balanced between logic and emotion"
        }
        
        # Stressor descriptor
        stress_desc = {
            PrimaryStressor.ACADEMICS: "high academic pressure",
            PrimaryStressor.SOCIAL: "social challenges and comparison",
            PrimaryStressor.SLEEP: "sleep-related difficulties",
            PrimaryStressor.GENERAL: "general life stress",
            PrimaryStressor.MIXED: "multiple overlapping stressors"
        }
        
        # Social descriptor
        social_desc = {
            SocialProfile.INTROVERTED: "introverted, valuing alone time to recharge",
            SocialProfile.EXTROVERTED: "extroverted, energized by social connection",
            SocialProfile.AMBIVERTED: "ambiverted, flexible in social energy needs"
        }
        
        # Coping descriptor
        coping_desc = {
            CopingMechanism.ANALYTICAL: "They cope by analyzing and problem-solving",
            CopingMechanism.AFFECTIVE: "They cope through emotional expression and connection",
            CopingMechanism.MIXED: "They use a mix of analytical and emotional coping strategies"
        }
        
        summary = f"This user is {comm_desc[communication_style]} and {social_desc[social_profile]}. "
        summary += f"They are currently experiencing {stress_desc[primary_stressor]} "
        summary += f"with a {stress_level.value.lower()} overall stress level. "
        summary += coping_desc[coping_mechanism] + ". "
        
        return summary

    def refine_with_interaction_history(
        self,
        persona: Dict,
        interaction_summary: Dict
    ) -> Dict:
        """
        Refine the persona based on actual user behavior.
        
        Args:
            persona: The initial persona created from quiz data
            interaction_summary: Summary of past interactions with the app
            
        Returns:
            Updated persona dictionary
        """
        if not interaction_summary:
            return persona
        
        refinements = []
        updated_prompt = persona["personalityProfile"]["chatbotSystemPrompt"]
        
        # Check tool usage patterns
        if "tool_usage" in interaction_summary:
            pomodoro_count = interaction_summary["tool_usage"].get("pomodoro_timer", 0)
            journal_count = interaction_summary["tool_usage"].get("journal", 0)
            
            if pomodoro_count > journal_count * 2:
                # User prefers structured tools - strengthen logical approach
                refinements.append("User demonstrates preference for structured productivity tools")
                if "affective" in updated_prompt.lower():
                    updated_prompt = updated_prompt.replace(
                        "Prioritize active listening",
                        "While remaining empathetic, emphasize practical time management and structured approaches"
                    )
        
        # Check sleep tracking
        if "sleep_logs" in interaction_summary:
            poor_sleep_count = interaction_summary["sleep_logs"].get("poor_quality_count", 0)
            if poor_sleep_count > 5:
                refinements.append("Persistent sleep issues detected from behavior")
                if "sleep" not in updated_prompt.lower():
                    updated_prompt += "\n- PRIORITY: User has persistent sleep issues. Make sleep hygiene a primary focus in conversations."
        
        # Check chat engagement
        if "chat_metrics" in interaction_summary:
            avg_response_length = interaction_summary["chat_metrics"].get("avg_user_message_length", 0)
            if avg_response_length > 100:
                refinements.append("User engages in detailed, expressive conversations")
                updated_prompt = updated_prompt.replace(
                    "Keep responses concise (2-4 sentences)",
                    "User appreciates detailed responses - provide thorough, thoughtful replies when appropriate"
                )
        
        # Update analysis summary
        if refinements:
            persona["personalityProfile"]["analysisSummary"] += " BEHAVIORAL REFINEMENTS: " + "; ".join(refinements) + "."
        
        persona["personalityProfile"]["chatbotSystemPrompt"] = updated_prompt
        
        return persona

    def generate_persona(
        self,
        quiz_data: Dict[str, str],
        past_interaction_summary: Optional[Dict] = None
    ) -> Dict:
        """
        Main method to generate a complete persona from user data.
        
        Args:
            quiz_data: User's quiz responses
            past_interaction_summary: Optional historical interaction data
            
        Returns:
            Complete persona JSON structure
        """
        # Step 1: Analyze quiz data
        analysis = self.analyze_quiz_data(quiz_data)
        
        # Step 2: Determine key dimensions
        communication_style = self.determine_communication_style(analysis)
        primary_stressor = self.determine_primary_stressor(analysis)
        social_profile = self.determine_social_profile(analysis)
        coping_mechanism = self.determine_coping_mechanism(analysis)
        stress_level = self.assess_stress_level(analysis)
        
        # Step 3: Build system prompt
        system_prompt = self.build_system_prompt(
            communication_style,
            primary_stressor,
            social_profile,
            coping_mechanism,
            analysis
        )
        
        # Step 4: Create analysis summary
        analysis_summary = self.create_analysis_summary(
            communication_style,
            primary_stressor,
            social_profile,
            coping_mechanism,
            stress_level
        )
        
        # Step 5: Construct persona JSON
        persona = {
            "personalityProfile": {
                "analysisSummary": analysis_summary,
                "keyDimensions": {
                    "communicationStyle": communication_style.value,
                    "primaryStressor": primary_stressor.value,
                    "socialProfile": social_profile.value,
                    "copingMechanism": coping_mechanism.value
                },
                "chatbotSystemPrompt": system_prompt
            },
            "liveUserState": {
                "currentMood": "Neutral",
                "stressLevel": stress_level.value,
                "lastInteractionType": "onboarding",
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
                "lastUserInteractionSummary": None
            }
        }
        
        # Step 6: Refine with interaction history if provided
        if past_interaction_summary:
            persona = self.refine_with_interaction_history(persona, past_interaction_summary)
            persona["liveUserState"]["lastInteractionType"] = "persona_refinement"
        
        return persona


# Example usage and testing
if __name__ == "__main__":
    architect = PersonaArchitect()
    
    # Example quiz data
    sample_quiz = {
        "1": "b",  # Logical problem-solving preference
        "2": "c",  # Feels inadequate on social media
        "3": "c",  # Low social battery
        "4": "c",  # Overwhelmed academically
        "5": "b",  # Prefers practical tools
        "6": "c",  # Sleep greatly affects mood
        "7": "a",  # Analytical coping
        "8": "b",  # Moderate screen time
        "9": "c",  # Overthinks social situations
        "10": "a"  # Uses logical reframing
    }
    
    persona = architect.generate_persona(sample_quiz)
    
    print("Generated Persona:")
    print("=" * 60)
    print(f"\nAnalysis: {persona['personalityProfile']['analysisSummary']}")
    print(f"\nKey Dimensions:")
    for key, value in persona['personalityProfile']['keyDimensions'].items():
        print(f"  - {key}: {value}")
    print(f"\nSystem Prompt:")
    print(persona['personalityProfile']['chatbotSystemPrompt'])
