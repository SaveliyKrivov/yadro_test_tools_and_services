from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.ProfileListView.as_view(), name="profile_list"),
    path("<int:profile_id>", views.ProfileDetailView.as_view(), name="profile_detail"),
    path("random", views.RandomProfileView.as_view(), name="random_profile"),
]
