from django.shortcuts import render

# Create your views here.

def shell(request, id):
    return render(request,'shell/webshell.html',locals())