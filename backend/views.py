from pyramid.view import view_config
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from models import Review, DBSession
from huggingface_hub import InferenceClient # Gunakan library ini!

load_dotenv()

# --- KONFIGURASI AI ---
HF_TOKEN = os.getenv('HF_API_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Inisialisasi Client Hugging Face
# Library ini otomatis menangani URL baru (router.huggingface.co)
# Pastikan token Anda valid di .env
hf_client = InferenceClient(api_key=HF_TOKEN)

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
    except:
        pass

def call_huggingface_sentiment(text):
    """Step 1: Sentiment Analysis via Hugging Face Library"""
    if not HF_TOKEN:
        print("❌ HF Token Missing")
        return {"label": "CFG_ERR", "score": 0.0}

    try:
        # Gunakan model standar DistilBERT yang stabil
        model_id = "distilbert-base-uncased-finetuned-sst-2-english"
        
        print(f"Sending to HF Library ({model_id})...")
        
        # Panggil API menggunakan library resmi (Bukan requests manual)
        result = hf_client.text_classification(text, model=model_id)
        
        # Result dari library formatnya lebih rapi objek (bukan JSON mentah)
        # Ambil hasil pertama (confidence tertinggi)
        top_result = result[0]
        
        return {
            "label": top_result.label.upper(), 
            "score": top_result.score
        }

    except Exception as e:
        print(f"❌ HF Error: {str(e)}")
        # Cek jika error 503 (Model Loading)
        if "503" in str(e) or "loading" in str(e).lower():
            return {"label": "LOADING...", "score": 0.0}
        
        return {"label": "API_ERR", "score": 0.0}

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
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.split("```")[1]
            if cleaned_text.startswith("json"):
                cleaned_text = cleaned_text[4:]
        
        return json.loads(cleaned_text.strip())
    except Exception as e:
        print(f"❌ Gemini Exception: {str(e)}")
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