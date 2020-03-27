import unittest
from dto.divvy_dose_dto import OrganizationInfo, Repository, Languages, Topics 
from service.repository_service import RepositoryService
from constants import FORKED_TYPE_NAME, ORIGINAL_TYPE_NAME

class RepositoryServiceTests(unittest.TestCase):
    
    def setUp(self):
        from app import divvy_dose_app
        self.divvy_dose_app = divvy_dose_app
        with divvy_dose_app.app.app_context():
            self.repository_service = RepositoryService()

    def tearDown(self):
        pass
    
    def _get_test_organization_info(self):
        """ Gets test OrganizationInfo DTO """
        languages = Languages(languages=[], total=0)
        topics = Topics(topics=[], total=0)
        repository_1 = Repository(name='themainrepo', repo_type=ORIGINAL_TYPE_NAME, language='python',topics=['games', 'python'], watchers=2)
        repository_2 = Repository(name='webapp', repo_type=FORKED_TYPE_NAME, language='javascript',topics=['infolist','javascript','Python'], watchers=3)
        repositories ={ORIGINAL_TYPE_NAME:[repository_1], FORKED_TYPE_NAME:[repository_2]}
        organization_info_dto = OrganizationInfo(organization='pygame',repositories=repositories, total_forked_repos=0, total_repos=0, \
                                                 total_watchers=0, languages=languages, topics=topics)
        return organization_info_dto

    def test_get_organization_totals(self):
        organization_info = self._get_test_organization_info()
        topics, languages, total_watcher_count = self.repository_service.get_organization_totals(organization_info)
        self.assertEqual(topics.total, 4, 'Should have 4 topics')
        self.assertEqual(languages.total, 2, 'Should have 2 languages')
        self.assertEqual(total_watcher_count, 5, 'Should have 5 topics')

    def test_get_repositories_by_organization_and_team(self):
        """ Create Mock JSON responses from github and bitbucket repo / watchers endpoints and check the parsing returns and entire OrganizationInfo.  Instead of mocking tested directly with Swagger UI"""
        pass

    def test_parse_github_response(self):
        """ Create Mock JSON response from github and check the parsing returns list of repositoryDtos"""
        pass
    
    def test_parse_bitbucket_repository_response(self):
        """ Create Mock JSON response from bitbucket and check the parsing returns list of repositoryDtos"""
        pass

if __name__ == "__main__":
    unittest.main()
