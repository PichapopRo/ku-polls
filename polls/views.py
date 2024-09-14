"""Import every django essential package."""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question, Vote
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed
from django.dispatch import receiver
from django.http import Http404

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """This class is for index view or the main poll page and initializing."""

    template_name = 'polls/index.html'
    context_object_name = "latest_question_list"
    ordered_questions = Question.objects.order_by('-pub_date')

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date")[:5]


class DetailView(generic.DetailView):
    """This class is for detail view or the main poll page and initializing."""

    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        """To return the past vote of the user."""
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Get the current user's vote for this question, if it exists
        if self.request.user.is_authenticated:
            try:
                vote = Vote.objects.get(user=self.request.user,
                                        choice__question=question)
                context[
                    'user_vote'] = vote.choice.id
            except Vote.DoesNotExist:
                context['user_vote'] = None

        return context

    def get(self, request, *args, **kwargs):
        """Rewrote the get method to make it be able to redirect user."""
        try:
            # Try to get the object. If it doesn't exist, it will raise
            # Http404.
            question = self.get_object()
        except Http404:
            messages.error(request, "The requested poll does not exist.")
            return redirect('polls:index')

        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return redirect('polls:index')

        # If everything is fine, proceed to the default behavior.
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """Initializing the result page and render the page."""

    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """Handle voting on a question."""
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
                         f"Your vote was updated to "
                         f"'{selected_choice.choice_text}'")
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
    return render(
        request, 'registration/signup.html',
        {'form': form})


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Use signals to log data into the log file."""
    ip_add = get_client_ip(request)
    logger.info(f"User {user.username} logged in. IP: {ip_add}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Use a signal when the user logs out to log all relevant information."""
    logger.info(f"User {user.username} logged out")


@receiver(user_login_failed)
def log_unsuccessful_login(sender, credentials, request, **kwargs):
    """Use signal from failed login attempt to log."""
    logger.warning(
        f"Unsuccessful login attempt for username: "
        f"{credentials.get('username')}")


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
