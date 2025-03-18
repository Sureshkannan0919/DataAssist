from typing import List, Dict, Any, Optional, Tuple, Union
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
import pandas as pd

class PostgresManager:
    def __init__(self):
        """Initialize PostgreSQL Manager with no connection"""
        self.connection = None
        self.cursor = None
        self.current_db = None

    def connect(self, connection_params: Dict[str, str]) -> bool:
        """
        Connect to PostgreSQL using connection parameters
        
        Args:
            connection_params (Dict[str, str]): Dictionary with connection parameters
                (host, port, user, password, database)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**connection_params)
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            self.current_db = connection_params.get('database')
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def list_databases(self) -> List[str]:
        """
        Get list of all database names
        
        Returns:
            List[str]: List of database names
        """
        if not self.connection:
            raise ConnectionError("Not connected to PostgreSQL")
        
        old_isolation_level = self.connection.isolation_level
        self.connection.set_isolation_level(0)  # AUTOCOMMIT
        
        try:
            self.cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            databases = [row[0] for row in self.cursor.fetchall()]
            return databases
        finally:
            self.connection.set_isolation_level(old_isolation_level)

    def use_database(self, db_name: str) -> bool:
        """
        Switch to specified database
        
        Args:
            db_name (str): Name of database to use
            
        Returns:
            bool: True if successful, False if database doesn't exist
        """
        if not self.connection:
            raise ConnectionError("Not connected to PostgreSQL")
        
        if db_name in self.list_databases():
            # Close current connection and reconnect to new database
            connection_params = {
                'host': self.connection.info.host,
                'port': self.connection.info.port,
                'user': self.connection.info.user,
                'password': self.connection.info.password,
                'database': db_name
            }
            self.close_connection()
            return self.connect(connection_params)
        return False

    def list_tables(self) -> List[str]:
        """
        Get list of tables in current database
        
        Returns:
            List[str]: List of table names
        """
        if not self.connection:
            raise ConnectionError("Not connected to PostgreSQL")
        
        self.cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> Tuple[List[str], List[str]]:
        """
        Get schema (column names and their data types) of specified table
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Tuple[List[str], List[str]]: Lists of column names and their data types
        """
        if not self.connection:
            raise ConnectionError("Not connected to PostgreSQL")
        
        self.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        results = self.cursor.fetchall()
        columns = [row[0] for row in results]
        data_types = [row[1] for row in results]
        
        return columns, data_types

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
            raise ConnectionError("Not connected to PostgreSQL")
        
        try:
            self.cursor.execute(query, params or ())
            
            if self.cursor.description:  # Check if query returns data
                columns = [desc[0] for desc in self.cursor.description]
                return pd.DataFrame(self.cursor.fetchall(), columns=columns)
            else:
                self.connection.commit()
                return pd.DataFrame()  # Empty DataFrame for non-SELECT queries
                
        except Exception as e:
            self.connection.rollback()
            print(f"Query error: {str(e)}")
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
            raise ConnectionError("Not connected to PostgreSQL")
        
        query = sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table_name))
        
        try:
            self.cursor.execute(query, (limit,))
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(self.cursor.fetchall(), columns=columns)
        except Exception as e:
            print(f"Error fetching sample data: {str(e)}")
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
            raise ConnectionError("Not connected to PostgreSQL")
        
        try:
            for query, params in queries:
                self.cursor.execute(query, params or ())
            
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Transaction error: {str(e)}")
            return False

    def close_connection(self):
        """Close PostgreSQL connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_db = None