"""hotels_todo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from todo.views import get_index
from todo.views import sign_in_view
from django.contrib.auth import views as auth_views
from todo import views 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', get_index, name="home"),  
    path('summernote/', include('django_summernote.urls')),
    path('todo/', include('todo.urls')),  
    path('accounts/', include('allauth.urls')),  
    path('signin/', auth_views.LoginView.as_view(template_name='todo/signIn.html'), name='sign_in'),
    path('signup/', views.sign_up_view, name='signUp'),
    path('signout/', auth_views.LogoutView.as_view(next_page='home'), name='sign_out'),
]
