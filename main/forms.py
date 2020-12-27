from django.core.exceptions import ValidationError
from django import forms

from main.reg import student
from main.models import Candidate, Position

import re

class RegForm(forms.Form):
    reg_number = forms.CharField(max_length="20")

    def clean_reg_number(self):
        reg_number = self.cleaned_data.get("reg_number", "").upper()
        regex = "MOUAU/[a-zA-Z]{3}/[0-9]{2}/[0-9]{6}"
        if not re.match(regex, reg_number):
            raise ValidationError("Enter a valid reg number of the form 'mouau/xxx/xx/xxxxxx' ")
        if reg_number not in student:
            raise ValidationError("This reg number does not belong to any student in the database")
        return reg_number


class VoteForm(forms.Form):
    candidate = forms.CharField(max_length="54")


def strToList(string):
    if string == "":
        return []

class CandidateRegistrationForm(forms.Form):
    name = forms.CharField(max_length=20)
    level = forms.ChoiceField(choices=Candidate.Levels.choices)
    position = forms.ModelChoiceField(queryset=Position.objects.all())

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Candidate.objects.filter(name=name):
            raise ValidationError("Candidate exists")
        else:
            return name

    def save(self, form):
        candidate, created = Candidate.objects.get_or_create(
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
        if Position.objects.filter(name=name):
            raise ValidationError("Position already exists")
        else:
            return name 

    def save(self, form):
        position = Position.objects.create(
            name=forms.cleaned_data.get("name"),
        )
        return position 