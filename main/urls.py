from django.urls import path
from .views import views
from .views import popular_views, profile_views
from .views import account_views
from .views import topic_views
from .views import category_views
from .views import follow_views
from .views import hashtag_views
from .views import bookmark_views
from .views import search_views
# from .views import ai_views  # Geçici olarak kapatıldı
from .views import yer_adlari_views
from .views import api_views
from .views import font_views
from .views import settings_views


handler404 = 'main.views.custom_404'
urlpatterns = [

    path('', topic_views.home, name='home'),
    path('create-topic/', topic_views.create_topic, name='create_topic'),
    path('topic/<slug:slug>/', topic_views.topic_detail, name='topic_detail'),
    path('topic/<slug:slug>/add-entry/', topic_views.add_entry, name='add_entry'),
    path('topic/<slug:slug>/vote/', topic_views.vote_topic, name='vote_topic'),
    path('entry/<int:entry_id>/like/', topic_views.like_entry, name='like_entry'),
    path('entry/<int:entry_id>/vote/', topic_views.vote_entry, name='vote_entry'),
    path('topic/<slug:slug>/edit/', topic_views.edit_topic, name='edit_topic'),
    path('topic/<slug:slug>/delete/', topic_views.delete_topic, name='delete_topic'),
    path('entry/<int:entry_id>/edit/', topic_views.edit_entry, name='edit_entry'),
    path('entry/<int:entry_id>/delete/', topic_views.delete_entry, name='delete_entry'),
    path('load-more-topics/', topic_views.load_more_topics, name='load_more_topics'),
    path('login/', views.login_page, name='login_page'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),

    path('search/', search_views.advanced_search, name='search'),
    path('search/suggestions/', search_views.search_suggestions, name='search_suggestions'),
    path('search/quick/', search_views.quick_search, name='quick_search'),
    path('global-search/', search_views.global_search, name='global_search'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-social-links/', profile_views.update_social_links, name='update_social_links'),
    path('update-visibility/', profile_views.update_visibility, name='update_visibility'),

    path('popular/', popular_views.popular, name='popular'),
    path('popular/<str:period>/', popular_views.popular, name='popular_period'),
    path('load-more-popular/', popular_views.load_more_popular, name='load_more_popular'),
    path('load-more-agenda/', popular_views.load_more_agenda, name='load_more_agenda'),
    path('gundem/', popular_views.agenda, name='agenda'),



    path('profile/<str:username>/', profile_views.profile, name='profile_detail'),

    path('emojis/', topic_views.get_emojis, name='get_emojis'),

    # Sozluk URL’leri
    path('sozluk/harf/<str:harf>/', views.sozluk_harf, name='sozluk_harf'),
    path('sozluk/harf-yukle/', views.sozluk_harf_yukle, name='sozluk_harf_yukle'),
    path('sozluk/kelime/<int:kelime_id>/', views.sozluk_kelime, name='sozluk_kelime'),
    path('sozluk/kelime-sil/<int:kelime_id>/', views.sozluk_kelime_sil, name='sozluk_kelime_sil'),
    path('sozluk/', views.sozluk_ana_sayfa, name='sozluk_ana_sayfa'),  
    path('sozluk/kelime-duzenle/<int:kelime_id>/', views.sozluk_kelime_duzenle, name='sozluk_kelime_duzenle'),
    path('sozluk/kelime-veri/<int:kelime_id>/', views.sozluk_kelime_veri, name='sozluk_kelime_veri'),
    path('sozluk/detay-ekle/<int:kelime_id>/', views.sozluk_detay_ekle, name='sozluk_detay_ekle'),
    path('sozluk/detay-sil/<int:detay_id>/', views.sozluk_detay_sil, name='sozluk_detay_sil'),
    path('sozluk/detay-duzenle/<int:detay_id>/', views.sozluk_detay_duzenle, name='sozluk_detay_duzenle'),
    path('sozluk/detay-veri/<int:detay_id>/', views.sozluk_detay_veri, name='sozluk_detay_veri'),
    path('sozluk/ara/', views.sozluk_ara, name='sozluk_ara'),
    path('sozluk/tum-kelimeler/', views.sozluk_tum_kelimeler, name='sozluk_tum_kelimeler'),




    path('kisi/ekle/',views.kisi_ekle, name='kisi_ekle'),
    path('kisi/liste/',views.kisi_liste, name='kisi_liste'),
    path('kisi/liste-yukle/', views.kisi_liste_yukle, name='kisi_liste_yukle'),
    path('kisi/detay/<int:kisi_id>/', views.kisi_detay, name='kisi_detay'),
    path('kisi/sil/<int:kisi_id>/', views.kisi_sil, name='kisi_sil'),
    
    path('kisi/detay-ekle/<int:kisi_id>/', views.kisi_detay_ekle, name='kisi_detay_ekle'),
    path('kisi/detay-sil/<int:detay_id>/', views.kisi_detay_sil, name='kisi_detay_sil'),
    path('kisi/detay-duzenle/<int:detay_id>/', views.kisi_detay_duzenle, name='kisi_detay_duzenle'),
    path('kisi/detay-veri/<int:detay_id>/', views.kisi_detay_veri, name='kisi_detay_veri'),
  
    
    # Account management URLs
    path('account/freeze/', account_views.freeze_account, name='freeze_account'),
    path('account/unfreeze/', account_views.unfreeze_account, name='unfreeze_account'),
    path('account/delete/', account_views.schedule_account_deletion, name='schedule_account_deletion'),
    path('account/cancel-deletion/', account_views.cancel_account_deletion, name='cancel_account_deletion'),
    

    # Şarkı sözleri URL’leri
    path('sarki/', views.sarki_sozleri, name='sarki_sozleri'),
    path('sarki/kisi-ara/', views.sarki_kisi_ara, name='sarki_kisi_ara'),
    path('sarki/album-liste/<int:kisi_id>/', views.sarki_album_liste, name='sarki_album_liste'),
    path('sarki/liste/<int:album_id>/', views.sarki_liste, name='sarki_liste'),
    path('sarki/detay/<int:sarki_id>/', views.sarki_detay, name='sarki_detay'),
    path('sarki/sil/<int:sarki_id>/', views.sarki_sil, name='sarki_sil'),
    path('sarki/ekle/', views.sarki_ekle, name='sarki_ekle'),
    path('sarki/album-sil/<int:album_id>/', views.sarki_album_sil, name='sarki_album_sil'),
 
    # Şarkı sözleri için yeni URL’ler
    path('sarki/ara/', views.sarki_ara, name='sarki_ara'),  # Şarkı arama ve türe göre filtreleme
    path('sarki/album-ekle/<int:kisi_id>/', views.sarki_album_ekle, name='sarki_album_ekle'),  # Albüm ekleme
    path('sarki/detay-ekle/<int:sarki_id>/', views.sarki_detay_ekle, name='sarki_detay_ekle'),  # Şarkıya detay ekleme
    path('sarki/detay-veri/<int:detay_id>/', views.sarki_detay_veri, name='sarki_detay_veri'),  # Şarkı detayını düzenleme için veri
    path('sarki/detay-duzenle/<int:detay_id>/', views.sarki_detay_duzenle, name='sarki_detay_duzenle'),  # Şarkı detayını düzenleme
    path('sarki/detay-sil/<int:detay_id>/', views.sarki_detay_sil, name='sarki_detay_sil'),  # Şarkı detayını silme
    path('sarki/album-degistir-veri/<int:sarki_id>/', views.sarki_album_degistir_veri, name='sarki_album_degistir_veri'),  # Şarkı albümünü değiştirme için veri
    path('sarki/album-degistir/<int:sarki_id>/', views.sarki_album_degistir, name='sarki_album_degistir'), # Şarkı albümünü değiştirme
    path('sarki/duzenle/<int:sarki_id>/', views.sarki_duzenle, name='sarki_duzenle'),  # Şarkı düzenleme
    path('sarki/duzenle-kaydet/<int:sarki_id>/', views.sarki_duzenle_kaydet, name='sarki_duzenle_kaydet'),  # Şarkı düzenleme kaydetme
    
    
    # Daha spesifik URL’ler önce gelmeli
    path('atasozu-deyim/ara/', views.atasozu_deyim_ara, name='atasozu_deyim_ara'),
    path('atasozu-deyim/ekle/', views.atasozu_deyim_ekle, name='atasozu_deyim_ekle'),
    # Detay işlemleri için URL’ler
    path('atasozu-deyim/detay/<int:detay_id>/duzenle/', views.atasozu_deyim_detay_duzenle, name='atasozu_deyim_detay_duzenle'),
    path('atasozu-deyim/detay/<int:detay_id>/sil/', views.atasozu_deyim_detay_sil, name='atasozu_deyim_detay_sil'),
    path('atasozu-deyim/detay/<int:detay_id>/veri/', views.atasozu_deyim_detay_veri, name='atasozu_deyim_detay_veri'),
    # Atasözü/Deyim ile ilgili işlemler
    path('atasozu-deyim/<str:tur>/<int:id>/detay-ekle/', views.atasozu_deyim_detay_ekle, name='atasozu_deyim_detay_ekle'),
    path('atasozu-deyim/<str:tur>/<int:id>/sil/', views.atasozu_deyim_sil, name='atasozu_deyim_sil'),
    path('atasozu-deyim/<str:tur>/<int:id>/duzenle/', views.atasozu_deyim_duzenle, name='atasozu_deyim_duzenle'),
    # Daha genel URL’ler sona gelmeli
    path('atasozu-deyim/<str:tur>/<int:id>/', views.atasozu_deyim_detay, name='atasozu_deyim_detay'),
    path('atasozu-deyim/', views.atasozu_deyim, name='atasozu_deyim'),


    # Katkılar URL’leri
    path('katki/load-more/', views.load_more_katkilar, name='load_more_katkilar'),
    path('katki/load-more-liderler/', views.load_more_liderler, name='load_more_liderler'),

    # AI URL’leri
    # path('enhance/', ai_views.process_text, name='enhance'),  # Geçici olarak kapatıldı

    path('yer-adlari/', yer_adlari_views.yer_adlari_anasayfa, name='yer_adlari_anasayfa'),
    path('yer-adi/ekle/', yer_adlari_views.yer_adi_ekle, name='yer_adi_ekle'),
    path('yer-adi/<int:yer_adi_id>/', yer_adlari_views.yer_adi_detay, name='yer_adi_detay'),
    path('yer-adi/<int:yer_adi_id>/duzenle/', yer_adlari_views.yer_adi_duzenle, name='yer_adi_duzenle'),
    path('yer-adi/<int:yer_adi_id>/sil/', yer_adlari_views.yer_adi_sil, name='yer_adi_sil'),
    path('yer-adi-detay/<int:detay_id>/duzenle/', yer_adlari_views.yer_adi_detay_duzenle, name='yer_adi_detay_duzenle'),
    path('yer-adi-detay/<int:detay_id>/sil/', yer_adlari_views.yer_adi_detay_sil, name='yer_adi_detay_sil'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    
    # Category URLs
    path('category/', category_views.categories, name='category_list'),
    path('categories/', category_views.categories, name='categories'),
    path('category/<slug:slug>/', category_views.category_detail, name='category_detail'),
    
    # Follow URLs
    path('follow/<str:username>/', follow_views.toggle_follow, name='toggle_follow'),
    path('toggle-follow/<str:username>/', follow_views.toggle_follow, name='toggle_follow'),
    
    # Hashtag URLs
    path('hashtag/<slug:slug>/', hashtag_views.hashtag_detail, name='hashtag_detail'),
    path('trending/', hashtag_views.trending_hashtags, name='trending_hashtags'),
    
    # Bookmark URLs
    path('bookmark/<int:entry_id>/', bookmark_views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmark-topic/<slug:topic_slug>/', bookmark_views.toggle_topic_bookmark, name='toggle_topic_bookmark'),
    path('bookmarks/', bookmark_views.user_bookmarks, name='user_bookmarks'),
    
    # PWA URLs
    path('offline/', views.offline_page, name='offline'),
    
    # API URLs
    path('api/check-updates/', api_views.check_updates, name='api_check_updates'),
    path('api/ai-suggest-topics/', api_views.ai_suggest_topics, name='api_ai_suggest_topics'),
    path('api/ai-generate-hashtags/', api_views.ai_generate_hashtags, name='api_ai_generate_hashtags'),
    path('api/trending-topics/', api_views.trending_topics, name='api_trending_topics'),
    path('api/live-stats/', api_views.live_stats, name='api_live_stats'),
    path('api/quick-vote/', api_views.quick_vote, name='api_quick_vote'),
    path('api/search-suggestions/', api_views.search_suggestions, name='api_search_suggestions'),
    
    # Font URLs
    path('fonts/', font_views.font_list, name='font_list'),
    path('fonts/download/<str:font_name>/', font_views.download_font, name='download_font'),
    
    # Settings URLs
    path('settings/', settings_views.user_settings, name='user_settings'),
    path('settings/privacy/', settings_views.privacy_settings, name='privacy_settings'),
    path('settings/notifications/', settings_views.notification_settings, name='notification_settings'),

]   