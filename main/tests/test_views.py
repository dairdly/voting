from django.contrib.messages.api import get_messages
from main.forms import CandidateRegistrationForm
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from unittest.mock import patch

from main.models import Candidate, Position, User 
from main.views import (
    CandidateRegistrationView, 
    PositionRegistrationView
)

from faker import Faker
fake = Faker()

class TestRegFormView(TestCase):
    @patch('main.forms.requests.post')
    def setUp(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/my-account-student.php'
        response_mock.return_value.url = response_mock_url 
        self.data = {
            'username': 'SKH3833',
            'password': 'SKH3833'
        }
        self.response = Client().post(reverse('reg'), data=self.data)

    def test_user_has_been_logged_in(self):
        user = User.objects.get(username=self.data.get("username"))
        self.assertEqual(self.response.wsgi_request.user, user)

    def test_redirect_to_vote_for_new_users(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('vote'))

    @patch('main.forms.requests.post')
    def test_redirect_to_vote_for_users_that_have_voted_before(self, response_mock):
        response_mock_url = 'https://mouauportal.edu.ng/my-account-student.php'
        response_mock.return_value.url = response_mock_url 
        user = User.objects.get(username=self.data.get('username'))
        user.hasVoted = True
        user.save()
        response = Client().post(reverse('reg'), data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('thanks'))

    
class TestVoteFormviewGetContextData(TestCase):
    def setUp(self):
        self.position1 = Position.objects.create(name=fake.text())
        self.position2 = Position.objects.create(name=fake.text())
        self.position3 = Position.objects.create(name=fake.text())
        self.candidate1 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1
        )
        self.candidate2 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1
        )
        self.candidate3 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2
        )
        self.candidate4 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2
        )
        self.candidate5 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3
        )
        self.candidate6 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3
        )
        self.user = User.objects.create(username=fake.user_name())
        self.client = Client()
        self.client.force_login(user=self.user)
        self.response = self.client.get(reverse('vote'))

    def test_candidates_is_in_get_context_data(self):
        self.assertEqual(len(self.response.context.get("candidates")), len(Candidate.objects.all()))

    def test_positions_is_in_get_context_data(self):
        self.assertEqual(len(self.response.context.get("positions")), len(Position.objects.all()))


class TestVoteFormViewPost(TestCase):
    def setUp(self):
        self.position1 = Position.objects.create(name=fake.text())
        self.position2 = Position.objects.create(name=fake.text())
        self.position3 = Position.objects.create(name=fake.text())
        self.candidate1 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.candidate2 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.candidate3 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2, 
            votes = fake.random_int()
        )
        self.candidate4 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2, 
            votes = fake.random_int()
        )
        self.candidate5 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3, 
            votes = fake.random_int()
        )
        self.candidate6 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3, 
            votes = fake.random_int()
        )
        self.data = {
            self.position1.name: self.candidate2.name,
            self.position3.name: self.candidate4,
            'some_data': 'some_value'
        }
        self.user = User.objects.create(username=fake.user_name())
        self.user.set_password(fake.password())
        self.user.save()
        self.client = Client()
        self.client.force_login(user=self.user)
        self.response = self.client.post(reverse('vote'), data=self.data)
        

    def test_user_has_voted(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.hasVoted)

    def test_non_authenticated_users_redirect_to_reg_form(self):
        response = Client().post(reverse('vote'), data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('reg'))

    def test_candidate_vote_has_been_added(self):
        votes2 = self.candidate2.votes
        votes4 = self.candidate4.votes
        self.candidate2.refresh_from_db()
        self.candidate4.refresh_from_db()
        self.assertEqual(self.candidate2.votes, votes2+1)
        self.assertEqual(self.candidate4.votes, votes4+1)

    def test_candidates_not_voted_for_has_no_vote_increase(self):
        votes1 = self.candidate1.votes
        votes3 = self.candidate3.votes
        votes5 = self.candidate5.votes
        votes6 = self.candidate6.votes
        self.candidate1.refresh_from_db()
        self.candidate3.refresh_from_db()
        self.candidate5.refresh_from_db()
        self.candidate6.refresh_from_db()
        self.assertEqual(self.candidate1.votes, votes1)
        self.assertEqual(self.candidate3.votes, votes3)
        self.assertEqual(self.candidate5.votes, votes5)
        self.assertEqual(self.candidate6.votes, votes6)

    def test_non_candidate_data_in_request_post_is_ignored_and_redirects_correctly(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse("thanks"))

    
