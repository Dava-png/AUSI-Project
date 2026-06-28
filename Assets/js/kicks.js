// Service Data
const servicesData = {
    'fast-clean': {
        title: 'Fast Clean',
        desc: 'Cuci cepat 1 hari selesai.',
        features: ['Cuci luar', 'Pengeringan', 'Pewangi'],
        price: 'Rp15.000',
        orderText: 'JASA LAUNDRY - CUCI FAST CLEAN',
        image: 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&h=500&fit=crop'
    },
    'lem-sol': {
        title: 'Lem Sol Lepas',
        desc: 'Sol sepatu jadi kuat seperti baru.',
        features: ['Lem berkualitas tinggi', 'Kuat dan tahan lama', 'Rapi tidak berbekas'],
        price: 'Rp30.000',
        orderText: 'JASA REPARASI - LEM SOL LEPAS',
        image: 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=500&h=500&fit=crop'
    },
    'full-repaint': {
        title: 'Full Repaint',
        desc: 'Perbaiki cat sepatu yang rusak.',
        features: ['Repaint seluruh bagian', 'Warna solid & rata', 'Finishing premium'],
        price: 'Rp30.000',
        orderText: 'JASA REPAINT - FULL REPAINT',
        image: 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&h=500&fit=crop'
    },
    'deep-clean': {
        title: 'Deep Clean',
        desc: 'Cuci mendalam 2-3 hari selesai.',
        features: ['Cuci luar & dalam', 'Membersihkan noda membandel', 'Pengeringan', 'Pewangi'],
        price: 'Rp25.000',
        orderText: 'JASA LAUNDRY - CUCI DEEP CLEAN',
        image: 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=500&h=500&fit=crop'
    },
    'ganti-outsole': {
        title: 'Ganti Outsole',
        desc: 'Ganti sol luar untuk cengkeraman dan tampilan maksimal.',
        features: ['Pilihan sol original', 'Tahan lama', 'Awet dipakai'],
        price: 'Rp150.000',
        orderText: 'JASA REPARASI - GANTI OUTSOLE',
        image: 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&h=500&fit=crop'
    },
    'custom-color': {
        title: 'Custom Color',
        desc: 'Bebas pilih warna sesuai keinginan kamu.',
        features: ['Pilih warna custom', 'Warna sesuai request', 'Finishing premium'],
        price: 'Rp50.000',
        orderText: 'JASA REPAINT - CUSTOM COLOR',
        image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=500&fit=crop'
    },
    'extra-clean': {
        title: 'Extra Clean',
        desc: 'Perawatan ekstra 3-4 hari selesai.',
        features: ['Deep clean menyeluruh', 'Whitening', 'Penghilang bau', 'Pewangi premium'],
        price: 'Rp35.000',
        orderText: 'JASA LAUNDRY - CUCI EXTRA CLEAN',
        image: 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=500&h=500&fit=crop'
    },
    'jahit-sol': {
        title: 'Jahit Sol',
        desc: 'Sol di jahit keliling agar lebih kuat dan tidak mudah lepas.',
        features: ['Jahitan kuat & rapi', 'Benang khusus', 'Lebih awet'],
        price: 'Rp75.000',
        orderText: 'JASA REPARASI - JAHIT SOL',
        image: 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=500&h=500&fit=crop'
    },
    'midsole-repaint': {
        title: 'Midsole Repaint',
        desc: 'Cat ulang midsole agar kembali bersih & fresh.',
        features: ['Repaint midsole', 'Warna cerah', 'Tahan lama'],
        price: 'Rp55.000',
        orderText: 'JASA REPAINT - MIDSOLE REPAINT',
        image: 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&h=500&fit=crop'
    }
};

let currentQty = 5;

// ─── Filters ────────────────────────────────────────────────────────────────

function filterServices(category, btn) {
    btn.parentElement.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.service-card').forEach(card => {
        card.style.display = category === 'all' || card.dataset.category === category ? 'flex' : 'none';
    });
}

function filterOrders(status, btn) {
    btn.parentElement.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('#orders-body tr').forEach(row => {
        row.style.display = status === 'all' || row.dataset.status === status ? '' : 'none';
    });
}

function filterProducts(category, btn) {
    const filters = document.getElementById('product-filters');
    const allBtn = filters.querySelector('[data-cat="all"]');

    if (category === 'all') {
        filters.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        allBtn.classList.add('active');
        document.querySelectorAll('#product-grid .product-card').forEach(c => c.style.display = '');
        return;
    }

    allBtn.classList.remove('active');
    btn.classList.toggle('active');

    const active = [];
    filters.querySelectorAll('.filter-tab.active').forEach(t => {
        if (t.dataset.cat) active.push(t.dataset.cat);
    });

    if (active.length > 3) {
        btn.classList.remove('active');
        return;
    }

    if (active.length === 0) {
        allBtn.classList.add('active');
        document.querySelectorAll('#product-grid .product-card').forEach(c => c.style.display = '');
        return;
    }

    document.querySelectorAll('#product-grid .product-card').forEach(card => {
        card.style.display = active.includes(card.dataset.category) ? '' : 'none';
    });
}

function changeQty(delta) {
    currentQty += delta;
    if (currentQty < 1) currentQty = 1;
    if (currentQty > 99) currentQty = 99;
    document.getElementById('qty-value').textContent = currentQty;
}

// ─── Chat / Admin Picker ─────────────────────────────────────────────────

