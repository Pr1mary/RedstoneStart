
from django.urls import path
from .views import (
    PlayerManagerView, PlayerManagerDetailView,
    PlayerJoinManagerView, PlayerBanManagerView,
    PlayerUnbanManagerView, PlayerSyncManagerView,
    PlayerJoinManagerSuccessView
    )

urlpatterns = [
    path('', PlayerManagerView.as_view(), name="player_list"),
    path('<int:id>', PlayerManagerDetailView.as_view(), name="player_details"),
    path('joinserver', PlayerJoinManagerView.as_view(), name="player_join_server"),
    path('joinserver/success', PlayerJoinManagerSuccessView.as_view(), name="player_join_server_success"),
    path('ban', PlayerBanManagerView.as_view(), name="player_server_ban"),
    path('unban', PlayerUnbanManagerView.as_view(), name="player_server_unban"),
    path('sync', PlayerSyncManagerView.as_view(), name="player_server_sync"),
]
