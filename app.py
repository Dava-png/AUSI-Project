from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import uuid
import os
from urllib.parse import unquote
from datetime import datetime

app = Flask(__name__, static_folder=None)
app.secret_key = 'mrkicks-secret-key-2026'
CORS(app, supports_credentials=True)

DB_PATH = 'database.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'proof')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, 'Pages', 'user'), 'login.html')


@app.route('/<path:path>')
def serve_static(path):
    # Try direct (Assets/, database.db, etc.)
    direct = os.path.join(BASE_DIR, path)
    if os.path.exists(direct) and os.path.isfile(direct):
        return send_from_directory(BASE_DIR, path)
    # Try Pages/user/ subdirectory
    user_pages = os.path.join(BASE_DIR, 'Pages', 'user', path)
    if os.path.exists(user_pages) and os.path.isfile(user_pages):
        return send_from_directory(os.path.join(BASE_DIR, 'Pages', 'user'), path)
    # Try Pages/ subdirectory
    pages = os.path.join(BASE_DIR, 'Pages', path)
    if os.path.exists(pages) and os.path.isfile(pages):
        return send_from_directory(os.path.join(BASE_DIR, 'Pages'), path)
    # Fallback
    return send_from_directory(os.path.join(BASE_DIR, 'Pages', 'user'), 'login.html')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def generate_id(prefix=''):
    return prefix + uuid.uuid4().hex[:8].upper()


def require_auth():
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return row_to_dict(user)


