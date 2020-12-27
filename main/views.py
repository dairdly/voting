from django.http.response import HttpResponseRedirect
from django.views.generic import FormView, TemplateView, ListView, DeleteView, View
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from main.forms import (
    RegForm, 
    VoteForm,
    CandidateRegistrationForm,
    PositionRegistrationForm,
)
from main.models import Candidate, Position


class RegFormView(FormView):
    form_class = RegForm 
    success_url = reverse_lazy("vote")
    template_name = "main/reg_form.html"

class VoteFormView(TemplateView):
    template_name = "main/vote_form.html"

    def get_context_data(self, **kwargs):
        kwargs = super(VoteFormView, self).get_context_data(**kwargs)
        kwargs['candidates'] = Candidate.objects.all()
        kwargs['positions'] = Position.objects.all()
        return kwargs

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken')
        for position in data:
            try:
                candidate = Candidate.objects.get(name=data[position])
                candidate.votes += 1
                candidate.save()
            except Candidate.DoesNotExist:
                pass
        return HttpResponseRedirect(reverse('thanks'))


class ThanksView(TemplateView):
    template_name = "main/thanks.html"

class CandidateRegistrationView(FormView):
    form_class = CandidateRegistrationForm
    template_name = "main/candidate_form.html"
    success_url = reverse_lazy('list')

    def form_valid(self, form):
        form.save(form)
        messages.add_message(self.request, messages.SUCCESS, "Candidate has been successfully created")
        return super(CandidateRegistrationView, self).form_valid(form)


class PositionRegistrationView(FormView):
    form_class = PositionRegistrationForm 
    template_name = "main/position_form.html"
    success_url = reverse_lazy('list')

    def form_valid(self, form):
        position = Position(name = form.cleaned_data.get("name").upper())
        position.save()
        messages.add_message(self.request, messages.SUCCESS, "Position has been successfully created")
        return super(PositionRegistrationView, self).form_valid(form)


class PositionAndCandidateList(TemplateView):
    template_name = "main/list.html"

    def get_context_data(self, **kwargs):
        kwargs = super(PositionAndCandidateList, self).get_context_data(**kwargs)
        kwargs['candidates'] = Candidate.objects.all()
        kwargs['positions'] = Position.objects.all()
        return kwargs

def DeleteCandidate(request, pk):
    try:
        candidate = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        messages.add_message(request, messages.WARNING, "Candidate does not exist")
        return HttpResponseRedirect(reverse("list"))
    candidate.delete()
    messages.add_message(request, messages.ERROR, "Candidate has been deleted")
    return HttpResponseRedirect(reverse("list"))


def DeletePosition(request, pk):
    try:
        position = Position.objects.get(pk=pk)
    except Position.DoesNotExist:
        messages.add_message(request, messages.WARNING, "Position does not exist")
        return HttpResponseRedirect(reverse("list"))
    position.delete()
    messages.add_message(request, messages.ERROR, "Position has been deleted")
    return HttpResponseRedirect(reverse("list"))