document:addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const checkAlertsBtn = document.getElementById('check-alerts-btn');
    const alertsContainer = document.getElementById('alerts-container');
    const timerContainer = document.getElementById('timer-container');
    const approvedLocationsDatalist = document.getElementById('approved-locations');
    const liveSyncIndicator = document.getElementById('live-sync-indicator');
    const syncStatusText = document.getElementById('sync-status-text');

    let userLocation = '';
    let fetchInterval;
    let errorCounter = 0;
    let approvedLocations = [];
    
    // Timer state
    let lastAlertTimestamp = null;
    let lastAlertStatus = null;
    let lastAlertMessage = null;
    let lastAlertTitle = null;
    let timerInterval = null;
    let currentAlertsSignature = ''; // For checking if alerts changed

    // Live Sync state
    let lastSuccessfulSync = null;
    let statusUpdateInterval = null;

    const updateSyncStatusDisplay = () => {
        if (!syncStatusText) return;

        if (liveSyncIndicator.classList.contains('error')) {
            syncStatusText.textContent = 'Offline';
            return;
        }

        if (liveSyncIndicator.classList.contains('syncing')) {
            syncStatusText.textContent = 'Updating...';
            return;
        }

        if (!lastSuccessfulSync) {
            syncStatusText.textContent = 'Live';
            return;
        }

        const now = new Date();
        const diffSeconds = Math.floor((now - lastSuccessfulSync) / 1000);

        if (diffSeconds > 10) {
            liveSyncIndicator.classList.add('stale');
            liveSyncIndicator.classList.remove('active');
        } else {
            liveSyncIndicator.classList.remove('stale');
            liveSyncIndicator.classList.add('active');
        }

        if (diffSeconds < 1) {
            syncStatusText.textContent = 'Live: Just now';
        } else {
            syncStatusText.textContent = `Live: ${diffSeconds}s ago`;
        }
    };

    // Start status update interval
    if (!statusUpdateInterval) {
        statusUpdateInterval = setInterval(updateSyncStatusDisplay, 1000);
    }

    const fetchApprovedLocations = async () => {
        try {
            const response = await fetch('/api/approved-locations');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            approvedLocations = data.locations;
            // Clear previous options to avoid duplicates
            while (approvedLocationsDatalist.firstChild) {
                approvedLocationsDatalist.removeChild(approvedLocationsDatalist.firstChild);
            }
            approvedLocations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                approvedLocationsDatalist.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching approved locations:', error);
        }
    };

    // Fetch all alerts (not just active)
    const fetchAllAlerts = async () => {
        if (!userLocation) {
            alertsContainer.innerHTML = '<div class="alert-loading">Enter a location to begin.</div>';
            return [];
        }
        
        if (liveSyncIndicator) {
            liveSyncIndicator.classList.add('syncing');
            liveSyncIndicator.classList.remove('error');
            updateSyncStatusDisplay();
        }

        try {
            const url = `/api/alerts/all?location=${encodeURIComponent(userLocation)}`;
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            errorCounter = 0;
            lastSuccessfulSync = new Date();
            
            if (liveSyncIndicator) {
                liveSyncIndicator.classList.remove('error');
            }
            
            return {
                alerts: data.alerts || [],
                syncing: data.syncing || false
            };
        } catch (error) {
            console.error('Error fetching all alerts:', error);
            errorCounter++;
            if (errorCounter >= 3) {
                alertsContainer.innerHTML = `<div class="alert-error">Reconnecting...</div>`;
                if (liveSyncIndicator) {
                    liveSyncIndicator.classList.add('error');
                    liveSyncIndicator.classList.remove('active', 'syncing', 'stale');
                }
            }
            return { alerts: [], syncing: false };
        } finally {
            if (liveSyncIndicator) {
                setTimeout(() => {
                    liveSyncIndicator.classList.remove('syncing');
                    updateSyncStatusDisplay();
                }, 500);
            }
        }
    };

    // Format time mm:ss
    window.formatTime = (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const updateTimer = () => {
        const isSafeToLeave = lastAlertMessage === 'ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו' || 
                             lastAlertTitle === 'ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו';

        if (!lastAlertTimestamp || isSafeToLeave) {
            timerContainer.style.display = 'none';
            if (timerInterval) clearInterval(timerInterval);
            return;
        }

        const now = new Date();
        const alertTime = new Date(lastAlertTimestamp);
        const diffSeconds = Math.floor((now - alertTime) / 1000);

        if (diffSeconds < 0) {
            // If the alert is in the future (skew), show 00:00
             timerContainer.innerHTML = `<div class="timer-box">Time passed: 00:00</div>`;
             return;
        }

        timerContainer.style.display = 'block';
        const timeStr = formatTime(diffSeconds);
        
        let timerClass = 'timer-box';
        let statusText = '';
        
        if (lastAlertStatus === 'upcoming') {
            if (diffSeconds >= 600) {
                timerClass += ' timer-danger';
                statusText = ' (Warning: Long delay)';
            } else {
                timerClass += ' warning';
                statusText = ' (Alert may sound any moment)';
            }
        } else {
            // "Actual" alert (status is 'active' or other, but we assume active if not upcoming)
            if (diffSeconds >= 600) {
                timerClass += ' safe timer-safe';
                statusText = ' (Safe to exit)';
            } else {
                timerClass += ' warning';
            }
        }
        
        timerContainer.innerHTML = `<div class="${timerClass}">Time passed: ${timeStr}${statusText}</div>`;
    };

    // Check if alerts have changed to avoid unnecessary re-renders
    const hasAlertsChanged = (newAlerts, syncing) => {
        const newSignature = JSON.stringify({ alerts: newAlerts, syncing });
        if (newSignature === currentAlertsSignature) {
            return false;
        }
        currentAlertsSignature = newSignature;
        return true;
    };

    // Display the latest alert at the top (styled as before), and the rest as history
    const displayAlerts = (alerts, syncing = false) => {
        // Timer Logic: Always use the latest alert for the active location
        if (alerts && alerts.length > 0) {
            const latestAlertTime = alerts[0].alertDate;
            const latestStatus = alerts[0].status;
            const latestMessage = alerts[0].message;
            const latestTitle = alerts[0].title;
            
            if (latestAlertTime !== lastAlertTimestamp || 
                latestStatus !== lastAlertStatus || 
                latestMessage !== lastAlertMessage || 
                latestTitle !== lastAlertTitle) {
                lastAlertTimestamp = latestAlertTime;
                lastAlertStatus = latestStatus;
                lastAlertMessage = latestMessage;
                lastAlertTitle = latestTitle;
                if (timerInterval) clearInterval(timerInterval);
                timerInterval = setInterval(updateTimer, 1000);
            }
            updateTimer(); // Immediate update
        } else if (!syncing) {
            lastAlertTimestamp = null;
            lastAlertStatus = null;
            lastAlertMessage = null;
            lastAlertTitle = null;
            if (timerInterval) clearInterval(timerInterval);
            timerContainer.style.display = 'none';
        }

        // Regression Fix: Don't show loading message if we already have alerts to show
        if (syncing && alerts.length === 0) {
            alertsContainer.innerHTML = '<div class="alert-item alert-loading">Syncing data...</div>';
            return;
        }

        alertsContainer.innerHTML = '';
        if (alerts && alerts.length > 0) {
            const alert = alerts[0]; // Show only the most recent alert
            const alertElement = document.createElement('div');
            alertElement.className = 'alert-item alert-entry-animate'; // Added entry animation
            
            // Handle statuses
            if (alert.status === 'active') {
                alertElement.classList.add('active');
            } else if (alert.status === 'upcoming') {
                alertElement.classList.add('alert-upcoming');
            } else {
                // Default to calm if no status or ended
                alertElement.classList.add('alert-calm');
            }

            const locationElement = document.createElement('div');
            locationElement.className = 'alert-location';
            locationElement.textContent = alert.location;
            alertElement.appendChild(locationElement);

            const threatElement = document.createElement('div');
            threatElement.className = 'alert-threat';
            threatElement.textContent = alert.title;
            alertElement.appendChild(threatElement);

            if (alert.message && alert.message !== alert.title) {
                const messageElement = document.createElement('div');
                messageElement.className = 'alert-message';
                messageElement.textContent = alert.message;
                alertElement.appendChild(messageElement);
            }

            const timeElement = document.createElement('div');
            timeElement.className = 'alert-time';
            
            // Format time to exactly HH:MM as shown in the screenshots
            const dateObj = new Date(alert.alertDate);
            
            // Format in Israel time
            const timeString = dateObj.toLocaleTimeString('en-US', { 
                timeZone: 'Asia/Jerusalem', 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            timeElement.textContent = timeString;
            
            alertElement.appendChild(timeElement);

            alertsContainer.appendChild(alertElement);
        } else {
            const calmElement = document.createElement('div');
            calmElement.className = 'alert-item alert-calm alert-entry-animate';
            calmElement.textContent = 'All Quiet';
            alertsContainer.appendChild(calmElement);
        }
    };

    // Display the rest of the alerts as history (excluding the latest)
    const displayHistory = (alerts) => {
        const historyContainer = document.getElementById('history-container');
        historyContainer.innerHTML = '<h2>Alert History</h2>';
        if (alerts && alerts.length > 1) {
            for (let i = 1; i < alerts.length; i++) {
                const alert = alerts[i];
                const historyElement = document.createElement('div');
                historyElement.className = 'history-item';
                if (alert.status === 'active') {
                    historyElement.classList.add('active');
                } else if (alert.status === 'upcoming') {
                    historyElement.classList.add('upcoming');
                }
                const detailsElement = document.createElement('div');
                detailsElement.className = 'history-details';
                const threatElement = document.createElement('div');
                threatElement.className = 'history-threat';
                threatElement.textContent = alert.title;
                detailsElement.appendChild(threatElement);
                const locationElement = document.createElement('div');
                locationElement.className = 'history-location';
                locationElement.textContent = alert.location;
                detailsElement.appendChild(locationElement);
                // Removed duplicate message display
                historyElement.appendChild(detailsElement);
                const timeElement = document.createElement('div');
                timeElement.className = 'history-time';
                
                // Format time to exactly HH:MM as shown in the screenshots
                const dateObj = new Date(alert.alertDate);
                const timeString = dateObj.toLocaleTimeString('en-US', { 
                    timeZone: 'Asia/Jerusalem', 
                    hour12: false, 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                timeElement.textContent = timeString;
                
                historyElement.appendChild(timeElement);
                historyContainer.appendChild(historyElement);
            }
        } else {
            historyContainer.innerHTML += '<p>No history available.</p>';
        }
    };

    // --- State memory for last location ---
    function saveLastLocation(location) {
        try {
            localStorage.setItem('lastLocation', location);
        } catch (e) {}
    }
    function getLastLocation() {
        try {
            return localStorage.getItem('lastLocation') || '';
        } catch (e) { return ''; }
    }

    // --- Modified startFetching to save location ---
    const startFetching = async () => {
        const newLocation = locationInput.value.trim();
        
        // If location is the same and we are already fetching, trigger force refresh
        if (newLocation === userLocation && fetchInterval) {
            checkAlertsBtn.classList.add('loading-aurora');
            checkAlertsBtn.textContent = 'Checking...';
            try {
                const response = await fetch('/api/force-refresh', { method: 'POST' });
                if (response.ok) {
                    currentAlertsSignature = ''; // Force UI update
                    const { alerts, syncing } = await fetchAllAlerts();
                    displayAlerts(alerts, syncing);
                    displayHistory(alerts);
                }
            } catch (e) {
                console.error("Force refresh failed", e);
            } finally {
                setTimeout(() => {
                    checkAlertsBtn.classList.remove('loading-aurora');
                    checkAlertsBtn.textContent = 'Check Alerts';
                }, 800);
            }
            return;
        }

        userLocation = newLocation;
        if (fetchInterval) {
            clearInterval(fetchInterval);
        }
        if (userLocation) {
            saveLastLocation(userLocation);
            
            // Start animation IMMEDIATELY on click
            checkAlertsBtn.classList.add('loading-aurora');
            checkAlertsBtn.textContent = 'Checking...';
            
            const fetchAndRender = async () => {
                const { alerts, syncing } = await fetchAllAlerts();
                if (hasAlertsChanged(alerts, syncing)) {
                    displayAlerts(alerts, syncing);
                    displayHistory(alerts);
                }
            };
            
            try {
                // Initial fetch
                await fetchAndRender();
            } finally {
                // Ensure smooth transition out
                setTimeout(() => {
                    checkAlertsBtn.classList.remove('loading-aurora');
                    checkAlertsBtn.textContent = 'Check Alerts';
                }, 800); // Small delay to ensure the aurora feels natural
            }
            
            fetchInterval = setInterval(fetchAndRender, 2000);
        } else {
            alertsContainer.innerHTML = '<div class="alert-loading">Please enter a location.</div>';
        }
    };

    // --- On load, restore last location if available after locations are fetched ---
    fetchApprovedLocations().then(() => {
        const lastLoc = getLastLocation();
        if (lastLoc && approvedLocations.includes(lastLoc)) {
            locationInput.value = lastLoc;
            checkAlertsBtn.disabled = false;
            startFetching();
        } else {
            // If last location is not approved, clear the input and disable the button
            locationInput.value = '';
            checkAlertsBtn.disabled = true;
        }
    });

    checkAlertsBtn.addEventListener('click', startFetching);

    locationInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            if (!checkAlertsBtn.disabled) {
                startFetching();
            }
        }
    });

    locationInput.addEventListener('input', () => {
        const enteredLocation = locationInput.value.trim();
        if (approvedLocations.includes(enteredLocation)) {
            checkAlertsBtn.disabled = false;
        } else {
            checkAlertsBtn.disabled = true;
        }
    });

    fetchApprovedLocations();
});
