# 🚀 Paket Teslimat Rotası (Dinamik TSP)

> Python ve Pygame ile geliştirilmiş, A* yol bulma algoritması ve greedy hedef seçimi kullanan gerçek zamanlı kurye teslimat simülasyonu.

---

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Algoritmalar](#-algoritmalar)
- [Performans Metrikleri ve Ödül–Ceza Mekanizması](#-performans-metrikleri-ve-ödülceza-mekanizması)
- [Arayüz ve Görsel Tasarım](#-arayüz-ve-görsel-tasarım)
- [Davranışsal Analiz](#-davranışsal-analiz)
- [Tartışma ve Eleştiriler](#-tartışma-ve-eleştiriler)
- [Geliştirme Önerileri](#-geliştirme-önerileri)
- [Kurulum ve Kullanım](#-kurulum-ve-kullanım)
- [Temel Fonksiyonlar](#-temel-fonksiyonlar)
- [Sonuç](#-sonuç)

---

## 🌐 Genel Bakış

**Akıllı Lojistik Simülatörü**, modern lojistik ve dağıtım problemlerini simüle etmek amacıyla geliştirilmiş bir Python/Pygame uygulamasıdır. Sistem;

- **20×20 ızgara** ortamında rastgele engeller ve çoklu teslimat noktaları içerir
- **A\*** algoritması ile teslimatlar için en kısa yolları belirler
- **Greedy (Nearest Neighbor)** yaklaşımıyla hedef sıralaması yapar
- **Ödül–Ceza mekanizması** ile performans değerlendirmesi gerçekleştirir
- Süre, mesafe, puan, ceza ve net kâr gibi **anlık metrikler** sunar

> Bu sistem, pratik bir A\* demonstrasyonu ve eğitim amaçlı bir simülasyon platformudur. Pekiştirmeli Öğrenme (RL) ortamına dönüştürülmeye uygun bir altyapı sunar.

---

## 🏗️ Sistem Mimarisi

### Çevre Modülü

Ortam, sabit büyüklükte **(20×20)** bir ızgaradır. Her hücre ya `yol (0)` ya da `bina/engel (-1)` olarak tanımlanır.

- `grid` matrisi hücre bilgisini tutar
- `_gen_buildings()` fonksiyonu başlangıçta **15 rastgele bina grubu** yerleştirir
- Her bina hücresinin rengi `building_colors` sözlüğünde saklanır
- Simülasyon süresince çevre **statik** kalır (engeller değişmez)

### Hedefler

Teslimat noktaları `target_data` listesinde tutulur. Her hedef için:

| Alan | Açıklama |
|------|----------|
| `pos` | Izgara üzerindeki konum |
| `icon` | Simge türü (havaalanı, hastane, AVM vb.) |
| `color` | Renk bilgisi |
| `visited` | Ziyaret edildi bilgisi |
| `visit_time` | Teslimat zamanı |

Ortam her sıfırlandığında (`reset_env`) belirli sayıda hedef (varsayılan: **6**) rastgele boş hücrelere yerleştirilir.

### Kuryenin Durumu

| Değişken | Açıklama |
|----------|----------|
| `pos` | Kuryenin mevcut ızgara konumu (depodan başlar) |
| `path` | Planlı yolun hücre listesi |
| `trail` | Son 30 konumun izi (kuyruk) |
| `heading` | Son hareket yönü vektörü |
| `time` | Toplam adım sayısı (mesafe) |
| `elapsed_s` | Geçen süre (saniye) |
| `score` | Toplam ödül |
| `penalties` | Toplam ceza |
| `delivery_log` | Gerçekleşen teslimat kayıtları |

### Ana Döngü Akış Diyagramı

```
Simülasyon Başlangıcı
        │
        ▼
   Ortamı Sıfırla
        │
        ▼
┌─ Ziyaret Edilmemiş Hedef Var mı? ─┐
│               │                   │
│              Evet                Hayır
│               │                   │
│               ▼                   ▼
│     Rota Planlama (A*)        Epizodu Bitir
│               │                   │
│               ▼                   ▼
│     Güncellemeleri Yap      Sonuç Grafiği Göster
│               │
│       ┌───────┴───────┐
│       │               │
│     Hayır           Evet
│       │               │
│  Hareket Devam   Teslimat İşareti
│       │          ve Puan Hesaplama
│       └───────────────┘
│               │
└───────────────┘
```

---

## 🔍 Algoritmalar

### A\* Yol Bulma Algoritması

Simülasyonun çekirdeğinde **A\*** algoritması yer alır. `a_star(start, goal)` fonksiyonu ile uygulanır.

**Değerlendirme Fonksiyonu:**

```
f(n) = g(n) + h(n)
```

- `g(n)` → Başlangıçtan mevcut düğüme gerçek maliyet
- `h(n)` → Manhattan mesafesi tahmini (heuristik)

**Manhattan Mesafesi:**

```python
h = abs(n[0] - goal[0]) + abs(n[1] - goal[1])
```

Bu ızgara probleminde Manhattan metriği **admissible (yanıltıcı olmayan)** bir tahmin yöntemidir; çünkü her adımdaki maliyet `1` olarak sabittir ve tahmin gerçek en küçük maliyeti asla geçmez. Bu şart altında **A\* en kısa yolu bulmayı garanti eder**.

**Kod Karşılığı:**

```python
f = tg + abs(nb[0] - goal[0]) + abs(nb[1] - goal[1])
```

**Özellikler:**

| Özellik | Değer |
|---------|-------|
| Tamlık (Completeness) | ✅ Evet |
| Optimalite | ✅ Evet (admissible heuristik ile) |
| Zaman Karmaşıklığı | O(b^d) — küçük gridde makul |
| Heuristik | Manhattan Mesafesi |

> 💡 **Not:** 1968'de Hart, Nilsson ve Raphael tarafından geliştirilen A\*, Dijkstra'nın tam aramasına göre keşfedilecek düğüm sayısını önemli ölçüde azaltır.

**Sınırlamalar:**
- Rakım değişimi veya köşe geçiş ücretlerini hesaba katmaz
- Dinamik engellere uyum sağlayamaz
- Çok büyük haritalarda hesap yükü artabilir

---

### Hedef Seçimi: Greedy Nearest Neighbor

Her adımda ziyaret edilmemiş hedefler arasından **en yakın olanı** seçilir:

```python
next_target = min(unvisited, key=lambda t: distance(cur_pos, t))
```

**Karşılaştırma Tablosu:**

| Özellik | Nearest Neighbor | TSP Tam Çözümü |
|---------|-----------------|----------------|
| Uygulama kolaylığı | ✅ Kolay | ❌ Zor |
| Hesap karmaşıklığı | O(N) | NP-Zor |
| Global optimalite | ❌ Garanti yok | ✅ Optimal |
| Gerçek zamanlı kullanım | ✅ Uygun | ⚠️ Sınırlı |

> ⚠️ Nearest-neighbor yöntemi, ilk etapta seçilen yakın hedef genel rotayı uzatabilir. Her büyüklükte `r` için optimalden `r` kat daha maliyetli turlar üretme riski vardır.

---

### Bileşen Karşılaştırma Tablosu

| Bileşen | Mevcut Yaklaşım | Artıları | Eksileri | Önerilen Alternatif | Beklenen Etki |
|---------|----------------|----------|----------|---------------------|--------------|
| Hedef Seçimi | Nearest Neighbor | Kolay, hızlı | Global optimal değil | TSP yaklaşımı | Tur maliyetinde iyileşme |
| Rota Planlama | A* (Manhattan) | En kısa yol garantisi | Dinamik engellere uyum yok | Theta* / RRT* | Daha doğal yollar |
| Ödül Yapısı | Zaman-ödül, adım-ceza | Anlaşılır, hızlı teslimat teşviki | Statik formül, öğrenme yok | Reward Shaping | RL eğitimi hızlanır |
| Araç Sayısı | Tek kurye | Sade tasarım | Tüm yük tek ajana | Çoklu kurye (multi-agent) | İşbirliği senaryoları |
| Çevre Dinamiği | Statik engeller | Deterministik | Gerçekçi değil | Dinamik engeller, trafik | Daha zorlu test ortamı |

---

## 📊 Performans Metrikleri ve Ödül–Ceza Mekanizması

### Takip Edilen Metrikler

- **Geçen Süre** (`elapsed_s`) — Gerçek zaman (saniye)
- **Mesafe** (`time`) — Toplam adım sayısı
- **Toplam Ödül** (`score`)
- **Toplam Ceza** (`penalties`)
- **Net Kâr** = Ödül – Ceza

### Ödül Hesaplama

Bir hedefe varıldığında:

```python
bonus = max(50, 300 - 2 * elapsed_s)
```

| Teslimat Süresi | Bonus Puanı |
|----------------|------------|
| Çok hızlı | ~300 puan |
| Orta | ~150 puan |
| Çok geç | 50 puan (taban) |

### Ceza Hesaplama

Her adımda hız seviyesine göre ceza eklenir:

| Hız Seviyesi | Adım Başı Ceza |
|-------------|----------------|
| Yavaş | 0.4 puan |
| Normal | 0.8 puan |
| Hızlı | 1.4 puan |

### Performans Grafiği Örneği

```python
import matplotlib.pyplot as plt

logs = [entry['bonus'] for entry in delivery_log]
plt.bar(range(1, len(logs) + 1), logs, color='g')
plt.xlabel('Teslimat Numarası')
plt.ylabel('Bonus Puanı')
plt.title('Teslimat Başı Ödül Dağılımı')
plt.show()
```

> 📈 Epizod sonunda **GRAFİK** butonuna basarak teslimat bonuslarını, kümülatif ödül zaman çizgisini ve net sonuçları görselleştirebilirsiniz.

---

## 🎨 Arayüz ve Görsel Tasarım

### Harita Çizimi

- Her hücre bir **kare** olarak çizilir
- Bina hücreleri için **gradient ton geçişi** uygulanır
- Yol hücreleri için düz renk kullanılır
- Binaların pencereleri rastgele desenlerle çizilir

### Semantik Simgeler

| Hedef Tipi | Simge |
|-----------|-------|
| Havaalanı | ✈️ Uçak silueti |
| Hastane | ➕ Haç işareti |
| AVM | 🏪 Mağaza simgesi |
| Fabrika | 🏭 Baca simgesi |

### Animasyon Efektleri

- **Nabız Efekti** — Teslimat hedefleri sürekli dalgalanır
- **İz Efekti (Trail)** — Kuryenin son 30 konumu çizilir
- **Depo Pulsatörü** — Depo noktası etrafında animasyonlu halka

### Kullanıcı Etkileşimi

| Kontrol | Fonksiyon |
|---------|-----------|
| `S` | Simülasyonu başlat/durdur |
| `R` | Simülasyonu sıfırla |
| `1` | Yavaş hız |
| `2` | Normal hız |
| `3` | Hızlı hız |
| `Fare` | Buton tıklama, grafik açma |

---

## 📈 Davranışsal Analiz

Simülasyon çalıştırıldığında ajanın davranışı:

1. **Depo noktası** seçilir, en yakın hedeften başlanır
2. Planlanan A\* yolu üzerinde **adım adım** hareket edilir
3. Hedefe varıldığında **bonus kazanılır**, hedef işaretlenir
4. **Bir sonraki en yakın hedefe** rota çizilir
5. Tüm hedefler ziyaret edilene kadar devam eder

**Gözlemler:**

- Kısa sürede yapılan teslimatlarda ~300 bonus alınır
- Geç kalındığında taban değer olan +50 puana düşülür
- Hız seviyesine göre net kâr pozitif veya negatif olabilir
- Sistem **deterministik** davranır — aynı başlangıç koşullarıyla hep aynı rota oluşur

---

## 🔎 Tartışma ve Eleştiriler

### Güçlü Yönler

- A\*'ın **garantili en kısa yol bulma** özelliği
- Deterministik ve öngörülebilir ajan davranışı
- Zengin görsel arayüz ve anlık metrik gösterimi

### Sınırlılıklar

- A\* **adım-adım rota planladığı** için çok hedefli optimizasyon tam çözülmez
- Manhattan heuristi **dönüş maliyetleri** gibi gerçek dünya kısıtlarını içermez
- Nearest-neighbor yaklaşımı **küresel rotayı optimize etmez**
- Çevre statik — **trafik, hareketli engeller** mevcut değil
- **Tek kurye** kısıtı; çok ajanli senaryolar desteklenmiyor
- RL öğrenmesi içermez; politika elle belirlenmiştir

### RL Bağlamında Değerlendirme

Sutton ve Barto'nun tanımına göre, bir RL ajanının tek amacı toplam ödülü maksimize etmektir. Mevcut sistem bu tanıma uygun bir ortam sunar; ancak ödül sinyali **dense** (adım başına ceza) ve **sparse** (hedef bonus) karmasıdır. RL entegrasyonu için ödül şekillendirme (reward shaping) gerekebilir.

---

## 🛠️ Geliştirme Önerileri

### 1. Pekiştirmeli Öğrenme Entegrasyonu

Simülasyon bir RL ortamına dönüştürülebilir:

```python
# Pseudo-kod: Q-Öğrenme Örneği
from collections import defaultdict
import numpy as np

Q = defaultdict(lambda: np.zeros(num_actions))

for episode in range(N):
    state = env.reset()
    done = False
    while not done:
        action = choose_action_epsilon_greedy(Q, state)
        next_state, reward, done, _ = env.step(action)
        best_next = np.max(Q[next_state])
        Q[state][action] += alpha * (reward + gamma * best_next - Q[state][action])
        state = next_state
```

**Durum Uzayı:** Kuryenin konumu + bitişik engel bilgisi + kalan hedeflerin pozisyonları  
**Aksiyonlar:** Dört hareket yönü  
**Ödül:** Mevcut +bonus ve -ceza sinyalleri (veya şekillendirilmiş hali)

### 2. Çoklu Kurye (Multi-Agent) Simülasyonu

- Her kurye farklı hedef grubuna atanabilir
- **Hungarian Algoritması** ile görev dağıtımı yapılabilir
- Çoklu ajanlı RL veya merkezi optimizasyon algoritmaları entegre edilebilir

### 3. Dinamik Engeller ve Trafik

- Hareketli araçlar yolları kesebilir
- **D\* Lite** algoritması ile canlı yeniden planlama yapılabilir
- Trafik ışıkları veya hız değişimleri gerçekçiliği artırabilir

### 4. İyileştirilmiş Heuristikler ve Yol Yumuşatma

```python
# Yol Yumuşatma Örneği
path = a_star(start, goal)
smooth_path = [path[0]]

for pt in path[1:]:
    if not colinear(smooth_path[-1], smooth_path[-2], pt):
        smooth_path.append(pt)

smooth_path.append(path[-1])
```

Bu sayede 90° dönüşler azaltılarak daha gerçekçi bir sürüş deneyimi elde edilir.

Alternatif algoritmalar: **Theta\***, **Lazy Theta\***, **JPS (Jump Point Search)**

### 5. Performans Optimizasyonu

- `pygame.Surface` önbellekleme ile rendering hızlandırılabilir
- Statik arka plan için bitmap önbelleği kullanılabilir
- Büyük haritalarda **JPS** veya **PRM/RRT** değerlendirilebilir

---

## ⚙️ Kurulum ve Kullanım

### Gereksinimler

```bash
python -m venv venv
source venv/bin/activate
pip install pygame matplotlib numpy
```

### Çalıştırma

```bash
python3 simulator.py
```

### Kontroller

```
S    →  Simülasyonu Başlat / Durdur
R    →  Simülasyonu Sıfırla
1    →  Yavaş Hız
2    →  Normal Hız
3    →  Hızlı Hız
```

---

## 📁 Temel Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `reset_env()` | Ortam ve hedefleri rastgele oluşturur, ajan durumu ve metrikleri sıfırlar |
| `a_star(start, goal)` | Verilen başlangıç ve hedef koordinatları için A\* uygular, yol listesi döndürür |
| `update_logic()` | Her zaman adımında ajanı hareket ettirir, zamanı/cezayı günceller, teslimatı kaydeder |
| `draw()` | Ana çizim fonksiyonu |
| `_draw_map()` | Haritayı, ajanı ve hedef ikonlarını çizer |
| `_draw_panel()` | Kontrol panelini ve metrikleri Pygame ile çizer |
| `_draw_graph_overlay()` | Epizod sonu performans grafiğini gösterir |
| `run()` | Pygame event döngüsünü yönetir, kullanıcı girdi ve simülasyon adımlarını kontrol eder |

---

## 📚 Kaynaklar

- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.*
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction.*
- Erdal T., Aytu O. (2016). *K-En Yakın Komşu Algoritması Parametrelerinin Sınıflandırma Performansı Üzerine Etkisinin İncelenmesi*

---

## 🔚 Sonuç

Akıllı Lojistik Simülatörü, A\* algoritmasının optimalite garantisi, uygun heuristiği (Manhattan mesafesi) sayesinde geçerli bir yol planlaması sunar. Ödül-ceza yapısı teslimat süresi ve hız odaklı motivasyon sağlar. Önerilen geliştirmeler (RL entegrasyonu, çoklu ajanlar, dinamik ortamlar, gelişmiş heuristikler) ile sistem; endüstri veya araştırma uygulamaları için güçlü bir test platformuna dönüştürülebilir.

---

<div align="center">
  <sub><b>Python & Pygame ile geliştirilmiştir • Akıllı Lojistik Simülatörü</b></sub>
</div>





##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 📸 Görsel 1
![Ekran](assets/images/sim_1.png)
## 📊 Grafik 1
![Ekran](assets/images/grafik_1.png)
## 🔁 Gif 1
[Gif İzle](assets/videos/sim_vid_1.gif)
## 🎥 Demo Video 1
[Demo Videoyu İzle](assets/videos/sim_vid_1.mp4)

##----------------------------------------------
## 📸 Görsel 2
![Ekran](assets/images/sim_2.png)
## 📊 Grafik 2
![Ekran](assets/images/grafik_2.png)
## 🔁 Gif 2
[Gif İzle](assets/videos/sim_vid_2.gif)
## 🎥 Demo Video 2
[Demo Videoyu İzle](assets/videos/sim_vid_2.mp4)

##----------------------------------------------
## 📸 Görsel 3
![Ekran](assets/images/sim_3.png)
## 📊 Grafik 3
![Ekran](assets/images/grafik_3.png)
## 🔁 Gif 3
[Gif İzle](assets/videos/sim_vid_3.gif)
## 🎥 Demo Video 3
[Demo Videoyu İzle](assets/videos/sim_vid_3.mp4)

##----------------------------------------------
## 📸 Görsel 4
![Ekran](assets/images/sim_4.png)
## 📊 Grafik 4
![Ekran](assets/images/grafik_4.png)
## 🔁 Gif 4
[Gif İzle](assets/videos/sim_vid_4.gif)
## 🎥 Demo Video 4
[Demo Videoyu İzle](assets/videos/sim_vid_4.mp4)