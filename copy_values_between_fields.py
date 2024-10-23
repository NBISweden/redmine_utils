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
    Main function to copy values from one Redmine field and prepend to another field.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
    parser.add_argument('-p', '--project', help='Name of the project to update, including all sub-projects', required=True)
    parser.add_argument('-d', '--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
    parser.add_argument('-l', '--longoutput', action='store_true', help='Output also instances where values of field "assignee" already was present in field "All assignees"')
    parser.add_argument('-o', '--onlyissue', help='Specified issue ID for debug/testing -- only change this issue!')
    parser.add_argument('-f', '--fromfield', help='copy values from this field', default='assigned_to')
    parser.add_argument('-t', '--tofield', help='copy values to this field', default='All assignees')
    parser.add_argument('-u', '--userids', action='store_true', help='Target values are user IDs', default=False)
    parser.add_argument('-s', '--separator', help='use separator to create a list from string field value', default=None)
    
    
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
    # Set up user db indexed by user id
    userNameToId = redmine.create_user_name_to_id(project_id)
    
    # Get all issues in the project
    issues = redmine.get_all_project_issues(project_id)

#    fromField = "assigned_to"
#    toField = "All assignees"

    missingMain = []
    # Iterate over the issues
    print(f"Doing updates for project {project_name}") 
    for issue in issues:
        if args.onlyissue and str(issue['id']) != args.onlyissue:
          continue
        values = get_field(issue, args.fromfield)
        if values == None or values == '':
          missingMain.append(str(issue['id']))
          #pprint(f"project {issue['project']['name']} -- issue #{issue['id']}: no value assigned")
          continue
        # Always work with lists
        if args.separator !=  None:
          if args.separator == "\\n":
            values = values.splitlines()
          else:
            values = values.split(args.separator)
        else:
          values = [ values ]
        if args.userids:
           values = [ userNameToId[val] for val in values ]
        values = set([ str(a) for a in values ])
        target = get_field(issue, args.tofield)
        # Always work with lists
        if target == None or target == '':
          target = []
        elif type (target) != list:
          if args.separator != None:
            if args.separator == "\\n":
              target = target.splitlines()
            else:
              target = target.split(args.separator)
          else:
            target = [ target ]
        target = set([ str(a) for a in target ])
        if len(values.difference(target)) == 0:
          if args.longoutput:
            print(f"issue #{issue['id']}: "+
                  f"All {args.fromfield} value(s) {[ userIdToName[a] if args.userids else a for a in target.intersection(values) ]} "+
                  f"already in {args.tofield} field: {[ userIdToName[a] if args.userids else a for a in target ]}")
          continue
        target = target.union(values)
        if args.dryrun:
          print(f"Dry run: Would have updated issue #{issue['id']}: "+
          f"{args.fromfield} values {[ userIdToName[a] if args.userids else a for a in target.intersection(values) ]} "+
          f"copied to {args.tofield} => {[ userIdToName[a] if args.userids else a for a in target ]}")
          continue
        print(f"Updated issue #{issue['id']}: "+
        f"values {[ userIdToName[a] if args.userids else a for a in target.intersection(values) ]} copied to {args.tofield} "+
        f"=> {[ userIdToName[a] if args.userids else a for a in target ]}")
        target = list(target)
        if args.separator:
          target = f"\r\n".join(target) if args.separator == "\\n" else f"{args.separator}".join(target) 
        redmine.update_issue_custom_field(issue, str(args.tofield), target)
    if len(missingMain) !=0:
        print("\nThe following issues has no main assignee\n{a}".format(a='\n'.join(missingMain)))

if __name__ == '__main__':
    # Run the main function
    main()




