from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
import asyncio
import time
import re
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from langchain_persona_architect import (
    LangChainPersonaArchitect,
    UserPersona,
    LiveUserState,
)
from firebase_service import firebase_service
from insight_extractor import InsightExtractor

# Load environment variables from .env file
load_dotenv()


app = FastAPI(
    title="Serenique Mental Wellness API - Gemini Edition",
    description="AI-powered mental wellness chatbot with Gemini-based personalized personas",
    version="4.0.0",
)

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Google API key from environment (Gemini API key)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.5"))

if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY not set. Persona generation will fail.")
    print("   Set it via: export GOOGLE_API_KEY='your_key_here'")
    print("   Or set it in your environment variables")
else:
    print(f"✅ Gemini configured with model: {MODEL_NAME}")

persona_architect = LangChainPersonaArchitect(
    google_api_key=GOOGLE_API_KEY,
    model_name=MODEL_NAME,
    temperature=MODEL_TEMPERATURE
)

# Initialize Insight Extractor for long-term memory
insight_extractor = InsightExtractor()
print("✅ Insight Extractor initialized")


auth_scheme = HTTPBearer(auto_error=False)


async def get_authenticated_uid(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Missing Firebase ID token",
        )

    try:
        decoded_token = firebase_auth.verify_id_token(credentials.credentials)
        uid = decoded_token.get("uid")
        if not uid:
            raise ValueError("Token does not contain a uid")
        return uid
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase ID token",
        )


def require_matching_user(requested_user_id: str, authenticated_uid: str) -> None:
    if requested_user_id != authenticated_uid:
        raise HTTPException(
            status_code=403,
            detail="Authenticated user does not match requested user_id",
        )


@app.middleware("http")
async def verify_protected_api_token(request: Request, call_next):
    protected_paths = (
        "/api/persona/generate",
        "/api/persona/update-state",
        "/api/chat",
    )
    is_body_protected_path = request.url.path in protected_paths
    user_path_match = None
    if not is_body_protected_path:
        user_path_match = re.match(
            r"^/api/(persona|chat/history|insights)/([^/]+)(?:/.*)?$",
            request.url.path,
        )

    if not is_body_protected_path and user_path_match is None:
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing Firebase ID token"},
        )

    try:
        token = authorization.split(" ", 1)[1].strip()
        decoded_token = firebase_auth.verify_id_token(token)
        authenticated_uid = decoded_token.get("uid")
        if not authenticated_uid:
            raise ValueError("Token does not contain a uid")
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired Firebase ID token"},
        )

    requested_user_id = user_path_match.group(2) if user_path_match else None
    body_bytes = None
    if requested_user_id is None and request.method in {"POST", "PUT", "PATCH"}:
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes.decode("utf-8") or "{}")
            requested_user_id = body.get("user_id") if isinstance(body, dict) else None
        except Exception:
            requested_user_id = None

    if requested_user_id and requested_user_id != authenticated_uid:
        return JSONResponse(
            status_code=403,
            content={"detail": "Authenticated user does not match requested user_id"},
        )

    if body_bytes is not None:
        async def receive():
            return {
                "type": "http.request",
                "body": body_bytes,
                "more_body": False,
            }

        request = Request(request.scope, receive)

    request.state.user_id = authenticated_uid
    return await call_next(request)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GeneratePersonaRequest(BaseModel):
    """Request to generate persona from quiz data"""
    user_id: str
    quiz_data: Dict[int, str]  # {1: "a", 2: "b", ...}


class UpdateStateRequest(BaseModel):
    """Request to update live user state"""
    user_id: str
    action: Dict[str, Any]  # {"type": "chat_message", "content": "...", "mood": "anxious"}


class PersonaResponse(BaseModel):
    """Response containing complete user persona"""
    success: bool
    user_persona: Optional[Dict] = None
    message: str


class StateUpdateResponse(BaseModel):
    """Response for state update"""
    success: bool
    updated_state: Optional[Dict] = None
    message: str


class ChatRequest(BaseModel):
    """Request to send chat message"""
    user_id: str
    message: str
    include_history: bool = True  # Whether to include previous chat history


class ChatResponse(BaseModel):
    """Response containing AI chatbot reply"""
    success: bool
    response: Optional[str] = None
    message: str
    chat_history_saved: bool = False
    recommended_tools: Optional[Dict[str, int]] = {
        # Breathing Exercises (0 to 100 score)
        "diaphragmatic_breathing": 0,
        "box_breathing": 0,
        "four_seven_eight_breathing": 0,
        "pursed_lip_breathing": 0,
        # Body Relaxation
        "body_mapping": 0,
        "wave_breathing": 0,
        "self_hug": 0,
        # Grounding Techniques
        "five_four_three_two_one": 0,
        "texture_focus": 0,
        "mental_grounding": 0,
        # Mindfulness Meditation
        "body_scan_meditation": 0,
        "mindful_walking": 0,
        "mindful_eating": 0
    }


class ChatHistoryResponse(BaseModel):
    """Response containing chat history messages"""
    success: bool
    user_id: str
    message_count: int
    messages: list
    message: str


