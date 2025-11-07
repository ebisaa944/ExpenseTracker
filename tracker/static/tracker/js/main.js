// ExpenseTracker Main Application JavaScript
class ExpenseTracker {
    constructor() {
        this.charts = new Map();
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeComponents();
        this.setupAjaxCSRF();
        this.setupAnimations();
    }

    // Initialize all event listeners
    initializeEventListeners() {
        // Quick actions
        this.setupQuickActions();
        
        // Filter handling
        this.setupFilterHandlers();
        
        // Form interactions
        this.setupFormInteractions();
        
        // Card interactions
        this.setupCardInteractions();
    }

    // Initialize components
    initializeComponents() {
        this.initializeTooltips();
        this.updateProgressBars();
        this.initializeCharts();
        this.setupCounters();
    }

    // Setup quick action buttons with animations
    setupQuickActions() {
        const quickFilters = document.querySelectorAll('.quick-filter');
        quickFilters.forEach(filter => {
            filter.addEventListener('click', (e) => this.handleQuickFilter(e));
            this.addHoverEffect(filter);
        });

        // Add floating action button for mobile
        this.createFloatingActionButton();
    }

    // Setup filter handlers with enhanced UX
    setupFilterHandlers() {
        const realtimeFilters = document.querySelectorAll('.realtime-filter');
        realtimeFilters.forEach(filter => {
            filter.addEventListener('input', 
                this.debounce((e) => this.handleRealtimeFilter(e), 300)
            );
            
            // Add clear button to search inputs
            if (filter.type === 'search' || filter.dataset.type === 'search') {
                this.addClearButton(filter);
            }
        });

        // Date range picker enhancement
        this.enhanceDatePickers();
    }

