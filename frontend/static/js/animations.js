/* VerdeBlock POS — GSAP Animations */

(function () {
  'use strict';

  function whenGsap(fn) {
    if (window.gsap) { fn(); return; }
    const t = setInterval(() => { if (window.gsap) { clearInterval(t); fn(); } }, 30);
  }

  /* ── Page entrance ──────────────────────────────────────── */
  function animatePageEntrance() {
    const content = document.querySelector('.vb-content');
    if (!content) return;

    const head = content.querySelector('.vb-page-head');
    if (head) {
      gsap.fromTo(head,
        { opacity: 0, y: -12 },
        { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out', clearProps: 'all' }
      );
    }

    const cards = content.querySelectorAll('.vb-card');
    if (cards.length) {
      gsap.fromTo(cards,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.45, stagger: 0.07, ease: 'power2.out', clearProps: 'all' }
      );
    }

    animateTableRows(content);
  }

  /* ── Table row stagger ──────────────────────────────────── */
  function animateTableRows(root) {
    root = root || document;
    const rows = root.querySelectorAll('.vb-table tbody tr');
    if (!rows.length) return;
    gsap.fromTo(rows,
      { opacity: 0, x: -10 },
      { opacity: 1, x: 0, duration: 0.3, stagger: 0.04, ease: 'power1.out', clearProps: 'all' }
    );
  }

  /* ── Dashboard number counters ──────────────────────────── */
  function animateCounters() {
    document.querySelectorAll('.vb-counter').forEach(el => {
      const raw = el.dataset.value;
      if (raw === undefined) return;
      const target = parseFloat(raw);
      const isMoney = el.dataset.money === '1';
      const obj = { val: 0 };
      gsap.to(obj, {
        val: target,
        duration: 1.1,
        ease: 'power2.out',
        onUpdate() {
          el.textContent = isMoney
            ? '$' + obj.val.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : Math.round(obj.val).toLocaleString('es-MX');
        }
      });
    });
  }

  /* ── Modal open animation ───────────────────────────────── */
  function animateModalOpen(container) {
    const backdrop = container.querySelector('.vb-modal-backdrop');
    const modal    = container.querySelector('.vb-modal');
    if (!backdrop || !modal) return;
    gsap.fromTo(backdrop,
      { opacity: 0 },
      { opacity: 1, duration: 0.22, ease: 'power1.out' }
    );
    gsap.fromTo(modal,
      { opacity: 0, scale: 0.93, y: -8 },
      { opacity: 1, scale: 1, y: 0, duration: 0.28, ease: 'back.out(1.4)', clearProps: 'all' }
    );
  }

  /* ── POS step transition (called from Alpine) ───────────── */
  window.vbAnimatePosStep = function (el, direction) {
    gsap.fromTo(el,
      { opacity: 0, x: (direction || 1) * 32 },
      { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out', clearProps: 'all' }
    );
  };

  /* ── Sidebar nav entrance ───────────────────────────────── */
  function animateSidebar() {
    const items = document.querySelectorAll('.vb-nav-item');
    if (!items.length) return;
    gsap.fromTo(items,
      { opacity: 0, x: -18 },
      { opacity: 1, x: 0, duration: 0.35, stagger: 0.055, ease: 'power2.out',
        delay: 0.05, clearProps: 'all' }
    );
  }

  /* ── Toast entrance ─────────────────────────────────────── */
  function animateToastLatest(wrap) {
    const toasts = wrap.querySelectorAll('.vb-toast');
    if (!toasts.length) return;
    const last = toasts[toasts.length - 1];
    gsap.fromTo(last,
      { opacity: 0, x: 60, scale: 0.88 },
      { opacity: 1, x: 0, scale: 1, duration: 0.36, ease: 'back.out(1.5)', clearProps: 'transform' }
    );
  }

  /* ── HTMX hooks ─────────────────────────────────────────── */
  function bindHtmxHooks() {
    document.body.addEventListener('htmx:afterSettle', function (e) {
      const target = e.detail.target;
      if (!target) return;
      animateTableRows(target);
      if (target.id === 'modal-container' && target.children.length) {
        animateModalOpen(target);
      }
    });
  }

  /* ── MutationObserver: modal & toast ────────────────────── */
  function watchModal() {
    const c = document.getElementById('modal-container');
    if (!c) return;
    new MutationObserver(() => {
      if (c.children.length) animateModalOpen(c);
    }).observe(c, { childList: true });
  }

  function watchToasts() {
    const wrap = document.querySelector('.vb-toast-wrap');
    if (!wrap) return;
    new MutationObserver(() => animateToastLatest(wrap))
      .observe(wrap, { childList: true, subtree: true });
  }

  /* ── Init ───────────────────────────────────────────────── */
  whenGsap(function () {
    animateSidebar();
    animatePageEntrance();
    animateCounters();
    bindHtmxHooks();
    watchToasts();
    watchModal();
  });

})();
