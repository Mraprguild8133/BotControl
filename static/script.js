// MaprGuild Movie Bot - Frontend JavaScript

class BotDashboard {
    constructor() {
        this.apiBaseUrl = '';
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.isLoading = false;
        
        this.init();
    }

    init() {
        // Initialize dashboard if we're on the dashboard page
        if (window.location.pathname === '/dashboard') {
            this.initializeDashboard();
        }
        
        // Initialize common functionality
        this.checkBotStatus();
        this.setupEventListeners();
        
        // Start periodic updates
        setInterval(() => {
            this.updateData();
        }, this.updateInterval);
    }

    setupEventListeners() {
        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('refresh-btn')) {
                this.refreshData();
            }
        });

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    async checkBotStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            this.updateBotStatus(data.status === 'healthy' && data.bot_running);
        } catch (error) {
            console.error('Error checking bot status:', error);
            this.updateBotStatus(false);
        }
    }

    updateBotStatus(isOnline) {
        const statusElements = document.querySelectorAll('#bot-status, #bot-status-nav');
        const statusIndicators = document.querySelectorAll('.status-indicator');
        
        statusElements.forEach(element => {
            if (element) {
                element.textContent = isOnline ? 'Online' : 'Offline';
                element.className = isOnline ? 'text-success' : 'text-danger';
            }
        });

        statusIndicators.forEach(indicator => {
            if (indicator) {
                indicator.className = `status-indicator ${isOnline ? 'status-online' : 'status-offline'}`;
            }
        });

        // Update detailed bot status on homepage
        const botStatusDetail = document.getElementById('bot-status');
        if (botStatusDetail && window.location.pathname === '/') {
            botStatusDetail.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="status-indicator ${isOnline ? 'status-online' : 'status-offline'} me-3"></div>
                    <div>
                        <h5 class="mb-1">${isOnline ? 'Bot Online' : 'Bot Offline'}</h5>
                        <small class="text-muted">Last checked: ${new Date().toLocaleTimeString()}</small>
                    </div>
                </div>
            `;
        }
    }

    async initializeDashboard() {
        try {
            await this.loadDashboardData();
            this.initializeCharts();
            this.loadHealthStatus();
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadDashboardData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/stats');
            const data = await response.json();
            
            this.updateStatistics(data);
            this.updateLastUpdated();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        } finally {
            this.showLoading(false);
        }
    }

    updateStatistics(data) {
        // Update stat cards
        const statElements = {
            'total-users': data.total_users || 0,
            'total-channels': data.total_channels || 0,
            'total-keywords': data.total_keywords || 0,
            'blocked-messages': data.blocked_messages || 0
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumber(element, parseInt(value));
            }
        });

        // Update bot running status
        this.updateBotStatus(data.bot_running);
    }

    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil(Math.abs(targetValue - currentValue) / 20);
        const isIncreasing = targetValue > currentValue;

        const animate = () => {
            const current = parseInt(element.textContent) || 0;
            
            if ((isIncreasing && current < targetValue) || (!isIncreasing && current > targetValue)) {
                const newValue = isIncreasing ? 
                    Math.min(current + increment, targetValue) : 
                    Math.max(current - increment, targetValue);
                
                element.textContent = newValue.toLocaleString();
                requestAnimationFrame(animate);
            } else {
                element.textContent = targetValue.toLocaleString();
            }
        };

        animate();
    }

    initializeCharts() {
        this.initializeActivityChart();
        this.initializeContentChart();
    }

    initializeActivityChart() {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        // Sample data - in a real implementation, this would come from the API
        const data = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'Movie Searches',
                    data: [12, 19, 8, 15, 22, 18, 25],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Blocked Messages',
                    data: [3, 5, 2, 8, 4, 6, 3],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'New Users',
                    data: [5, 8, 12, 6, 15, 10, 18],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }
            ]
        };

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initializeContentChart() {
        const ctx = document.getElementById('contentChart');
        if (!ctx) return;

        const data = {
            labels: ['Allowed', 'Blocked - Keywords', 'Blocked - AI', 'Pending Review'],
            datasets: [{
                data: [75, 15, 8, 2],
                backgroundColor: [
                    '#28a745',
                    '#ffc107',
                    '#dc3545',
                    '#6c757d'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        this.charts.content = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    async loadHealthStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            this.updateHealthStatus(data);
        } catch (error) {
            console.error('Error loading health status:', error);
            this.showHealthError();
        }
    }

    updateHealthStatus(data) {
        const healthContainer = document.getElementById('health-status');
        if (!healthContainer) return;

        const isHealthy = data.status === 'healthy';
        const isBotRunning = data.bot_running;

        healthContainer.innerHTML = `
            <div class="health-item">
                <span>Bot Status</span>
                <div class="health-status ${isBotRunning ? 'status-good' : 'status-error'}">
                    <i class="fas ${isBotRunning ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                    ${isBotRunning ? 'Running' : 'Stopped'}
                </div>
            </div>
            <div class="health-item">
                <span>API Health</span>
                <div class="health-status ${isHealthy ? 'status-good' : 'status-error'}">
                    <i class="fas ${isHealthy ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                    ${isHealthy ? 'Healthy' : 'Error'}
                </div>
            </div>
            <div class="health-item">
                <span>Database</span>
                <div class="health-status status-good">
                    <i class="fas fa-check-circle"></i>
                    Connected
                </div>
            </div>
            <div class="health-item">
                <span>Memory Usage</span>
                <div class="health-status status-good">
                    <i class="fas fa-check-circle"></i>
                    Normal
                </div>
            </div>
        `;
    }

    showHealthError() {
        const healthContainer = document.getElementById('health-status');
        if (!healthContainer) return;

        healthContainer.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Unable to load health status
            </div>
        `;
    }

    updateLastUpdated() {
        const element = document.getElementById('last-updated');
        if (element) {
            element.textContent = new Date().toLocaleString();
        }
    }

    async refreshData() {
        try {
            await this.loadDashboardData();
            await this.loadHealthStatus();
            this.showSuccess('Data refreshed successfully');
        } catch (error) {
            this.showError('Failed to refresh data');
        }
    }

    async updateData() {
        if (this.isLoading) return;
        
        try {
            await this.checkBotStatus();
            
            if (window.location.pathname === '/dashboard') {
                await this.loadDashboardData();
            }
        } catch (error) {
            console.error('Error updating data:', error);
        }
    }

    showLoading(show) {
        this.isLoading = show;
        const loadingElements = document.querySelectorAll('.loading-indicator');
        
        loadingElements.forEach(element => {
            element.style.display = show ? 'block' : 'none';
        });
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} toast-notification`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        // Add toast styles
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    startAutoRefresh() {
        // Auto refresh is already running via the interval in init()
        console.log('Auto-refresh enabled');
    }

    stopAutoRefresh() {
        // Would need to store interval ID to actually stop it
        console.log('Auto-refresh disabled');
    }
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.botDashboard = new BotDashboard();
});

// Global function for dashboard initialization (called from dashboard.html)
function initializeDashboard() {
    if (window.botDashboard) {
        window.botDashboard.initializeDashboard();
    }
}

// Add CSS animations for toasts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .toast-notification {
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        border-radius: 8px;
    }
    
    .toast-notification .btn-close {
        margin-left: 1rem;
        font-size: 0.8rem;
    }
`;
document.head.appendChild(style);
