#!/bin/env python3

# Author: Martin D, NBIS

# make the parent directory available for imports, to be able to import Redmine_apis.py there
import sys
sys.path.append('..')

from Redmine_apis import Redmine_server_api
from pprint import pprint
import argparse
import datetime
import logging
import os
import pdb
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# load arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
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
projects = redmine.get_all_projects()

# get id of nbis project
logger.debug('Finding NBIS project ID')
nbis_project_id = [ proj['id'] for proj in projects if proj['name'] == 'National Bioinformatics Support' ][0]

# fetch all time entries from the nbis project this year
logger.info('Fetching time entries for NBIS project for the year 2024')
time_entries_period = redmine.fetch_time_entries_by_project_id(nbis_project_id, start_date='2024-01-01', end_date='2024-12-31')
time_entries_support_period = [ te for te in time_entries_period if te['activity']['name'] == 'Support' ]

# summarize time entries by issue
logger.debug('Summarizing time entries by issue')
time_entries_by_issue = {}
for te in time_entries_support_period:
    issue_id = te['issue']['id']

    # if it is the first time entry for this issue, initialize the entry
    if issue_id not in time_entries_by_issue:
        time_entries_by_issue[issue_id] = {'first': datetime.datetime.strptime(te['spent_on'], '%Y-%m-%d'), 'last': datetime.datetime.strptime(te['spent_on'], '%Y-%m-%d')}
    else:
        time_entries_by_issue[issue_id]['first'] = min(time_entries_by_issue[issue_id]['first'], datetime.datetime.strptime(te['spent_on'], '%Y-%m-%d'))
        time_entries_by_issue[issue_id]['last']  = max(time_entries_by_issue[issue_id]['last'],  datetime.datetime.strptime(te['spent_on'], '%Y-%m-%d'))

# fetch all issues with logged time entries
logger.info('Fetching all issues for NBIS project')
issues = redmine.get_all_project_issues(nbis_project_id, status_id='*', extra_params={'issue_id': ','.join([str(issue_id) for issue_id in time_entries_by_issue.keys()])})
issues_by_id = { issue['id']: issue for issue in issues }

### massage the data

# find issues that started earlier years and set first to the project start date
logger.debug('Adjusting first time entries for issues created before 2024')
for time_entry_issue_id in time_entries_by_issue.keys():
    issue = issues_by_id[time_entry_issue_id]
    issue_created_on_dt = datetime.datetime.strptime(issue['created_on'], '%Y-%m-%dT%H:%M:%SZ')
    if issue_created_on_dt < datetime.datetime(2024, 1, 1):
        time_entries_by_issue[time_entry_issue_id]['first'] = issue_created_on_dt

# find issues that are still open and check if they are more than 6 months old
logger.debug('Adjusting last time entries for issues still open')
time_entries_by_issue_keys = list(time_entries_by_issue.keys())  # create a static list of keys to avoid runtime error when deleting
for time_entry_issue_id in time_entries_by_issue_keys:
    issue = issues_by_id[time_entry_issue_id]
    if issue['status']['name'] in ['New', 'In Progress', 'Pending']:
        # check if the issue would end up in the 6+ months category regardless of being open
        if (datetime.datetime(2024, 12, 31) - time_entries_by_issue[time_entry_issue_id]['first']).days > 180:
            time_entries_by_issue[time_entry_issue_id]['last'] = datetime.datetime(2024, 12, 31)
        else:
            # skip issues that are still open but less than 6 months old
            logger.debug(f"Issue {time_entry_issue_id} is still open but less than 6 months old, skipping...")
            del time_entries_by_issue[time_entry_issue_id]



# summarize issues by lifespan categories
logger.info('Summarizing issues by lifespan categories')
lifespan_categories = {
    '<1 day': 0,
    '<1 week': 0,
    '<1 month': 0,
    '<6 months': 0,
    '6+ months': 0
}

lifespan_categories_ids = {
    '<1 day': [],
    '<1 week': [],
    '<1 month': [],
    '<6 months': [],
    '6+ months': []
}

for issue_id, times in time_entries_by_issue.items():
    lifespan_days = (times['last'] - times['first']).days
    if lifespan_days < 1:
        lifespan_categories['<1 day'] += 1
        lifespan_categories_ids['<1 day'].append(issue_id)
    elif lifespan_days < 7:
        lifespan_categories['<1 week'] += 1
        lifespan_categories_ids['<1 week'].append(issue_id)
    elif lifespan_days < 30:
        lifespan_categories['<1 month'] += 1
        lifespan_categories_ids['<1 month'].append(issue_id)
    elif lifespan_days < 180:
        lifespan_categories['<6 months'] += 1
        lifespan_categories_ids['<6 months'].append(issue_id)
    else:
        lifespan_categories['6+ months'] += 1
        lifespan_categories_ids['6+ months'].append(issue_id)


pdb.set_trace()
