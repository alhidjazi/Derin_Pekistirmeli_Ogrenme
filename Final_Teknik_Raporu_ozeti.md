# 🚚 Akıllı Lojistik Simülatörü

## Trafik, Batarya Kısıtları ve Çoklu Ajan Koordinasyonu Altında Hibrit A* ve Pekiştirmeli Öğrenme Tabanlı Kentsel Lojistik Simülasyon Platformu

> Yapay zekâ, yol planlama ve çoklu ajan sistemleri alanlarında geliştirilen araştırma odaklı bir simülasyon projesi.

---

## 📌 Proje Hakkında

Akıllı Lojistik Simülatörü, şehir içi son-mil (Last-Mile Delivery) teslimat problemlerini modellemek amacıyla geliştirilmiş çoklu ajan destekli bir kentsel lojistik simülasyon platformudur.

Proje kapsamında;

* Trafik yoğunluğu
* Enerji tüketimi
* Şarj istasyonları
* Çoklu kurye koordinasyonu
* Görev paylaşımı
* Yol planlama
* Pekiştirmeli öğrenme

gibi gerçek dünyada karşılaşılan lojistik problemleri tek bir simülasyon ortamında bir araya getirilmiştir.

Sistem, klasik yapay zekâ yaklaşımı olan **A*** algoritması ile modern öğrenme tabanlı yaklaşım olan **Q-Öğrenmesi (Q-Learning)** yöntemlerini aynı çevrede karşılaştırmalı olarak çalıştırabilmektedir.

Bu yönüyle proje yalnızca bir simülasyon uygulaması değil, aynı zamanda yapay zekâ ve lojistik optimizasyon araştırmaları için deneysel bir araştırma platformu niteliği taşımaktadır.

---

# 🎯 Araştırma Problemi

Son-mil teslimat operasyonları lojistik maliyetlerin önemli bir bölümünü oluşturmaktadır.

Bu süreçte:

* Trafik yoğunluğu
* Sınırlı enerji kapasitesi
* Birden fazla teslimat noktası
* Eşzamanlı çalışan araçlar
* Görev dağıtımı

gibi faktörler karar verme sürecini karmaşık hale getirmektedir.

Bu proje aşağıdaki araştırma sorusuna odaklanmaktadır:

> Trafik ve enerji kısıtları altında çalışan çoklu teslimat ajanlarında, klasik yol planlama algoritmaları ile öğrenme tabanlı yöntemler nasıl performans göstermektedir?

---

# 🔬 Akademik Katkılar

Bu çalışma aşağıdaki alanlarda araştırma değeri taşımaktadır:

### Yapay Zekâ

* Heuristik Arama Algoritmaları
* Pekiştirmeli Öğrenme
* Karar Verme Sistemleri

### Akıllı Ulaşım Sistemleri

* Son-Mil Teslimat
* Akıllı Şehir Lojistiği
* Trafik Farkındalıklı Navigasyon

### Çoklu Ajan Sistemleri

* Görev Paylaşımı
* Merkezi Olmayan Koordinasyon
* Kaynak Kısıtlı Rotalama

### Simülasyon ve Modelleme

* Grid Tabanlı Ortam Tasarımı
* Deneysel Yapay Zekâ Platformları
* Eğitim Amaçlı RL Ortamları

---

# 🏗 Sistem Mimarisi

```text
+---------------------------------------------------+
|             Akıllı Lojistik Simülatörü            |
+---------------------------------------------------+

          Çevre Katmanı
-----------------------------------------------------
- Binalar
- Trafik Bölgeleri
- Teslimat Noktaları
- Şarj İstasyonları
- Depo ve Bitiş Noktası

                    ↓

          Karar Katmanı
-----------------------------------------------------
- A* Yol Planlayıcı
- Q-Learning Ajanı
- Görev Atama Sistemi

                    ↓

          Ajan Katmanı
-----------------------------------------------------
- Kurye 1
- Kurye 2
- Kurye 3

                    ↓

          Görselleştirme
-----------------------------------------------------
- Pygame Arayüzü
- Performans Raporları
- İstatistik Paneli
```

---

# 🌍 Simülasyon Ortamı

| Özellik            | Değer   |
| ------------------ | ------- |
| Harita Boyutu      | 20×20   |
| Bina Kümeleri      | 15      |
| Trafik Bölgeleri   | 16      |
| Teslimat Noktaları | 6       |
| Şarj İstasyonları  | Dinamik |
| Ajan Sayısı        | 1–3     |

Her deney çalıştırıldığında harita yeniden üretilerek farklı senaryolar oluşturulabilmektedir.

Bu yaklaşım öğrenen ajanların farklı çevresel koşullara karşı davranışlarının incelenmesine olanak sağlamaktadır.

---

# 🤖 Kullanılan Yapay Zekâ Yaklaşımları

## 1. A* Algoritması

A* algoritması teslimat hedeflerine ulaşmak için kullanılan deterministik yol planlama yöntemidir.

