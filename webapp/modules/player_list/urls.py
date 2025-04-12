
from django.urls import path
from .views import PlayerManagerView, PlayerManagerDetailView, PlayerJoinManagerView

urlpatterns = [
    path('', PlayerManagerView.as_view(), name="player_list"),
    path('<int:id>', PlayerManagerDetailView.as_view(), name="player_details"),
    path('joinserver', PlayerJoinManagerView.as_view(), name="player_join_server"),
]
