import logging

from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render
from mysite import settings

from polls.forms import LoginForm

logger = logging.getLogger(__name__)

@login_required(login_url=settings.LOGIN_URL) 
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(request=request, username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        # request.session['stub'] = {'username':user.username,'login': 'hm','time':time.time()}
        request.session.save()
        login_url = request.GET.get('next',settings.LOGIN_REDIRECT_URL)
        logger.info('SNG-DEBUG: login-next-url6 [%s]' % (login_url ) )
        # return redirect(login_url)
        return HttpResponse("login.")
    else:
        form = LoginForm()
        return HttpResponse("login.。。。")
        # return render(request, 'polls/login.html', {'FORCE_SCRIPT_NAME':settings.FORCE_SCRIPT_NAME,'form': form,'tm':tm.isoformat(),'next':next})


    # Redirect to a success page.
    # return HttpResponseRedirect("/account/loggedin/")
    # else:
    # Show an error page
    # return HttpResponseRedirect("/account/invalid/")

    # return HttpResponse("Hello, world. You're at the polls index.")

def logout(request):
    auth.logout(request)
    # return HttpResponseRedirect("/account/loggedout/")
    return HttpResponse("logout.")
