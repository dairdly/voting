from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from unittest.mock import patch, Mock

from datetime import datetime, timedelta

from main.models import User, Candidate, Position, Election
from main.forms import (
    RegForm,
    validate_student,
    CandidateRegistrationForm,
    PositionRegistrationForm,
    StartElectionForm,
    ChangeStaffCodeForm,
    ChangeAdminCodeForm,
)

from faker import Faker
fake = Faker()

class TestRegForm(TestCase):
    def setUp(self):
        start = datetime.now(timezone.utc)
        delta = timedelta(days=7)
        delta2 = timedelta(days=5)
        self.election = Election.objects.create(
            name = fake.sentence(nb_words=2),
            start = start - delta2,
            end = start + delta
        )
        username = fake.first_name()
        self.data = {
            'username': username,
            'password': username
        }
        self.form = RegForm(data=self.data)

    @patch('main.forms.requests.post')
    def test_form_is_valid(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/my-account-student.php'
        response_mock.return_value.url = response_mock_url 
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    @patch('main.forms.requests.post')
    def test_validation_error_for_invalid_username_and_password(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/login.php'
        response_mock.return_value.url = response_mock_url
        response = Client().post(reverse("reg"), data=self.data)
        self.assertFormError(response, "form", None, errors="Invalid username and password")

    @patch('main.forms.requests.post')
    def test_validate_student_returns_true(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/my-account-student.php'
        response_mock.return_value.url = response_mock_url
        self.assertTrue(validate_student(fake.user_name(), fake.password()))

    @patch('main.forms.requests.post')
    def test_validate_student_returns_false(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/login.php'
        response_mock.return_value.url = response_mock_url
        self.assertFalse(validate_student(fake.user_name(), fake.password()))

    def test_validate_student_returns_None_on_connectionError(self):
        self.assertEqual(validate_student(fake.user_name(), fake.password()), None)

    def test_Election_is_not_running_validationError(self):
        Election.objects.all().delete()
        response = Client().post(reverse("reg"), data=self.data)
        self.assertFormError(response, "form", None, errors="No Election is running")


    
class TestCandidateRegistrationForm(TestCase):
    def setUp(self):
        start = datetime.now(timezone.utc)
        delta = timedelta(days=7)
        delta2 = timedelta(days=5)
        self.election = Election.objects.create(
            name = fake.sentence(nb_words=2),
            start = start + delta2,
            end = start + delta
        )
        self.admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        self.position = Position.objects.create(name="Some Position")
        self.data = {
            'name': fake.name(), 
            'level': 500,
            'position': self.position,
            'election': self.election
        }
        self.form = CandidateRegistrationForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    def test_error_for_a_candidate_that_exists(self):
        start = datetime.now(timezone.utc)
        delta = timedelta(days=1)
        self.election = Election.objects.create(
            name = fake.sentence(nb_words=2),
            start = start,
            end = start + delta
        )
        name = fake.name()
        Candidate.objects.create(name=name, level=200, post=self.position, election=self.election)
        data = {
            'name': name,
            'level': 400,
            'position': self.position,
        }
        client = Client()
        client.force_login(user=self.admin)
        response = client.post(reverse("register_candidate"), data=data)
        self.assertFormError(response, "form", "name", errors="Candidate exists")

    def test_test_election_has_been_registered_validationError(self):
        name = fake.name()
        data = {
            'name': name,
            'level': 400,
            'position': self.position
        }
        client = Client()
        client.force_login(user=self.admin)
        Election.objects.all().delete()
        response = client.post(reverse("register_candidate"), data=data)
        self.assertFormError(response, "form", None, errors="No Election has been registered")


    def test_valid_name(self):
        self.assertFalse(self.form.errors)

    def test_candidate_is_created(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.assertTrue(Candidate.objects.get(name=self.data.get('name')))

    def test_candidate_is_added_to_position(self):
        self.form.is_valid()
        self.form.save(self.form)
        candidate = Candidate.objects.get(name=self.data.get('name'))
        self.assertIn(candidate, self.position.candidates.all())

    def test_camel_case_for_candidate(self):
        data = {
            'name': "saMuel UCHe",
            'level': 300,
            'position': self.position 
        }
        form = CandidateRegistrationForm(data=data)
        form.is_valid()
        candidate = form.save(form)
        self.assertEqual(candidate.name, "Samuel Uche")

    
class TestPositionRegistrationForm(TestCase):
    def setUp(self):
        start = datetime.now(timezone.utc)
        delta = timedelta(days=7)
        self.election = Election.objects.create(
            name = fake.sentence(nb_words=2),
            start = start + delta,
            end = start + delta + delta
        )
        self.admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        self.data = {
            'name': 'position name'
        }
        self.form = PositionRegistrationForm(data=self.data)
    
    def test_validation_error_for_postion_name_that_already_exists(self):
        Position.objects.create(name=self.data.get('name').upper())
        client = Client()
        client.force_login(user=self.admin)
        response = client.post(reverse("register_position"), data=self.data)
        self.assertFormError(response, "form", "name", errors="Position exists")

    def test_validation_error_for_no_election_registered(self):
        Position.objects.create(name=self.data.get('name').upper())
        client = Client()
        client.force_login(user=self.admin)
        Election.objects.all().delete()
        response = client.post(reverse("register_position"), data=self.data)
        self.assertFormError(response, "form", None, errors="No Election has been registered")


    def test_valid_name(self):
        self.assertFalse(self.form.errors)

    def test_position_is_created(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.assertTrue(Position.objects.get(name=self.data.get("name").upper()))
   
# mehn, I give up on this test
# class TeststartElectionForm(TestCase):
#     @patch('main.forms.datetime')
#     def setUp(self, mock_datetime):
#         start = datetime.now(timezone.utc)
#         delta = timedelta(days=7)
#         mock_datetime.now.return_value = datetime(2021, 1, 12, 3, 5, 23)
#         # mock_datetime.strptime.return_value = datetime.strptime("2021-01-01 01:04", "%Y-%m-%d %H:%M")
#         mock_datetime.datetime.strptime.side_effect = [datetime.strptime("2021-01-01 01:04", "%Y-%m-%d %H:%M"), datetime.strptime("2021-01-02 00:00", "%Y-%m-%d %H:%M"),]
#         mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
#         self.data = {
#             'name': fake.sentence(nb_words=2),
#             'duration': '2021-01-01 01:04 to 2021-01-02 00:00'
#         }
#         self.form = StartElectionForm(data=self.data)
    
#     def test_election_is_created(self):
#         self.form.is_valid()
#         self.form.save(self.form)
#         self.assertTrue(Election.objects.get(name=self.data.get('name').upper()))


class TestChangeStaffCodeForm(TestCase):
    def setUp(self):
        self.data = {
            'old_access_code': 'staff',
            'new_access_code': 'new',
            'repeat_access_code': 'new'
        }
        self.staff = User.objects.create(
            username = 'staff', 
            is_staff = True
        )
        self.staff.set_password('staff')
        self.staff.save()
        self.form = ChangeStaffCodeForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    def test_password_has_changed(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.check_password('staff'))
        self.assertTrue(self.staff.check_password('new'))

    def test_incorrect_access_code(self):
        data = {
            'old_access_code': 'old',
            'new_access_code': 'new',
            'repeat_access_code': 'new'   
        }
        self.admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        client = Client()
        client.force_login(user=self.admin)
        response = client.post(reverse("change-staff-code"), data=data)
        self.assertFormError(response, "form", "old_access_code", errors="Incorrect Access Code")


class TestChangeAdminCodeForm(TestCase):
    def setUp(self):
        self.data = {
            'old_access_code': 'admin',
            'new_access_code': 'new',
            'repeat_access_code': 'new'
        }
        self.admin = User.objects.create(
            username = 'admin', 
            is_staff = True,
            is_superuser = True
        )
        self.admin.set_password('admin')
        self.admin.save()
        self.form = ChangeAdminCodeForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    def test_password_has_changed(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.check_password('admin'))
        self.assertTrue(self.admin.check_password('new'))

    def test_incorrect_access_code(self):
        data = {
            'old_access_code': 'old',
            'new_access_code': 'new',
            'repeat_access_code': 'new'   
        }
        self.admin, created = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)
        client = Client()
        client.force_login(user=self.admin)
        response = client.post(reverse("change-admin-code"), data=data)
        self.assertFormError(response, "form", "old_access_code", errors="Incorrect Access Code")