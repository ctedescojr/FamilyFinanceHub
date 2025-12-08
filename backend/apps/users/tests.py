from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class UserApiTests(APITestCase):
    def setUp(self):
        # Create a regular user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'family_role': 'FATHER'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # Create another user to test permissions
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123',
            family_role='MOTHER'
        )
        
        # URL for user list
        self.list_url = reverse('users:user-list')
        # URL for user detail (using the ID of the first user)
        self.detail_url = reverse('users:user-detail', kwargs={'pk': self.user.id})

    def test_get_user_profile_authenticated(self):
        """
        Ensure authenticated user can see their own profile with correct fields.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['family_role'], self.user_data['family_role'])
        # Check if custom fields from serializer are present
        self.assertIn('job', response.data)
        self.assertIn('cellphone', response.data)

    def test_user_cannot_see_others_profile(self):
        """
        Ensure regular user cannot see other users' profiles (list view filtration).
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only contain 1 user (themselves), not 'other_user'
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], self.user_data['email'])

    def test_get_user_profile_unauthenticated(self):
        """
        Ensure unauthenticated user cannot access the API.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)