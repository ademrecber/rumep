# Veritabanından bağımsız web yayını — 24 Kasım 2026

Railway logu: Neon kota aşımı `migrate` sırasında bağlantıyı reddettiği için Gunicorn başlamıyordu. Tek yeniden başlatmada aynı hata güncel logda doğrulandı.

Docker artık `scripts/start_public.py` ile **açıkça ayrı public site modunu** çalıştırır. Bu mod `rumep.public_settings` / `public_urls` / `public_wsgi` kullanır. Ana sayfa, Rumep Spor tanıtımı, yasal sayfalar ve iletişim formu mevcut şablonlarla sunulur. Veritabanı sürücüsü dummy, model/admin/session uygulamaları yüklenmez; iletişim mesajları mevcut SMTP ayarlarıyla gönderilir, sonuç mesajı imzalı cookie'de tutulur. CSRF kontrolü korunur. `/healthz/` veritabanına gitmez.

Bu, eski Django modunda migration hatasını görmezden gelmek değildir. Eski `scripts/start_production.py`, `rumep.settings`, modeller, migration dosyaları, Neon ve eski görseller olduğu gibi korunur. Tam yönetim arşivine dönmek gerektiğinde Neon erişimi ve güncel migration'lar doğrulanarak o başlangıç komutu özellikle seçilmelidir. Public mod eski veritabanına otomatik geçiş yapmaz.

Yeni yayın yönetimi `/rumep-studyo/content/` Cloudflare Worker yolundadır. `/rumep-studyo/` buraya yönlenir. Cloudflare'ın mevcut feed/wallpaper/bildirim yolları değişmedi. Futbol API'si ve diğer projeler değiştirilmedi. Eski dinamik admin public modda sunulmaz; eski veriler silinmez.

Gerekli runtime secret: `SECRET_KEY` (mevcut Railway değeri). İletişim için mevcut `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`. Hiçbir secret yeni dosyalara kopyalanmaz. Deployment ortamı `DJANGO_SETTINGS_MODULE` değişkeniyle legacy ayara zorlanmış olsa bile public giriş bunu doğru modüle ayarlar.

Yerel doğrulama: `python scripts/test_public_site.py`. Veritabanı bağlantısı özellikle yasaklanarak 13 public uç, iletişim POST/geri bildirim cookie'si, CSRF reddi ve admin ayrımı test edilir; mail yalnız bellek backend'ine yazılır. Bu test SMTP tesliminin kanıtı değildir. Gerçek yayında `/`, `/rumep-spor/`, CSS, görseller ve health ayrıca doğrulanmalıdır.

24 Kasım canlı doğrulaması: `c576a15` Railway `feb65639-d7fe-49a2-8c9b-b4cb94de7e3b` dağıtımı Active oldu. `/`, `/rumep-spor/`, `/healthz/`, ana CSS, hero ve uygulama ekran görselleri, mevcut Cloudflare `/api/spor-feed/` ve gizlilik sayfası HTTP 200 döndü. Chrome'da rumep.net ana sayfası gerçek görselleriyle açıldı. Kontrol sırasında yerel DNS'in eski sorununu ayırmak için HTTP isteklerinde `curl --resolve rumep.net:443:104.21.6.245` kullanıldı; TLS doğrulaması kapatılmadı. İki ana sayfadaki 15 statik referansın kaynak dosyası bulundu.
