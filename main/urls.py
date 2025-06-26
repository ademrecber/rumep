from django.urls import path
from .views import views
from .views import popular_views, profile_views
from .views import post_views
from .views import account_views
from .views import home_views
from .views import ai_views


handler404 = 'main.views.custom_404'
urlpatterns = [

    path('', home_views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete_post'),
    path('post/<uuid:pk>/', views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-visibility/', profile_views.update_visibility, name='update_visibility'),
    path('load-more/', views.load_more, name='load_more'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('vote-post/<uuid:post_id>/', views.vote_post, name='vote_post'),
    path('vote-comment/<int:comment_id>/', views.vote_comment, name='vote_comment'),
    path('like-post/<uuid:post_id>/', views.like_post, name='like_post'),
    path('bookmark-post/<uuid:post_id>/', post_views.bookmark_post, name='bookmark_post'),
    path('popular/', popular_views.popular, name='popular'),
    path('popular/<str:period>/', popular_views.popular, name='popular_period'),
    path('load-more-popular/', popular_views.load_more_popular, name='load_more_popular'),
    path('add-critique/<uuid:post_id>/', views.add_critique, name='add_critique'),
    path('list-critiques/', views.list_critiques, name='list_critiques'),
    path('delete-critique/<uuid:critique_id>/', post_views.delete_critique, name='delete_critique'),
    path('vote-critique/<uuid:critique_id>/', post_views.vote_critique, name='vote_critique'),
    path('popular-critiques/', post_views.popular_critiques, name='popular_critiques'),
    path('unlike-post/<uuid:post_id>/', views.unlike_post, name='unlike_post'),

    path('remove-bookmark/<uuid:post_id>/', profile_views.remove_bookmark, name='remove_bookmark'),
    path('profile-delete-comment/<int:comment_id>/', views.profile_delete_comment, name='profile_delete_comment'),
    path('profile-delete-post/<uuid:post_id>/', views.profile_delete_post, name='profile_delete_post'),
    path('profile-delete-critique/<uuid:critique_id>/', views.profile_delete_critique, name='profile_delete_critique'),
    path('profile/<str:username>/', profile_views.profile, name='profile_detail'),

    path('rmp/<str:short_code>/', post_views.redirect_short_link, name='redirect_short_link'),
    path('emojis/', post_views.get_emojis, name='get_emojis'),

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
    path('enhance/', ai_views.process_text, name='enhance'),

]   