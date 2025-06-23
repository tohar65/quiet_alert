import os
from flask import Flask, jsonify, render_template, request
from oref_alert_parser.parser import OrefAlertParser, fetch_alerts
from oref_alert_parser.approved_locations import APPROVED_LOCATIONS

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    """
    Serves the main page.
    """
    return render_template('index.html')


@app.route('/alerts')
def alerts():
    """
    Provides the alert data as a JSON object.
    """
    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        return jsonify([alert.to_dict() for alert in parser.get_alerts()])
    return jsonify([])


@app.route('/api/approved-locations')
def approved_locations():
    """
    Returns the list of approved locations.
    """
    return jsonify({'locations': APPROVED_LOCATIONS})


@app.route('/api/alerts/all')
def all_alerts():
    """
    Provides all historical alerts for a specific location.
    """
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400
    
    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        all_alerts = parser.get_alerts()
        # Assuming get_alerts() returns all alerts and we filter here
        location_alerts = [alert.to_dict() for alert in all_alerts if alert.location == location]
        return jsonify({"alerts": location_alerts})
    return jsonify({"alerts": []})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)