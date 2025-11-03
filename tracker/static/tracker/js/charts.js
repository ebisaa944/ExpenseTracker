// ExpenseTracker Charts Management
class ExpenseCharts {
    constructor() {
        this.charts = new Map();
        this.init();
    }

    init() {
        this.initializeCharts();
    }

    // Initialize all charts on the page
    initializeCharts() {
        this.initSpendingTrendChart();
        this.initCategoryDistributionChart();
    }

    // Spending trend line chart
    initSpendingTrendChart() {
        const ctx = document.getElementById('spendingTrendChart');
        if (!ctx) return;

        // Sample data - replace with actual API call
        const data = [
            { month: 'Jan', amount: 1200 },
            { month: 'Feb', amount: 1500 },
            { month: 'Mar', amount: 1300 },
            { month: 'Apr', amount: 1700 },
            { month: 'May', amount: 1600 },
            { month: 'Jun', amount: 1400 }
        ];

        this.createSpendingTrendChart(ctx, data);
    }

    createSpendingTrendChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month),
                datasets: [{
                    label: 'Monthly Spending',
                    data: data.map(item => item.amount),
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
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
                                return `$${context.parsed.y.toFixed(2)}`;
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

        this.charts.set('spendingTrend', chart);
    }

    // Category distribution chart
    initCategoryDistributionChart() {
        const ctx = document.getElementById('categoryDistributionChart');
        if (!ctx) return;

        // Sample data - replace with actual data
        const chartData = {
            labels: ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping'],
            data: [1200, 800, 400, 300, 600]
        };

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: [
                        '#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });

        this.charts.set('categoryDistribution', chart);
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.expenseCharts = new ExpenseCharts();
});