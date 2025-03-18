from typing import List, Dict, Any, Optional, Tuple, Union
import mysql.connector
from mysql.connector import errorcode
import pandas as pd

class MySqlManager:
    def __init__(self):
        """Initialize MySQL Manager with no connection"""
        self.connection = None
        self.cursor = None
        self.current_db = None

    def connect(self, connection_params: Dict[str, str]) -> bool:
        """
        Connect to MySQL using connection parameters
        
        Args:
            connection_params (Dict[str, str]): Dictionary with connection parameters
                (host, port, user, password, database)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(**connection_params)
            self.cursor = self.connection.cursor(dictionary=True)
            self.current_db = connection_params.get('database')
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: Invalid username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Error: Database '{connection_params.get('database')}' does not exist")
            else:
                print(f"Connection error: {str(err)}")
            return False

    def list_databases(self) -> List[str]:
        """
        Get list of all database names
        
        Returns:
            List[str]: List of database names
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        try:
            self.cursor.execute("SHOW DATABASES")
            return [row['Database'] for row in self.cursor.fetchall()]
        except mysql.connector.Error as err:
            print(f"Error listing databases: {str(err)}")
            return []

    def use_database(self, db_name: str) -> bool:
        """
        Switch to specified database
        
        Args:
            db_name (str): Name of database to use
            
        Returns:
            bool: True if successful, False if database doesn't exist
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        if db_name in self.list_databases():
            try:
                self.cursor.execute(f"USE {db_name}")
                self.current_db = db_name
                return True
            except mysql.connector.Error as err:
                print(f"Error switching database: {str(err)}")
                return False
        return False

    def list_tables(self) -> List[str]:
        """
        Get list of tables in current database
        
        Returns:
            List[str]: List of table names
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        if not self.current_db:
            raise ValueError("No database selected")
        
        try:
            self.cursor.execute("SHOW TABLES")
            return [list(row.values())[0] for row in self.cursor.fetchall()]
        except mysql.connector.Error as err:
            print(f"Error listing tables: {str(err)}")
            return []

    def get_table_schema(self, table_name: str) -> Tuple[List[str], List[str]]:
        """
        Get schema (column names and their data types) of specified table
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Tuple[List[str], List[str]]: Lists of column names and their data types
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        if not self.current_db:
            raise ValueError("No database selected")
        
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            results = self.cursor.fetchall()
            
            columns = [row['Field'] for row in results]
            data_types = [row['Type'] for row in results]
            
            return columns, data_types
        except mysql.connector.Error as err:
            print(f"Error getting table schema: {str(err)}")
            return [], []

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        Execute a SQL query
        
        Args:
            query (str): SQL query string
            params (Tuple, optional): Parameters for the query
            
        Returns:
            pd.DataFrame: Query results as a DataFrame
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        try:
            self.cursor.execute(query, params or ())
            
            if self.cursor.description:  # Check if query returns data
                return pd.DataFrame(self.cursor.fetchall())
            else:
                self.connection.commit()
                return pd.DataFrame()  # Empty DataFrame for non-SELECT queries
                
        except mysql.connector.Error as err:
            self.connection.rollback()
            print(f"Query error: {str(err)}")
            return pd.DataFrame()

    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """
        Get sample rows from specified table
        
        Args:
            table_name (str): Name of the table
            limit (int): Number of rows to return
            
        Returns:
            pd.DataFrame: Sample rows as a DataFrame
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        if not self.current_db:
            raise ValueError("No database selected")
        
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
            return pd.DataFrame(self.cursor.fetchall())
        except mysql.connector.Error as err:
            print(f"Error fetching sample data: {str(err)}")
            return pd.DataFrame()

    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        Execute multiple queries as a single transaction
        
        Args:
            queries (List[Tuple[str, Optional[Tuple]]]): List of (query, params) tuples
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
        
        try:
            for query, params in queries:
                self.cursor.execute(query, params or ())
            
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            self.connection.rollback()
            print(f"Transaction error: {str(err)}")
            return False

    def create_database(self, db_name: str) -> bool:
        """
        Create a new database
        
        Args:
            db_name (str): Name of the database to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection:
            raise ConnectionError("Not connected to MySQL")
            
        try:
            self.cursor.execute(f"CREATE DATABASE {db_name}")
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error creating database: {str(err)}")
            return False

    def close_connection(self):
        """Close MySQL connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_db = None