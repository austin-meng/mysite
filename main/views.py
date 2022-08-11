from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from . import models
from .forms import LoginForm, RegisterForm

import traceback


def index(request):
    return render(request,'main/index.html')
 

def login(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        message = "请检查填写的内容！"
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = auth.authenticate(username=username, password=password)
                print(user)

                if not user:
                    message = "密码不正确！"
                else:
                    auth.login(request, user)
                    # request.session['is_login']=True
                    # request.session['user_id'] = user.id
                    # request.session['username'] = user.name
                    
                    return render(request, 'main/index.html', locals())
            except Exception as e:
                print(e)
                traceback.print_exc()
                message = "登录失败"
        return render(request, 'main/login.html', locals())
    return render(request, 'main/login.html', locals())


def register(request):
    message = ""
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            users = User.objects.filter(username=username)
            if users:
                message = f'{username}用户名已存在'
                return render(request, 'main/register.html', locals())
            else:
                user = User.objects.create_user(username=username, password=password)
                # user.is_superuser=is_superuser
                # user.last_name = username
                user.is_staff = True
                user.is_active = True
                user.save()
                message = f"用户{username}注册成功"
                return render(request, 'main/login.html', locals())

    return render(request, 'main/register.html', locals())


def logout(request):
    form = LoginForm()
    res = auth.logout(request)
    return render(request, 'main/login.html', locals())