Değerlendirme fonksiyonu:

```math
f(n)=g(n)+h(n)
```

Burada:

* g(n) : gerçek maliyet
* h(n) : Manhattan mesafesi

olarak tanımlanmaktadır.

Trafik bölgeleri maliyet fonksiyonuna doğrudan etki etmektedir.

### Avantajları

* Hızlı yakınsama
* Kararlı davranış
* Düşük hesaplama maliyeti

### Sınırlılıkları

* Dinamik çevre değişimlerine duyarlılık
* Trafik etkinken optimalite garantisinin zayıflaması

---

## 2. Q-Öğrenmesi (Q-Learning)

Pekiştirmeli öğrenme modunda ajanlar deneyim yoluyla öğrenmektedir.

Durum uzayı:

```python
(pos, hedef_konumu)
```

Aksiyon kümesi:

```text
Yukarı
Aşağı
Sağ
Sol
```

Öğrenme kuralı:

```math
Q(s,a) ← Q(s,a)
+ α[r + γmaxQ(s',a') - Q(s,a)]
```

Bu yapı sayesinde ajanlar zaman içerisinde daha kısa ve daha verimli rotalar öğrenebilmektedir.

---

# 🔋 Enerji ve Batarya Modeli

Sistemde üç farklı araç profili bulunmaktadır.

| Araç       | Hız   | Enerji Tüketimi |
| ---------- | ----- | --------------- |
| Bisiklet   | 0.65× | 0.50×           |
| Motosiklet | 1.00× | 1.00×           |
| Araba      | 1.60× | 1.80×           |

Batarya tüketimi trafik yoğunluğuna bağlı olarak değişmektedir.

Bu durum rotalama problemini klasik en kısa yol probleminden çıkarıp kaynak kısıtlı optimizasyon problemine dönüştürmektedir.

---

# 👥 Çoklu Ajan Koordinasyonu

Sistem eşzamanlı olarak üç kurye desteklemektedir.

Her ajan:

1. Ziyaret edilmemiş hedefleri inceler.
2. En yakın hedefi seçer.
3. Hedefi kilitler (Claim).
4. Teslimatı tamamlar.

Bu yöntem:

* Basit
* Ölçeklenebilir
* Hesaplama açısından ucuz

olmasına rağmen küresel optimum garanti etmemektedir.

---

# 📈 Performans Analizi

Simülasyon boyunca aşağıdaki ölçümler kaydedilmektedir:

* Toplam Teslimat Sayısı
* Geçen Süre
* Toplam Mesafe
* Ödül
* Ceza
* Net Kâr
* Teslimat Başına Performans
* Kümülatif Ödül Eğrisi

Bu metrikler farklı algoritmaların karşılaştırılmasını mümkün kılmaktadır.

---

# 📚 Gelecek Araştırma Yönleri

Proje aşağıdaki araştırma alanlarına genişletilmeye uygundur:

### Yol Planlama

* D* Lite
* Theta*
* Jump Point Search (JPS)

### Pekiştirmeli Öğrenme

* Deep Q-Network (DQN)
* Double DQN
* PPO
* Multi-Agent Reinforcement Learning (MARL)

### Görev Dağıtımı

* Macar Algoritması (Hungarian Algorithm)
* K-Means Tabanlı Görev Kümeleme
* Merkezi Görev Planlayıcılar

### Akıllı Şehir Uygulamaları

* Gerçek zamanlı trafik verileri
* IoT entegrasyonu
* Dijital İkiz (Digital Twin) sistemleri

---

# 🛠 Kullanılan Teknolojiler

* Python
* Pygame
* NumPy
* Heapq
* Reinforcement Learning
* A* Search
* Multi-Agent Systems

---

# 🚀 Kurulum

```bash
git clone https://github.com/kullanici_adi/akilli-lojistik-simulatoru.git

cd akilli-lojistik-simulatoru

pip install -r requirements.txt

python simulator.py
```

---

# 👨‍🎓 Akademik Amaç

Bu proje;

* Yüksek Lisans Araştırmaları
* Doktora Çalışmaları
* Yapay Zekâ Ders Projeleri
* Akıllı Ulaşım Sistemleri Araştırmaları
* Pekiştirmeli Öğrenme Deneyleri
* Çoklu Ajan Sistemleri Çalışmaları

için deneysel bir araştırma altyapısı sunmayı amaçlamaktadır.

---

# 📖 Kaynakça

Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*. IEEE Transactions on Systems Science and Cybernetics.

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction (2nd Edition)*. MIT Press.

---

# 👤 Geliştirici

**Ousman Moussa Mahamat**

Bilgisayar Mühendisi
Yapay Zekâ • Pekiştirmeli Öğrenme • Çoklu Ajan Sistemleri • Akıllı Ulaşım Sistemleri

---

> Bu proje akademik araştırma, eğitim ve bilimsel çalışmalar amacıyla geliştirilmiştir.
