from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from main.models import History, User
import json
from django.views import View
from main.session import DatabaseSessionManager
import pandas as pd


class HistoryView(View):

    @staticmethod
    def save_history(request):
        # Only allow POST requests
        if request.method != 'POST':
            return JsonResponse({"error": "Invalid request method"}, status=405)
        
        user_id = request.session.get('user')
        if not user_id:
            return JsonResponse({"error": "User not logged in"}, status=401)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        session_manager = DatabaseSessionManager()
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session.get('user_name'))
        session = session_manager.get_session(user_id)

        # Safely get session data
        user_query = session.get('input_query')
        generated_sql = session.get('query')
        if not user_query or not generated_sql:
            return JsonResponse({"error": "No query data available to save"}, status=400)

        url = "http://datatables.net/tn/3"
        # For now, just save a dummy pandas_df
        pandas_df = {"hello": "1"}

        # Save history record
        history = History(
            user=user,
            url=url,
            user_query=user_query,
            generates_sql=generated_sql,
            pandas_df=pandas_df
        )
        history.save_history()

        return JsonResponse({"status": "success", "message": "History saved successfully", "history_id": history.id})

    @staticmethod
    def view_history(request):
        user_id = request.session.get('user')
        
        if not user_id:
            return HttpResponse("User not logged in", status=401)

        history_records = History.get_history_by_user(user_id)
        
        return render(request, 'main/history.html', {'history_records': history_records})
