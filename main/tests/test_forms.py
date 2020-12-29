from django.test import TestCase, Client
from django.urls import reverse

from unittest.mock import Mock, patch

from main.models import User, Candidate, Position
from main.forms import (
    RegForm,
    validate_student,
    CandidateRegistrationForm,
    PositionRegistrationForm,
)

from faker import Faker
fake = Faker()

class TestRegForm(TestCase):
    def setUp(self):
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

    
class TestCandidateRegistrationForm(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Some Position")
        self.data = {
            'name': fake.name(), 
            'level': 500,
            'position': self.position
        }
        self.form = CandidateRegistrationForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())

    def test_error_for_a_candidate_that_exists(self):
        name = fake.name()
        Candidate.objects.create(name=name, level=200, position=self.position)
        data = {
            'name': name,
            'level': 400,
            'position': self.position
        }
        response = Client().post(reverse("register_candidate"), data=data)
        self.assertFormError(response, "form", "name", errors="Candidate exists")

    def test_valid_name(self):
        self.assertFalse(self.form.errors)

    def test_candidate_is_created(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.assertTrue(Candidate.objects.get(name=self.data.get('name')))

    def test_canidate_is_added_to_position(self):
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
        self.data = {
            'name': 'position name'
        }
        self.form = PositionRegistrationForm(data=self.data)
    
    def test_validation_error_for_postion_name_that_already_exists(self):
        Position.objects.create(name=self.data.get('name').upper())
        response = Client().post(reverse("register_position"), data=self.data)
        self.assertFormError(response, "form", "name", errors="Position exists")

    def test_valid_name(self):
        self.assertFalse(self.form.errors)

    def test_position_is_created(self):
        self.form.is_valid()
        self.form.save(self.form)
        self.assertTrue(Position.objects.get(name=self.data.get("name").upper()))
   