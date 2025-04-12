
from django.urls import include, path

urlpatterns = [
    path('', include("webapp.modules.main_page.urls"), name="main_page"),
    path('servermanager/', include("webapp.modules.server_list.urls"), name="server_manager"),
    path('playermanager/', include("webapp.modules.player_list.urls"), name="player_manager"),
    path('accounts/', include("webapp.modules.accounts.urls"), name="accounts"),
]
