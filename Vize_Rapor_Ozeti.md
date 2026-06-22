# Akıllı Lojistik ve Rota Optimizasyonu Simülasyonu Teknik Analiz Raporu

## Özet
Bu rapor, Python/Pygame tabanlı **Akıllı Lojistik Simülatörü** yazılımının sistem mimarisini, operasyonel algoritmalarını ve performans metriklerini incelemektedir. Çalışma kapsamında, $20 \times 20$ ızgara (grid) tabanlı bir ortamda dinamik hedef takibi yapan bir kurye ajanının davranışı analiz edilmiştir. En kısa yol planlaması için **A\*** algoritması, hedef sıralaması için **Greedy Nearest Neighbor (GNN)** yaklaşımı ve performans değerlendirmesi için zaman tabanlı bir **Ödül-Ceza Mekanizması** entegre edilmiştir. Bulgular, sistemin deterministik senaryolarda yüksek doğrulukla çalıştığını, ancak global optimizasyon ve dinamik çevre koşulları noktasında geliştirme alanları bulunduğunu göstermektedir.

---

## 1. Giriş
Lojistik operasyonlarında verimlilik, Gezgin Satıcı Problemi (TSP) ve Araç Rotalama Problemi (VRP) gibi NP-Zor (NP-Hard) problemlerin çözümüne dayanır. Bu simülasyon, söz konusu karmaşık problemleri kontrol edilebilir bir ızgara evreninde modellemek amacıyla geliştirilmiştir. Raporun ilerleyen bölümlerinde, sistemin teknik bileşenleri, kullanılan sezgisel (heuristic) yöntemlerin matematiksel dayanakları ve gelecekteki Pekiştirmeli Öğrenme (RL) entegrasyonu potansiyeli ele alınacaktır.

---

## 2. Sistem Mimarisi ve Operasyonel Modüller

### 2.1 Çevre ve Nesne Modelleme
Sistem, statik engellerin (binalar) ve dinamik hedeflerin bulunduğu iki boyutlu bir matris üzerinde kurgulanmıştır:
* **Izgara Dünyası:** $20 \times 20$ boyutlarında, hücre bazlı bir yapıdır. Hücre değerleri $0$ (yol) ve $-1$ (engel) olarak kodlanmıştır.
* **Hedef Yönetimi:** `target_data` yapısı altında; koordinat, ikon türü ve ziyaret durumu gibi öznitelikleri barındıran asenkron bir listedir.
* **Ajan Durumu:** Kurye ajanı; mevcut koordinat, yönelim (heading), geçmiş iz (trail) ve birikimli maliyet (distance/time) verilerini anlık olarak günceller.

### 2.2 İş Akışı (Flowchart)
Simülasyonun yaşam döngüsü aşağıdaki mantıksal silsileyi takip eder:



---

## 3. Algoritmik Analiz

### 3.1 A* Yol Planlaması ve Heuristik Seçimi
Kurye ajanının iki nokta arasındaki en kısa yolu bulması için A* algoritması kullanılmıştır. Algoritmanın başarı kriteri, maliyet fonksiyonunun doğruluğuna bağlıdır:

$$f(n) = g(n) + h(n)$$

Burada:
* $g(n)$: Başlangıç düğümünden mevcut $n$ düğümüne ulaşmak için gereken gerçek maliyet.
* $h(n)$: Mevcut düğümden hedefe olan tahmini uzaklık (Manhattan Mesafesi).

**Analiz:** Izgara üzerinde diyagonal hareketin yasak olduğu bu simülasyonda, Manhattan mesafesi ($|x_1-x_2| + |y_1-y_2|$) "admissible" (uygun) bir heuristiktir. Bu durum, A*'nın her zaman teorik olarak en kısa yolu bulmasını garanti eder.

### 3.2 Hedef Seçimi: Yakın Komşu (Nearest Neighbor)
Çoklu teslimat senaryosunda hedef sıralaması "Greedy" (açgözlü) bir yaklaşımla belirlenir. Ajan, her aşamada Öklid veya Manhattan metriğine göre kendisine en yakın olan "ziyaret edilmemiş" hedefe yönelir.

> **Kritik Not:** Yakın komşu algoritması hesaplama açısından $O(N)$ karmaşıklığı ile çok hızlıdır; ancak TSP bağlamında global optimumu garanti etmez. Kötü senaryolarda toplam rota uzunluğu, optimal çözümün $\approx 1.5$ ila $2$ katı kadar sapma gösterebilir.

---

## 4. Performans Metrikleri ve Ekonomik Model
Sistem, bir kurye operasyonunun kârlılığını şu formülle simüle eder:

### 4.1 Ödül Fonksiyonu
Teslimat başarısı, zamana duyarlı bir bonus ile ödüllendirilir:
$$Bonus = \max(50, 300 - 2 \cdot t_{gecen})$$

### 4.2 Ceza ve Net Kâr
Her hareket adımı, seçilen hız seviyesine ($v$) bağlı olarak bir işletme maliyeti (ceza) doğurur:
$$Net Kâr = \sum Bonus - \sum (Adım \times v_{maliyet})$$

Bu model, ajanı (veya ileride eğitilecek RL modelini) **hız vs. enerji tüketimi** dengesini kurmaya zorlar.

---

## 5. Karşılaştırmalı Analiz ve Alternatif Yaklaşımlar

| Bileşen | Mevcut Durum | Profesyonel Öneri | Beklenen Kazanım |
| :--- | :--- | :--- | :--- |
| **Rota Opt.** | Nearest Neighbor | Ant Colony / Genetic Alg. | Toplam mesafede %15-20 kısalma |
| **Yol Bulma** | Standart A* | JPS (Jump Point Search) | Hesaplama süresinde %30 hızlanma |
| **Dinamik Yapı**| Statik Engeller | D* Lite / RRT* | Hareketli trafiğe uyum yeteneği |

---

## 6. Geliştirme Yol Haritası ve Öneriler

### 6.1 Pekiştirmeli Öğrenme (RL) Entegrasyonu
Simülasyonun bir Markov Karar Süreci (MDP) olarak modellenmesi önerilir.
* **State (Durum):** Kurye konumu + Hedeflerin maskesi + Yerel engel haritası.
* **Action (Eylem):** Yukarı, Aşağı, Sağ, Sol.
* **Reward (Ödül):** Mevcut ödül-ceza mekanizmasının normalleştirilmiş hali.

### 6.2 Yol Yumuşatma (Path Smoothing)
Mevcut $90^\circ$ dönüşler, fiziksel bir aracın momentumuyla uyumsuzdur. A* tarafından üretilen düğüm noktaları arasına **B-Spline** veya **Bezier Eğrileri** eklenerek daha akışkan bir sürüş profili oluşturulabilir.

---

## 7. Sonuç
Bu teknik raporun konusu olan Akıllı Lojistik Simülatörü; algoritma tasarımı, görselleştirme ve veri takibi açısından sağlam bir temel sunmaktadır. A* entegrasyonu yol planlama ihtiyacını eksiksiz karşılarken, görsel arayüz kullanıcı deneyimini (UX) ön planda tutmaktadır. Global rota optimizasyonu ve dinamik engel yönetimi gibi alanlarda yapılacak güncellemelerle, yazılım akademik bir çalışma seviyesinden endüstriyel bir test simülasyonuna dönüştürülebilir.

---
**Raporu Hazırlayan:** OUSMAN MOUSSA MAHAMAT  
**Tarih:** 24 Nisan 2026  
**Teknoloji Yığını:** Python, Pygame, A* Search, Greedy Heuristics