import json

# Load the JSON report
with open('bandit_report.json', 'r') as file:
    report = json.load(file)

# Filter high severity issues
high_severity_issues = [issue for issue in report['results'] if issue['issue_severity'] == 'HIGH']

# Print high severity issues
for issue in high_severity_issues:
    print(f"Filename: {issue['filename']}")
    print(f"Line Number: {issue['line_number']}")
    print(f"Issue: {issue['issue_text']}")
    print(f"Code: {issue['code']}")
    print("-" * 40)