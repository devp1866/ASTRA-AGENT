import datetime
import uuid
import logging
from utils.db import db

logger = logging.getLogger(__name__)

# MongoDB collection
chats = db["chat_memory"]


def create_new_session():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    logger.info(f"🆕 New session created: {session_id}")
    return session_id

def clear_session(session_id: str):
    result = chats.delete_many({"session_id": session_id})
    logger.info(f"🧹 Cleared session memory for {session_id} ({result.deleted_count} messages deleted)")


def save_to_memory(session_id: str, role: str, message: str):
    if not session_id:
        session_id = create_new_session()

    try:
        chats.insert_one({
            "session_id": session_id,
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.utcnow()
        })
    except Exception as e:
        logger.error(f"⚠️ Error saving to memory for {session_id}: {e}")

#Retrieve entire memory history for a given session as structured list.
def get_memory(session_id: str):
    try:
        previous = chats.find({"session_id": session_id}).sort("timestamp", 1)
        memory = [{"role": chat.get("role", "unknown"), "message": chat.get("message", "")} for chat in previous]
        return memory
    except Exception as e:
        logger.error(f"⚠️ Error retrieving memory for {session_id}: {e}")
        return []

#Fetch only the recent few messages to minimize token usage.
def get_recent_messages(session_id: str, limit: int = 5):
    try:
        previous = chats.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
        history = [{"role": chat.get("role", "unknown"), "message": chat.get("message", "")} for chat in previous]
        return list(reversed(history))
    except Exception as e:
        logger.error(f"⚠️ Error retrieving recent messages for {session_id}: {e}")
        return []



# utilities
def count_session_messages(session_id: str):
    try:
        return chats.count_documents({"session_id": session_id})
    except Exception as e:
        logger.error(f"⚠️ Error counting messages for {session_id}: {e}")
        return 0
