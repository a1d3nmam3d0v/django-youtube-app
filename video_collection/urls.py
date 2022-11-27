from django.urls import path

from . import views

# ((((( every page needs URL, view, template ))))


urlpatterns = [
    path("", views.home, name="home"),
    path("add", views.add, name="add_video"),
    path("video_list", views.video_list, name="video_list"),
]
