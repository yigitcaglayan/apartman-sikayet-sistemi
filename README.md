🏢 Apartman Şikayet Yönetim Sistemi

Bu uygulama, apartman sakinlerinin şikayetlerini dijital ortamda yönetime iletebilmesi ve yöneticilerin bu süreci takip edebilmesi için geliştirilmiştir.

🚀Özellikler

Kullanıcı Paneli: Şikayet oluşturma ve durum takibi.

Yönetici Paneli: Tüm şikayetleri görüntüleme, durum güncelleme (Beklemede, Çözüldü vb.) ve yönetici notu ekleme.

İstatistikler: Dashboard üzerinden bekleyen ve çözülen işlerin takibi.Güvenlik: Şifrelerin hashlenerek saklanması ve rol tabanlı yetkilendirme.

🛠️Kullanılan Teknolojiler

Backend: Python, Flask

Veritabanı: SQLite

Frontend: Jinja2, HTML, CSS

```📦 Kurulum ve Çalıştırma
Kütüphanelerin Yüklenmesi

Bash
pip install flask
Uygulamanın Başlatılması

Bash
python sikayet_sistemi_backend.py

Uygulama başladıktan sonra tarayıcınızdan http://localhost:5000 adresine giderek sisteme erişebilirsiniz.

🔑 Test Hesapları (Demo)

Sistem ilk kez çalıştırıldığında aşağıdaki hesaplar otomatik olarak oluşturulur:

Rol E-posta Şifre

Yönetici admin@site.com admin123

Kullanıcı ahmet@email.com kullanici123

Bu proje, Yönetim Bilişim Sistemleri (YBS) kapsamında bir bitirme/ödev projesi olarak tasarlanmıştır.
