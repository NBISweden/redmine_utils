import yaml
import argparse
import requests
import pdb
from pprint import pprint

def main():
    """
    Main function to retrieve and update issues in Redmine.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to the YAML config file')
    parser.add_argument('-e', '--exclude', help='Comma-separated list of project identifiers to exclude')
    parser.add_argument('--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
    args = parser.parse_args()

    # Load Redmine credentials from YAML config file
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Create Redmine API URL for projects
    url = f"{config['url']}/projects.json"

    # Set Redmine API key
    headers = {"X-Redmine-API-Key": config['api_key']}

    # Get all projects
    projects = get_all_projects(url, headers)

    # Get the project named "Long-term Support"
    project_name = "Long-term Support"
    project_id = None
    for project in projects:
        if project['name'] == project_name:
            project_id = project['id']

    if project_id is None:
        print(f"Project '{project_name}' not found.")
        return

    # Create Redmine API URL for issues
    url = f"{config['url']}/issues.json"
    update_issue_status(f"{config['url']}/issues", headers, 7312, 6)
    import sys
    sys.exit(1)

    # Get all issues in the project
    issues = get_all_project_issues(url, headers, project_id)

    # Get the sub-project names to exclude
    exclude_projects = args.exclude.split(',') if args.exclude else []

    # Set url for status update
    url = f"{config['url']}/issues"

    # Iterate over the issues
    for issue in issues:
        # Check if the issue's custom field "WABI ID" is empty
        if not get_custom_field(issue, 'WABI ID'):
            # Exclude issues in the specified sub-projects
            if issue['project']['name'] not in exclude_projects:
                # Print status message
                print(f"Updating {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}'")
            
                pdb.set_trace()
                # Perform dry run if specified
                if args.dryrun:
                    continue

                # Change the status of the issue to "Rejected"
                update_issue_status(url, headers, int(issue['id']), 6)  # assuming "Rejected" status ID is 6

def get_custom_field(issue, field_name):


    # get field value
    field_value = [ field['value'] for field in issue['custom_fields'] if field['name']==field_name ]
    if len(field_value) > 0:
        field_value = field_value[0]
    else:
        field_value = ''

    return field_value

def get_all_projects(url, headers):
    """
    Retrieve all projects from Redmine API by paginating through the results.
    """
    projects = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params={"page": page})
        response.raise_for_status()
        data = response.json()
        projects.extend(data['projects'])
        if data['total_count'] <= len(projects):
            break
        page += 1
    return projects

def get_project_id(projects, project_name):
    """
    Retrieve the ID of a project from the given list of projects and its name.
    """
    for project in projects:
        print(project['name'])
        if project['name'] == project_name:
            return project['id']
    return None

def get_all_project_issues(url, headers, project_id):
    """
    Retrieve all issues in a project from the Redmine API by paginating through the results.

    Args:
        url (str): The URL of the Redmine API.
        headers (dict): The headers containing the API key for authentication.
        project_id (int): The ID of the project.

    Returns:
        list: A list of all issues in the project.

    """
    issues = []
    page = 1
    while True:
        # Retrieve issues for the current page
        response = requests.get(url, headers=headers, params={"project_id": project_id, "page": page})
        response.raise_for_status()
        data = response.json()
        issues.extend(data['issues'])

        # Break the loop if all issues have been retrieved
        if data['total_count'] <= len(issues):
            break

        # Move to the next page
        page += 1

    return issues

def update_issue_status(url, headers, issue_id, status_id):
    """
    Update the status of an issue in Redmine using the provided URL, headers, issue ID, and status ID.
    """
    payload = {
        "issue": {
            "status_id": status_id,
            "notes": "Cleaning out old issues."
        },
    }
    issue_url = f"{url}/{issue_id}.json"
    pdb.set_trace()
    response = requests.put(issue_url, headers=headers, json=payload)
    response.raise_for_status()

if __name__ == '__main__':
    # Run the main function
    main()