    // Setup form interactions
    setupFormInteractions() {
        // Form validation with real-time feedback
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            this.enhanceFormValidation(form);
        });

        // Dynamic form fields
        this.setupDynamicFormFields();
    }

    // Setup card interactions
    setupCardInteractions() {
        const cards = document.querySelectorAll('.interactive-card');
        cards.forEach(card => {
            this.addCardInteractions(card);
        });

        // Budget cards with expandable details
        const budgetCards = document.querySelectorAll('.budget-card');
        budgetCards.forEach(card => {
            this.addBudgetCardInteractions(card);
        });
    }

    // Handle quick filter with animation
    handleQuickFilter(e) {
        e.preventDefault();
        const filterType = e.target.dataset.filter;
        const filterValue = e.target.dataset.value;
        
        // Add click animation
        this.animateButtonClick(e.target);
        
        this.applyFilter(filterType, filterValue);
        
        // Update active state with transition
        document.querySelectorAll('.quick-filter').forEach(btn => {
            btn.classList.remove('active', 'pulse');
        });
        e.target.classList.add('active', 'pulse');
        
        // Remove pulse after animation
        setTimeout(() => {
            e.target.classList.remove('pulse');
        }, 600);
    }

    // Enhanced real-time filter with smooth transitions
    handleRealtimeFilter(e) {
        const filterValue = e.target.value.toLowerCase();
        const container = e.target.closest('.filter-container');
        const items = container ? container.querySelectorAll('.filterable-item') : document.querySelectorAll('.filterable-item');
        
        let visibleCount = 0;
        
        items.forEach((item, index) => {
            const text = item.textContent.toLowerCase();
            const shouldShow = text.includes(filterValue);
            
            // Smooth transition
            if (shouldShow) {
                visibleCount++;
                item.style.display = '';
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 50);
            } else {
                item.style.opacity = '0';
                item.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    item.style.display = 'none';
                }, 300);
            }
        });

        // Show empty state if no results
        this.toggleEmptyState(container, visibleCount === 0);
    }

    // Apply filter to data with enhanced loading
    applyFilter(type, value) {
        console.log(`Applying filter: ${type} = ${value}`);
        
        // Show loading state with progress
        this.showLoadingState();
        
        // Simulate API call with progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            this.updateLoadingProgress(progress);
            if (progress >= 100) {
                clearInterval(progressInterval);
                this.hideLoadingState();
                this.showNotification(`Filter applied: ${type} = ${value}`, 'success');
                
                // Update charts if they exist
                this.updateCharts();
            }
        }, 50);
    }

    // Initialize tooltips with custom styling
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus',
                customClass: 'expense-tooltip'
            });
        });
    }

    // Enhanced progress bars with animation
    updateProgressBars() {
        document.querySelectorAll('.budget-progress').forEach(bar => {
            const spent = parseFloat(bar.dataset.spent);
            const total = parseFloat(bar.dataset.total);
            const percentage = Math.min((spent / total) * 100, 100);
            
            // Animate progress bar
            setTimeout(() => {
                bar.style.width = `${percentage}%`;
                bar.style.transition = 'width 1s ease-in-out';
            }, 100);
            
            // Update color and add warning indicators
            this.updateProgressBarColor(bar, percentage);
            
            // Add percentage text
            this.addProgressText(bar, percentage, spent, total);
        });
    }

    // Update progress bar color with thresholds
    updateProgressBarColor(bar, percentage) {
        bar.classList.remove('bg-danger', 'bg-warning', 'bg-success', 'bg-info');
        
        if (percentage > 100) {
            bar.classList.add('bg-danger');
            bar.parentElement.classList.add('budget-over-limit');
        } else if (percentage > 80) {
            bar.classList.add('bg-warning');
            bar.parentElement.classList.add('budget-warning');
        } else if (percentage > 50) {
            bar.classList.add('bg-info');
        } else {
            bar.classList.add('bg-success');
        }
    }

    // Add percentage text to progress bars
    addProgressText(bar, percentage, spent, total) {
        const parent = bar.parentElement;
        let textElement = parent.querySelector('.progress-text');
        
        if (!textElement) {
            textElement = document.createElement('div');
            textElement.className = 'progress-text';
            parent.appendChild(textElement);
        }
        
        textElement.innerHTML = `
            <small class="text-muted">
                ${ExpenseUtils.formatCurrency(spent)} / ${ExpenseUtils.formatCurrency(total)} 
                (${percentage.toFixed(1)}%)
            </small>
        `;
    }

    // Initialize charts with interactive features
    initializeCharts() {
        const chartContainers = document.querySelectorAll('[data-chart]');
        
        chartContainers.forEach(container => {
            const chartType = container.dataset.chart;
            const ctx = container.getContext('2d');
            
            switch(chartType) {
                case 'expense-breakdown':
                    this.createExpenseBreakdownChart(ctx, container.dataset);
                    break;
                case 'budget-progress':
                    this.createBudgetProgressChart(ctx, container.dataset);
                    break;
                case 'spending-trend':
                    this.createSpendingTrendChart(ctx, container.dataset);
                    break;
            }
        });
    }

    // Create expense breakdown chart
    createExpenseBreakdownChart(ctx, data) {
        const chartData = JSON.parse(data.values || '{}');
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(chartData),
                datasets: [{
                    data: Object.values(chartData),
                    backgroundColor: [
                        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
                        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        onClick: (e, legendItem, legend) => {
                            // Custom click handler for legend
                            const index = legendItem.datasetIndex;
                            const ci = legend.chart;
                            const meta = ci.getDatasetMeta(index);

                            meta.hidden = meta.hidden === null ? 
                                !ci.data.datasets[index].hidden : null;
                            ci.update();
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${ExpenseUtils.formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                },
                onClick: (e, activeElements) => {
                    if (activeElements.length > 0) {
                        const index = activeElements[0].index;
                        const label = chart.data.labels[index];
                        this.applyFilter('category', label);
                    }
                }
            }
        });

        this.charts.set('expense-breakdown', chart);
    }

    // Setup animated counters
    setupCounters() {
        const counters = document.querySelectorAll('.animated-counter');
        
        counters.forEach(counter => {
            const target = parseFloat(counter.dataset.target);
            const duration = parseInt(counter.dataset.duration) || 2000;
            const suffix = counter.dataset.suffix || '';
            
            this.animateCounter(counter, 0, target, duration, suffix);
        });
    }

    // Animate number counters
    animateCounter(element, start, end, duration, suffix = '') {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            
            element.textContent = suffix === '$' ? 
                ExpenseUtils.formatCurrency(value) : value + suffix;
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        globalThis.requestAnimationFrame(step);
    }

    // Show enhanced loading state
    showLoadingState(element = document.body) {
        element.classList.add('loading');
        
        // Create loading overlay if it doesn't exist
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading...</p>
                    <div class="progress mt-2" style="height: 4px; width: 100px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        
        overlay.style.display = 'flex';
    }

    // Update loading progress
    updateLoadingProgress(progress) {
        const progressBar = document.querySelector('.loading-overlay .progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    // Hide loading state
    hideLoadingState(element = document.body) {
        element.classList.remove('loading');
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // Enhanced notification system
    showNotification(message, type = 'info', duration = 5000) {
        const toastContainer = this.getToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-bg-${type} border-0`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${this.getNotificationIcon(type)} ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.remove();
            }
        }, duration);

        return toastId;
    }

    // Get toast container
    getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    // Setup animations
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        // Observe elements for animation
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // Add hover effects to elements
    addHoverEffect(element) {
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'translateY(-2px)';
            element.style.transition = 'all 0.3s ease';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = 'translateY(0)';
        });
    }

    // Animate button clicks
    animateButtonClick(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }

    // Add clear button to search inputs
    addClearButton(input) {
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'btn-clear-search';
        clearBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearBtn.style.cssText = `
            position: absolute;
            right: '10px';
            top: '50%';
            transform: 'translateY(-50%)';
            background: none;
            border: none;
            color: '#6c757d';
            display: none;
        `;
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(clearBtn);
        
        input.addEventListener('input', () => {
            clearBtn.style.display = input.value ? 'block' : 'none';
        });
        
        clearBtn.addEventListener('click', () => {
            input.value = '';
            input.focus();
            clearBtn.style.display = 'none';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    }

    // Toggle empty state
    toggleEmptyState(container, isEmpty) {
        let emptyState = container.querySelector('.empty-state');
        
        if (isEmpty && !emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'empty-state text-center py-5';
            emptyState.innerHTML = `
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">No items found</p>
            `;
            container.appendChild(emptyState);
        } else if (!isEmpty && emptyState) {
            emptyState.remove();
        }
    }

    // Create floating action button for mobile
    createFloatingActionButton() {
        if (window.innerWidth < 768) {
            const fab = document.createElement('button');
            fab.className = 'fab btn btn-primary rounded-circle';
            fab.innerHTML = '<i class="fas fa-plus"></i>';
            fab.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            `;
            
            fab.addEventListener('click', () => {
                // Trigger add expense action
                const addBtn = document.querySelector('[data-action="add-expense"]');
                if (addBtn) addBtn.click();
            });
            
            document.body.appendChild(fab);
        }
    }

    // Update charts when data changes
    updateCharts() {
        this.charts.forEach((chart, key) => {
            // Simulate data update - in real app, this would fetch new data
            chart.update();
        });
    }

    // Setup AJAX CSRF token
    setupAjaxCSRF() {
        const csrftoken = this.getCSRFToken();
        // Your existing CSRF setup code...
    }

    // Get CSRF token from cookies
    getCSRFToken() {
        // Your existing CSRF token code...
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

// Enhanced utility functions
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

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
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
    },

    // New utility: Calculate percentage
    calculatePercentage(part, total) {
        return total === 0 ? 0 : (part / total) * 100;
    },

    // New utility: Generate random color
    generateColor(index) {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#82E0AA', '#F8C471', '#85C1E9'
        ];
        return colors[index % colors.length];
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseTracker = new ExpenseTracker();
    window.ExpenseUtils = ExpenseUtils;
    
    // Add CSS for new interactive elements
    const style = document.createElement('style');
    style.textContent = `
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .animate-on-scroll.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .pulse {
            animation: pulse 0.6s ease-in-out;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.9);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .fab {
            animation: fadeInUp 0.3s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .expense-tooltip .tooltip-inner {
            background: #333;
            color: white;
            border-radius: 8px;
            padding: 8px 12px;
        }
    `;
    document.head.appendChild(style);
});