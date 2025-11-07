"""
Firebase Admin SDK Service for Serenique Cloud Server

Handles all Firebase Firestore operations for user persona management.
Stores user_persona collection with references to user IDs from auth.
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from langchain_persona_architect import UserPersona, LiveUserState

# Load environment variables from .env file
load_dotenv()


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
            
            # Initialize in-memory cache for chat history
            self._chat_cache: Dict[str, Dict] = {}
            self._cache_ttl = 300  # 5 minutes TTL (in seconds)
            
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK from FIREBASE_CREDENTIALS environment variable"""
        
        # Skip if already initialized globally
        if firebase_admin._apps:
            print("ℹ️ Firebase already initialized (using existing app)")
            return
            
        try:
            # Method 1: Load from FIREBASE_CREDENTIALS environment variable
            firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
            
            if firebase_creds_json:
                try:
                    cred_dict = json.loads(firebase_creds_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized from FIREBASE_CREDENTIALS env variable")
                    return
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse FIREBASE_CREDENTIALS: {e}")
                except Exception as e:
                    print(f"⚠️ Failed to initialize from FIREBASE_CREDENTIALS: {e}")
            
            # Method 2: Check for GOOGLE_APPLICATION_CREDENTIALS (file path)
            google_app_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if google_app_creds and os.path.exists(google_app_creds):
                try:
                    cred = credentials.Certificate(google_app_creds)
                    firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase initialized from GOOGLE_APPLICATION_CREDENTIALS: {google_app_creds}")
                    return
                except Exception as e:
                    print(f"⚠️ Failed to initialize from GOOGLE_APPLICATION_CREDENTIALS: {e}")
            
            # Method 3: Check for local service account file
            local_cred_paths = [
                "serenique-avni-firebase-adminsdk-fbsvc-40c2275922.json",
                "firebase-service-account.json",
                "serviceAccountKey.json",
            ]
            
            for path in local_cred_paths:
                if os.path.exists(path):
                    try:
                        cred = credentials.Certificate(path)
                        firebase_admin.initialize_app(cred)
                        print(f"✅ Firebase initialized from local file: {path}")
                        return
                    except Exception as e:
                        print(f"⚠️ Failed to initialize from {path}: {e}")
            
            # If all methods fail
            raise ValueError(
                "❌ Could not initialize Firebase Admin SDK. Please provide credentials via:\n"
                "1. FIREBASE_CREDENTIALS environment variable (JSON string)\n"
                "2. GOOGLE_APPLICATION_CREDENTIALS environment variable (file path)\n"
                "3. Local service account JSON file\n"
            )
            
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize Firebase: {e}")

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
    # CHAT HISTORY OPERATIONS
    # ========================================================================
    
    def save_chat_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a chat message to Firestore.
        
        Stores in chat_history/{user_id}/messages/{message_id}
        
        Args:
            user_id: User ID from Firebase Authentication
            role: "user" or "assistant"
            content: Message text
            metadata: Optional metadata (mood, context, etc.)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message_data = {
                "role": role,
                "content": content,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "created_at": datetime.utcnow().isoformat()
            }
            
            if metadata:
                message_data["metadata"] = metadata
            
            # Save to chat_history/{user_id}/messages subcollection
            messages_ref = self.db.collection("chat_history").document(user_id).collection("messages")
            messages_ref.add(message_data)
            
            # Update last message timestamp in parent doc
            chat_ref = self.db.collection("chat_history").document(user_id)
            chat_ref.set({
                "last_message_at": firestore.SERVER_TIMESTAMP,
                "user_id": user_id,
                "total_messages": firestore.Increment(1)
            }, merge=True)
            
            # ⚡ Invalidate cache (force fresh data on next request)
            self.invalidate_chat_cache(user_id)
            
            print(f"✅ Saved {role} message for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving chat message for user {user_id}: {e}")
            return False
    
    def get_chat_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a user.
        
        Args:
            user_id: User ID from Firebase Authentication
            limit: Maximum number of messages to retrieve (default 50)
        
        Returns:
            List of message dictionaries ordered by timestamp
        """
        try:
            messages_ref = (
                self.db.collection("chat_history")
                .document(user_id)
                .collection("messages")
                .order_by("created_at", direction=firestore.Query.ASCENDING)
                .limit(limit)
            )
            
            messages = messages_ref.stream()
            
            chat_history = []
            for msg in messages:
                msg_data = msg.to_dict()
                chat_history.append({
                    "role": msg_data.get("role"),
                    "content": msg_data.get("content"),
                    "timestamp": msg_data.get("created_at"),
                    "metadata": msg_data.get("metadata", {})
                })
            
            print(f"✅ Retrieved {len(chat_history)} messages for user {user_id}")
            return chat_history
            
        except Exception as e:
            print(f"❌ Error retrieving chat history for user {user_id}: {e}")
            return []
    
    def get_chat_history_optimized(
        self,
        user_id: str,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        ⚡ OPTIMIZED: Retrieve chat history with in-memory caching.
        
        Performance Strategy:
        - Tier 1: Check in-memory cache (0ms - instant!)
        - Tier 2: Fetch from Firebase (~100ms)
        - Cache expires after 5 minutes
        - Auto-invalidated when new messages saved
        
        Args:
            user_id: User ID from Firebase Authentication
            limit: Number of recent messages (default 10, optimized for AI)
            use_cache: Whether to use cache (default True)
        
        Returns:
            List of recent messages with role, content, timestamp
        """
        cache_key = f"{user_id}_chat_{limit}"
        
        # Tier 1: Check in-memory cache
        if use_cache and cache_key in self._chat_cache:
            cached_data = self._chat_cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data["timestamp"])
            
            # Check if cache is still valid (within TTL)
            age_seconds = (datetime.utcnow() - cache_time).total_seconds()
            if age_seconds < self._cache_ttl:
                print(f"✅ Cache HIT for {user_id} (age: {int(age_seconds)}s, saved ~100ms)")
                return cached_data["messages"]
            else:
                print(f"⏰ Cache EXPIRED for {user_id} (age: {int(age_seconds)}s)")
        
        print(f"❌ Cache MISS for {user_id} - Fetching from Firebase...")
        
        # Tier 2: Fetch from Firebase (cache miss or expired)
        try:
            messages_ref = (
                self.db.collection("chat_history")
                .document(user_id)
                .collection("messages")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)  # Only fetch what we need!
            )
            
            docs = messages_ref.stream()
            messages = []
            
            for doc in docs:
                data = doc.to_dict()
                messages.append({
                    'role': data.get('role', 'user'),
                    'content': data.get('content', ''),
                    'timestamp': data.get('created_at', ''),
                    'metadata': data.get('metadata', {})
                })
            
            # Reverse to chronological order (oldest first)
            messages.reverse()
            
            # Store in cache
            self._chat_cache[cache_key] = {
                "messages": messages,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"💾 Cached {len(messages)} messages for {user_id}")
            return messages
            
        except Exception as e:
            print(f"❌ Error fetching chat history: {e}")
            return []
    
    def invalidate_chat_cache(self, user_id: str):
        """
        Invalidate all cached chat history for a user.
        Called automatically when new messages are saved.
        
        Args:
            user_id: User ID to invalidate cache for
        """
        keys_to_remove = [k for k in self._chat_cache.keys() if k.startswith(user_id)]
        removed_count = len(keys_to_remove)
        
        for key in keys_to_remove:
            del self._chat_cache[key]
        
        if removed_count > 0:
            print(f"🗑️ Invalidated {removed_count} cache entries for {user_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring performance.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_cached_users": len(set(k.split('_')[0] for k in self._chat_cache.keys())),
            "total_cache_entries": len(self._chat_cache),
            "cache_ttl_seconds": self._cache_ttl,
            "cached_user_ids": list(set(k.split('_')[0] for k in self._chat_cache.keys()))
        }
    
    def clear_chat_history(self, user_id: str) -> bool:
        """
        Clear all chat history for a user.
        
        Args:
            user_id: User ID from Firebase Authentication
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete all messages in subcollection
            messages_ref = (
                self.db.collection("chat_history")
                .document(user_id)
                .collection("messages")
            )
            
            # Batch delete
            batch = self.db.batch()
            for msg in messages_ref.stream():
                batch.delete(msg.reference)
            batch.commit()
            
            print(f"✅ Cleared chat history for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing chat history for user {user_id}: {e}")
            return False
    
    # ========================================================================
    # KEY INSIGHTS - Long-term Memory (Important Conversation Moments)
    # ========================================================================
    
    def save_key_insight(
        self,
        user_id: str,
        insight_type: str,
        content: str,
        original_message: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Save important conversation insights for long-term memory.
        
        This allows the chatbot to remember key moments even after 1000s of messages.
        Examples: stressors mentioned, breakthroughs, support needs, milestones.
        
        Args:
            user_id: User ID
            insight_type: Type of insight - "stressor", "breakthrough", "support_need", "milestone", "crisis"
            content: Summary of the insight (e.g., "User was scolded by teacher publicly")
            original_message: Original message from user (for context)
            timestamp: When this was discussed (defaults to now)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            timestamp = timestamp or datetime.utcnow().isoformat()
            
            insight_data = {
                'insight_type': insight_type,
                'content': content,
                'original_message': original_message[:500],  # Limit to 500 chars
                'timestamp': timestamp,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Save to chat_insights/{user_id}/insights/{auto_id}
            insights_ref = (
                self.db.collection('chat_insights')
                .document(user_id)
                .collection('insights')
            )
            insights_ref.add(insight_data)
            
            # Update metadata in parent document
            meta_ref = self.db.collection('chat_insights').document(user_id)
            meta_ref.set({
                'user_id': user_id,
                'total_insights': firestore.Increment(1),
                'last_insight_at': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            print(f"💡 Saved key insight for {user_id}: [{insight_type}] {content[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error saving key insight: {e}")
            return False
    
    def get_relevant_insights(
        self,
        user_id: str,
        limit: int = 5,
        insight_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent key insights for context enrichment.
        
        Returns the most recent important conversation moments to provide
        long-term memory context beyond the last 10 messages.
        
        Args:
            user_id: User ID
            limit: Number of insights to retrieve (default 5)
            insight_types: Optional filter by types (e.g., ["stressor", "breakthrough"])
        
        Returns:
            List of insights ordered chronologically (oldest to newest)
        """
        try:
            insights_ref = (
                self.db.collection('chat_insights')
                .document(user_id)
                .collection('insights')
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .limit(limit * 2)  # Fetch more if we need to filter
            )
            
            docs = insights_ref.stream()
            insights = []
            
            for doc in docs:
                data = doc.to_dict()
                
                # Filter by type if specified
                if insight_types and data.get('insight_type') not in insight_types:
                    continue
                
                insights.append({
                    'id': doc.id,
                    'type': data.get('insight_type'),
                    'content': data.get('content'),
                    'original_message': data.get('original_message'),
                    'timestamp': data.get('timestamp'),
                    'created_at': data.get('created_at')
                })
                
                if len(insights) >= limit:
                    break
            
            # Reverse to chronological order (oldest first)
            insights.reverse()
            
            print(f"💡 Retrieved {len(insights)} key insights for {user_id}")
            return insights
            
        except Exception as e:
            print(f"❌ Error fetching insights: {e}")
            return []
    
    def delete_insight(self, user_id: str, insight_id: str) -> bool:
        """
        Delete a specific key insight.
        
        Args:
            user_id: User ID
            insight_id: Insight document ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            insight_ref = (
                self.db.collection('chat_insights')
                .document(user_id)
                .collection('insights')
                .document(insight_id)
            )
            insight_ref.delete()
            
            print(f"🗑️ Deleted insight {insight_id} for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting insight: {e}")
            return False
    
    def get_insights_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about saved insights for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with insight statistics
        """
        try:
            meta_ref = self.db.collection('chat_insights').document(user_id)
            meta_doc = meta_ref.get()
            
            if meta_doc.exists:
                meta_data = meta_doc.to_dict()
                return {
                    'total_insights': meta_data.get('total_insights', 0),
                    'last_insight_at': meta_data.get('last_insight_at')
                }
            else:
                return {
                    'total_insights': 0,
                    'last_insight_at': None
                }
                
        except Exception as e:
            print(f"❌ Error fetching insights stats: {e}")
            return {'total_insights': 0, 'last_insight_at': None}
    
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
