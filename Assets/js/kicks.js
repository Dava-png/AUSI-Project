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
let paymentMode = false;

function showDetail(serviceId) {
    const data = servicesData[serviceId];
    if (!data) return;

    document.getElementById('detail-title').textContent = data.title;
    document.getElementById('detail-desc').textContent = data.desc;
    document.getElementById('detail-price').textContent = data.price;
    document.getElementById('order-item').textContent = data.orderText;
    document.getElementById('detail-image').src = data.image;

    const featuresList = document.getElementById('detail-features');
    featuresList.innerHTML = '';
    data.features.forEach(feature => {
        const li = document.createElement('li');
        li.textContent = feature;
        featuresList.appendChild(li);
    });

    paymentMode = false;
    document.querySelector('.btn-order').innerHTML = '<i class="fas fa-shopping-cart"></i><span id="btn-text">Buat Pesanan</span>';
    document.getElementById('qty-selector').style.display = 'none';
    currentQty = 5;
    document.getElementById('qty-value').textContent = currentQty;

    document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
    document.getElementById('detail-page').classList.add('active');
}

function togglePayment() {
    paymentMode = !paymentMode;
    const qtySelector = document.getElementById('qty-selector');
    const btn = document.querySelector('.btn-order');

    if (paymentMode) {
        btn.innerHTML = '<span>BAYAR SEKARANG</span>';
        qtySelector.style.display = 'flex';
    } else {
        btn.innerHTML = '<i class="fas fa-shopping-cart"></i><span>Buat Pesanan</span>';
        qtySelector.style.display = 'none';
    }
}

function changeQty(delta) {
    currentQty += delta;
    if (currentQty < 1) currentQty = 1;
    if (currentQty > 99) currentQty = 99;
    document.getElementById('qty-value').textContent = currentQty;
}

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

function toggleChat() {
    document.getElementById('chatPanel').classList.toggle('open');
    document.getElementById('chatBubble').classList.toggle('hidden');
}

function sendChat() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    const body = document.getElementById('chatBody');
    const now = new Date();
    const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');

    const msg = document.createElement('div');
    msg.className = 'chat-msg user';
    msg.innerHTML = `<div class="chat-msg-content"><p>${text}</p><span class="chat-msg-time">${time}</span></div>`;
    body.appendChild(msg);
    body.scrollTop = body.scrollHeight;
    input.value = '';
}

// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }
});
