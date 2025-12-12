# 🌿 ReviewSense.ai - AI Product Review Analyzer

**ReviewSense.ai** adalah aplikasi Full-Stack Web yang memanfaatkan kecerdasan buatan (AI) untuk menganalisis ulasan produk secara otomatis. Aplikasi ini dapat menentukan sentimen pelanggan dan mengekstrak poin-poin penting dari teks ulasan.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Tech Stack](https://img.shields.io/badge/Stack-Pyramid%20%2B%20React-blue)

## ✨ Fitur Utama

- **Analisis Sentimen Akurat:** Menggunakan model **DistilBERT** via Hugging Face untuk menentukan apakah ulasan bersifat Positif atau Negatif.
- **Ekstraksi Poin Kunci:** Menggunakan **Google Gemini (2.5 Flash)** untuk merangkum poin-poin utama (kelebihan/kekurangan) dari ulasan panjang.
- **Organic Modern UI:** Antarmuka yang bersih dan elegan dengan tema warna alam (Cream, Sage, Forest Green).
- **Riwayat Analisis:** Menyimpan semua hasil analisis ke database **PostgreSQL** (Neon Tech) untuk referensi di masa mendatang.
- **Robust Error Handling:** Menangani "Cold Boot" pada API gratis dan koneksi database dengan aman.

## 🛠️ Tech Stack

### Frontend
- **Framework:** React + Vite
- **Styling:** CSS3 (Custom Properties & Glassmorphism elements)
- **Icons:** Lucide React
- **HTTP Client:** Axios

### Backend
- **Framework:** Python Pyramid
- **Database ORM:** SQLAlchemy
- **AI Integration:**
  - `huggingface_hub` (Sentiment Analysis)
  - `google-generativeai` (Key Points Extraction)
- **Database:** PostgreSQL (Cloud via Neon.tech)

---

## 🚀 Cara Menjalankan Project

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal Anda.

### Prasyarat
- Python 3.8+
- Node.js & npm
- Akun & API Key dari [Hugging Face](https://huggingface.co/)
- Akun & API Key dari [Google AI Studio](https://aistudio.google.com/)
- Database PostgreSQL (Lokal atau Cloud)

### 1. Setup Backend (Python)

Masuk ke folder backend dan buat virtual environment:

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Untuk Windows (Git Bash)
# source venv/bin/activate  # Untuk Mac/Linux
````

Install dependencies:

```bash
pip install -r requirements.txt
```

*(Catatan: Pastikan library `pyramid`, `waitress`, `sqlalchemy`, `psycopg2-binary`, `google-generativeai`, `huggingface_hub`, `python-dotenv`, `wsgicors` terinstall)*

Buat file `.env` di dalam folder `backend/` dan isi konfigurasi berikut:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSy_xxxxxxxxxxxxxxxxxxxxxxx
```

Jalankan Server:

```bash
python app.py
```

*Server akan berjalan di http://0.0.0.0:6543*

### 2\. Setup Frontend (React)

Buka terminal baru, masuk ke folder frontend:

```bash
cd frontend
npm install
```

Jalankan Frontend:

```bash
npm run dev
```

*Aplikasi akan berjalan di http://localhost:5173*

-----

## 📂 Struktur Project

```
ai-paw/
├── backend/              # Python Pyramid Server
│   ├── app.py            # Entry point & Config
│   ├── models.py         # Database Schema
│   ├── views.py          # API Logic & AI Integration
│   └── .env              # Environment Variables (Hidden)
│
└── frontend/             # React Vite App
    ├── src/
    │   ├── App.jsx       # Main Component
    │   ├── App.css       # Styling
    │   └── index.css     # Global Styles (Theme Variables)
    └── package.json
```
