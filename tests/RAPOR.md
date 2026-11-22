# HelpDesk - proje durumu

Kısa özet: uygulama hazır. Başlangıçta sadece bilet oluşturup listeyen küçük bir
konsol programıydı, sonunda tasarım kalıplarının hepsi birbirine bağlı hale
geldi. Aşağıda ne yaptığımızı ve hangi noktaları sonradan düzelttiğimizi yazdım.

## Veritabanı tarafı

SQLite üzerinde dört tablo var: `staff`, `tickets`, `ticket_activity` ve
`notifications`. Tüm bilet alanlarını tek bir `tickets` tablosunda tutmayı
seçtik; üç bilet türü için ayrı tablo açmak hem sorguları zorlaştıracaktı hem de
aynı kayıt kaydetme kodunu üç kez yazmamıza yol açacaktı.

Başta birkaç şeyi atlamıştık, sonradan düzelttik:

- SQLite foreign key'leri varsayılan olarak kapalı tutuyor. Her bağlantıda
  `PRAGMA foreign_keys = ON` çalıştırıyoruz.
- Tarihleri ISO-8601 metin olarak saklıyoruz. Naive ve aware datetime'ları
  karşılaştırmak hata verdiği için sıralama stratejisinde `_as_utc()` var.
- Filtrelenen kolonlara indeks ekledik (status, priority, category, staff,
  deadline, activity.ticket_id).
- Doğrudan oluşturulan bir bilette `updated_at` boş kalabiliyordu; repository
  artık onu `created_at`'ten dolduruyor.

Şema değişse bile `Database.initialize()` tekrar tekrar çağrılabiliyor.

## Kalıplar

- **State:** biletin durum geçişleri (`OPEN`, `IN_PROGRESS`, `RESOLVED`,
  `CLOSED`) dört ayrı sınıfa bölündü. Geçersiz geçişler sessizce geçilmiyor,
  `InvalidTransitionError` atılıyor. 7 günlük yeniden açma kuralı da burada.
- **Factory Method:** her kategori için bir creator var. Zorunlu alanlar
  (component / affected_account / asset_tag + location) ve varsayılan
  öncelikler bilet oluşturulurken kontrol ediliyor.
- **Strategy:** sıralama için öncelik ve son tarih stratejileri, atama için de
  en az işi olan personeli seçen strateji var. Çalışma anında değiştirilebiliyor.
- **Observer ve Decorator:** event'ler publisher üzerinden yayınlanıyor; biri
  konsola yazıyor, diğeri `ticket_activity` tablosuna kayıt atıyor. Bildirime
  log ve urgent özelliklerini ekleyen decorator'lar ise sadece `main.py`'de
  birleştiriliyor. Observer sınıflarına dokunmak zorunda kalmadık.

## Testler

`pytest` ile son durum: **207 geçti, 7 test atlandı**. Atlananlar bilinçli:
durum matrisinde geçişin serbest olduğu hücreler, orada hata mesajı test
edilemediği için atlanıyor.

Testler birbirini etkilemesin diye her test kendi geçici veritabanını
kullanıyor. Birim testlerinin yanında durum matrisi, sınır değerleri, seed,
repository ve uçtan uca senaryolar için de ayrı dosyalar var. Seed'i iki kez
çalıştırınca ikincisinin veri eklemediğini de kontrol ettik.

## Şu anki durum

Proje çalışır durumda. Elle denemek için `helpdesk.db`'yi silip seed'i
çalıştırmak, sonra menüden 1-7 arası seçenekleri denemek yeterli. Kalan küçük
tavizler README'de yazılı: `status` eski çağrılar için kod değerini döndürüyor,
okunabilir isim `status_display`'de; birkaç eski import yolu da uyumluluk için
bırakıldı.
