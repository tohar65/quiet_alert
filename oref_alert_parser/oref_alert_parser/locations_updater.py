import json
import argparse
import os
from typing import Set

def update_approved_locations(log_file_path: str, output_file_path: str) -> None:
    """
    Parses a log file to extract unique location names and updates a Python module.

    The log file is expected to contain JSON-serialized alert objects, one per line.
    The extracted locations are sorted and written as a list to a Python file.

    Args:
        log_file_path: Path to the log file containing raw alert JSON strings.
        output_file_path: Path to the Python file where the locations list will be written.
    """
    unique_locations: Set[str] = set()
    try:
        # Use 'utf-8-sig' to handle the BOM character at the start of the file
        with open(log_file_path, 'r', encoding='utf-8-sig') as log_file:
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
        print(f"Error: {log_file_path} not found.")
        return

    sorted_locations = sorted(list(unique_locations))

    with open(output_file_path, 'w', encoding='utf-8') as approved_file:
        approved_file.write("from typing import List\n\n")
        approved_file.write("APPROVED_LOCATIONS = [\n")
        for location in sorted_locations:
            # Escape double quotes inside the location string, just in case
            location_str = location.replace('"', '\\"')
            approved_file.write(f'    "{location_str}",\n')
        approved_file.write("]\n")

    print(f"{output_file_path} has been updated successfully with {len(sorted_locations)} locations.")

def main() -> None:
    """
    Defines the command-line interface for updating approved locations.
    """
    # The output file should be in the same directory as this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_path = os.path.join(script_dir, 'approved_locations.py')

    parser = argparse.ArgumentParser(description="Update the list of approved locations from an alerts log.")
    parser.add_argument('log_file', help="Path to the alerts.log file.")
    parser.add_argument('--output', default=default_output_path, help=f"Path to the output approved_locations.py file. Defaults to {default_output_path}")
    args = parser.parse_args()

    update_approved_locations(args.log_file, args.output)

if __name__ == "__main__":
    main()