# ============================================================================
# PERSONA GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/persona/generate", response_model=PersonaResponse)
async def generate_persona(
    request: GeneratePersonaRequest,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Generate personalized chatbot persona from quiz responses.
    
    This endpoint:
    1. Analyzes quiz data using LangChain + Gemini
    2. Generates personalityProfile (static) and liveUserState (dynamic)
    3. Saves to Firebase Firestore (user_persona collection)
    4. Returns complete persona to Flutter app
    
    Flow: Flutter Quiz → This Endpoint → LangChain Analysis → Firebase Storage → Flutter Chat
    """
    require_matching_user(request.user_id, authenticated_uid)

    try:
        print(f"🔄 Generating persona for user {request.user_id}...")

        # Check if Google API key is set
        if not GOOGLE_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Google API key not configured on server"
            )
        
        # Validate quiz data
        if not request.quiz_data or len(request.quiz_data) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quiz data. Expected 10 questions, got {len(request.quiz_data)}"
            )
        
        # Generate persona using LangChain
        persona = persona_architect.generate_persona(
            user_id=request.user_id,
            quiz_data=request.quiz_data
        )
        
        # Save to Firebase Firestore
        saved = firebase_service.save_user_persona(persona)
        
        if not saved:
            print(f"⚠️  Persona generated but failed to save to Firebase for user {request.user_id}")
        
        # Mark persona as generated in users collection
        firebase_service.mark_persona_generated(request.user_id)
        
        print(f"✅ Persona generated and saved for user {request.user_id}")
        
        return PersonaResponse(
            success=True,
            user_persona=persona.model_dump(),
            message="Persona generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating persona: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate persona: {str(e)}"
        )


@app.get("/api/persona/{user_id}")
async def get_persona(
    user_id: str,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Retrieve existing persona for a user.
    Used by Flutter app to load persona when initializing chat.
    """
    require_matching_user(user_id, authenticated_uid)
    print(f"⚙️ Fetching persona for {user_id}")

    try:
        # Test Firebase connection first
        print(f"🔍 Testing Firebase connection...")
        
        loop = asyncio.get_event_loop()
        persona = await asyncio.wait_for(
            loop.run_in_executor(None, firebase_service.get_user_persona, user_id),
            timeout=30  # Increased from 15 to 30 seconds
        )
        
        print(f"✅ Firebase query completed")

        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No persona found for user {user_id}"
            )

        return {
            "success": True,
            "user_persona": persona.model_dump() if hasattr(persona, "model_dump") else persona,
            "message": "Persona retrieved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error retrieving persona: {e}")
        print(f"❌ Full traceback:\n{error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve persona: {str(e)}"
        )

# ============================================================================
# LIVE STATE UPDATE ENDPOINT
# ============================================================================