class TestCandidateRegistrationView(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="A position title")
        self.data = {
            'name': fake.name(),
            'level': fake.random_element(elements=[100, 200, 300, 400, 500]),
            'position': self.position.id
        }
        self.response = Client().post(reverse('register_candidate'), data=self.data)
    
    def test_candidate_has_been_registered(self):
        self.assertTrue(Candidate.objects.get(name=self.data.get('name')))

    def test_successful_redirect(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('list'))

    def test_success_message(self):
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Candidate has been successfully created")

    
class TestPositionRegistrationView(TestCase):
    def setUp(self):
        self.data = {'name': 'position title'}
        self.response = Client().post(reverse('register_position'), data=self.data)

    def test_position_is_created(self):
        self.assertTrue(Position.objects.get(name=self.data.get('name').upper()))

    def test_success_message(self):
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Position has been successfully created")

    def test_redirect_to_success_url(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('list'))


class TestPositionAndCandidateList(TestCase):
    def setUp(self):
        self.position1 = Position.objects.create(name=fake.text())
        self.position2 = Position.objects.create(name=fake.text())
        self.position3 = Position.objects.create(name=fake.text())
        self.candidate1 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.candidate2 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.candidate3 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2, 
            votes = fake.random_int()
        )
        self.candidate4 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position2, 
            votes = fake.random_int()
        )
        self.candidate5 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3, 
            votes = fake.random_int()
        )
        self.candidate6 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position3, 
            votes = fake.random_int()
        )
        self.response = Client().get(reverse('list'))

    def test_candidates_in_getContextData(self):
        self.assertEqual(len(self.response.context.get('candidates')), len(Candidate.objects.all()))

    def test_positions_in_getContextData(self):
        self.assertEqual(len(self.response.context.get('positions')), len(Position.objects.all()))

    
class TestDeleteCandidate(TestCase):
    def setUp(self):
        self.position1 = Position.objects.create(name=fake.text())
        self.candidate1 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.response = Client().get(f"/candidate/{self.candidate1.pk}/delete/")

    def test_candidate_does_not_exist_message(self):
        response = Client().get("/candidate/30/delete/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].message, "Candidate does not exist")

    def test_candidate_does_not_exist_redirect(self):
        response = Client().get("/candidate/3/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('list'))

    def test_candidate_is_deleted(self):
        with self.assertRaises(Candidate.DoesNotExist):
            self.candidate1.refresh_from_db()
    
    def test_message_after_deletion(self):
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(messages[0].message, "Candidate has been deleted")

    def test_redirect_after_deletion(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('list'))


class TestDeletePositionView(TestCase):
    def setUp(self):
        self.position1 = Position.objects.create(name=fake.text())
        self.candidate1 = Candidate.objects.create(
            name = fake.name(),
            level = fake.random_element(elements=(100, 200, 300, 400, 500)),
            position = self.position1, 
            votes = fake.random_int()
        )
        self.response = Client().get(f"/position/{self.position1.pk}/delete/")

    def test_message_if_position_does_not_exist(self):
        response = Client().get("/position/50/delete/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Position does not exist")
    
    def test_redirect_if_position_does_not_exist(self):
        response = Client().get("/position/4/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('list'))

    def test_position_is_deleted(self):
        with self.assertRaises(Position.DoesNotExist):
            self.position1.refresh_from_db()
        
    def test_message_after_deletion(self):
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Position has been deleted")
    
    def test_redirect_after_deletion(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('list'))