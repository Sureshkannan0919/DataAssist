from django.shortcuts import render
from django.views import View




class HowToUseView(View):
    def how_to_use(request):
        request.session['chat_history'] = [
            {
                'input': 'input1',
                'output': 'output1'
            },
            {
                'input': 'input2',
                'output': 'output2'
            },
            {
                'input': 'input3',
                'output': 'output3'
            }
        ]
        return render(request,'main/howtouse.html')
    
