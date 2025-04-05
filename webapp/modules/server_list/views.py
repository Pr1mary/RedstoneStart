from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from .models import ServerList

class ServerManagerView(View):
    template = "modules/server_list/templates/index.html"
    ctx = {
        "page_title": "server_manager"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        server_list = ServerList.objects.filter(is_deleted=False).order_by("-created_at")
        server_detail_list = []
        for server in server_list:
            server_detail = {
                "name": server.server_name,
                "url": server.server_url,
                "active": server.is_active
            }
            server_detail_list.append(server_detail)

        self.ctx["server_list"] = server_detail_list

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST
        req_user = request.user

        # handle if user is anonymous
        if req_user.id == None:
            req_user = None

        server_url = req_body.get("server-address")
        server_name = req_body.get("server-name")

        server_list = ServerList(
            server_url = server_url,
            server_name = server_name,
            is_active = True,
            created_by = req_user,
            updated_by = req_user,
        )
        server_list.save()

        return redirect("server_list")