import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    logger.critical("CRITICAL SECURITY ERROR: MONGO_URI environment variable is missing. Database cannot connect.")
    raise ValueError("Server Configuration Error: Missing Database Credentials")

db = None
try:
    # Adding connection timeout for production readiness
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["customer_support_agent"]
    
    # Ensure indexes for production performance
    db["chat_memory"].create_index([("session_id", ASCENDING), ("timestamp", ASCENDING)])
    db["queries"].create_index([("session_id", ASCENDING)])
    
    logger.info("MongoDB connection successful and indexes verified.")
except Exception as e:
    logger.error(f"MongoDB connection failed: {str(e)}")

# Helper function to get a specific collection
def get_collection(name: str):
    if db is not None:
        return db[name]
    else:
        logger.error("Attempted to access collection but DB connection is not established.")
        raise ConnectionError("Database connection not established.")
