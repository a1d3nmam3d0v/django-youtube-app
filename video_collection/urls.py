from django.urls import path

from . import views

# ((((( every page needs URL, view, template ))))


urlpatterns = [
    path("", views.home, name="home"),
    path("add", views.add, name="add_video"),
    path("video_list", views.video_list, name="video_list"),
    # Lab part 2 -
    # Create a new page that displays all the data about one video.
    path("video/<int:video_pk>", views.video_details, name="video_details"),
]
