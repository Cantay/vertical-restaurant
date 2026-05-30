# Vaka 05: Dijital Restoran Deneyimi

## Kısa Kart Metni

Restoranlar için, QR menü, masa içi servis deneyimi, online sipariş, teslimat, PWA ve operasyon kalite süreçlerini aynı yapıda yöneten bütünleşik bir platform geliştirdik. Menüden siparişe, garson çağrısından mobil kullanım ve saha kalite takibine kadar farklı katmanları tek sistemde birleştirdik.

## Kısa Vaka Özeti

Bu projede hedef, restoranların dijital yüzünü yalnızca bir menü sayfası ya da basit bir sipariş ekranı olmaktan çıkarıp, salon deneyimi ile paket servis operasyonunu aynı omurgada buluşturan bir sisteme dönüştürmekti. Lugatsoft olarak QR menü, AR destekli ürün sunumu, garson çağırma, alerjen ve besin bilgileri, online sipariş, adres ve ödeme akışları, yorum yönetimi, PWA kurulumu, lokasyon bazlı online formlar ve operasyon kalite bildirimlerini aynı platformda kurguladık.

Ortaya çıkan yapı, restoran için hem salon içi deneyimi güçlendiren hem de paket servis operasyonunu hızlandıran dijital bir merkez haline geldi.

## Problem

Restoranlarda müşteri deneyimi ve operasyon çoğu zaman birbirinden kopuk araçlarla yönetilir. Masadaki müşteri menüyü başka yerden görür, paket sipariş başka sistemden akar, teslimat süreci farklı ekiplerce takip edilir. Bu da hem kullanıcı tarafında dağınık bir deneyim hem de işletme tarafında yönetim zorluğu üretir.

Bu proje için ihtiyaç duyulan yapı:

- QR kod ile hızlı ve modern menü deneyimi sunmak
- Masa bazlı kullanım ve garson çağırma senaryolarını dijitalleştirmek
- Alerjen, içerik ve besin bilgilerini erişilebilir hale getirmek
- Restoran ürünlerini online sipariş akışıyla bağlamak
- Adres, ödeme, favoriler, kuponlar ve sipariş geçmişi gibi kullanıcı fonksiyonlarını tek yapıda toplamak
- Yeni siparişleri restoran ekibine anlık ulaştırmak
- QR menü ile teslimat uygulamasını ayrı veri yapıları yerine tek bir içerik omurgasında yönetmek
- Mobil uygulama benzeri kurulum deneyimi ve lokasyon bazlı operasyon formları sunmak
- Misafir geri bildirimi ve kalite süreçlerini dijitalleştirmek

## Çözüm

Lugatsoft olarak restoran sektörüne özel, çok katmanlı bir dijital deneyim altyapısı geliştirdik. Bu yapı ilk aşamada `Ronix QR Menu`, `Ronix Food Delivery` ve bu iki sistemi veri ve görünüm tarafında bağlayan `Ronix QR Menu Bridge` ile kuruldu; ikinci aşamada ise `Ronix PWA Manager`, `Ronix Online Form Manager` ve `Ronix Quality Manager` katmanlarıyla genişletildi.

Kurulan yapı içinde:

- Her masa için QR kod tabanlı dijital menü kurgulandı
- Menü kategorileri ve ürün detayları mobil uyumlu sayfalara dönüştürüldü
- Alerjen, içerik ve besin bilgileri ürün sayfasına taşındı
- 3D model desteği ile AR ürün görüntüleme senaryosu eklendi
- Garson çağırma sistemi ve gerçek zamanlı çağrı takibi geliştirildi
- Online sipariş, sepet, ödeme, adres ve sipariş geçmişi akışları oluşturuldu
- Restoran çalışma saatleri, popülerlik, değerlendirme ve favori yapıları işlendi
- Kupon, bahşiş, ürün eklentileri ve restoran yorumları desteklendi
- Yeni siparişler için backend uyarı ve operasyon ekranı oluşturuldu
- QR menü ile food delivery arasında restoran, kategori ve ürün senkronizasyonu kuruldu
- Belirli path'ler için installable PWA deneyimi kurgulandı
- Lokasyon bazlı tekrar kullanılabilir online formlar ve gönderim yönetimi eklendi
- Misafir şikayetleri, denetim, ürün takibi ve kalite operasyonları için özel yönetim katmanı oluşturuldu

