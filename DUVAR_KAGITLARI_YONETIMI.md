# Rumep Stüdyo — duvar kağıdı yönetimi

## 20 Kasım 2026 — içerik sınırları

- Tribün: en yeni 40 yayımlanmış paylaşım. Sıra yayın tarihi ve kayıt numarasıdır.
- Duvar kâğıdı: en yeni 50 yayımlanmış kayıt. Galeriyle aynı oluşturulma tarihi/kayıt numarası sırası kullanılır.
- Yalnızca yeni yayın/taslaktan yayına geçiş sonrasında temizlik tetiklenir; okuma, normal düzenleme veya zamanlayıcı temizlik başlatmaz. Taslaklar silinmez. Yeni yayın sınırı aşmadıkça eski kayıtlar korunur.
- Temizlik, yayın işlemi başarıyla tamamlandıktan sonra çalışır. Eski paylaşımın ek görselleri de temizlenir. Başka bir paylaşım, ek görsel veya duvar kâğıdı tarafından kullanılan dosyalar korunur. Dosyalar veritabanı silme işlemi commit edildikten sonra silinir. Depolama silme hataları loglanır; böyle bir durumda dosya artıkları kalabilir.
- PostgreSQL'de aynı türün eşzamanlı temizlikleri işlem süresince kilitlenir. Yeni tablo/migration ve sürekli açık bağlantı eklenmedi.
- Yönetim ekranındaki Yayında alanı, kalıcı temizleme sınırını açıklar. Sınırı aşan içerik kalıcı olarak silinir; geri dönüş kopyası üretilmez.
- 29 yerel Django testi başarılı. Gerçek Neon/S3 silme işlemi yapılmadı. Neon kota kesintisi ve Cloudflare içerik taşıması bu değişiklikle çözülmüş değildir; canlı etkinlik ayrıca doğrulanmalıdır.

Aşağıdaki kurulum notları tarihsel kayıttır.

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
