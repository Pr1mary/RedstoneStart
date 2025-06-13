from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import resolve

import random, string, json

class UserLoginView(View):
    template = "modules/accounts/templates/index-login.html"
    ctx = {
        "page_title": "login_page"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        form = AuthenticationForm()
        self.ctx["form"] = form

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):


        form = AuthenticationForm(request, request.POST)
        user = None
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

        if not user:       
            messages.error(request, "Wrong username or password!")
            return redirect("auth_login")

        login(request, user)
        return redirect("main_page")
    
class UserRegisterView(View):
    template = "modules/accounts/templates/index-register.html"
    ctx = {
        "page_title": "register_page"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):

        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username)
        if user.exists():
            messages.error(request, "Username already taken!")
            return redirect("auth_register")

        user = User.objects.create_user(email=email, username=username)
        user.set_password(password)
        user.save()

        return redirect("auth_login")

class UserLogoutView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        if request.user.is_authenticated:
            logout(request)

        return redirect("auth_login")
    
class UserInfoDetailsView(LoginRequiredMixin, View):
    template = "modules/accounts/templates/index.html"
    ctx = {
        "page_title": "register_page"
    }
    login_url = "/accounts/auth/login"

    def get(self, request: HttpRequest, *args, **kwargs):

        if request.user.is_authenticated:
            self.ctx["curr_username"] = request.user.username
            self.ctx["curr_email"] = request.user.email

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):

        data = request.POST

        try:
            if not request.user.is_authenticated:
                raise Exception("not authenticated")
            
            if data.get("email"):
                request.user.email = data.get("email")

            if data.get("password"):
                request.user.set_password(data.get("password"))

            request.user.save()

        except Exception as e:
            if e.args[0] == "not authenticated":
                messages.error(request, "User is not authenticated")
            else:
                messages.error(request, "Unknown error when updating user data")
            return redirect("details_info")
        
        messages.info(request, "User data successfully updated! Please login again.")
        return redirect("details_info")