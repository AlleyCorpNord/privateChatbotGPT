import os
import argparse
import streamlit as st
import torch

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import GPT4All, LlamaCpp, CTransformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

load_dotenv()


embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')

model_type = os.environ.get('MODEL_TYPE')
model_path = os.environ.get('MODEL_PATH')
model_n_ctx = os.environ.get('MODEL_N_CTX')
model_n_predict = int(os.environ.get('MODEL_N_PREDICT', 256))
model_temperature = float(os.environ.get('MODEL_TEMPERATURE', 0.8))
model_top_p = float(os.environ.get('MODEL_TOP_P', 0.95))
model_n_batch = int(os.environ.get('MODEL_N_BATCH',8))
model_n_gpu_layers = os.environ.get('MODEL_N_GPU_LAYERS', None)
model_n_gpu_layers = None if model_n_gpu_layers is None else int(model_n_gpu_layers)
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS',4))
ctransformers_model_type = os.environ.get('CTRANSFORMERS_MODEL_TYPE')

from constants import CHROMA_SETTINGS

@st.cache_resource
def create_qa():
    # Parse the command line arguments
    args = parse_arguments()
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    # activate/deactivate the streaming StdOut callback for LLMs
    callbacks = [] if args.mute_stream else [StreamingStdOutCallbackHandler()]
    # Prepare the LLM
    match model_type:
        case "LlamaCpp":
             llm = LlamaCpp(temperature=model_temperature, top_p=model_top_p, model_path=model_path, n_ctx=model_n_ctx, n_batch=model_n_batch, n_gpu_layers=model_n_gpu_layers, callbacks=callbacks, verbose=False)
        case "GPT4All":
            llm = GPT4All(temp=model_temperature, top_p=model_top_p, model=model_path, n_ctx=model_n_ctx, backend='gptj', n_batch=model_n_batch, n_predict=model_n_predict, callbacks=callbacks, verbose=False)
        case "CTransformers":
            print("CTransformers")
            ctransformers_config = {'max_new_tokens': 2000, 'batch_size': model_n_batch, 'context_length': int(model_n_ctx)}
            llm = CTransformers(model=model_path, model_type=ctransformers_model_type, config=ctransformers_config)
        case _default:
            # raise exception if model_type is not supported
            raise Exception(f"Model type {model_type} is not supported. Please choose one of the following: LlamaCpp, GPT4All")
        
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents= not args.hide_source)
    return qa

def parse_arguments():
    parser = argparse.ArgumentParser(description='privateGPT: Ask questions to your documents without an internet connection, '
                                                 'using the power of LLMs.')
    parser.add_argument("--hide-source", "-S", action='store_true',
                        help='Use this flag to disable printing of source documents used for answers.')

    parser.add_argument("--mute-stream", "-M",
                        action='store_true',
                        help='Use this flag to disable the streaming StdOut callback for LLMs.')

    return parser.parse_args()


def get_torch_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def translate(text, model_name):
    device = get_torch_device()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True).to(device))
    tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    return tgt_text[0]
