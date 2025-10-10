from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from langchain_persona_architect import (
    LangChainPersonaArchitect,
    UserPersona,
    LiveUserState,
)
from firebase_service import firebase_service


app = FastAPI(
    title="Serenique Mental Wellness API - LangChain Edition",
    description="AI-powered mental wellness chatbot with LangChain-based personalized personas",
    version="3.0.0",
)

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain Persona Architect
# Get OpenRouter API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")  # Cost-effective default
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

if not OPENROUTER_API_KEY:
    print("⚠️  WARNING: OPENROUTER_API_KEY not set. Persona generation will fail.")
    print("   Set it via: export OPENROUTER_API_KEY='your_key_here'")
else:
    print(f"✅ OpenRouter configured with model: {MODEL_NAME}")

persona_architect = LangChainPersonaArchitect(
    openrouter_api_key=OPENROUTER_API_KEY,
    model_name=MODEL_NAME,
    temperature=MODEL_TEMPERATURE
)


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


# ============================================================================
# PERSONA GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/persona/generate", response_model=PersonaResponse)
async def generate_persona(request: GeneratePersonaRequest):
    """
    Generate personalized chatbot persona from quiz responses.
    
    This endpoint:
    1. Analyzes quiz data using LangChain + OpenRouter
    2. Generates personalityProfile (static) and liveUserState (dynamic)
    3. Saves to Firebase Firestore (user_persona collection)
    4. Returns complete persona to Flutter app
    
    Flow: Flutter Quiz → This Endpoint → LangChain Analysis → Firebase Storage → Flutter Chat
    """
    try:
        print(f"🔄 Generating persona for user {request.user_id}...")
        
        # Check if OpenRouter API key is set
        if not OPENROUTER_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenRouter API key not configured on server"
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
    try:
        persona = firebase_service.get_user_persona(user_id)
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"No persona found for user {user_id}"
            )
        
        return PersonaResponse(
            success=True,
            user_persona=persona.model_dump(),
            message="Persona retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving persona: {e}")
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
# HEALTH AND STATS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "Serenique LangChain Persona Service",
        "version": "3.0.0",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
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
        <title>Vercel + FastAPI</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }

            header {
                border-bottom: 1px solid #333333;
                padding: 0;
            }

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

            .nav-links {
                display: flex;
                gap: 1.5rem;
                margin-left: auto;
            }

            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }

            .nav-links a:hover {
                color: #ffffff;
                background-color: #111111;
            }

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

            .hero {
                margin-bottom: 3rem;
            }

            .hero-code {
                margin-top: 2rem;
                width: 100%;
                max-width: 900px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }

            .hero-code pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: left;
                grid-column: 1 / -1;
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

            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background-color: #0070f3;
                color: #ffffff;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-bottom: 2rem;
            }

            .status-dot {
                width: 6px;
                height: 6px;
                background-color: #00ff88;
                border-radius: 50%;
            }

            pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 1rem;
                overflow-x: auto;
                margin: 0;
            }

            code {
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                font-size: 0.85rem;
                line-height: 1.5;
                color: #ffffff;
            }

            /* Syntax highlighting */
            .keyword {
                color: #ff79c6;
            }

            .string {
                color: #f1fa8c;
            }

            .function {
                color: #50fa7b;
            }

            .class {
                color: #8be9fd;
            }

            .module {
                color: #8be9fd;
            }

            .variable {
                color: #f8f8f2;
            }

            .decorator {
                color: #ffb86c;
            }

            @media (max-width: 768px) {
                nav {
                    padding: 1rem;
                    flex-direction: column;
                    gap: 1rem;
                }

                .nav-links {
                    margin-left: 0;
                }

                main {
                    padding: 2rem 1rem;
                }

                h1 {
                    font-size: 2rem;
                }

                .hero-code {
                    grid-template-columns: 1fr;
                }

                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Vercel + FastAPI</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/data">API</a>
                </div>
            </nav>
        </header>
        <main>
            <div class="hero">
                <h1>Vercel + FastAPI</h1>
                <div class="hero-code">
                    <pre><code><span class="keyword">from</span> <span class="module">fastapi</span> <span class="keyword">import</span> <span class="class">FastAPI</span>

<span class="variable">app</span> = <span class="class">FastAPI</span>()

<span class="decorator">@app.get</span>(<span class="string">"/"</span>)
<span class="keyword">def</span> <span class="function">read_root</span>():
    <span class="keyword">return</span> {<span class="string">"Python"</span>: <span class="string">"on Vercel"</span>}</code></pre>
                </div>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Interactive API Docs</h3>
                    <p>Explore this API's endpoints with the interactive Swagger UI. Test requests and view response schemas in real-time.</p>
                    <a href="/docs">Open Swagger UI →</a>
                </div>

                <div class="card">
                    <h3>Sample Data</h3>
                    <p>Access sample JSON data through our REST API. Perfect for testing and development purposes.</p>
                    <a href="/api/data">Get Data →</a>
                </div>

            </div>
        </main>
    </body>
    </html>
    """
