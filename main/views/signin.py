from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.hashers import check_password
from main.models import User
from main.session import DatabaseSessionManager




class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get ('return_url')
        return render (request, 'main/signin.html')

    def post(self, request):
        email = request.POST.get ('email')
        password = request.POST.get ('password')
        user = User.get_user_by_email (email)
        error_message = None
        if user:
            flag = check_password (password, user.password)
            if flag:
                request.session['user'] = user.id
                request.session['user_name'] = user.user_name
                session_manager = DatabaseSessionManager()
                session_manager.create_session(user.id, user.user_name)

                if Login.return_url:
                    return HttpResponseRedirect (Login.return_url)
                else:
                    Login.return_url = None
                    return redirect ('home')
            else:
                error_message = 'Invalid !!'
        else:
            error_message = 'Invalid !!'

        print (email, password)
        return render (request, 'main/signin.html', {'error': error_message})
    

    @staticmethod
    def logout(request):
        if 'user' in request.session:
            session_manager = DatabaseSessionManager()
            session_manager.close_session(request.session['user'])
        request.session.clear()
        return redirect('signin')