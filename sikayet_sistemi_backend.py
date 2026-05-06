from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = '8a6e8b4c042d3f1a9e701b2c4d5f6a7b8c9d0e1f2a3b4c5d'

DATABASE = 'apartman.db'

def init_db():
    """Veritabanını başlat ve tabloları oluştur"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            daire_no TEXT,
            telefon TEXT,
            rol TEXT DEFAULT 'kullanici',
            kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Şikayetler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sikayetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER NOT NULL,
            baslik TEXT NOT NULL,
            kategori TEXT NOT NULL,
            aciklama TEXT NOT NULL,
            durum TEXT DEFAULT 'Beklemede',
            oncelik TEXT DEFAULT 'Orta',
            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            admin_notu TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id)
        )
    ''')
    
    # Trigger for guncelleme_tarihi
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_sikayet_timestamp 
        AFTER UPDATE ON sikayetler
        BEGIN
            UPDATE sikayetler SET guncelleme_tarihi = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    ''')
    
    # Demo admin kullanıcısı ekle (eğer yoksa)
    cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE email = 'admin@site.com'")
    if cursor.fetchone()[0] == 0:
        admin_sifre = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO kullanicilar (ad_soyad, email, sifre, daire_no, telefon, rol) VALUES (?, ?, ?, ?, ?, ?)",
            ('Yönetici', 'admin@site.com', admin_sifre, 'A1', '05551234567', 'admin')
        )
    
    # Demo kullanıcı ekle (eğer yoksa)
    cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE email = 'ahmet@email.com'")
    if cursor.fetchone()[0] == 0:
        kullanici_sifre = generate_password_hash('kullanici123')
        cursor.execute(
            "INSERT INTO kullanicilar (ad_soyad, email, sifre, daire_no, telefon, rol) VALUES (?, ?, ?, ?, ?, ?)",
            ('Ahmet Yılmaz', 'ahmet@email.com', kullanici_sifre, 'B5', '05559876543', 'kullanici')
        )
    
    conn.commit()
    conn.close()

def get_db():
    """Veritabanı bağlantısı aç"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'kullanici_id' in session:
        if session.get('rol') == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('kullanici_panel'))
    return redirect(url_for('giris'))

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kullanicilar WHERE email = ?", (email,))
        kullanici = cursor.fetchone()
        conn.close()
        
        if kullanici and check_password_hash(kullanici['sifre'], sifre):
            session['kullanici_id'] = kullanici['id']
            session['ad_soyad'] = kullanici['ad_soyad']
            session['rol'] = kullanici['rol']
            
            flash('Giriş başarılı!', 'success')
            if kullanici['rol'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('kullanici_panel'))
        else:
            flash('Email veya şifre hatalı!', 'error')
    
    return render_template('giris.html')

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        ad_soyad = request.form['ad_soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        daire_no = request.form['daire_no']
        telefon = request.form['telefon']
        
        hashed_sifre = generate_password_hash(sifre)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO kullanicilar (ad_soyad, email, sifre, daire_no, telefon) VALUES (?, ?, ?, ?, ?)",
                (ad_soyad, email, hashed_sifre, daire_no, telefon)
            )
            conn.commit()
            conn.close()
            
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('giris'))
        except sqlite3.IntegrityError:
            flash('Bu email adresi zaten kullanılıyor!', 'error')
    
    return render_template('kayit.html')

@app.route('/cikis')
def cikis():
    session.clear()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('giris'))

@app.route('/kullanici')
def kullanici_panel():
    if 'kullanici_id' not in session or session.get('rol') != 'kullanici':
        return redirect(url_for('giris'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sikayetler WHERE kullanici_id = ? ORDER BY olusturma_tarihi DESC",
        (session['kullanici_id'],)
    )
    sikayetler = cursor.fetchall()
    conn.close()
    
    return render_template('kullanici_panel.html', sikayetler=sikayetler)

@app.route('/sikayet-olustur', methods=['GET', 'POST'])
def sikayet_olustur():
    if 'kullanici_id' not in session or session.get('rol') != 'kullanici':
        return redirect(url_for('giris'))
    
    if request.method == 'POST':
        baslik = request.form['baslik']
        kategori = request.form['kategori']
        aciklama = request.form['aciklama']
        oncelik = request.form['oncelik']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sikayetler (kullanici_id, baslik, kategori, aciklama, oncelik) VALUES (?, ?, ?, ?, ?)",
            (session['kullanici_id'], baslik, kategori, aciklama, oncelik)
        )
        conn.commit()
        conn.close()
        
        flash('Şikayetiniz başarıyla oluşturuldu!', 'success')
        return redirect(url_for('kullanici_panel'))
    
    return render_template('sikayet_olustur.html')

@app.route('/admin')
def admin_panel():
    if 'kullanici_id' not in session or session.get('rol') != 'admin':
        return redirect(url_for('giris'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Tüm şikayetleri kullanıcı bilgileriyle birlikte getir
    cursor.execute("""
        SELECT s.*, k.ad_soyad, k.daire_no, k.telefon 
        FROM sikayetler s 
        JOIN kullanicilar k ON s.kullanici_id = k.id 
        ORDER BY s.olusturma_tarihi DESC
    """)
    sikayetler = cursor.fetchall()
    
    # İstatistikler
    cursor.execute("SELECT COUNT(*) as toplam FROM sikayetler")
    toplam = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as bekleyen FROM sikayetler WHERE durum = 'Beklemede'")
    bekleyen = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as cozuldu FROM sikayetler WHERE durum = 'Çözüldü'")
    cozuldu = cursor.fetchone()[0]
    
    conn.close()
    
    istatistikler = {
        'toplam': toplam,
        'bekleyen': bekleyen,
        'cozuldu': cozuldu
    }
    
    return render_template('admin_panel.html', sikayetler=sikayetler, istatistikler=istatistikler)

@app.route('/admin/sikayet/<int:id>', methods=['GET', 'POST'])
def admin_sikayet_detay(id):
    if 'kullanici_id' not in session or session.get('rol') != 'admin':
        return redirect(url_for('giris'))
    
    if request.method == 'POST':
        durum = request.form['durum']
        admin_notu = request.form['admin_notu']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sikayetler SET durum = ?, admin_notu = ? WHERE id = ?",
            (durum, admin_notu, id)
        )
        conn.commit()
        conn.close()
        
        flash('Şikayet güncellendi!', 'success')
        return redirect(url_for('admin_panel'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, k.ad_soyad, k.email, k.daire_no, k.telefon 
        FROM sikayetler s 
        JOIN kullanicilar k ON s.kullanici_id = k.id 
        WHERE s.id = ?
    """, (id,))
    sikayet = cursor.fetchone()
    conn.close()
    
    if not sikayet:
        flash('Şikayet bulunamadı!', 'error')
        return redirect(url_for('admin_panel'))
    
    return render_template('admin_sikayet_detay.html', sikayet=sikayet)

if __name__ == '__main__':
    # templates klasörünü oluştur
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Veritabanını başlat
    init_db()
    print("✅ Veritabanı hazır!")
    print("🚀 Uygulama başlatılıyor...")
    print("📍 http://localhost:5000 adresinden erişebilirsiniz")
    print("\n👤 Demo Hesaplar:")
    print("   Admin: admin@site.com / admin123")
    print("   Kullanıcı: ahmet@email.com / kullanici123\n")
    
    app.run(debug=True, port=5000)