// ExpenseTracker Main Application JavaScript
class ExpenseTracker {
    constructor() {
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeComponents();
        this.setupAjaxCSRF();
    }

    // Initialize all event listeners
    initializeEventListeners() {
        // Quick actions
        this.setupQuickActions();
        
        // Filter handling
        this.setupFilterHandlers();
    }

    // Initialize components
    initializeComponents() {
        this.initializeTooltips();
        this.updateProgressBars();
    }

    // Setup quick action buttons
    setupQuickActions() {
        // Quick filter buttons
        const quickFilters = document.querySelectorAll('.quick-filter');
        quickFilters.forEach(filter => {
            filter.addEventListener('click', (e) => this.handleQuickFilter(e));
        });
    }

    // Setup filter handlers
    setupFilterHandlers() {
        // Real-time filtering
        const realtimeFilters = document.querySelectorAll('.realtime-filter');
        realtimeFilters.forEach(filter => {
            filter.addEventListener('input', 
                this.debounce((e) => this.handleRealtimeFilter(e), 300)
            );
        });
    }

    // Handle quick filter
    handleQuickFilter(e) {
        e.preventDefault();
        const filterType = e.target.dataset.filter;
        const filterValue = e.target.dataset.value;
        
        this.applyFilter(filterType, filterValue);
        
        // Update active state
        document.querySelectorAll('.quick-filter').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.classList.add('active');
    }

    // Handle real-time filter
    handleRealtimeFilter(e) {
        const filterValue = e.target.value.toLowerCase();
        const items = document.querySelectorAll('.filterable-item');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(filterValue)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Apply filter to data
    applyFilter(type, value) {
        console.log(`Applying filter: ${type} = ${value}`);
        
        // Show loading state
        this.showLoadingState();
        
        // Simulate API call
        setTimeout(() => {
            this.hideLoadingState();
            this.showNotification(`Filter applied: ${type} = ${value}`, 'info');
        }, 500);
    }

    // Initialize tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Update progress bars
    updateProgressBars() {
        document.querySelectorAll('.budget-progress').forEach(bar => {
            const spent = parseFloat(bar.dataset.spent);
            const total = parseFloat(bar.dataset.total);
            const percentage = Math.min((spent / total) * 100, 100);
            
            bar.style.width = `${percentage}%`;
            
            // Update color based on percentage
            if (percentage > 100) {
                bar.classList.add('bg-danger');
                bar.classList.remove('bg-warning', 'bg-success');
            } else if (percentage > 80) {
                bar.classList.add('bg-warning');
                bar.classList.remove('bg-danger', 'bg-success');
            } else {
                bar.classList.add('bg-success');
                bar.classList.remove('bg-danger', 'bg-warning');
            }
        });
    }

    // Show loading state
    showLoadingState(element = document.body) {
        element.classList.add('loading');
    }

    // Hide loading state
    hideLoadingState(element = document.body) {
        element.classList.remove('loading');
    }

    // Show notification
    showNotification(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        
        const icon = this.getNotificationIcon(type);
        toast.innerHTML = `
            ${icon} ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    // Get notification icon
    getNotificationIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle me-2"></i>',
            error: '<i class="fas fa-exclamation-triangle me-2"></i>',
            warning: '<i class="fas fa-exclamation-circle me-2"></i>',
            info: '<i class="fas fa-info-circle me-2"></i>'
        };
        return icons[type] || icons.info;
    }

    // Setup AJAX CSRF token
    setupAjaxCSRF() {
        const csrftoken = this.getCSRFToken();
    }

    // Get CSRF token from cookies
    getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Utility functions
const ExpenseUtils = {
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseTracker = new ExpenseTracker();
    window.ExpenseUtils = ExpenseUtils;
});