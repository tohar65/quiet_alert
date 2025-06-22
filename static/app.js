document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const checkAlertsBtn = document.getElementById('check-alerts-btn');
    const alertsContainer = document.getElementById('alerts-container');
    const approvedLocationsDatalist = document.getElementById('approved-locations');

    let userLocation = '';
    let fetchInterval;
    let errorCounter = 0;
    let approvedLocations = [];

    const fetchApprovedLocations = async () => {
        try {
            const response = await fetch('/api/approved-locations');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            approvedLocations = data.locations;
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

    // Display the latest alert at the top (styled as before), and the rest as history
    const displayAlerts = (alerts) => {
        alertsContainer.innerHTML = '';
        if (alerts && alerts.length > 0) {
            const alert = alerts[0]; // Show only the most recent alert
            const alertElement = document.createElement('div');
            alertElement.className = 'alert-item';
            if (alert.status === 'active') {
                alertElement.classList.add('active');
            } else if (alert.status === 'upcoming') {
                alertElement.style.color = '#ffd700';
                alertElement.style.backgroundColor = 'rgba(255,215,0,0.1)';
                alertElement.style.border = '2px solid #ffd700';
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

            const timeElement = document.createElement('div');
            timeElement.className = 'alert-time';
            timeElement.textContent = new Date(alert.alertDate).toLocaleString();
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
                historyElement.appendChild(detailsElement);
                const timeElement = document.createElement('div');
                timeElement.className = 'history-time';
                timeElement.textContent = new Date(alert.alertDate).toLocaleString();
                historyElement.appendChild(timeElement);
                historyContainer.appendChild(historyElement);
            }
        } else {
            historyContainer.innerHTML += '<p>No history available.</p>';
        }
    };

    const startFetching = () => {
        userLocation = locationInput.value.trim();
        if (fetchInterval) {
            clearInterval(fetchInterval);
        }
        if (userLocation) {
            const fetchAndRender = async () => {
                const allAlerts = await fetchAllAlerts();
                displayAlerts(allAlerts);
                displayHistory(allAlerts);
            };
            fetchAndRender();
            fetchInterval = setInterval(fetchAndRender, 5000);
        } else {
            alertsContainer.innerHTML = '<div class="alert-loading">Please enter a location.</div>';
        }
    };

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