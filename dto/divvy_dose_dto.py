from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Team:
    name:str

@dataclass
class User:
    name:str

@dataclass
class Repository:
    name:str
    repo_type:str  # original / forked
    language:str
    topics:List[str]
    watchers:int

@dataclass
class Languages:
    languages:List[str]
    total:int
    
@dataclass
class Topics:
    topics:List[str]
    total:int
    
@dataclass
class Repositories:
    repositories:List[Repository]
    total:int


@dataclass
class OrganizationInfo:
    """ Top level response class for organization Info. Can be used to serialize / share schema with api consumers """
    organization:str
    total_forked_repos:int
    total_repos:int
    total_watchers:int
    languages:Languages
    topics:Topics
    repositories:Dict[str, List[Repository]]

    
"""  
The profile should include the following information (when available):
○ Total number of public repos (seperate by original repos vs forked repos)
○ Total watcher/follower count
○ A list/count of languages used across all public repos
○ A list/count of repo topics

"""