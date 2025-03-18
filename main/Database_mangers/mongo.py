from typing import List, Dict, Any, Optional
from pymongo import MongoClient 
from pymongo.database import Database 
from pymongo.collection import Collection
import pandas as pd
from bson import ObjectId

class MongoManager:
    def __init__(self):
        """Initialize MongoDB Manager with no connection"""
        self.client = None
        self.current_db = None
        self.current_collection = None

    def connect(self, connection_url: str) -> bool:
        """
        Connect to MongoDB using connection URL
        
        Args:
            connection_url (str): MongoDB connection string
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(connection_url)
            # Test connection
            self.client.server_info()
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def list_databases(self):
        """
        Get list of all database names
        
        Returns:
            List[str]: List of database names
        """
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        return self.client.list_database_names()

    def use_database(self, db_name: str) -> bool:
        """
        Switch to specified database
        
        Args:
            db_name (str): Name of database to use
            
        Returns:
            bool: True if successful, False if database doesn't exist
        """
        if not self.client:
            raise ConnectionError("Not connected to MongoDB")
        
        if db_name in self.list_databases():
            self.current_db = self.client[db_name]
            self.current_collection = None  # Reset current collection
            return True
        return False

    def list_collections(self) -> List[str]:
        """
        Get list of collections in current database
        
        Returns:
            List[str]: List of collection names
        """
        if self.current_db == None:
            raise ValueError("No database selected")
        return self.current_db.list_collection_names()

    def use_collection(self, collection_name: str) -> bool:
        """
        Switch to specified collection
        
        Args:
            collection_name (str): Name of collection to use
            
        Returns:
            bool: True if successful, False if collection doesn't exist
        """
        if self.current_db == None:
            raise ValueError("No database selected")
        
        if collection_name in self.list_collections():
            self.current_collection = self.current_db[collection_name]
            return True
        return False

    def get_collection_schema(self) -> Dict[str, List[str]]:
        """
        Get schema (field names and their data types) of current collection
        
        Returns:
            Dict[str, List[str]]: Dictionary with field names and their possible data types
        """
        if self.current_collection == None:
            raise ValueError("No collection selected")

        schema = {}
        # Sample documents to infer schema
        for doc in self.current_collection.find().limit(100):
            for field, value in doc.items():
                if field not in schema:
                    schema[field] = set()
                schema[field].add(type(value).__name__)

        # Convert sets to lists for better readability
        schema = {k: list(v) for k, v in schema.items()}
        column = list(schema.keys())
        data_types = [list(v)[0] for v in schema.values()]
        return column,data_types

    def execute_query(self, query: Dict, projection: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a MongoDB query on current collection
        
        Args:
            query (Dict): MongoDB query dictionary
            projection (Dict, optional): Fields to include/exclude in results
            
        Returns:
            List[Dict]: Query results
        """
        if self.current_collection == None:
            raise ValueError("No collection selected")
        
        try:
            cursor = self.current_collection.find(query, projection)
            return pd.DataFrame(list(cursor))
        except Exception as e:
            print(f"Query error: {str(e)}")
            return []

    def execute_aggregation(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Execute an aggregation pipeline on current collection
        
        Args:
            pipeline (List[Dict]): MongoDB aggregation pipeline
            
        Returns:
            List[Dict]: Aggregation results
        """
        if not self.current_collection:
            raise ValueError("No collection selected")
        
        try:
            return list(self.current_collection.aggregate(pipeline))
        except Exception as e:
            print(f"Aggregation error: {str(e)}")
            return []

    def get_sample_data(self, limit: int = 5) -> List[Dict]:
        """
        Get sample documents from current collection
        
        Args:
            limit (int): Number of documents to return
            
        Returns:
            List[Dict]: Sample documents
        """
        if self.current_collection == None:
            raise ValueError("No collection selected")
        
        df=pd.DataFrame(list(self.current_collection.find().limit(limit)))
        return df
        
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.current_db = None
            self.current_collection = None
