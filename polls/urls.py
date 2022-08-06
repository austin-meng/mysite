from django.urls import path

from . import views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('login', views.login, name='login'),
#     path('logout', views.logout, name='logout'),
# ]



app_name = 'polls'
urlpatterns = [
    path('index/', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),

    path('login/', views.login, name='login'),
    # path('register/', views.register),
    # path('logout/', views.logout),

]
