from django.test import TestCase, Client, override_settings
from django.views.generic.base import View
from django.urls import reverse, path

from main.models import User 
from main.mixins import UserRequiredMixin, StaffRequiredMixin, AdminRequiredMixin
from main.views import RegFormView, AccessCodeView

from faker import Faker
fake = Faker()

class UserRequiredView(UserRequiredMixin, View):
    pass

class StaffRequiredView(StaffRequiredMixin, View):
    pass

class AdminRequiredView(AdminRequiredMixin, View):
    pass

urlpatterns = [
    path('user/', UserRequiredView.as_view(), name='user'),
    path('staff/', StaffRequiredView.as_view(), name='staff'),
    path('admin/', AdminRequiredView.as_view(), name='admin'),
    path('', RegFormView.as_view(), name="reg"),
    path('auth/', AccessCodeView.as_view(), name="access_code"),
]

@override_settings(ROOT_URLCONF=__name__)
class TestUserRequiredMixin(TestCase):
    def setUp(self):
        pass

    def test_unauthorized_user_redirected_to_reg(self):
        response = Client().get(reverse('user'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('reg'))
    
    def test_authenticated_user_can_access_view(self):
        client = Client()
        user = User.objects.create(username=fake.user_name())
        user.set_password(fake.password())
        user.save()
        client.force_login(user=user)
        response = client.get(reverse('user'))
        self.assertEqual(response.status_code, 405)


@override_settings(ROOT_URLCONF=__name__)
class TestStaffRequiredMixin(TestCase):
    def setUp(self):
        pass
        
    def test_staff_is_avaliable(self):
        Client().get(reverse('staff'))
        self.assertTrue(User.objects.get(username='staff'))

    def test_staff_default_password_is_avaliable(self):
        Client().get(reverse('staff'))
        self.assertTrue(User.objects.get(username='staff').check_password('staff'))

    def test_admin_is_avaliable(self):
        Client().get(reverse('staff'))
        self.assertTrue(User.objects.get(username='admin'))

    def test_admin_default_password_is_avaliable(self):
        Client().get(reverse('staff'))
        self.assertTrue(User.objects.get(username='admin').check_password('admin'))

    def test_access_for_users_with_is_staff_true(self):
        client = Client()
        client.get(reverse('staff'))
        staff = User.objects.get(username='staff')
        client.force_login(user=staff)
        response = client.get(reverse('staff'))
        self.assertEqual(response.status_code, 405)

    def test_not_accessable_for_users_with_is_staff_false(self):
        client = Client()
        client.force_login(user=User.objects.create(username=fake.user_name()))
        response = client.get(reverse('staff'))
        self.assertEqual(response.status_code, 302)

    def test_next_is_contained_in_redirect_url(self):
        client = Client()
        client.force_login(user=User.objects.create(username=fake.user_name()))
        response = client.get(reverse('staff'))
        self.assertEqual(response.url, '/auth/?next=/staff/')

@override_settings(ROOT_URLCONF=__name__)
class TestAdminRequiredMixin(TestCase):
    def setUp(self):
        pass

    def test_admin_is_avaliable(self):
        Client().get(reverse('admin'))
        self.assertTrue(User.objects.get(username='admin'))

    def test_admin_has_default_password(self):
        Client().get(reverse('admin'))
        self.assertTrue(User.objects.get(username='admin').check_password('admin'))
    
    def test_access_for_users_with_is_superuser_true(self):
        client = Client()
        client.get(reverse('admin'))
        client.force_login(user=User.objects.get(username='admin'))
        response = client.get(reverse('admin'))
        self.assertEqual(response.status_code, 405)

    def test_no_access_for_not_is_superuser_true_users(self):
        client = Client()
        client.get(reverse('staff'))
        client.force_login(user=User.objects.get(username='staff'))
        response = client.get(reverse('admin'))
        self.assertEqual(response.status_code, 302)

    def test_next_in_redirect_url_for_unauthorized_users(self):
        client = Client()
        client.get(reverse('staff'))
        client.force_login(user=User.objects.get(username='staff'))
        response = client.get(reverse('admin'))
        self.assertEqual(response.url, '/auth/?next=/admin/')