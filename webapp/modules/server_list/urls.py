
from django.urls import path
from .views import ServerManagerView, ServerManagerDetailView, ServerManagerInviteView, ServerManagerInviteDetailsView

urlpatterns = [
    path('', ServerManagerView.as_view(), name="server_list"),
    path('<int:id>', ServerManagerDetailView.as_view(), name="server_details"),
    path('invite/<int:id>', ServerManagerInviteDetailsView.as_view(), name="server_invite"),
]
