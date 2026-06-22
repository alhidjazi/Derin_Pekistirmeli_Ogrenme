# 🚀 Akıllı Lojistik Simülatörü (Multi-Agent A* / RL)

> Python ve Pygame ile geliştirilmiş; trafik, batarya, şarj istasyonları, çoklu kurye ve hibrit A\*/Pekiştirmeli Öğrenme (RL) destekli gerçek zamanlı teslimat simülasyonu.

---

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Araç ve Batarya Sistemi](#-araç-ve-batarya-sistemi)
- [Algoritmalar](#-algoritmalar)
- [Çoklu Ajan (Multi-Agent) Mantığı](#-çoklu-ajan-multi-agent-mantığı)
- [Ödül–Ceza Mekanizması ve Metrikler](#-ödülceza-mekanizması-ve-metrikler)
- [Arayüz ve Görsel Tasarım](#-arayüz-ve-görsel-tasarım)
- [Kullanıcı Etkileşimi](#-kullanıcı-etkileşimi)
- [Davranışsal Analiz](#-davranışsal-analiz)
- [Tartışma ve Eleştiriler](#-tartışma-ve-eleştiriler)
- [Geliştirme Önerileri](#-geliştirme-önerileri)
- [Kurulum ve Kullanım](#-kurulum-ve-kullanım)
- [Temel Fonksiyonlar](#-temel-fonksiyonlar)
- [Sonuç](#-sonuç)

---

## 🌐 Genel Bakış

**Akıllı Lojistik Simülatörü**, klasik tek-ajanlı A\* demolarının ötesine geçerek gerçekçi bir şehir içi teslimat senaryosunu simüle eder. Sistem;

- **20×20 ızgara** üzerinde rastgele bina blokları, **trafik bölgeleri** ve **şarj istasyonları** içerir
- **1 ile 3 arasında** eşzamanlı çalışan kurye (ajan) destekler
- Her kurye için **Motosiklet / Bisiklet / Araba** olmak üzere üç farklı araç profili sunar (hız ve batarya tüketimi farklıdır)
- **Sınırlı batarya** mekaniği ile kuryelerin şarj istasyonlarını kullanmasını zorunlu kılar
- İki farklı karar verme modu sunar: **A\*** (deterministik, optimal yol) ve **RL** (Q-learning ile öğrenen kurye)
- Opsiyonel olarak özel **Depo** ve **Bitiş Noktası** seçimine izin verir
- Ödül–ceza mekanizmasıyla performansı puanlar ve epizod sonunda **grafik raporu** üretir

> Bu sistem, klasik yol bulma algoritmalarını pekiştirmeli öğrenme ile karşılaştırmalı olarak gözlemlemeye uygun, etkileşimli bir eğitim/araştırma platformudur.

---

## 🏗️ Sistem Mimarisi

### Çevre Modülü

Ortam, sabit büyüklükte **(20×20)** bir ızgaradır. Her hücre `yol (0)` veya `bina/engel (-1)` olarak tanımlanır.

- `grid` matrisi hücre tipini tutar
- `_gen_buildings()` fonksiyonu başlangıçta **15 rastgele bina grubu** (1–3 hücre genişlik, 1–2 hücre yükseklik) yerleştirir
- Her bina bloğu için gradyan renk çifti `building_colors` sözlüğünde saklanır ve pencere dokusu rastgele üretilir
- `traffic` sözlüğü, yol hücrelerinden rastgele **16 adedini** trafik bölgesi olarak işaretler; her trafik hücresi **2.0×, 2.5× veya 3.0×** maliyet/tüketim çarpanı taşır
- `charge_stations` listesi, yol üzerinde rastgele **3 adet** şarj istasyonu konumlar; bir kurye bu hücreye girdiğinde bataryası **+9 birim** artar (kapasiteyi aşmayacak şekilde)

### Hedefler (Teslimat Noktaları)

Teslimat noktaları `target_data` listesinde tutulur. `LOCATION_DEFS` havuzundan rastgele seçilen lokasyon tipleri kullanılır (AVM, Teknopark, Hastane, Liman Deposu, Üniversite, Market, Havalimanı, Sanayi Bölgesi).

| Alan | Açıklama |
|------|----------|
| `pos` | Izgara üzerindeki konum |
| `name` / `icon` / `color` | Lokasyon adı, simge türü ve rengi |
| `visited` / `visit_time` | Ziyaret durumu ve zamanı |
| `claimed_by` | Hedefi şu an hangi ajanın hedeflediği (çoklu ajan çakışmasını önler) |

Varsayılan olarak her sıfırlamada (`reset_env`) **6 hedef** rastgele boş hücrelere yerleştirilir.

### Depo ve Bitiş Noktası

- `depot`: Tüm kuryelerin başlangıç konumu (varsayılan `(0,0)`), harita üzerinde tıklanarak değiştirilebilir
- `end_point`: Tüm teslimatlar tamamlandıktan sonra kuryelerin yönlendirildiği opsiyonel bitiş noktası; tanımlı değilse epizod, son teslimatla birlikte biter

### Kurye (Ajan) Durumu

Her ajan bir sözlük olarak modellenir:

| Değişken | Açıklama |
|----------|----------|
| `pos` / `path` / `trail` / `heading` | Konum, planlı A\* yolu, son 30 konumun izi, hareket yönü |
| `battery` / `battery_capacity` | Anlık ve maksimum batarya seviyesi |
| `vehicle_key` / `color` | Araç tipi ve görsel renk kimliği |
| `status` | `idle` / `moving` / `to_end` / `done` / `stranded` |
| `target` | Şu anda gidilen hedef (teslimat veya bitiş noktası) |

Genel simülasyon seviyesinde tutulan değişkenler: `time` (toplam adım), `elapsed_s` (geçen süre), `score`, `penalties`, `delivery_log`.

### Ana Döngü Akış Diyagramı

```
Simülasyon Başlangıcı
        │
        ▼
   Ortamı Sıfırla (grid, hedefler, trafik, şarj, ajanlar)
        │
        ▼
┌─ Her Ajan İçin: Bataryası Var mı? ─┐
│            │                       │
│           Evet                   Hayır
│            │                       │
│            ▼                       ▼
│  Hedef Atanmış mı? (claim)     Ajan "stranded"
│            │                  (hedefi serbest bırakılır)
│            ▼
│  Mod = A* ise → a_star() ile yol
│  Mod = RL ise → ε-greedy Q-tablosu adımı
│            │
│            ▼
│     Bir Hücre İlerle (trafik çarpanlı maliyet/tüketim)
│            │
│            ▼
│   Şarj İstasyonunda mı? → Bataryayı Doldur
│            │
│            ▼
│   Hedefe Ulaşıldı mı? → Puanla, İşaretle, Yeni Hedef Ata
└────────────┴───────────────────────┘
        │
        ▼
Tüm Hedefler Bitti + Tüm Ajanlar done/stranded + Bitiş Noktasına Ulaşıldı mı?
        │
        ▼
   Epizodu Bitir → Sonuç Grafiğini Aç
```

---

## 🔋 Araç ve Batarya Sistemi

Üç araç profili `VEHICLES` sözlüğünde tanımlıdır; her biri farklı bir **hız çarpanı** ve **batarya tüketim çarpanı** taşır:

| Araç | Hız Çarpanı | Tüketim Çarpanı | Karakteristik |
|------|------------|------------------|----------------|
| 🏍️ Motosiklet | 1.0× | 1.0× | Dengeli, varsayılan profil |
| 🚲 Bisiklet | 0.65× | 0.5× | Yavaş ama düşük tüketim |
| 🚗 Araba | 1.6× | 1.8× | Hızlı ama yüksek tüketim |

Batarya kapasitesi `BATTERY_OPTIONS = [60, 100, 160]` arasından panelden seçilebilir. Her adımda harcanan enerji:

```python
drain = vehicle["drain"] * traffic_multiplier
battery -= drain
```

Batarya **0**'a düştüğünde ajan `stranded` (mahsur) durumuna geçer, üzerine atanmış teslimat hedefi serbest bırakılır (`claimed_by = None`) ve diğer ajanlar tarafından devralınabilir. Şarj istasyonuna giren ajan bataryasını **+9** birim yeniler.

---

## 🔍 Algoritmalar

### A\* Yol Bulma Algoritması (Trafik Maliyetli)

`a_star(start, goal)` fonksiyonu, standart A\*'ı **trafik-ağırlıklı maliyet** ile genişletir:

```
f(n) = g(n) + h(n)
```

- `g(n)` → Başlangıçtan mevcut düğüme kadar **trafik çarpanlarıyla** biriken gerçek maliyet
- `h(n)` → Manhattan mesafesi (heuristik)

```python
cost = traffic.get(neighbor, 1.0)        # trafik hücresinde 1.0 yerine 2.0–3.0
g_new = g[current] + cost
f = g_new + abs(nb[0]-goal[0]) + abs(nb[1]-goal[1])
```

> ⚠️ **Önemli not:** Manhattan mesafesi, adım maliyeti sabit `1` olduğunda admissible'dır. Ancak bu sistemde trafik hücreleri maliyeti `1`'in üzerine çıkardığı için heuristik artık **gerçek maliyetin garanti bir alt sınırı değildir** — pratikte yine de iyi sonuçlar üretir, fakat klasik anlamda "garanti optimal" iddiası trafik aktifken teorik olarak zayıflar. Daha katı bir doğruluk isteniyorse heuristik, ortamdaki minimum hücre maliyetiyle ölçeklendirilmelidir (`h = min_cost * manhattan`).

| Özellik | Değer |
|---------|-------|
| Tamlık (Completeness) | ✅ Evet |
| Optimalite | ⚠️ Trafiksiz haritada evet; trafikli haritada heuristik artık formel olarak admissible değil |
| Zaman Karmaşıklığı | O(b^d) — 20×20 gridde pratikte hızlı |
| Heuristik | Manhattan Mesafesi |

### RL Modu: Q-Learning (Tablo Tabanlı)

`mode_rl` aktif edildiğinde her ajan, `_rl_step()` üzerinden **durum-aksiyon çiftleri** ile öğrenen bir politikayla hareket eder.

- **Durum:** `(pos, target_pos)` çifti
- **Aksiyonlar:** `RL_ACTIONS = [(0,1),(0,-1),(1,0),(-1,0)]` (dört yön)
- **Keşif (epsilon):** Epizod sayısına göre azalan ε-greedy strateji

```python
epsilon = max(0.05, 0.6 - episode_count * 0.03)
```

- **Ödül sinyali:**

```python
reward = 10.0 if hedefe_ulaşıldı else (0.3 if mesafe_azaldı else -0.6) - trafik_cezasi
```

- **Güncelleme (Q-learning, öğrenme oranı α=0.3, indirim γ=0.9):**

```python
Q[s,a] += 0.3 * (reward + 0.9 * max(Q[s', a']) - Q[s,a])
```

Q-tablosu (`self.q_table`) tüm epizodlar arasında **kalıcıdır** (sıfırlanmaz), yani kurye `R` ile harita yeniden üretilse de aynı çalışma oturumunda biriktirdiği deneyimi korur ve epizodlar ilerledikçe rotaları giderek iyileşir.

### Hedef Seçimi: Greedy Nearest Neighbor + Claim Mekanizması

Her ajan, henüz ziyaret edilmemiş ve **başka bir ajan tarafından claim edilmemiş** hedefler arasından en yakınını seçer:

```python
unvisited = [t for t in targets if not t.visited and t.claimed_by in (None, agent.id)]
best = min(unvisited, key=lambda t: distance(agent.pos, t.pos))
best.claimed_by = agent.id
```

Bu mekanizma çoklu ajan senaryosunda iki kuryenin aynı hedefe gitmesini önler; bir ajan mahsur kalırsa (`stranded`) claim'i bırakılır ve hedef yeniden açık hale gelir.

---

## 🤝 Çoklu Ajan (Multi-Agent) Mantığı

- `num_agents` (1–3) panelden döngüsel olarak değiştirilebilir; her ajan kendi rengine (`AGENT_COLORS`), aracına ve bataryasına sahiptir
- Hedefler ajanlar arasında **claim** sistemiyle paylaşılır — merkezi bir atama algoritması (örn. Macar Algoritması) kullanılmaz, greedy + kilitleme yeterli görülmüştür
- Tüm hedefler tükendiğinde, varsa `end_point`'e yönlendirilir; ajan zaten oradaysa veya `end_point` tanımsızsa `done` durumuna geçer
- Epizod, **tüm hedefler ziyaret edilmiş VE tüm ajanlar `done`/`stranded` VE (varsa) bitiş noktasına ulaşılmış** olduğunda sona erer

---

## 📊 Ödül–Ceza Mekanizması ve Metrikler

### Takip Edilen Metrikler

- **Süre** (`elapsed_s`) — gerçek simülasyon saniyesi
- **Mesafe** (`time`) — toplam adım sayısı (tüm ajanlar toplamı)
- **Ödül** (`score`)
- **Ceza** (`penalties`)
- **Net Kâr** = Ödül − Ceza

### Ödül Hesaplama

Bir hedefe ulaşıldığında:

```python
bonus = max(50, 300 - 2 * elapsed_s)
```

| Teslimat Süresi | Bonus Puanı |
|----------------|------------|
| Çok hızlı | ~300 puan |
| Orta | ~150 puan |
| Çok geç | 50 puan (taban) |

### Ceza Hesaplama

Her adımda hız seviyesine **ve trafik çarpanına** bağlı ceza eklenir:

```python
pen = {1: 0.4, 2: 0.8, 3: 1.4}[speed_level] * traffic_multiplier
```

| Hız Seviyesi | Temel Adım Cezası |
|-------------|--------------------|
| Yavaş | 0.4 puan |
| Normal | 0.8 puan |
| Hızlı | 1.4 puan |

> Trafik hücresinden geçilirse ceza ek olarak ×2/×2.5/×3 katlanır.

### Performans Grafiği

Epizod tamamlandığında **GRAFİK** butonu aktif hale gelir ve aşağıdakileri içeren bir overlay açılır:

- Teslimat başına bonus bar grafiği
- Toplam teslimat / süre / mesafe / ödül / ceza / net kâr özeti
- Kümülatif ödülün zaman çizgisi (line chart)

```python
import matplotlib.pyplot as plt

logs = [entry['bonus'] for entry in delivery_log]
plt.bar(range(1, len(logs) + 1), logs, color='g')
plt.xlabel('Teslimat Numarası')
plt.ylabel('Bonus Puanı')
plt.title('Teslimat Başı Ödül Dağılımı')
plt.show()
```

---

## 🎨 Arayüz ve Görsel Tasarım

### Harita Çizimi

- Bina hücreleri gradyan tonlarla, rastgele pencere dokularıyla çizilir
- Trafik hücreleri turuncu/kahverengi yarı saydam katman ve çapraz çizgi desenleriyle vurgulanır
- Şarj istasyonları nabız efektli yıldırım ikonuyla gösterilir
- Depo, animasyonlu yeşil halka ile; bitiş noktası mor bayrak ikonuyla işaretlenir

### Semantik Lokasyon Simgeleri

| Hedef Tipi | Simge |
|-----------|-------|
| Havalimanı | ✈️ Uçak silueti |
| Hastane | ➕ Haç işareti |
| AVM | 🏬 Çatılı mağaza |
| Teknopark | 💻 Cam cepheli ofis |
| Liman Deposu | 📦 Çatılı depo |
| Üniversite | 🏛️ Sütunlu bina |
| Gıda Market | 🛒 Tenteli dükkân |
| Sanayi Bölgesi | 🏭 Bacalı fabrika |

### Animasyon Efektleri

- **Nabız Efekti** — ziyaret edilmemiş hedefler ve şarj istasyonları sürekli dalgalanır
- **İz Efekti (Trail)** — her ajanın son 30 konumu, kendi rengiyle solan bir kuyruk olarak çizilir
- **Batarya Çubuğu** — her ajanın üzerinde anlık batarya yüzdesini gösteren renkli mini bar (yeşil/turuncu/kırmızı eşiklerle)
- **Depo/Bitiş Pulsatörü** — animasyonlu halka efektleri

### Kontrol Paneli (Sağ Panel)

Panel şu bloklardan oluşur: **Kontrol Merkezi** (durum), **Mevcut Hedef**, **Performans Metrikleri** (4 kart), **Net Kâr**, **Ajan & Pil Durumu** (her ajan için satır), **Teslimat Geçmişi** (son 3 kayıt), **Hız Seçici**, **Teslimat Listesi**, **Gelişmiş Ayarlar** (Araç / Pil / Mod / Ajan Sayısı / Depo Seç / Bitiş Seç butonları).

---

## 🕹️ Kullanıcı Etkileşimi

| Kontrol | Fonksiyon |
|---------|-----------|
| `S` / **BAŞLAT** butonu | Simülasyonu başlat/durdur |
| `R` / **SIFIRLA** butonu | Ortamı yeniden rastgele üret |
| `1` / `2` / `3` | Yavaş / Normal / Hızlı hız seviyesi |
| `ESC` | Grafik overlay'ini veya konum seçim modunu kapat |
| **GRAFİK** butonu | Epizod bitince sonuç grafiğini aç/kapat |
| **ARAÇ** butonu | Motosiklet → Bisiklet → Araba arasında döngü |
| **PİL** butonu | 60 → 100 → 160 batarya kapasitesi arasında döngü |
| **MOD** butonu | A\* ↔ RL modu arasında geçiş |
| **AJAN** butonu | 1 → 2 → 3 ajan arasında döngü |
| **DEPO SEÇ** / **BİTİŞ EKLE/SEÇ** | Haritada tıklanacak yeni depo/bitiş konumu seçim modunu açar |
| Fare tıklaması (harita) | Seçim modundayken depo/bitiş konumunu ayarlar |

> Not: Araç, pil, mod veya ajan sayısı değiştirildiğinde `reset_env()` tetiklenir ve ortam (hedefler, trafik, şarj istasyonları dahil) yeniden rastgele üretilir.

---

## 📈 Davranışsal Analiz

Simülasyon çalıştırıldığında her kuryenin davranışı:

1. **Depo noktasından** başlanır, claim edilmemiş en yakın hedef seçilir
2. A\* modunda planlanan yol adım adım, RL modunda ε-greedy aksiyonlarla adım adım izlenir
3. Her adımda trafik çarpanına göre batarya tüketilir ve ceza işlenir
4. Şarj istasyonuna girilirse batarya yenilenir
5. Hedefe varıldığında bonus kazanılır, hedef işaretlenir, bir sonraki açık hedefe geçilir
6. Batarya tükenirse ajan `stranded` olur ve hedefini bırakır; diğer ajanlar devralabilir
7. Tüm hedefler bitince (varsa) bitiş noktasına gidilir, ardından epizod sona erer

**Gözlemler:**

- A\* modu deterministik ve genelde daha hızlı yakınsar; aynı harita için tutarlı rotalar üretir
- RL modu başlangıçta (yüksek ε) verimsiz dolaşır, epizodlar ilerledikçe Q-tablosu sayesinde rotalar kısalır
- Düşük tüketimli bisiklet daha az şarj molası gerektirir ama toplam süreyi uzatır; araba hızlıdır fakat sık şarj ihtiyacı doğurabilir
- Çoklu ajan senaryosunda hedefler kuryeler arasında otomatik paylaşılır, ancak küresel optimizasyon yapılmaz (her ajan kendi açısından greedy karar verir)

---

## 🔎 Tartışma ve Eleştiriler

### Güçlü Yönler

- Trafik-ağırlıklı A\* ile gerçekçi maliyet modellemesi
- Batarya/şarj mekaniği sayesinde kaynak kısıtlı planlama senaryosu
- A\* ve RL'nin aynı arayüzde karşılaştırılabilmesi
- Çoklu ajan desteği ve claim tabanlı çakışma önleme
- Zengin görsel arayüz, anlık metrikler ve epizod sonu grafik raporu

### Sınırlılıklar

- Trafik aktifken Manhattan heuristiği klasik anlamda admissible değildir; A\*'ın "garanti optimal" özelliği bu durumda teorik olarak zayıflar
- Hedef ataması her ajan için bağımsız greedy yapılır; küresel bir görev dağıtım algoritması (örn. Macar Algoritması) kullanılmaz
- RL ajanı basit tablo tabanlı Q-learning kullanır; durum uzayı `(pos, target)` ile sınırlıdır, engel/trafik bilgisini doğrudan durum olarak görmez
- Trafik ve şarj istasyonu konumları epizod boyunca **statik**tir (gerçek zamanlı dinamik trafik yoktur)
- Köşe dönüş maliyeti veya yol yumuşatma uygulanmaz, rotalar "merdiven" şeklinde ilerler

### RL Bağlamında Değerlendirme

Sutton ve Barto'nun tanımına göre bir RL ajanının amacı, beklenen toplam ödülü maksimize etmektir. Bu sistemde ödül sinyali **dense** (mesafe azalışı/artışı ve trafik cezası, her adımda) ile **sparse** (hedefe ulaşınca +10) bileşenlerin karışımıdır; bu, klasik bir **reward shaping** örneğidir ve öğrenmeyi hızlandırmaya yöneliktir. Buna karşın durum uzayının küçük tutulması (`pos, target_pos`), ajanın trafik veya diğer ajanların varlığını doğrudan gözlemleyememesi anlamına gelir.

---

## 🛠️ Geliştirme Önerileri

### 1. Durum Uzayını Genişletmek (Daha Güçlü RL)

```python
# Önerilen durum: (pos, target_pos, batarya_seviyesi_bucket, en_yakin_trafik_yonu)
state = (pos, target_pos, battery_bucket(agent["battery"]), nearby_traffic_signature(pos))
```

Bu sayede ajan, trafik ve batarya farkındalığıyla daha iyi rota/şarj kararları öğrenebilir.

### 2. Görev Dağıtımında Küresel Optimizasyon

- Çoklu ajan için bağımsız greedy yerine **Macar Algoritması (Hungarian Algorithm)** ile toplu atama
- Ya da basit bir **clustering** (k-means benzeri) ile hedefleri ajan sayısına göre önceden bölme

### 3. Dinamik Trafik ve Yeniden Planlama

- Trafik yoğunluğu zamanla değişebilir (örn. her N saniyede yeniden örneklenebilir)
- **D\* Lite** veya periyodik A\* yeniden hesaplama ile canlı adaptasyon

### 4. Yol Yumuşatma

```python
path = a_star(start, goal)
smooth_path = [path[0]]
for pt in path[1:]:
    if not colinear(smooth_path[-1], smooth_path[-2], pt):
        smooth_path.append(pt)
smooth_path.append(path[-1])
```

90° dönüşleri azaltarak daha akıcı bir hareket görseli sağlar. Alternatif algoritmalar: **Theta\***, **Lazy Theta\***, **JPS (Jump Point Search)**.

### 5. Heuristik Düzeltmesi

Trafikli ortamda admissibility'yi korumak için heuristik, ortamdaki en düşük hücre maliyetiyle çarpılabilir:

```python
h = min_cell_cost * (abs(nb[0]-goal[0]) + abs(nb[1]-goal[1]))
```

### 6. Performans Optimizasyonu

- Statik arka plan (binalar, yol ızgarası) için `pygame.Surface` önbellekleme
- Büyük haritalarda JPS veya örnekleme tabanlı planlayıcılar (PRM/RRT) değerlendirilebilir

---

## ⚙️ Kurulum ve Kullanım

### Gereksinimler

```bash
python -m venv venv
source venv/bin/activate
pip install pygame numpy
```

> Not: Grafik overlay'i uygulama içinde Pygame ile çizilir; `matplotlib` yalnızca yukarıdaki örnek dış-analiz koduna referans olarak verilmiştir, çalışma zamanında zorunlu değildir.

### Çalıştırma

```bash
python3 simulator.py
```

### Hızlı Kontrol Özeti

```
S            →  Simülasyonu Başlat / Durdur
R            →  Simülasyonu Sıfırla
1 / 2 / 3    →  Yavaş / Normal / Hızlı Hız
ESC          →  Grafik / Seçim Modunu Kapat
Fare         →  Buton tıklama, depo/bitiş konumu seçme
```

---

## 📁 Temel Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `reset_env()` | Ortamı (binalar, hedefler, trafik, şarj istasyonları) ve tüm ajanları rastgele yeniden oluşturur |
| `a_star(start, goal)` | Trafik maliyetli A\* uygular, hücre listesi döndürür |
| `_plan_agent_target(agent)` | Ajan için en yakın açık hedefi (veya bitiş noktasını) seçer ve claim eder |
| `_rl_step(agent)` | RL modunda ε-greedy aksiyon seçer ve Q-tablosunu günceller |
| `update_logic()` | Tüm ajanları bir adım ilerletir; batarya, zaman, ceza ve teslimat kayıtlarını günceller |
| `draw()` | Ana çizim döngüsü; harita, panel ve (varsa) grafik overlay'ini çizer |
| `_draw_map()` | Haritayı, ajanları, hedef/şarj/depo/bitiş ikonlarını ve alt butonları çizer |
| `_draw_panel()` | Sağ kontrol panelini, metrikleri ve gelişmiş ayar butonlarını çizer |
| `_draw_graph_overlay()` | Epizod sonu performans grafiğini (bar + zaman çizgisi) gösterir |
| `_handle_map_click(mpos)` | Depo/bitiş seçim modunda harita tıklamasını işler |
| `run()` | Pygame event döngüsünü yönetir; girişleri ve simülasyon zamanlamasını kontrol eder |

---

## 📚 Kaynaklar

- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.*
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction.*
- Erdal T., Aytu O. (2016). *K-En Yakın Komşu Algoritması Parametrelerinin Sınıflandırma Performansı Üzerine Etkisinin İncelenmesi*

---

## 🔚 Sonuç

Akıllı Lojistik Simülatörü, klasik A\* yol planlamasını trafik maliyetleri, sınırlı batarya ve çoklu kurye dinamikleriyle zenginleştirerek gerçekçi bir teslimat senaryosu sunar. Aynı ortamda isteğe bağlı olarak devreye alınabilen Q-learning tabanlı RL modu, deterministik planlama ile öğrenen davranış arasında doğrudan bir karşılaştırma imkânı verir. Önerilen geliştirmeler (genişletilmiş durum uzayı, küresel görev dağıtımı, dinamik trafik, yol yumuşatma) ile sistem; lojistik optimizasyonu ve multi-agent RL araştırmaları için daha da güçlü bir test platformuna dönüştürülebilir.

---

<div align="center">
  <sub><b>Python & Pygame ile geliştirilmiştir • Akıllı Lojistik Simülatörü</b></sub>
</div>