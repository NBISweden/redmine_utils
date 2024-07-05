from Redmine_apis import *
import sys
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
    parser.add_argument('-d', '--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
    args = parser.parse_args()

    # Load Redmine credentials from YAML config file
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Create Redmine API URL for projects
    url = f"{config['url']}/projects.json"

    # Set Redmine API key
    headers = {"X-Redmine-API-Key": config['api_key']}

    redmine = Redmine_server_api(config)
    
    # Get all projects
    projects = redmine.get_all_projects()

    # Get project id
    project_name = args.project
    project_id = redmine.find_project_id_from_name(project_name)

    # Set up user db indexed by user id
    userIdToName = redmine.create_user_id_to_name(project_id)

    # Get all issues in the project
    issues = redmine.get_all_project_issues(project_id)

    # Set up user db indexed by user id
    userNameToId = redmine.create_user_name_to_id(project_id)

    fromField = "assigned_to"
    toField = "Assignees"

    # Iterate over the issues
    for issue in issues:
        assignee = userNameToId[get_field(issue, fromField)]
        if assignee == None:
          print(f"issue #{issue['id']}: no assignee assigned")
          continue
        assignees = get_field(issue, toField)
        if f"{assignee}" in assignees: 
          pprint(f"issue #{issue['id']}: {assignee} already in {assignees}")
          continue
        assignees = [ f"{assignee}" ] + assignees
        if args.dryrun:
          pprint(f"Dry run: Would have updated {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}' -- field Assignees -- value {assignees}")
          continue
        p=redmine.update_issue_custom_field(issue, "Assignees", assignees)

if __name__ == '__main__':
    # Run the main function
    main()




