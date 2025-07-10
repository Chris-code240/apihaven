from .urls_generated import path
from .urls_generated import urlpatterns as generated_urls
from main.api_auth import APITokenObtainPairView, APITokenRefreshView, APISignUpView
urlpatterns = [
    *generated_urls,
    path("login/",APITokenObtainPairView.APITokenObtainPairView.as_view(), name="login"),
    path("token/",APITokenObtainPairView.APITokenObtainPairView.as_view(), name="token"),
    path("signup/", APISignUpView.APISignUpView.as_view(), name="signup")
]
