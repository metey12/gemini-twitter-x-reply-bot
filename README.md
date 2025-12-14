# 🤖 Gemini X (Twitter) Reply Bot

Gemini API kullanarak X (Twitter) üzerinde **etiketlendiğinde otomatik cevap veren**,
kısa, agresif ve küfürlü yanıtlar üreten bir Python botu.

Bot:
- Seni etiketleyen tweet’leri bulur
- Metni temizler (RT, mention, link vs.)
- Gemini’den cevap alır
- Tweet’e reply atar
- Aynı tweet’e **bir daha cevap vermez**

> ⚠️ **Uyarı:** Bu bot küfürlü ve sert dil kullanır. Gerçek hesaplarda kullanmadan önce X (Twitter) kurallarını mutlaka incele.

---

## 🚀 Özellikler

- ✅ Gemini 2.5 Flash modeli
- ✅ Tweepy v2 (read + write client ayrımı)
- ✅ Mention (@kullanıcı) takibi
- ✅ Türkçe tweet filtresi
- ✅ 280 karakter limiti kontrolü
- ✅ Rate limit (429) yönetimi
- ✅ Duplicate cevap engelleme
- ✅ Otomatik bekleme (5–10 dk)

---

## 🧠 Kullanılan Teknolojiler

- Python 3.10+
- [Tweepy](https://www.tweepy.org/)
- Google Gemini API
- dotenv
- Regex (tweet temizleme)

## .env dosyası oluşturup gerekli bilgileri giriniz. Ücretsiz API planlarında sınıra takılıyor sürekli. Daha iyi  bir deneyim için X API'nin ücretli sürümünü öneririm.