function toggleChat() {
    const panel = document.getElementById('chatPanel');
    const bubble = document.getElementById('chatBubble');
    if (!panel || !bubble) return;

    const isOpen = panel.classList.contains('open');
    if (isOpen) {
        panel.classList.remove('open');
        bubble.classList.remove('hidden');
    } else {
        showAdminPicker();
    }
}

function showAdminPicker() {
    try {
        const panel = document.getElementById('chatPanel');
        const bubble = document.getElementById('chatBubble');
        if (!panel || !bubble) return;
        panel.classList.add('open');
        bubble.classList.add('hidden');

        const title = panel.querySelector('.chat-panel-header-title');
        const status = panel.querySelector('.chat-panel-header-status');
        const current = sessionStorage.getItem('mrkicks_chat_admin');

        if (current) {
            if (title) title.textContent = 'Ganti Admin';
            if (status) status.textContent = 'Saat ini: ' + current;
        } else {
            if (title) title.textContent = 'Pilih Admin';
            if (status) status.textContent = '';
        }

        const body = document.getElementById('chatBody');
        if (!body) return;
        body.innerHTML = `
            <div class="admin-picker">
                <div class="admin-picker-icon"><i class="fas fa-headset"></i></div>
                <h3 class="admin-picker-title">${current ? 'Ganti Admin' : 'Pilih Admin'}</h3>
                <p class="admin-picker-sub">Silakan pilih admin yang ingin dihubungi</p>
                <div class="admin-picker-list" id="adminPickerList">
                    <div style="text-align:center;color:var(--color-text-muted);padding:20px;">
                        <i class="fas fa-spinner fa-spin"></i> Memuat...
                    </div>
                </div>
            </div>
        `;
        loadAdminList();
    } catch (e) {
        console.error('showAdminPicker error:', e);
    }
}

async function loadAdminList() {
    try {
        const admins = await api.getAdmins();
        const list = document.getElementById('adminPickerList');
        if (!list) return;
        list.innerHTML = '';
        admins.forEach(a => {
            const btn = document.createElement('button');
            btn.className = 'admin-picker-btn';
            btn.innerHTML = '<i class="fas fa-user-shield"></i><span>' + a.name + '</span>';
            btn.onclick = function () { selectAdmin(a.name); };
            list.appendChild(btn);
        });
    } catch (e) {
        const list = document.getElementById('adminPickerList');
        if (list) list.innerHTML = '<div style="text-align:center;color:var(--color-text-muted);padding:20px;">Gagal memuat daftar admin</div>';
    }
}

function selectAdmin(name) {
    const current = sessionStorage.getItem('mrkicks_chat_admin');
    if (current && current !== name) {
        if (!confirm('Anda akan pindah dari ' + current + ' ke ' + name + '. Chat sebelumnya akan tetap tersimpan. Lanjutkan?')) return;
    }
    sessionStorage.setItem('mrkicks_chat_admin', name);
    location.href = 'chat.html';
}

function handleLogout() {
    if (!confirm('Apakah anda yakin ingin logout?')) return;
    sessionStorage.removeItem('mrkicks_user');
    sessionStorage.removeItem('mrkicks_chat_admin');
    api.logout().catch(() => {});
    location.href = '../login.html';
}

function showToast(msg) {
    const existing = document.getElementById('toast');
    if (existing) {
        document.getElementById('toast-msg').textContent = msg;
        existing.classList.add('show');
        setTimeout(() => existing.classList.remove('show'), 2500);
        return;
    }
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    toast.innerHTML = '<i class="fas fa-check-circle"></i> <span id="toast-msg">' + msg + '</span>';
    Object.assign(toast.style, {
        position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
        background: 'var(--bg-card)', border: '1px solid var(--border-gold)',
        borderRadius: '12px', padding: '14px 24px', color: 'var(--color-text-main)',
        fontSize: '0.85rem', zIndex: '10000', display: 'flex', alignItems: 'center',
        gap: '10px', opacity: '0', transition: 'opacity 0.3s ease',
        fontFamily: 'var(--font-primary)'
    });
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => toast.classList.remove('show'), 2500);
}

// ─── Search ────────────────────────────────────────────────────────────────

function setupSearch() {
    const input = document.querySelector('.search-box input');
    if (!input) return;

    input.addEventListener('input', function () {
        const q = this.value.toLowerCase().trim();
        if (!q) {
            document.querySelectorAll('#product-grid .product-card').forEach(c => c.style.display = '');
            document.querySelectorAll('.service-card').forEach(c => c.style.display = 'flex');
            document.querySelectorAll('#orders-body tr').forEach(r => r.style.display = '');
            document.querySelectorAll('#history-body tr').forEach(r => r.style.display = '');
            return;
        }
        document.querySelectorAll('#product-grid .product-card').forEach(card => {
            const name = card.querySelector('.product-name');
            card.style.display = name && name.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
        document.querySelectorAll('.service-card').forEach(card => {
            const title = card.querySelector('.service-title');
            const desc = card.querySelector('.service-desc');
            const match = (title && title.textContent.toLowerCase().includes(q)) ||
                          (desc && desc.textContent.toLowerCase().includes(q));
            card.style.display = match ? 'flex' : 'none';
        });
        document.querySelectorAll('#orders-body tr').forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
        document.querySelectorAll('#history-body tr').forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });
}

// ─── Greeting & DOM Ready ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    setupSearch();
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }
    const isAdminPage = location.pathname.includes('/admin/');
    const user = JSON.parse(sessionStorage.getItem('mrkicks_user') || '{}');
    const greeting = document.querySelector('.user-info h4');
    if (greeting && user.name && !isAdminPage) {
        greeting.textContent = 'Halo, ' + user.name + ' !';
    }
});
