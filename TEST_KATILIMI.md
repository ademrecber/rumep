# Rumep Spor test katılımı

- Sayfa: `/rumep-spor/test-katilim/`
- Yönetim: Rumep Stüdyo → Spor test başvuruları
- Gmail adresi ve zorunlu veri kullanım onayı alınır. Önizleme POST'u kayıt oluşturmaz; süreli, imzalı son onayla kayıt oluşur. E-posta URL'ye yazılmaz, sayfa önbelleğe alınmaz.
- Yalnızca `gmail.com` kabul edilir; noktalı yazımlar tek Gmail hesabı olarak birleştirilir. `+` ek adresleri kabul edilmez.
- Yönetici Google Play listesine elle ekler, “Teste eklendi” kutusunu kaydeder ve başvuruyu siler. Başvuru silmek Google Play listesinden kaldırmaz.
- Otomatik e-posta veya otomatik Play Console ekleme yok. Bekleme mesajı yaklaşık 10 dakika önerir; Google onayı/elle ekleme için kesin süre sözü verilmez.
- İndirme hedefi kullanıcının verdiği `https://play.google.com/store/apps/details?id=net.rumep.spor`. Kapalı teste ayrıca katılım gerekebilir; üretim henüz açık değil.
- Silme: Django admin standart tekli/toplu silme onayı. İlgili adres teknik yedeklerde bir süre daha kalabilir; “hiç saklanmaz” iddiası yapılmaz.
- CSRF, sunucu Gmail doğrulaması, imzalı onay (10 dk), tekrar kayıt koruması ve temel çerez bazlı deneme limiti var. Çok işlemli üretim/saldırı ölçeğinde ortak Redis/kenar hız sınırlaması ayrıca değerlendirilmeli. Ham e-posta veya IP özel uygulama loguna yazılmaz.
- Dağıtımda `python manage.py migrate` çalışmalı: `0003_sportestapplication`.
