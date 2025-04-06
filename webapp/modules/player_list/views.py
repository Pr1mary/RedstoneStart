from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from .models import PlayerList, PlayerServerMap, ServerList
from django.db.models import Q

import random, string, json

class PlayerManagerView(View):
    template = "modules/player_list/templates/index.html"
    ctx = {
        "page_title": "player_manager"
    }

    def get(self, request: HttpRequest, *args, **kwargs):

        player_list = PlayerList.objects.all().order_by("-created_at")
        player_detail_list = []
        for player in player_list:
            player_detail = {
                "id": player.pk,
                "name": player.player_name,
            }
            player_detail_list.append(player_detail)

        self.ctx["player_list"] = player_detail_list

        return render(request, self.template, self.ctx)
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST
        req_user = request.user

        # handle if user is anonymous
        if req_user.id == None:
            req_user = None

        player_url = req_body.get("server-address")
        player_name = req_body.get("server-name")

        try:

            player_list = PlayerList(
                player_name = player_name,
            )
            player_list.save()

        except Exception as err:
            print(f"Error when storing server: {err.args}")

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

        player_id = kwargs.get("id")
        resp_data = {}

        try:
            if not player_id:
                raise Exception("player_id is empty")
            
            player_details = ServerList.objects.filter(pk=player_id).first()
            if not player_details:
                raise Exception("player_details is empty")
                
            resp_data["id"] = player_details.pk
            resp_data["name"] = player_details.player_name
            resp_data["url"] = player_details.player_url
            resp_data["active"] = player_details.is_active
            resp_data["players"] = 0

            return JsonResponse(resp_data)

        except Exception as err:
            return JsonResponse(resp_data)
        
    def delete(self, request: HttpRequest, *args, **kwargs):

        player_id = kwargs.get("id")
        resp_data = {}

        try:
            if not player_id:
                raise Exception("player_id is empty")
            
            player_details = ServerList.objects.filter(pk=player_id).first()
            if not player_details:
                raise Exception("player_details is empty")
                
            player_details.delete()

            resp_data["deleted"] = True

            return JsonResponse(resp_data)

        except Exception as err:
            resp_data["deleted"] = False
            return JsonResponse(resp_data)
