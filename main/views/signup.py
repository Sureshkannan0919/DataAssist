from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import make_password
from main.models import User



class Signup (View):
    def get(self, request):
        return render (request, 'main/signup.html')

    def post(self, request):
        postData = request.POST
        user_name = postData.get ('username')
        email = postData.get ('email')
        password = postData.get ('password')
        # validation
        value = {
            'user' : user_name,
            'email': email
        }
        error_message = None

        user = User (        user_name= user_name,
                             email=email,
                             password=password)
        error_message = validateUser(user)

        if not error_message:
            print (user_name, email, password)
            user.password = make_password (user.password)
            user.register ()
            return redirect ('home')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render (request, 'main/signup.html', data)
    

def validateUser(user):
        error_message = None
        if (not user.user_name):
            error_message = "Please Enter your First Name !!"
        elif len (user.user_name) < 3:
            error_message = 'username must be 3 char long or more'
        elif len (user.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len (user.email) < 5:
            error_message = 'Email must be 5 char long'
        elif user.isexists ():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message