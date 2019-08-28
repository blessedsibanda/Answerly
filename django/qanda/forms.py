from django import forms
from django.contrib.auth import get_user_model

from qanda.models import Question, Answer


class QuestionForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=get_user_model.objects.all(),
        widget=forms.HiddenInput,
        disabled=True,
    )
    class Meta:
        model = Question
        fields = ['title', 'question', 'user',]


class AnswerForm(forms.ModelForm):
    user = form.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True,
    )
    question = form.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=Question.objects.all(),
        disabled=True,
    )
    class Meta:
        model = Answer
        fields = ['answer', 'user', 'question',]


class AnswerAcceptanceForm(forms.ModelForm):
    accepted = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False,
    )
    class Meta:
        model = Answer
        fields = ['accepted',]