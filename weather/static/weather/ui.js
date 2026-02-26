/**
 * Weather Application JavaScript
 * Handles real-time updates, API communication, and UI interactions
 */

class WeatherApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.updateInterval = 300000; // 5 minutes
        this.init();
    }

    /**
     * Initialize the weather app
     */
    init() {
        console.log('🌤️ Initializing Weather App...');
        this.setupEventListeners();
        this.loadWeatherData();
        this.startAutoRefresh();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[data-refresh]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadWeatherData());
        }

        // Location list items
        document.addEventListener('click', (e) => {
            if (e.target.closest('.location-item')) {
                const locationId = e.target.closest('.location-item').dataset.locationId;
                this.selectLocation(locationId);
            }
        });
    }

    /**
     * Load weather data from API
     */
    async loadWeatherData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/locations/`);
            if (!response.ok) throw new Error('Failed to fetch locations');
            
            const locations = await response.json();
            console.log('📍 Loaded locations:', locations);
            
            // Update UI with location data
            locations.forEach(location => {
                this.updateLocationWeather(location);
            });
        } catch (error) {
            console.error('❌ Error loading weather data:', error);
            this.showNotification('Error loading weather data', 'danger');
        }
    }

    /**
     * Update weather for a specific location
     */
    async updateLocationWeather(location) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/locations/${location.id}/current_weather/`);
            if (!response.ok) throw new Error('Failed to fetch weather');
            
            const weather = await response.json();
            console.log(`🌡️ Weather for ${location.name}:`, weather);
            
            // Update card if it exists
            const card = document.querySelector(`[data-location-id="${location.id}"]`);
            if (card) {
                this.updateWeatherCard(card, weather);
            }
        } catch (error) {
            console.error(`❌ Error updating weather for ${location.name}:`, error);
        }
    }

    /**
     * Update weather card with new data
     */
    updateWeatherCard(card, weather) {
        // Update temperature
        const tempElement = card.querySelector('.temperature');
        if (tempElement) {
            tempElement.textContent = `${Math.round(weather.temperature)}°C`;
        }

        // Update condition
        const conditionElement = card.querySelector('.condition-badge');
        if (conditionElement) {
            conditionElement.textContent = weather.condition.toUpperCase();
            conditionElement.className = `condition-badge condition-${weather.condition}`;
        }

        // Update humidity
        const humidityElement = card.querySelector('[data-weather="humidity"]');
        if (humidityElement) {
            humidityElement.textContent = `${weather.humidity}%`;
        }

        // Update wind speed
        const windElement = card.querySelector('[data-weather="wind"]');
        if (windElement) {
            windElement.textContent = `${weather.wind_speed.toFixed(1)} m/s`;
        }

        // Add animation
        card.classList.add('updated');
        setTimeout(() => card.classList.remove('updated'), 500);
    }

    /**
     * Select a location and show details
     */
    selectLocation(locationId) {
        // Remove active class from all items
        document.querySelectorAll('.location-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to selected item
        const selectedItem = document.querySelector(`[data-location-id="${locationId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        // Could load forecast or additional details here
        console.log('📌 Selected location:', locationId);
    }

    /**
     * Start auto-refresh of weather data
     */
    startAutoRefresh() {
        console.log('⏰ Starting auto-refresh...');
        this.autoRefreshInterval = setInterval(() => {
            console.log('🔄 Auto-refreshing weather data...');
            this.loadWeatherData();
        }, this.updateInterval);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            console.log('⏹️ Auto-refresh stopped');
        }
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    /**
     * Get temperature color based on value
     */
    getTemperatureColor(temp) {
        if (temp <= 0) return '#0000ff';
        if (temp <= 10) return '#00ffff';
        if (temp <= 20) return '#00ff00';
        if (temp <= 30) return '#ffff00';
        if (temp <= 40) return '#ff8800';
        return '#ff0000';
    }

    /**
     * Format temperature for display
     */
    formatTemperature(temp, unit = 'C') {
        if (unit === 'F') {
            return ((temp * 9/5) + 32).toFixed(1);
        }
        return temp.toFixed(1);
    }
}

/**
 * API Helper Functions
 */
class WeatherAPI {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Get all locations
     */
    async getLocations() {
        return fetch(`${this.baseUrl}/locations/`).then(r => r.json());
    }

    /**
     * Get specific location
     */
    async getLocation(id) {
        return fetch(`${this.baseUrl}/locations/${id}/`).then(r => r.json());
    }

    /**
     * Get current weather for location
     */
    async getCurrentWeather(locationId) {
        return fetch(`${this.baseUrl}/locations/${locationId}/current_weather/`).then(r => r.json());
    }

    /**
     * Get forecast for location
     */
    async getForecast(locationId, hours = 24) {
        return fetch(`${this.baseUrl}/locations/${locationId}/forecast/?hours=${hours}`).then(r => r.json());
    }

    /**
     * Get weather data
     */
    async getWeatherData(locationId = null) {
        let url = `${this.baseUrl}/weather/`;
        if (locationId) url += `?location=${locationId}`;
        return fetch(url).then(r => r.json());
    }

    /**
     * Manually update weather for location
     */
    async manualUpdate(locationId) {
        return fetch(`${this.baseUrl}/locations/${locationId}/update_weather/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        }).then(r => r.json());
    }

    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

/**
 * Initialize app when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    window.weatherApp = new WeatherApp();
    window.weatherAPI = new WeatherAPI();
    
    console.log('✅ Weather App initialized');
    console.log('Available: window.weatherApp, window.weatherAPI');
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', function() {
    if (window.weatherApp) {
        window.weatherApp.stopAutoRefresh();
    }
});
