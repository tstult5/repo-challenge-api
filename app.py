from connexion.resolver import RestyResolver
import connexion
import logging

from cache.api_cache import GitHubCache, BitBucketCache
from constants import GITHUB_SOURCE_NAME, BITBUCKET_SOURCE_NAME

""" Logging -  """
logging.basicConfig(level=logging.DEBUG)

"""  URL routing and Swagger documentation through connexion """
divvy_dose_app = connexion.FlaskApp(__name__, specification_dir='./')
divvy_dose_app.add_api('divvy-dose-api.yml', resolver=RestyResolver('api'))
divvy_dose_app.app.config.from_object('settings')
""" Caching for this demo purpose is a simple in-memory map. Would normally use Redis, e.g. configured here"""
divvy_dose_app.app.caches = { GITHUB_SOURCE_NAME:GitHubCache(), BITBUCKET_SOURCE_NAME:BitBucketCache()}

if __name__ == '__main__':
    divvy_dose_app.run(port=5000, debug=divvy_dose_app.app.config["DEBUG"] , use_reloader=False)
    logger = logging.getLogger('divvy_dose_app')
    logger.info( "Starting DivvyDose API ")
