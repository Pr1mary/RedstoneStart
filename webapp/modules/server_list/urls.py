
from django.urls import path
from .views import ServerManagerView, ServerManagerDetailView

urlpatterns = [
    path('', ServerManagerView.as_view(), name="server_list"),
    path('<int:id>', ServerManagerDetailView.as_view(), name="server_details"),
]