@app.post("/api/persona/update-state", response_model=StateUpdateResponse)
async def update_user_state(
    request: UpdateStateRequest,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Update live user state based on app interactions.
    
    This endpoint is called by Flutter app whenever user:
    - Sends a chat message
    - Uses a mental wellness tool
    - Logs sleep data
    - Any other tracked interaction
    
    Updates liveUserState in Firebase with current mood, recent stressors, etc.
    """
    require_matching_user(request.user_id, authenticated_uid)

    try:
        print(f"🔄 Updating state for user {request.user_id}...")

        # Get current persona
        persona = firebase_service.get_user_persona(request.user_id)
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No persona found for user {request.user_id}. Generate persona first."
            )
        
        # Update live state using LangChain architect's logic
        updated_state = persona_architect.update_user_state(
            current_state=persona.live_user_state,
            action=request.action
        )
        
        # Save updated state to Firebase
        saved = firebase_service.update_live_state(request.user_id, updated_state)
        
        if not saved:
            raise HTTPException(
                status_code=500,
                detail="Failed to save updated state to Firebase"
            )
        
        print(f"✅ State updated for user {request.user_id}")
        
        return StateUpdateResponse(
            success=True,
            updated_state=updated_state.model_dump(),
            message="State updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update state: {str(e)}"
        )


# ============================================================================
# BACKGROUND TASK FUNCTIONS
# ============================================================================

def save_chat_and_update_state(
    user_id: str,
    user_message: str,
    ai_response: str,
    recommended_tools: Dict[str, int],
    persona: UserPersona,
    model_name: str
):
    """
    Background task to save chat messages and update user state.
    This runs after the response is returned to the user.
    """
    try:
        # Use IST (Indian Standard Time, UTC+5:30)
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(ist)
        
        # Save user message to Firebase
        firebase_service.save_chat_message(
            user_id=user_id,
            role="user",
            content=user_message,
            metadata={
                "mood": persona.live_user_state.current_mood.value,
                "timestamp": now_ist.isoformat()
            }
        )
        
        # Save AI response to Firebase
        firebase_service.save_chat_message(
            user_id=user_id,
            role="assistant",
            content=ai_response,
            metadata={
                "model": model_name,
                "timestamp": now_ist.isoformat()
            },
            recommended_tools=recommended_tools
        )
        
        # Extract and save key insights from this conversation
        extracted_insights = insight_extractor.extract_insights(
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save significant insights to Firebase
        insights_saved = 0
        for insight in extracted_insights:
            if insight_extractor.should_save_insight(insight):
                firebase_service.save_key_insight(
                    user_id=user_id,
                    insight_type=insight['type'],
                    content=insight['content'],
                    original_message=insight['original_message'],
                    timestamp=insight['timestamp']
                )
                insights_saved += 1
        
        if insights_saved > 0:
            print(f"💡 Background: Saved {insights_saved} key insights")
        
        # Update live user state
        updated_state = persona_architect.update_user_state(
            current_state=persona.live_user_state,
            action={
                "type": "chat_message",
                "content": user_message,
                "mood": persona.live_user_state.current_mood.value
            }
        )
        firebase_service.update_live_state(user_id, updated_state)
        
        print(f"✅ Background: Chat saved and state updated for {user_id}")
        
    except Exception as e:
        print(f"❌ Background task error: {e}")
        # Don't raise - background task failure shouldn't affect user response


# ============================================================================
# CHAT ENDPOINT
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Chat with AI assistant using personalized persona.
    
    This endpoint:
    1. Retrieves user's persona (personality profile + live state)
    2. Generates AI response using Gemini with full context
    3. Returns response immediately to user
    4. Saves messages and updates state in background (non-blocking)
    
    The AI response is personalized based on:
    - Quiz answers (personality profile)
    - Current mood and stress level (live state)
    - Recent wellness tool usage (coping successes)
    - Recent stressors
    - Key insights from past conversations
    
    Flow: Flutter Chat UI → This Endpoint → Gemini AI → Immediate Response → Background Save
    """
    require_matching_user(request.user_id, authenticated_uid)

    try:
        print(f"💬 Processing chat for user {request.user_id}...")

        # Check if Google API key is set
        if not GOOGLE_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Google API key not configured on server"
            )

        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # ⚡ Fetch persona, key insights, chat history, and full name in parallel (non-blocking)
        loop = asyncio.get_event_loop()
        persona, key_insights, chat_history, user_full_name = await asyncio.gather(
            loop.run_in_executor(None, firebase_service.get_user_persona, request.user_id),
            loop.run_in_executor(None, firebase_service.get_relevant_insights, request.user_id, 5),
            loop.run_in_executor(None, firebase_service.get_chat_history, request.user_id, 10),
            loop.run_in_executor(None, firebase_service.get_user_full_name, request.user_id)
        )
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No persona found for user {request.user_id}. Generate persona first."
            )
        
        # Get last 5 messages for context
        recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
        
        # ⏰ TIME-BASED CHAT FEATURES
        # 1. Check if last chat was > 5 hours ago → reset to fresh conversation
        # 2. Check if last chat was < 1 hour ago → add follow-up personalization
        user_message_to_send = request.message
        
        if chat_history and len(chat_history) > 0:
            # Get timestamp from most recent message
            last_msg_timestamp = chat_history[-1].get('timestamp', '')
            
            if last_msg_timestamp:
                from datetime import datetime, timedelta, timezone
                try:
                    # Parse ISO timestamp with timezone
                    if last_msg_timestamp.endswith('Z'):
                        last_time = datetime.fromisoformat(last_msg_timestamp.replace('Z', '+00:00'))
                    else:
                        last_time = datetime.fromisoformat(last_msg_timestamp)
                    
                    # Get current time in same timezone
                    if last_time.tzinfo:
                        now = datetime.now(last_time.tzinfo)
                    else:
                        now = datetime.now()
                    
                    time_diff = now - last_time
                    hours_ago = time_diff.total_seconds() / 3600
                    
                    # 5-HOUR RESET WINDOW: Start fresh if > 5 hours
                    if time_diff > timedelta(hours=5):
                        recent_history = []  # Ignore old history
                        print(f"⏰ Last chat was {hours_ago:.1f} hours ago - starting fresh conversation")
                    
                    # 1-5 HOUR FOLLOW-UP WINDOW: Add personalization if between 1-5 hours
                    elif time_diff >= timedelta(hours=1) and time_diff <= timedelta(hours=5):
                        minutes_ago = int(time_diff.total_seconds() / 60)
                        # Add marker that will be detected by persona_architect
                        user_message_to_send = f"[FOLLOW_UP:{minutes_ago}min] {request.message}"
                        print(f"💭 Follow-up detected - last chat {minutes_ago} minutes ago")
                    
                    # < 1 HOUR: Normal flow with chat history (no special follow-up)
                    
                except Exception as e:
                    print(f"⚠️ Error parsing timestamp for time-based features: {e}")
        
        print(f"💡 Loaded {len(key_insights)} key insights and {len(recent_history)} recent messages for context")
        
        # ⚡ UNIFIED: Single LLM call returns both response + tool recommendations
        # Returns tuple: (response_text, recommended_tools_dict)
        start_time = time.time()
        
        ai_response, recommended_tools = persona_architect.chat(
            user_message=user_message_to_send,
            persona=persona,
            chat_history=recent_history,
            key_insights=key_insights,
            user_full_name=user_full_name
        )
        
        ai_time = time.time() - start_time
        print(f"⏱️ AI response generated in {ai_time:.2f}s ({ai_time*1000:.0f}ms)")
        
        # Convert to integers for consistent API response
        recommended_tools = {k: int(v) for k, v in recommended_tools.items()}
        
        print(f"✅ Generated unified response ({len(ai_response)} chars)")
        print(f"🔧 Tool recommendations: {recommended_tools}")
        
        # 🚀 RETURN RESPONSE IMMEDIATELY - Save in background
        background_tasks.add_task(
            save_chat_and_update_state,
            user_id=request.user_id,
            user_message=request.message,
            ai_response=ai_response,
            recommended_tools=recommended_tools,
            persona=persona,
            model_name=MODEL_NAME
        )
        
        print(f"⚡ Response returned immediately - saving in background")
        
        return ChatResponse(
            success=True,
            response=ai_response,
            message="Chat response generated successfully",
            chat_history_saved=True,
            recommended_tools=recommended_tools
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat: {str(e)}"
        )


