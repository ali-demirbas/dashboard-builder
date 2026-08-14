# KPI İlişkileri İçin Web Arama Kılavuzu

Bu doküman, **KPI tanımları** için değil, **KPI'lar arası ilişkiler** için arama yaparken kullanılacak.
Tanımlar zaten vendor dokümanlarından çekiliyor (`knowledge/metrics/`). Burada aradığımız şey farklı bir bilgi türü:

> "CPI düşerken retention da düşüyorsa bu ne demek?" — bu bir **tanım** değil, bir **nedensellik iddiası**.

Ve internetin %95'i bu konuda kanıtsız blog yazısı. Arama stratejisinin tek amacı: **kanıt üretmiş kaynakları, kanıt üretmemiş olanlardan ayırmak.**

---

## 1. Neden ayrı bir strateji gerekiyor

| Bilgi türü | Doğru kaynak | Yanlış kaynak |
|---|---|---|
| "CTOR nasıl hesaplanır?" | Vendor dokümanı | Ajans blogu |
| "Ortalama open rate kaçtır?" | Vendor benchmark raporu (metodolojisi açık olan) | "2026 email benchmarks" listicle'ları |
| **"Open rate artıp conversion düşüyorsa sebebi ne?"** | **Deney/incrementality çalışması, MMM literatürü, akademik pazarlama** | **Herkes. Özellikle SEO için yazılmış "10 reasons why" içerikleri** |

Üçüncü satır bizim işimiz. Bir ilişki iddiası ancak şu üçünden biriyle desteklenirse değerlidir:
1. **Randomize deney** (A/B, holdout, geo-lift, PSA test)
2. **Modelleme** (MMM, kausal çıkarım, difference-in-differences)
3. **Büyük-N gözlemsel veri + metodoloji açıklaması** (ör. "12.000 kampanya, şu şekilde normalize edildi")

Bunlardan hiçbiri yoksa iddia **HYPOTHESIS** etiketiyle kayda geçer, FACT olarak değil.

---

## 2. Kaynak katmanları

**Tier 1 — Deney yapmış olanlar (en değerli)**
- Platformların kendi bilim ekipleri: Meta Research, Google Research / Think with Google *ölçüm* yazıları, Microsoft ExP (deney platformu ekibi), Netflix/Airbnb/Booking tech blogları (deney tasarımı)
- Marketing science: Marketing Science Institute (MSI), Journal of Marketing / Journal of Marketing Research, SSRN pazarlama çalışmaları
- Meta-analizler: Ehrenberg-Bass Institute (Byron Sharp), Analytic Partners, Nielsen/Kantar ölçüm çalışmaları
- Ünlü incrementality çalışmaları: eBay'in arama reklamı deneyi (Blake, Nosko, Tadelis), Facebook'un "Ghost Ads" makalesi (Johnson, Lewis, Nubbemeyer), Lewis & Rao "The Unfavorable Economics of Measuring the Returns to Advertising"

**Tier 2 — Metodolojisi açık, büyük veri sahibi**
- Amplitude / Mixpanel product benchmark raporları
- Adjust / AppsFlyer / Sensor Tower / data.ai sektör raporları
- Reforge, Bessemer, OpenView, SaaS Capital benchmark'ları
- Klaviyo / Braze / Iterable benchmark raporları (metodoloji bölümü olanlar)

**Tier 3 — Deneyimli pratisyen, kanıt zayıf ama sinyal değerli**
- Lenny's Newsletter, Andrew Chen, Brian Balfour, Casey Winters, Elena Verna, Rand Fishkin
- Bunları "hipotez kaynağı" olarak kullan, "kanıt kaynağı" olarak değil.

**Tier 4 — Kullanma**
- "Ultimate guide to X metrics" tipi SEO içerikleri
- Metodolojisi olmayan benchmark listeleri
- Kendi ürününü satmak için yazılmış "why your CAC is high" yazıları

---

## 3. Kopyala-yapıştır arama kalıpları

### A. Nedensellik / incrementality arıyorsan
```
"incrementality" AND "holdout" [kanal adı] site:research.facebook.com
ghost ads experiment advertising effectiveness filetype:pdf
"geo experiment" measurement methodology site:research.google
"incremental ROAS" methodology holdout study
advertising effectiveness randomized experiment site:ssrn.com
```

### B. İki metrik arasındaki ilişkiyi arıyorsan
Kalıp: `[metrik A] "correlation" OR "relationship" [metrik B] + kanıt kelimesi`
```
"retention" "correlation" "acquisition channel" cohort study
CPI retention quality paid user acquisition study site:adjust.com
"email frequency" "unsubscribe rate" experiment diminishing returns
"open rate" "conversion" correlation weak signal Apple MPP
LTV CAC ratio benchmark methodology "how we calculated"
```

