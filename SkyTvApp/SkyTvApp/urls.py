from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from DevSign_Vote.views import (
    homepage,
    profile,
    edit_profile,
    signup,
    user_login,
    user_logout,
    vote_on_session,
    session_select,
    create_voting_session,
    join_session,
    portal_view,
    confirmation_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='home'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('create_session/', create_voting_session, name='create_session'),
    path('vote/<int:session_id>/', vote_on_session, name='voting'),
    path('sessions/', session_select, name='session-select'),
    path('sessions/<int:session_id>/', join_session, name='join_session'),
    path('portal/', portal_view, name='portal'),
    path('confirmation/<int:session_id>/', confirmation_view, name='confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
