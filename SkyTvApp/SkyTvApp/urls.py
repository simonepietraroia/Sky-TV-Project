
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from DevSign_Vote.views import homepage, profile, edit_profile, signup, user_login, user_logout  


urlpatterns = [
    path('admin/', admin.site.urls),  
    path('', homepage, name='home'),
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("signup/", signup, name="signup"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
