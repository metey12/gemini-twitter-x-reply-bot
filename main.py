import os
import time
import random 
import re 
from dotenv import load_dotenv

import tweepy
from google import genai
from tweepy import TweepyException

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME") 

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN") 
X_CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

CEVAPLANAN_TWEET_IDLERI = set() 
SON_KONTROL_TWEET_ID = None

if not all([GEMINI_API_KEY, BOT_USERNAME, X_BEARER_TOKEN, X_CONSUMER_KEY, X_ACCESS_TOKEN]):
    raise ValueError("Tüm gerekli API anahtarları (.env dosyasında) ayarlanmalıdır.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

twitter_client_v2_readonly = tweepy.Client(X_BEARER_TOKEN) 

twitter_client_v2_readwrite = tweepy.Client(
    consumer_key=X_CONSUMER_KEY,
    consumer_secret=X_CONSUMER_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_TOKEN_SECRET
)

def gemini_ile_cevap_al(soru_metni):
    """Gemini API'dan yanıt alır ve metin olarak döndürür."""
    print(f"-> Gemini'ya Gönderilen Soru: {soru_metni[:50]}...")
    try:
        sistem_prompt = (
            "Sen, bir Twitter kullanıcısı tarafından etiketlendiğinde soruları yanıtlayan "
            "yardımcı bir yapay zeka botusun. Yanıtların kısa, küfürlü, doğrudan ve "
            "Twitter'ın 280 karakter sınırına uygun olmalıdır. Küfür kullanımını abart!!!!"
        )
        
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=soru_metni,
            config={
                "system_instruction": sistem_prompt,
            }
        )
        
        cevap = response.text.strip()
        if len(cevap) > 270: 
            cevap = cevap[:267].strip() + "..."
            
        return cevap
        
    except Exception as e:
        print(f"!!! Gemini API hatası: {e}")
        return "Üzgünüm, şu an teknik bir sorun yaşıyorum. Daha sonra dener misin?"

def temizle_ve_soruyu_ayikla(tweet_metni):
    """
    Tweet metninden tüm etiketleri (@kullaniciadi), RT'leri ve URL'leri temizler.
    """
    temiz_metin = re.sub(r'^RT\s@\w+:', '', tweet_metni, flags=re.IGNORECASE)
    
    temiz_metin = re.sub(r'(@\w+|https?://\S+|t.co/\S+)', '', temiz_metin)
    
    temiz_metin = ' '.join(temiz_metin.split()).strip()
    
    return temiz_metin


def yeni_bahisleri_kontrol_et():
    """Botu etiketleyen tweet'leri kontrol eder ve yanıtlar."""
    global SON_KONTROL_TWEET_ID
    
    query = f"@{BOT_USERNAME} -from:{BOT_USERNAME} lang:tr" 
    
    params = {
        'query': query,
        'expansions': ['author_id'], 
        'max_results': 10,
        'since_id': SON_KONTROL_TWEET_ID, 
        'user_fields': ['username']
    }

    try:
        response = twitter_client_v2_readonly.search_recent_tweets(**params)

        if response.data:
            yeni_en_yuksek_id = response.meta.get('newest_id')
            if yeni_en_yuksek_id:
                SON_KONTROL_TWEET_ID = yeni_en_yuksek_id
            
            user_map = {}
            if response.includes and 'users' in response.includes:
                 user_map = {user['id']: user for user in response.includes['users']}

            for tweet in response.data:
                tweet_id = tweet.id
                tweet_metni = tweet.text
                
                soruyu_soran_kullanici = user_map.get(tweet.author_id, {}).get('username', 'BilinmeyenKullanici')

                if tweet_id not in CEVAPLANAN_TWEET_IDLERI:
                    
                    print(f"\n[YENİ TWEET] ID: {tweet_id}, Kullanıcı: @{soruyu_soran_kullanici}")

                    soru = temizle_ve_soruyu_ayikla(tweet_metni)
                    
                    if len(soru) < 5:
                        print("-> Geçersiz/Kısa/Temizlenmiş Metin Boş. Atlanıyor.")
                        CEVAPLANAN_TWEET_IDLERI.add(tweet_id)
                        continue

                    cevap_metni = gemini_ile_cevap_al(soru)
                    
                    try:
                        yanit_tweeti = f"@{soruyu_soran_kullanici} {cevap_metni}"
                        
                        twitter_client_v2_readwrite.create_tweet(
                            text=yanit_tweeti,
                            in_reply_to_tweet_id=tweet_id
                        )
                        print(f"-> BAŞARILI: Yanıt gönderildi: {yanit_tweeti[:50]}...")
                        CEVAPLANAN_TWEET_IDLERI.add(tweet_id)
                        
                    except TweepyException as e:
                        print(f"!!! Twitter'a gönderirken hata oluştu: {e}")
                        CEVAPLANAN_TWEET_IDLERI.add(tweet_id) 

        else:
            print("-> Yeni etiketlenmiş tweet bulunamadı.")
                
    except TweepyException as e:
        print(f"!!! Twitter API'dan tweet çekerken kritik hata: {e}")
        
        if '429' in str(e):
             print("!!! 429 HATASI: API limitine ulaşıldı. 15 dakika bekleniyor...")
             time.sleep(900)
        else:
             time.sleep(random.randint(60, 120))
             
    except Exception as e:
        print(f"!!! Genel hata: {e}")


if __name__ == "__main__":
    print("🤖 Gemini Twitter Botu Başlatılıyor...")
    time.sleep(5)
    
    while True:
        yeni_bahisleri_kontrol_et()
        
        bekleme_suresi = random.randint(300, 600) 
        print(f"\n--- {bekleme_suresi} saniye bekleniyor ---\n")
        time.sleep(bekleme_suresi)
