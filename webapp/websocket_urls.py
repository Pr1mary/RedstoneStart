
from django.urls import path
from channels.routing import URLRouter

from .modules.server_list.websocket_urls import urlpatterns as server_list_pattern

urlpatterns = URLRouter([
    path('servermanager/', server_list_pattern, name="server_manager"),
])
