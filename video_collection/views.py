from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import Lower
from .forms import VideoForm, SearchForm
from .models import Video

# ((((( every page needs URL, view, template ))))

# Create your views here.


def home(request):
    app_name = "Noise and Sound"  # for home.html "Welcome to the ___ app!" heading
    return render(request, "video_collection/home.html", {"app_name": app_name})


def add(request):
    """Determine if request is GET OR POST-
    If POST, validate, then add/save new video from form data,
    redirect to video list if successful
    """
    if request.method == "POST":
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():  # validate first
            try:
                new_video_form.save()  # save to db
                return redirect("video_list")  # redirect to video list
            except ValidationError:
                messages.warning(request, "Invalid YT URL")
            except IntegrityError:
                messages.warning(request, "Video already in list.")

        messages.warning(request, "Unable to save - check entered data.")
        return render(
            request, "video_collection/add.html", {"new_video_form": new_video_form}
        )
    new_video_form = VideoForm()
    return render(
        request, "video_collection/add.html", {"new_video_form": new_video_form}
    )


def video_list(request):
    # builds form from user's data sent to the app
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        search_term = search_form.cleaned_data["search_term"]
        videos = Video.objects.filter(name__icontains=search_term).order_by(
            Lower("name")
        )

    else:
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower("name"))

    return render(
        request,
        "video_collection/video_list.html",
        {"videos": videos, "search_form": search_form},
    )


def video_details(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    return render(request, "video_collection/video_detail.html", {"video": video})