document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const setLocationBtn = document.getElementById('set-location-btn');
    const alertsContainer = document.getElementById('alerts-container');
    const approvedLocationsDatalist = document.getElementById('approved-locations');

    let userLocation = '';
    let fetchInterval;
    let errorCounter = 0;

    const fetchApprovedLocations = async () => {
        try {
            const response = await fetch('/api/approved-locations');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            data.locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                approvedLocationsDatalist.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching approved locations:', error);
        }
    };

    const displayAlerts = (alerts) => {
        alertsContainer.innerHTML = ''; // Clear previous alerts
        if (alerts && alerts.length > 0) {
            alerts.forEach(alert => {
                const alertElement = document.createElement('div');
                alertElement.className = 'alert-item';

                const locationElement = document.createElement('div');
                locationElement.className = 'alert-location';
                locationElement.textContent = alert.data;
                alertElement.appendChild(locationElement);

                const threatElement = document.createElement('div');
                threatElement.className = 'alert-threat';
                threatElement.textContent = alert.title;
                alertElement.appendChild(threatElement);

                const timeElement = document.createElement('div');
                timeElement.className = 'alert-time';
                timeElement.textContent = new Date(alert.id).toLocaleString();
                alertElement.appendChild(timeElement);

                alertsContainer.appendChild(alertElement);
            });
        } else {
            alertsContainer.innerHTML = '<div class="alert-calm">All Quiet</div>';
        }
    };

    const fetchAlerts = async () => {
        if (!userLocation) {
            alertsContainer.innerHTML = '<div class="alert-loading">Enter a location to begin.</div>';
            return;
        }

        try {
            const url = `/api/alerts?location=${encodeURIComponent(userLocation)}`;
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            errorCounter = 0; // Reset counter on success
            displayAlerts(data.alerts);
        } catch (error) {
            console.error('Error fetching alerts:', error);
            errorCounter++;
            if (errorCounter >= 3) {
                alertsContainer.innerHTML = `<div class="alert-error">Reconnecting...</div>`;
            }
        }
    };

    const startFetching = () => {
        userLocation = locationInput.value.trim();
        if (fetchInterval) {
            clearInterval(fetchInterval);
        }
        if (userLocation) {
            fetchAlerts(); // Fetch immediately
            fetchInterval = setInterval(fetchAlerts, 5000); // Then fetch every 5 seconds
        } else {
            alertsContainer.innerHTML = '<div class="alert-loading">Please enter a location.</div>';
        }
    };

    setLocationBtn.addEventListener('click', startFetching);

    locationInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            startFetching();
        }
    });

    fetchApprovedLocations();
});