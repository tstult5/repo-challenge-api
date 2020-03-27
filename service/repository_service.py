from dto.divvy_dose_dto import Repository as RepositoryDto,  OrganizationInfo as OrganizationInfoDto, Languages as LanguagesDto, Topics as TopicsDto
from client.api_clients import GitHubAPIClient, BitbucketAPIClient
from constants import GITHUB_SOURCE_NAME, BITBUCKET_SOURCE_NAME, FORKED_TYPE_NAME, ORIGINAL_TYPE_NAME
from flask import current_app
from typing import List
import logging

class RepositoryService:

    def __init__(self):
        self.logger = logging.getLogger('divvy_dose_app')
        self.github_client = GitHubAPIClient()
        self.bitbucket_client = BitbucketAPIClient()
        self.caches = current_app.caches 

    def _set_or_get_cached_response(self, repo:List, cache_key:str, api_name:str):
        """if no results from API, check the cache. If response is present, cache it """
        if not repo:
            repo = current_app.caches[api_name].get_cached_repositories(cache_key)
            if repo:
                return repo
            return []
        else:
            current_app.caches[api_name].set_cached_repositories(repo, cache_key)
            return repo

    def get_repositories_by_organization_and_team(self, organization_name:str, team_name:str):
        """ Gets Repository information from API sources by organization and team names. 
            Checks cache for recent responses. Attempts to retrieve from cache on API failure. """
        repo_map = {FORKED_TYPE_NAME:[], ORIGINAL_TYPE_NAME:[]}
        
        """ Check cache for recent responses. """
        original_github_repos = self._set_or_get_cached_response(None, organization_name + '_'+ ORIGINAL_TYPE_NAME, GITHUB_SOURCE_NAME)
        if not original_github_repos:
            github_repo_response = self.github_client.get_repository_for_organization_name(organization_name)
            original_github_repos = self.parse_github_repository_response(github_repo_response, False)
            original_github_repos = self._set_or_get_cached_response(original_github_repos, organization_name + '_'+ ORIGINAL_TYPE_NAME, GITHUB_SOURCE_NAME)

        forked_github_repos = self._set_or_get_cached_response(None, organization_name + '_'+ FORKED_TYPE_NAME, GITHUB_SOURCE_NAME)
        if not forked_github_repos:
            github_forked_repo_response = self.github_client.get_all_forks_for_repositories_and_organization(original_github_repos, organization_name)
            forked_github_repos = self.parse_github_repository_response(github_forked_repo_response, True)
            forked_github_repos = self._set_or_get_cached_response(forked_github_repos, organization_name + '_'+ FORKED_TYPE_NAME, GITHUB_SOURCE_NAME)

        repo_map[ORIGINAL_TYPE_NAME].extend(original_github_repos)
        repo_map[FORKED_TYPE_NAME].extend(forked_github_repos)
        
        original_bitbucket_repos = self._set_or_get_cached_response(None, team_name + '_'+ ORIGINAL_TYPE_NAME, BITBUCKET_SOURCE_NAME)
        if not original_bitbucket_repos:
            bitbucket_repo_response = self.bitbucket_client.get_repositories_by_team_name(team_name)
            original_bitbucket_repos = self.parse_bitbucket_repository_response(team_name, bitbucket_repo_response, False)
            original_bitbucket_repos = self._set_or_get_cached_response(original_bitbucket_repos, team_name + '_'+ ORIGINAL_TYPE_NAME, BITBUCKET_SOURCE_NAME)
        
        forked_bitbucket_repos = self._set_or_get_cached_response(None, organization_name + '_'+ FORKED_TYPE_NAME, BITBUCKET_SOURCE_NAME)
        if not forked_bitbucket_repos:
            bitbucket_forked_repo_response = self.bitbucket_client.get_all_forks_for_repositories_and_team(original_bitbucket_repos,  team_name)
            forked_bitbucket_repos = self.parse_bitbucket_repository_response(team_name, bitbucket_forked_repo_response, True)
            forked_bitbucket_repos = self._set_or_get_cached_response(forked_bitbucket_repos, organization_name + '_'+ FORKED_TYPE_NAME, BITBUCKET_SOURCE_NAME)

        repo_map[ORIGINAL_TYPE_NAME].extend(original_bitbucket_repos)
        repo_map[FORKED_TYPE_NAME].extend(forked_bitbucket_repos)

        total_repos =   len(repo_map[ORIGINAL_TYPE_NAME])
        total_forked_repos = len(repo_map[FORKED_TYPE_NAME])
        
        organization_info = OrganizationInfoDto(organization=organization_name, repositories=repo_map, total_repos=total_repos,\
                                                 total_forked_repos=total_forked_repos, total_watchers=0, languages=None, topics=None)

        topics, languages, total_watcher_count = self.get_organization_totals(organization_info)
        organization_info.languages = languages
        organization_info.total_watchers = total_watcher_count
        organization_info.topics = topics
        return organization_info

    def get_organization_totals(self, organization_info:OrganizationInfoDto):
        """ Maps through the entire OrganizationInfoDto and creates top-level list and counts of topics, languages and watchers for the entire org."""
        topics = TopicsDto(topics=[], total=0)
        languages = LanguagesDto(languages=[],total=0)
        total_watcher_count = 0

        repo_list = organization_info.repositories.get(FORKED_TYPE_NAME,[]) + organization_info.repositories.get(ORIGINAL_TYPE_NAME,[])

        total_watcher_count = sum(map(lambda x: x.watchers, repo_list))
        languages.languages = list(filter(None, set(map(lambda x: x.language.lower(), repo_list))))
        languages.total = len(languages.languages)
        topic_list = []
        list(map(lambda x: topic_list.extend(x.topics), repo_list))
        topics.topics  = list(filter(None, set(map(lambda x: x.lower() , topic_list))))
        topics.total = len(topics.topics)

        return topics, languages, total_watcher_count

    def parse_github_repository_response(self, github_response:dict, fork=False):
        """ Parses Json dictionary from github /repository endpoint. If it's an error message it responds with empty so the cache can be checked for a proper response"""
        if 'error' in github_response:
            return None

        repositories = []
        repo_type = 'fork' if fork else 'original'
        for repo in github_response:
            repository_dto = RepositoryDto(name=repo['name'], repo_type=repo_type, topics=repo['topics'], language=repo['language'] if repo['language'] else '',  watchers=repo['watchers'])
            repositories.append(repository_dto)
        return repositories
    
    def parse_bitbucket_repository_response(self,team_name:str, bitbucket_response:dict, fork=False):
        """ Parses Json dictionary from bitbucket /repository endpoint. If it's an error message it responds with empty so the cache can be checked for a proper response"""
        if 'error' in bitbucket_response or 'values' not in bitbucket_response:
            return None
        repositories = []
        repo_type = 'fork' if fork else 'original'

        topics =[]
        for repo in bitbucket_response['values']:
            original_bitbucket_repo_watchers = self.bitbucket_client.get_watchers_by_team_and_repository_name(team_name, repo['name'])
            watcher_count = original_bitbucket_repo_watchers.get('size', 0)
            repository_dto = RepositoryDto(name=repo['name'], repo_type=repo_type, topics=topics, language=repo['language'], watchers=watcher_count)
            repositories.append(repository_dto)
        return repositories
