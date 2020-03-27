from flask import request
from dataclasses_serialization.json import JSONSerializer 
from dto.divvy_dose_dto import OrganizationInfo as OrganizationInfoDto 
from service.repository_service import RepositoryService

def get_repositories_by_organization_and_team(organization_name:str, team_name:str, include_repo_detail:str):
    """ Gets Organization Info for public original and forked repos from github with organization_name, and bitbucket with team name.
        If only top-level stats are desired, pass in include_repo_detail=false, otherwise you can opt to include specific details about each repo. """
    repository_service = RepositoryService()
    organization_info_dto = repository_service.get_repositories_by_organization_and_team(organization_name, team_name)

    if  include_repo_detail == 'false':
        organization_info_dto.repositories = {}
    return JSONSerializer.serialize(organization_info_dto), 200