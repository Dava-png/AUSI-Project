const API_BASE = '/api';

const api = {
    async request(method, path, body) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(API_BASE + path, opts);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Request failed');
        return data;
    },
    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },
    del(path) { return this.request('DELETE', path); },

    // Auth
    login(email, password) { return this.post('/login', { email, password }); },
    register(name, email, password) { return this.post('/register', { name, email, password }); },
    logout() { return this.post('/logout'); },
    getUser() { return this.get('/user'); },
    updateUser(data) { return this.put('/user', data); },

    // Products
    getProducts() { return this.get('/products'); },
    createProduct(data) { return this.post('/products', data); },
    updateProduct(id, data) { return this.put('/products/' + id, data); },
    deleteProduct(id) { return this.del('/products/' + id); },

    // Services
    getServices() { return this.get('/services'); },
    getService(id) { return this.get('/services/' + id); },

    // Orders
    getOrders() { return this.get('/orders'); },
    createOrder(data) { return this.post('/orders', data); },
    updateOrderStatus(id, status) { return this.put('/orders/' + encodeURIComponent(id) + '/status', { status }); },
    deleteOrder(id) { return this.del('/orders/' + encodeURIComponent(id)); },

    // History
    // Admins
    getAdmins() { return this.get('/admins'); },

    // History
    getHistory() { return this.get('/history'); },

    // Chat
    getChats() { return this.get('/chats'); },
    createChat(data) { return this.post('/chats', data || {}); },
    getMessages(chatId) { return this.get('/chats/' + chatId + '/messages'); },
    sendMessage(chatId, text, sender) { return this.post('/chats/' + chatId + '/messages', { text, sender }); },
    markRead(chatId) { return this.put('/chats/' + chatId + '/read'); },
};
