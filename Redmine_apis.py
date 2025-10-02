import requests
import pdb
from pprint import pprint
import sys
import datetime

# "freestanding" util functions
#------------------------------
def get_field(issue, field_name):
  """
  Retrieve the value of any field, including custom_fields, from an issue.
  
        Args:
        issue: A dict with formatted issue info to be searched
        field_name: a string with the name of the requested field 

        Returns: 
        field value     if field exists
        empty string    otherwise
  """
  if field_name in issue.keys():
    # get field value
    field_value = issue[field_name]
    if field_value == None:
      field_value = ''
    elif isinstance(field_value, dict): #len(field_value) > 1:
      field_value = field_value['name']
    return field_value
  else:
    return get_custom_field(issue, field_name)
  

def get_custom_field(issue, field_name):
  """
  Retrieve the value of a custom field from an issue.
      Args:
        issue: A dict with formatted issue info to be searched
        field_name: a string with the name of the requested field 

      Returns: 
        field value     if field exists
        empty string    otherwise
  """
  # get field value
  field_value = [ field['value'] for field in issue['custom_fields'] if field['name']==field_name ]
  if len(field_value) > 0 and field_value[0] != None:
    field_value = field_value[0]
  else:
    field_value = ''
  return field_value


def get_custom_field_id(issue, field_name):
  """
  Retrieve the id of a custom field from an issue.
      Args:
        issue: A dict with formatted issue info to be searched
        field_name: a string with the name of the requested field 

      Returns: 
        field id     if field exists
        None        otherwise
  """
  # get field value
  field_id = [ field['id'] for field in issue['custom_fields'] if field['name']==field_name ]
  if len(field_id) > 0:
    field_id = field_id[0]
  else:
    field_id = None
  return field_id
  

