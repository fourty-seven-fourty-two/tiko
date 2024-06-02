from django.urls import path

from rest_framework_simplejwt import views as jwt_views

from profiles import views as profile_views


urlpatterns = [
    path("signup/", profile_views.CreateUserView.as_view(), name="signup"),
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
