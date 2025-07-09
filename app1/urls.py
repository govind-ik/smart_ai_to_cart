
from django.urls import path,include
from . import views


urlpatterns = [
    
    path('',views.home,name='home_page'),
    path('login/',views.user_login,name='login'),
    path('registration/',views.register,name='register'),
    path('logout/',views.logout_user,name='logout_user'),
]
