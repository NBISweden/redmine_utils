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

    if project_id is None:
        print(f"Project '{project_name}' not found.")
        return

    # Create Redmine API URL for issues
#    url = f"{config['url']}/issues.json"
#    update_issue_status(f"{config['url']}/issues", headers, 7437, 6)
#    import sys
#    sys.exit(1)

    # Get all issues in the project
    issues = get_all_project_issues(f"{config['url']}/issues.json", headers, project_id)

    # Get the sub-project names to exclude
    exclude_projects = args.exclude.split(',') if args.exclude else []

    # Set url for status update
    url = f"{config['url']}/issues"

    l = {3361,3417,3595,3609,3611,3615,3618,3620,3622,3623,3626,3627,3628,3629,3635,3636,3637,3638,3639,3640,3641,3642,3643,3644,3645,3646,3647,3649,3650,3651,3653,3655,3658,3659,3660,3661,3662,3663,3664,3665,3666,3667,3668,3669,3670,3671,3672,3673,3674,3675,3676,3678,3679,3680,3681,3682,3683,3684,3685,3686,3799,3808,3812,3813,3817,3820,3822,3823,3826,3827,3830,3831,3834,3835,3836,3837,3838,3839,3840,3841,3843,3844,3845,3847,3850,3851,3852,3853,3854,3855,3948,4016,4018,4021,4022,4023,4025,4028,4029,4033,4034,4035,4036,4037,4038,4039,4045,4046,4049,4050,4051,4187,4194,4199,4200,4203,4206,4207,4209,4210,4211,4212,4215,4216,4217,4218,4219,4220,4221,4223,4224,4225,4227,4229,4230,4231,4232,4233,4331,4346,4348,4349,4350,4351,4352,4353,4354,4357,4358,4362,4363,4365,4366,4367,4368,4369,4480,4481,4483,4487,4488,4490,4491,4494,4500,4501,4503,4505,4508,4511,4514,4516,4517,4518,4519,4520,4525,4551,4590,4606,4607,4608,4614,4619,4621,4622,4627,4630,4631,4639,4641,4642,4644,4645,4647,4648,4649,4650,4652,4653,4654,4657,4659,4660,4661,4662,4664,4665,4666,4667,4668,4714,4752,4754,4755,4757,4759,4762,4763,4765,4766,4767,4768,4769,4772,4774,4775,4776,4777,4778,4779,4781,4782,4783,4784,4785,4911,4917,4919,4920,4922,4924,4928,4929,4930,4931,4932,4990,5007,5008,5018,5019,5020,5024,5026,5030,5032,5035,5036,5037,5038,5040,5041,5042,5045,5046,5048,5049,5051,5138,5151,5154,5165,5166,5169,5170,5171,5172,5173,5178,5179,5182,5333,5341,5367,5370,5371,5372,5375,5377,5378,5383,5384,5385,5386,5387,5388,5391,5393,5395,5396,5397,5398,5399,5400,5402,5404,5405,5406,5407,5408,5627,5640,5643,5645,5647,5648,5649,5650,5653,5654,5655,5660,5668,5676,5678,5684,5686,5687,5690,5794,5803,5804,5806,5810,5811,5812,5813,5814,5815,5817,5818,5819,5821,5822,5824,5825,5826,5827,5828,5829,5830,5831,5832,5833,5834,5835,5836,5837,5838,5841,5957,5960,5967,5973,5976,5979,5981,5982,5984,5985,5988,5989,5990,5991,5993,5994,5996,6016,6117,6118,6119,6120,6122,6124,6126,6127,6128,6129,6130,6132,6133,6136,6137,6138,6139,6140,6141,6142,6145,6160,6258,6259,6261,6266,6271,6275,6277,6279,6285,6287,6288,6289,6290,6291,6293,6294,6298,6299,6302,6304,6305,6307,6308,6309,6328,6444,6450,6452,6458,6459,6460,6461,6462,6463,6465,6466,6467,6468,6470,6471,6568,6573,6616,6626,6629,6630,6634,6635,6637,6638,6639,6643,6644,6645,6646,6647,6648,6649,6652,6653,6654,6656,6658,6661,6662,6664,6721,6731,6732,6733,6734,6735,6736,6737,6739,6741,6742,6743,6744,6745,6747,6748,6749,6750,6751,6753,6754,6755,6758,6759,6760,6762}

    # Iterate over the issues
    for issue in issues:
        #if issue['id'] != 7535:
        #    pdb.set_trace()
        #    continue
        #pdb.set_trace()

        # exclude issues that are already closed
        if issue['status']['name'] in ['Closed', 'Rejected', 'Resolved', 'Feedback', 'Declined by client']:
            continue

        # Exclude issues in the specified sub-projects
        if issue['project']['name'] not in exclude_projects:
            # Check if the issue's custom field "WABI ID" is empty
            if not get_custom_field(issue, 'WABI ID'):
                
                # remove issue id from set l
                l.remove(issue['id'])

                # pdb.set_trace()
                # Perform dry run if specified
                if args.dryrun:
                    print(f"Dry run: Would have updated {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}'")
                    continue
                else:
                    # Change the status of the issue to "Rejected"
                    # Print status message
                    print(f"Updating {issue['project']['name']} - issue #{issue['id']} - '{issue['subject']}'")
                    update_issue_status(url, headers, int(issue['id']), 6)  # assuming "Rejected" status ID is 6

    # Print the list of issues that were not updated
    print(f"Issues not updated: {l}")

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
        "suppress_mail" : "1",
        "issue": {
            "status_id": status_id,
            "notes": "Cleaning out old issues.",
            "custom_fields":
            [
              {
                  "value": '0', "id" : 22 #"name":"Send survey when closed"
              }
            ]
        },
    }
    issue_url = f"{url}/{issue_id}.json"
    # pdb.set_trace()
    response = requests.put(issue_url, headers=headers, json=payload)
    response.raise_for_status()
    return response

if __name__ == '__main__':
    # Run the main function
    main()




