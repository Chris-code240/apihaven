from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User



class SignupTests(APITestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.payload = { "username":"user", "password":"aVeryStrongPassword@user"}
    
    def test_signup_sucessful(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_paylod(self):
        invalid_payload = { "username":"user"}
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn('password', response.data)
    
    def test_common_password(self):
        invalid_payload = { "username":"newuser", "password":"password"}
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(400, response.status_code)

class TokenTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.payload = { "username":"user", "password":"aVeryStrongPassword@user"}

    def test_login_successful(self):
        reponse = self.client.post(reverse('signup'), self.payload, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(200, response.status_code)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_missing_param(self):
        reponse = self.client.post(reverse('signup'), self.payload, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.post(self.url, { "password":"aVeryStrongPassword@user"}, format='json')
        self.assertEqual(400, response.status_code)

    def test_login_non_existing_user(self):
        reponse = self.client.post(reverse('signup'), self.payload, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.post(self.url, { "username":"someuser", "password":"somepassword"}, format='json')
        self.assertEqual(401, response.status_code)
    
    def test_login_refresh(self):
        reponse = self.client.post(reverse('signup'), self.payload, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.post(reverse('refresh'), reponse.data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertIn('access', response.data)

class ProfileTest(APITestCase):
    def setUp(self):
        self.url = reverse('profile')
        self.update_payload = {"first_name":"some first name", "url":"somedb.url.net", "database":{ "username":"user","password":"somepassword"}}
        self.credentials = { "username":"user", "password":"aVeryStrongPassword@user"}
    def test_get_profile(self):
        reponse = self.client.post(reverse('signup'), self.credentials, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.get(self.url, self.credentials, headers={'Authorization':f"Bearer {reponse.data['access']}"}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, response.data['success'])
    
    def test_update_profile(self):
        reponse = self.client.post(reverse('signup'), self.credentials, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.patch(self.url, self.update_payload, headers={'Authorization':f"Bearer {reponse.data['access']}"}, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, response.data['success'])
        # print(self.update_payload,"\n", response.data)
        for key in self.update_payload:
            self.assertEqual(self.update_payload[key], reponse.data['data'][key])

    
    def test_remove_or_delete_user(self):
        reponse = self.client.post(reverse('signup'), self.credentials, format='json')
        self.assertEqual(reponse.status_code, 201)
        response = self.client.delete(self.url, headers={'Authorization':f"Bearer {reponse.data['access']}"}, format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(True, response.data['success']) 

def get_token(username, password, instance):
    res_signup = instance.client.post(reverse('signup'), {"username":username, "password":password}, format="json")
    instance.assertEqual(201, res_signup.status_code)
    res = instance.client.post(reverse('login'), {"username":username, "password":password}, format="json")
    return res.data if instance.assertIn('access', res.data) else None
class ModelTest(APITestCase):
    def setUp(self):
        self.credentials =  { "username":"user", "password":"aVeryStrongPassword@user"}
        self.payload = {
  "name": "user_model",
  "params": {
    "use_for_auth": True,
    "actions": ["getAll", "update", "delete", "create"],
    "fields": [
      {"name": "name", "type": "str"},
      {"name": "id", "type": "int", "primary_key": True}
    ]
  }
}
    
        self.url = reverse('model')
    
    def test_model_creation_successfull(self):
        res_signup = self.client.post(reverse('signup'), self.credentials, format="json")
        self.assertEqual(201, res_signup.status_code)
        res = self.client.post(reverse('login'), self.credentials, format="json")
        token = res.data
        print("Token: ", token['access'])
        self.assertEqual(True, isinstance(token, dict))
        response = self.client.post(self.url, self.payload, headers={'Authorization':f"Bearer {token['access']}"}, format='json')
        print(response.data)
    

              
        
