import google.generativeai as genai

def initialize_gemini():
    genai.configure(api_key="AIzaSyCpTsXe_xZQIzSMyx6Pg5oKZQQu58RKLhI")
    
    generation_config = {
        "temperature": 0.2,  # Lower temperature for more precise, deterministic outputs
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    system_instruction = """
    You are a specialized SQL and NoSQL query generator. Your responses must:
    1. Contain ONLY the executable query with no explanations or additional text
    2. in the excutable query, query operator should always be within double quotes this should followed only for mongodb database
    for example {"wintrade": {$lt: 100}} should be like this {"wintrade": {"$lt": 100}}
    3. Follow best practices for query optimization and security
    4. Only respond to database query-related questions
    5. If the question is not related to databases, respond with: "Please ask a question about SQL or NoSQL queries."
    
    """
    
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

def handle_user_query(db_type, user_query, metadata=None):
    model = initialize_gemini()
    
    prompt = f"""
    Generate a {db_type} query that addresses the following request:
    
    USER REQUEST: {user_query}
    
    DATABASE METADATA: {metadata if metadata else 'Not provided'}
    
    Important: Return ONLY the executable query with no explanations or additional text.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating query: {str(e)}"


def pandas_query(user_query,db_type,metadata):
    model = initialize_gemini()
    prompt = f"""
    Generate a pandas query that addresses the following request:
    
    USER REQUEST: {user_query}
    
    column and datatypes: {db_type}

    DATABASE METADATA: {metadata if metadata else 'Not provided'}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating query: {str(e)}"

    

