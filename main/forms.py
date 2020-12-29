from django.core.exceptions import ValidationError
from django import forms
from django.urls import reverse

from main.models import Candidate, Position

import requests


def validate_student(username, password):
    data = {
        'username': username,
        'password': password
    }
    try:
        response = requests.post("https://mouauportal.edu.ng/login.php", data)
    except requests.exceptions.ConnectionError:
        return None
    if response.url == 'https://mouauportal.edu.ng/my-account-student.php':
        return True
    else:
        return False
        

class RegForm(forms.Form):
    username = forms.CharField(max_length="10")
    password = forms.CharField(max_length="10", widget=forms.widgets.PasswordInput())

    def clean(self):
        cleaned_data = super(RegForm, self).clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if validate_student(username, password):
            return cleaned_data
        else:
            raise ValidationError('Invalid username and password')

def format_name(name):
    formatted = ""
    name_list = name.split()
    for idx, word in enumerate(name_list):
        formatted += word[0].upper() + word[1:].lower()
        if (idx + 1) != len(name_list):
            formatted += " "
    return formatted


class CandidateRegistrationForm(forms.Form):
    name = forms.CharField(max_length=20)
    level = forms.ChoiceField(choices=Candidate.Levels.choices)
    position = forms.ModelChoiceField(queryset=Position.objects.all())

    def clean_name(self):
        name = format_name(self.cleaned_data.get("name"))
        try:
            Candidate.objects.get(name=name)
            raise ValidationError("Candidate exists")
        except Candidate.DoesNotExist:
            return name

    def save(self, form):
        candidate = Candidate.objects.create(
            name = form.cleaned_data.get("name"),
            level = form.cleaned_data.get("level"),
            post = form.cleaned_data.get("position"),
        )
        position = Position.objects.get(name=form.cleaned_data.get("position"))
        position.candidates.add(candidate)
        return candidate


class PositionRegistrationForm(forms.Form):
    name = forms.CharField(max_length=30)
    
    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        try:
            Position.objects.get(name=name)
            raise ValidationError("Position exists")
        except Position.DoesNotExist:
            return name 

    def save(self, form):
        position = Position.objects.create(
            name=form.cleaned_data.get("name"),
        )
        return position 