from urllib.parse import urlparse
import re
import json

def parse_database_url(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the database type (protocol) from the URL
    db_type = parsed_url.scheme.lower()
    
    # Initialize default components
    username, password, host, port, database_name = None, None, None, None, None
    
    if db_type == 'postgresql' or db_type == 'postgres':
        # For PostgreSQL
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database_name = parsed_url.path.lstrip('/')
    
    elif db_type == 'mysql':
        # For MySQL
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database_name = parsed_url.path.lstrip('/')
    
    elif db_type == 'mongodb':
        # For MongoDB
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 27017  # Default MongoDB port is 27017
        database_name = parsed_url.path.lstrip('/')
    
    else:
        raise ValueError("Unsupported database type: " + db_type)

    return db_type, username, password, host, port, database_name



# def query_parser(query):
    
#     match = re.search(r"\(\s*({.*?})\s*\)", query, re.DOTALL)

#     return match.group(1).strip() if match else Noneimport json



# def query_parser(query):
#     Match a JSON-like dictionary starting with '{' and ending with '}'
#   match = re.search(r'({.*})', query, re.DOTALL)
#    return match.group(1).strip() if match else None
# def query_parser(query):
#     # Extract JSON-like content using regex
#     match = re.search(r'({.*})', query, re.DOTALL)
#     if match:
#         try:
#             # Convert the string to a Python dict
#             return json.loads(match.group(1).strip())
#         except json.JSONDecodeError as e:
#             print("JSON Decode Error:", e)
#             return None
#     return None

def query_parser(query):
    match = re.search(r'({.*})', query, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1).strip())
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return None
    return None



def extract_sql_queries(input_text):
    """
    Extracts valid SQL queries from a given string and returns them as a single string.
    """
    if not isinstance(input_text, str):
        raise TypeError("Input must be a string")
    
    # Regular expression to match SQL statements
    sql_pattern = re.compile(
        r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|WITH)\b.*?;",
        re.IGNORECASE | re.DOTALL
    )
    
    queries = [match.group().strip() for match in sql_pattern.finditer(input_text)]
    
    return "\n".join(queries)

