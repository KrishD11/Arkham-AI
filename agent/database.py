"""MongoDB Atlas database service for Arkham AI"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure

from agent.config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB Atlas database operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize database service"""
        self.config = config or Config()
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connected = False
        
        if self.config.MONGODB_URI:
            self.connect()
        else:
            logger.warning("MONGODB_URI not configured. Database operations will be disabled.")
    
    def connect(self) -> bool:
        """Connect to MongoDB Atlas"""
        if not self.config.MONGODB_URI:
            logger.error("MONGODB_URI not configured")
            return False
        
        try:
            self.client = MongoClient(
                self.config.MONGODB_URI,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=15000,
                socketTimeoutMS=15000,
                tls=True,
                tlsAllowInvalidCertificates=False,
                retryWrites=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.config.MONGODB_DATABASE]
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB Atlas database: {self.config.MONGODB_DATABASE}")
            
            # Create indexes for better query performance
            self._create_indexes()
            
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._connected = False
            return False
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Indexes for risk_data collection
            risk_data_collection = self.get_collection("risk_data")
            risk_data_collection.create_index([("timestamp", -1)])  # Descending for recent first
            risk_data_collection.create_index([("category", 1)])
            risk_data_collection.create_index([("location", 1)])
            risk_data_collection.create_index([("source", 1)])
            risk_data_collection.create_index([("timestamp", -1), ("category", 1)])  # Compound index
            
            # Indexes for routes collection
            routes_collection = self.get_collection("routes")
            routes_collection.create_index([("route_id", 1)], unique=True)
            routes_collection.create_index([("origin", 1), ("destination", 1)])
            routes_collection.create_index([("status", 1)])
            
            # Indexes for assessments collection
            assessments_collection = self.get_collection("assessments")
            assessments_collection.create_index([("route_id", 1)])
            assessments_collection.create_index([("assessment_timestamp", -1)])
            assessments_collection.create_index([("risk_level", 1)])
            
            # Indexes for executions collection
            executions_collection = self.get_collection("executions")
            executions_collection.create_index([("shipment_id", 1)])
            executions_collection.create_index([("action_id", 1)], unique=True)
            executions_collection.create_index([("status", 1)])
            executions_collection.create_index([("created_at", -1)])
            
            # Indexes for logs collection
            logs_collection = self.get_collection("logs")
            logs_collection.create_index([("timestamp", -1)])
            logs_collection.create_index([("category", 1)])
            logs_collection.create_index([("level", 1)])
            logs_collection.create_index([("shipment_id", 1)])
            logs_collection.create_index([("route_id", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self._connected or not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            self._connected = False
            return False
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a MongoDB collection"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot get collection.")
            return None
        return self.db[collection_name]
    
    def insert_risk_data(self, risk_data_points: List[Dict[str, Any]]) -> int:
        """Insert risk data points into MongoDB"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot insert risk data.")
            return 0
        
        collection = self.get_collection(self.config.MONGODB_COLLECTION_RISK_DATA)
        if collection is None:
            return 0
        
        try:
            # Convert dataclass objects to dictionaries if needed
            documents = []
            for point in risk_data_points:
                if hasattr(point, '__dict__'):
                    doc = point.__dict__.copy()
                elif hasattr(point, '__dataclass_fields__'):
                    # Handle dataclass
                    from dataclasses import asdict
                    doc = asdict(point)
                else:
                    doc = dict(point)
                
                # Convert datetime to ISO format string for MongoDB
                if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
                    doc['timestamp'] = doc['timestamp'].isoformat()
                
                # Add metadata
                doc['stored_at'] = datetime.utcnow().isoformat()
                documents.append(doc)
            
            if documents:
                result = collection.insert_many(documents, ordered=False)
                logger.info(f"Inserted {len(result.inserted_ids)} risk data points into MongoDB")
                return len(result.inserted_ids)
            return 0
            
        except Exception as e:
            logger.error(f"Error inserting risk data: {e}")
            return 0
    
    def get_risk_data(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        days_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query risk data from MongoDB"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot query risk data.")
            return []
        
        collection = self.get_collection(self.config.MONGODB_COLLECTION_RISK_DATA)
        if collection is None:
            return []
        
        try:
            query = {}
            
            if category:
                query['category'] = category
            if location:
                query['location'] = {'$regex': location, '$options': 'i'}  # Case-insensitive
            if source:
                query['source'] = source
            if days_back:
                cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_back)
                query['timestamp'] = {'$gte': cutoff_date.isoformat()}
            
            cursor = collection.find(query).sort('timestamp', -1).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            from bson import ObjectId
            for result in results:
                if '_id' in result and isinstance(result['_id'], ObjectId):
                    result['_id'] = str(result['_id'])
            
            logger.info(f"Retrieved {len(results)} risk data points from MongoDB")
            return results
            
        except Exception as e:
            logger.error(f"Error querying risk data: {e}")
            return []
    
    def save_route_assessment(self, assessment: Dict[str, Any]) -> Optional[str]:
        """Save a route risk assessment to MongoDB"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot save assessment.")
            return None
        
        collection = self.get_collection(self.config.MONGODB_COLLECTION_ASSESSMENTS)
        if collection is None:
            return None
        
        try:
            # Convert datetime objects to ISO strings
            doc = dict(assessment)
            if 'assessment_timestamp' in doc and isinstance(doc['assessment_timestamp'], datetime):
                doc['assessment_timestamp'] = doc['assessment_timestamp'].isoformat()
            
            doc['stored_at'] = datetime.utcnow().isoformat()
            
            result = collection.insert_one(doc)
            logger.info(f"Saved route assessment with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving route assessment: {e}")
            return None
    
    def save_execution(self, execution: Dict[str, Any]) -> Optional[str]:
        """Save an execution action to MongoDB"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot save execution.")
            return None
        
        collection = self.get_collection(self.config.MONGODB_COLLECTION_EXECUTIONS)
        if collection is None:
            return None
        
        try:
            doc = dict(execution)
            if 'created_at' in doc and isinstance(doc['created_at'], datetime):
                doc['created_at'] = doc['created_at'].isoformat()
            if 'executed_at' in doc and isinstance(doc['executed_at'], datetime):
                doc['executed_at'] = doc['executed_at'].isoformat()
            
            doc['stored_at'] = datetime.utcnow().isoformat()
            
            result = collection.insert_one(doc)
            logger.info(f"Saved execution with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving execution: {e}")
            return None
    
    def save_log(self, log_entry: Dict[str, Any]) -> Optional[str]:
        """Save a log entry to MongoDB"""
        if not self.is_connected():
            logger.warning("Database not connected. Cannot save log.")
            return None
        
        collection = self.get_collection(self.config.MONGODB_COLLECTION_LOGS)
        if collection is None:
            return None
        
        try:
            doc = dict(log_entry)
            if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
                doc['timestamp'] = doc['timestamp'].isoformat()
            
            doc['stored_at'] = datetime.utcnow().isoformat()
            
            result = collection.insert_one(doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving log: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB connection closed")


# Global database service instance
_database_service_instance: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Singleton pattern for DatabaseService"""
    global _database_service_instance
    if _database_service_instance is None:
        _database_service_instance = DatabaseService()
    return _database_service_instance

