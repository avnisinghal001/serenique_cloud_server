"""
LangChain-based Persona Architect for Serenique Mental Wellness AI

This module analyzes user quiz responses using LangChain with OpenRouter
to generate personalized chatbot personas. It uses structured output parsing
to ensure consistent personality profiles and implements LangGraph for
extended workflow capabilities.

Architecture:
- Uses LangChain with OpenRouter models for intelligent analysis
- Implements strict output parsing with Pydantic models
- Stores results in Firebase Firestore (user_persona collection)
- Supports dynamic state updates for real-time personalization
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# ============================================================================
# ENUMS - Personality Dimensions
# ============================================================================

class CommunicationStyle(str, Enum):
    """How the user prefers to process and discuss emotions"""
    LOGICAL = "logical"  # Prefers structured, analytical approaches
    EMOTIONAL = "emotional"  # Prefers empathetic, feeling-based approaches
    BALANCED = "balanced"  # Comfortable with both approaches


class PrimaryStressor(str, Enum):
    """Main source of stress for the user"""
    ACADEMICS = "academics"  # Academic pressure, deadlines, performance
    SOCIAL = "social"  # Social interactions, relationships, loneliness
    SLEEP = "sleep"  # Sleep issues, fatigue, energy management
    GENERAL = "general"  # General life stress, multiple factors


class SocialProfile(str, Enum):
    """User's social energy and interaction preferences"""
    INTROVERTED = "introverted"  # Drained by social interaction
    EXTROVERTED = "extroverted"  # Energized by social interaction
    AMBIVERTED = "ambiverted"  # Context-dependent social energy


class CopingMechanism(str, Enum):
    """How the user naturally copes with stress"""
    ANALYTICAL = "analytical"  # Problem-solving, planning, logic
    AFFECTIVE = "affective"  # Emotional expression, talking, connection
    MIXED = "mixed"  # Uses both analytical and affective strategies


class StressLevel(str, Enum):
    """Current overall stress assessment"""
    LOW = "low"  # Manageable stress, good coping
    MODERATE = "moderate"  # Some challenges, occasional overwhelm
    HIGH = "high"  # Significant stress, needs immediate support


