from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.models import History, User
import json
from django.views import View
from main.session import DatabaseSessionManager
import pandas as pd


class HistoryView(View):

    @staticmethod
    def save_history(request):
        if request.method != 'POST':
            return HttpResponse("Invalid request method", status=405)
            
        user_id = request.session.get('user')
        if not user_id:
            return HttpResponse("User not logged in", status=401)
        
        try:
            user = User.objects.get(id=user_id)  # Get actual User instance
        except User.DoesNotExist:
            return HttpResponse("User not found", status=404)
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']

        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        session = session_manager.get_session(user_id)

        url = "http://datatables.net/tn/3"
        user_query = session['input_query']
        generated_sql = session['query']
        pandas_df_json = session['data_frame'].to_json("records")
        try:
            pandas_df = json.loads(pandas_df_json)  # Ensure valid JSON
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON format", status=400)

        # Save history record
        history = History(
            user=user,
            url=url,
            user_query=user_query,
            generates_sql=generated_sql,
            pandas_df=pandas_df
        )
        history.save_history()

        return redirect('view_history')

    @staticmethod
    def view_history(request):
        user_id = request.session.get('user')
        
        if not user_id:
            return HttpResponse("User not logged in", status=401)

        history_records = History.get_history_by_user(user_id)
        
        return render(request, 'main/history.html', {'history_records': history_records})