# ============================================================================
# CHAT HISTORY ENDPOINT
# ============================================================================

@app.get("/api/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Get all chat history messages for a particular user.
    
    This endpoint retrieves all messages from the chat_history collection
    for a specific user, ordered by timestamp.
    
    Args:
        user_id: The Firebase Auth user ID
        limit: Maximum number of messages to retrieve (default: 50, max: 500)
    
    Returns:
        List of chat messages with role, content, timestamp, and metadata
    """
    require_matching_user(user_id, authenticated_uid)

    try:
        print(f"🔄 Fetching chat history for user {user_id}...")

        # Validate limit parameter
        if limit < 1 or limit > 500:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 500"
            )
        
        # Get chat history from Firebase
        loop = asyncio.get_event_loop()
        chat_history = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                firebase_service.get_chat_history,
                user_id,
                limit
            ),
            timeout=30
        )
        
        print(f"✅ Retrieved {len(chat_history)} messages for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "message_count": len(chat_history),
            "messages": chat_history,
            "message": f"Successfully retrieved {len(chat_history)} messages"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


# ============================================================================
# CHAT HISTORY BY DATE ENDPOINT
# ============================================================================

@app.get("/api/chat/history/{user_id}/date", response_model=ChatHistoryResponse)
async def get_chat_history_by_date(
    user_id: str,
    date: str,
    limit: int = 50,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Get chat history messages for a particular user filtered by date.

    Args:
        user_id: The Firebase Auth user ID
        date: Date in format YYYY-MM-DD (e.g., "2025-11-07")
        limit: Maximum number of messages to retrieve (default: 50, max: 500)

    Returns:
        List of chat messages from that specific date with role, content, timestamp, and metadata
    """
    require_matching_user(user_id, authenticated_uid)

    try:
        print(f"🔄 Fetching chat history for user {user_id} on date {date}...")
        
        # Validate limit parameter
        if limit < 1 or limit > 500:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 500"
            )
        
        # Parse and validate date
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD (e.g., 2025-11-07)"
            )
        
        # Get chat history from Firebase filtered by date
        loop = asyncio.get_event_loop()
        chat_history = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                firebase_service.get_chat_history_by_date,
                user_id,
                date,
                limit
            ),
            timeout=30
        )
        
        print(f"✅ Retrieved {len(chat_history)} messages for user {user_id} on {date}")
        
        return {
            "success": True,
            "user_id": user_id,
            "message_count": len(chat_history),
            "messages": chat_history,
            "message": f"Successfully retrieved {len(chat_history)} messages for {date}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving chat history by date: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


# ============================================================================
# HEALTH AND STATS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "Serenique Gemini Persona Service",
        "version": "4.0.0",
        "gemini_configured": bool(GOOGLE_API_KEY),
        "firebase_initialized": firebase_service._initialized
    }


@app.get("/api/stats")
async def get_stats():
    """
    Get persona generation statistics.
    """
    try:
        stats = firebase_service.get_persona_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }





