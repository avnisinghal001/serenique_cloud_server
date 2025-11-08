from fastapi import FastAPI, HTTPException
import asyncio
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
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
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

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
async def generate_persona(request: GeneratePersonaRequest):
    """
    Generate personalized chatbot persona from quiz responses.
    
    This endpoint:
    1. Analyzes quiz data using LangChain + Gemini
    2. Generates personalityProfile (static) and liveUserState (dynamic)
    3. Saves to Firebase Firestore (user_persona collection)
    4. Returns complete persona to Flutter app
    
    Flow: Flutter Quiz → This Endpoint → LangChain Analysis → Firebase Storage → Flutter Chat
    """
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
async def get_persona(user_id: str):
    """
    Retrieve existing persona for a user.
    Used by Flutter app to load persona when initializing chat.
    """
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
async def update_user_state(request: UpdateStateRequest):
    """
    Update live user state based on app interactions.
    
    This endpoint is called by Flutter app whenever user:
    - Sends a chat message
    - Uses a mental wellness tool
    - Logs sleep data
    - Any other tracked interaction
    
    Updates liveUserState in Firebase with current mood, recent stressors, etc.
    """
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
# CHAT ENDPOINT
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AI assistant using personalized persona.
    
    This endpoint:
    1. Retrieves user's persona (personality profile + live state)
    2. Optionally loads previous chat history from Firebase
    3. Generates AI response using Gemini with full context
    4. Saves both user message and AI response to chat history
    5. Updates live user state (increments chat_message_count)
    
    The AI response is personalized based on:
    - Quiz answers (personality profile)
    - Current mood and stress level (live state)
    - Recent wellness tool usage (coping successes)
    - Recent stressors
    - Previous conversation context
    
    Flow: Flutter Chat UI → This Endpoint → Gemini AI → Response + State Update
    """
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
        
        # Get user persona
        persona = firebase_service.get_user_persona(request.user_id)
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No persona found for user {request.user_id}. Generate persona first."
            )
        
        # Get chat history if requested
        chat_history = []
        if request.include_history:
            # ⚡ OPTIMIZED: Use cached version (10 messages, 0ms if cached)
            chat_history = firebase_service.get_chat_history_optimized(
                user_id=request.user_id,
                limit=10,  # Reduced from 50! Optimal for AI context
                use_cache=True  # Enable in-memory caching
            )
            print(f"📚 Loaded {len(chat_history)} messages (optimized with cache)")
        
        # 🧠 NEW: Load key insights for long-term memory
        key_insights = firebase_service.get_relevant_insights(
            user_id=request.user_id,
            limit=5  # Last 5 important moments
        )
        print(f"💡 Loaded {len(key_insights)} key insights for context")
        
        # Generate AI response using persona + recent history + key insights
        ai_response = persona_architect.chat(
            user_message=request.message,
            persona=persona,
            chat_history=chat_history,
            key_insights=key_insights  # ← NEW: Long-term memory
        )
        
        print(f"✅ Generated AI response ({len(ai_response)} chars)")
        
        # Save user message to Firebase
        firebase_service.save_chat_message(
            user_id=request.user_id,
            role="user",
            content=request.message,
            metadata={
                "mood": persona.live_user_state.current_mood.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Save AI response to Firebase
        firebase_service.save_chat_message(
            user_id=request.user_id,
            role="assistant",
            content=ai_response,
            metadata={
                "model": MODEL_NAME,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # 🧠 NEW: Extract and save key insights from this conversation
        extracted_insights = insight_extractor.extract_insights(
            user_message=request.message,
            ai_response=ai_response,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save significant insights to Firebase
        insights_saved = 0
        for insight in extracted_insights:
            if insight_extractor.should_save_insight(insight):
                firebase_service.save_key_insight(
                    user_id=request.user_id,
                    insight_type=insight['type'],
                    content=insight['content'],
                    original_message=insight['original_message'],
                    timestamp=insight['timestamp']
                )
                insights_saved += 1
        
        if insights_saved > 0:
            print(f"💡 Saved {insights_saved} key insights for long-term memory")
        
        # Update live user state (increment chat count)
        updated_state = persona_architect.update_user_state(
            current_state=persona.live_user_state,
            action={
                "type": "chat_message",
                "content": request.message,
                "mood": persona.live_user_state.current_mood.value
            }
        )
        firebase_service.update_live_state(request.user_id, updated_state)
        
        print(f"✅ Chat processed successfully for user {request.user_id}")
        
        return ChatResponse(
            success=True,
            response=ai_response,
            message="Chat response generated successfully",
            chat_history_saved=True
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
async def get_chat_history(user_id: str, limit: int = 50):
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
    limit: int = 50
):
    """
    Get chat history messages for a particular user filtered by date.
    
    This endpoint retrieves messages from the chat_history collection
    for a specific user on a specific date, ordered by timestamp.
    
    Args:
        user_id: The Firebase Auth user ID
        date: Date in format YYYY-MM-DD (e.g., "2025-11-07")
        limit: Maximum number of messages to retrieve (default: 50, max: 500)
    
    Returns:
        List of chat messages from that specific date with role, content, timestamp, and metadata
    """
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


@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    ⚡ Get chat history cache statistics for performance monitoring.
    
    Shows:
    - Number of cached users
    - Total cache entries
    - Cache TTL setting
    - List of cached user IDs
    
    Useful for monitoring cache hit rates and performance optimization.
    """
    try:
        stats = firebase_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats,
            "performance_notes": {
                "cache_hit": "~0-1ms response time",
                "cache_miss": "~100-200ms (Firebase query)",
                "ttl": "5 minutes (300 seconds)",
                "optimization": "Cache automatically invalidated on new messages"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/insights/{user_id}")
async def get_user_insights(user_id: str, limit: int = 10):
    """
    🧠 Get key insights for a user (long-term memory).
    
    Returns important conversation moments that are remembered
    beyond the 10-message context window.
    
    Args:
        user_id: User ID
        limit: Number of insights to retrieve (default 10)
    
    Returns:
        List of insights with type, content, and timestamp
    """
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
async def delete_user_insight(user_id: str, insight_id: str):
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
        <title>Serenique + Gemini 2.0</title>
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
            <h1>Serenique + Gemini 2.0 Flash</h1>
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
