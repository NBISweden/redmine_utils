import yaml
import argparse
from redminelib import Redmine

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to the YAML config file')
    parser.add_argument('-e', '--exclude', help='Comma-separated list of project identifiers to exclude')
    parser.add_argument('--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
    args = parser.parse_args()

    # Load Redmine credentials from YAML config file
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Connect to Redmine using API key
    redmine = Redmine(config['url'], key=config['api_key'])

    # Get the project named "Long-term Support"
    project_name = "Long-term Support"
    project = redmine.project.get(project_name)

    # Get all issues in the project
    issues = project.issues

    # Get the sub-project names to exclude
    exclude_projects = args.exclude.split(',') if args.exclude else []

    # Iterate over the issues
    for issue in issues:
        # Check if the issue's custom field "WABI ID" is empty
        if not issue.custom_fields.WABI_ID:
            # Exclude issues in the specified sub-projects
            if issue.project.identifier not in exclude_projects:
                # Print status message
                print(f"Updating issue #{issue.id} - {issue.subject}")

                # Perform dry run if specified
                if args.dryrun:
                    continue

                # Change the status of the issue to "Resolved"
                issue.status_id = 5  # assuming "Resolved" status ID is 5
                issue.save()

if __name__ == '__main__':
    main()
