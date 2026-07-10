/* VerdeBlock POS — Alpine.js stores and utilities */

/* ---------- Helpers ---------- */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}
const money = n => '$' + (+(n) || 0).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const numFmt = n => (+(n) || 0).toLocaleString('es-MX');

/* ---------- Login PIN store ---------- */
function loginStore() {
  return {
    step: 'users',
    user: null,
    pin: '',
    error: '',
    pinOk: false,
    pinErr: false,
    users: JSON.parse(document.getElementById('login-users-data')?.textContent || '[]'),

    selectUser(u) {
      this.user = u;
      this.step = 'pin';
      this.pin = '';
      this.error = '';
      this.pinOk = false;
      this.pinErr = false;
    },

    back() {
      this.step = 'users';
      this.user = null;
      this.pin = '';
      this.error = '';
      this.pinOk = false;
      this.pinErr = false;
    },

    pressKey(k) {
      if (this.pinOk || this.pin.length >= 4) return;
      this.pin += k;
      this.error = '';
      this.pinErr = false;
      if (this.pin.length === 4) this.verify();
    },

    backspace() {
      this.pin = this.pin.slice(0, -1);
      this.pinErr = false;
      this.error = '';
    },

    async verify() {
      const res = await fetch('/auth/verify-pin/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ user_id: this.user.id, pin: this.pin }),
      });
      const data = await res.json();
      if (data.ok) {
        this.pinOk = true;
        setTimeout(() => { window.location = data.redirect || '/'; }, 700);
      } else {
        this.pinErr = true;
        this.pin = '';
        this.error = 'PIN incorrecto, inténtalo de nuevo';
        setTimeout(() => { this.pinErr = false; }, 600);
      }
    },

    get dots() { return [0,1,2,3].map(i => i < this.pin.length); },

    getColor(name, type) {
      const COLORS = [
        { soft:'#e8f6e6', ink:'#067a08' },
        { soft:'#e8f0fa', ink:'#3a72b8' },
        { soft:'#faf1d9', ink:'#9a6c03' },
        { soft:'#fbe9e5', ink:'#ad3525' },
        { soft:'#f0f0ff', ink:'#5b5bd6' },
        { soft:'#fdf0ff', ink:'#9333ea' },
      ];
      const idx = Math.abs([...(name||'')].reduce((s,c)=>s+c.charCodeAt(0),0)) % COLORS.length;
      return COLORS[idx][type];
    },
  };
}

/* ---------- Theme store ---------- */
function themeStore() {
  return {
    theme: localStorage.getItem('vb-theme') || 'light',
    fontscale: localStorage.getItem('vb-fontscale') || 'normal',
    init() { this._apply(); },
    toggle() {
      this.theme = this.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('vb-theme', this.theme);
      this._apply();
    },
    setScale(s) {
      this.fontscale = s;
      localStorage.setItem('vb-fontscale', s);
      document.documentElement.setAttribute('data-fontscale', s);
    },
    _apply() {
      document.documentElement.setAttribute('data-theme', this.theme);
      document.documentElement.setAttribute('data-fontscale', this.fontscale);
    },
  };
}

/* ---------- Sidebar store ---------- */
function sidebarStore() {
  return {
    collapsed: JSON.parse(localStorage.getItem('vb-sidebar') || 'false'),
    toggle() {
      this.collapsed = !this.collapsed;
      localStorage.setItem('vb-sidebar', this.collapsed);
    },
  };
}

/* ---------- Toast store ---------- */
function toastStore() {
  return {
    items: [],
    show(msg) {
      const id = Date.now() + Math.random();
      this.items.push({ id, msg });
      setTimeout(() => { this.items = this.items.filter(t => t.id !== id); }, 2600);
    },
  };
}

