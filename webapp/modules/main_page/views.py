from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View

import random, string, json

class MainPageView(View):

    def get(self, request: HttpRequest, *args, **kwargs):

        anonym_page_path = "player_join_server"
        logedin_page_path = "server_list"

        if request.user.is_authenticated:
            target_redirect = logedin_page_path
        else:
            target_redirect = anonym_page_path

        return redirect(target_redirect)
    