#!/usr/bin/env python3

import logging
import os
import sys
from dotenv import load_dotenv

from langchain.llms import CTransformers
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index import (
    download_loader,
    LangchainEmbedding,
    ListIndex,
    NotionPageReader,
    ServiceContext,
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

model_type = os.environ.get('MODEL_TYPE')
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
model_path = os.environ.get("MODEL_PATH")
model_n_ctx = os.environ.get("MODEL_N_CTX")
model_n_batch = int(os.environ.get("MODEL_N_BATCH", 8))
target_source_chunks = int(os.environ.get("TARGET_SOURCE_CHUNKS", 4))
ctransformers_model_type = os.environ.get('CTRANSFORMERS_MODEL_TYPE')

# get documents
NotionPageReader = download_loader("NotionPageReader")
integration_token = os.getenv("NOTION_INTEGRATION_TOKEN")
reader = NotionPageReader(integration_token=integration_token)
page_ids = [  # testing only one page for now
    "79d4f07bdace41bba2b84002b1a847ba"  # https://www.notion.so/alleycorpnord/How-we-work-79d4f07bdace41bba2b84002b1a847ba
]
documents = reader.load_data(page_ids=page_ids)

# activate/deactivate the streaming StdOut callback for LLMs
callbacks = [StreamingStdOutCallbackHandler()]

# define LLM
match model_type:
    case "LlamaCpp":
         llm = LlamaCpp(temperature=model_temperature, top_p=model_top_p, model_path=model_path, n_ctx=model_n_ctx, n_batch=model_n_batch, n_gpu_layers=model_n_gpu_layers, callbacks=callbacks, verbose=False)
    case "GPT4All":
        llm = GPT4All(temp=model_temperature, top_p=model_top_p, model=model_path, n_ctx=model_n_ctx, backend='gptj', n_batch=model_n_batch, n_predict=model_n_predict, callbacks=callbacks, verbose=False)
    case "CTransformers":
        ctransformers_config = {'max_new_tokens': 2000, 'batch_size': model_n_batch, 'context_length': int(model_n_ctx)}
        llm = CTransformers(model=model_path, model_type=ctransformers_model_type, config=ctransformers_config)
    case _default:
        # raise exception if model_type is not supported
        raise Exception(f"Model type {model_type} is not supported. Please choose one of the following: LlamaCpp, GPT4All")

embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name=embeddings_model_name)
)
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

# build index
index = ListIndex.from_documents(documents, service_context=service_context)

# get response from query
# query = "When is payroll?"
# query_engine = index.as_query_engine()
# print("QUERY ENGINE IS!!!", query_engine)
# response = query_engine.query(query)
# print(f"RESPONSE: {response}")