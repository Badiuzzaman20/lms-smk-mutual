// ===================================
// LMS SMK Mutual - Main JavaScript
// ===================================

// Live Clock
function updateClock() {
    const el = document.getElementById('liveTime');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// Sidebar Toggle (Mobile)
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// Pertemuan Toggle (Accordion)
function toggleSection(id) {
    const body = document.getElementById(id);
    if (!body) return;
    const isOpen = body.classList.contains('open');
    body.classList.toggle('open');
    const header = body.previousElementSibling;
    if (header) {
        const chevron = header.querySelector('.chevron');
        if (chevron) chevron.style.transform = isOpen ? 'rotate(0)' : 'rotate(180deg)';
    }
}

// Modals
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}
// Close modal on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal') && e.target.classList.contains('open')) {
        e.target.classList.remove('open');
        document.body.style.overflow = '';
    }
});
// Close on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.open').forEach(m => {
            m.classList.remove('open');
            document.body.style.overflow = '';
        });
    }
});

// Tab switching
function switchTab(tabId, btnEl) {
    const container = btnEl.closest('.tabs-container');
    container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const tab = document.getElementById(tabId);
    if (tab) tab.classList.add('active');
    btnEl.classList.add('active');
}

// Password toggle
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    field.type = field.type === 'password' ? 'text' : 'password';
}

// Table search filter - supports two calling conventions:
// filterTable(query) - for monitoring page (targets #monitoringTable)
// filterTable(inputEl, tableId) - for other pages (targets table by ID)
function filterTable(queryOrInput, tableId) {
    let q, table;
    if (typeof queryOrInput === 'string') {
        // Called as filterTable(query) - monitoring page style
        q = queryOrInput.toLowerCase();
        table = document.getElementById('monitoringTable');
    } else {
        // Called as filterTable(inputEl, tableId) - other pages style
        q = queryOrInput.value.toLowerCase();
        table = document.getElementById(tableId);
    }
    if (!table) return;
    table.querySelectorAll('tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    });
}

// Auto-dismiss alerts after 5s
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(a => {
            a.style.opacity = '0';
            a.style.transition = 'opacity 0.5s ease';
            setTimeout(() => a.remove(), 500);
        });
    }, 5000);

    // Animate progress bars on load
    document.querySelectorAll('.progress-fill, .progress-bar-fill').forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => bar.style.width = target, 200);
    });

    // Add active class to first pertemuan if only one exists
    const firstBody = document.querySelector('.pertemuan-body');
    if (firstBody && document.querySelectorAll('.pertemuan-body').length === 1) {
        firstBody.classList.add('open');
    }
});
