"""Tests of user authentication.

   Put this file in a subdirectory of your ku-polls project,
   for example, a directory named "auth".
   Then run: manage.py test auth

"""
import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from polls.models import Question, Choice
from mysite import settings
from django.http import HttpResponse
from django.test import Client


def user_vote(client: Client, choice: Choice):
    response = client.post(reverse("polls:vote", args=(choice.question_id,)),
                           {"choice": choice.id})


class UserAuthTest(django.test.TestCase):

    def setUp(self):
        # superclass setUp creates a Client object and initializes test
        # database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can log in using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        # the query parameter ?next=/polls/1/vote/
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_registration(self):
        # Post data to the registration form
        registration_data = {
            'username': 'newuser',
            'password1': 'complexpassword',
            'password2': 'complexpassword',
        }
        response = self.client.post(reverse('signup'), registration_data)
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newuser')
        self.assertIsNotNone(new_user)

    def test_user_can_login_after_registration(self):
        """Test that a new user can log in after registering."""
        registration_data = {
            'username': 'newuser',
            'password1': 'newstrongpassword123',
            'password2': 'newstrongpassword123',
        }
        self.client.post(reverse('signup'), registration_data)
        login_data = {
            'username': 'newuser',
            'password': 'newstrongpassword123',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class VoteTests(django.test.TestCase):

    def setUp(self):
        # Create a test user and log them in
        self.user1 = User.objects.create_user(username='testuser1',
                                              password='testpassword')
        self.client.force_login(self.user1)

        # Create a test question and two choices
        self.question = Question.objects.create(question_text="Test question",
                                                pub_date="2023-09-01")
        self.choice1 = Choice.objects.create(choice_text="Choice 1",
                                             question=self.question)
        self.choice2 = Choice.objects.create(choice_text="Choice 2",
                                             question=self.question)

    def test_user_can_vote_only_once(self):
        """A user can vote on only one choice."""
        vote_url = reverse('polls:vote', args=[self.question.id])

        # User votes for choice1
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 302)  # Redirect after voting

        # Check that choice1 gets 1 vote and choice2 gets 0 votes
        self.choice1.refresh_from_db()
        self.choice2.refresh_from_db()
        self.assertEqual(self.choice1.votes, 1)
        self.assertEqual(self.choice2.votes, 0)

        # User changes vote to choice2
        response = self.client.post(vote_url, {'choice': self.choice2.id})
        self.assertEqual(response.status_code, 302)  # Redirect after voting

        # Check that choice1 has 0 votes and choice2 has 1 vote
        self.choice1.refresh_from_db()
        self.choice2.refresh_from_db()
        self.assertEqual(self.choice1.votes, 0)
        self.assertEqual(self.choice2.votes, 1)


class UnauthenticatedVoteTest(django.test.TestCase):

    def setUp(self):
        # Create a test question and choices
        self.question = Question.objects.create(question_text="Test question",
                                                pub_date="2023-09-01")
        self.choice1 = Choice.objects.create(choice_text="Choice 1",
                                             question=self.question)
        self.choice2 = Choice.objects.create(choice_text="Choice 2",
                                             question=self.question)

    def test_unauthenticated_user_cannot_vote(self):
        """An unauthenticated user should be redirected to the login page when attempting to vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])

        # Attempt to vote without logging in
        response = self.client.post(vote_url, {'choice': self.choice1.id})

        # Check that the response redirects to the login page
        expected_login_url = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, expected_login_url)

        # Ensure that the vote was not counted
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 0)
