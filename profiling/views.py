from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from .models import *

def index_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('profiling_view')
    return render(request, 'index.html')

def users_view(request):
    context = {'message': 'Hello, World!'}
    return render(request, 'portal/user.html', context)

def profiling_view(request):
    cases = Investigation.objects.all()
    recent_investigations = Investigation.objects.all()
    hearings = JudicialCase.objects.all()
    context = {
        'cases': cases,
        'recent': recent_investigations,
        'hearings': hearings,
        }
    return render(request, 'portal/dashboard.html', context)

