
from django.urls import re_path
from channels.routing import URLRouter
from .views import ServerManagerRconShellView

urlpatterns = URLRouter([
    re_path(r"rconshell/(?P<room_name>\w+)/$", ServerManagerRconShellView.as_asgi(), name="rcon_websocket")
])
