from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
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
            return redirect("auth_login")

        login(request, user)
        return redirect("main_page")

class UserLogoutView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        if request.user.is_authenticated:
            logout(request)

        return redirect("auth_login")
        