## Öne Çıkan Bileşenler

### 1. QR Kod Tabanlı Masa Deneyimi

Her masa için ayrı QR kod üretimiyle müşterilerin doğrudan restoran menüsüne ve hatta ilgili masa bağlamına ulaşabildiği bir yapı geliştirildi. Bu yaklaşım, fiziksel menü bağımlılığını azaltırken masa bazlı dijital deneyimin temelini oluşturdu.

### 2. Zengin Dijital Menü

Menü yalnızca ürün adı ve fiyat gösteren bir yapı olarak bırakılmadı. Kategori düzeni, ürün detay sayfası, görsel içerik, içerik açıklamaları, alerjen bilgileri ve besin verileri ile daha güven verici bir deneyim tasarlandı. Bu özellikle sağlık, hassasiyet ve premium sunum açısından önemliydi.

### 3. AR ile Ürün Sunumu

Restoran ürünlerinin 3D model ile görüntülenebildiği AR katmanı, dijital menüyü daha yenilikçi ve daha etkileyici bir seviyeye taşıdı. Bu, standart QR menü deneyiminden ayrışan güçlü bir kullanıcı deneyimi katmanı oldu.

### 4. Garson Çağırma ve Salon Operasyonu

Masa üzerinden garson çağırma akışı ve çağrıların yönetici/ekip tarafında izlenmesi için gerçek zamanlı bir çağrı sistemi geliştirildi. Böylece müşteri tarafında bekleme deneyimi iyileşirken restoran ekibi için salon içi talepler daha görünür hale geldi.

### 5. Online Sipariş ve Teslimat Uygulaması

Platformun ikinci büyük ayağında restoranların online sipariş, sepet, ödeme, adres ve sipariş geçmişi akışlarını yöneten food delivery deneyimi kurgulandı. Kullanıcılar restoranları keşfedebilir, ürünleri sepete ekleyebilir, sipariş verebilir ve geçmiş siparişlerini takip edebilir hale geldi.

### 6. Restoran ve Müşteri Deneyimi Katmanları

Favori restoranlar, popüler ürünler, kupon ekranları, hesap ve profil alanları, kayıtlı adresler, bildirimler ve yardım/destek sayfaları ile sistem yalnızca sipariş alan bir kanal değil, gerçek bir son kullanıcı ürünü haline getirildi.

### 7. Çalışma Saatleri, Teslimat ve Derecelendirme

Restoranların açık/kapalı durumunu çalışma saatleri ve zaman dilimi mantığına göre yöneten yapı, teslimat süresi, sabit veya kilometre bazlı teslimat bedeli, yorum puanı ve yemek puanı gibi unsurlarla birlikte daha güvenilir bir sipariş deneyimi sundu.

### 8. Ürün Eklentileri ve Sepet Kurgusu

Yemeklere bağlı addon yapısı ile ekstra malzeme, opsiyonel ürün ve fiyat farkı senaryoları desteklendi. Bu sayede sipariş akışı restoran sektörünün gerçek ürün çeşitliliğine daha uygun hale geldi.

### 9. Yorum ve Geri Bildirim Sistemi

Restoran ve ürün bazlı puanlama, yorum etiketleri ve değerlendirme yapıları sayesinde müşteri geri bildirimi görünür hale getirildi. Bu katman hem son kullanıcı güvenini artırdı hem de restoranlara hizmet kalitesi konusunda veri sağladı.

### 10. Operasyonel Sipariş Uyarıları

