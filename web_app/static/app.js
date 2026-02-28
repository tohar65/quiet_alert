document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const checkAlertsBtn = document.getElementById('check-alerts-btn');
    const alertsContainer = document.getElementById('alerts-container');
    const timerContainer = document.getElementById('timer-container');
    const approvedLocationsDatalist = document.getElementById('approved-locations');

    let userLocation = '';
    let fetchInterval;
    let errorCounter = 0;
    let approvedLocations = [];
    
    // Timer state
    let lastAlertTimestamp = null;
    let timerInterval = null;
    let currentAlertsSignature = ''; // For checking if alerts changed

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
        try {
            const url = `/api/alerts/all?location=${encodeURIComponent(userLocation)}`;
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            errorCounter = 0;
            return data.alerts || [];
        } catch (error) {
            console.error('Error fetching all alerts:', error);
            errorCounter++;
            if (errorCounter >= 3) {
                alertsContainer.innerHTML = `<div class="alert-error">Reconnecting...</div>`;
            }
            return [];
        }
    };

    // Format time mm:ss
    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const updateTimer = () => {
        if (!lastAlertTimestamp) {
            timerContainer.style.display = 'none';
            if (timerInterval) clearInterval(timerInterval);
            return;
        }

        const now = new Date();
        const alertTime = new Date(lastAlertTimestamp);
        const diffSeconds = Math.floor((now - alertTime) / 1000);

        if (diffSeconds < 0) {
            // Future alert? Should not happen usually, but treat as 0
             timerContainer.innerHTML = `<div class="timer-box">Time passed: 00:00</div>`;
             return;
        }

        timerContainer.style.display = 'block';
        
        if (diffSeconds >= 600) { // 10 minutes
            timerContainer.innerHTML = `<div class="timer-box safe">Safe to exit (10 mins passed)</div>`;
        } else {
             timerContainer.innerHTML = `<div class="timer-box warning">Time passed: ${formatTime(diffSeconds)}</div>`;
        }
    };

    // Check if alerts have changed to avoid unnecessary re-renders
    const hasAlertsChanged = (newAlerts) => {
        const newSignature = JSON.stringify(newAlerts);
        if (newSignature === currentAlertsSignature) {
            return false;
        }
        currentAlertsSignature = newSignature;
        return true;
    };

    // Display the latest alert at the top (styled as before), and the rest as history
    const displayAlerts = (alerts) => {
        // Handle Timer Logic based on the latest ACTIVE alert
        const activeAlert = alerts.find(a => a.status === 'active');
        
        if (activeAlert) {
            const activeTime = activeAlert.alertDate; // Assuming ISO string
            // If it's a new active alert (different timestamp), or we just started tracking
            if (activeTime !== lastAlertTimestamp) {
                lastAlertTimestamp = activeTime;
                // Restart timer interval if not running
                if (timerInterval) clearInterval(timerInterval);
                timerInterval = setInterval(updateTimer, 1000);
            }
             updateTimer(); // Immediate update
        } else {
            // No active alerts
            if (lastAlertTimestamp) {
                // If we were tracking an alert, but now it's gone or ended...
                // Option A: Keep timer until user clears it? 
                // Option B: Clear timer immediately.
                // The requirement says: "When a new alert (active/recent) is detected: Start/Reset a timer."
                // And "After 10 minutes, display a 'Safe to exit'".
                // If the alert status changes to 'ended', we might still want to show the timer if < 10 mins?
                // However, usually 'active' means it just happened.
                
                // Let's keep the timer running if we have a timestamp, until it hits 10 mins or is manually cleared?
                // For now, if no active alert is returned in the list, we might assume the event is over.
                // But the 'history' might still contain it.
                // Let's look at the first alert in the list.
            }
             // If the top alert is not active (e.g. ended), we might still want to show "Safe to exit" if it was recent.
             const topAlert = alerts[0];
             if (topAlert && (new Date() - new Date(topAlert.alertDate) < 600000 + 5000)) { // 10m + buffer
                 if (topAlert.alertDate !== lastAlertTimestamp) {
                     lastAlertTimestamp = topAlert.alertDate;
                     if (timerInterval) clearInterval(timerInterval);
                     timerInterval = setInterval(updateTimer, 1000);
                 }
                 updateTimer();
             } else {
                 lastAlertTimestamp = null;
                 if (timerInterval) clearInterval(timerInterval);
                 timerContainer.style.display = 'none';
             }
        }

        alertsContainer.innerHTML = '';
        if (alerts && alerts.length > 0) {
            const alert = alerts[0]; // Show only the most recent alert
            const alertElement = document.createElement('div');
            alertElement.className = 'alert-item';
            if (alert.status === 'active') {
                alertElement.classList.add('active');
            } else if (alert.status === 'upcoming') {
                alertElement.classList.add('alert-upcoming');
            } else if (alert.status === 'ended') {
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

            if (alert.message) {
                const messageElement = document.createElement('div');
                messageElement.className = 'alert-message';
                messageElement.textContent = alert.message;
                alertElement.appendChild(messageElement);
            }

            const timeElement = document.createElement('div');
            timeElement.className = 'alert-time';
            
            // Format time to exactly HH:MM as shown in the screenshots
            console.log(`[DEBUG] Received alertDate: ${alert.alertDate}`); // Add logging
            const dateObj = new Date(alert.alertDate);
            console.log(`[DEBUG] Parsed dateObj: ${dateObj.toString()}`); // Add logging
            
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
            alertsContainer.innerHTML = '<div class="alert-item calm">All Quiet</div>';
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
                if (alert.message) {
                    const messageElement = document.createElement('div');
                    messageElement.className = 'history-message';
                    messageElement.textContent = alert.message;
                    detailsElement.appendChild(messageElement);
                }
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
    const startFetching = () => {
        userLocation = locationInput.value.trim();
        if (fetchInterval) {
            clearInterval(fetchInterval);
        }
        if (userLocation) {
            saveLastLocation(userLocation);
            const fetchAndRender = async () => {
                const allAlerts = await fetchAllAlerts();
                if (hasAlertsChanged(allAlerts)) {
                    displayAlerts(allAlerts);
                    displayHistory(allAlerts);
                } else {
                    // Even if alerts didn't change, we might need to update the timer? 
                    // The timer runs on its own setInterval (timerInterval), so we don't need to do it here.
                    // However, we need to ensure the timer logic is checked if we start with existing alerts.
                    // Actually, displayAlerts sets up the timer. If we don't call displayAlerts, we might miss setting up the timer on initial load?
                    // But hasAlertsChanged will be true on first load (currentAlertsSignature is empty).
                    
                    // One edge case: if we refresh the page, we fetch alerts. hasAlertsChanged = true. displayAlerts is called. Timer starts.
                    // Next fetch: alerts same. hasAlertsChanged = false. displayAlerts NOT called.
                    // But timerInterval is already running from the first call. So we are good.
                }
            };
            fetchAndRender();
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