class Mood(str, Enum):
    """Current mood state"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    SAD = "sad"
    MOTIVATED = "motivated"
    TIRED = "tired"


# ============================================================================
# PYDANTIC MODELS - Data Structures
# ============================================================================

class PersonalityProfile(BaseModel):
    """Static personality profile derived from quiz responses"""
    
    # Core personality dimensions
    communication_style: CommunicationStyle = Field(
        description="Preferred communication and emotion processing style"
    )
    primary_stressor: PrimaryStressor = Field(
        description="Main source of stress and anxiety"
    )
    social_profile: SocialProfile = Field(
        description="Social energy and interaction preferences"
    )
    coping_mechanism: CopingMechanism = Field(
        description="Natural stress coping strategy"
    )
    stress_level: StressLevel = Field(
        description="Overall current stress assessment"
    )
    
    # Detailed insights
    strengths: List[str] = Field(
        description="User's psychological strengths and resilience factors",
        min_length=2,
        max_length=5
    )
    vulnerabilities: List[str] = Field(
        description="Areas where user may need extra support",
        min_length=2,
        max_length=5
    )
    recommended_approach: str = Field(
        description="Recommended therapeutic approach (CBT, ACT, Emotion-Focused, etc.)"
    )
    
    # Chatbot behavior configuration
    chatbot_tone: str = Field(
        description="Tone the chatbot should use (e.g., 'warm and empathetic', 'structured and logical')"
    )
    chatbot_methodology: str = Field(
        description="Therapeutic methodology to apply (e.g., 'CBT-based cognitive restructuring', 'emotion-focused validation')"
    )
    proactive_triggers: List[str] = Field(
        description="Situations where chatbot should proactively reach out",
        min_length=2,
        max_length=5
    )
    
    # System prompt for AI chatbot
    chatbot_system_prompt: str = Field(
        description="Complete system prompt for AI chatbot personalization"
    )
    
    # Metadata
    generated_at: str = Field(
        description="ISO timestamp of when profile was generated"
    )
    quiz_version: str = Field(
        default="1.0",
        description="Version of quiz used for generation"
    )


class LiveUserState(BaseModel):
    """Dynamic user state updated through app interactions"""
    
    # Current state
    current_mood: Mood = Field(
        default=Mood.NEUTRAL,
        description="User's current mood"
    )
    last_interaction: str = Field(
        default="onboarding",
        description="Last type of interaction (onboarding, chat, tool_use, sleep_log, etc.)"
    )
    last_interaction_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of last interaction"
    )
    
    # Engagement metrics
    chat_message_count: int = Field(
        default=0,
        description="Total chat messages sent by user"
    )
    tool_usage_count: int = Field(
        default=0,
        description="Number of times user used mental wellness tools"
    )
    sleep_logs_count: int = Field(
        default=0,
        description="Number of sleep logs recorded"
    )
    
    # Behavioral insights (updated over time)
    recent_stressors: List[str] = Field(
        default_factory=list,
        description="Recent stressors mentioned by user",
        max_length=5
    )
    coping_successes: List[str] = Field(
        default_factory=list,
        description="Coping strategies that worked well",
        max_length=5
    )
    needs_check_in: bool = Field(
        default=False,
        description="Flag indicating user might need proactive support"
    )
    
    # Update metadata
    last_updated: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of last state update"
    )


class UserPersona(BaseModel):
    """Complete user persona combining static profile and dynamic state"""
    
    user_id: str = Field(
        description="Unique user ID from Firebase Authentication"
    )
    personality_profile: PersonalityProfile = Field(
        description="Static personality profile from quiz analysis"
    )
    live_user_state: LiveUserState = Field(
        description="Dynamic user state updated through interactions"
    )


# ============================================================================
# LANGCHAIN PERSONA ARCHITECT
# ============================================================================

class LangChainPersonaArchitect:
    """
    LangChain-based persona architect using OpenRouter models
    for intelligent quiz analysis and persona generation.
    """
    
    def __init__(
        self,
        openrouter_api_key: str,
        model_name: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.7
    ):
        """
        Initialize LangChain persona architect.
        
        Args:
            openrouter_api_key: API key for OpenRouter
            model_name: Model to use (e.g., "anthropic/claude-3.5-sonnet")
            temperature: Model temperature (0.0-1.0)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
        )
        
        # Set up output parser for PersonalityProfile
        self.parser = JsonOutputParser(pydantic_object=PersonalityProfile)
        
        # Define the analysis prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert clinical psychologist specializing in personality assessment and therapeutic matching for college students. Your role is to analyze quiz responses and generate a comprehensive personality profile that will guide an AI mental wellness chatbot.

The chatbot (named Serenique) serves college students dealing with stress, anxiety, sleep issues, and academic pressure. Your analysis must be:
1. Psychologically accurate and evidence-based
2. Tailored to college student mental health needs
3. Actionable for AI chatbot personalization
4. Empathetic yet professional

Quiz Question Reference:
Q1: "When you're stressed, how do you prefer to work through it?"
Q2: "When you see posts about others' achievements on social media, how do you usually feel?"
Q3: "After a long social event, what do you usually want to do?"
Q4: "When you have a big deadline coming up, how do you usually feel?"
Q5: "How do you feel about reaching out for help when you're struggling?"
Q6: "How much does sleep affect your mood and stress levels?"
Q7: "When something goes wrong, what's your first response?"
Q8: "How often do you find yourself distracted by your phone or social media?"
Q9: "When you're feeling lonely, what's your go-to move?"
Q10: "How often do you catch yourself thinking negative thoughts about yourself?"

{format_instructions}"""),
            ("user", """Analyze these quiz responses and generate a comprehensive personality profile:

{quiz_responses}

Generate a complete PersonalityProfile with:
1. Core personality dimensions (communication_style, primary_stressor, social_profile, coping_mechanism, stress_level)
2. Detailed insights (strengths, vulnerabilities, recommended_approach)
3. Chatbot configuration (tone, methodology, proactive_triggers)
4. Complete chatbot_system_prompt that will guide the AI's behavior

