
from django.contrib import admin
from django.urls import path,include
from .import views
from django.conf import settings
from .views import PhishingDetectionView
from django.conf.urls.static import static

from django.views.static import serve
from django.conf.urls import url




urlpatterns = [
    # path('admin/', admin.site.urls,),
    path('',views.index,name='home'),
    path('login',views.user_login,name="login"),
    path('signup',views.signup,name='sign'),
    path('about',views.about,name="about"),
    path('faq',views.faq,name='faq'),
    path('admin_user',views.admin_user,name='admin_user'),
    path('detection', PhishingDetectionView.as_view(), name='detect_phishing'),
    path('admin_login',views.adminlogin,name='admin_login'),
    path('admin/', views.admin,name='admin'),
    path('blacklist',views.blacklist_db,name='blacklist'),
    path('forget',views.forget,name='forget'),
    path('change_pass/<token>/',views.change_pass,name='change_pass'),

    

]