@app.get("/api/insights/{user_id}")
async def get_user_insights(
    user_id: str,
    limit: int = 10,
    authenticated_uid: str = Depends(get_authenticated_uid),
):
    """
    Get key insights for a user (long-term memory).
    Args:
        user_id: User ID
        limit: Number of insights to retrieve (default 10)
    Returns:
        List of insights with type, content, and timestamp
    """
    require_matching_user(user_id, authenticated_uid)
    try:
        insights = firebase_service.get_relevant_insights(user_id, limit=limit)
        stats = firebase_service.get_insights_stats(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "insights": insights,
            "stats": stats,
            "count": len(insights)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.delete("/api/insights/{user_id}/{insight_id}")
async def delete_user_insight(
    user_id: str,
    insight_id: str,
    authenticated_uid: str = Depends(get_authenticated_uid)
):
    """
    🗑️ Delete a specific key insight.
    
    Args:
        user_id: User ID
        insight_id: Insight document ID
    
    Returns:
        Success status
    """
    try:
        success = firebase_service.delete_insight(user_id, insight_id)
        
        if success:
            return {
                "success": True,
                "message": f"Insight {insight_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete insight")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# LEGACY ENDPOINTS (keep for backward compatibility)
# ============================================================================

@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300}
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    return {
        "item": {
            "id": item_id,
            "name": "Sample Item " + str(item_id),
            "value": item_id * 100
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }


# ============================================================================
# HOME PAGE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Serenique + Gemini 2.5</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            header { border-bottom: 1px solid #333333; padding: 0; }
            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                gap: 2rem;
            }
            .logo {
                font-size: 1.25rem;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
            }
            .nav-links { display: flex; gap: 1.5rem; margin-left: auto; }
            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }
            .nav-links a:hover { color: #ffffff; background-color: #111111; }
            main {
                flex: 1;
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            h1 {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #ffffff, #888888);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                font-size: 1.25rem;
                color: #888888;
                margin-bottom: 2rem;
                max-width: 600px;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                width: 100%;
                max-width: 900px;
                margin-top: 2rem;
            }
            .card {
                background-color: #111111;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                transition: all 0.2s ease;
                text-align: left;
            }
            .card:hover {
                border-color: #555555;
                transform: translateY(-2px);
            }
            .card h3 {
                font-size: 1.125rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #ffffff;
            }
            .card p {
                color: #888888;
                font-size: 0.875rem;
                margin-bottom: 1rem;
            }
            .card a {
                display: inline-flex;
                align-items: center;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.875rem;
                font-weight: 500;
                padding: 0.5rem 1rem;
                background-color: #222222;
                border-radius: 6px;
                border: 1px solid #333333;
                transition: all 0.2s ease;
            }
            .card a:hover {
                background-color: #333333;
                border-color: #555555;
            }
            pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                overflow-x: auto;
                text-align: left;
                margin: 2rem 0;
                max-width: 600px;
            }
            code {
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
                font-size: 0.85rem;
                line-height: 1.5;
                color: #ffffff;
            }
            .keyword { color: #ff79c6; }
            .string { color: #f1fa8c; }
            .function { color: #50fa7b; }
            .class { color: #8be9fd; }
            .module { color: #8be9fd; }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Serenique AI + Gemini</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/health">Health</a>
                </div>
            </nav>
        </header>
        <main>
            <h1>Serenique + Gemini 2.5 Flash</h1>
            <p class="subtitle">AI-powered mental wellness chatbot with personalized personas</p>
            
            <pre><code><span class="keyword">from</span> <span class="module">langchain_google_genai</span> <span class="keyword">import</span> <span class="class">ChatGoogleGenerativeAI</span>

<span class="decorator">@app.post</span>(<span class="string">"/api/chat"</span>)
<span class="keyword">async def</span> <span class="function">chat</span>():
    <span class="keyword">return</span> persona_architect.<span class="function">chat</span>()</code></pre>

            <div class="cards">
                <div class="card">
                    <h3>Interactive API Docs</h3>
                    <p>Explore AI persona generation endpoints with Swagger UI.</p>
                    <a href="/docs">Open Swagger UI →</a>
                </div>
                <div class="card">
                    <h3>Health Check</h3>
                    <p>Monitor API health and Gemini configuration status.</p>
                    <a href="/api/health">Check Health →</a>
                </div>
            </div>
        </main>
    </body>
    </html>
    """


# ──────────────────────────────────────────────
# LEGAL PAGES
# ──────────────────────────────────────────────

_LEGAL_STYLE = """
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f7f8fc;
        color: #1a1a2e;
        line-height: 1.75;
        padding: 0 1rem 4rem;
      }
      header {
        background: #1036D6;
        color: #fff;
        padding: 1.25rem 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
      }
      header a { color: #fff; text-decoration: none; font-size: 0.9rem; opacity: 0.8; }
      header a:hover { opacity: 1; }
      header h1 { font-size: 1.1rem; font-weight: 700; }
      .container { max-width: 760px; margin: 2.5rem auto 0; }
      h2 { font-size: 1.6rem; font-weight: 800; margin-bottom: 0.25rem; color: #1036D6; }
      .meta { font-size: 0.85rem; color: #888; margin-bottom: 2rem; }
      h3 { font-size: 1.05rem; font-weight: 700; margin: 2rem 0 0.5rem; color: #1a1a2e; }
      p, li { font-size: 0.95rem; color: #333; margin-bottom: 0.5rem; }
      ul { padding-left: 1.4rem; margin-bottom: 0.5rem; }
      .callout {
        background: #fff3cd;
        border-left: 4px solid #e6a817;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin: 1.5rem 0;
      }
      .callout.danger {
        background: #fde8e8;
        border-color: #d63031;
      }
      a { color: #1036D6; }
      hr { border: none; border-top: 1px solid #e0e0e0; margin: 2rem 0; }
    </style>
"""


@app.get("/api/privacy", response_class=HTMLResponse)
@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Policy : Serenique</title>
  {_LEGAL_STYLE}
</head>
<body>
  <header>
    <a href="/">← Serenique</a>
    <h1>Privacy Policy</h1>
  </header>
  <div class="container">
    <h2>Privacy Policy</h2>
    <p class="meta">Effective Date: 17 May 2026 &nbsp;|&nbsp; Last Updated: 17 May 2026</p>

    <h3>1. Who We Are</h3>
    <p>
      Serenique is a personal wellness companion application ("App") designed to support
      emotional well-being through mood tracking, guided exercises and an AI-powered
      chat companion called Serebot. Serenique is <strong>not</strong> a medical device,
      clinical therapy service or mental-health provider.
    </p>
    <p>
      This Privacy Policy explains what personal data we collect when you use the
      Serenique App, how we use it and your rights regarding that data. By using the
      App, you agree to the practices described here.
    </p>

    <hr>

    <h3>2. Data We Collect</h3>

    <p><strong>a) Account Data</strong></p>
    <ul>
      <li>Email address and hashed password (managed by Firebase Authentication)</li>
      <li>Unique Firebase User ID (UID)</li>
      <li>Display name, first name, last name (optional, user-provided)</li>
      <li>Age range and self-identified gender (optional, used to personalise the experience)</li>
      <li>Profession / student status (optional)</li>
    </ul>

    <p><strong>b) Wellness Data</strong></p>
    <ul>
      <li>Mood ratings you submit inside the App</li>
      <li>Onboarding quiz responses used to generate your AI persona profile</li>
      <li>Practice logs (breathing exercises, mindfulness sessions, grounding activities)</li>
      <li>Wellness trends and insight summaries derived from your activity</li>
    </ul>

    <p><strong>c) AI Interaction Data</strong></p>
    <ul>
      <li>Text messages you send to Serebot, stored in your personal chat history</li>
      <li>AI-generated responses paired with your messages, timestamped per session</li>
      <li>AI content reports you voluntarily submit (flagged responses)</li>
    </ul>

    <p><strong>d) Technical & Device Data</strong></p>
    <ul>
      <li>Firebase-issued device tokens (for push-notification delivery, if enabled)</li>
      <li>Basic crash and error logs collected automatically by Firebase Crashlytics</li>
    </ul>

    <hr>

    <h3>3. How We Use Your Data</h3>
    <ul>
      <li><strong>Personalised AI experience</strong> : Your onboarding responses are used to generate a custom AI persona that shapes how Serebot interacts with you.</li>
      <li><strong>Chat conversations</strong> : Your messages to Serebot are processed to generate supportive, contextual responses.</li>
      <li><strong>Wellness tracking</strong> : Mood ratings and activity logs are stored so you can view historical trends on your dashboard.</li>
      <li><strong>Insight extraction</strong> : Anonymised patterns from your chat sessions are used to surface weekly wellness insights within the App.</li>
      <li><strong>Safety</strong> : Crisis-keyword detection runs locally on your device before any message is sent to a server, so no AI model ever processes a crisis message as a routine prompt.</li>
      <li><strong>Account management</strong> : Email and UID are used for authentication and to link all your data to your account.</li>
    </ul>
    <p>We do <strong>not</strong> use your data for advertising, profiling for third-party marketing or any purpose unrelated to providing the Serenique wellness experience.</p>

    <hr>

    <h3>4. Generative AI Disclosure</h3>
    <div class="callout">
      <strong>How Serebot works:</strong> Text messages you send are transmitted to our
      secure backend API (hosted on Vercel) and then forwarded to Google's Gemini API
      for response generation. Your Firebase UID is used to fetch your conversation
      context, but <strong>personally identifiable information such as your email
      address or real name is never included in the AI prompt payload</strong>.
      All API calls are authenticated using verified Firebase ID Tokens, unauthenticated
      requests are rejected before reaching any AI model.
    </div>
    <p>
      Serebot is powered by Google Gemini 2.5 Flash via LangChain. AI-generated
      responses are wellness-oriented and not clinical advice. Responses may occasionally
      be inaccurate or inappropriate, you can flag any response using the "Report response"
      button inside the chat screen.
    </p>

    <hr>

    <h3>5. Data Storage &amp; Security</h3>
    <ul>
      <li>All user data is stored in <strong>Google Firebase / Cloud Firestore</strong>, a SOC 2-compliant cloud database.</li>
      <li>All communication between the App and our backend is encrypted in transit using HTTPS/TLS.</li>
      <li>Backend API endpoints require a valid, server-verified <strong>Firebase ID Token</strong>. Each token is scoped to a single user, no endpoint can read or modify another user's data.</li>
      <li>Firebase service account credentials are stored as encrypted environment variables on Vercel and are never included in source code or public repositories.</li>
    </ul>

    <hr>

    <h3>6. Data Sharing</h3>
    <p>We do <strong>not sell, rent or trade</strong> your personal data.</p>
    <p>We share data only with the following trusted sub-processors, strictly to operate the service:</p>
    <ul>
      <li><strong>Google Firebase</strong> : Authentication and Firestore database (Google LLC, USA)</li>
      <li><strong>Google Gemini API</strong> : AI response generation (Google LLC, USA)</li>
      <li><strong>Vercel Inc.</strong> : Serverless API hosting (USA)</li>
    </ul>
    <p>All sub-processors operate under their own privacy policies and applicable data-protection law.</p>

    <hr>

    <h3>7. Data Retention &amp; Deletion</h3>
    <p>
      Your data is retained for as long as your account exists. You may permanently
      delete your account and <strong>all associated data</strong> (mood logs, chat
      history, AI persona, insights) at any time by:
    </p>
    <ul>
      <li><strong>In-app:</strong> Profile → Delete Account (instant, irreversible)</li>
      <li><strong>Web form:</strong> <a href="/delete-account">serenique.app/delete-account</a> (processed within 48 hours)</li>
    </ul>
    <p>
      We do <strong>not</strong> retain backup copies of deleted accounts beyond 30 days,
      and no deleted user's data is used for AI training.
    </p>

    <hr>

    <h3>8. Children's Privacy</h3>
    <p>
      Serenique is intended for users aged <strong>13 and older</strong>. We do not
      knowingly collect personal data from children under 13. If you believe a child
      under 13 has registered, please contact us at
      <a href="mailto:arisyn.studios@gmail.com">arisyn.studios@gmail.com</a> for immediate removal.
    </p>

    <hr>

    <h3>9. Your Rights</h3>
    <p>Depending on your jurisdiction, you may have the right to access, correct or erase your data. To exercise any right, contact us at <a href="mailto:arisyn.studios@gmail.com">arisyn.studios@gmail.com</a>.</p>

    <hr>

    <h3>10. Changes to This Policy</h3>
    <p>We may update this policy periodically. Material changes will be notified through the App. Continued use after changes constitutes acceptance.</p>

    <hr>

    <h3>11. Contact</h3>
    <p>Questions about this policy? Email us at <a href="mailto:arisyn.studios@gmail.com">arisyn.studios@gmail.com</a>.</p>
  </div>
</body>
</html>"""


@app.get("/api/terms", response_class=HTMLResponse)
@app.get("/terms", response_class=HTMLResponse)
def terms_of_service():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Terms of Service : Serenique</title>
  {_LEGAL_STYLE}
</head>
<body>
  <header>
    <a href="/">← Serenique</a>
    <h1>Terms of Service</h1>
  </header>
  <div class="container">
    <h2>Terms of Service</h2>
    <p class="meta">Effective Date: 17 May 2026 &nbsp;|&nbsp; Last Updated: 17 May 2026</p>

    <p>
      Please read these Terms of Service ("Terms") carefully before using the
      Serenique mobile application and associated web services ("Service").
      By creating an account or using the Service, you agree to be bound by these Terms.
    </p>

    <hr>

    <h3>1. Medical &amp; Clinical Disclaimer</h3>
    <div class="callout danger">
      <strong>IMPORTANT — Please read carefully.</strong><br><br>
      Serenique and its AI companion, Serebot, provide wellness-tracking and
      emotional support tools for general well-being purposes only.
      <strong>Serenique is NOT a medical device, a clinical therapy platform
      or a replacement for professional psychological or psychiatric care.</strong><br><br>
      Serebot is an AI chatbot, not a licensed therapist, psychologist, counsellor
      or medical provider. Nothing it says constitutes medical advice, diagnosis
      or treatment.<br><br>
      <strong>If you are experiencing a mental health crisis, thoughts of self-harm
      or suicidal ideation, do NOT rely on the App.</strong> Please immediately contact
      emergency services (112) or a dedicated crisis helpline such as
      AASRA: +91-9820466726 or iCall: +91-9152987821.
    </div>

    <hr>

    <h3>2. User Eligibility</h3>
    <p>
      Serenique is intended for personal, non-commercial wellness use by individuals
      aged <strong>13 years or older</strong>. By registering, you confirm that you
      meet this age requirement. Users between 13 and 18 should have parental or
      guardian awareness before using the Service.
    </p>
    <p>
      If you are under 13, you may not create an account or use the Service.
    </p>

    <hr>

    <h3>3. Nature of the Service</h3>
    <p>
      Serenique provides:
    </p>
    <ul>
      <li>AI-powered wellness conversations through Serebot</li>
      <li>Mood logging and historical wellness trend tracking</li>
      <li>Guided breathing, mindfulness and grounding exercises</li>
      <li>Personalised wellness insights derived from your activity</li>
    </ul>
    <p>
      All AI-generated content is produced by automated language models and may
      occasionally be inaccurate, incomplete or contextually inappropriate.
      You acknowledge that AI responses are <strong>not a substitute for professional
      advice</strong> of any kind.
    </p>

    <hr>

    <h3>4. Acceptable Use</h3>
    <p>You agree <strong>not</strong> to:</p>
    <ul>
      <li>Attempt to manipulate, jailbreak or circumvent Serebot's safety guidelines through prompt-injection or adversarial inputs.</li>
      <li>Submit abusive, harassing, illegal, explicit or hate-speech content to the chatbot.</li>
      <li>Exploit, probe, scan or reverse-engineer our backend API endpoints.</li>
      <li>Use automated scripts or bots to generate artificial usage or extract data.</li>
      <li>Impersonate another user or misrepresent your identity.</li>
      <li>Use the Service for any purpose that violates applicable laws or regulations.</li>
    </ul>
    <p>
      Violation of these rules may result in immediate account suspension or termination
      without notice.
    </p>

    <hr>

    <h3>5. Generative AI Content</h3>
    <p>
      Serebot's responses are generated by Google Gemini, a third-party AI model.
      We apply safety filters and persona guardrails, but we cannot guarantee that
      every AI response will be perfectly accurate, safe or appropriate for your
      specific situation. You use AI-generated content at your own discretion.
    </p>
    <p>
      You may report any AI response you find harmful or inappropriate using the
      "Report response" feature inside the chat screen. We review flagged content
      to continuously improve safety.
    </p>

    <hr>

    <h3>6. Intellectual Property</h3>
    <p>
      All content, design, branding and software in the Serenique App are owned by
      or licensed to us. You may not copy, reproduce, distribute or create derivative
      works without written permission.
    </p>
    <p>
      You retain ownership of the personal content you submit (mood entries, exercises). By submitting content, you grant us a limited, non-exclusive licence to
      process it solely to provide the Service to you.
    </p>

    <hr>

    <h3>7. Limitation of Liability</h3>
    <p>
      To the fullest extent permitted by applicable law, Serenique and its developers
      shall not be liable for any direct, indirect, incidental, consequential or
      punitive damages arising from:
    </p>
    <ul>
      <li>Reliance on AI-generated content or wellness suggestions</li>
      <li>Decisions or actions taken based on any output from the App</li>
      <li>Temporary unavailability of the Service</li>
      <li>Loss of data due to circumstances beyond our reasonable control</li>
    </ul>
    <p>
      <strong>You expressly acknowledge that you use this Service at your own risk
      and that Serenique is a wellness tool, not a safety net for mental health
      emergencies.</strong>
    </p>

    <hr>

    <h3>8. Termination</h3>
    <p>
      You may delete your account at any time via the App (Profile → Delete Account)
      or through our <a href="/delete-account">web deletion form</a>.
      We reserve the right to suspend or terminate accounts that violate these Terms.
    </p>

    <hr>

    <h3>9. Changes to These Terms</h3>
    <p>
      We may revise these Terms from time to time. Continued use of the Service after
      changes take effect constitutes acceptance of the revised Terms. Material changes
      will be communicated through in-app notifications.
    </p>

    <hr>

    <h3>10. Governing Law</h3>
    <p>
      These Terms are governed by the laws of India. Any disputes shall be subject
      to the exclusive jurisdiction of the courts of India.
    </p>

    <hr>

    <h3>11. Contact</h3>
    <p>Questions about these Terms? Contact us at <a href="mailto:arisyn.studios@gmail.com">arisyn.studios@gmail.com</a>.</p>
  </div>
</body>
</html>"""


@app.get("/api/delete-account", response_class=HTMLResponse)
@app.get("/delete-account", response_class=HTMLResponse)
def delete_account_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Request Account Deletion : Serenique</title>
  {_LEGAL_STYLE}
  <style>
    .method-box {{
      background: #fff;
      border: 1.5px solid #e0e0e0;
      border-radius: 12px;
      padding: 1.5rem 1.8rem;
      margin: 1.5rem 0;
    }}
    .method-box h3 {{ margin-top: 0; }}
    .badge {{
      display: inline-block;
      background: #1036D6;
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      border-radius: 20px;
      padding: 2px 10px;
      margin-bottom: 0.75rem;
      letter-spacing: 0.5px;
    }}
    .badge.alt {{ background: #888; }}
    ol li {{ margin-bottom: 0.4rem; }}
    .scope-list {{ background: #f0f4ff; border-radius: 8px; padding: 1rem 1rem 1rem 2rem; margin: 1rem 0; }}
    .scope-list li {{ color: #1036D6; font-weight: 600; }}
    .email-block {{
      background: #f0f4ff;
      border-radius: 8px;
      padding: 1rem 1.2rem;
      font-family: monospace;
      margin: 0.75rem 0;
      word-break: break-all;
    }}
  </style>
</head>
<body>
  <header>
    <a href="/">← Serenique</a>
    <h1>Request Account &amp; Data Deletion</h1>
  </header>
  <div class="container">
    <h2>Delete Your Account &amp; Data</h2>
    <p class="meta">Serenique is committed to your privacy. You can permanently erase your account at any time.</p>

    <div class="callout danger">
      <strong>Warning: Account deletion is permanent and irreversible.</strong><br>
      All your data will be permanently erased, including mood logs, chat history,
      wellness insights and your AI persona profile. This cannot be undone.
    </div>

    <h3>What gets deleted</h3>
    <ul class="scope-list">
      <li>Account credentials (email, UID)</li>
      <li>All Serebot chat messages and conversation history</li>
      <li>Mood ratings and tracking data</li>
      <li>Wellness insights and activity logs</li>
      <li>AI persona profile and onboarding quiz responses</li>
      <li>Any AI content reports you submitted</li>
    </ul>

    <hr>

    <div class="method-box">
      <div class="badge">Recommended — Instant</div>
      <h3>Option 1: Delete directly inside the App</h3>
      <p>This is the fastest method and takes effect immediately.</p>
      <ol>
        <li>Open the <strong>Serenique</strong> app and sign in.</li>
        <li>Tap the <strong>Profile</strong> tab (bottom navigation).</li>
        <li>Scroll down to <strong>Privacy &amp; Data</strong>.</li>
        <li>Tap <strong>Delete Account</strong> and enter your password to confirm.</li>
        <li>Your account and all associated data are permanently deleted immediately.</li>
      </ol>
    </div>

    <div class="method-box">
      <div class="badge alt">Fallback — 48 Hours</div>
      <h3>Option 2: Email deletion request</h3>
      <p>
        If you no longer have the Serenique app installed and still wish to remove
        your account and data, send an email <strong>from your registered email address</strong> to:
      </p>
      <div class="email-block">arisyn.studios@gmail.com</div>
      <p><strong>Subject line (required):</strong></p>
      <div class="email-block">Account Deletion Request</div>
      <p>
        Include your registered email address in the body. We will permanently purge
        all associated data within <strong>48 hours</strong> and send a confirmation reply.
      </p>
      <p>
        You do not need to provide a reason. We will not attempt to retain, anonymise,
        or repurpose your data after a verified deletion request.
      </p>
    </div>

    <hr>

    <h3>Questions?</h3>
    <p>
      If you have any concerns about your data or this process, contact us at
      <a href="mailto:arisyn.studios@gmail.com">arisyn.studios@gmail.com</a>.
      We typically respond within 24 hours.
    </p>

    <p style="margin-top:2rem; font-size:0.85rem; color:#888;">
      See also: <a href="/privacy">Privacy Policy</a> &nbsp;·&nbsp; <a href="/terms">Terms of Service</a>
    </p>
  </div>
</body>
</html>"""
