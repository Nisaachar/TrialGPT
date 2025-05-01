from retrieval_module import hybridRetriever
from matching import matching_module
from ranking_updated import ranking_module

import time 


start_time = time.time()


hybridRetriever()
matching_module()
ranking_module()


elapsed_time = time.time() - start_time

print(f"Total time elapsed: {elapsed_time:.2f} seconds.")

