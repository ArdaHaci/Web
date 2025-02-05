from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import signal
import pytz  # Türkiye saat dilimi için

# Flask uygulamasını başlat
app = Flask(__name__, template_folder="templates", static_folder="static")

# SQLite Veritabanı Konfigürasyonu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False  # Türkçe karakter desteği

# Veritabanı
db = SQLAlchemy(app)

# Türkiye saat dilimi ayarı
turkey_tz = pytz.timezone("Europe/Istanbul")

# 📌 Haberler Modeli
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(turkey_tz))  # Türkiye saati

# 📌 Bültenler Modeli
class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(turkey_tz))  # Türkiye saati

# 📌 Veritabanını Başlat
with app.app_context():
    db.create_all()

# 📌 Sayfa Route'ları
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/haber')
def haber_sayfasi():
    return render_template("haber.html")

@app.route('/bulten')
def bulten_sayfasi():
    return render_template("bulten.html")

# 📌 Haber API'leri
@app.route('/add_news', methods=['POST'])
def add_news():
    try:
        data = request.json
        new_news = News(
            title=data.get("title"),
            content=data.get("content"),
            timestamp=datetime.now(turkey_tz)  # Türkiye saati ile kaydet
        )
        db.session.add(new_news)
        db.session.commit()
        return jsonify({"message": "Haber başarıyla eklendi!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

@app.route('/get_news', methods=['GET'])
def get_news():
    try:
        news = News.query.order_by(News.timestamp.desc()).all()
        news_list = [{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for n in news]
        return jsonify(news_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    try:
        news = News.query.get_or_404(news_id)
        db.session.delete(news)
        db.session.commit()
        return jsonify({"message": "Haber başarıyla silindi!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

@app.route('/update_news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    try:
        news = News.query.get_or_404(news_id)
        data = request.json

        if not data or not data.get('title') or not data.get('content'):
            return jsonify({"error": "Başlık ve içerik zorunludur"}), 400

        news.title = data.get('title')
        news.content = data.get('content')
        db.session.commit()

        return jsonify({"message": "Haber başarıyla güncellendi!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

# 📌 Bülten API'leri
@app.route('/add_bulletin', methods=['POST'])
def add_bulletin():
    try:
        data = request.json
        new_bulletin = Bulletin(
            title=data.get("title"),
            summary=data.get("summary"),
            content=data.get("content"),
            timestamp=datetime.now(turkey_tz)  # Türkiye saati ile kaydet
        )
        db.session.add(new_bulletin)
        db.session.commit()
        return jsonify({"message": "Bülten başarıyla eklendi!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

@app.route('/get_bulletins', methods=['GET'])
def get_bulletins():
    try:
        bulletins = Bulletin.query.order_by(Bulletin.timestamp.desc()).all()
        bulletin_list = [{
            "id": b.id,
            "title": b.title,
            "summary": b.summary,
            "content": b.content,
            "timestamp": b.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for b in bulletins]
        return jsonify(bulletin_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_bulletin/<int:bulletin_id>', methods=['PUT'])
def update_bulletin(bulletin_id):
    try:
        bulletin = Bulletin.query.get_or_404(bulletin_id)
        data = request.json

        if not data or not data.get('title') or not data.get('summary') or not data.get('content'):
            return jsonify({"error": "Başlık, özet ve içerik zorunludur"}), 400

        bulletin.title = data.get('title')
        bulletin.summary = data.get('summary')
        bulletin.content = data.get('content')
        db.session.commit()

        return jsonify({"message": "Bülten başarıyla güncellendi!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

@app.route('/delete_bulletin/<int:bulletin_id>', methods=['DELETE'])
def delete_bulletin(bulletin_id):
    try:
        bulletin = Bulletin.query.get_or_404(bulletin_id)
        db.session.delete(bulletin)
        db.session.commit()
        return jsonify({"message": "Bülten başarıyla silindi!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

# 📌 Flask Sunucusunu Kapatma İşlemi
def signal_handler(sig, frame):
    print("\nFlask sunucusu kapatılıyor...")
    db.session.close()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 📌 Sunucuyu Başlat
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Hata: {e}")