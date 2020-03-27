from typing import List
""" In memory simple Maps used for a cache.  Example of Interface where an optimized Cache Redis e.g. would be the proper production implementation """

class GitHubCache():
    
    def __init__(self):
        self.response_map = {}

    def get_cached_repositories(self, cache_key:str):
        return self.response_map.get(cache_key, None)
    
    def set_cached_repositories(self, repositories:List, cache_key):
        self.response_map[cache_key] = repositories

class BitBucketCache():
    
    def __init__(self):
        self.response_map = {}
        
    def get_cached_repositories(self, cache_key:str):
        return self.response_map.get(cache_key, None)
    
    def set_cached_repositories(self, repositories:List, cache_key):
        self.response_map[cache_key ]=repositories