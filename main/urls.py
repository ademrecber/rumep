from django.urls import path
from django.views.generic import TemplateView
from .views import views
from .tester_views import tester_signup

urlpatterns = [
    path('rumep-spor/test-katilim/', tester_signup, name='rumep_spor_testers'),
    path('rumep-spor/terms-of-use/', TemplateView.as_view(template_name='rumep-spor/terms.html'), name='rumep_spor_terms'),
    path('rumep-spor/data-deletion/', TemplateView.as_view(template_name='rumep-spor/data.html'), name='rumep_spor_data'),
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
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('statistics/', views.statistics, name='statistics'),

]
