// ExpenseTracker Enhanced Charts Management
class ExpenseCharts {
    constructor() {
        this.charts = new Map();
        this.chartData = new Map();
        this.init();
    }

    init() {
        this.initializeCharts();
        this.setupChartInteractions();
        this.setupDataRefresh();
    }

    // Initialize all charts on the page
    initializeCharts() {
        this.initSpendingTrendChart();
        this.initCategoryDistributionChart();
        this.initBudgetProgressChart();
        this.initMonthlyComparisonChart();
        this.initExpenseHeatmapChart();
    }

    // Setup chart interactions and event listeners
    setupChartInteractions() {
        // Chart type toggles
        this.setupChartToggles();
        
        // Time period filters
        this.setupTimeFilters();
        
        // Chart export functionality
        this.setupChartExport();
    }

    // Setup automatic data refresh
    setupDataRefresh() {
        // Refresh charts every 30 seconds if visible
        setInterval(() => {
            if (this.isAnyChartVisible()) {
                this.refreshChartData();
            }
        }, 30000);
    }

    // Spending trend line chart with enhanced features
    initSpendingTrendChart() {
        const ctx = document.getElementById('spendingTrendChart');
        if (!ctx) return;

        this.loadSpendingTrendData().then(data => {
            this.createSpendingTrendChart(ctx, data);
        });
    }

    async loadSpendingTrendData(timeRange = '6months') {
        // Simulate API call - replace with actual endpoint
        return new Promise((resolve) => {
            setTimeout(() => {
                const sampleData = {
                    '1month': [
                        { date: '2024-01-01', amount: 1200 },
                        { date: '2024-01-08', amount: 1500 },
                        { date: '2024-01-15', amount: 1300 },
                        { date: '2024-01-22', amount: 1700 },
                        { date: '2024-01-29', amount: 1600 }
                    ],
                    '3months': [
                        { month: 'Nov', amount: 1400 },
                        { month: 'Dec', amount: 1800 },
                        { month: 'Jan', amount: 1600 }
                    ],
                    '6months': [
                        { month: 'Aug', amount: 1200 },
                        { month: 'Sep', amount: 1500 },
                        { month: 'Oct', amount: 1300 },
                        { month: 'Nov', amount: 1700 },
                        { month: 'Dec', amount: 1600 },
                        { month: 'Jan', amount: 1400 }
                    ],
                    '1year': [
                        { month: 'Jan', amount: 1200 }, { month: 'Feb', amount: 1500 },
                        { month: 'Mar', amount: 1300 }, { month: 'Apr', amount: 1700 },
                        { month: 'May', amount: 1600 }, { month: 'Jun', amount: 1400 },
                        { month: 'Jul', amount: 1800 }, { month: 'Aug', amount: 1200 },
                        { month: 'Sep', amount: 1500 }, { month: 'Oct', amount: 1300 },
                        { month: 'Nov', amount: 1700 }, { month: 'Dec', amount: 1600 }
                    ]
                };

                resolve(sampleData[timeRange] || sampleData['6months']);
            }, 500);
        });
    }

    createSpendingTrendChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month || item.date),
                datasets: [{
                    label: 'Spending Trend',
                    data: data.map(item => item.amount),
                    borderColor: '#4361ee',
                    backgroundColor: this.createGradient(ctx, '#4361ee', 0.1),
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#4361ee',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#4361ee',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `$${context.parsed.y.toFixed(2)}`;
                            },
                            title: function(tooltipItems) {
                                return tooltipItems[0].label;
                            }
                        }
                    },
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x',
                        },
                        pan: {
                            enabled: true,
                            mode: 'x',
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const label = chart.data.labels[element.index];
                        const value = chart.data.datasets[0].data[element.index];
                        this.onChartPointClick('spendingTrend', { label, value });
                    }
                }
            }
        });

        this.charts.set('spendingTrend', chart);
        this.chartData.set('spendingTrend', data);
    }

    // Enhanced category distribution chart
    initCategoryDistributionChart() {
        const ctx = document.getElementById('categoryDistributionChart');
        if (!ctx) return;

        this.loadCategoryData().then(data => {
            this.createCategoryDistributionChart(ctx, data);
        });
    }

    async loadCategoryData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    labels: ['Food & Dining', 'Transportation', 'Utilities', 'Entertainment', 'Shopping', 'Healthcare', 'Education'],
                    data: [1200, 800, 400, 300, 600, 350, 250],
                    colors: ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0', '#4895ef', '#560bad']
                });
            }, 500);
        });
    }

    createCategoryDistributionChart(ctx, chartData) {
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: chartData.colors,
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: $${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const category = chart.data.labels[element.index];
                        this.onCategoryClick(category);
                    }
                }
            }
        });

        this.charts.set('categoryDistribution', chart);
    }

    // Budget progress chart
    initBudgetProgressChart() {
        const ctx = document.getElementById('budgetProgressChart');
        if (!ctx) return;

        this.loadBudgetData().then(data => {
            this.createBudgetProgressChart(ctx, data);
        });
    }

    async loadBudgetData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve([
                    { category: 'Food', spent: 450, budget: 600 },
                    { category: 'Transport', spent: 280, budget: 400 },
                    { category: 'Entertainment', spent: 150, budget: 200 },
                    { category: 'Shopping', spent: 320, budget: 300 },
                    { category: 'Utilities', spent: 180, budget: 250 }
                ]);
            }, 500);
        });
    }

    createBudgetProgressChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.category),
                datasets: [
                    {
                        label: 'Spent',
                        data: data.map(item => item.spent),
                        backgroundColor: data.map(item => 
                            item.spent > item.budget ? '#ef476f' : '#06d6a0'
                        ),
                        borderColor: data.map(item => 
                            item.spent > item.budget ? '#ef476f' : '#06d6a0'
                        ),
                        borderWidth: 1
                    },
                    {
                        label: 'Budget',
                        data: data.map(item => item.budget),
                        backgroundColor: 'rgba(100, 100, 100, 0.2)',
                        borderColor: 'rgba(100, 100, 100, 0.8)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        type: 'line',
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label;
                                const value = context.parsed.y;
                                const item = data[context.dataIndex];
                                
                                if (label === 'Spent') {
                                    const percentage = ((item.spent / item.budget) * 100).toFixed(1);
                                    const status = item.spent > item.budget ? 'Over' : 'Under';
                                    return `${label}: $${value} (${percentage}% - ${status} Budget)`;
                                }
                                return `${label}: $${value}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });

        this.charts.set('budgetProgress', chart);
    }

    // Monthly comparison chart
    initMonthlyComparisonChart() {
        const ctx = document.getElementById('monthlyComparisonChart');
        if (!ctx) return;

        this.loadComparisonData().then(data => {
            this.createMonthlyComparisonChart(ctx, data);
        });
    }

    async loadComparisonData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    currentYear: [1200, 1500, 1300, 1700, 1600, 1400],
                    previousYear: [1100, 1300, 1400, 1500, 1200, 1300]
                });
            }, 500);
        });
    }

    createMonthlyComparisonChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Current Year',
                        data: data.currentYear,
                        backgroundColor: 'rgba(67, 97, 238, 0.7)',
                        borderColor: '#4361ee',
                        borderWidth: 1
                    },
                    {
                        label: 'Previous Year',
                        data: data.previousYear,
                        backgroundColor: 'rgba(100, 100, 100, 0.5)',
                        borderColor: 'rgba(100, 100, 100, 0.8)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        stacked: false,
                    },
                    y: {
                        stacked: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });

        this.charts.set('monthlyComparison', chart);
    }

    // Expense heatmap chart (calendar view)
    initExpenseHeatmapChart() {
        const ctx = document.getElementById('expenseHeatmapChart');
        if (!ctx) return;

        this.loadHeatmapData().then(data => {
            this.createExpenseHeatmapChart(ctx, data);
        });
    }

    async loadHeatmapData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                // Generate sample heatmap data for current month
                const daysInMonth = new Date().getDate();
                const heatmapData = [];
                
                for (let i = 1; i <= daysInMonth; i++) {
                    heatmapData.push({
                        day: i,
                        amount: Math.floor(Math.random() * 200) // Random amount for demo
                    });
                }
                
                resolve(heatmapData);
            }, 500);
        });
    }

    createExpenseHeatmapChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.day),
                datasets: [{
                    label: 'Daily Spending',
                    data: data.map(item => item.amount),
                    backgroundColor: data.map(item => 
                        this.getHeatmapColor(item.amount)
                    ),
                    borderColor: data.map(item => 
                        this.getHeatmapColor(item.amount, 1)
                    ),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Day ${context.label}: $${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });

        this.charts.set('expenseHeatmap', chart);
    }

    // Setup chart type toggles
    setupChartToggles() {
        const toggles = document.querySelectorAll('[data-chart-toggle]');
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const chartId = toggle.dataset.chartToggle;
                const newType = toggle.dataset.chartType;
                this.toggleChartType(chartId, newType);
                
                // Update active state
                toggles.forEach(t => t.classList.remove('active'));
                toggle.classList.add('active');
            });
        });
    }

    // Setup time period filters
    setupTimeFilters() {
        const filters = document.querySelectorAll('[data-time-filter]');
        filters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                const chartId = filter.dataset.chartFilter;
                const timeRange = filter.dataset.timeRange;
                this.updateChartTimeRange(chartId, timeRange);
                
                // Update active state
                filters.forEach(f => f.classList.remove('active'));
                filter.classList.add('active');
            });
        });
    }

    // Setup chart export functionality
    setupChartExport() {
        const exportButtons = document.querySelectorAll('[data-chart-export]');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const chartId = button.dataset.chartExport;
                this.exportChart(chartId, button.dataset.exportFormat || 'png');
            });
        });
    }

    // Toggle chart type (e.g., line to bar)
    toggleChartType(chartId, newType) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.config.type = newType;
            chart.update();
        }
    }

    // Update chart time range
    async updateChartTimeRange(chartId, timeRange) {
        if (chartId === 'spendingTrend') {
            const data = await this.loadSpendingTrendData(timeRange);
            const chart = this.charts.get('spendingTrend');
            if (chart) {
                chart.data.labels = data.map(item => item.month || item.date);
                chart.data.datasets[0].data = data.map(item => item.amount);
                chart.update();
            }
        }
    }

    // Export chart as image
    exportChart(chartId, format = 'png') {
        const chart = this.charts.get(chartId);
        if (chart) {
            const link = document.createElement('a');
            link.download = `chart-${chartId}-${new Date().toISOString().split('T')[0]}.${format}`;
            link.href = chart.toBase64Image();
            link.click();
        }
    }

    // Refresh all chart data
    async refreshChartData() {
        const refreshPromises = [];
        
        if (this.charts.has('spendingTrend')) {
            refreshPromises.push(this.loadSpendingTrendData().then(data => {
                const chart = this.charts.get('spendingTrend');
                chart.data.datasets[0].data = data.map(item => item.amount);
                chart.update();
            }));
        }
        
        // Add similar refresh logic for other charts
        
        await Promise.all(refreshPromises);
        this.showNotification('Charts updated successfully', 'success');
    }

    // Check if any chart is visible
    isAnyChartVisible() {
        return Array.from(this.charts.keys()).some(chartId => {
            const canvas = document.querySelector(`#${chartId}Chart`);
            return canvas && this.isElementInViewport(canvas);
        });
    }

    // Utility: Check if element is in viewport
    isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Utility: Create gradient background
    createGradient(ctx, color, opacity = 0.1) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, this.hexToRgba(color, opacity));
        gradient.addColorStop(1, this.hexToRgba(color, 0));
        return gradient;
    }

    // Utility: Convert hex to rgba
    hexToRgba(hex, alpha = 1) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Utility: Get heatmap color based on amount
    getHeatmapColor(amount, alpha = 0.7) {
        if (amount < 50) return `rgba(76, 201, 240, ${alpha})`;
        if (amount < 100) return `rgba(67, 97, 238, ${alpha})`;
        if (amount < 150) return `rgba(114, 9, 183, ${alpha})`;
        return `rgba(247, 37, 133, ${alpha})`;
    }

    // Event handlers
    onChartPointClick(chartId, data) {
        console.log(`Chart ${chartId} point clicked:`, data);
        // You can trigger filtering or show detailed view
        window.expenseTracker.showNotification(`Selected: ${data.label} - $${data.value}`, 'info');
    }

    onCategoryClick(category) {
        console.log('Category clicked:', category);
        // Filter expenses by this category
        window.expenseTracker.applyFilter('category', category);
    }

    showNotification(message, type = 'info') {
        if (window.expenseTracker) {
            window.expenseTracker.showNotification(message, type);
        } else {
            // Fallback notification
            alert(message);
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseCharts = new ExpenseCharts();
});

// Add CSS for chart controls
const chartStyles = `
.chart-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.chart-toggle, .time-filter {
    padding: 6px 12px;
    border: 1px solid #dee2e6;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.chart-toggle:hover, .time-filter:hover {
    background: #f8f9fa;
}

.chart-toggle.active, .time-filter.active {
    background: #4361ee;
    color: white;
    border-color: #4361ee;
}

.chart-export {
    padding: 6px 12px;
    border: 1px solid #28a745;
    background: white;
    color: #28a745;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.chart-export:hover {
    background: #28a745;
    color: white;
}

.chart-container {
    position: relative;
    height: 400px;
    margin-bottom: 2rem;
}

.chart-header {
    display: flex;
    justify-content: between;
    align-items: center;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    .chart-controls {
        flex-direction: column;
    }
    
    .chart-container {
        height: 300px;
    }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = chartStyles;
document.head.appendChild(styleSheet);