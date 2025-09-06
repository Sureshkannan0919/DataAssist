import pandas as pd
import re
from typing import Optional

def preprocess_data(data):
    for col in data.select_dtypes(include=['object']):
        data[col] = data[col].str.lower()
    return data

def clean_data(data):
    data = data.dropna()
    data = data.drop_duplicates()
    return data

def pandas_parse_query(query_str: str) -> str:
    """
    Parse a string containing pandas DataFrame filtering code or a raw logical expression,
    and return the executable pandas code as a string.

    Handles:
    1. df.query() style: df.query('offer > 50 and cprice < 1000')
    2. Boolean indexing: df[(df['ocassion'] == 'formal') & (df['offer'] == 60.0)]
    3. Raw logical expressions: gender == 'male' and cprice < 1000

    Args:
        query_str (str): String containing the query code

    Returns:
        str: Executable pandas filtering code
    """
    query_str = query_str.strip()

    # 1. df.query() style
    query_pattern = r"df\.query\((['\"])(.*?)\1\)"
    query_match = re.fullmatch(query_pattern, query_str)
    if query_match:
        return f"df.query({query_match.group(1)}{query_match.group(2)}{query_match.group(1)})"

    # 2. Boolean indexing style
    boolean_pattern = r"df\[(.*)\]"
    boolean_match = re.fullmatch(boolean_pattern, query_str)
    if boolean_match:
        return f"df[{boolean_match.group(1)}]"

    # 3. Raw logical expression (e.g., "gender == 'male' and cprice < 1000")
    # Heuristic: contains 'and'/'or' or comparison operators, but not 'df.'
    if (
        any(op in query_str for op in [' and ', ' or ', '==', '!=', '<', '>', '<=', '>='])
        and 'df.' not in query_str
        and 'df[' not in query_str
    ):
        # Escape single quotes inside the expression
        safe_query = query_str.replace("'", "\\'")
        return f"df.query('{safe_query}')"

    return "# Could not parse query"



def execute_query(df: pd.DataFrame, query_str: str) -> Optional[pd.DataFrame]:

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("A valid pandas DataFrame must be provided")

    if not query_str or not isinstance(query_str, str):
        raise ValueError("A valid query string must be provided")

    # Clean up the query string
    query_str = query_str.strip()

    # Check if it contains the full df.query syntax
    if query_str.startswith("df.query("):
        # Extract the query part
        pattern = r"df\.query\(['\"]([^'\"]+)['\"]\)"
        match = re.search(pattern, query_str)
        if match:
            query_condition = match.group(1)
            try:
                return df.query(query_condition)
            except Exception as e:
                print(f"Error executing query: {e}")
                return None

    # Check if it's just a query condition without df.query()
    elif not any(char in query_str for char in "[](){}") and not query_str.startswith("df["):
        # Likely a simple query condition
        try:
            return df.query(query_str)
        except Exception as e:
            print(f"Error executing query condition: {e}")
            return None

    # Check if it's a boolean indexing with the full df[] syntax
    elif query_str.startswith("df["):
        # Extract the condition part
        pattern = r"df\[(.*)\]"
        match = re.search(pattern, query_str)
        if match:
            condition = match.group(1)
            try:
                # Create a safe local namespace with only the df
                local_vars = {"df": df, "pd": pd}
                result = eval(f"df[{condition}]", {"__builtins__": {}}, local_vars)
                return result
            except Exception as e:
                print(f"Error executing boolean indexing: {e}")
                return None

    # Check if it's just the condition part of boolean indexing without df[]
    else:
        try:
            # Create a safe local namespace with only the df
            local_vars = {"df": df, "pd": pd}
            result = eval(f"df[{query_str}]", {"__builtins__": {}}, local_vars)
            return result
        except Exception as e:
            print(f"Error executing condition: {e}")
            return None
