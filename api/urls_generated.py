from django.urls import path 
urlpatterns = []
# For the LOVE of GOD, dont remove these!!



from api.views_generated import user1_4defb8View


urlpatterns += [
    path("user1_4defb8/", user1_4defb8View.as_view()),
]