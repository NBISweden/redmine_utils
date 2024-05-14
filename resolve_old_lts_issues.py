import yaml
import argparse
import requests
import pdb
from pprint import pprint
import datetime

def main():
    """
    Main function to retrieve and update issues in Redmine.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
    parser.add_argument('-p', '--project', help='Name of the project to update, including all sub-projects', required=True)
    parser.add_argument('-e', '--exclude', help='Comma-separated list of project identifiers to exclude')
    parser.add_argument('-d', '--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
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
    project_name = args.project
    project_id = None
    for project in projects:
        if project['name'] == project_name:
            project_id = project['id']

    # exit if project not found
    if project_id is None:
        print(f"Project '{project_name}' not found.")
        return


    # Get all issues in the project
    issues = get_all_project_issues(f"{config['url']}/issues.json", headers, project_id)

    # Get the sub-project names to exclude
    exclude_projects = args.exclude.split(',') if args.exclude else []

    # Set url for status update
    url = f"{config['url']}/issues"

    # Iterate over the issues
    for issue in issues:
        #if issue['id'] != 7535:
            #pdb.set_trace()
        #    continue
        # pdb.set_trace()

        # exclude issues that are already closed
        if issue['status']['name'] in ['Closed', 'Rejected', 'Resolved', 'Feedback', 'Declined by client']:
            continue

        # Exclude issues in the specified sub-projects
        if issue['project']['name'] not in exclude_projects:
            # Check if the issue's custom field "WABI ID" is empty
            if not get_custom_field(issue, 'WABI ID'):
                
                # pdb.set_trace()
                # Perform dry run if specified
                if args.dryrun:
                    print(f"Dry run: Would have updated {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}'")
                    continue
                else:
                    # Change the status of the issue to "Rejected"
                    # Print status message
                    print(f"Updating {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}'")
                    update_issue_status(url, headers, issue, 6)  # assuming "Rejected" status ID is 6



def get_custom_field(issue, field_name):
    """
    Retrieve the value of a custom field from an issue.
    """

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



def update_issue_status(url, headers, issue, status_id):
    """
    Update the status of an issue in Redmine using the provided URL, headers, issue ID, and status ID.
    """

    # Create the payload for updating the issue status, and suppress email notifications and surveys
    payload = {
        "suppress_mail" : "1",
        "issue": {
            "status_id": status_id,
            "notes": "Cleaning out old issues.",
            "custom_fields": [
                                {
                                "value": '0', "id" : 22 #"name":"Send survey when closed"
                                }
                            ]
        },
    }

    # check if important issue fields are None (will crash redmine if they are)
    fields = ['description']
    for field in fields:
        if issue[field] is None:
            payload['issue'][field] = ''

    # check if custom fields are None (will crash redmine if they are)
    for field in issue['custom_fields']:
        if field['value'] is None:
            payload['issue']['custom_fields'].append({'id': field['id'], 'value': ''})

        # check if custom fields have leading or trailing white spaces (email with white spaces will crash redmine)
        elif field['value'] != field['value'].strip():
            payload['issue']['custom_fields'].append({'id': field['id'], 'value': field['value'].strip()})

    # set url to update issue
    issue_url = f"{url}/{issue['id']}.json"
    #pdb.set_trace()

    # Update the issue
    response = requests.put(issue_url, headers=headers, json=payload)
    response.raise_for_status()
    return response



if __name__ == '__main__':
    # Run the main function
    main()




