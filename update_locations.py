import json

def update_approved_locations():
    """
    Parses 'alerts.log' to extract unique location names and updates
    'approved_locations.py' with the sorted list of these locations.
    """
    unique_locations = set()
    try:
        # Use 'utf-8-sig' to handle the BOM character at the start of the file
        with open('alerts.log', 'r', encoding='utf-8-sig') as log_file:
            for line in log_file:
                try:
                    alert = json.loads(line)
                    location = alert.get('data')
                    if location:
                        unique_locations.add(location)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse line as JSON: {line.strip()}")
                    continue
    except FileNotFoundError:
        print("Error: alerts.log not found.")
        return

    sorted_locations = sorted(list(unique_locations))

    with open('approved_locations.py', 'w', encoding='utf-8') as approved_file:
        approved_file.write("APPROVED_LOCATIONS = [\n")
        for location in sorted_locations:
            # Escape double quotes inside the location string, just in case
            location_str = location.replace('"', '\\"')
            approved_file.write(f'    "{location_str}",\n')
        approved_file.write("]\n")

    print(f"approved_locations.py has been updated successfully with {len(sorted_locations)} locations.")

if __name__ == "__main__":
    update_approved_locations()