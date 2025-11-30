from django.urls import path
from .views import views

urlpatterns = [
    path('', views.font_list, name='home'),
    path('download/<str:font_name>/', views.download_font, name='download_font'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('usage-guide/', views.usage_guide, name='usage_guide'),
]
