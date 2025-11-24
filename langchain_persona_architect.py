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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import json


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


class ChatResponse(BaseModel):
    """Unified chat response with tool recommendations in single JSON structure"""
    
    response: str = Field(
        description="The conversational response to the user's message"
    )
    recommended_tools: Dict[str, float] = Field(
        description="Wellness tool recommendations with probability scores (0-100)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I hear you clearly, and it sounds like you are feeling afraid right now...",
                "recommended_tools": {
                    "diaphragmatic_breathing": 95,
                    "box_breathing": 75,
                    "four_seven_eight_breathing": 55,
                    "pursed_lip_breathing": 70,
                    "body_mapping": 10,
                    "wave_breathing": 75,
                    "self_hug": 10,
                    "five_four_three_two_one": 15,
                    "texture_focus": 10,
                    "mental_grounding": 85,
                    "body_scan_meditation": 10,
                    "mindful_walking": 0,
                    "mindful_eating": 0
                }
            }
        }


# ============================================================================
# LANGCHAIN PERSONA ARCHITECT
# ============================================================================

class LangChainPersonaArchitect:
    """
    LangChain-based persona architect using Google Gemini 2.0 Flash
    for intelligent quiz analysis and persona generation.
    """
    
    def __init__(
        self,
        google_api_key: str,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.5
    ):
        """
        Initialize LangChain persona architect with Gemini.
        
        Args:
            google_api_key: Google API key for Gemini
            model_name: Gemini model to use (default: gemini-2.5-flash)
            temperature: Model temperature (0.0-1.0)
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=google_api_key,
            #convert_system_message_to_human=True
            top_p=0.8,
            top_k=40
        )
        
        # Set up output parser for PersonalityProfile (quiz generation)
        self.parser = JsonOutputParser(pydantic_object=PersonalityProfile)
        
        # Set up output parser for ChatResponse (unified chat + tools)
        self.chat_parser = JsonOutputParser(pydantic_object=ChatResponse)
        
        # Define the analysis prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert clinical psychologist specializing in personality assessment and therapeutic matching for college students. Your role is to analyze quiz responses and generate a comprehensive personality profile that will guide an AI mental wellness chatbot.

The chatbot (named Serebot) serves college students dealing with stress, anxiety, sleep issues, and academic pressure. Your analysis must be:
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
        Update live user state based on wellness tool actions.
        
        Supported action types:
        - chat_message: General chat interaction
        - tool_use: Generic tool usage
        - sleep_log: Sleep tracking
        - breathing_exercise: From breathing_service (4-7-8, Diaphragmatic, Box, etc.)
        - grounding_technique: From grounding_service (5-4-3-2-1, Body Scan, etc.)
        - mindfulness_meditation: From mindfulness_service (Body Scan, Mindful Walking, Mindful Eating)
        - body_relaxation: From body_relaxation_service (Body Mapping, Wave Breathing, Self-Hug)
        
        Args:
            current_state: Current LiveUserState
            action: Dictionary with "type" and "content" (exercise data from Firebase)
        
        Returns:
            Updated LiveUserState
        """
        action_type = action.get("type", "unknown").lower()
        content = action.get("content", {})
        
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
            
            # Extract recent stressors from content
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
        
        # ====================================================================
        # BREATHING EXERCISES (breathing_service.dart)
        # ====================================================================
        elif action_type == "breathing_exercise":
            current_state.tool_usage_count += 1
            current_state.last_interaction = "breathing_exercise"
            
            # Update mood from afterMood
            after_mood = content.get("afterMood", "").lower()
            if after_mood:
                try:
                    current_state.current_mood = Mood(after_mood)
                except ValueError:
                    pass
            
            # Track technique as coping success
            technique = content.get("technique", "Breathing Exercise")
            mood_improvement = content.get("moodImprovement", "")
            
            if mood_improvement == "Improved":
                success = f"{technique} - Improved mood"
                if success not in current_state.coping_successes:
                    current_state.coping_successes.append(success)
                    if len(current_state.coping_successes) > 5:
                        current_state.coping_successes.pop(0)
                current_state.needs_check_in = False
            
            # Check if user struggled (needs support)
            session_quality = content.get("sessionQuality", "")
            completed = content.get("completed", False)
            paused_times = content.get("pausedTimes", 0)
            
            if session_quality == "Needs Improvement" or (not completed and paused_times > 3):
                current_state.needs_check_in = True
                # Track difficulty as potential stressor
                stressor = f"Difficulty with {technique}"
                if stressor not in current_state.recent_stressors:
                    current_state.recent_stressors.append(stressor)
                    if len(current_state.recent_stressors) > 5:
                        current_state.recent_stressors.pop(0)
        
        # ====================================================================
        # GROUNDING TECHNIQUES (grounding_service.dart)
        # ====================================================================
        elif action_type == "grounding_technique":
            current_state.tool_usage_count += 1
            current_state.last_interaction = "grounding_technique"
            
            # Update mood
            after_mood = content.get("afterMood", "").lower()
            if after_mood:
                try:
                    current_state.current_mood = Mood(after_mood)
                except ValueError:
                    pass
            
            # Track technique
            technique_used = content.get("techniqueUsed", "Grounding Technique")
            mood_improvement = content.get("moodImprovement", "")
            
            if mood_improvement == "Improved":
                success = f"{technique_used} - Helped with grounding"
                if success not in current_state.coping_successes:
                    current_state.coping_successes.append(success)
                    if len(current_state.coping_successes) > 5:
                        current_state.coping_successes.pop(0)
                current_state.needs_check_in = False
            
            # Check stress levels and environment
            stress_level = content.get("currentStressLevel", "")
            if stress_level in ["High", "Very High"]:
                current_state.needs_check_in = True
                environment = content.get("environmentType", "general situation")
                stressor = f"High stress in {environment}"
                if stressor not in current_state.recent_stressors:
                    current_state.recent_stressors.append(stressor)
                    if len(current_state.recent_stressors) > 5:
                        current_state.recent_stressors.pop(0)
        
        # ====================================================================
        # MINDFULNESS MEDITATION (mindfulness_service.dart)
        # ====================================================================
        elif action_type == "mindfulness_meditation":
            current_state.tool_usage_count += 1
            current_state.last_interaction = "mindfulness_meditation"
            
            # Update mood
            after_mood = content.get("moodAfter", "").lower()
            if after_mood:
                try:
                    current_state.current_mood = Mood(after_mood)
                except ValueError:
                    pass
            
            # Track technique
            technique_used = content.get("techniqueUsed", "Meditation")
            mood_improvement = content.get("moodImprovement", "")
            session_quality = content.get("sessionQuality", "")
            
            if mood_improvement == "Improved" or session_quality == "Excellent":
                success = f"{technique_used} meditation"
                if success not in current_state.coping_successes:
                    current_state.coping_successes.append(success)
                    if len(current_state.coping_successes) > 5:
                        current_state.coping_successes.pop(0)
                current_state.needs_check_in = False
            
            # Check for struggles
            completed = content.get("completed", False)
            pause_count = content.get("pauseCount", 0)
            completion_rate = float(content.get("completionRate", 100))
            
            if not completed and pause_count > 2 and completion_rate < 50:
                current_state.needs_check_in = True
                stressor = f"Difficulty maintaining focus during {technique_used}"
                if stressor not in current_state.recent_stressors:
                    current_state.recent_stressors.append(stressor)
                    if len(current_state.recent_stressors) > 5:
                        current_state.recent_stressors.pop(0)
        
        # ====================================================================
        # BODY RELAXATION (body_relaxation_service.dart)
        # ====================================================================
        elif action_type == "body_relaxation":
            current_state.tool_usage_count += 1
            current_state.last_interaction = "body_relaxation"
            
            # Update mood
            after_mood = content.get("moodAfter", "").lower()
            if after_mood:
                try:
                    current_state.current_mood = Mood(after_mood)
                except ValueError:
                    pass
            
            # Track tool
            tool_used = content.get("toolUsed", "Body Relaxation")
            mood_improvement = content.get("moodImprovement", "")
            session_quality = content.get("sessionQuality", "")
            
            if mood_improvement == "Improved" or session_quality == "Excellent":
                success = f"{tool_used}"
                if success not in current_state.coping_successes:
                    current_state.coping_successes.append(success)
                    if len(current_state.coping_successes) > 5:
                        current_state.coping_successes.pop(0)
                current_state.needs_check_in = False
            
            # Check for body tension issues (Body Mapping specific)
            if tool_used == "Body Mapping":
                has_very_tense = content.get("hasVeryTenseTensionAreas", False)
                if has_very_tense:
                    stressor = "Significant body tension detected"
                    if stressor not in current_state.recent_stressors:
                        current_state.recent_stressors.append(stressor)
                        if len(current_state.recent_stressors) > 5:
                            current_state.recent_stressors.pop(0)
        
        # Update timestamp
        current_state.last_interaction_timestamp = datetime.utcnow().isoformat()
        current_state.last_updated = datetime.utcnow().isoformat()
        
        return current_state
    
    def _analyze_user_sentiment(
        self,
        state: LiveUserState,
        key_insights: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Analyze user's current sentiment and generate adaptive communication guidance.
        
        Args:
            state: Current LiveUserState
            key_insights: Recent key moments
            
        Returns:
            Sentiment-specific communication guidance
        """
        mood = state.current_mood.value
        needs_support = state.needs_check_in
        has_stressors = len(state.recent_stressors) > 0
        has_successes = len(state.coping_successes) > 0
        
        # Analyze recent insights for crisis indicators
        crisis_indicators = False
        if key_insights:
            for insight in key_insights:
                if insight.get('type') in ['crisis', 'severe_stress', 'self_harm']:
                    crisis_indicators = True
                    break
        
        # Generate adaptive guidance based on sentiment
        if crisis_indicators or mood in ['sad', 'anxious'] and needs_support:
            return """**CURRENT SENTIMENT: NEEDS GENTLE SUPPORT**
- They're struggling right now—be extra gentle and validating
- Don't rush to fix or offer solutions immediately
- Sit with them in the discomfort: "This sounds really hard..."
- Listen more than you speak
- If appropriate, gently suggest grounding tools (**5-4-3-2-1 Method**, **Wave Breathing**)
- Avoid toxic positivity or minimizing their pain"""
        
        elif mood == 'anxious' or 'anxiety' in str(state.recent_stressors).lower():
            return """**CURRENT SENTIMENT: ANXIOUS/OVERWHELMED**
- They need calm and grounding right now
- Use slow, steady language—avoid rushing
- Acknowledge the anxiety without amplifying it: "That sounds overwhelming..."
- Offer grounding/breathing techniques naturally if they seem open
- Focus on "one step at a time" mentality
- **Box Breathing**, **5-4-3-2-1 Method**, or **Diaphragmatic Breathing** might help"""
        
        elif mood == 'stressed':
            return """**CURRENT SENTIMENT: STRESSED**
- They're under pressure—validate that stress is real
- Be practical and supportive, not overly soft
- It's okay to give honest perspective with care
- Ask what's specifically stressing them out
- Suggest active tools: **Box Breathing** (focus), **Body Mapping** (release tension)
- Help them break things down if they're overwhelmed"""
        
        elif mood == 'tired' or 'sleep' in str(state.recent_stressors).lower():
            return """**CURRENT SENTIMENT: EXHAUSTED**
- They're drained—meet them with gentle energy
- Validate exhaustion: "You sound so tired... that's okay"
- Don't push active tools—offer rest-focused ones
- **4-7-8 Breathing** (sleep), **Body Scan** (relaxation), **Wave Breathing** (gentle)
- Sometimes just being heard is enough—don't over-advise"""
        
        elif mood in ['happy', 'motivated'] or has_successes:
            return """**CURRENT SENTIMENT: POSITIVE MOMENTUM**
- They're doing well—celebrate genuinely!
- Match their energy (but keep it natural, not fake-enthusiastic)
- "That's wonderful! What's been helping?"
- Reinforce what's working: reference their recent successes
- Don't be overly cautious—they can handle real conversation right now
- Build on momentum without pressuring"""
        
        elif mood == 'neutral' and not needs_support:
            return """**CURRENT SENTIMENT: STABLE/NEUTRAL**
- They're in a good place to have real conversations
- Be natural and authentic—no need to walk on eggshells
- You can offer honest perspective with care
- Good time to check in on goals or explore deeper topics
- Balance support with gentle challenge if appropriate"""
        
        elif has_stressors and not has_successes:
            return """**CURRENT SENTIMENT: STRUGGLING TO COPE**
- They're facing stressors without finding what works yet
- Be patient and exploratory: "Let's figure this out together..."
- Don't overwhelm with too many tool suggestions
- Focus on understanding their experience first
- Gently introduce one relevant tool at a time
- Validate that finding what works takes time"""
        
        else:
            return """**CURRENT SENTIMENT: GETTING TO KNOW THEM**
- Early in the relationship—build trust first
- Be warm, genuine, and non-judgmental
- Listen deeply and remember what they share
- Don't rush to give advice—understand them first
- Ask curious, caring questions
- Let the relationship develop naturally"""
    
    def chat(
        self,
        user_message: str,
        persona: UserPersona,
        chat_history: Optional[List[Dict[str, str]]] = None,
        key_insights: Optional[List[Dict[str, Any]]] = None,
        user_full_name: Optional[str] = None
    ) -> tuple[str, Dict[str, float]]:
        """
        Generate AI response based on user's persona, chat history, and key insights.
        Ultra-optimized version with minimal token usage.
        
        Returns:
            Tuple of (response_text, recommended_tools_dict)
        """
        chat_history = chat_history or []
        key_insights = key_insights or []
        
        # --- Detect follow-up marker from main.py ---
        import re
        follow_up_minutes = None
        if user_message.startswith("[FOLLOW_UP:"):
            match = re.match(r'\[FOLLOW_UP:(\d+)min\] (.*)', user_message)
            if match:
                follow_up_minutes = match.group(1)
                user_message = match.group(2)  # Remove marker from actual message
                print(f"🔔 Follow-up context detected: {follow_up_minutes} minutes ago")
        
        # --- Build minimal persona context ---
        p = persona.personality_profile
        s = persona.live_user_state

        persona_ctx = (
            f"style={p.communication_style.value}, "
            f"stressor={p.primary_stressor.value}, "
            f"social={p.social_profile.value}, "
            f"coping={p.coping_mechanism.value}, "
            f"level={p.stress_level.value}, "
            f"mood={s.current_mood.value}, "
            f"recent={','.join(s.recent_stressors) or 'none'}, "
            f"checkin={s.needs_check_in}"
        )

        # --- Short insights (max 3) ---
        insights = ""
        if key_insights:
            last = key_insights[-3:]
            items = [f"{i.get('type', 'note')}: {i.get('content', '')}" for i in last]
            insights = " | ".join(items)

        # --- Build follow-up instruction if detected ---
        follow_up_instruction = ""
        if follow_up_minutes:
            follow_up_instruction = f"""

**IMPORTANT FOLLOW-UP CONTEXT:**
The user just chatted with you {follow_up_minutes} minutes ago. They're coming back for a follow-up conversation.
Start your response by warmly acknowledging this and asking how they're doing with what you discussed earlier.
Examples: 
- "Hey (First Name)[Name], I'm glad you're back! How are you feeling about what we talked about? Are things any better?"
- "Welcome back, [Name]! It's only been {follow_up_minutes} minutes - how are things going with [previous topic]?"
Be gentle, caring, and show genuine interest in their wellbeing after your last conversation.
"""

        # --- Ultra-optimized system prompt ---
        name_str = user_full_name if user_full_name else "User"
        system_prompt = f"""
You are Serebot — a calm, soft, empathetic, gentle wellbeing companion created by Avni Singhal (LinkedIn: https://www.linkedin.com/in/avnisinghal001 | GitHub: https://github.com/avnisinghal001).

ALWAYS address the user by only their first name(strictly first name only before the first space) from (**{name_str}**) in every response to create a personal touch. The name is fetched using the get_user_full_name function for personalization.
{follow_up_instruction}
Soothe first: create emotional safety and validation.
Guide second: offer thoughtful, actionable, and realistic steps.
offer 2–3 gentle, grounded steps.
Empower third: encourage progress and autonomy, never dependency.

Use persona + key insights only when they naturally fit the user's current emotional state.
Respond briefly, softly, and with emotional clarity.
No medical claims, no diagnosis, no fabricated facts; if unsure, say so honestly.
If user expresses crisis, self-harm, or severe distress → respond with compassion, stabilize them, and recommend contacting local helplines (e.g., AASRA: 022-27546669).

You MUST output ONLY a JSON object, and the "response" field MUST be written in clean, readable Markdown (formatted like a beautiful Markdown message). Do NOT add any text outside the JSON object:
{{{{
  "response": "<empathetic reply: you understand their feelings and offer gentle support and solutions based on situations as a therapist would>",
  "recommended_tools": {{{{
    "diaphragmatic_breathing": 0-100,
    "box_breathing": 0-100,
    "four_seven_eight_breathing": 0-100,
    "pursed_lip_breathing": 0-100,
    "body_mapping": 0-100,
    "wave_breathing": 0-100,
    "self_hug": 0-100,
    "five_four_three_two_one": 0-100,
    "texture_focus": 0-100,
    "mental_grounding": 0-100,
    "body_scan_meditation": 0-100,
    "mindful_walking": 0-100,
    "mindful_eating": 0-100
  }}}}
}}}}

Tool scoring logic:
- 90–100: explicitly suggested
- 70–89: strong emotional match
- 50–69: moderate relevance
- 30–49: weak relevance
- 10–29: minimal match
- 0–9: not relevant

Emotion→tool mapping:
diaphragmatic_breathing=anxiety/overwhelm
box_breathing=focus_loss/exam_stress
four_seven_eight_breathing=insomnia/night_anxiety
pursed_lip_breathing=panic_spike
body_mapping=body_tension/heaviness
wave_breathing=agitation
self_hug=self_blame/lonely
five_four_three_two_one=panic/dissociation/overstim
texture_focus=public_anxiety/subtle_grounding
mental_grounding=rumination/loops
body_scan_meditation=fatigue/bedtime
mindful_walking=stuck/restless
mindful_eating=emotional_eating/appetite_issues

Context: {persona_ctx}
Insights: {insights}
"""

        # --- Build conversation messages ---
        messages = [("system", system_prompt)]

        # Add recent chat history (last 5 messages already filtered in main.py)
        for msg in chat_history:
            role = "human" if msg.get("role") == "user" else "assistant"
            messages.append((role, msg.get("content", "")))

        messages.append(("human", user_message))

        # --- LLM call ---
        try:
            prompt = ChatPromptTemplate.from_messages(messages)
            resp = (prompt | self.llm).invoke({})
            text = resp.content if hasattr(resp, "content") else str(resp)

            data = self._extract_json_from_response(text)

            response = data.get("response", "I'm here with you.")
            tools = data.get("recommended_tools", self._get_default_tools())
            tools = self._validate_tool_scores(tools)

            return response, tools

        except Exception as e:
            print(f"❌ Chat Error: {e}")
            import traceback
            traceback.print_exc()
            return "I'm here with you.", self._get_default_tools()
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from LLM response that may contain extra text"""
        import json
        import re
        
        # Try to find JSON object in the response
        # Look for pattern: { ... } with proper nesting
        json_pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        # Try each match (usually the largest one is the complete JSON)
        for match in reversed(matches):  # Start with longest matches
            try:
                parsed = json.loads(match)
                # Verify it has the expected structure
                if "response" in parsed and "recommended_tools" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # If no valid JSON found, raise error
        raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")
    
    def _get_default_tools(self) -> Dict[str, float]:
        """Return default tool scores (all 0.0)"""
        return {
            "diaphragmatic_breathing": 0.0,
            "box_breathing": 0.0,
            "four_seven_eight_breathing": 0.0,
            "pursed_lip_breathing": 0.0,
            "body_mapping": 0.0,
            "wave_breathing": 0.0,
            "self_hug": 0.0,
            "five_four_three_two_one": 0.0,
            "texture_focus": 0.0,
            "mental_grounding": 0.0,
            "body_scan_meditation": 0.0,
            "mindful_walking": 0.0,
            "mindful_eating": 0.0
        }
    
    def _validate_tool_scores(self, tools: Dict[str, float]) -> Dict[str, float]:
        """Validate and sanitize tool scores to ensure all tools present with valid ranges"""
        default_tools = self._get_default_tools()
        
        # Update with provided scores, ensuring valid range
        for key in default_tools:
            if key in tools:
                try:
                    score = float(tools[key])
                    default_tools[key] = max(0.0, min(100.0, score))
                except (ValueError, TypeError):
                    default_tools[key] = 0.0
        
        return default_tools
    
    # REMOVED: _extract_tool_recommendations() - Now unified in single chat() call
    # REMOVED: _fallback_tool_extraction() - Tool recommendations now part of structured output
    
    def _legacy_fallback_tool_extraction(self, response_text: str) -> Dict[str, float]:
        """
        LEGACY: Keyword-based tool extraction (kept for emergency fallback).
        NOTE: Should never be called - structured output handles this automatically.
        If you see this being called, there's a problem with JsonOutputParser.
        """
        # Initialize all tools at 0
        tools = {
            "diaphragmatic_breathing": 0.0,
            "box_breathing": 0.0,
            "four_seven_eight_breathing": 0.0,
            "pursed_lip_breathing": 0.0,
            "body_mapping": 0.0,
            "wave_breathing": 0.0,
            "self_hug": 0.0,
            "five_four_three_two_one": 0.0,
            "texture_focus": 0.0,
            "mental_grounding": 0.0,
            "body_scan_meditation": 0.0,
            "mindful_walking": 0.0,
            "mindful_eating": 0.0
        }
        
        response_lower = response_text.lower()
        
        # Keyword mappings with scores
        keyword_scores = {
            # Breathing exercises
            "diaphragmatic_breathing": [
                ("diaphragmatic breathing", 95.0),
                ("belly breath", 85.0),
                ("deep breath", 60.0),
                ("breath deeply", 55.0)
            ],
            "box_breathing": [
                ("box breathing", 95.0),
                ("4-4-4-4", 90.0),
                ("equal breath", 70.0)
            ],
            "four_seven_eight_breathing": [
                ("4-7-8 breathing", 95.0),
                ("four seven eight", 95.0),
                ("sleep breath", 75.0)
            ],
            "pursed_lip_breathing": [
                ("pursed lip", 95.0),
                ("pursed-lip", 95.0),
                ("slow exhale", 70.0),
                ("gentle exhale", 65.0),
                ("breathe out slowly", 60.0)
            ],
            # Body relaxation
            "body_mapping": [
                ("body mapping", 95.0),
                ("body tension", 70.0),
                ("where you feel", 60.0)
            ],
            "wave_breathing": [
                ("wave breathing", 95.0),
                ("wave breath", 90.0),
                ("rhythmic breath", 65.0)
            ],
            "self_hug": [
                ("self-hug", 95.0),
                ("self hug", 95.0),
                ("hug yourself", 85.0),
                ("self-compassion", 60.0)
            ],
            # Grounding techniques
            "five_four_three_two_one": [
                ("5-4-3-2-1", 95.0),
                ("five things", 80.0),
                ("sensory grounding", 75.0),
                ("what you see", 65.0),
                ("notice around you", 55.0)
            ],
            "texture_focus": [
                ("texture focus", 95.0),
                ("feel the texture", 85.0),
                ("texture", 70.0),
                ("touch something", 60.0),
                ("feeling something physical", 65.0)
            ],
            "mental_grounding": [
                ("mental grounding", 95.0),
                ("racing thoughts", 70.0),
                ("slow your thoughts", 65.0)
            ],
            # Meditation
            "body_scan_meditation": [
                ("body scan", 95.0),
                ("scan your body", 85.0),
                ("progressive relaxation", 80.0)
            ],
            "mindful_walking": [
                ("mindful walk", 95.0),
                ("walking meditation", 90.0),
                ("mindful step", 80.0)
            ],
            "mindful_eating": [
                ("mindful eat", 95.0),
                ("mindful meal", 85.0),
                ("eating meditation", 80.0)
            ]
        }
        
        # Scan for keywords and assign highest matching score
        for tool_key, keywords in keyword_scores.items():
            max_score = 0.0
            for keyword, score in keywords:
                if keyword in response_lower:
                    max_score = max(max_score, score)
            tools[tool_key] = max_score
        
        # Context-based boosting for implicit suggestions
        if any(word in response_lower for word in ["anxiety", "anxious", "panic", "overwhelm"]):
            if tools["pursed_lip_breathing"] < 50:
                tools["pursed_lip_breathing"] = max(tools["pursed_lip_breathing"], 60.0)
            if tools["five_four_three_two_one"] < 50:
                tools["five_four_three_two_one"] = max(tools["five_four_three_two_one"], 55.0)
        
        if any(word in response_lower for word in ["sleep", "rest", "tired", "exhausted"]):
            if tools["four_seven_eight_breathing"] < 50:
                tools["four_seven_eight_breathing"] = max(tools["four_seven_eight_breathing"], 65.0)
            if tools["body_scan_meditation"] < 50:
                tools["body_scan_meditation"] = max(tools["body_scan_meditation"], 60.0)
        
        if any(word in response_lower for word in ["tension", "tight", "tense", "body"]):
            if tools["body_mapping"] < 50:
                tools["body_mapping"] = max(tools["body_mapping"], 60.0)
        
        return tools


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
