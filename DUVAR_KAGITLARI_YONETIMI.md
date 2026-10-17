# Rumep Stüdyo — duvar kağıdı yönetimi

Yerel uygulama hazır; canlıya henüz dağıtılmadı.

## Hazırlananlar

- Yeni yönetim yolu `/rumep-studyo/`; eski `/admin/` yolu 404 döner. URL değişikliği kimlik doğrulamasının yerine geçmez. Mevcut admin yetkileri korunur.
- Duvar kağıtları yönetiminde başlık, açıklama, JPEG/PNG/WebP dosyası ve yayın durumu.
- Küçük önizleme, çözünürlük, dosya boyutu ve tarihler otomatik hazırlanır. Önizleme isteği admin girişi ve model görüntüleme izni gerektirir; taslak önizlemesi herkese açılmaz.
- Dosya en fazla 12 MB ve 25 megapiksel, en az 320×320 olmalı. Gerçek görsel doğrulanır; hareketli dosyalar reddedilir. Piksel verisinden yeniden üretim EXIF ve dosya sonu eklerini temizler. Kullanıcı dosya adı sunucuda kullanılmaz.
- Yeni kayıt varsayılan olarak taslaktır. Bu çalışma Flutter'a yayınlama/Firebase senkronizasyonunu içermez.

## Canlıya geçmeden önce

Railway production şu anda kalıcı volume olmayan `/app/db.sqlite3` kullanıyor. Kullanıcının oluşturduğu admin hesabı korunmalı. Yeniden dağıtımdan önce SQLite yedeği alınıp veriler kalıcı PostgreSQL'e aktarılmalı ve admin girişi doğrulanmalı. Yedek, parola karmaları içerebilir; Git'e veya sohbete eklenmez.

Neon Free hesabı için kullanıcı girişi henüz tamamlanmadı; ücretli Railway veritabanı/disk veya abonelik açılmadı. `DATABASE_URL` desteği hazırlanmış olsa da gerçek bağlantı henüz yapılmadı.

Görseller ayrıca kalıcı dosya/nesne depolamasında tutulmalı. PostgreSQL dosya depolamasının yerini tutmaz. Mevcut Railway geçici diski bu amaçla kullanılmaz. Üretimde `WALLPAPER_UPLOADS_ENABLED` varsayılanı kapalı; kalıcı depolama bağlanıp test edilmeden açılmaz. Yerelde geçici dosya depolaması test için kullanılabilir. `MEDIA_ROOT` dizini Git dışında kalır; medya staticfiles dizinine konulmaz.

Bu iki kalıcılık adımı tamamlandıktan sonra migration `main/0002_wallpaper.py` uygulanıp kod dağıtılır. Admin hesabı var olduğundan yeni dağıtım sonrası aynı hesap korunmalı; ortak/default parola üretilmez. Canlı adres ancak dağıtımdan sonra `https://rumep.net/rumep-studyo/` olur.

## Kontroller

`python manage.py test main.test_wallpapers rumep.test_database_config` — 8 test geçti. Eski URL'nin kapanması, yeni URL'de oturum gerekliliği, gerçek admin dosya yükleme, taslak varsayılanı, dosya normalleştirme, önizleme yetkileri, bozuk/büyük dosya reddi, üretim yükleme kilidi ve metadata düzenleme test edildi.

`python manage.py check` temiz; migration kontrolü yapıldı. Bunlar yerel testlerdir; canlı yükleme doğrulaması değildir.
