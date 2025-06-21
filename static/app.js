document.addEventListener('DOMContentLoaded', () => {
    const locationInput = document.getElementById('location-input');
    const setLocationBtn = document.getElementById('set-location-btn');
    const alertStatusDiv = document.getElementById('alert-status');

    let userLocation = '';
    let fetchInterval;

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
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.alerts && data.alerts.length > 0) {
                const alertTitles = data.alerts.map(alert => alert.title).join('<br>');
                alertStatusDiv.innerHTML = `<strong>ALERT ACTIVE</strong><br>${alertTitles}`;
                alertStatusDiv.className = 'alert-active';
            } else {
                alertStatusDiv.innerHTML = 'Status: Calm';
                alertStatusDiv.className = 'alert-calm';
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
            alertStatusDiv.innerHTML = 'Error fetching alert status.';
            alertStatusDiv.className = ''; // Default style
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
});