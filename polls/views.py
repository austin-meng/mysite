
import logging

from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from mysite import settings

# from polls.forms import LoginForm
from polls.forms import LoginForm, RegisterForm

from .models import Choice, Question

logger = logging.getLogger(__name__)

@login_required(login_url=settings.LOGIN_URL) 
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


# def detail(request, question_id):
#     return HttpResponse("You're looking at question %s." % question_id)

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


# class IndexView(generic.ListView):
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'

#     def get_queryset(self):
#         """Return the last five published questions."""
#         return Question.objects.order_by('-pub_date')[:5]


# class DetailView(generic.DetailView):
#     model = Question
#     template_name = 'polls/detail.html'


# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))



    # Redirect to a success page.
    # return HttpResponseRedirect("/account/loggedin/")
    # else:
    # Show an error page
    # return HttpResponseRedirect("/account/invalid/")

    # return HttpResponse("Hello, world. You're at the polls index.")

# def logout(request):
#     auth.logout(request)
#     # return HttpResponseRedirect("/account/loggedout/")
#     return HttpResponse("logout.")


#     if user is not None and user.is_active:
#         auth.login(request, user)
#         # request.session['stub'] = {'username':user.username,'login': 'hm','time':time.time()}
#         request.session.save()
#         login_url = request.GET.get('next',settings.LOGIN_REDIRECT_URL)
#         logger.info('SNG-DEBUG: login-next-url6 [%s]' % (login_url ) )
#         # return redirect(login_url)
#         return HttpResponse("login.")
#     else:
#         # form = LoginForm()
#         return HttpResponse("login.。。。")
#         # return render(request, 'polls/login.html', {'FORCE_SCRIPT_NAME':settings.FORCE_SCRIPT_NAME,'form': form,'tm':tm.isoformat(),'next':next})



def login(request):
    # if request.session.get('is_login', None):  # 防止重复登录
    #     return redirect('/index')

    if request.method == "POST":
        form = LoginForm(request.POST)
        message = "请检查填写的内容！"
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(request=request, username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                request.session.save()
                login_url = request.GET.get('next',settings.LOGIN_REDIRECT_URL)
                logger.info('SNG-DEBUG: login-next-url6 [%s]' % (login_url ) )
                return redirect('/polls/index/')
                # return HttpResponse(" 登录成功" )
            else:
                message = "密码不正确！"
        else:
            form = LoginForm()
            message = "密码不正确！"
            return render(request, 'polls/login.html', locals())
    form = LoginForm()
    return render(request, 'polls/login.html', locals())


def register(request):
    return HttpResponse(" register" )
#     if request.session.get('is_login', None):  # 登录状态不允许注册
#         return redirect("/index/")
#     if request.method == "POST":
#         register_form = RegisterForm(request.POST)
#         message = "请检查填写的内容！"
#         if register_form.is_valid():  # 获取数据
#             username = register_form.cleaned_data['username']
#             password1 = register_form.cleaned_data['password1']
#             password2 = register_form.cleaned_data['password2']
#             email = register_form.cleaned_data['email']
#             if password1 != password2:  # 判断两次密码是否相同
#                 message = "两次输入的密码不同！"
#                 return render(request, 'register.html', locals())
#             else:
#                 same_name_user = models.User.objects.filter(username=username)
#                 if same_name_user:  # 用户名唯一
#                     message = '用户名已经存在！'
#                     return render(request, 'register.html', locals())
#                 same_email_user = models.User.objects.filter(email=email)
#                 # 当一切都OK的情况下，创建新用户

#                 new_user = models.User.objects.create()
#                 new_user.username = username
#                 new_user.password = hash_code(password1)  # 使用加密密码
#                 new_user.email = email
#                 new_user.save()
#                 return redirect('/polls/login/')  # 自动跳转到登录页面
#     register_form = RegisterForm()
#     return render(request, 'register.html', locals())


# def logout(request):
#     if not request.session.get('is_login', None):  # 如果本来就未登录，也就没有登出一说
#         return redirect("/index/")
#     request.session.flush()  # 将session中的所有内容全部清空
#     return redirect('/index/')