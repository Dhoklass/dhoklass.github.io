document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alerts
  document.querySelectorAll('.alert').forEach(a => {
    setTimeout(() => { a.style.transition = 'opacity .5s'; a.style.opacity = '0'; }, 4000);
    setTimeout(() => a.remove(), 4600);
  });
  // Role tab switcher
  const roleTabs = document.querySelectorAll('.role-tab');
  const roleInput = document.getElementById('role-input');
  roleTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      roleTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      if (roleInput) roleInput.value = tab.dataset.role;
    });
  });
  // Confirm destructive actions
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => { if (!confirm(btn.dataset.confirm)) e.preventDefault(); });
  });
  // Active sidebar link
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar__link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
  // FAQ chevron
  document.querySelectorAll('details').forEach(d => {
    d.addEventListener('toggle', () => {
      const icon = d.querySelector('.fa-chevron-down');
      if (icon) icon.style.transform = d.open ? 'rotate(180deg)' : 'rotate(0)';
    });
  });
  // Mark notifications read
  const bell = document.getElementById('notif-bell');
  if (bell) {
    bell.addEventListener('click', () => {
      fetch('/api/notifications/read', { method: 'POST' });
      document.querySelector('.notif-dot')?.remove();
    });
  }
  // Animate stat counters
  document.querySelectorAll('.stat-value').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step = Math.max(1, Math.ceil(target / 25));
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 40);
  });
});
