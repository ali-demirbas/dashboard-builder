# Audit Brief — dashboard-builder skill

## Ne inceleniyor

`dashboard-builder-consolidated.md` — bir Claude Code skill'inin tek dosya haline getirilmiş tam hali. Orijinali `skills/dashboard-builder/SKILL.md` + `skills/dashboard-builder/references/` altındaki 5 dosyadan oluşuyor (data-quality-gate, comparability-rules, kpi-framework, analysis-playbook, dashboard-blueprints); bu tek dosya onların birleşimi, aynı içerik.

Skill'in işlevi: kullanıcı pazarlama/büyüme verisi (Adjust, AppsFlyer, GA4, Firebase, Braze, Klaviyo, Insider, Dengage, Meta/Google/TikTok/LinkedIn Ads exports vb.) yüklediğinde, veriyi kalite kontrolünden geçirip, platformlar arası karşılaştırılabilirlik kurallarını uygulayıp, KPI'ları standardize edip, önceliklendirilmiş bir teşhis + dashboard spesifikasyonu üretiyor.

Destek dosyaları (kaynaklama eki, bu dosyaya dahil değil ama iddiaların dayandığı yer): `research/raw/*.md` — her biri gerçek vendor dokümanlarından/akademik makalelerden çekilmiş, URL'li kaynaklarla.

## İstenen

Bu skill'i **eleştirel bir gözle** denetle. Önceden hiçbir bulgu, ipucu veya "muhtemelen şurada sorun var" yönlendirmesi verilmiyor — bağımsız olarak oku ve kendi değerlendirmeni oluştur. Aşağıdaki kategorilerde çıktı üret:

1. **Mantık hataları** — iç tutarsızlıklar, çelişen kurallar, birbirini geçersiz kılan iki talimat, sıralama sorunları (bir adımın ihtiyaç duyduğu bilgi ondan sonraki adımda üretiliyorsa gibi), formüllerin birim/ölçek tutarlılığı.
2. **Kapsam boşlukları** — skill'in ele almadığı ama işlevi gereği ele alması beklenen durumlar (örn. veri türleri, girdi biçimleri, edge case'ler, gizlilik/güvenlik gibi belirtilmemiş konular).
3. **Yenilenmesi gerekenler** — zamanla bayatlayacak, platform politikası/varsayılanı değiştiğinde yanlış hale gelecek somut iddialar; hangi iddiaların "şu an doğru ama kalıcı değil" olduğunu işaretle.
4. **Mekanik/teknik hatalar** — bozuk markdown, tutarsız tablo, geçersiz YAML/JSON, matematiksel hata (formüllerin kendi içinde tutarlılığı — örneğin bir bölümde verilen bir formülün başka bir bölümdeki kullanımıyla uyuşup uyuşmadığı).
5. **Diğer** — yukarıdaki kategorilere girmeyen ama önemli bulduğun her şey.

## Nasıl çalışman gerektiği

- Varsayımda bulunma — dosyayı gerçekten oku, iddiaları birbirine çapraz kontrol et.
- "İyi görünüyor" gibi genel geçer yorumlardan kaçın; her bulguyu somut satır/bölüm referansıyla ver.
- Ciddiyet derecelendir (kritik / önemli / küçük).
- Skill'in kendi iddia ettiği kaynaklama standardını (her formül/tanımın bir vendor dokümanına veya akademik kaynağa dayandığı) sorgula — eğer bir iddia şüpheli görünüyorsa bunu da belirt, doğrulaman gerekmiyor ama "bu iddia doğrulanmaya değer" diye işaretleyebilirsin.
- Hiçbir bulguyu atlama gerekçesiyle küçümseme; kapsamlı ol.

## Çıktı formatı

Serbest — ama her bulgu için: **[kategori] [ciddiyet] konum → sorun → neden sorun**.
