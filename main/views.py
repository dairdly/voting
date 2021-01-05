from django.http.response import HttpResponseRedirect
from django.views.generic import FormView, TemplateView, View, ListView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from main.forms import (
    RegForm, 
    CandidateRegistrationForm,
    PositionRegistrationForm,
    AccessCodeForm,
    StartElectionForm,
    ChangeStaffCodeForm,
    ChangeAdminCodeForm,
)
from main.models import Candidate, Position, User, Election, refresh_election_status
from main.mixins import UserRequiredMixin, StaffRequiredMixin, AdminRequiredMixin

class HomeView(TemplateView):
    template_name = "main/home.html"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class RegFormView(FormView):
    form_class = RegForm 
    success_url = reverse_lazy("vote")
    template_name = "main/reg_form.html"

    def get(self, request, *args, **kwargs):
        refresh_election_status()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        auth_user = authenticate(username=username, password=password)
        login(self.request, auth_user)
        if auth_user.hasVoted:
            return HttpResponseRedirect(reverse('thanks'))
        return super(RegFormView, self).form_valid(form)


class VotersListView(TemplateView):
    template_name = 'main/vlist.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['candidates'] = Candidate.objects.all()
        kwargs['positions'] = Position.objects.all()
        return kwargs


class VoteFormView(UserRequiredMixin, TemplateView):
    template_name = "main/vote_form.html"

    def get_context_data(self, **kwargs):
        kwargs = super(VoteFormView, self).get_context_data(**kwargs)
        kwargs['candidates'] = Candidate.objects.all()
        kwargs['positions'] = Position.objects.all()
        return kwargs

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        for position in data:
            try:
                candidate = Candidate.objects.get(name=data[position])
                candidate.votes += 1
                candidate.save()
            except Candidate.DoesNotExist:
                pass
        user = self.request.user
        user.hasVoted = True
        user.save()
        logout(self.request)
        return HttpResponseRedirect(reverse('thanks'))


class ThanksView(TemplateView):
    template_name = "main/thanks.html"

class CandidateRegistrationView(StaffRequiredMixin, FormView):
    form_class = CandidateRegistrationForm
    template_name = "main/candidate_form.html"
    success_url = reverse_lazy('list')

    def form_valid(self, form):
        form.save(form)
        messages.add_message(self.request, messages.SUCCESS, "Candidate has been successfully created")
        return super(CandidateRegistrationView, self).form_valid(form)


class PositionRegistrationView(StaffRequiredMixin, FormView):
    form_class = PositionRegistrationForm 
    template_name = "main/position_form.html"
    success_url = reverse_lazy('list')

    def form_valid(self, form):
        form.save(form)
        messages.add_message(self.request, messages.SUCCESS, "Position has been successfully created")
        return super(PositionRegistrationView, self).form_valid(form)


class PositionAndCandidateList(StaffRequiredMixin, TemplateView):
    template_name = "main/list.html"

    def get_context_data(self, **kwargs):
        kwargs = super(PositionAndCandidateList, self).get_context_data(**kwargs)
        kwargs['candidates'] = Candidate.objects.all()
        kwargs['positions'] = Position.objects.all()
        return kwargs

class DeleteCandidate(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            candidate = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            messages.add_message(request, messages.WARNING, "Candidate does not exist")
            return HttpResponseRedirect(reverse("list"))
        candidate.delete()
        messages.add_message(request, messages.ERROR, "Candidate has been deleted")
        return HttpResponseRedirect(reverse("list"))


class DeletePosition(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            position = Position.objects.get(pk=pk)
        except Position.DoesNotExist:
            messages.add_message(request, messages.WARNING, "Position does not exist")
            return HttpResponseRedirect(reverse("list"))
        position.delete()
        messages.add_message(request, messages.ERROR, "Position has been deleted")
        return HttpResponseRedirect(reverse("list"))


class AccessCodeView(FormView):
    form_class = AccessCodeForm
    template_name = "main/access_code.html"

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        access_code = form.cleaned_data.get('access_code')
        staff = authenticate(username='staff', password=access_code)
        admin = authenticate(username='admin', password=access_code)
        if staff:
            login(self.request, staff)
        elif admin:
            login(self.request, admin)
        else:
            messages.add_message(self.request, messages.ERROR, "Access denied")
            return HttpResponseRedirect(reverse('access_code'))
        next_url = self.request.GET.get('next')
        if next_url and next_url != reverse('reg'):
            return HttpResponseRedirect(next_url)
        else:
            if staff:
                return HttpResponseRedirect(reverse('list'))
            if admin:
                return HttpResponseRedirect(reverse('manage'))


class LogoutView(TemplateView):
    template_name = 'main/index.html'

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.WARNING, "You are logged out")
        return HttpResponseRedirect(reverse('home'))
  

class ManageElectionView(AdminRequiredMixin, FormView):
    form_class = StartElectionForm
    model = Election
    template_name = 'main/manage.html'

    def form_valid(self, form):
        form.save(form)
        return HttpResponseRedirect(reverse('manage'))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['election'] = Election.objects.last()
        return kwargs

    
class CancelElectionView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        User.objects.exclude(username="staff").exclude(username="admin").delete()
        Election.objects.all().delete()
        messages.add_message(request, messages.SUCCESS, "Election has been deleted parmanently")
        return HttpResponseRedirect(reverse('manage'))

    
class ResultView(AdminRequiredMixin, ListView):
    template_name = 'main/result.html'
    model = Position
    context_object_name = 'positions'
    paginate_by = 1
    

class ChangeAccessCodeView(AdminRequiredMixin, TemplateView):
    template_name = 'main/change_codes.html'


class ChangeStaffCodeView(AdminRequiredMixin, FormView):
    form_class = ChangeStaffCodeForm
    template_name = 'main/change_codes.html'
    success_url = reverse_lazy('change-codes')

    def form_valid(self, form):
        form.save(form)
        messages.add_message(self.request, messages.SUCCESS, "Staff Access Code has been changed")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(sForm=form))


class ChangeAdminCodeView(AdminRequiredMixin, FormView):
    form_class = ChangeAdminCodeForm
    template_name = 'main/change_codes.html'
    success_url = reverse_lazy('change-codes')

    def form_valid(self, form):
        form.save(form)
        messages.add_message(self.request, messages.SUCCESS, "Admin Access Code has been changed")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(aForm=form))