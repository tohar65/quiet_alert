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
        window.displayAlerts = displayAlerts;
        window.displayHistory = displayHistory;
        window.updateTimer = updateTimer;

        if (!lastSuccessfulSync) {
            syncStatusText.textContent = 'Last update: --';
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

        syncStatusText.textContent = `Last update: ${diffSeconds}s ago`;
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
        const isSafeToLeave = (lastAlertMessage && (lastAlertMessage.includes('ניתן לצאת מהמרחב המוגן') || lastAlertMessage.includes('האירוע הסתיים'))) || 
                              (lastAlertTitle && (lastAlertTitle.includes('ניתן לצאת מהמרחב המוגן') || lastAlertTitle.includes('האירוע הסתיים'))) ||
                              lastAlertStatus === 'ended';

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
        
        if (lastAlertStatus === 'upcoming') {
            if (diffSeconds >= 600) {
                // Case: Upcoming + Long delay -> Red
                timerClass += ' timer-danger';
            } else {
                // Case: Upcoming + Alert may sound -> Yellow
                timerClass += ' timer-warning';
            }
        } else {
            // Actual alert
            if (diffSeconds >= 600) {
                // Case: Actual + Safe to exit -> Green
                timerClass += ' timer-safe';
            } else {
                // Case: Actual + Initial state -> White
                timerClass += ' timer-active';
            }
        }
        
        timerContainer.innerHTML = `
            <div class="${timerClass}">
                <div class="timer-label">Time passed:</div>
                <div class="timer-value">${timeStr}</div>
            </div>`;
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
        window.displayAlerts = displayAlerts;
        window.displayHistory = displayHistory;
        window.updateTimer = updateTimer;
        let deduplicatedAlerts = deduplicateAlerts(alerts);

        // Filter for "Today only" (since 00:00 local time)
        const now = new Date();
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
        
        deduplicatedAlerts = deduplicatedAlerts.filter(alert => {
            const alertTime = new Date(alert.alertDate).getTime();
            return alertTime >= todayStart;
        });

        // Timer Logic: Always use the latest alert for the active location
        if (deduplicatedAlerts && deduplicatedAlerts.length > 0) {
            const latestAlert = deduplicatedAlerts[0];
            const latestAlertTime = latestAlert.alertDate;
            const latestStatus = (latestAlert.status === 'upcoming' || 
                                 latestAlert.oref_category === 14 || 
                                 (latestAlert.title && latestAlert.title.includes('התרעה מוקדמת'))) ? 'upcoming' : latestAlert.status;
            const latestMessage = latestAlert.message;
            const latestTitle = latestAlert.title;
            
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
        if (syncing && deduplicatedAlerts.length === 0) {
            alertsContainer.innerHTML = '<div class="alert-item alert-loading">Syncing data...</div>';
            return;
        }

        alertsContainer.innerHTML = '';
        if (deduplicatedAlerts && deduplicatedAlerts.length > 0) {
            const alert = deduplicatedAlerts[0]; // Show only the most recent alert
            const alertElement = document.createElement('div');
            alertElement.className = 'alert-item alert-entry-animate'; // Added entry animation
            
            // Handle color-coding
            alertElement.classList.add(getAlertColorClass(alert));

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
            calmElement.className = 'alert-item alert-green alert-entry-animate';
            calmElement.textContent = 'All Quiet';
            alertsContainer.appendChild(calmElement);
        }
    };

    // Display the rest of the alerts as history (excluding the latest)
    const displayHistory = (alerts) => {
        let deduplicatedAlerts = deduplicateAlerts(alerts);
        
        // Filter for "Today only" (since 00:00 local time)
        const now = new Date();
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
        
        deduplicatedAlerts = deduplicatedAlerts.filter(alert => {
            const alertTime = new Date(alert.alertDate).getTime();
            return alertTime >= todayStart;
        });

        const historyContainer = document.getElementById('history-container');
        
        // Removed hard historyLimit cap to show all available history for the location
        
        historyContainer.innerHTML = '<h2>Alert History</h2>';
        if (deduplicatedAlerts && deduplicatedAlerts.length > 0) {
            // Show all historical alerts after the first one
            const alertsToShow = deduplicatedAlerts.slice(1);
            
            if (alertsToShow.length === 0) {
                historyContainer.innerHTML += '<p>No past history for today.</p>';
                return;
            }

            alertsToShow.forEach(alert => {
                const historyElement = document.createElement('div');
                historyElement.className = 'history-item';
                
                // Color coding for history too
                const colorClass = window.getAlertColorClass(alert);
                if (colorClass === 'alert-red' || colorClass === 'active') {
                    historyElement.classList.add('active');
                } else if (colorClass === 'alert-yellow' || colorClass === 'upcoming') {
                    historyElement.classList.add('upcoming');
                } else if (colorClass === 'alert-green' || colorClass === 'alert-calm') {
                    historyElement.classList.add('safe');
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
            });
        } else {
            historyContainer.innerHTML += '<p>No history available.</p>';
        }
    };

    window.deduplicateAlerts = (alerts) => {
        if (!alerts || alerts.length === 0) return [];
        
        const deduplicated = [];
        
        alerts.forEach(alert => {
            const isDuplicate = deduplicated.some(existing => {
                // Priority 1: Exact ID match
                if (alert.id && existing.id && alert.id === existing.id) {
                    return true;
                }
                
                // Priority 2: Content-based match
                const alertTime = new Date(alert.alertDate).getTime();
                const existingTime = new Date(existing.alertDate).getTime();
                const timeDiff = Math.abs(existingTime - alertTime);
                const sameLocation = existing.location === alert.location;
                
                // Flexible content match: same location and (exact match OR swapped title/message)
                const contentMatch = (existing.title === alert.title && existing.message === alert.message) ||
                                     (existing.title === alert.message && existing.message === alert.title);
                
                // Broaden window for "Upcoming" alerts (Category 14) which pulse frequently
                const isUpcoming = alert.status === 'upcoming' || existing.status === 'upcoming' ||
                                 alert.oref_category === 14 || existing.oref_category === 14;
                
                if (isUpcoming && sameLocation && contentMatch && timeDiff <= 300000) { // 5 minute window for upcoming
                    return true;
                }

                // If same location and time is very close (within 1 min), and content is similar enough
                // OR if it's the exact same content within 2 mins
                return sameLocation && (
                    (contentMatch && timeDiff <= 120000) || 
                    (timeDiff <= 60000) // Same location, same minute -> likely duplicate for UI
                );
            });
            
            if (!isDuplicate) {
                deduplicated.push(alert);
            }
        });
        
        return deduplicated;
    };

    window.getAlertColorClass = (alert) => {
        const title = alert.title || '';
        const message = alert.message || '';

        // Rule 1: Safe to leave / Ended -> green
        if (title.includes('ניתן לצאת מהמרחב המוגן') || message.includes('ניתן לצאת מהמרחב המוגן') ||
            title.includes('האירוע הסתיים') || message.includes('האירוע הסתיים') ||
            alert.status === 'ended') {
            return 'alert-green';
        }

        // Rule 2: Upcoming -> yellow
        // Check both status and oref_category 14 for robustness, and common Hebrew keywords
        if (alert.status === 'upcoming' || alert.oref_category === 14 || 
            title.includes('התרעה מוקדמת') || message.includes('התרעה מוקדמת')) {
            return 'alert-yellow';
        }

        // Rule 3: Actual alert (Rockets/Aircraft) -> red
        if (title.includes('ירי רקטות וטילים') || message.includes('ירי רקטות וטילים') ||
            title.includes('כלי טיס עוין') || message.includes('כלי טיס עוין')) {
            return 'alert-red';
        }
        
        // Fallback logic
        if (alert.status === 'active') return 'alert-red'; // Consistent with Rule 3
        return 'alert-green'; // Default calm
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
