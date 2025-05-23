from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import requests

from .models import Profile
from .forms import ProfileCountForm
from .services import fetch_users, save_users_to_db

class ProfileModelTests(TestCase):
    def test_profile_creation(self):
        profile = Profile.objects.create(
            gender="male",
            first_name="John",
            last_name="Doe",
            phone="123-456-7890",
            email="john.doe@example.com",
            location="USA, New York",
            photo="http://example.com/photo.jpg"
        )
        self.assertEqual(str(profile), "John Doe")

class ProfileCountFormTests(TestCase):
    def test_valid_form(self):
        form = ProfileCountForm(data={'count': 10})
        self.assertTrue(form.is_valid())

    def test_invalid_forms(self):
        invalid_data = [
            {'count': 0},
            {'count': 5001},
            {'count': 'abc'},
            {}
        ]
        for data in invalid_data:
            form = ProfileCountForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('count', form.errors)


class UserServicesTests(TestCase):
    @patch('users.services.requests.get')
    def test_fetch_users_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [{'name': {'first': 'Jane', 'last': 'Doe'}, 'gender': 'female'}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        users = fetch_users(count=1)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['name']['first'], 'Jane')

    @patch('users.services.requests.get')
    def test_fetch_users_handles_errors(self, mock_get):
        # Test API error
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        users = fetch_users(count=1)
        self.assertEqual(len(users), 0)

        # Test JSON decode error
        mock_get.side_effect = None
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        users = fetch_users(count=1)
        self.assertEqual(len(users), 0)

    def test_save_users_to_db(self):
        users_data = [
            {'gender': 'male', 'name': {'first': 'Test', 'last': 'User1'}, 
             'phone': '111', 'email': 'test1@example.com', 
             'location': {'country': 'US', 'city': 'LA'}, 'picture': {'large': 'pic1.jpg'}},
        ]
        saved_count = save_users_to_db(users_data)
        
        self.assertEqual(saved_count, 1)
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.get(email='test1@example.com')
        self.assertEqual(profile.location, 'US, LA')

    def test_save_users_handles_malformed_data(self):
        users_data = [
            {'gender': 'male', 'name': {'first': 'Good', 'last': 'User'}, 'phone': '111', 'email': 'good@example.com', 'location': {'country': 'US', 'city': 'LA'}, 'picture': {'large': 'pic1.jpg'}},
            {'gender': 'female', 'name': {}, 'phone': '222', 'email': 'bad@example.com'},  # Missing required fields
        ]
        saved_count = save_users_to_db(users_data)
        
        self.assertEqual(saved_count, 1)
        self.assertTrue(Profile.objects.filter(email='good@example.com').exists())
        self.assertFalse(Profile.objects.filter(email='bad@example.com').exists())

class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = Profile.objects.create(
            gender="male",
            first_name="John",
            last_name="Doe", 
            phone="123",
            email="john@example.com",
            location="US, NY",
            photo="john.jpg"
        )

    def test_profile_list_view(self):
        response = self.client.get(reverse('users:profile_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.first_name)

    @patch('users.views.fetch_users')
    @patch('users.views.save_users_to_db')
    def test_profile_list_post_valid(self, mock_save_users, mock_fetch_users):
        mock_fetch_users.return_value = [{'name': 'test'}]
        mock_save_users.return_value = 1

        response = self.client.post(
            reverse('users:profile_list'), {'count': 5}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        mock_fetch_users.assert_called_once_with(5)

    def test_profile_list_post_invalid(self):
        response = self.client.post(
            reverse('users:profile_list'), {'count': 0}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_profile_detail_view(self):
        response = self.client.get(reverse('users:profile_detail', kwargs={'profile_id': self.profile.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.first_name)

    def test_profile_detail_not_found(self):
        response = self.client.get(reverse('users:profile_detail', kwargs={'profile_id': 999}))
        self.assertEqual(response.status_code, 404)

    @patch('users.views.fetch_users')
    @patch('users.views.save_users_to_db')
    def test_random_profile_view(self, mock_save_users, mock_fetch_users):
        Profile.objects.all().delete()
        
        mock_fetch_users.return_value = [{'test': 'data'}]
        mock_save_users.return_value = 1
        
        with patch.object(Profile.objects, 'order_by') as mock_order_by:
            mock_profile = MagicMock()
            mock_profile.email = 'random@example.com'
            mock_order_by.return_value.first.return_value = mock_profile
            
            response = self.client.get(reverse('users:random_profile'))
            self.assertEqual(response.status_code, 200)
            mock_fetch_users.assert_called_once_with(1)
