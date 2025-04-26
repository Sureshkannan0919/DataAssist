import datetime
from threading import Lock


class DatabaseSessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSessionManager, cls).__new__(cls)
            cls._instance._sessions = {}
            cls._instance._lock = Lock()
        return cls._instance

    def create_session(self, user_id, user_name):
        """Create a new session using user ID from login."""
        with self._lock:
            session_id = str(user_id)
            self._sessions[session_id] = {
                'db_type':None,
                'manager': None,
                'current_database': None,
                'current_collection': None,
                'current_table':None,
                'user_id': user_id,
                'user_name': user_name,
                'created_at': datetime.datetime.now(),
                'query':None,
                'input_query':None,
                'data_frame':None,
                'pandas_df':None,
            }
            return session_id

    def get_session(self, user_id):
        """Retrieve a session by user ID."""
        return self._sessions.get(str(user_id))

    def validate_session(self, user_id):
        """Check if a session exists for the user."""
        return str(user_id) in self._sessions

    def close_session(self, user_id):
        """Close and remove a user's session."""
        with self._lock:
            if str(user_id) in self._sessions:
                del self._sessions[str(user_id)]
