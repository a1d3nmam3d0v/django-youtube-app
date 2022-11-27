from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse  # converts name of url to the url path
from django.core.exceptions import ValidationError
from .models import Video

# Create your tests here.


class TestHomePageMessage(TestCase):
    def test_home_page_message_shows_app_name(self):
        # Should say "This is the Noise and Sound app."
        url = reverse("home")
        response = self.client.get(url)
        self.assertContains(response, "Noise and Sound")


class TestAddVideos(TestCase):
    def test_add_video(self):

        url = reverse("add_video")

        valid_video = {
            "name": "AIRPLANE SOUNDS",
            "notes": "10 hours of airplane cabin and jet sounds",
            "url": "https://www.youtube.com/watch?v=co7KgV2e",
        }
        # self.client.post for testing post requests
        response = self.client.post(url, data=valid_video, follow=True)

        # is the correct template is rendered?
        self.assertTemplateUsed("video_collection/video_list.html")

        # does the new video show up in the list?
        self.assertContains(response, "AIRPLANE SOUNDS")
        self.assertContains(response, "https://www.youtube.com/watch?v=co7KgV2e")
        self.assertContains(response, "10 hours of airplane cabin and jet sounds")

        # video counter shows right number of vids, correctly shows singular and plural video(s)?
        self.assertContains(response, "1 video:")
        self.assertNotContains(response, "1 videos:")

        # new vid in db
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # only 1 vid so it's the first one
        video = Video.objects.first()

        self.assertEqual("AIRPLANE SOUNDS", video.name)
        self.assertEqual("https://www.youtube.com/watch?v=co7KgV2e", video.url)
        self.assertEqual("10 hours of airplane cabin and jet sounds", video.notes)
        self.assertEqual("co7KgV2e", video.video_id)

    def test_invalid_url_video_isnt_added(self):
        # test videos with invalid urls not added to list

        invalid_video_urls = [
            "https://www.youtube.com/watch",
            "https://www.youtube.com/watch?",
            "https://www.youtube.com/watch?a=020202",
            "https://www.youtube.com/watch?v=",
            "https://www.google.com/",
            "https://www.gmail.com/watch?v=do3sK2r",
            "https://www.youtube.com/watch",
        ]

        for invalid_video_url in invalid_video_urls:
            new_video = {
                "name": "example",
                "url": invalid_video_url,
                "note": "example notes",
            }

            url = reverse("add_video")
            response = self.client.post(url, new_video)

            # should stay on the same page -  add.html
            self.assertTemplateNotUsed("video_collection/add.html")

            messages = response.context["messages"]
            message_texts = [message.message for message in messages]

            # assertIn looks for a specific string inside a list of strings
            # assertContains looks for a response inside a django webpage
            self.assertIn("Invalid YT URL", message_texts)
            self.assertIn("Unable to save - check entered data.", message_texts)

            # checks there is 0 videos in list
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    def test_all_videos_displayed_in_correct_order(self):
        # Displayed in proper (alphabetical) order?

        v1 = Video.objects.create(
            name="Xxx", notes="example", url="https://www.youtube.com/watch?v=123"
        )
        v2 = Video.objects.create(
            name="aaa", notes="example", url="https://www.youtube.com/watch?v=124"
        )
        v3 = Video.objects.create(
            name="Abc", notes="example", url="https://www.youtube.com/watch?v=125"
        )
        v4 = Video.objects.create(
            name="gogo", notes="example", url="https://www.youtube.com/watch?v=126"
        )

        expected_order = [v2, v3, v4, v1]

        url = reverse("video_list")
        response = self.client.get(url)

        # context is all the data combined with the template to display on page
        # the stuff rendered in perentheses
        videos_in_template = list(response.context["videos"])

        self.assertEqual(videos_in_template, expected_order)

    def test_no_video_message(self):
        # When there's no videos in the list?
        url = reverse("video_list")
        response = self.client.get(url)
        self.assertContains(response, "No videos.")
        self.assertEqual(0, len(response.context["videos"]))

    def test_video_count_says_one_video(self):
        v1 = Video.objects.create(
            name="xyz", notes="notenotenote", url="https://www.youtube.com/watch?v=123"
        )
        url = reverse("video_list")
        response = self.client.get(url)
        self.assertContains(response, "1 video")
        self.assertNotContains(response, "1 videos")

    def test_video_count_says_two_videos(self):
        v1 = Video.objects.create(
            name="abc", notes="lalala", url="https://www.youtube.com/watch?v=420"
        )
        v2 = Video.objects.create(
            name="xyz", notes="zzzz", url="https://www.youtube.com/watch?v=666"
        )

        url = reverse("video_list")
        response = self.client.get(url)
        self.assertContains(response, "2 videos")

    def test_video_search_matches(self):
        # test the search results only show matches or partial matches (case-insensitive)
        v1 = Video.objects.create(
            name="ABC", notes="example", url="https://www.youtube.com/watch?v=436"
        )
        v2 = Video.objects.create(
            name="nonono", notes="example", url="https://www.youtube.com/watch?v=844"
        )
        v3 = Video.objects.create(
            name="abc1234", notes="example", url="https://www.youtube.com/watch?v=584"
        )
        v4 = Video.objects.create(
            name="hello no",
            notes="example",
            url="https://www.youtube.com/watch?v=929",
        )

        expected_video_order = [v1, v3]
        response = self.client.get(reverse("video_list") + "?search_term=abc")
        videos_in_template = list(response.context["videos"])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_results_no_matches(self):
        v1 = Video.objects.create(
            name="hello", notes="aaaaa", url="https://www.youtube.com/watch?v=123"
        )
        v2 = Video.objects.create(
            name="goodbye", notes="aaaaa", url="https://www.youtube.com/watch?v=8329"
        )
        v3 = Video.objects.create(
            name="derp", notes="aaaaa", url="https://www.youtube.com/watch?v=38239"
        )
        v4 = Video.objects.create(
            name="meh", notes="aaaaa", url="https://www.youtube.com/watch?v=38292"
        )

        expected_video_order = []
        response = self.client.get(reverse("video_list") + "?search_term=blah")
        videos_in_template = list(response.context["videos"])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, "No videos")


class TestVideoSearch(TestCase):
    pass


class TestVideoModel(TestCase):
    def test_invalid_url_raises_validation_error(self):
        # Does invalid URL raise validation error?

        invalid_video_urls = [
            "https://www.youtube.com/watch",
            "https://www.youtube.com/watch?",
            "https://www.youtube.com/watch?a=020202",
            "https://www.youtube.com/watch?v=",
            "https://www.google.com/",
            "https://www.gmail.com/watch?v=do3sK2r",
            "https://www.youtube.com/watch/",
            "https://www.youtube.com/watch/extrastuff",
            "https://www.youtube.com/watch/extrastuff?v=28393",  # sneaky passss
            "12345678",
            "hhhhhhhttps://www.youtube.com/watch",
            "http://www.youtube.com/watch/somestuff?v=293829",
            "https://github.com/watch?v=3902230",
        ]

        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):

                Video.objects.create(
                    name="example", notes="ffffff", url=invalid_video_url
                )
        self.assertEqual(0, Video.objects.count())

    def test_duplicate_video_raises_integrity_error(self):
        # Does adding the same video twice raise an error?

        v1 = Video.objects.create(
            name="abc", notes="123", url="https://www.youtube.com/watch?v=789"
        )
        with self.assertRaises(IntegrityError):
            Video.objects.create(
                name="abc", notes="123", url="https://www.youtube.com/watch?v=789"
            )
