
from django.urls import path
from channels.routing import URLRouter
from .views import ServerManagerRconShellView

urlpatterns = URLRouter([
    path("rconshell/", ServerManagerRconShellView.as_asgi(), name="rcon_websocket")
])
