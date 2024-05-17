from django.shortcuts import render

def chart_list(request):
    return render(request, 'chart_list.html')
