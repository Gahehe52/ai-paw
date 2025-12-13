from pyramid.view import view_config
import google.generativeai as genai
import requests
import time
import json
import os
from dotenv import load_dotenv
from models import Review, DBSession

load_dotenv()

# --- KONFIGURASI API ---
HF_TOKEN = os.getenv('HF_API_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Konfigurasi Gemini
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
    except:
        pass

def call_huggingface_sentiment(text):
    """
    Step 1: Sentiment Analysis menggunakan requests manual
    Diadaptasi dari kode referensi ai_services.py yang berhasil.
    """
    if not HF_TOKEN:
        print("❌ HF Token Missing")
        return {"label": "CFG_ERR", "score": 0.0}

    # Gunakan Model & URL dari referensi yang terbukti jalan
    model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    API_URL = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    print(f"📡 Sending to HF ({model_id})...")

    try:
        # Request Pertama
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        
        # Handle Cold Boot (Error 503) - Tunggu & Coba lagi
        if response.status_code == 503:
            print("⏳ Model sedang loading (Cold Boot)... Menunggu 5 detik...")
            time.sleep(5)
            response = requests.post(API_URL, headers=headers, json={"inputs": text})

        if response.status_code != 200:
            print(f"❌ HF Error {response.status_code}: {response.text}")
            return {"label": "API_ERR", "score": 0.0}

        result = response.json()
        
        # Parsing hasil model Roberta (List of List of Dicts)
        # Contoh: [[{'label': 'positive', 'score': 0.9}, {'label': 'negative', 'score': 0.1}]]
        if isinstance(result, list) and len(result) > 0:
            # Ambil list skor pertama
            scores = result[0] 
            
            # Cari label dengan score tertinggi
            top_result = max(scores, key=lambda x: x['score'])
            label_raw = top_result['label']
            score = top_result['score']
            
            # Mapping label agar seragam (huruf besar)
            if label_raw == "positive": 
                final_label = "POSITIVE"
            elif label_raw == "negative": 
                final_label = "NEGATIVE"
            else: 
                final_label = "NEUTRAL"
            
            print(f"✅ HF Success: {final_label} ({score:.2f})")
            return {"label": final_label, "score": score}

        return {"label": "UNKNOWN", "score": 0.0}

    except Exception as e:
        print(f"❌ HF Exception: {str(e)}")
        return {"label": "CONN_ERR", "score": 0.0}

def extract_key_points_gemini(text):
    """Step 2: Extract Key Points via Gemini"""
    try:
        # Gunakan model yang VALID di akun Anda (gemini-2.5-flash)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Analyze this review and return a JSON array of strings containing max 3 key points.
        Format: ["Point 1", "Point 2"]
        Review: {text}
        """
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return ["No analysis returned"]

        cleaned_text = response.text.strip()
        # Bersihkan markdown ```json jika ada
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.split("```")[1]
            if cleaned_text.startswith("json"):
                cleaned_text = cleaned_text[4:]
        
        return json.loads(cleaned_text.strip())
    except Exception as e:
        print(f"❌ Gemini Exception: {str(e)}")
        # Return fallback jika gagal agar frontend tidak crash
        return ["Failed to extract points"]

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        data = request.json_body
        product_name = data.get('product_name')
        review_text = data.get('review_text')

        # 1. Jalankan AI
        sentiment_result = call_huggingface_sentiment(review_text)
        key_points = extract_key_points_gemini(review_text)

        # 2. Simpan ke Database
        new_review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment_result['label'],
            confidence=sentiment_result['score'],
            key_points=json.dumps(key_points)
        )
        DBSession.add(new_review)
        
        # Flush agar ID terbentuk tanpa memutus sesi
        DBSession.flush() 
        
        return {
            'id': new_review.id,
            'product_name': product_name,
            'sentiment': sentiment_result['label'],
            'confidence': sentiment_result['score'],
            'key_points': key_points
        }
    except Exception as e:
        print(f"❌ Server Error: {str(e)}")
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='get_reviews', request_method='GET', renderer='json')
def get_reviews(request):
    try:
        reviews = DBSession.query(Review).order_by(Review.created_at.desc()).all()
        return [{
            'id': r.id,
            'product_name': r.product_name,
            'review_text': r.review_text,
            'sentiment': r.sentiment,
            'confidence': r.confidence,
            'key_points': json.loads(r.key_points) if r.key_points else [],
            'created_at': str(r.created_at)
        } for r in reviews]
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        request.response.status = 500
        return {'error': 'Database error'}