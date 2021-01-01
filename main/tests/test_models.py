from django.test import TestCase 
from django.contrib.auth import authenticate
from django.utils import timezone

from main.models import Candidate, Position, User, Election

from unittest.mock import patch

from datetime import datetime, timedelta

from faker import Faker
fake = Faker()

class TestCandidateModel(TestCase):
    def setUp(self):
        start = datetime.now(timezone.utc)
        delta = timedelta(days=1)
        self.election = Election.objects.create(
            name = fake.sentence(nb_words=2),
            start = start,
            end = start + delta
        )
        self.position = Position.objects.create(name='An election position')
        self.candidate = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            post = self.position,
            election = self.election, 
        )

    def test_candidate_can_be_created(self):
        self.assertTrue(self.candidate)

    def test_str_function(self):
        self.assertEqual(str(self.candidate), self.candidate.name)


class TestPositionModel(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="positon title")

    def test_position_is_created(self):
        self.assertTrue(self.position)

    def test_str_function(self):
        self.assertEqual(str(self.position), self.position.name)

    
class TestUserModel(TestCase):
    def setUp(self):
        self.student = User.objects.create(username=fake.user_name())

    def test_student_created(self):
        self.assertTrue(self.student)
    
    def test_str_function(self):
        self.assertEqual(str(self.student), self.student.username)


class TestCreateUserModel(TestCase):
    def setUp(self):
        self.username = fake.user_name()
        self.password = fake.password()
        self.user = User.objects.create_user(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
    
    def test_user_is_created(self):
        self.assertTrue(self.user)

    def test_user_can_be_authenticated(self):
        auth_user = authenticate(username = self.username, password = self.password)
        self.assertEqual(auth_user, self.user)

    def test_no_username_valueError(self):
        with self.assertRaises(ValueError, msg='You must provide a username'):
            user = User.objects.create_user(username="")

    def test_default_is_superuser_is_false(self):
        self.assertFalse(self.user.is_superuser)
    
    def test_default_is_staff_is_false(self):
        self.assertFalse(self.user.is_staff)
    
    def test_default_is_active_is_True(self):
        self.assertTrue(self.user.is_active)

    def test_default_hasVoted_is_false(self):
        self.assertFalse(self.user.hasVoted)


class TestCreateSuperuserModel(TestCase):
    def setUp(self):
        self.username = fake.user_name()
        self.password = fake.password()
        self.superuser = User.objects.create_superuser(username=self.username, password=self.password)
    
    def test_default_is_staff_is_true(self):
        self.assertTrue(self.superuser.is_staff)

    def test_default_is_superuser_is_true(self):
        self.assertTrue(self.superuser.is_superuser)

    def test_default_is_active_is_true(self):
        self.assertTrue(self.superuser.is_active)

    def test_default_hasVoted_is_false(self):
        self.assertFalse(self.superuser.hasVoted)

    def test_valueError_for_is_staff_false(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_staff=True"):
            self.superuser = User.objects.create_superuser(username=fake.user_name(), password=fake.password(), is_staff=False)

    def test_valueError_for_is_superuser_false(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_superuser=True"):
            self.superuser = User.objects.create_superuser(username=fake.user_name(), password=fake.password(), is_superuser=False)


class TestElectionModel(TestCase):
    @patch('main.models.datetime')
    def setUp(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2021, 1, 12, 3, 5, 23)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        self.election = Election.objects.create(
            name=fake.sentence(nb_words=2),
            start = datetime(2020, 11, 29, 5, 45, 34),
            end = datetime(2020, 12, 29, 5, 45, 34),
        )

    def test_str_function(self):
        self.assertEqual(str(self.election), self.election.name)

    def test_started_is_set_to_true(self):
        self.assertTrue(self.election.started)

    def test_ended_is_set_to_true(self):
        self.assertTrue(self.election.ended)