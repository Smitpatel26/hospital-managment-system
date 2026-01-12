/* =====================================================
   HOSPITAL MANAGEMENT SYSTEM - JAVASCRIPT
   Main functionality and real-time updates
   ===================================================== */

// =============== DOCUMENT READY ===============
document.addEventListener('DOMContentLoaded', function () {
    // Initialize current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);

    // Initialize alerts
    loadAlerts();
    setInterval(loadAlerts, 30000); // Refresh every 30 seconds

    // Setup alert bell click
    setupAlertBell();
});

// =============== TIME DISPLAY ===============
function updateCurrentTime() {
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        const now = new Date();
        const options = {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        };
        timeElement.textContent = now.toLocaleDateString('en-IN', options);
    }
}

// =============== ALERTS SYSTEM ===============
function loadAlerts() {
    fetch('/api/alerts')
        .then(response => response.json())
        .then(alerts => {
            // Update count
            const countElement = document.getElementById('alertCount');
            if (countElement) {
                countElement.textContent = alerts.length;
                countElement.style.display = alerts.length > 0 ? 'block' : 'none';
            }

            // Update dropdown list
            const listElement = document.getElementById('alertsList');
            if (listElement) {
                if (alerts.length === 0) {
                    listElement.innerHTML = '<p class="no-alerts-text">No new alerts</p>';
                } else {
                    listElement.innerHTML = alerts.map(alert => `
                        <div class="alert-dropdown-item alert-${alert.severity.toLowerCase()}">
                            <div class="alert-dropdown-header">
                                <strong>${alert.type}</strong>
                                <span class="alert-time">${alert.created_at}</span>
                            </div>
                            <p>${alert.message}</p>
                            <button onclick="dismissAlert(${alert.alert_id})" class="alert-dismiss-btn">Dismiss</button>
                        </div>
                    `).join('');
                }
            }
        })
        .catch(error => console.error('Error loading alerts:', error));
}

function setupAlertBell() {
    const bell = document.getElementById('alertBell');
    const dropdown = document.getElementById('alertsDropdown');

    if (bell && dropdown) {
        bell.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function () {
            dropdown.classList.remove('show');
        });
    }
}

function dismissAlert(alertId) {
    fetch(`/api/alerts/${alertId}/read`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadAlerts();
            }
        });
}

// =============== MODAL FUNCTIONS ===============
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modal on escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            activeModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
});

// Close modal on background click
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// =============== UTILITY FUNCTIONS ===============
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// =============== NOTIFICATION TOAST ===============
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// =============== DATA REFRESH ===============
function refreshData() {
    // Refresh the current page data without full reload
    // This can be customized per page
    const path = window.location.pathname;

    if (path.includes('dashboard')) {
        // Refresh dashboard stats
        location.reload();
    } else if (path.includes('patients')) {
        // Refresh patient list
        location.reload();
    }
}

// =============== PRINT FUNCTIONALITY ===============
function printBill(billId) {
    // Open new window with bill details for printing
    window.open(`/api/bills/${billId}/print`, '_blank');
}

// =============== CONFIRMATION DIALOGS ===============
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// =============== FORM VALIDATION ===============
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// =============== ANIMATION ON SCROLL ===============
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}

// Initialize scroll animations
animateOnScroll();

// =============== EXPORT TO CSV ===============
function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    let csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push('"' + col.innerText.replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

console.log('Hospital Management System JS loaded successfully!');
