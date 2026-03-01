import os
import json
import pytest
from oref_alert_parser.locations_updater import update_approved_locations

def test_update_approved_locations(tmp_path):
    # Create a mock log file
    log_file = tmp_path / "alerts.log"
    log_content = [
        {"data": "Location C"},
        {"data": "Location A"},
        {"data": "Location B"},
        {"data": "Location A"}, # Duplicate
        {"invalid": "data"},    # Missing data key
        "not json"              # Invalid JSON
    ]
    
    with open(log_file, "w", encoding="utf-8-sig") as f:
        for entry in log_content:
            if isinstance(entry, dict):
                f.write(json.dumps(entry) + "\n")
            else:
                f.write(entry + "\n")
                
    output_file = tmp_path / "approved_locations.py"
    
    # Run the updater
    update_approved_locations(str(log_file), str(output_file))
    
    # Verify the output file
    assert output_file.exists()
    
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert 'APPROVED_LOCATIONS = [' in content
    assert '    "Location A",' in content
    assert '    "Location B",' in content
    assert '    "Location C",' in content
    assert ']' in content
    
    # Check sorting
    lines = [line.strip() for line in content.splitlines() if line.strip().startswith('"')]
    assert lines == ['"Location A",', '"Location B",', '"Location C",']

def test_update_approved_locations_file_not_found(tmp_path, capsys):
    update_approved_locations("non_existent.log", "output.py")
    captured = capsys.readouterr()
    assert "Error: non_existent.log not found." in captured.out
