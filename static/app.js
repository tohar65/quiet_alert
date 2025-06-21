const locationInput = document.getElementById('location-input');
const setLocationBtn = document.getElementById('set-location-btn');
const alertStatusDiv = document.getElementById('alert-status');

let userLocation = '';

const fetchAlerts = async () => {
    let url = '/api/alerts';
    if (userLocation) {
        url += `?location=${encodeURIComponent(userLocation)}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.active_alerts && data.active_alerts.length > 0) {
            alertStatusDiv.innerHTML = `<strong>Active Alert:</strong> ${data.active_alerts[0].title}`;
            alertStatusDiv.className = 'alert-active';
        } else {
            alertStatusDiv.innerHTML = 'No active alerts.';
            alertStatusDiv.className = 'alert-calm';
        }
    } catch (error) {
        console.error('Error fetching alerts:', error);
        alertStatusDiv.innerHTML = 'Error fetching alert status.';
        alertStatusDiv.className = '';
    }
};

setLocationBtn.addEventListener('click', () => {
    userLocation = locationInput.value.trim();
    fetchAlerts(); // Fetch immediately after setting new location
});

// Fetch alerts on initial load and then every 500ms
fetchAlerts();
setInterval(fetchAlerts, 500);