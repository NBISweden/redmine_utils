import requests
import pdb
from pprint import pprint

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
    
    
    
    def get_all_project_issues(self, project_id):
      """
      Retrieve all issues in a project from the Redmine API by paginating through the results.
  
      Args:
          project_id (int): The ID of the project.
  
      Returns:
          list: A list if dictionaries with issue info for all issues in the project.
  
      """
      issues = []
      page = 1
      while True:
          # Retrieve issues for the current page
          response = requests.get(f"{self.baseurl}/issues.json", headers=self.headers, params={"project_id": project_id, "page": page})
          response.raise_for_status()
          data = response.json()
          issues.extend(data['issues'])

          # Break the loop if all issues have been retrieved
          if data['total_count'] <= len(issues):
              break
  
          # Move to the next page
          page += 1
  
      return issues


