from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question, Vote
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date")[
               :5
               ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """ Check weather it can vote or not if it cannot vote return error
        message"""
        question = self.get_object()
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return redirect('polls:index')

        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """ handle voting on a question """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        logger.error("An error occurred while updating the vote")
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    # Reference to the user
    this_user = request.user
    print("current user is", this_user.id, "login", this_user.username)
    print("Real name:", this_user.first_name, this_user.last_name)
    logger.info('User has submitted a vote')
    # Get user's vote
    try:
        # vote = this_user.vote_set.get(choice__question=question)
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # User has a vote for this question! Update his choice.
        vote.choice = selected_choice
        vote.save()
        messages.success(request,
                         f"Your vote was updated to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        logger.error("An error occurred while updating the vote")
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        # Does not have to vote yet
        # Auto save
        messages.success(request,
                         f"Your voted for '{selected_choice.choice_text}'")
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named field from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('polls:index')
        # What if form is not valid?
        # we should display a message in signup.html
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged in")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged out")


@receiver(user_login_failed)
def log_unsuccessful_login(sender, credentials, request, **kwargs):
    logger.warning(
        f"Unsuccessful login attempt for username: {credentials.get('username')}")
