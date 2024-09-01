import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


# Create your tests here.

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """test if question was published in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """ test if question was published in the past"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ test if question was published in the recently"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_pub_date(self):
        """test is_published if question was published in the future"""
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """test is_published if question was published in the default date"""
        now_question = Question(pub_date=timezone.now())
        self.assertIs(now_question.is_published(), True)

    def test_is_published_with_past_pub_date(self):
        """test is_published if question was published in the past"""
        past_time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=past_time)
        self.assertIs(past_question.is_published(), True)

    def can_vote_with_end_date_passed(self):
        """Test end_date after end date has passed"""
        pub_date = timezone.now() + datetime.timedelta(days=3)
        end_date = timezone.localtime().date() - datetime.timedelta(days=1)
        question = Question(pub_date=timezone.localtime() -
                                     datetime.timedelta(days=3)
                            , end_date=end_date)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_without_end_date(self):
        """can_vote returns True if there is no end_date and the current
        date is after pub_date."""
        pub_date = timezone.localtime().date() - datetime.timedelta(days=1)
        question = Question(
            pub_date=timezone.localtime() - datetime.timedelta(days=1),
            end_date=None)
        self.assertIs(question.can_vote(), True)

    def test_cannot_vote_before_pub_date(self):
        """can_vote returns False if the current date is before the
        pub_date."""
        pub_date = timezone.localtime().date() + datetime.timedelta(days=1)
        question = (Question
                    (pub_date=timezone.localtime()
                              + datetime.timedelta(days=1),
                     end_date=None))
        self.assertIs(question.can_vote(), False)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexVIewTest(TestCase):
    def test_index(self):
        """If no questions exist, an appropriate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_failure_question_and_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.",
                                          days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
