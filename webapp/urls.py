
from django.urls import include, path

urlpatterns = [
    path('servermanager/', include("webapp.modules.server_list.urls"), name="server_manager")
]
