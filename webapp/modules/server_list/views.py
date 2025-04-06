from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from .models import ServerList

import random, string, json

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
                "active": server.is_active,
                "invite_code": server.server_invite_code
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
            resp_data["players"] = server_details.player_server_map.all().count() if server_details.player_server_map else 0

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

class ServerManagerInviteView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_post = request.POST
        server_id = req_post.get("server_id")
        code_len = req_post.get("code_len", 0)
        resp_data = {}

        try:
            code_len = int(code_len)

            if not server_id:
                raise Exception("server_id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("server_details is empty")
                
            char_list = string.ascii_lowercase + string.digits
            rand_letters = ''.join(random.choice(char_list) for i in range(code_len))

            server_details.server_invite_code = rand_letters
            server_details.save()

            resp_data["invite_code"] = rand_letters

            return JsonResponse(resp_data)

        except Exception as err:
            return JsonResponse(resp_data)
        
class ServerManagerInviteDetailsView(View):
    
    def put(self, request: HttpRequest, *args, **kwargs):

        req_post = json.loads(request.body)
        server_id = kwargs.get("id")
        code_len = req_post.get("code_len", 0)
        close_invite = req_post.get("close_invite", False)
        resp_data = {}

        try:
            code_len = int(code_len)

            if not server_id:
                raise Exception("server_id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("server_details is empty")
            
            if not close_invite:
                char_list = string.ascii_lowercase + string.digits
                rand_letters = ''.join(random.choice(char_list) for i in range(code_len))
            else:
                rand_letters = None


            server_details.server_invite_code = rand_letters
            server_details.save()

            resp_data["invite_code"] = rand_letters
            resp_data["invite_closed"] = close_invite

            return JsonResponse(resp_data)

        except Exception as err:
            return JsonResponse(resp_data)