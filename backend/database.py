import os
import json
import datetime
from typing import List, Optional

class LocalFileDB:
    """Simple JSON file-based database - no MongoDB needed"""
    
    def __init__(self, filename="luna_memory.json"):
        self.filename = filename
        self._ensure_file()
    
    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({
                    "conversations": [],
                    "visual_memories": [],
                    "generated_images": []
                }, f)
    
    def _read_data(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return {"conversations": [], "visual_memories": [], "generated_images": []}
    
    def _write_data(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    @property
    def conversations(self):
        return self._Collection(self, "conversations")
    
    @property
    def visual_memories(self):
        return self._Collection(self, "visual_memories")
    
    @property
    def generated_images(self):
        return self._Collection(self, "generated_images")
    
    class _Collection:
        def __init__(self, db_instance, name):
            self.db = db_instance
            self.name = name
        
        def find(self, query=None):
            data = self.db._read_data()
            rows = data.get(self.name, [])
            
            if query and "user_id" in query:
                rows = [r for r in rows if r.get("user_id") == query["user_id"]]
            
            class Cursor(list):
                def sort(self, key, direction=1):
                    try:
                        reverse = (direction == -1)
                        return Cursor(sorted(self, key=lambda x: x.get(key, ""), reverse=reverse))
                    except:
                        return self
                
                def limit(self, n):
                    return Cursor(self[:n])
            
            return Cursor(rows)
        
        def insert_one(self, doc):
            data = self.db._read_data()
            if self.name not in data:
                data[self.name] = []
            
            if "timestamp" in doc and isinstance(doc["timestamp"], datetime.datetime):
                doc["timestamp"] = doc["timestamp"].isoformat()
            
            data[self.name].append(doc)
            self.db._write_data(data)
            return True

# Initialize database
db = LocalFileDB()

# Export collections
conversations_collection = db.conversations
visual_memory_collection = db.visual_memories
generated_images_collection = db.generated_images
