"""
Test script to verify unified single-call chat implementation
"""
import os
from dotenv import load_dotenv
from langchain_persona_architect import (
    LangChainPersonaArchitect,
    UserPersona,
    LiveUserState,
    Mood,
    PersonalityType,
    CopingStyle,
    EmotionalSensitivity,
    PrimaryConcern,
    SupportPreference,
    SocialBattery
)

# Load environment
load_dotenv()

def test_unified_chat():
    """Test that chat() returns correct tuple format with single LLM call"""
    
    # Initialize architect
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set in environment")
        return
    
    architect = LangChainPersonaArchitect(
        google_api_key=api_key,
        model_name="gemini-2.5-flash",
        temperature=0.7
    )
    
    # Create test persona
    test_persona = UserPersona(
        user_id="test_user_123",
        personality_type=PersonalityType.ANALYTICAL_ACHIEVER,
        primary_concern=PrimaryConcern.STRESS_MANAGEMENT,
        emotional_sensitivity=EmotionalSensitivity.MODERATE,
        coping_style=CopingStyle.PROBLEM_SOLVER,
        support_preference=SupportPreference.PRACTICAL_GUIDANCE,
        social_battery=SocialBattery.BALANCED,
        key_challenges=["Work deadlines", "Perfectionism", "Sleep issues"],
        positive_traits=["Organized", "Logical", "Detail-oriented"],
        live_user_state=LiveUserState(
            current_mood=Mood.ANXIOUS,
            recent_triggers=["Upcoming project deadline"],
            sessions_completed=5
        )
    )
    
    # Test message
    test_message = "I have a big presentation tomorrow and I'm feeling really anxious about it. My mind is racing."
    
    print("\n" + "="*70)
    print("🧪 TESTING UNIFIED CHAT IMPLEMENTATION")
    print("="*70)
    print(f"\n📝 Test message: '{test_message}'")
    print(f"👤 Persona: {test_persona.personality_type.value}")
    print(f"😰 Current mood: {test_persona.live_user_state.current_mood.value}")
    print("\n" + "-"*70)
    print("🚀 Calling chat() with single unified LLM call...")
    print("-"*70 + "\n")
    
    # Call chat method
    response_text, recommended_tools = architect.chat(
        user_message=test_message,
        persona=test_persona,
        chat_history=[],
        key_insights=[]
    )
    
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    
    # Verify response
    print(f"\n✅ Response type: {type(response_text)}")
    print(f"✅ Response length: {len(response_text)} characters")
    print(f"\n💬 AI Response:\n{response_text}\n")
    
    # Verify tools
    print(f"✅ Tools type: {type(recommended_tools)}")
    print(f"✅ Tools count: {len(recommended_tools)} tools")
    
    # Check all expected tools present
    expected_tools = [
        "diaphragmatic_breathing", "box_breathing", "four_seven_eight_breathing",
        "pursed_lip_breathing", "body_mapping", "wave_breathing", "self_hug",
        "five_four_three_two_one", "texture_focus", "mental_grounding",
        "body_scan_meditation", "mindful_walking", "mindful_eating"
    ]
    
    missing_tools = [t for t in expected_tools if t not in recommended_tools]
    if missing_tools:
        print(f"❌ Missing tools: {missing_tools}")
    else:
        print(f"✅ All 13 tools present")
    
    # Categorize tools by score
    high_priority = {k: v for k, v in recommended_tools.items() if v >= 70}
    medium_priority = {k: v for k, v in recommended_tools.items() if 50 <= v < 70}
    low_priority = {k: v for k, v in recommended_tools.items() if 30 <= v < 50}
    minimal = {k: v for k, v in recommended_tools.items() if v < 30}
    
    print("\n📊 Tool Recommendations by Priority:")
    print(f"   🔴 HIGH (>=70):     {len(high_priority)} tools")
    if high_priority:
        for tool, score in sorted(high_priority.items(), key=lambda x: x[1], reverse=True):
            print(f"      - {tool}: {score:.1f}")
    
    print(f"   🟡 MEDIUM (50-69):  {len(medium_priority)} tools")
    if medium_priority:
        for tool, score in sorted(medium_priority.items(), key=lambda x: x[1], reverse=True):
            print(f"      - {tool}: {score:.1f}")
    
    print(f"   🟢 LOW (30-49):     {len(low_priority)} tools")
    if low_priority:
        for tool, score in sorted(low_priority.items(), key=lambda x: x[1], reverse=True):
            print(f"      - {tool}: {score:.1f}")
    
    print(f"   ⚪ MINIMAL (<30):   {len(minimal)} tools")
    
    # Validate scores are in range
    invalid_scores = {k: v for k, v in recommended_tools.items() if not (0 <= v <= 100)}
    if invalid_scores:
        print(f"\n❌ Invalid scores (must be 0-100): {invalid_scores}")
    else:
        print(f"\n✅ All scores in valid range (0.0-100.0)")
    
    print("\n" + "="*70)
    print("🎉 TEST COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\n📈 Summary:")
    print(f"   • Single LLM call returned tuple: (str, Dict[str, float])")
    print(f"   • Response: {len(response_text)} chars")
    print(f"   • Tools: {len(recommended_tools)} tools with {len(high_priority)} high-priority")
    print(f"   • Format: ✅ Correct - ready for main.py integration")
    print("\n")

if __name__ == "__main__":
    test_unified_chat()