### C. Bir "kural"ın kaynağını arıyorsan (çok önemli)
Sektörde dolaşan sayıların çoğunun sahibi belirsiz. Kaynağını bulmadan kullanma.
```
"3x" "LTV to CAC" origin who said forEntrepreneurs
"rule of 40" original source Brad Feld
"0.3%" spam complaint rate site:support.google.com
"50 conversions" learning phase site:facebook.com/business/help
```

### D. Kaynak tipini daraltan operatörler
```
site:support.google.com          → GA4/Ads resmi tanımı
site:braze.com/docs              → Braze metrik tanımı
site:help.adjust.com             → MMP tanımı
site:developer.apple.com         → SKAN / MPP gerçeği
filetype:pdf "methodology"       → gerçek çalışma, blog değil
site:ssrn.com OR site:nber.org   → akademik
site:github.com [metrik] SQL     → metriğin kodla yazılmış hali
after:2024                       → GA4/SKAN/MPP sonrası dünya
```

### E. Türkiye / MENA bağlamı için
```
Insider "conversion rate" metrik tanımı site:useinsider.com
Dengage metrik dokümantasyon
Türkiye e-ticaret dönüşüm oranı benchmark [yıl] metodoloji
```

---

## 4. Aramayı yaparken uygulanacak 4 filtre

Bir sayfayı bana getirmeden önce şunlara bak:

1. **Metodoloji bölümü var mı?** Yoksa Tier 3'e düşür.
2. **N kaç?** "Müşterilerimizde gördük" ≠ "40.000 kampanya".
3. **Tarih GA4 / iOS 14.5 / Apple MPP sonrası mı?** 2021 öncesi attribution ve open-rate içeriği büyük ölçüde geçersiz.
4. **Kim yazdı ve ne satıyor?** Satıcı kendi metriğini yüceltiyorsa iddiayı düşür, tanımını yine de al.

---

## 5. Bana nasıl getirmeni istiyorum

Link yığını yerine şu formatta gelirse doğrudan `knowledge/` altına işlerim:

```
KAYNAK: <url>
KİM: <kurum/yazar> — <ne satıyor / çıkar ilişkisi var mı>
TARİH: <yayın tarihi>
İDDİA: <tek cümle: hangi KPI hangi KPI'yı nasıl etkiliyor>
KANIT TÜRÜ: deney / model / gözlemsel / yok
N: <örneklem>
BENİM NOTUM: <şüphen varsa yaz>
```

Sadece URL yapıştırırsan da olur, ben açar okurum — ama "kim yazdı, ne satıyor" bilgisi elde varsa değerlendirmeyi hızlandırıyor.

---

## 6. Öncelik sırası — ilk turda şunları arayalım

En çok karar değiştiren, en çok yanlış bilinen 8 ilişki:

1. ✅ Attributed ROAS ↔ incremental ROAS farkı (holdout kanıtı) — `unit-economics-metrics.md` §13, eBay/Lewis-Rao/Gordon et al.
2. ✅ CPI ↓ ile retention/kalite ilişkisi (kanal kalitesi) — `causal-evidence-three-relationships.md` §1. **Sonuç: zayıf kanıt, Tier 1 çalışma yok — HYPOTHESIS olarak işaretli kaldı, Apple Search Ads karşı-örneği var**
3. ✅ LTV:CAC eşiklerinin gerçek kaynağı ve gross margin şartı — `unit-economics-metrics.md` §3, Skok'un kendi sözleri
4. ✅ Cohort maturity bias — `unit-economics-metrics.md` §8, Fader & Hardie
5. ✅ Email/push frekans ↑ ile unsubscribe & conversion/user ilişkisi — `causal-evidence-three-relationships.md` §2. **Sonuç: güçlü Tier 1 RCT kanıtı (Baek et al. 2025, Chae/Bruno/Feinberg 2019)**
6. ✅ Apple MPP sonrası open rate'in bilgi değeri — `crm-lifecycle-metrics.md` §6
7. ✅ Brand/paid search cannibalization (eBay deneyi) — `unit-economics-metrics.md` §13e, Blake/Nosko/Tadelis
8. ✅ Spend ↑ ile marjinal getiri (saturation / diminishing returns eğrisi, MMM literatürü) — `causal-evidence-three-relationships.md` §3. **Sonuç: en güçlü kanıtlı ilişki — Shapiro/Hitsch/Tuchman 2021 (N=288 marka), Lodish et al. 1995 (389 deney)**

Tüm 8 madde `skills/dashboard-builder/references/kpi-framework.md` §8'deki co-movement tablosuna "Outside evidence tier" sütunu olarak işlendi.