# Main class for interacting with the Redmine REST API
#-------------------------------------------------------
class Redmine_server_api:
    """
    Class to interact with the Redmine Server API.
    """

    def __init__(self, config):
      """
      create a object from a config file'
      
      Args:
        config: a dictionary with the redmine url and its api key
      """
      self.baseurl    = config['url']
      self.headers    = {
                            "X-Redmine-API-Key": config['api_key']
      #                     "Accept": "application/json",
      #                     "Content-Type": "application/json",
                        }
    

    def get_project_memberships(self, project_id):
      """
      Get the members of a project_id 

      Args:
        project_id (int): The ID of the project.

      Returns:
        list: A list of dictionaries with user info for all members in the project.

      """
      users = []
      for offset in range(0,1000,100):
          url = f"{self.baseurl}/projects/{project_id}/memberships.json?offset={offset}&limit=100"
          # Get project memberships including user details
          response = requests.get(url, headers=self.headers)
          if response.status_code == 200:
              data = response.json()
              users.extend(data["memberships"])
              if data['total_count'] <= len(users):
                  break
          else:
              print(f"Failed to get memberships: {response.status_code}")
              return None
      return users

    def create_user_id_to_name(self, project_id):
      """
      Create a dict translating user id to user name for all members of a project_id 
      
      Args:
           project_id (int): The ID of the project.
  
      Returns:
          dict: A dictionary mapping id to name for all users in the project.
  
      """
      memberships = self.get_project_memberships(project_id)
      if memberships:
        users = {}
        for membership in memberships:
          if "user" in membership:
            name = membership["user"]['name']
            if "id" in membership:
                id = membership["user"]["id"]
                users[f"{id}"] = name
        users[''] = ''   #Fall back 1  
        users[None] = '' #Fall back 2
        return users
      else:
        return []
      
    def create_user_name_to_id(self, project_id):
      """
      Create a dict translating user name to user id for all members of a project_id 
      
      Args:
           project_id (int): The ID of the project.
  
      Returns:
          dict: A dictionary mapping id to name for all users in the project.
  
      """
      memberships = self.get_project_memberships(project_id)
      if memberships:
        users = {}
        for membership in memberships:
          if "user" in membership:
            name = membership["user"]['name']
            if "id" in membership:
                id = membership["user"]["id"]
                users[name] = id
        users[''] = None   #Fall back 1  
        users[None] = None #Fall back 2
        return users
      else:
        return []

    def get_all_projects(self):
      """
      Retrieve all projects from Redmine API by paginating through the results.
      
      Returns:
        projects: A list of all projects

      """
      projects = []
      page = 1
      while True:
          response = requests.get(f"{self.baseurl}/projects.json", headers=self.headers, params={"page": page})
          response.raise_for_status()
          data = response.json()
          projects.extend(data['projects'])
          if data['total_count'] <= len(projects):
              break
          page += 1
      return projects
    
    def find_project_id_from_name(self, project_name):
      """
      Get the project_id corresponding to project_name
      Args:
           project_name (string):  the name of the requestedd project
  
      Returns:
          int(?): The id of the requested project
      """     
      project_id = None
      projects = self.get_all_projects()
      for project in projects:
          if project['name'] == project_name:
              return project['id']
            
      # exit if project not found
      print(f"Project '{project_name}' not found.")
      return
    
    
    
    def get_all_project_issues(self, project_id, status_id = 'open'):
      """
      Retrieve all issues in a project from the Redmine API by paginating through the results.
  
      Args:
          project_id (int): The ID of the project.
          status_id (string): Retrieve only projects with status status_id (valid value ='open', 'closed', 'all'? -- check this!)
  
      Returns:
          list: A list if dictionaries with issue info for all issues in the project.
  
      """
      issues = []
      page = 1
      while True:
          # Retrieve issues for the current page
          response = requests.get(f"{self.baseurl}/issues.json", headers=self.headers, params={"project_id": project_id, "status_id": status_id, "page": page }) 
          response.raise_for_status()

          data = response.json()
          issues.extend(data['issues'])

          # Break the loop if all issues have been retrieved
          if data['total_count'] <= len(issues):
              break
  
          # Move to the next page
          page += 1
  
      return issues


    # def update_issue_standard_field(self, issue, field_name, value, id):
    #     """
    #     WORK IN PROGRESS -- it is unclear how to determine which fields take a string and which takes an id
    #     also the field "Assignee" is not called  as "assigned_to" as in get calls, but as "assigned_to_id"
    #     -- A jungle!
    #     
    #     Update the value of the given field in a given issue in the current
    #     Redmine instance. NB! Overwrites current value.
    #     """
    #     raise Exception("Not working currently -- WORK IN PROGRESS")
    #   
    #     # Create the payload for updating the issue status, and suppress email notifications and surveys
    #     payload = {
    #         "suppress_mail" : "1",
    #         "issue": {
    #           field_name: id, #{ 
    #             #"name": value, 
    #            # "id": id
    #           #},
    #         }
    #     }
    #     
    #     return self.__update_issue(issue, payload)
    


    def update_issue_custom_field(self, issue, field_name, value):
        """
        Update the value of the given field in a given issue in the current
        Redmine instance. NB! Overwrites current value.
        """
        field_id = get_custom_field_id(issue, field_name)
        # Create the payload for updating the issue status, and suppress email notifications and surveys
        payload = {
            "suppress_mail" : "1",
            "issue": {
                "custom_fields": [
                                    {
                                    "value": value, 
                                    "id": field_id
                                    }
                                ]
            },
        }
        
        return self.__update_issue(issue, payload)
    
    def fetch_issue(self, issue_id):
      """
      Fetch and cache issue details to minimize API requests.
      """
      issue_cache = {}
      if issue_id in issue_cache:
          return issue_cache[issue_id]
  
      response = requests.get(f"{self.baseurl}/issues/{issue_id}.json", headers=self.headers)
  
      if response.status_code == 200:
          issue_data = response.json()['issue']
          issue_cache[issue_id] = issue_data
          return issue_data
      else:
        raise Exception(f"Failed to fetch issue data: {response.status_code}")

    
    def __update_issue(self, issue, payload):
        """
        Helper function for updating fields in an issue
        should not be called directly
        """

        # check if important issue fields are None (will crash redmine if they are)
        fields = ['description']
        for field in fields:
            if issue[field] is None:
                payload['issue'][field] = ''
        #pprint(payload)
        # check if custom fields are None (will crash redmine if they are)
        for field in issue['custom_fields']:
          if field['value'] is None:
            payload['issue']['custom_fields'].append({'id': field['id'], 'value': ''})
          # check if custom fields have leading or trailing white spaces (email with white spaces will crash redmine)
          elif isinstance(field['value'], list) == False and field['value'] != field['value'].strip():
            pprint(f"{field['value']} != {field['value'].strip()}:")
            payload['issue']['custom_fields'].append({'id': field['id'], 'value': field['value'].strip()})
        # set url to update issue
        issue_url = f"{self.baseurl}/issues/{issue['id']}.json"
    
        # Update the issue
        response = requests.put(issue_url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response


    def fetch_time_entries(self,  user_id, start_date, end_date):
        """
        Helper function for producing a Spent time report
        should not be called directly
        arguments:
          start_date and end_date: in isoformat,e.g., 2024-09-11
          user_id
        """
        # start_date = datetime.date(year, 1, 1).isoformat()
        # end_date = datetime.date(year, 12, 31).isoformat()
        limit = 100  # Adjust based on your needs
        offset = 0
        time_entries = []
    
        times=0
        page = 1
        while True:
            params = {
                'user_id': user_id,
                'from': start_date,
                'to': end_date,
                'limit': limit,
                'page': page,
                'tracker': True,
            }
            response = requests.get(f"{self.baseurl}/time_entries.json", headers=self.headers, params=params)
#            response = requests.get(f'{base_url}/time_entries.json', headers=headers, params=params)
            if response.status_code != 200:
                print("Failed to fetch data:", response.status_code)
                break
    
            data = response.json()
            time_entries.extend(data.get('time_entries', []))

            if len(data.get('time_entries', [])) < limit:
                break  # Exit loop if last page
    
            page += 1
            times += 1
            
#            offset += limit
        return time_entries
    
    def report_time_entries_by_activity_and_month(self, user_id, start_date, end_data):
      
        time_entries = self.fetch_time_entries(user_id, start_date, end_data)
        activity_report = {}
        for entry in time_entries:
            activity = entry['activity']['name']
            spent_date = datetime.datetime.strptime(entry['spent_on'], '%Y-%m-%d').date()
            month = f"{spent_date.year}-{spent_date.month}"
            hours = entry['hours']
            if activity not in activity_report:
                activity_report[activity] = { 'Total time' : 0 }  # Initialize if not exist
            
            if month not in activity_report[activity]:
                activity_report[activity][month] = 0  # Initialize month if not exist
            
            activity_report[activity][month] += hours
            activity_report[activity]['Total time'] += hours
            
        return activity_report
    
    def report_time_entries_by_issue(self, user_id, start_date, end_data):
      
        time_entries = self.fetch_time_entries(user_id, start_date, end_data)
        issue_report = {}
        for entry in time_entries:
            issue_id = entry['issue']['id']
            project = entry['project']['name']
            hours = entry['hours']
            if issue_id not in issue_report:
                issue = self.fetch_issue(issue_id)
                tracker = get_field(issue, 'tracker')
                name = get_field(issue, 'subject')
                issue_report[issue_id] = { 'Project' : project, 'Tracker' : tracker, 'Name' : name, 'Total time' : 0 }  # Initialize if not exist
            issue_report[issue_id]['Total time'] += hours

        return issue_report
    
