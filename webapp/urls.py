
from django.urls import include, path

urlpatterns = [
    path('servermanager/', include("webapp.modules.server_list.urls"), name="server_manager"),
    path('playermanager/', include("webapp.modules.player_list.urls"), name="player_manager")
]
