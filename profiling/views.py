from django.shortcuts import render

def index_view(request):
    context = {'message': 'Hello, World!'}
    return render(request, 'index.html', context)

def profiling_view(request):
    context = {'message': 'Hello, World!'}
    return render(request, 'my_template.html', context)

