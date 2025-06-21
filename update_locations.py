import re

def update_approved_locations():
    """
    Parses 'alerts.log' to extract unique location names and updates
    'approved_locations.py' with the sorted list of these locations.
    """
    try:
        with open('alerts.log', 'r', encoding='utf-8') as log_file:
            log_content = log_file.read()
    except FileNotFoundError:
        print("Error: alerts.log not found.")
        return

    # Regex to find the value of the 'data' field
    locations = re.findall(r"'data': '(.*?)'", log_content)

    # Get unique locations and sort them
    unique_locations = sorted(list(set(locations)))

    # Write the updated list to approved_locations.py
    with open('approved_locations.py', 'w', encoding='utf-8') as approved_file:
        approved_file.write(f"APPROVED_LOCATIONS = {unique_locations}\n")

    print("approved_locations.py has been updated successfully.")

if __name__ == "__main__":
    update_approved_locations()