/* ---------- POS store ---------- */
function posStore() {
  return {
    step: 1,
    clienteId: null,
    clienteNombre: '',
    clienteTipo: 'Público',
    cart: [],       /* [{id, nombre, precio, stock, unidad, cant}] */
    iva: false,
    descPct: 0,
    metodo: 'Efectivo',
    precioTipo: 'auto',
    showSuccess: false,
    lastFolio: '',
    submitting: false,

    get canNext() {
      if (this.step === 1) return this.clienteId !== null;
      if (this.step === 2) return this.cart.length > 0;
      return true;
    },
    get piezas() { return this.cart.reduce((s,l) => s + l.cant, 0); },
    get sub() { return this.cart.reduce((s,l) => s + l.cant * l.precio, 0); },
    get descMonto() { return this.sub * this.descPct; },
    get base() { return this.sub - this.descMonto; },
    get ivaMonto() { return this.iva ? this.base * 0.16 : 0; },
    get total() { return this.base + this.ivaMonto; },

    selectCliente(id, nombre, tipo) {
      this.clienteId = id; this.clienteNombre = nombre; this.clienteTipo = tipo;
    },

    addProduct(id, nombre, precioUnitario, precioMayoreo, stock, unidad) {
      const precio = this.precioTipo === 'mayoreo' ? precioMayoreo
        : this.precioTipo === 'unitario' ? precioUnitario
        : this.clienteTipo === 'Mayoreo' ? precioMayoreo : precioUnitario;
      const step = unidad === 'pieza' ? 10 : 1;
      const ex = this.cart.find(l => l.id === id);
      if (ex) { ex.cant += step; }
      else { this.cart.push({ id, nombre, precio, stock, unidad, cant: step }); }
      this.cart = [...this.cart];
    },

    updateQty(id, val) {
      const v = parseInt(val) || 0;
      if (v <= 0) { this.cart = this.cart.filter(l => l.id !== id); }
      else { const l = this.cart.find(l => l.id === id); if (l) l.cant = v; this.cart = [...this.cart]; }
    },

    removeLine(id) { this.cart = this.cart.filter(l => l.id !== id); },

    inCart(id) { const l = this.cart.find(l => l.id === id); return l ? l.cant : 0; },

    updatePrices() {
      this.cart = this.cart.map(l => {
        const raw = document.querySelector(`[data-prod-id="${l.id}"]`);
        if (!raw) return l;
        const pu = parseFloat(raw.dataset.precio || l.precio);
        const pm = parseFloat(raw.dataset.mayoreo || l.precio);
        const precio = this.precioTipo === 'mayoreo' ? pm
          : this.precioTipo === 'unitario' ? pu
          : this.clienteTipo === 'Mayoreo' ? pm : pu;
        return { ...l, precio };
      });
    },

    next() { if (this.canNext && this.step < 3) this.step++; },
    prev() { if (this.step > 1) this.step--; },
    goStep(s) { if (s < this.step) this.step = s; },

    async confirmar() {
      if (this.submitting) return;
      this.submitting = true;
      try {
        const res = await fetch('/sales/create/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
          body: JSON.stringify({
            cliente_id: this.clienteId,
            metodo: this.metodo,
            iva: this.iva,
            desc_pct: this.descPct,
            precio_tipo: this.precioTipo,
            items: this.cart.map(l => ({ product_id: l.id, cant: l.cant, precio: l.precio })),
          }),
        });
        const data = await res.json();
        if (data.ok) {
          this.lastFolio = data.folio;
          this.showSuccess = true;
        }
      } finally {
        this.submitting = false;
      }
    },

    reset() {
      this.step = 1; this.clienteId = null; this.clienteNombre = '';
      this.clienteTipo = 'Público'; this.cart = []; this.iva = false;
      this.descPct = 0; this.metodo = 'Efectivo'; this.precioTipo = 'auto';
      this.showSuccess = false; this.lastFolio = '';
    },

    formatMoney(n) { return money(n); },
    formatNum(n) { return numFmt(n); },
  };
}

/* ---------- Product modal store ---------- */
function productoModalStore() {
  return {
    open: false,
    prod: null,
    movType: 'entrada',
    movCant: '',
    movNota: '',
    saving: false,
    history: [],

    show(prodData) {
      this.prod = { ...prodData };
      this.open = true;
      this.movType = 'entrada';
      this.movCant = '';
      this.movNota = '';
      this.loadHistory();
    },
    close() { this.open = false; this.prod = null; this.history = []; },

    async loadHistory() {
      if (!this.prod) return;
      const res = await fetch(`/products/${this.prod.id}/movements/`);
      if (res.ok) this.history = await res.json();
    },

    async guardar() {
      if (this.saving || !this.movCant || parseInt(this.movCant) <= 0) return;
      this.saving = true;
      try {
        const res = await fetch(`/products/${this.prod.id}/movement/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
          body: JSON.stringify({ tipo: this.movType, cantidad: parseInt(this.movCant), nota: this.movNota }),
        });
        if (res.ok) {
          const data = await res.json();
          this.prod.stock = data.stock;
          this.movCant = ''; this.movNota = '';
          this.history.unshift(data.mov);
          // trigger table refresh via HTMX event
          document.dispatchEvent(new CustomEvent('products:reload'));
          Alpine.store('toast').show(`Stock actualizado: ${numFmt(data.stock)} unidades`);
        }
      } finally { this.saving = false; }
    },

    get stockColor() {
      if (!this.prod) return 'var(--text-muted)';
      if (this.prod.stock <= this.prod.min) return 'var(--danger-ink)';
      if (this.prod.stock <= this.prod.min * 1.5) return 'var(--warn-ink)';
      return 'var(--ok-ink)';
    },
    get stockLabel() {
      if (!this.prod) return '';
      if (this.prod.stock <= 0) return 'Sin existencias';
      if (this.prod.stock <= this.prod.min) return 'Stock bajo';
      return 'En stock';
    },
    formatMoney(n) { return money(n); },
    formatNum(n) { return numFmt(n); },
  };
}

/* ---------- Register stores on Alpine init ---------- */
document.addEventListener('alpine:init', () => {
  Alpine.store('theme', themeStore());
  Alpine.store('sidebar', sidebarStore());
  Alpine.store('toast', toastStore());
});

/* ---------- HTMX toast integration ---------- */
document.addEventListener('htmx:afterRequest', e => {
  const msg = e.detail.xhr.getResponseHeader('X-Toast');
  if (msg) Alpine.store('toast').show(decodeURIComponent(msg));
});

/* ---------- Apply theme/fontscale on load (before Alpine init) ---------- */
(function() {
  const t = localStorage.getItem('vb-theme') || 'light';
  const fs = localStorage.getItem('vb-fontscale') || 'normal';
  document.documentElement.setAttribute('data-theme', t);
  document.documentElement.setAttribute('data-fontscale', fs);
})();
