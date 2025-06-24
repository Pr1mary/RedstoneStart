from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.generic import View
from .models import PlayerList, PlayerServerMap, ServerList
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import connection
from webapp.utils.mc_rcon_util import MCRconUtil
from multiprocessing import Process, Pool, Manager
from datetime import datetime

import random, string, json

class PlayerManagerView(LoginRequiredMixin, View):
    template = "modules/player_list/templates/index.html"
    ctx = {
        "page_title": "player_manager"
    }
    login_url = "/accounts/auth/login"

    def get(self, request: HttpRequest, *args, **kwargs):

        server_id = request.GET.get("server_id", None)
        username_target = request.GET.get("username", None)
        user_status = request.GET.get("status", None)
        try:
            server_id = int(server_id)
        except:
            server_id = None

        curr_server_id = None
        server_list_parsed = []
        server_list = ServerList.objects.all().order_by("created_at")
        if not server_id and server_list:
            server_id = server_list.first().pk
            curr_server_id = server_id
        for server in server_list:
            server_list_parsed.append({
                "id": server.pk,
                "name": server.server_name,
                "active": server.pk == server_id
            })
            if server.pk == server_id:
                curr_server_id = server_id
        player_map_list = PlayerServerMap.objects.filter(server_joined__pk=server_id).order_by("-created_at")

        if username_target:
            player_map_list = player_map_list.filter(player_invited__player_name__icontains=username_target)

        if user_status and user_status == "BANNED":
            player_map_list = player_map_list.filter(banned_status=True)
        elif user_status and user_status == "FAILED":
            player_map_list = player_map_list.filter(is_synced=False)
        elif user_status and user_status == "OUTSTANDING":
            player_map_list = player_map_list.filter(banned_status=False, is_synced=True)
        
        player_server_detail_list = []
        for player in player_map_list:

            status_name = "ONLINE" if player.online_status else "OFFLINE"
            status_name = "BANNED" if player.banned_status else status_name
            status_name = "FAILED" if not player.is_synced else status_name

            player_detail = {
                "id": player.pk,
                "name": player.player_invited.player_name,
                "status": status_name, 
                "joined_at": player.created_at,
                "created_at": player.player_invited.created_at
            }
            player_server_detail_list.append(player_detail)

        self.ctx["server_list"] = server_list_parsed
        self.ctx["curr_server_id"] = curr_server_id
        self.ctx["curr_username_target"] = username_target if username_target else ""
        self.ctx["curr_filter_status"] = user_status
        self.ctx["player_server_list"] = player_server_detail_list

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

        player_server_map, player_server_map_created = PlayerServerMap.objects.get_or_create(
            player_invited=player_details,
            server_joined_id=server_id,
            defaults={
                "created_by": req_user,
                "updated_by": req_user,
            }
        )

        if player_server_map_created:
            # player_mapping_process = Process(target=self.__add_whitelist_player, args=[player_server_map.pk])
            # player_mapping_process.start()

            player_handler = PlayerHandler()
            player_handler.add_whitelist_player(player_server_map.pk)


        return redirect("player_list")
    
    def __add_whitelist_player(self, player_server_id:str):

        try:
            connection.close()
            
            if not player_server_id:
                raise Exception("Player server map id is empty")
            
            player_server_map_details = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_server_map_details:
                raise Exception("Player server map not found")

            server_address = player_server_map_details.server_joined.server_url
            server_secret = player_server_map_details.server_joined.server_secret
            server_is_vanilla = player_server_map_details.server_joined.server_is_vanilla

            player_name = player_server_map_details.player_invited.player_name

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_whitelist = mcrcon.addWhitelist(player_name)
            if not player_whitelist:
                raise Exception("problem when whitelisting player")

            print("Add player '{}' to whitelist success".format(player_name))
            
            player_online_list = mcrcon.getPlayerList()
            if player_name in player_online_list:
                player_server_map_details.online_status = True
                
                print("Player '{}' status updated to ONLINE".format(player_name))
            
            player_server_map_details.is_synced = True
            player_server_map_details.save()

        except Exception as err:
            print("Error add player whitelist: {}".format(err))
        
        finally:
            connection.close()
    
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
                    "created_by": find_server.created_by,
                    "updated_by": find_server.created_by,
                },
            )

            player_server_map, _ = PlayerServerMap.objects.get_or_create(
                player_invited = player,
                server_joined = find_server,
                defaults={
                    "created_by": find_server.created_by,
                    "updated_by": find_server.created_by,
                },
            )

            player_handler = PlayerHandler()
            player_handler.add_whitelist_player(player_server_map.pk)

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

                status_name = "ONLINE" if server.online_status else "OFFLINE"
                status_name = "BANNED" if server.banned_status else status_name
                status_name = "FAILED" if not server.is_synced else status_name

                server_list.append({
                    "server_player_id": server.pk,
                    "server_id": server.server_joined.pk,
                    "server_name": server.server_joined.server_name, 
                    "server_url": server.server_joined.server_url,
                    "server_joined_at": server.created_at,
                    "player_status": status_name
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

            server_id = player_server_map.server_joined.pk
            player_name = player_details.player_name

            player_server_map.delete()

            if player_server_map_count_before <= 1:
                player_details.delete()

            player_mapping_process = Process(target=self.__remove_whitelist_player, args=[server_id, player_name])
            player_mapping_process.start()
            
            resp_data["deleted"] = True

            return JsonResponse(resp_data)

        except Exception as err:
            resp_data["deleted"] = False
            return JsonResponse(resp_data)

    def __remove_whitelist_player(self, server_id: str, player_name:str):

        try:
            connection.close()
            
            if not player_name:
                raise Exception("Player name is empty")
            elif not server_id:
                raise Exception("Server id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("Server not found")

            server_address = server_details.server_url
            server_secret = server_details.server_secret
            server_is_vanilla = server_details.server_is_vanilla

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_whitelist = mcrcon.delWhitelist(player_name)
            if not player_whitelist:
                raise Exception("problem when removing whitelisted player")

            print("Remove player '{}' from whitelist success".format(player_name))

        except Exception as err:
            print("Error remove player whitelist: {}".format(err))
        
        finally:
            connection.close()


class PlayerBanManagerView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST

        player_server_id = req_body.get("player-server-id", None)
        ban_reason = req_body.get("reason-text", "Banned by administrator")
        resp_data = {}

        try:

            player_map = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_map:
                raise Exception("player server map was not found")
            
            player_map.banned_status = True
            player_map.banned_reason = ban_reason
            player_map.banned_at = datetime.now()
            player_map.save()

            player_handler = PlayerHandler()
            player_handler.ban_player(player_map.pk)
            
            resp_data["banned"] = True

        except Exception as err:
            print(f"Error when banning player to server: {err.args}")
            resp_data["banned"] = False

        return JsonResponse(resp_data)
    
class PlayerUnbanManagerView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST

        player_server_id = req_body.get("player-server-id", None)
        resp_data = {}

        try:

            player_map = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_map:
                raise Exception("player server map was not found")
            
            player_map.banned_status = False
            player_map.save()

            player_handler = PlayerHandler()
            player_handler.unban_player(player_map.pk)
            
            resp_data["unbanned"] = True

        except Exception as err:
            print(f"Error when unbanning player to server: {err.args}")
            resp_data["unbanned"] = False

        return JsonResponse(resp_data)
    
class PlayerSyncManagerView(View):
    
    def post(self, request: HttpRequest, *args, **kwargs):

        req_body = request.POST

        server_id = req_body.get("server-id", None)
        resp_data = {}

        try:
            player_handler = PlayerHandler()
            result = player_handler.get_list_player(server_id)
            player_list:list = result.get("player_list")
            banned_list:list = result.get("banned_list")
            online_list:list = result.get("online_list")

            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise "Server not found"
            
            for player_raw in player_list:
                player_data = PlayerList.objects.filter(player_name=player_raw).first()
                if not player_data:
                    player_data = PlayerList.objects.create(
                        player_name = player_raw,
                        created_by = request.user,
                        updated_by = request.user,
                    )

                is_banned = player_raw in banned_list
                
                player_mapping = PlayerServerMap.objects.filter(player_invited=player_data, server_joined=server_details).first()
                if not player_mapping:
                    player_mapping = PlayerServerMap.objects.create(
                        player_invited = player_data,
                        server_joined = server_details,
                        is_synced = True,
                        online_status = True,
                        banned_status = is_banned,
                        created_by = request.user,
                        updated_by = request.user,
                    )
                elif is_banned:
                    player_mapping.banned_status = True
                    player_mapping.save()
                elif player_mapping.banned_status and not is_banned:
                    player_mapping.banned_status = False
                    player_mapping.save()

            resp_data["success"] = True

        except Exception as err:
            print(f"Error when fetching player on the server: {err.args}")
            resp_data["success"] = False

        return JsonResponse(resp_data)
    
class PlayerHandler():

    def add_whitelist_player(self, player_server_id:str):
        
        player_mapping_process = Process(target=self.__add_whitelist, args=[player_server_id])
        player_mapping_process.start()

    def del_whitelist_player(self, server_id: str, player_name:str):

        player_mapping_process = Process(target=self.__remove_whitelist, args=[server_id, player_name])
        player_mapping_process.start()

    def ban_player(self, player_server_id:str):
        
        player_mapping_process = Process(target=self.__ban_player, args=[player_server_id])
        player_mapping_process.start()

    def unban_player(self, player_server_id:str):

        player_mapping_process = Process(target=self.__unban_player, args=[player_server_id])
        player_mapping_process.start()

    def get_list_player(self, server_id):

        manager = Manager()
        return_dict = manager.dict()

        player_mapping_process = Process(target=self.__player_list, args=[server_id, return_dict])
        player_mapping_process.start()
        player_mapping_process.join()

        return return_dict
    
    def __add_whitelist(self, player_server_id:str):

        try:
            connection.close()
            
            if not player_server_id:
                raise Exception("Player server map id is empty")
            
            player_server_map_details = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_server_map_details:
                raise Exception("Player server map not found")

            server_address = player_server_map_details.server_joined.server_url
            server_secret = player_server_map_details.server_joined.server_secret
            server_is_vanilla = player_server_map_details.server_joined.server_is_vanilla

            player_name = player_server_map_details.player_invited.player_name

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_whitelist = mcrcon.addWhitelist(player_name)
            if not player_whitelist:
                raise Exception("problem when whitelisting player")

            print("Add player '{}' to whitelist success".format(player_name))
            
            player_online_list = mcrcon.getPlayerList()
            if player_name in player_online_list:
                player_server_map_details.online_status = True
                
                print("Player '{}' status updated to ONLINE".format(player_name))
            
            player_server_map_details.is_synced = True
            player_server_map_details.save()

        except Exception as err:
            print("Error add player whitelist: {}".format(err))
        
        finally:
            connection.close()

    def __remove_whitelist(self, server_id: str, player_name:str):

        try:
            connection.close()
            
            if not player_name:
                raise Exception("Player name is empty")
            elif not server_id:
                raise Exception("Server id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("Server not found")

            server_address = server_details.server_url
            server_secret = server_details.server_secret
            server_is_vanilla = server_details.server_is_vanilla

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_whitelist = mcrcon.delWhitelist(player_name)
            if not player_whitelist:
                raise Exception("problem when removing whitelisted player")

            print("Remove player '{}' from whitelist success".format(player_name))

        except Exception as err:
            print("Error remove player whitelist: {}".format(err))
        
        finally:
            connection.close()

    def __ban_player(self, player_server_id:str):

        try:
            connection.close()
            
            if not player_server_id:
                raise Exception("Player server map id is empty")
            
            player_server_map_details = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_server_map_details:
                raise Exception("Player server map not found")

            server_address = player_server_map_details.server_joined.server_url
            server_secret = player_server_map_details.server_joined.server_secret
            server_is_vanilla = player_server_map_details.server_joined.server_is_vanilla

            player_name = player_server_map_details.player_invited.player_name

            ban_reason = player_server_map_details.banned_reason

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_banned = mcrcon.banPlayer(player_name, ban_reason)
            if not player_banned:
                raise Exception("problem when banning player")

            print("Ban player '{}' success".format(player_name))
            
        except Exception as err:
            print("Error when banning player: {}".format(err))
        
        finally:
            connection.close()
    
    def __unban_player(self, player_server_id:str):

        try:
            connection.close()
            
            if not player_server_id:
                raise Exception("Player server map id is empty")
            
            player_server_map_details = PlayerServerMap.objects.filter(pk=player_server_id).first()
            if not player_server_map_details:
                raise Exception("Player server map not found")

            server_address = player_server_map_details.server_joined.server_url
            server_secret = player_server_map_details.server_joined.server_secret
            server_is_vanilla = player_server_map_details.server_joined.server_is_vanilla

            player_name = player_server_map_details.player_invited.player_name

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_unbanned = mcrcon.pardonPlayer(player_name)
            if not player_unbanned:
                raise Exception("problem when unbanning player")

            print("Unban player '{}' success".format(player_name))
            
        except Exception as err:
            print("Error when unbanning player: {}".format(err))
        
        finally:
            connection.close()
    
    def __player_list(self, server_id:str, return_dict:dict):

        try:
            connection.close()
            
            if not server_id:
                raise Exception("Server id is empty")
            
            server_details = ServerList.objects.filter(pk=server_id).first()
            if not server_details:
                raise Exception("Server not found")

            server_address = server_details.server_url
            server_secret = server_details.server_secret
            server_is_vanilla = server_details.server_is_vanilla

            mcrcon = MCRconUtil(server_address, server_secret, is_vanilla=server_is_vanilla)
            player_list = mcrcon.getWhitelist()
            if not player_list:
                raise Exception("problem when getting list of player")
            
            ban_list = mcrcon.getBanList(player_list)
            if not player_list:
                raise Exception("problem when getting list of player")

            return_dict["player_list"] = player_list
            return_dict["banned_list"] = ban_list
            return_dict["online_list"] = []

            print("Fetch player list success")

        except Exception as err:
            return_dict["player_list"] = []
            return_dict["banned_list"] = []
            return_dict["online_list"] = []
            print("Error when fetching player list: {}".format(err))
        
        finally:
            connection.close()