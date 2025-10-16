#!/bin/env python3

# Author: Martin D, NBIS

# make the parent directory available for imports, to be able to import Redmine_apis.py there
import sys
sys.path.append('..')

from Redmine_apis import Redmine_server_api
from email.mime.text import MIMEText
from pprint import pprint
import argparse
import datetime
import logging
import os
import pdb
import smtplib
import time
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# load arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Path to the YAML config file', required=True)
parser.add_argument('-s', '--start-date', help='Start date in YYYY-MM-DD format', required=True)
parser.add_argument('-e', '--end-date', help='End date in YYYY-MM-DD format', required=True)
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-d', '--dry-run', action='store_true', help='Dry run mode, do not send emails or update issues')
args = parser.parse_args()

if args.verbose:
    logger.setLevel(logging.DEBUG)

if args.dry_run:
    logger.info('Dry run mode enabled, no emails will be sent and no issues will be updated')

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
redmine_project_ids = [ proj['id'] for proj in redmine_projects if proj['name'] in ['Test project', 'National Bioinformatics Support', 'Long-term Support'] ]

# fetch all issues with logged time entries
logger.info('Fetching all issues that might have been closed or resolved in the requested interval, and that are marked for survey')
issues = []
for redmine_project_id in redmine_project_ids:
    logger.debug(f'Project ID: {redmine_project_id}')
    issues += redmine.get_all_project_issues(redmine_project_id, status_id=3, extra_params={'updated_on': f'>={args.start_date}', 'cf_22': '1', 'tracker_id': '3'})  # status_id 3 = Resolved, tracker_id=3 (Support)
    issues += redmine.get_all_project_issues(redmine_project_id, status_id=5, extra_params={'updated_on': f'>={args.start_date}', 'cf_22': '1', 'tracker_id': '3'}) # status_id 5 = Closed, tracker_id=3 (Support)
issues_by_id = { issue['id']: issue for issue in issues }

# go through all issues with status resolved and check if they were resolved in the requested interval
logger.info('Filtering issues closed or resolved in the requested interval')
resolved_issues = []
found = False
for issue in issues:

    if issue['subject'].startswith('[DM]'):
        logger.debug(f'Skipping issue {issue["id"]} as it is a DM issue')
        continue

    # fetch the journal entries for the issue
    journals = redmine.get_issue_journals(issue['id'])
    
    # find the journal entry that changed the status to resolved or closed
    for journal in reversed(journals):
        for detail in journal['details']:
            if detail['name'] == 'status_id' and detail['new_value'] in ['3', '5']:  # 3 = resolved, 5 = closed
                change_date = datetime.datetime.strptime(journal['created_on'], '%Y-%m-%dT%H:%M:%SZ').date()
                if change_date >= datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() and change_date <= datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date():
                    found = True # set to break the outer loop as well
                    resolved_issues.append(issue)
                    logger.debug(f"Issue {issue['id']} resolved on {change_date}")
                break
        # break the outer loop if close/resolve found
        if found:
            found = False
            break
    
# print out the PI email and url to the issue
if args.verbose:
    logger.debug('Issues to send survey for:')
    for issue in resolved_issues:
        custom_fields = { cf['id']: cf['value'] for cf in issue.get('custom_fields', []) }
        pi_email = custom_fields.get(18) 
        issue_url = f"{redmine.baseurl}/issues/{issue['id']}"
        logger.debug(f"{pi_email}\t{issue_url}")

# send out the survey emails
logger.info('Starting to send out survey emails')
for issue in resolved_issues:
    custom_fields = { cf['id']: cf['value'] for cf in issue.get('custom_fields', []) } # get all custom fields as a dict
    pi_email = custom_fields.get(18) # custom field 18 = PI email
    issue_url = f"{redmine.baseurl}/issues/{issue['id']}"
    if not pi_email:
        logger.warning(f'No PI email found for issue {issue["id"]}, skipping ({issue_url})')
        continue

    # prepare email body
    email_body = f"""Thank you for using NBIS support recently in your project '{issue['subject']}'. To help us improve our services, we kindly ask that you fill out a short, ~2 minutes, anonymous survey. 

Survey link:  https://nbis.typeform.com/to/MzYPp6F7

If someone else was the main contact with NBIS for your project, please feel free to get their input on any question where applicable.
Thanks in advance and have a nice day!"""

    # send email
    email_subject = f"NBIS User Survey - Feedback for \'{issue['subject']}'"
    logger.debug(f'Sending email to {pi_email} for issue {issue["id"]}')
    msg = MIMEText(email_body)
    msg['Subject'] = email_subject
    # add a from address with a name
    msg['From'] = f"NBIS Support System <{config['smtp_user']}>"
    msg['To'] = pi_email
    with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
        server.starttls()
        server.login(config['smtp_user'], config['smtp_password'])
        if args.dry_run:
            logger.info(f'DRY RUN: Email not sent to {pi_email} for issue {issue["id"]}')
        else:
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            logger.info(f'Email sent to {pi_email} for issue {issue["id"]}')

    # update the issue description to add a note about survey sent, and disable send survey custom field (cf_22) to 0
    if not args.dry_run:
        # add a note about survey sent to the issue and which date
        logger.debug(f'Updating issue {issue["id"]} to add note about survey sent.')
        redmine.update_issue_description(issue, f"{issue['description']}\n\nSurvey email sent to {pi_email} on {datetime.datetime.now().strftime('%Y-%m-%d')}.")
        logger.debug(f'Disabling send survey custom field for issue {issue["id"]}.')
        redmine.update_issue_custom_field(issue, 22, '0')  # custom field 22 = send survey
        logger.info(f'Issue {issue["id"]} updated to add note about survey sent and disable send survey custom field.')
    else:
        logger.info(f'DRY RUN: Issue {issue["id"]} not updated to add note about survey sent or disable send survey custom field.')

    #sys.exit(0)
    # wait for a bit to avoid overwhelming the email server
    #time.sleep(1)

logger.info('All survey emails sent')
logger.info('Script completed successfully')
# end of script







