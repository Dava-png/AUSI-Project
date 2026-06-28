// ─── Admin Data Layer (API-backed) ──────────────────────────────────────────

async function seedData() {
    try {
        await api.getProducts();
    } catch {
        // API is running — data already in DB
    }
}

async function getData() {
    const [products, orders, chats] = await Promise.all([
        api.getProducts(),
        api.getOrders(),
        api.getChats(),
    ]);
    return { products, orders, chats };
}

async function saveData(data) {
    // Admin pages call saveData after modifications.
    // With API, each CRUD op hits the API directly, so this is a no-op.
    // We keep it so existing inline scripts don't break.
}

function formatPrice(num) {
    return 'Rp ' + Number(num).toLocaleString('id-ID');
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    if (!toast) return;
    toastMsg.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}

function getStatusBadge(status) {
    const cls = status === 'completed' ? 'status-completed'
        : status === 'delivered' ? 'status-delivered'
        : status === 'shipped' ? 'status-shipped'
        : status === 'processing' ? 'status-processing'
        : 'status-cancelled';
    return `<span class="status-badge ${cls}">${status}</span>`;
}
