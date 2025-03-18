from django.views import View
from django.http import JsonResponse
from main.session import DatabaseSessionManager
import json
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from main.Database_mangers.mongo import MongoManager
from main.Database_mangers.mysql import MySqlManager
from main.Database_mangers.postgres import PostgresManager
import os
from django.conf import settings



class ConnectionView(View):
    @staticmethod
    def connection(request):
        return render(request,'main/connection.html')
    
    @staticmethod
    def get_database_type(request):
        if 'user' not in request.session:
            return redirect ('signup')
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']
        
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        if request.method == 'POST':
            data = json.loads(request.body)
            input_type = data.get('inputType', None)
            session = session_manager.get_session(user_id)
            session["db_type"] = input_type
            if input_type == "postgres":
                session["manager"] = PostgresManager()
            elif input_type == "mysql":
                session["manager"] = MySqlManager()
            elif input_type == "mongoDB":
                session["manager"] = MongoManager()
            return JsonResponse({'message': input_type})
        else:
            return JsonResponse({'message': 'Invalid request method'})
        
    def upload_file(request):
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file was uploaded'}, status=400)
    
        uploaded_file = request.FILES['file']
    
    # Validate file extension
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
    
        if file_ext not in ['.csv', '.xls', '.xlsx']:
            return JsonResponse({'error': 'Invalid file format. Only CSV and Excel files are allowed'}, status=400)
    
    # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Save the file
        file_path = os.path.join(uploads_dir, file_name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
    
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                # Excel files
               df = pd.read_excel(file_path)
        # Example processing - you can modify this part based on your needs
            row_count = len(df)
            column_count = len(df.columns)
        
        # Get first few rows for preview
            preview = df.head(5).to_dict('records')
        
            return JsonResponse({
            'message': 'File uploaded and processed successfully',
            'filename': file_name,
            'rows': row_count,
            'columns': column_count,
            'preview': preview
            })
        
        except Exception as e:
            print(e)
            if os.path.exists(file_path):
                os.remove(file_path)
            return JsonResponse({'error': str(e)}, status=500)
        
    @staticmethod
    def get_connection_parameters(request):
        if 'user' not in request.session:
            return redirect ('signup')
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']
        
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        if request.method == 'POST':
            data = json.loads(request.body)
            user_name = data.get('user_name', None)
            password = data.get('password', None)
            host = data.get('host', None)
            port = data.get('port', None)
            print(user_name,password,host,port)
            session = session_manager.get_session(user_id)
            db_type = session["db_type"]
            if db_type == "postgres":
                session["manager"].connect({
                    "dbname": "postgres",  # Change this to your database name
                    "user": f"{user_name}",
                    "password": f"{password}",
                    "host": f"{host}",
                    "port": f"{port}"
                 })
            elif db_type == "mysql":
                session["manager"].connect({
                    "host": f"{host}",       # Change if MySQL is running on another host
                    "user": f"{user_name}",   # Replace with your MySQL username
                    "password": f"{password}",  # Replace with your MySQL password
                    "database": "mysql"   # Replace with your database name
                })
            return JsonResponse({'message': 'Connection successful'})
        else:
            return JsonResponse({'message': 'Invalid request method'})
      
            

    @staticmethod
    def process_url_view(request):
        if 'user' not in request.session:
            return redirect ('signup')
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']
        
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                url = data.get('url', None)
                print(url)
                if url:
                    session = session_manager.get_session(user_id)
                    session['manager'].connect(url)
                    return JsonResponse({'message': f'Database Type: {request.session["Db"]}','user_name': request.session['user_name']})
                else:
                    return JsonResponse({'error': 'No URL provided'}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    @staticmethod
    def get_database(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']
        
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        session = session_manager.get_session(user_id)
        options = session['manager'].list_databases()
        return JsonResponse(options, safe=False)

    @staticmethod
    @csrf_exempt
    def process_selection(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])

        if request.method == 'POST':
            selected_option = request.POST.get('selected_option')
            print(selected_option)
            session = session_manager.get_session(user_id)
            session['manager'].use_database(selected_option)
            session['current_database'] = selected_option
            return JsonResponse({
                'status': 'success', 
                'selected': selected_option
            })
        return JsonResponse({'error': 'Table not select'}, status=405)

    @staticmethod
    def get_tabel(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        
        session = session_manager.get_session(user_id)
        if session["db_type"] == "postgres" or session["db_type"]== "mysql":
            options=session['manager'].list_tables()
            return JsonResponse(options, safe=False)
        elif session["db_type"] == "mongoDB":
            options = session['manager'].list_collections()
            return JsonResponse(options, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)

    @staticmethod
    @csrf_exempt
    def tb_selection(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        
        if request.method == 'POST':
            selected_option = request.POST.get('selected_option')
            session = session_manager.get_session(user_id)
            if session["db_type"] == "mongoDB":
                session['manager'].use_collection(selected_option)
                session['current_collection'] = selected_option
                request.session['current_collection'] = selected_option
                return JsonResponse({
                'status': 'success', 
                'selected': selected_option
                 })
            elif session["db_type"] == "postgres" or session["db_type"] == "mysql":
                session["current_table"] = selected_option
                return JsonResponse({
                'status': 'success', 
                'selected': selected_option
                 })
            else:
                return JsonResponse({'error': 'Invalid request method'}, status=400)

        return JsonResponse({'error': 'Invalid request method'}, status=405)

    @staticmethod
    def get_sample(request):
        if 'user' not in request.session:
            return JsonResponse({'error': 'Please login first'}, status=401)
        
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        
        try:
            session = session_manager.get_session(user_id)
            if session["db_type"] == "mongoDB":
                data = session['manager'].get_sample_data()
                df = pd.DataFrame(data)
                df = df.applymap(str)
                records = df.to_dict('records')
                columns = [{"data": col, "title": col} for col in df.columns]
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            elif session["db_type"] == "postgres" or session["db_type"] == "mysql":
                table=session["current_table"]
                data = session['manager'].get_sample_data(table)
                df=pd.DataFrame(data)
                records = df.to_dict('records')
                columns = [{"data": col, "title": col} for col in df.columns]
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            elif session["db_type"] == "file":
                df=pd.DataFrame(data)
                records = df.to_dict('records')
                columns = [{"data": col, "title": col} for col in df.columns]
                return JsonResponse({"data": records, "columns": columns}, safe=False)
            else:
                return JsonResponse({"error":"invalid"},status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
        
    @staticmethod
    def disconnect(request):
        if 'user' in request.session:
            session_manager = DatabaseSessionManager()
            session_manager.close_session(request.session['user'])
        return redirect('home')
