# Create your models here.

import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    def was_published_recently(self):
        """ Check whether this question has been published recently. """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """ Check whether this question has been published """
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """ Check whether this question can be voted """
        now = timezone.now()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """return the votes for this choice"""
        return self.vote_set.count()

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """A vote by a user for a choice in a poll"""
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
