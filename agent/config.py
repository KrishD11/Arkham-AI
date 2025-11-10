"""Configuration settings for Arkham AI agent"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "arkham-ai-477701")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Service Account Configuration
    SERVICE_ACCOUNT_EMAIL = os.getenv("SERVICE_ACCOUNT_EMAIL", "arkham-ai@arkham-ai-477701.iam.gserviceaccount.com")
    SERVICE_ACCOUNT_KEY_ID = os.getenv("SERVICE_ACCOUNT_KEY_ID", "881b8567ceffea3c3d12be333417274f0e0f9867")
    SERVICE_ACCOUNT_UNIQUE_ID = os.getenv("SERVICE_ACCOUNT_UNIQUE_ID", "113099405793271955965")
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Agent Configuration
    AGENT_NAME = os.getenv("AGENT_NAME", "Arkham AI")
    
    # API Configuration
    API_PREFIX = "/api"
    
    # External API Keys (optional - for real data sources)
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    GEOPOLITICAL_API_KEY = os.getenv("GEOPOLITICAL_API_KEY", "")
    PORT_API_KEY = os.getenv("PORT_API_KEY", "")
    TRADE_NEWS_API_KEY = os.getenv("TRADE_NEWS_API_KEY", "")
    
    # ACLED API Configuration
    ACLED_USERNAME = os.getenv("ACLED_USERNAME", "")
    ACLED_PASSWORD = os.getenv("ACLED_PASSWORD", "")
    
    # MongoDB Atlas Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "arkham_ai")
    MONGODB_COLLECTION_RISK_DATA = os.getenv("MONGODB_COLLECTION_RISK_DATA", "risk_data")
    MONGODB_COLLECTION_ROUTES = os.getenv("MONGODB_COLLECTION_ROUTES", "routes")
    MONGODB_COLLECTION_ASSESSMENTS = os.getenv("MONGODB_COLLECTION_ASSESSMENTS", "assessments")
    MONGODB_COLLECTION_EXECUTIONS = os.getenv("MONGODB_COLLECTION_EXECUTIONS", "executions")
    MONGODB_COLLECTION_LOGS = os.getenv("MONGODB_COLLECTION_LOGS", "logs")

