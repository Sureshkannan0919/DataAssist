from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from main.session import DatabaseSessionManager
import json
import pandas as pd
from main.genai import handle_user_query,pandas_query
from main.tools import query_parser, extract_sql_queries
from main.pandas_tool import preprocess_data,pandas_parse_query,execute_query


class QueryHelper(View):
    @staticmethod
    def query_helper(request):
        request.session['chat'] = [
        ]
        return render(request,'main/queryhelper.html')
    
    @staticmethod
    def query_response(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method'}, status=405)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        
        try:
            session = session_manager.get_session(user_id)
            data = json.loads(request.body)
            query = data.get('query')
            print(query)
            session['input_query']=query
            if not query:
                return JsonResponse({'error': 'No query provided'}, status=400)
            
            
            if session["db_type"] == "mongoDB":
                columns, data_type = session['manager'].get_collection_schema()
                metadata = {
                "columns": columns,
                "data_type": data_type
                }
                generated_query=handle_user_query(session["db_type"], query, metadata)
                print(generated_query)
                parsedquery=query_parser(generated_query)
                print(type(parsedquery))
                print(parsedquery)
                session['query']=parsedquery

                return JsonResponse({
                'message': str(parsedquery)
                })
            elif session["db_type"] == "postgres" or session["db_type"] == "mysql":
                columns, data_type  =session['manager'].get_table_schema(session["current_table"])
                metadata = {
                "table_name":session["current_table"],
                "columns": columns,
                "data_type": data_type
                }
                print(metadata)# or get from session if it's stored there
                parsedquery=extract_sql_queries(handle_user_query(session["db_type"], query, metadata))
                print(parsedquery)
                session['query']=parsedquery
                return JsonResponse({
                'message': str(parsedquery)
                })
            elif session["db_type"] == "pandas":
                df=session['pandas_df']
                df=preprocess_data(df)
                datatypes=df.dtypes.to_dict()
                metadata=df.sample(5).to_string()
                generated_query=pandas_query(query,datatypes,metadata)
                print(generated_query)
                parsed_query=pandas_parse_query(generated_query)
                session['query']=parsed_query
                return JsonResponse({
                'message': str(parsed_query)
                })
            else:
                return JsonResponse({'error': 'Invalid database type'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    @staticmethod
    def get_dataframe(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        
        try:
            session = session_manager.get_session(user_id)
            if session["db_type"] == "mongoDB":
                query=session['query']
                data = session['manager'].execute_query(query)
                df=pd.DataFrame(data)
                df=df.drop("_id",axis=1)
                session['data_frame']=df
                records = df.to_dict('records')
                print("records:",records)
                columns = [{"data": col, "title": col} for col in df.columns]
                print("columns:",columns)
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            
            elif session["db_type"] == "postgres" or session["db_type"] == "mysql":
                query=session['query']
                data = session['manager'].execute_query(query)
                df=pd.DataFrame(data)
                session['data_frame']=df
                records = df.to_dict('records')
                print("records:",records)
                columns = [{"data": col, "title": col} for col in df.columns]
                print("columns:",columns)
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            
            elif session["db_type"] == "pandas":
                df=session['pandas_df']
                df=preprocess_data(df)
                query=session['query']
                result=execute_query(df,query)
                records=result.to_dict('records')
                print(records)
                columns=[{"data": col, "title": col} for col in result.columns]
                print(columns)
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            else:
                return JsonResponse({'error': 'Invalid database type'}, status=400)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        