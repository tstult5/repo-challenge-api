import requests
import settings
import math
from typing import List
from datetime import datetime


class GitHubAPIClient():
    """ Github api calls.  There is a header available to pass in that allows latest version to obtain the Topics node with the response. 
        With this version of the API you have to follow a second endpoint for all of the forks of a repo. This results in n+1 calls which is expensive 
        and mitigated with caching, but I would seek to find a call with the information in a single call with nested info.  """
    def __init__(self):
        self.github_api_config = settings.API_CLIENTS['github']
        self.github_headers = {'Accept':'application/vnd.github.mercy-preview+json'}
        
    def get_repository_for_organization_name(self, organization_name:str):
        """ Gets original public repositories. NOTE github caps unauthorized calls at 60 PER HOUR.  Need to configure user or Token """
        url_repo_by_organization = '/orgs/{}/repos'

        try:
            api_url = self.github_api_config['BASE_URL'] + url_repo_by_organization.format(organization_name)
            response = requests.get(api_url, headers=self.github_headers, timeout=self.github_api_config['TIMEOUT_MILLISECONDS'])
            if response.status_code != 200:
                return {'error':'Github API Error ', 'http_status_code':response.status_code}
            json_data = response.json()
            if not json_data:
                return {'error':'empty_json', 'http_status_code':500}
            return json_data
        except Exception as e:
            return {'error':'response 500 from client', 'http_status_code':500}

    def get_all_forks_for_repositories_and_organization(self, repositories:List, organization_name:str):
        """ Gets forks for a list of repos by organization. """
        fork_responses = []
        if not repositories:
            return fork_responses
        for repository in repositories:
            fork_response = self.get_all_forks_for_repository(organization_name, repository.name)
            if 'error' not in fork_response:
                fork_responses.extend(fork_response)
        return fork_responses
    
    def get_all_forks_for_repository(self, organization_name:str, repository_name:str):
        """ Gets forks of a Repo for a repo name and  organization. """
        try:
            api_url_forks = self.github_api_config['BASE_URL'] + '/repos/{}/{}/forks'.format(organization_name, repository_name)
            response = requests.get(api_url_forks, headers=self.github_headers, timeout=self.github_api_config['TIMEOUT_MILLISECONDS'])
            if response.status_code != 200:
                return {'error':'Github Forks API Error ', 'http_status_code':response.status_code}
            json_data = response.json()
            if not json_data:
                return {'error':'empty_json', 'http_status_code':500}
            return json_data
        except Exception as e:
            return {'error':'response 500 from client', 'http_status_code':500}

class BitbucketAPIClient():

    def __init__(self):
        self.bitbucket_config = settings.API_CLIENTS['bitbucket']
        self.bitbucket_headers = 'Accept: application/json'
        
    def get_repositories_by_team_name(self, team_name:str):
        url_team_by_team_name = '/{}/repositories/{}'
        api_url = self.bitbucket_config['BASE_URL'] + url_team_by_team_name.format(self.bitbucket_config['VERSION'], team_name)

        try:
            response = requests.get(api_url, timeout=self.bitbucket_config['TIMEOUT_MILLISECONDS'])
            if response.status_code != 200:
                return {'error':'BitBucket API Error', 'http_status_code':response.status_code}
            json_data = response.json()
            return json_data
        except Exception as e:
            return {'error':'BitBucket API Error {}'.format(e.getstatus()), 'http_status_code':500}
    
    def get_watchers_by_team_and_repository_name(self, team_name:str, repository_name:str):
        """ This calls for all watchers of a repo. Paginated - but we'll only call it once for the total count"""
        bb_watchers_url = self.bitbucket_config['BASE_URL'] +'/{}/repositories/{}/{}/watchers'.format(self.bitbucket_config['VERSION'], team_name, repository_name)
        try:
            response = requests.get(bb_watchers_url, timeout=self.bitbucket_config['TIMEOUT_MILLISECONDS'])
            if response.status_code != 200:
                return {'error':'BitBucket Watchers API Error', 'http_status_code':response.status_code}
            json_data = response.json()
            return json_data
        except Exception as e:
            return {'error':'BitBucket Watchers API Error {}'.format(e.getstatus()), 'http_status_code':500}
    
    def get_all_forks_for_repositories_and_team(self, repositories:List, team_name:str):
        forked_repos = {"values":[]}
        for repository in repositories:
            repo_forks = self.get_all_forks_by_team_and_repository_name(team_name, repository.name)
            forked_repos['values'].extend(repo_forks['values'])
        return forked_repos

    def get_all_forks_by_team_and_repository_name(self, team_name:str, repository_name:str):
        """ Gets all forks by team name. Paginated reponses start with page 1. API provides 'next' url for the next page, pagelen and size"""
        first_page = self.get_forks_by_team_name(team_name, repository_name, 1)
        if 'error' in first_page:
            return None
        page_count = math.ceil(first_page['size'] / first_page['pagelen'])
        for x in range(2, int(page_count)):
            next_page = self.get_forks_by_team_name(repository_name,  team_name, x)
            if 'error' not in next_page:
                first_page['values'].extend(next_page['values'])
        return first_page

    def get_forks_by_team_name(self, repository_name:str,  team_name:str, page:int):
        """ This calls for forks of a repo. Paginated. """
        bb_fork_url = self.bitbucket_config['BASE_URL'] +'/{}/repositories/{}/{}/forks?page={}'.format(self.bitbucket_config['VERSION'], repository_name, team_name, str(page))
        try:
            response = requests.get(bb_fork_url, timeout=self.bitbucket_config['TIMEOUT_MILLISECONDS'])
            if response.status_code != 200:
                return {'error':'BitBucket Forks API Error', 'http_status_code':response.status_code}
            json_data = response.json()
            return json_data
        except Exception as e:
            return {'error':'BitBucket Forks API Error {}'.format(e.getstatus()), 'http_status_code':500}
        