def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        price INTEGER NOT NULL,
        desc TEXT DEFAULT '',
        icon TEXT DEFAULT 'fa-shoe-prints'
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        customer TEXT NOT NULL,
        item TEXT NOT NULL,
        date TEXT NOT NULL,
        total INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'processing',
        pickup_address TEXT DEFAULT '',
        pickup_date TEXT DEFAULT ''
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        desc TEXT DEFAULT '',
        price INTEGER NOT NULL,
        category TEXT NOT NULL DEFAULT 'cuci',
        features TEXT DEFAULT '[]',
        image TEXT DEFAULT ''
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        customer TEXT NOT NULL,
        admin TEXT DEFAULT ''
    )''')
    # Add admin column if missing (migration)
    try:
        db.execute('SELECT admin FROM chats LIMIT 1')
    except Exception:
        db.execute('ALTER TABLE chats ADD COLUMN admin TEXT DEFAULT ""')
    db.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        text TEXT NOT NULL,
        time TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL UNIQUE,
        customer TEXT NOT NULL,
        item TEXT NOT NULL,
        total INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed',
        completed_at TEXT NOT NULL
    )''')
    # Migrate old history table if it has the wrong schema
    try:
        db.execute('SELECT order_id FROM history LIMIT 1')
    except Exception:
        db.execute('DROP TABLE IF EXISTS history')
        db.execute('''CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            customer TEXT NOT NULL,
            item TEXT NOT NULL,
            total INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'completed',
            completed_at TEXT NOT NULL
        )''')
    # Migrate plain-text passwords to SHA256
    rows = db.execute('SELECT id, password FROM users').fetchall()
    for r in rows:
        pwd = r['password']
        if len(pwd) != 64 or not all(c in '0123456789abcdef' for c in pwd):
            hashed = hash_password(pwd)
            db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, r['id']))
    db.execute('''CREATE TABLE IF NOT EXISTS reset_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        code TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    # Add courier column to orders if missing
    try:
        db.execute('SELECT courier FROM orders LIMIT 1')
    except Exception:
        db.execute('ALTER TABLE orders ADD COLUMN courier TEXT DEFAULT ""')
    # Add created_at column to users if missing
    try:
        db.execute('SELECT created_at FROM users LIMIT 1')
    except Exception:
        db.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT ''")
        # Backfill for existing users
        db.execute("UPDATE users SET created_at = '17 Juni 2026' WHERE created_at = '' OR created_at IS NULL")
    # Add proof_photo column to orders if missing
    try:
        db.execute('SELECT proof_photo FROM orders LIMIT 1')
    except Exception:
        db.execute("ALTER TABLE orders ADD COLUMN proof_photo TEXT DEFAULT ''")
    db.commit()
    db.close()


init_db()


# ─── AUTH ────────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email dan password harus diisi'}), 400

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    db.close()

    if not user or user['password'] != hash_password(password):
        return jsonify({'error': 'Email atau password salah'}), 401

    session.permanent = True
    session['user_id'] = user['id']
    user_data = dict(user)
    return jsonify({
        'id': user_data['id'],
        'name': user_data['name'],
        'email': user_data['email'],
        'role': user_data['role'],
        'created_at': user_data.get('created_at', '') or ''
    })


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({'error': 'Semua field harus diisi'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password minimal 8 karakter'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': 'Email sudah terdaftar'}), 409

    db.execute('INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)',
               (name, email, hash_password(password), 'user', datetime.now().strftime('%d %B %Y')))
    db.commit()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    db.close()
    session.permanent = True
    session['user_id'] = user['id']
    user_data = dict(user)
    return jsonify({
        'id': user_data['id'],
        'name': user_data['name'],
        'email': user_data['email'],
        'role': user_data['role'],
        'created_at': user_data.get('created_at', '') or ''
    }), 201


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Email harus diisi'}), 400

    db = get_db()
    user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if not user:
        db.close()
        return jsonify({'message': 'Jika email terdaftar, kode reset akan dikirim'}), 200

    # Hapus kode lama untuk email ini
    db.execute('DELETE FROM reset_codes WHERE email = ?', (email,))

    # Generate kode 6 digit
    code = str(uuid.uuid4().int)[:6]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute('INSERT INTO reset_codes (email, code, created_at) VALUES (?, ?, ?)',
               (email, code, now))
    db.commit()
    db.close()

    return jsonify({
        'message': 'Kode reset telah dikirim',
        'code': code,
        'email': email
    }), 200


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    code = data.get('code', '').strip()
    password = data.get('password', '').strip()

    if not email or not code or not password:
        return jsonify({'error': 'Semua field harus diisi'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password minimal 8 karakter'}), 400

    db = get_db()
    record = db.execute(
        'SELECT * FROM reset_codes WHERE email = ? AND code = ? ORDER BY id DESC LIMIT 1',
        (email, code)
    ).fetchone()

    if not record:
        db.close()
        return jsonify({'error': 'Kode reset tidak valid'}), 400

    # Cek expiry 30 menit
    created = datetime.strptime(record['created_at'], '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - created).total_seconds() > 1800:
        db.execute('DELETE FROM reset_codes WHERE email = ?', (email,))
        db.commit()
        db.close()
        return jsonify({'error': 'Kode reset sudah kedaluwarsa'}), 400

    # Update password
    db.execute('UPDATE users SET password = ? WHERE email = ?',
               (hash_password(password), email))
    db.execute('DELETE FROM reset_codes WHERE email = ?', (email,))
    db.commit()
    db.close()

    return jsonify({'message': 'Password berhasil direset'}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout berhasil'})


@app.route('/api/user', methods=['GET'])
def get_user():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401
    return jsonify({
        'id': user['id'], 'name': user['name'], 'email': user['email'],
        'role': user['role'], 'created_at': user.get('created_at', '') or ''
    })


@app.route('/api/user', methods=['PUT'])
def update_user():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    data = request.get_json()
    db = get_db()

    if 'name' in data:
        db.execute('UPDATE users SET name = ? WHERE id = ?', (data['name'].strip(), user['id']))
    if 'email' in data:
        email = data['email'].strip()
        existing = db.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user['id'])).fetchone()
        if existing:
            db.close()
            return jsonify({'error': 'Email sudah digunakan'}), 409
        db.execute('UPDATE users SET email = ? WHERE id = ?', (email, user['id']))
    if 'password' in data and data['password'].strip():
        db.execute('UPDATE users SET password = ? WHERE id = ?', (hash_password(data['password'].strip()), user['id']))

    db.commit()
    db.close()
    return jsonify({'message': 'Profil berhasil diperbarui'})


# ─── PRODUCTS ────────────────────────────────────────────────────────────────

@app.route('/api/products', methods=['GET'])
def get_products():
    db = get_db()
    products = db.execute('SELECT * FROM products ORDER BY title').fetchall()
    db.close()
    return jsonify([row_to_dict(r) for r in products])


@app.route('/api/products', methods=['POST'])
def create_product():
    user = require_auth()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    pid = data.get('id', generate_id('PROD-'))
    db = get_db()
    db.execute('INSERT INTO products (id, title, category, price, desc, icon) VALUES (?, ?, ?, ?, ?, ?)',
               (pid, data['title'], data.get('category', 'style'),
                int(data['price']), data.get('desc', ''), data.get('icon', 'fa-shoe-prints')))
    db.commit()
    db.close()
    return jsonify({'id': pid, 'message': 'Produk berhasil ditambahkan'}), 201


@app.route('/api/products/<pid>', methods=['PUT'])
def update_product(pid):
    user = require_auth()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    db = get_db()
    db.execute('UPDATE products SET title=?, category=?, price=?, desc=?, icon=? WHERE id=?',
               (data.get('title'), data.get('category'), int(data.get('price', 0)),
                data.get('desc', ''), data.get('icon', 'fa-shoe-prints'), pid))
    db.commit()
    db.close()
    return jsonify({'message': 'Produk berhasil diperbarui'})


@app.route('/api/products/<pid>', methods=['DELETE'])
def delete_product(pid):
    user = require_auth()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (pid,))
    db.commit()
    db.close()
    return jsonify({'message': 'Produk berhasil dihapus'})


# ─── SERVICES ────────────────────────────────────────────────────────────────

@app.route('/api/services', methods=['GET'])
def get_services():
    db = get_db()
    services = db.execute('SELECT * FROM services ORDER BY title').fetchall()
    db.close()
    result = []
    for s in services:
        d = row_to_dict(s)
        import json
        d['features'] = json.loads(d.get('features', '[]'))
        result.append(d)
    return jsonify(result)


@app.route('/api/services/<sid>', methods=['GET'])
def get_service(sid):
    db = get_db()
    s = db.execute('SELECT * FROM services WHERE id = ?', (sid,)).fetchone()
    db.close()
    if not s:
        return jsonify({'error': 'Service not found'}), 404
    d = row_to_dict(s)
    import json
    d['features'] = json.loads(d.get('features', '[]'))
    return jsonify(d)


# ─── ORDERS ──────────────────────────────────────────────────────────────────

@app.route('/api/orders', methods=['GET'])
def get_orders():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    nama = request.args.get('nama', '').strip() or user['name']
    db = get_db()
    if user['role'] == 'admin':
        orders = db.execute('SELECT * FROM orders ORDER BY date DESC, id DESC').fetchall()
    else:
        orders = db.execute('SELECT * FROM orders WHERE customer = ? ORDER BY date DESC, id DESC',
                           (nama,)).fetchall()
    db.close()
    return jsonify([row_to_dict(o) for o in orders])


@app.route('/api/orders', methods=['POST'])
def create_order():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    data = request.get_json()
    oid = generate_id('MRK-')
    today = datetime.now().strftime('%d %B %Y')
    db = get_db()
    db.execute('''INSERT INTO orders (id, customer, item, date, total, status, pickup_address, pickup_date)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
               (oid, (data.get('customer') or '').strip() or user['name'], data.get('item', ''), today,
                int(data.get('total', 0)), 'processing',
                data.get('pickup_address', ''), data.get('pickup_date', '')))
    db.commit()
    db.close()
    return jsonify({'id': oid, 'message': 'Pesanan berhasil dibuat'}), 201


