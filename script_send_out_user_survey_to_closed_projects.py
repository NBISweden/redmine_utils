#!/bin/env python3

import os
import datetime
import yaml
import argparse
from pprint import pprint
from Redmine_apis import Redmine_server_api
import pdb
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# load arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
parser.add_argument('-s', '--start-date', help='Start date in YYYY-MM-DD format', required=True)
parser.add_argument('-e', '--end-date', help='End date in YYYY-MM-DD format', required=True)
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()

if args.verbose:
    logger.setLevel(logging.DEBUG)

# Load Redmine credentials from YAML config file
logger.debug(f'Loading config from {args.config}')
with open(args.config, 'r') as config_file:
    config = yaml.safe_load(config_file)

# create redmine utils object
logger.debug('Creating Redmine server API object')
redmine = Redmine_server_api(config)

# fetch all projects
logger.info('Fetching all projects from Redmine')
redmine_projects = redmine.get_all_projects()

# get id of nbis project
logger.debug('Finding project IDs of projects that should get sent to')
redmine_project_ids = [ proj['id'] for proj in redmine_projects if proj['name'] in ['Test project', 'Disabled National Bioinformatics Support'] ]

# fetch all issues with logged time entries
logger.info('Fetching all issues that might have been closed in the requested interval')
issues = redmine.get_all_project_issues(redmine_project_ids, status_id='closed,Resolved', extra_params={'updated_on': f'><{args.start_date}|{args.end_date}'})
issues_by_id = { issue['id']: issue for issue in issues }

pdb.set_trace()

# go through all issues with status resolved and check if they were resolved in the requested interval
logger.info('Filtering issues closed in the requested interval')
closed_issues = []
for issue in issues:

    # for closed issues
    if issue['status']['name'].lower() == 'closed':
            # check if closed_on is in the requested interval
        if 'closed_on' in issue and issue['closed_on']:
            closed_date = datetime.datetime.strptime(issue['closed_on'], '%Y-%m-%dT%H:%M:%S%z').date()
            start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()
            if start_date <= closed_date <= end_date:
                closed_issues.append(issue)


    # for resolved issues
    if issue['status']['name'].lower() == 'resolved':
            # check if resolved_on is in the requested interval
        if 'resolved_on' in issue and issue['resolved_on']:
            resolved_date = datetime.datetime.strptime(issue['resolved_on'], '%Y-%m-%dT%H:%M:%S%z').date()
            start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()
            if start_date <= resolved_date <= end_date:
                closed_issues.append(issue)












