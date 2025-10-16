#!/bin/env python3

# Author: Bengt S, NBIS

# make the parent directory available for imports, to be able to import Redmine_apis.py there
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from Redmine_apis import *
from pprint import pprint
import argparse
import datetime
import pdb
import re
import requests
import sys
import time
import yaml

def main():
    """
    Main function to copy unique values from one Redmine field and prepend to another field. 
    NB! Both fields should have a content representing an (unordered)  list of items -- NOT free text as content will be reorganized!
    NB! Duplicate values will be reduced to a single value in the target field.
    Copying has been verified to work for Redmine lists, text and long-text fields; different fields need not have same type.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Main function to copy unique values from one Redmine field and prepend to another field. " 
    "NB! Both fields should have a content representing an (unordered)  list of items -- NOT free text as content will be reorganized! "
    "NB! Duplicate values will be reduced to a single value in the target field. "
    "Copying has been verified to work for Redmine lists, text and long-text fields; different fields need not have same type.")
    parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
    parser.add_argument('-p', '--project', help='Name of the project to update, including all sub-projects', required=True)
    parser.add_argument('-d', '--dryrun', action='store_true', help='Perform a dry run without actually updating any issues')
    parser.add_argument('-l', '--longoutput', action='store_true', help='Output also instances where values of field "assignee" already was present in field "All assignees"')
    parser.add_argument('-o', '--onlyissue', help='Specified issue ID for debug/testing -- only change this issue!')
    parser.add_argument('-f', '--fromfield', help='copy values from this field', default='assigned_to')
    parser.add_argument('-t', '--tofield', help='copy values to this field', default='All assignees')
    parser.add_argument('-u', '--userids', action='store_true', help='Target values are user IDs', default=False)
    parser.add_argument('-s', '--separator', help='use separator to create a list from string field value', default=None)
    parser.add_argument('-n', '--newseparator', help='use new separator to write a list to string field target', default=None)
    parser.add_argument('-w', '--whatStatus', help='include issues with this status ("open", "closed","*"=all)', default='open')
    parser.add_argument('-x', '--excludeusers', help='ignore issues by these users (comma-separated list)', default=None)
    
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
    if(args.excludeusers):
      ignoredusers = args.excludeusers.split(",")
      print(f"Will ignore issues with the following assignees: {', '.join(ignoredusers)}")
    
    
    # Get all issues in the project
    issues = redmine.get_all_project_issues(project_id, args.whatStatus)

    missingFrom = []
    failedUpdate = {}
    failedNames = []
    # Iterate over the issues
    print(f"Doing updates for project {project_name}") 
    count = 0
    for issue in issues:
        # Use the following if seerver should complain on too many requests
        # if count >= 100:
        #   print("sleep a while")
        #   time.sleep(60)
        #   count = 0
        if args.excludeusers and get_field(issue, "assigned_to") not in ignoredusers:
          continue
        if args.onlyissue and str(issue['id']) != args.onlyissue:
          continue
        # Read From field
        values = get_field(issue, args.fromfield)
        # capture empty From-field
        if values == None or values == '':
          missingFrom.append(str(issue['id']))
          continue
        # Always work with lists; split strings if needed
        if args.separator !=  None:
          if args.separator == "\\n":
            values = values.splitlines()
          else:
            values = re.split(args.separator, values)
        else:
          values = [ values ]
          # NB inactivated users are omitted when userNameToId is created; the following conditinal approach 
        # Special case: convert user Ids
        if args.userids:
          # does not copletely solve the issue, but makes it catchable in a later try except clause
          values = [ userNameToId[val] if val in userNameToId.keys() else val for val in values ] 
        values = set([ str(a) for a in values ])
        #Check To field -- capture any existing values
        target = get_field(issue, args.tofield)
        # Always work with lists -- split string if needed
        if target == None or target == '':
          target = []
        elif type (target) != list:
          if args.newseparator != None:
            if args.newseparator == "\\n":
              target = target.splitlines()
            else:
              target = target.split(args.newseparator)
          else:
            target = [ target ]
            
        # Using python sets simplifies and removes duplicate values
        target = set([ str(a) for a in target ])
        # All values already in To filed
        if len(values.difference(target)) == 0:
          if args.longoutput:
            print(f"issue #{issue['id']}: "+
                  f"All {args.fromfield} value(s) {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target.intersection(values) ]} "+
                  f"already in {args.tofield} field: {[ userIdToName[a] if args.userids else a for a in target ]}")
          continue
        
        target = target.union(values)
        # Go back to lists -- mainly for the sake of stdout/err messages
        ret = list(target)
        if args.newseparator:
          ret = f"\r\n".join(ret) if args.newseparator == "\\n" else f"{args.newseparator}".join(ret) 

        commonErrMsg = ( f"issue #{issue['id']}: " +
          f"{args.fromfield} values {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target.intersection(values) ]} "+
          f"copied to {args.tofield} => {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target ]} "+ 
          f"as string '{ret}'" )
        
        if args.userids:
          if list(values)[0] in failedNames:
            continue
        fail = False
        if args.userids:
          for t in target:
            if t not in userIdToName.keys():
              print(f"***ERROR: User {t} not recognized: " + commonErrMsg)
              # f"issue #{issue['id']}: + f"values {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target.intersection(values) ]} copied to {args.tofield} "+
              failedUpdate[issue['id']] = f"User {t} not found in userIdToName database"
              # f"=> {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target ]}")
              fail= True
        if fail: 
          continue

        if args.dryrun:
          print(f"Dry run: Would have updated: " + commonErrMsg)
          #  f"issue #{issue['id']}: + f"{args.fromfield} values {[ userIdToName[a] if args.userids and a in userNameToId.keys() else a for a in target.intersection(values) ]} "+
          # f"copied to {args.tofield} => {[ userIdToName[a] if args.userids and a in userNameToId.keys() else a for a in target ]}")
          continue

        # Use exceptions to handle errors for individual issues
        try:
          count += 1
          redmine.update_issue_custom_field(issue, str(args.tofield), ret)
        except requests.exceptions.HTTPError as err:
        # except requests.exceptions.RequestException as err:
          print(f"***ERROR: Failed the following update: " + commonErrMsg)
          # f"issue #{issue['id']}: + f"values {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target.intersection(values) ]} copied to {args.tofield} "+
          # f"=> {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target ]}")
          failedUpdate[issue['id']] = err
          failedNames.append(list(values)[0])
          continue
        print(f"Updated: "+ commonErrMsg)
        # f"issue #{issue['id']}: + f"values {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target.intersection(values) ]} copied to {args.tofield} "+
        # f"=> {[ userIdToName[a] if args.userids and a in userIdToName.keys() else a for a in target ]}")
        
    # Collect log output at the end
    if args.longoutput and len(missingFrom) !=0:
        print("\nThe following issues has no value in the 'From' field\n{a}".format(a='\n'.join(missingFrom)))
    if len(failedUpdate) !=0:
        print(f"\nUpdate failed for the following issues:")
        for f in failedUpdate:
          print(f"Issue {f} : {failedUpdate[f]}")
        print()

if __name__ == '__main__':
    # Run the main function
    main()




