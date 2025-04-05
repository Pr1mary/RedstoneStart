
from django.urls import path
from .views import ServerManagerView

urlpatterns = [
    path('', ServerManagerView.as_view(), name="server_list"),
]
