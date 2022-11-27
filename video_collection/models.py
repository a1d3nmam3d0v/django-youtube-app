# urllib parses/splits url into parts
from urllib import parse

from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Video(models.Model):  # mapping db columns to object fields in Video class
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # Overrides django's automatic save method, and runs first.
        # extract vid ID from YT URL

        if not self.url.startswith("https://www.youtube.com/watch"):
            raise ValidationError("Not a YT URL {self.url}")

        url_components = parse.urlparse(self.url)
        query_string = url_components.query
        if not query_string:
            raise ValidationError(f"Invalid YT URL {self.url}")

        parameters = parse.parse_qs(query_string, strict_parsing=True)  # dictionary
        v_parameters_list = parameters.get("v")  # return None if no key found

        if not v_parameters_list:
            raise ValidationError(f"Invalid YT YRL - missing parameters {self.url}")
        self.video_id = v_parameters_list[0]  # string 

        super().save(*args, **kwargs) # calls django's save method to actually save data to db

    def __str__(self):
        return f"ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}"
