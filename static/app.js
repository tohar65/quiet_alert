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
                timeElement.textContent = new Date(alert.alertDate).toLocaleString();
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
                displayAlerts(allAlerts);
                displayHistory(allAlerts);
            };
            fetchAndRender();
            fetchInterval = setInterval(fetchAndRender, 5000);
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

    // --- Admin Modal Logic ---
    const adminOpenBtn = document.getElementById('admin-open-btn');
    const adminLoginModal = document.getElementById('admin-login-modal');
    const adminLoginClose = document.getElementById('admin-login-close');
    const adminLoginForm = document.getElementById('admin-login-form');
    const adminUsernameInput = document.getElementById('admin-username');
    const adminPasswordInput = document.getElementById('admin-password');
    const adminLoginError = document.getElementById('admin-login-error');
    const adminPanelModal = document.getElementById('admin-panel-modal');
    const adminPanelClose = document.getElementById('admin-panel-close');
    const adminLogoutBtn = document.getElementById('admin-logout-btn');
    const addTempAlertForm = document.getElementById('add-temp-alert-form');
    const tempAlertLocation = document.getElementById('temp-alert-location');
    const tempAlertThreat = document.getElementById('temp-alert-threat');
    const tempAlertMessage = document.getElementById('temp-alert-message');
    const tempAlertsList = document.getElementById('temp-alerts-list');
    const addTempLocationForm = document.getElementById('add-temp-location-form');
    const tempLocationName = document.getElementById('temp-location-name');
    const tempLocationsList = document.getElementById('temp-locations-list');

    let adminAuth = null; // {username, password}

    function getAdminAuthHeader() {
        if (!adminAuth) return {};
        const token = btoa(`${adminAuth.username}:${adminAuth.password}`);
        return { 'Authorization': `Basic ${token}` };
    }

    function showModal(modal) {
        modal.style.display = 'block';
        setTimeout(() => { modal.classList.add('show'); }, 10);
    }
    function hideModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => { modal.style.display = 'none'; }, 200);
    }

    adminOpenBtn.addEventListener('click', () => {
        // If admin creds are stored, try to use them and open panel directly
        const storedAdmin = getAdminAuth();
        if (storedAdmin) {
            tryAdminLogin(storedAdmin.username, storedAdmin.password).then(ok => {
                if (ok) {
                    adminAuth = storedAdmin;
                    showModal(adminPanelModal);
                    refreshAdminPanel();
                } else {
                    clearAdminAuth();
                    // fallback to login modal
                    showModal(adminLoginModal);
                    adminLoginError.textContent = '';
                    adminUsernameInput.value = '';
                    adminPasswordInput.value = '';
                    adminUsernameInput.focus();
                }
            });
        } else {
            showModal(adminLoginModal);
            adminLoginError.textContent = '';
            adminUsernameInput.value = '';
            adminPasswordInput.value = '';
            adminUsernameInput.focus();
        }
    });
    adminLoginClose.addEventListener('click', () => hideModal(adminLoginModal));
    adminPanelClose.addEventListener('click', () => hideModal(adminPanelModal));
    window.addEventListener('click', (e) => {
        if (e.target === adminLoginModal) hideModal(adminLoginModal);
        if (e.target === adminPanelModal) hideModal(adminPanelModal);
    });

    async function tryAdminLogin(username, password) {
        const res = await fetch('/api/admin/list-temp-alerts', {
            headers: { ...getAdminAuthHeader(), 'Authorization': `Basic ${btoa(username+":"+password)}` }
        });
        return res.ok;
    }

    // --- Admin Auth Persistence ---
    function saveAdminAuth(auth) {
        try {
            localStorage.setItem('adminAuth', btoa(`${auth.username}:${auth.password}`));
        } catch (e) {}
    }
    function getAdminAuth() {
        try {
            const token = localStorage.getItem('adminAuth');
            if (!token) return null;
            const [username, password] = atob(token).split(':');
            return { username, password };
        } catch (e) { return null; }
    }
    function clearAdminAuth() {
        try {
            localStorage.removeItem('adminAuth');
        } catch (e) {}
    }

    adminLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = adminUsernameInput.value.trim();
        const password = adminPasswordInput.value;
        const ok = await tryAdminLogin(username, password);
        if (ok) {
            adminAuth = { username, password };
            saveAdminAuth(adminAuth);
            hideModal(adminLoginModal);
            showModal(adminPanelModal);
            adminLoginError.textContent = '';
            refreshAdminPanel();
        } else {
            adminLoginError.textContent = 'Login failed';
        }
    });

    adminLogoutBtn.addEventListener('click', () => {
        adminAuth = null;
        clearAdminAuth();
        hideModal(adminPanelModal);
    });

    async function refreshAdminPanel() {
        // List temp alerts
        const alertsRes = await fetch('/api/admin/list-temp-alerts', { headers: getAdminAuthHeader() });
        const alertsData = alertsRes.ok ? await alertsRes.json() : { temporary_alerts: [] };
        tempAlertsList.innerHTML = '';
        alertsData.temporary_alerts.forEach((alert, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<b>${alert.location}</b> | <span style='color:#ff4d4d'>${alert.threat_type}</span> | ${alert.message} <span style='color:#888'>${new Date(alert.alertDate).toLocaleString()}</span>`;
            const btn = document.createElement('button');
            btn.textContent = 'Remove';
            btn.className = 'admin-remove-btn';
            btn.onclick = async () => {
                await fetch('/api/admin/remove-temp-alert', {
                    method: 'POST',
                    headers: { ...getAdminAuthHeader(), 'Content-Type': 'application/json' },
                    body: JSON.stringify(alert)
                });
                refreshAdminPanel();
                if (userLocation) startFetching(); // update main UI
            };
            li.appendChild(btn);
            tempAlertsList.appendChild(li);
        });
        // List temp locations
        const locRes = await fetch('/api/admin/list-temp-locations', { headers: getAdminAuthHeader() });
        const locData = locRes.ok ? await locRes.json() : { temporary_locations: [] };
        tempLocationsList.innerHTML = '';
        locData.temporary_locations.forEach((loc) => {
            const li = document.createElement('li');
            li.innerHTML = `<b>${loc}</b>`;
            const btn = document.createElement('button');
            btn.textContent = 'Remove';
            btn.className = 'admin-remove-btn';
            btn.onclick = async () => {
                await fetch('/api/admin/remove-temp-location', {
                    method: 'POST',
                    headers: { ...getAdminAuthHeader(), 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location: loc })
                });
                refreshAdminPanel();
                fetchApprovedLocations(); // update main UI
            };
            li.appendChild(btn);
            tempLocationsList.appendChild(li);
        });
    }

    addTempAlertForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const alert = {
            location: tempAlertLocation.value.trim(),
            threat_type: tempAlertThreat.value.trim(),
            message: tempAlertMessage.value.trim(),
            alertDate: new Date().toISOString(),
            status: 'active',
            title: tempAlertThreat.value.trim()
        };
        await fetch('/api/admin/add-temp-alert', {
            method: 'POST',
            headers: { ...getAdminAuthHeader(), 'Content-Type': 'application/json' },
            body: JSON.stringify(alert)
        });
        addTempAlertForm.reset();
        refreshAdminPanel();
        if (userLocation) startFetching(); // update main UI
    });

    addTempLocationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const location = tempLocationName.value.trim();
        await fetch('/api/admin/add-temp-location', {
            method: 'POST',
            headers: { ...getAdminAuthHeader(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ location })
        });
        addTempLocationForm.reset();
        refreshAdminPanel();
        fetchApprovedLocations(); // update main UI
    });

    fetchApprovedLocations();
});