from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from . import models
from .forms import LoginForm


def index(request):
    pass
    return render(request,'main/index.html')
 

def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                # user = User.objects.get(username=username)
                user = auth.authenticate(username=username, password=password)
                print(user.username)

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
                message = "用户不存在！"
        return render(request, 'main/login.html', locals())
 
    login_form = LoginForm()
    return render(request, 'main/login.html', locals())

def register(request):
    pass
    return render(request,'main/register.html')
 
def logout(request):
    res = auth.logout(request)
    print(res)
    return render(request, 'main/login.html', locals())

# def register(request):
#     # 定义一个错误提示为空
#     error_name = ''
#     if request.method=='POST':
#         user = request.POST.get('username')
#         password = request.POST.get('password')
#         email = request.POST.get('email')
#         user_list = models.User.objects.filter(username=user)
#         if user_list :
#             # 注册失败
#             error_name = '%s用户名已经存在了' % user
#             # 返回到注册页面，并且把错误信息报出来
#             return  render(request,'register.html',{'error_name':error_name})
#         else:
#             # 数据保存在数据库中，并返回到登录页面
#             user = models.User.objects.create(username=user,
#                                        password=password,
#                                        email=email)
#             user.save()
#             # 同ip下跳转
#             return redirect('/login/')
            
#     return render(request,'register.html')