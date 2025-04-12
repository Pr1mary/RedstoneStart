from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from .models import PlayerList, PlayerServerMap, ServerList
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

import random, string, json

class PlayerManagerView(LoginRequiredMixin, View):
    template = "modules/player_list/templates/index.html"
    ctx = {
        "page_title": "player_manager"
    }
    login_url = "/accounts/auth/login"

    def get(self, request: HttpRequest, *args, **kwargs):

        server_id = request.GET.get("server_id", None)
        try:
            server_id = int(server_id)
        except:
            server_id = None

        server_list_parsed = []
        server_list = ServerList.objects.all().order_by("created_at")
        if not server_id:
            server_id = server_list.first().pk
        for server in server_list:
            server_list_parsed.append({
                "id": server.pk,
                "name": server.server_name,
                "active": server.pk == server_id
            })
        player_map_list = PlayerServerMap.objects.filter(server_joined__pk=server_id).order_by("-created_at")
        
        player_detail_list = []
        for player in player_map_list:

            player_detail = {
                "id": player.pk,
                "name": player.player_invited.player_name,
                "joined_at": player.created_at,
                "created_at": player.player_invited.created_at
            }
            player_detail_list.append(player_detail)

        self.ctx["server_list"] = server_list_parsed
        self.ctx["player_list"] = player_detail_list

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_user = request.user

        # handle if user is anonymous
        if req_user.id == None:
            req_user = None

        player_name = request.POST.get("player-name")
        server_id = request.POST.get("server-target")

        player_details, _ = PlayerList.objects.get_or_create(
            player_name=player_name,
            defaults={
                "created_by": req_user,
                "updated_by": req_user,
            }
        )

        player_server_map, _ = PlayerServerMap.objects.get_or_create(
            player_invited=player_details,
            server_joined_id=server_id,
            defaults={
                "created_by": req_user,
                "updated_by": req_user,
            }
        )

        return redirect("player_list")
    
class PlayerJoinManagerView(View):
    template = "modules/player_list/templates/index_player_invite.html"
    ctx = {
        "page_title": "player_invite_room"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        req_data = request.GET

        self.ctx["invite_code"] = req_data.get("invitecode")

        return render(request, self.template, self.ctx)

    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST
        req_user = request.user

        # handle if user is anonymous
        if req_user.id == None:
            req_user = None

        invite_code = req_body.get("invite-code")
        server_id = req_body.get("server-id", None)


        try:
            player_name = req_body.get("player-name")
            if not player_name:
                raise Exception("player name empty")
            
            find_server = ServerList.objects.filter(Q(server_invite_code=invite_code) | Q(pk=server_id)).first()
            if not find_server:
                raise Exception("server not found")
            
            player, _ = PlayerList.objects.get_or_create(
                player_name = player_name,
                defaults={
                    "owner": find_server.created_by
                },
            )

            player_map, _ = PlayerServerMap.objects.get_or_create(
                player_invited = player,
                server_joined = find_server,
            )

        except Exception as err:
            print(f"Error when storing server: {err.args}")

        return redirect("player_join_server")
    
class PlayerManagerDetailView(View):

    def get(self, request: HttpRequest, *args, **kwargs):

        player_map_id = kwargs.get("id")
        resp_data = {}

        try:
            if not player_map_id:
                raise Exception("player_map_id is empty")
            
            player_server_map = PlayerServerMap.objects.filter(pk=player_map_id).first()
            if not player_server_map or not player_server_map.player_invited:
                raise Exception("Player for current server not found")
            
            player_details = player_server_map.player_invited

            server_list = []
            server_joined = player_details.player_server_map.all()
            for server in server_joined:
                if not server.server_joined:
                    server_list.append({
                        "server_id": 0,
                    })

                server_list.append({
                    "server_id": server.server_joined.pk,
                    "server_name": server.server_joined.server_name,
                    "server_id": server.server_joined.server_url,
                    "server_joined_at": server.created_at
                })
                
            resp_data["id"] = player_details.pk
            resp_data["name"] = player_details.player_name
            resp_data["server_list"] = server_list
            resp_data["created_at"] = player_details.created_at

            return JsonResponse(resp_data)

        except Exception as err:
            return JsonResponse(resp_data)
        
    def delete(self, request: HttpRequest, *args, **kwargs):

        player_map_id = kwargs.get("id")
        resp_data = {}

        try:
            if not player_map_id:
                raise Exception("player_map_id is empty")
            
            player_server_map = PlayerServerMap.objects.filter(pk=player_map_id).first()
            if not player_server_map or not player_server_map.player_invited:
                raise Exception("Player for current server not found")

            player_details = player_server_map.player_invited
            player_server_map_count_before = player_details.player_server_map.all().count()

            player_server_map.delete()

            if player_server_map_count_before <= 1:
                player_details.delete()

            resp_data["deleted"] = True

            return JsonResponse(resp_data)

        except Exception as err:
            resp_data["deleted"] = False
            return JsonResponse(resp_data)
