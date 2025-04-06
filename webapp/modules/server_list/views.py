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
                "id": server.pk,
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

        try:

            server_list = ServerList(
                server_url = server_url,
                server_name = server_name,
                is_active = True,
                created_by = req_user,
                updated_by = req_user,
            )
            server_list.save()

        except Exception as err:
            print(f"Error when storing server: {err.args}")

        return redirect("server_list")
    
class ServerManagerDetailView(View):
    template = "modules/server_list/templates/index.html"
    ctx = {
        "page_title": "server_manager"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        server_id = kwargs.get("id")
        resp_data = {}

        try:
            if not server_id:
                raise Exception("server_id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("server_details is empty")
                
            resp_data["id"] = server_details.pk
            resp_data["name"] = server_details.server_name
            resp_data["url"] = server_details.server_url
            resp_data["active"] = server_details.is_active
            resp_data["players"] = 0

            return JsonResponse(resp_data)

        except Exception as err:
            return JsonResponse(resp_data)
        
    def delete(self, request: HttpRequest, *args, **kwargs):

        server_id = kwargs.get("id")
        resp_data = {}

        try:
            if not server_id:
                raise Exception("server_id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("server_details is empty")
                
            server_details.delete()

            resp_data["deleted"] = True

            return JsonResponse(resp_data)

        except Exception as err:
            resp_data["deleted"] = False
            return JsonResponse(resp_data)
