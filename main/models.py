from django.db import models
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    user_name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=100)


    def register(self):
        self.save()

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except:
            return False

    def isexists(self):
        if User.objects.filter(email=self.email):
            return True
        else:
            return False

class History(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    url = models.URLField()
    user_query = models.CharField(max_length=2000)
    generates_sql = models.CharField(max_length = 2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    pandas_df = models.JSONField()


    def save_history(self):
        self.save()

    @staticmethod
    def get_history_by_user(user_id):
        return History.objects.filter(user=user_id).order_by('-timestamp')
