from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

#request handler (request --> response)

#function is called in mainapp.urls.py to senf a response to the client

def test_request(request):
    return render(request, 'entrance.html')