@app.route('/api/orders/<oid>/status', methods=['PUT', 'OPTIONS'])
def update_order_status(oid):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    oid = unquote(oid)
    user = require_auth()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    body = request.get_json(silent=True) or {}
    status = body.get('status', 'processing')
    db = get_db()

    # If completed, copy to history (or update if already exists)
    if status == 'completed':
        order = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
        if order:
            now = datetime.now().strftime('%d %B %Y %H:%M')
            existing = db.execute('SELECT id FROM history WHERE order_id = ?', (oid,)).fetchone()
            if existing:
                db.execute('''UPDATE history SET customer=?, item=?, total=?, date=?, status=?, completed_at=?
                              WHERE order_id=?''',
                           (order['customer'], order['item'],
                            order['total'], order['date'], 'completed', now, oid))
            else:
                db.execute('''INSERT INTO history (order_id, customer, item, total, date, status, completed_at)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (order['id'], order['customer'], order['item'],
                            order['total'], order['date'], 'completed', now))

    # If cancelled, remove from history
    if status == 'cancelled':
        db.execute('DELETE FROM history WHERE order_id = ?', (oid,))

    db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, oid))
    db.commit()
    db.close()
    return jsonify({'message': 'Status pesanan diperbarui'})


@app.route('/api/orders/<oid>', methods=['DELETE'])
def delete_order(oid):
    oid = unquote(oid)
    user = require_auth()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (oid,))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesanan berhasil dihapus'})


# ─── KURIR (Courier) ───────────────────────────────────────────────────────

def get_kurir_nama_list(db=None):
    db = db or get_db()
    rows = db.execute("SELECT name FROM users WHERE role = 'kurir' ORDER BY name").fetchall()
    return [r['name'] for r in rows]

@app.route('/api/kurir/list', methods=['GET'])
def get_kurir_list():
    return jsonify(get_kurir_nama_list())


@app.route('/api/orders/kurir', methods=['GET'])
def get_kurir_orders():
    nama = request.args.get('nama', '')
    db = get_db()
    if not nama or nama not in get_kurir_nama_list(db):
        db.close()
        return jsonify({'error': 'Nama kurir tidak valid'}), 400

    # Order yang assigned ke kurir ini (status processing, belum dikirim)
    diambil = db.execute(
        "SELECT * FROM orders WHERE courier = ? AND status = 'processing' ORDER BY date DESC",
        (nama,)
    ).fetchall()
    # Order yang ready (status processing, belum ada courier)
    tersedia = db.execute(
        "SELECT * FROM orders WHERE status = 'processing' AND (courier IS NULL OR courier = '') ORDER BY date DESC"
    ).fetchall()
    # Order yang sudah dikirim kurir tapi belum selesai (status shipped)
    selesai = db.execute(
        "SELECT * FROM orders WHERE courier = ? AND status = 'shipped' ORDER BY date DESC",
        (nama,)
    ).fetchall()
    # Riwayat pengiriman (status completed/delivered, courier = nama ini)
    riwayat = db.execute(
        "SELECT * FROM orders WHERE courier = ? AND status IN ('completed','delivered') ORDER BY date DESC LIMIT 20",
        (nama,)
    ).fetchall()
    db.close()
    return jsonify({
        'diambil': [row_to_dict(r) for r in diambil],
        'tersedia': [row_to_dict(r) for r in tersedia],
        'selesai': [row_to_dict(r) for r in selesai],
        'riwayat': [row_to_dict(r) for r in riwayat]
    })


@app.route('/api/orders/<oid>/ambil', methods=['PUT'])
def ambil_order(oid):
    oid = unquote(oid)
    nama = (request.get_json(silent=True) or {}).get('nama', '')
    db = get_db()
    kurir_list = get_kurir_nama_list(db)
    if not nama or nama not in kurir_list:
        db.close()
        return jsonify({'error': 'Nama kurir tidak valid'}), 400

    order = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    if not order:
        db.close()
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404
    if order['status'] != 'processing':
        db.close()
        return jsonify({'error': 'Pesanan sudah diambil atau dikirim'}), 400
    if order['courier']:
        db.close()
        return jsonify({'error': 'Pesanan sudah memiliki kurir'}), 400

    db.execute('UPDATE orders SET courier = ? WHERE id = ?', (nama, oid))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesanan berhasil diambil', 'courier': nama})


@app.route('/api/orders/<oid>/ship', methods=['PUT'])
def ship_order(oid):
    oid = unquote(oid)
    nama = (request.get_json(silent=True) or {}).get('nama', '')
    db = get_db()
    kurir_list = get_kurir_nama_list(db)
    if not nama or nama not in kurir_list:
        db.close()
        return jsonify({'error': 'Nama kurir tidak valid'}), 400

    order = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    if not order:
        db.close()
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404
    if order['courier'] != nama:
        db.close()
        return jsonify({'error': 'Bukan pesanan Anda'}), 403
    if order['status'] != 'processing':
        db.close()
        return jsonify({'error': 'Pesanan sudah dikirim atau selesai'}), 400

    db.execute('UPDATE orders SET status = ? WHERE id = ?', ('shipped', oid))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesanan dikonfirmasi dikirim'})


@app.route('/api/orders/<oid>/complete', methods=['PUT'])
def complete_order(oid):
    oid = unquote(oid)
    nama = request.form.get('nama', '')
    db = get_db()
    kurir_list = get_kurir_nama_list(db)
    if not nama or nama not in kurir_list:
        db.close()
        return jsonify({'error': 'Nama kurir tidak valid'}), 400

    order = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    if not order:
        db.close()
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404
    if order['courier'] != nama:
        db.close()
        return jsonify({'error': 'Bukan pesanan Anda'}), 403
    if order['status'] != 'shipped':
        db.close()
        return jsonify({'error': 'Pesanan belum dikirim'}), 400

    proof_path = ''
    if 'proof_photo' in request.files:
        file = request.files['proof_photo']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
            filename = f"{oid}_{uuid.uuid4().hex[:8]}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            proof_path = filename

    db.execute('UPDATE orders SET status = ?, proof_photo = ? WHERE id = ?',
               ('delivered', proof_path, oid))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesanan selesai', 'proof_photo': proof_path})


@app.route('/api/orders/<oid>/terima', methods=['PUT'])
def terima_order(oid):
    oid = unquote(oid)
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    data = request.get_json(silent=True) or {}
    nama = (data.get('nama') or '').strip() or user['name']

    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    if not order:
        db.close()
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404
    if order['customer'] != nama:
        db.close()
        return jsonify({'error': 'Bukan pesanan Anda'}), 403
    if order['status'] != 'shipped' and order['status'] != 'delivered':
        db.close()
        return jsonify({'error': 'Pesanan belum dikirim kurir'}), 400

    now = datetime.now().strftime('%d %B %Y %H:%M')
    existing = db.execute('SELECT id FROM history WHERE order_id = ?', (oid,)).fetchone()
    if existing:
        db.execute('''UPDATE history SET customer=?, item=?, total=?, date=?, status=?, completed_at=?
                      WHERE order_id=?''',
                   (order['customer'], order['item'],
                    order['total'], order['date'], 'completed', now, oid))
    else:
        db.execute('''INSERT INTO history (order_id, customer, item, total, date, status, completed_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (order['id'], order['customer'], order['item'],
                    order['total'], order['date'], 'completed', now))

    db.execute('UPDATE orders SET status = ? WHERE id = ?', ('completed', oid))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesanan dikonfirmasi diterima'})

# ─── SERVE UPLOADS ───────────────────────────────────────────────────────────

@app.route('/uploads/proof/<filename>')
def serve_proof(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ─── HISTORY ────────────────────────────────────────────────────────────────

@app.route('/api/history', methods=['GET'])
def get_history():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    db = get_db()
    if user['role'] == 'admin':
        history = db.execute('SELECT * FROM history ORDER BY completed_at DESC').fetchall()
    else:
        history = db.execute('SELECT * FROM history WHERE customer = ? ORDER BY completed_at DESC',
                            (user['name'],)).fetchall()
    db.close()
    return jsonify([row_to_dict(h) for h in history])


# ─── ADMINS ───────────────────────────────────────────────────────────────────

@app.route('/api/admins', methods=['GET'])
def get_admins():
    db = get_db()
    admins = db.execute("SELECT id, name, email FROM users WHERE role = 'admin'").fetchall()
    db.close()
    return jsonify([row_to_dict(a) for a in admins])


# ─── CHAT ────────────────────────────────────────────────────────────────────

@app.route('/api/chats', methods=['GET'])
def get_chats():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    db = get_db()
    if user['role'] == 'admin':
        chats = db.execute('SELECT * FROM chats WHERE admin = ? ORDER BY id DESC',
                          (user['name'],)).fetchall()
    else:
        chats = db.execute('SELECT * FROM chats WHERE customer = ? ORDER BY id DESC',
                          (user['name'],)).fetchall()
    db.close()
    result = []
    for c in chats:
        chat = row_to_dict(c)
        db2 = get_db()
        last = db2.execute('SELECT text, time, date, sender FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT 1',
                          (chat['id'],)).fetchone()
        unread = db2.execute("SELECT COUNT(*) as cnt FROM messages WHERE chat_id = ? AND sender = 'user'",
                            (chat['id'],)).fetchone()
        db2.close()
        chat['lastMessage'] = last['text'] if last else ''
        chat['lastTime'] = last['time'] if last else ''
        chat['lastSender'] = last['sender'] if last else ''
        chat['unread'] = unread['cnt'] if unread else 0
        result.append(chat)
    return jsonify(result)


@app.route('/api/chats', methods=['POST'])
def create_chat():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    data = request.get_json() or {}
    admin_name = (data.get('admin') or '').strip()
    if not admin_name:
        return jsonify({'error': 'Admin tidak dipilih'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM chats WHERE customer = ? AND admin = ?', (user['name'], admin_name)).fetchone()
    if existing:
        db.close()
        return jsonify({'id': existing['id'], 'message': 'Chat sudah ada'})

    cid = generate_id('conv_')
    db.execute('INSERT INTO chats (id, customer, admin) VALUES (?, ?, ?)', (cid, user['name'], admin_name))
    db.commit()
    db.close()
    return jsonify({'id': cid, 'message': 'Chat berhasil dibuat'}), 201


@app.route('/api/chats/<cid>/messages', methods=['GET'])
def get_messages(cid):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    db = get_db()
    messages = db.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC', (cid,)).fetchall()
    db.close()
    return jsonify([row_to_dict(m) for m in messages])


@app.route('/api/chats/<cid>/messages', methods=['POST'])
def send_message(cid):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401

    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    now = datetime.now()
    db = get_db()
    db.execute('INSERT INTO messages (chat_id, sender, text, time, date) VALUES (?, ?, ?, ?, ?)',
               (cid, data.get('sender', 'user'), text,
                now.strftime('%H:%M'), now.strftime('%Y-%m-%d')))
    db.commit()
    db.close()
    return jsonify({'message': 'Pesan terkirim'}), 201


@app.route('/api/chats/<cid>/read', methods=['PUT'])
def mark_read(cid):
    user = require_auth()
    if not user:
        return jsonify({'error': 'Belum login'}), 401
    # Mark all user messages as read (for admin)
    db = get_db()
    db.execute("UPDATE messages SET sender = 'user_read' WHERE chat_id = ? AND sender = 'user'", (cid,))
    db.commit()
    db.close()
    return jsonify({'message': 'OK'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
