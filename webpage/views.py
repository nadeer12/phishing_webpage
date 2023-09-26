from django.shortcuts import render, redirect,HttpResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import pandas as pd
import numpy as np
import random


# Machine Learning Packages
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from django.views import View
from .models import blacklist
from .models import Message
from django.http import HttpResponse




from django.contrib import messages
from .models import *
from .helpers import send_forget_password_mail
from .models import Profile
import uuid
# Create your views here.
def index(request):
    if request.method == 'POST':
        user_names = request.POST['name']
        user_emails = request.POST['email']
        user_messages = request.POST['message']

        if len(user_names)  < 1:
            return HttpResponse('<h1>!!!Name and Email are required</h1>' )
        else:
            new_contact = Message(user_name=user_names , user_email=user_emails, user_message=user_messages)
            new_contact.save()

    return render(request,'index.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('detect_phishing')
        else:
            return HttpResponse("<h1>Username or Password not found</h1>")
            return redirect('sign')
    return render(request,'login.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']

        if len(password)  < 6:
            return HttpResponse('<h1>password must be more than 6 character</h1>' )

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return HttpResponse("<h1>Username already taken</h1>")
            return render(request, 'signup.html', {'error_message': 'Username already taken'})

        try:
            myuser = User.objects.create_user(username=username, email=email, password=password)
            myuser.first_name = firstname
            myuser.last_name = lastname
            myuser.save()
            return redirect('login')
        except IntegrityError:
            return render(request, 'signup.html', {'error_message': 'An error occurred during signup'})
        


    return render(request, 'signup.html')


def about(request):
    return render(request,'aboutus.html')

def faq(request):
    return render(request,'faq.html')

def admin_user(request):
    return render(request,'admin_user.html')

class PhishingDetectionView(View):
    template_name = 'detection.html'

    def __init__(self):
        self.urls_data = pd.read_csv(r"C:\Users\91953\Desktop\vs code project\phishing_webpage\urldata.csv")  # Update the path
        self.vectorizer = TfidfVectorizer(tokenizer=self.make_tokens)
        self.X = self.vectorizer.fit_transform(self.urls_data["url"])
        self.y = self.urls_data["label"]
        self.logit = LogisticRegression()
        self.logit.fit(self.X, self.y)

    @staticmethod
    def make_tokens(f):
        tkns_BySlash = str(f.encode('utf-8')).split('/')	# make tokens after splitting by slash
        total_Tokens = []
        for i in tkns_BySlash:
            tokens = str(i).split('-')	# make tokens after splitting by dash
            tkns_ByDot = []
            for j in range(0,len(tokens)):
                temp_Tokens = str(tokens[j]).split('.')	# make tokens after splitting by dot
                tkns_ByDot = tkns_ByDot + temp_Tokens
            total_Tokens = total_Tokens + tokens + tkns_ByDot
        total_Tokens = list(set(total_Tokens))	#remove redundant tokens
        if 'com' in total_Tokens:
            total_Tokens.remove('com')	#removing .com since it occurs a lot of times and it should not be included in our features
        return total_Tokens
        
        pass

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        siteurl = request.POST.get('url', '')
        siteurl_transformed = self.vectorizer.transform([siteurl])
        result = self.logit.predict(siteurl_transformed)
        context = {'result': result[0]}
        return render(request, self.template_name, context)
    

    def post(self, request):
        siteurl = request.POST.get('url', '')
        siteurl_transformed = self.vectorizer.transform([siteurl])
        result = self.logit.predict(siteurl_transformed)
    
        context = {'result': result[0], 'typed_url': siteurl}
        return render(request, self.template_name, context)
    

def adminlogin(request):
    return render(request,'admin_login.html')

def admin(request):
    return render(request,admin.site.urls)

def blacklist_db(request):
    blacklists=blacklist.objects.all()
    return render(request,'blacklist.html',{'blacklists':blacklists})



def change_pass(request, token):
    # context = {}
    try:
        profile_obj = Profile.objects.filter(forget_password_token=token).first()
        # context = {'user_id': profile_obj.user.id}
        user_id=profile_obj.user.id
        if not profile_obj:
            messages.error(request, 'Invalid token or profile not found')
            return HttpResponse("<h1>Invalid token or profile not found</h1>")
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            # user_id = request.POST.get('user_id')

            if user_id is None:
                # messages.error(request, 'No user id found')
                return redirect(f'/change-pass/{token}/')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return HttpResponse("<h1>Passwords do not match</h1>")
                return redirect(f'/change-pass/{token}/')
            
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('login')

    except Exception as e:
        print(e)
        messages.error(request, 'An error occurred while processing your request.')
    
    
    # return render(request, 'change_pass.html', context)
    return render(request,'change_pass.html')


def forget(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            
            if not User.objects.filter(username=username).first():
                messages.error(request, 'No user found')
                return HttpResponse("<h1>No user found with this username</h1>")
            
            user_obj = User.objects.get(username=username)
            token = str(uuid.uuid4())

            # Check if a profile exists for the user
            profile_obj, created = Profile.objects.get_or_create(user=user_obj)

            # Update the forget_password_token
            profile_obj.forget_password_token = token
            profile_obj.save()

            send_forget_password_mail(user_obj.email, token)
            messages.success(request, 'An email has been sent')
            return HttpResponse("<h1>Email has been sent</h1>")

    except Exception as e:
        print(e)
        messages.error(request, 'An error occurred while processing your request.')

    return render(request, 'forget.html')

