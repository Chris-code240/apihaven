from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', TokenBlacklistView.as_view(), name="logout"),
    path('logout', TokenBlacklistView.as_view(), name='logout'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('model/', views.ModelView.as_view(), name='model'),
    path('model', views.ModelView.as_view(), name='model'),
    path('project/', views.ProjectView.as_view(), name="project"),
    path('project', views.ProjectView.as_view(), name="project"),
    path('protected/', views.ProtectedView.as_view(), name="protected")
]