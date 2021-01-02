from django.core.exceptions import ValidationError
from django import forms

from main.models import Candidate, Position, Election, User

from datetime import datetime

from pytz import timezone

import requests

afri = timezone('Africa/Lagos')

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
        election = Election.objects.filter(started=True).filter(ended=False).last()
        if election: 
            cleaned_data = super().clean()
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            if validate_student(username, password):
                return cleaned_data
            else:
                raise ValidationError('Invalid username and password')
        else:
            raise ValidationError('No Election is running')


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

    def clean(self):
        cleaned_data = super().clean()
        election = Election.objects.filter(started=False).filter(ended=False).last()
        if election == None:
            raise ValidationError('No Election has been registered')
        else:
            return cleaned_data

    def save(self, form):
        candidate, created = Candidate.objects.get_or_create(
            name = form.cleaned_data.get("name"),
            level = form.cleaned_data.get("level"),
            post = form.cleaned_data.get("position"),
            election = Election.objects.all().last()
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

    def clean(self):
        election = Election.objects.filter(started=False).filter(ended=False).last()
        if election:
            return super().clean()
        else:
            raise ValidationError('No Election has been registered')

    def save(self, form):
        position = Position.objects.get_or_create(
            name = form.cleaned_data.get("name"),
            election = Election.objects.all().last()
        )
        return position 

    
class AccessCodeForm(forms.Form):
    access_code = forms.CharField(widget=forms.widgets.PasswordInput())


class StartElectionForm(forms.ModelForm):
    duration = forms.CharField()
    class Meta:
        model = Election
        fields = ('name',)

    def clean_name(self):
        name = self.cleaned_data.get('name').upper()
        return name

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if not len(duration.split()) == 5:
            raise ValidationError("Select two dates for start and end")
        return duration

    def save(self, form):
        duration = self.cleaned_data.get('duration')
        start = " ".join(duration.split()[:2])
        end = " ".join(duration.split()[3:])
        start = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M")
        election = Election.objects.create(
            name = form.cleaned_data.get("name"),
            start = afri.localize(start), 
            end = afri.localize(end)
        )
        return election


class ChangeStaffCodeForm(forms.Form):
    old_access_code = forms.CharField()
    new_access_code = forms.CharField()
    
    def clean_old_access_code(self):
        old_access_code = self.cleaned_data.get('old_access_code')
        staff = User.objects.get(username='staff')
        if staff.check_password(old_access_code):
            return old_access_code
        else:
            raise ValidationError("Incorrect Access Code")
    
    def save(self, form):
        new_access_code = self.cleaned_data.get('new_access_code')
        staff = User.objects.get(username='staff')
        staff.set_password(new_access_code)
        staff.save()
        return staff
        

class ChangeAdminCodeForm(forms.Form):
    old_access_code = forms.CharField()
    new_access_code = forms.CharField()
    
    def clean_old_access_code(self):
        old_access_code = self.cleaned_data.get('old_access_code')
        admin = User.objects.get(username='admin')
        if admin.check_password(old_access_code):
            return old_access_code
        else:
            raise ValidationError("Incorrect Access Code")
    
    def save(self, form):
        new_access_code = self.cleaned_data.get('new_access_code')
        admin = User.objects.get(username='admin')
        admin.set_password(new_access_code)
        admin.save()
        return admin
    