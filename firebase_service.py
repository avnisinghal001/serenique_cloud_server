"""
Firebase Admin SDK Service for Serenique Cloud Server

Handles all Firebase Firestore operations for user persona management.
Stores user_persona collection with references to user IDs from auth.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from langchain_persona_architect import UserPersona, LiveUserState


class FirebaseService:
    """Service class for Firebase Firestore operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single Firebase Admin SDK initialization"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        if not self._initialized:
            self._initialize_firebase()
            self.db = firestore.client()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials"""
        
        # Try multiple methods to get credentials
        # Method 1: Check for FIREBASE_CREDENTIALS environment variable (JSON string)
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
        
        if firebase_creds_json:
            try:
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized from FIREBASE_CREDENTIALS env variable")
                return
            except Exception as e:
                print(f"⚠️  Failed to initialize from FIREBASE_CREDENTIALS: {e}")
        
        # Method 2: Check for GOOGLE_APPLICATION_CREDENTIALS (file path)
        google_app_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if google_app_creds and os.path.exists(google_app_creds):
            try:
                cred = credentials.Certificate(google_app_creds)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized from GOOGLE_APPLICATION_CREDENTIALS: {google_app_creds}")
                return
            except Exception as e:
                print(f"⚠️  Failed to initialize from GOOGLE_APPLICATION_CREDENTIALS: {e}")
        
        # Method 3: Check for local service account file
        local_cred_paths = [
            "firebase-service-account.json",
            "serviceAccountKey.json",
            "../serenique/android/app/google-services.json"  # Not recommended but fallback
        ]
        
        for path in local_cred_paths:
            if os.path.exists(path):
                try:
                    cred = credentials.Certificate(path)
                    firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase initialized from local file: {path}")
                    return
                except Exception as e:
                    print(f"⚠️  Failed to initialize from {path}: {e}")
        
        # Method 4: Use Application Default Credentials (for Google Cloud environment)
        try:
            firebase_admin.initialize_app()
            print("✅ Firebase initialized with Application Default Credentials")
            return
        except Exception as e:
            print(f"⚠️  Failed to initialize with Application Default Credentials: {e}")
        
        # If all methods fail
        raise ValueError(
            "❌ Could not initialize Firebase Admin SDK. Please provide credentials via:\n"
            "1. FIREBASE_CREDENTIALS environment variable (JSON string)\n"
            "2. GOOGLE_APPLICATION_CREDENTIALS environment variable (file path)\n"
            "3. Local service account JSON file\n"
            "4. Application Default Credentials (on Google Cloud)"
        )
    
    # ========================================================================
    # USER PERSONA OPERATIONS
    # ========================================================================
    
    def save_user_persona(self, persona: UserPersona) -> bool:
        """
        Save complete user persona to Firestore.
        
        Creates/updates document in 'user_persona' collection with user_id as doc ID.
        
        Args:
            persona: UserPersona object containing personality_profile and live_user_state
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert persona to dictionary
            persona_dict = persona.model_dump()
            
            # Add/update metadata
            persona_dict["updated_at"] = firestore.SERVER_TIMESTAMP
            persona_dict["version"] = "1.0"
            
            # Save to Firestore: user_persona/{user_id}
            doc_ref = self.db.collection("user_persona").document(persona.user_id)
            doc_ref.set(persona_dict, merge=True)
            
            print(f"✅ Saved persona for user {persona.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving persona for user {persona.user_id}: {e}")
            return False
    
    def get_user_persona(self, user_id: str) -> Optional[UserPersona]:
        """
        Retrieve user persona from Firestore.
        
        Args:
            user_id: User ID from Firebase Authentication
        
        Returns:
            UserPersona object if found, None otherwise
        """
        try:
            doc_ref = self.db.collection("user_persona").document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"ℹ️  No persona found for user {user_id}")
                return None
            
            persona_dict = doc.to_dict()
            
            # Remove Firestore metadata
            persona_dict.pop("updated_at", None)
            persona_dict.pop("version", None)
            
            # Convert to UserPersona object
            persona = UserPersona(**persona_dict)
            
            print(f"✅ Retrieved persona for user {user_id}")
            return persona
            
        except Exception as e:
            print(f"❌ Error retrieving persona for user {user_id}: {e}")
            return None
    
    def update_live_state(self, user_id: str, live_state: LiveUserState) -> bool:
        """
        Update only the live_user_state portion of a persona.
        
        More efficient than updating entire persona when only state changes.
        
        Args:
            user_id: User ID from Firebase Authentication
            live_state: Updated LiveUserState object
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection("user_persona").document(user_id)
            
            # Update only live_user_state field
            doc_ref.update({
                "live_user_state": live_state.model_dump(),
                "updated_at": firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Updated live state for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating live state for user {user_id}: {e}")
            return False
    
    def persona_exists(self, user_id: str) -> bool:
        """
        Check if persona exists for user.
        
        Args:
            user_id: User ID from Firebase Authentication
        
        Returns:
            bool: True if persona exists, False otherwise
        """
        try:
            doc_ref = self.db.collection("user_persona").document(user_id)
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            print(f"❌ Error checking persona existence for user {user_id}: {e}")
            return False
    
    # ========================================================================
    # USER COLLECTION OPERATIONS (for quiz data reference)
    # ========================================================================
    
    def get_user_quiz_data(self, user_id: str) -> Optional[Dict[int, str]]:
        """
        Retrieve quiz responses from users collection.
        
        Args:
            user_id: User ID from Firebase Authentication
        
        Returns:
            Dictionary mapping question IDs to answers, or None if not found
        """
        try:
            doc_ref = self.db.collection("users").document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"ℹ️  No user document found for {user_id}")
                return None
            
            user_data = doc.to_dict()
            quiz_responses = user_data.get("quizResponses", [])
            
            # Convert list format to dictionary format
            # From: [{"questionId": 1, "answer": "a"}, ...]
            # To: {1: "a", 2: "b", ...}
            quiz_dict = {}
            for response in quiz_responses:
                q_id = response.get("questionId")
                answer = response.get("answer")
                if q_id is not None and answer is not None:
                    quiz_dict[q_id] = answer
            
            print(f"✅ Retrieved quiz data for user {user_id}: {len(quiz_dict)} responses")
            return quiz_dict if quiz_dict else None
            
        except Exception as e:
            print(f"❌ Error retrieving quiz data for user {user_id}: {e}")
            return None
    
    def mark_persona_generated(self, user_id: str) -> bool:
        """
        Update users collection to indicate persona has been generated.
        
        Args:
            user_id: User ID from Firebase Authentication
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection("users").document(user_id)
            doc_ref.update({
                "personaGenerated": True,
                "personaGeneratedAt": firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Marked persona as generated for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error marking persona generated for user {user_id}: {e}")
            return False
    
    # ========================================================================
    # ANALYTICS AND MONITORING
    # ========================================================================
    
    def get_persona_stats(self) -> Dict[str, Any]:
        """
        Get statistics about persona generation.
        
        Returns:
            Dictionary with stats (total personas, recent generations, etc.)
        """
        try:
            personas_ref = self.db.collection("user_persona")
            personas = personas_ref.stream()
            
            total_count = 0
            recent_count = 0  # Last 24 hours
            
            now = datetime.utcnow()
            
            for persona in personas:
                total_count += 1
                
                persona_data = persona.to_dict()
                generated_at_str = persona_data.get("personality_profile", {}).get("generated_at")
                
                if generated_at_str:
                    try:
                        generated_at = datetime.fromisoformat(generated_at_str.replace('Z', '+00:00'))
                        hours_ago = (now - generated_at).total_seconds() / 3600
                        if hours_ago < 24:
                            recent_count += 1
                    except:
                        pass
            
            return {
                "total_personas": total_count,
                "recent_24h": recent_count,
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting persona stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Create singleton instance (will be initialized on first import)
firebase_service = FirebaseService()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test Firebase connection
    try:
        fs = FirebaseService()
        print("✅ Firebase service initialized successfully")
        
        # Test stats
        stats = fs.get_persona_stats()
        print(f"📊 Persona stats: {stats}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Firebase service: {e}")
