from django.urls import path
from .views import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('fonts/', views.font_list, name='font_list'), # Eski ana sayfa artık /fonts/ altında
    path('rumep-spor/', views.rumep_spor, name='rumep_spor'), # Rumep Spor Sayfası
    path('rumep-spor/privacy-policy/', views.rumep_spor_privacy, name='rumep_spor_privacy'), # Rumep Spor Gizlilik Politikası
    path('download/<str:font_name>/', views.download_font, name='download_font'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('usage-guide/', views.usage_guide, name='usage_guide'),
]
