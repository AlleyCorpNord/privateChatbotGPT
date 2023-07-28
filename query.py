# import logging
# import sys
# import os

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index import ListIndex, NotionPageReader

# integration_token = 'secret_XR6G0igcYzg4aaR0GNs9zTeHhdJsVU2WKJkiNAYgBs2'
# print("integration_token", integration_token)
# page_ids = ["79d4f07bdace41bba2b84002b1a847ba"]

# documents = NotionPageReader(integration_token=integration_token).load_data(
#     page_ids=page_ids
# )

# index = ListIndex.from_documents(documents)
# print("index is", index)

# # set Logging to DEBUG for more detailed outputs
# query_engine = index.as_query_engine()
# response = query_engine.query("when is payroll?")
# print("response is", response)


from llama_index import ListIndex, NotionPageReader

import os


integration_token = "secret_XR6G0igcYzg4aaR0GNs9zTeHhdJsVU2WKJkiNAYgBs2"
page_ids = ["79d4f07bdace41bba2b84002b1a847ba"]
reader = NotionPageReader(integration_token=integration_token)
documents = reader.load_data(
    page_ids=page_ids
)
index = ListIndex.from_documents(documents)

query_engine = index.as_query_engine()
print("query_engine is", query_engine)
