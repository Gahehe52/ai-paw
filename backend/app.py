from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from models import DBSession, Base
import os
from dotenv import load_dotenv
from wsgicors import CORS # Import library baru

load_dotenv()

def main(global_config, **settings):
    # 1. Setup Database
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("WARNING: DATABASE_URL not found in .env")

    settings['sqlalchemy.url'] = database_url
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Buat tabel jika belum ada
    Base.metadata.create_all(engine)

    # 2. Setup Pyramid Config
    with Configurator(settings=settings) as config:
        config.include('pyramid_tm')

        # Routes
        config.add_route('analyze_review', '/api/analyze-review')
        config.add_route('get_reviews', '/api/reviews')
        config.scan('views')

        # Buat WSGI App dasar
        app = config.make_wsgi_app()

        # 3. BUNGKUS DENGAN CORS (Agar Frontend bisa akses)
        return CORS(app, headers="*", methods="*", origin="*", maxage="86400")

if __name__ == '__main__':
    from waitress import serve
    # Jalankan fungsi main
    app = main({})
    print("Server running on http://0.0.0.0:6543")
    serve(app, host='0.0.0.0', port=6543)