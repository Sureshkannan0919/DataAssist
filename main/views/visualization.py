from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse



class VisualizationView(View):
    def visualization(request):
        return render(request,'main/visualization.html')
    
    