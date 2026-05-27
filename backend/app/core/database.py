import os
import json
import logging
from pymongo import MongoClient
from app.core.config import settings

logger = logging.getLogger("app.database")

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.is_fallback = False
        self.client = None
        self.mock_db = {
            "users": {},
            "expenses": {},
            "budgets": {}
        }
        self.mock_file_path = "mock_database.json"
        self.connect()

    def connect(self):
        """Attempts to connect to MongoDB; falls back to offline storage if it fails."""
        try:
            # Allow sufficient time (10 seconds) for remote MongoDB Atlas handshakes and DNS discovery
            self.client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=10000)
            # Trigger serverSelectionTimeoutMS if cluster is offline
            self.client.server_info() 
            self.db = self.client.get_database()
            logger.info("Successfully connected to MongoDB Cluster.")
            print("[INFO] Successfully connected to MongoDB Cluster.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Activating localized offline JSON DB engine.")
            print(f"[WARNING] MongoDB connection failed ({e}). Activating localized offline JSON DB engine.")
            self.is_fallback = True
            self.load_mock_data()

    def load_mock_data(self):
        """Loads data from local mock file system if it exists"""
        if os.path.exists(self.mock_file_path):
            try:
                with open(self.mock_file_path, "r") as f:
                    self.mock_db = json.load(f)
                logger.info("Loaded offline data successfully.")
            except Exception as e:
                logger.error(f"Error loading offline database files: {e}")

    def save_mock_data(self):
        """Saves active mock data state to local JSON file"""
        if not self.is_fallback:
            return
        try:
            with open(self.mock_file_path, "w") as f:
                json.dump(self.mock_db, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to persist offline database data: {e}")

    # --- Standard Generic CRUD Wrappers Supporting Both MongoDB & Mock Database ---
    
    def find_one(self, collection_name: str, query: dict) -> dict:
        if not self.is_fallback:
            return self.db[collection_name].find_one(query)
        
        # Mock search logic
        for item_id, item in self.mock_db.get(collection_name, {}).items():
            match = True
            for k, v in query.items():
                # Handle special ObjectId matching in queries
                if k == "_id":
                    if str(item.get("_id")) != str(v) and item_id != str(v):
                        match = False
                elif item.get(k) != v:
                    match = False
            if match:
                return item
        return None

    def find_many(self, collection_name: str, query: dict) -> list:
        if not self.is_fallback:
            return list(self.db[collection_name].find(query))
        
        results = []
        for item_id, item in self.mock_db.get(collection_name, {}).items():
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(item.get("_id")) != str(v) and item_id != str(v):
                        match = False
                elif item.get(k) != v:
                    match = False
            if match:
                results.append(item)
        return results

    def insert_one(self, collection_name: str, document: dict) -> str:
        if not self.is_fallback:
            res = self.db[collection_name].insert_one(document)
            # Add string ID representation
            document["_id"] = str(res.inserted_id)
            return document["_id"]
        
        # Offline schema auto-increment ID
        import uuid
        new_id = str(uuid.uuid4())
        document["_id"] = new_id
        if collection_name not in self.mock_db:
            self.mock_db[collection_name] = {}
        self.mock_db[collection_name][new_id] = document
        self.save_mock_data()
        return new_id

    def update_one(self, collection_name: str, query: dict, update_data: dict) -> bool:
        if not self.is_fallback:
            res = self.db[collection_name].update_one(query, {"$set": update_data})
            return res.modified_count > 0
        
        # Offline update logic
        target = self.find_one(collection_name, query)
        if target:
            target_id = target["_id"]
            self.mock_db[collection_name][target_id].update(update_data)
            self.save_mock_data()
            return True
        return False

    def delete_one(self, collection_name: str, query: dict) -> bool:
        if not self.is_fallback:
            res = self.db[collection_name].delete_one(query)
            return res.deleted_count > 0
        
        # Offline delete logic
        target = self.find_one(collection_name, query)
        if target:
            target_id = target["_id"]
            del self.mock_db[collection_name][target_id]
            self.save_mock_data()
            return True
        return False

# Initialize Global Singleton DB Driver Instance
db_manager = DatabaseManager()