Yeni siparişlerin backend tarafında sesli ve görsel uyarılarla ekibe iletilmesi için özel bir operasyon katmanı geliştirildi. Böylece restoran yöneticileri yeni siparişleri anlık görebilir ve gecikme riskini azaltabilir hale geldi.

### 11. QR Menü ve Delivery Arasında Veri Köprüsü

Projeyi güçlü kılan en önemli farklardan biri, QR menü ile food delivery tarafının birbirinden kopuk iki yapı olarak bırakılmaması oldu. Bridge katmanı ile restoran bilgileri, kategori yapıları, ürünler, puanlar, çalışma saatleri ve addon mantıkları senkronize edildi. Böylece içerik yönetimi daha sürdürülebilir hale geldi.

### 12. Installable PWA Deneyimi

Sistemin mobil kullanımını güçlendirmek için belirli website path'leri için kurulabilir PWA altyapısı eklendi. Özel isim, ikon, manifest dosyası ve yükleme butonu desteği sayesinde kullanıcı deneyimi klasik web kullanımının ötesine taşındı ve platform daha uygulama benzeri bir yapıya kavuştu.

### 13. Lokasyon Bazlı Online Form Yönetimi

Platforma tekrar kullanılabilir ve lokasyon bazlı çalışan online form altyapısı dahil edildi. Bu sayede farklı şube, alan veya kullanım senaryoları için frontend üzerinde formlar yayınlanabiliyor; tüm gönderimler ise yetki kontrollü biçimde backend tarafında yönetilebiliyor. Bu katman, restoran operasyonunda bilgi toplama ve süreç standardizasyonu açısından önemli bir genişleme sundu.

### 14. Kalite ve Misafir Geri Bildirimi Operasyonları

`Ronix Quality Manager` ile mobil uygulama lokasyonları, menü buton akışları, duyurular, eğitim içerikleri, denetim checklist'leri, operasyonel uygunsuzluklar, inspeksiyon raporları, ürün takibi, mal kabul süreçleri ve misafir şikayet yönetimi için ayrı bir operasyon katmanı kurgulandı. Böylece platform sadece sipariş ve servis yönetimi yapan bir yapı olmaktan çıkıp, kalite ve sürekli iyileştirme süreçlerini de destekleyen daha kapsamlı bir işletme çözümüne dönüştü.

## Sağlanan Değer

Bu proje ile:

- restoranın salon içi ve online sipariş deneyimi aynı sistemde toplandı,
- müşteri tarafında daha modern ve daha akıcı bir kullanım sunuldu,
- menü yönetimi daha zengin ve daha güncel hale geldi,
- operasyon ekibi için yeni sipariş ve masa talepleri daha görünür oldu,
- QR menü ile teslimat sistemleri arasında veri tekrarının önüne geçildi,
- mobil uygulama benzeri kullanım deneyimi güçlendirildi,
- lokasyon bazlı form ve kalite süreçleri dijitalleştirildi,
- restoran markaları için daha güçlü bir dijital servis altyapısı kuruldu.

Lugatsoft bu projede yalnızca bir QR menü ya da sipariş ekranı geliştirmedi; restoranların dijital servis, müşteri deneyimi, mobil kullanım ve operasyon kalite süreçlerini aynı çatı altında birleştiren ölçeklenebilir bir platform kurdu.

## Sitede Kullanılabilecek Güçlü Vurgu Cümleleri

- Restoran deneyimini masa içinden teslimata kadar tek sistemde kurguluyoruz.
- QR menü, online sipariş, PWA ve operasyon bildirimlerini aynı dijital omurgada birleştiriyoruz.
- Sadece ürün listeleyen değil, servis kalitesini artıran restoran platformları geliştiriyoruz.
- Menü verisini, sipariş akışını, kalite süreçlerini ve müşteri deneyimini tek merkezden yönetilebilir hale getiriyoruz.

## Etiketler

`QR Menü` `Online Sipariş` `Food Delivery` `PWA` `Kalite Yönetimi` `Garson Çağırma` `AR Menü` `Müşteri Deneyimi`
