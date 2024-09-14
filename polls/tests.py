"""Import the essential package for testing."""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    """Tests for Question model."""

    def test_was_published_recently_with_future_question(self):
        """Test if question was published in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.was_published_recently())

    def test_was_published_recently_with_old_question(self):
        """Test if question was published in the past."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertFalse(old_question.was_published_recently())

    def test_was_published_recently_with_recent_question(self):
        """Test if question was published in the recently."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())

    def test_is_published_with_future_pub_date(self):
        """Test is_published if question was published in the future."""
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertFalse(future_question.is_published())

    def test_is_published_with_default_pub_date(self):
        """Test is_published if question was published in the default date."""
        now_question = Question(pub_date=timezone.now())
        self.assertTrue(now_question.is_published())

    def test_is_published_with_past_pub_date(self):
        """Test is_published if question was published in the past."""
        past_time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=past_time)
        self.assertTrue(past_question.is_published())

    def can_vote_with_end_date_passed(self):
        """Test end_date after end date has passed."""
        end_date = timezone.localtime().date() - datetime.timedelta(days=1)
        question = Question(
            pub_date=timezone.localtime() - datetime.timedelta(days=3),
            end_date=end_date)
        self.assertFalse(question.can_vote())

    def test_can_vote_without_end_date(self):
        """can_vote returns True if no end_date and the current date passed."""
        question = Question(
            pub_date=timezone.localtime() - datetime.timedelta(days=1),
            end_date=None)
        self.assertTrue(question.can_vote())

    def test_cannot_vote_before_pub_date(self):
        """can_vote returns False if the current is before the pub_date."""
        question = (Question
                    (pub_date=timezone.localtime() + datetime.timedelta(
                        days=1),
                     end_date=None))
        self.assertFalse(question.can_vote())


def create_question(question_text, days):
    """Create and publish a question with a `days` offset."""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexVIewTest(TestCase):
    """Tests for Question index view."""

    def test_index(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_past_question(self):
        """Display questions with a past `pub_date` on the index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_failure_question_and_past_question(self):
        """Test failure question and past `pub_date` on index view."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Tests for question detail view."""

    def test_past_question(self):
        """Show the question's text if `pub_date` is in the past."""
        past_question = create_question(question_text="Past Question.",
                                        days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
