from django.db import models
from django.contrib.auth.models import User
from ..server_list.models import ServerList

class PlayerList(models.Model):

    player_name = models.CharField(max_length=255, null=True, blank=True)
    invite_code = models.CharField(max_length=255, null=True, blank=True)
    owner = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_owner")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_cb")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_ub")

class PlayerServerMap(models.Model):
    
    player_invited = models.ForeignKey(PlayerList, on_delete=models.CASCADE, related_name="player_server_map")
    server_joined = models.ForeignKey(ServerList, on_delete=models.CASCADE, related_name="player_server_map")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_server_map_cb")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_server_map_ub")
    updated_at = models.DateTimeField(auto_now=True)
    