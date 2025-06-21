document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const setLocationBtn = document.getElementById('set-location-btn');
    const alertStatusDiv = document.getElementById('alert-status');
    const approvedLocationsDatalist = document.getElementById('approved-locations');

    let userLocation = '';
    let fetchInterval;

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

    const fetchAlerts = async () => {
        if (!userLocation) {
            alertStatusDiv.innerHTML = 'Enter a location to begin.';
            alertStatusDiv.className = 'alert-loading';
            return;
        }

        alertStatusDiv.innerHTML = `Checking alerts for ${userLocation}...`;
        alertStatusDiv.className = 'alert-loading';

        try {
            const url = `/api/alerts?location=${encodeURIComponent(userLocation)}`;
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.alerts && data.alerts.length > 0) {
                alertStatusDiv.textContent = "ALERT!";
                alertStatusDiv.className = 'alert-active';
            } else {
                alertStatusDiv.textContent = 'All Quiet';
                alertStatusDiv.className = 'alert-calm';
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
            alertStatusDiv.innerHTML = `Error: ${error.message}`;
            alertStatusDiv.className = 'alert-error';
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
            alertStatusDiv.innerHTML = 'Please enter a location.';
            alertStatusDiv.className = 'alert-loading';
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