The system prompt should be comprehensive (300-500 words) and include:
- Core identity and role
- Tone and communication style
- Therapeutic methodology to use
- Specific guidance for this user's personality
- When to be proactive vs. reactive
- How to handle crisis situations""")
        ])
        
        # Create the analysis chain
        self.chain = (
            {"quiz_responses": RunnablePassthrough(), "format_instructions": lambda _: self.parser.get_format_instructions()}
            | self.prompt
            | self.llm
            | self.parser
        )
    
    def generate_persona(
        self,
        user_id: str,
        quiz_data: Dict[int, str]
    ) -> UserPersona:
        """
        Generate complete user persona from quiz responses.
        
        Args:
            user_id: Unique user ID from Firebase Auth
            quiz_data: Dictionary mapping question IDs to selected answers
                      e.g., {1: "a", 2: "c", 3: "b", ...}
        
        Returns:
            UserPersona with personality_profile and live_user_state
        """
        # Format quiz responses for LLM analysis
        quiz_text = self._format_quiz_for_analysis(quiz_data)
        
        # Run LangChain analysis
        personality_profile_dict = self.chain.invoke(quiz_text)
        
        # Add generation timestamp
        personality_profile_dict["generated_at"] = datetime.utcnow().isoformat()
        
        # Create PersonalityProfile from LLM output
        personality_profile = PersonalityProfile(**personality_profile_dict)
        
        # Create initial LiveUserState
        live_user_state = LiveUserState(
            current_mood=Mood.NEUTRAL,
            last_interaction="onboarding",
            last_interaction_timestamp=datetime.utcnow().isoformat()
        )
        
        # Combine into UserPersona
        persona = UserPersona(
            user_id=user_id,
            personality_profile=personality_profile,
            live_user_state=live_user_state
        )
        
        return persona
    
    def _format_quiz_for_analysis(self, quiz_data: Dict[int, str]) -> str:
        """Format quiz responses into readable text for LLM analysis"""
        
        # Question text for reference
        questions = {
            1: "When you're stressed, how do you prefer to work through it?",
            2: "When you see posts about others' achievements on social media, how do you usually feel?",
            3: "After a long social event, what do you usually want to do?",
            4: "When you have a big deadline coming up, how do you usually feel?",
            5: "How do you feel about reaching out for help when you're struggling?",
            6: "How much does sleep affect your mood and stress levels?",
            7: "When something goes wrong, what's your first response?",
            8: "How often do you find yourself distracted by your phone or social media?",
            9: "When you're feeling lonely, what's your go-to move?",
            10: "How often do you catch yourself thinking negative thoughts about yourself?"
        }
        
        # Answer text for reference (simplified - you can expand this)
        answer_interpretations = {
            (1, "a"): "Talk it out with someone",
            (1, "b"): "Make a plan and break it down logically",
            (1, "c"): "Take space and process alone",
            (1, "d"): "Distract myself with activities",
            (2, "a"): "Inspired and motivated",
            (2, "b"): "Behind or inadequate",
            (2, "c"): "Neutral, it's just social media",
            (2, "d"): "Happy for them, but sometimes envious",
            (3, "a"): "Recharge alone with quiet time",
            (3, "b"): "Process the event with someone",
            (3, "c"): "Plan the next social activity",
            (3, "d"): "Keep the energy going with more activities",
            (4, "a"): "Energized and focused",
            (4, "b"): "Anxious and overwhelmed",
            (4, "c"): "Calm, I pace myself well",
            (4, "d"): "Procrastinate until the last minute",
            (5, "a"): "Comfortable, I reach out easily",
            (5, "b"): "Uncomfortable, I prefer to handle things myself",
            (5, "c"): "It depends on the situation",
            (5, "d"): "I want to reach out but struggle to do so",
            (6, "a"): "Huge impact, sleep is critical",
            (6, "b"): "Moderate impact, noticeable but manageable",
            (6, "c"): "Small impact, I adapt easily",
            (6, "d"): "Minimal impact, rarely connected",
            (7, "a"): "Analyze what happened and why",
            (7, "b"): "Feel the emotions first, then problem-solve",
            (7, "c"): "Seek advice from others",
            (7, "d"): "Try to move on quickly",
            (8, "a"): "Very often, it's a constant distraction",
            (8, "b"): "Sometimes, when stressed or bored",
            (8, "c"): "Rarely, I'm pretty focused",
            (8, "d"): "Almost never, I stay present",
            (9, "a"): "Reach out to someone",
            (9, "b"): "Scroll through social media",
            (9, "c"): "Engage in a solo hobby",
            (9, "d"): "Just sit with the feeling",
            (10, "a"): "Very often, it's a daily struggle",
            (10, "b"): "Sometimes, especially during stress",
            (10, "c"): "Rarely, I'm generally positive",
            (10, "d"): "Almost never, I'm kind to myself"
        }
        
        formatted = "User Quiz Responses:\n\n"
        for q_id, answer in sorted(quiz_data.items()):
            question_text = questions.get(q_id, f"Question {q_id}")
            answer_text = answer_interpretations.get((q_id, answer), f"Answer {answer}")
            formatted += f"Q{q_id}: {question_text}\nAnswer: {answer_text}\n\n"
        
        return formatted
    
    def update_user_state(
        self,
        current_state: LiveUserState,
        action: Dict[str, Any]
    ) -> LiveUserState:
        """
        Update live user state based on app action.
        
        Args:
            current_state: Current LiveUserState
            action: Dictionary describing the action
                   e.g., {"type": "chat_message", "content": "...", "mood": "anxious"}
                   e.g., {"type": "tool_use", "tool_name": "breathing_exercise"}
                   e.g., {"type": "sleep_log", "hours": 6, "quality": "poor"}
        
        Returns:
            Updated LiveUserState
        """
        action_type = action.get("type", "unknown")
        
        # Update based on action type
        if action_type == "chat_message":
            current_state.chat_message_count += 1
            current_state.last_interaction = "chat"
            
            # Update mood if provided
            if "mood" in action:
                try:
                    current_state.current_mood = Mood(action["mood"])
                except ValueError:
                    pass  # Invalid mood, keep current
            
            # Extract recent stressors from content (simplified)
            if "content" in action and "stress" in action["content"].lower():
                stressor = action.get("stressor_detected", "general stress")
                if stressor not in current_state.recent_stressors:
                    current_state.recent_stressors.append(stressor)
                    if len(current_state.recent_stressors) > 5:
                        current_state.recent_stressors.pop(0)
        
        elif action_type == "tool_use":
            current_state.tool_usage_count += 1
            current_state.last_interaction = "tool_use"
            
            # Track successful coping strategies
            tool_name = action.get("tool_name", "unknown tool")
            success = f"Used {tool_name}"
            if success not in current_state.coping_successes:
                current_state.coping_successes.append(success)
                if len(current_state.coping_successes) > 5:
                    current_state.coping_successes.pop(0)
        
        elif action_type == "sleep_log":
            current_state.sleep_logs_count += 1
            current_state.last_interaction = "sleep_log"
            
            # Check if poor sleep indicates need for check-in
            hours = action.get("hours", 7)
            quality = action.get("quality", "good")
            if hours < 5 or quality in ["poor", "very poor"]:
                current_state.needs_check_in = True
        
        # Update timestamp
        current_state.last_interaction_timestamp = datetime.utcnow().isoformat()
        current_state.last_updated = datetime.utcnow().isoformat()
        
        return current_state


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example quiz data
    sample_quiz = {
        1: "b",  # Logical problem-solving
        2: "b",  # Feels behind on social media
        3: "a",  # Needs alone time after social events
        4: "b",  # Anxious about deadlines
        5: "d",  # Wants help but struggles to ask
        6: "a",  # Sleep critically affects mood
        7: "a",  # Analyzes problems first
        8: "b",  # Sometimes distracted by phone
        9: "a",  # Reaches out when lonely
        10: "b"  # Sometimes has negative self-talk
    }
    
    # Initialize architect (requires OpenRouter API key)
    # architect = LangChainPersonaArchitect(
    #     openrouter_api_key="your_api_key_here"
    # )
    
    # Generate persona
    # persona = architect.generate_persona("user123", sample_quiz)
    # print(persona.model_dump_json(indent=2))
