from django.urls import path
import views

# Simplified URL patterns: avoid duplicate empty ('') routes and include() for a
# non-existent 'lockers' module. Map the views to the templates that exist in
# the repository (index.html, selectLocker.html).
urlpatterns = [
    path('', views.home, name='home'),
    path('select/', views.select_locker, name='select_locker'),
    path('private/', views.private_auth, name='private_auth'),
    path('rfid/', views.rfid_login, name='rfid_login'),
    path('open/', views.open_locker, name='open_locker'),
    path('pin/', views.pin_entry, name='pin_entry'),
    path('fingerprint/', views.fingerprint_login, name='fingerprint_login'),
]
