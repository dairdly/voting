from django.shortcuts import redirect, reverse 
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from main.models import User


class UserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('reg'))
        else: 
            return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        staff, created = User.objects.get_or_create(username='staff', is_staff=True)
        if created:
            staff.set_password('staff')
            staff.save()
        admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        if created:
            admin.set_password('admin')
            admin.save()
        
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)            
        else:
            messages.add_message(self.request, messages.ERROR, "Access denied")
            return HttpResponseRedirect(reverse('access_code') + '?next=' + request.path)


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        if created:
            admin.set_password('admin')
            admin.save()
        
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.add_message(self.request, messages.ERROR, "Access denied")
            return HttpResponseRedirect(reverse('access_code') + '?next=' + request.path)