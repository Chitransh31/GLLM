"""
Description of this file:

This file contains utility functions for setting up and managing machine learning models in a Langchain application.
The models are used to generate G-codes from natural language instructions for CNC machines.
Various models including Zephyr-7b, Fine-tuned StarCoder, GPT-3.5, and CodeLlama are supported, with configurations tailored for text generation tasks.

The utilities are implemented in Python and utilize libraries such as Transformers, Langchain, and Hugging Face APIs
to ensure seamless integration and execution within the application.

Authors: Mohamed Abdelaal, Samuel Lokadjaja

This work was done at Software AG, Darmstadt, Germany in 2023-2024 and is published under the Apache License 2.0.
"""

import os
import toml
import openai
from langchain_openai import ChatOpenAI
from utils.prompts_utils import SYSTEM_MESSAGE
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from huggingface_hub import login, InferenceClient


# Define the path to the secrets.toml file
secrets_file_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '.streamlit', 'secrets.toml'))
# Load the secrets
secrets = toml.load(secrets_file_path)
# Set your OpenAI API key
openai.api_key = secrets["openai_token"]
# Get Hugging Face token
hf_token = secrets.get("huggingface_token")

# Login to Hugging Face if token is available
if hf_token:
    try:
        login(hf_token, add_to_git_credential=True)
        print("Successfully logged in to Hugging Face")
    except Exception as e:
        print(f"Warning: Could not login to Hugging Face: {e}")
else:
    print("Warning: No Hugging Face token found in secrets")


# HuggingFace model IDs for the serverless inference API
# NOTE: Models must be available on HF's Inference API (huggingface_hub v0.33+).
# Old models (CodeLlama-7b, DeepSeek-Coder-1.3b, StarCoder2-3b, Phi-3-Mini)
# are no longer routed by the provider system and have been replaced.
HF_MODELS = {
    "Zephyr-7b": "HuggingFaceH4/zephyr-7b-beta",
    "Qwen2.5-Coder-7B": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen2.5-Coder-1.5B": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "Llama-3.1-8B": "meta-llama/Llama-3.1-8B-Instruct",
    "Llama-3.2-1B": "meta-llama/Llama-3.2-1B-Instruct",
}

# Fallback order if a model fails
HF_FALLBACKS = ["HuggingFaceH4/zephyr-7b-beta", "Qwen/Qwen2.5-Coder-7B-Instruct"]


def _create_hf_chat_model(model_id: str) -> ChatHuggingFace:
    """Create a ChatHuggingFace model using the HF serverless inference API."""
    llm = HuggingFaceEndpoint(
        repo_id=model_id,
        task="text-generation",
        max_new_tokens=512,
        temperature=0.1,
        repetition_penalty=1.03,
        huggingfacehub_api_token=hf_token,
    )
    return ChatHuggingFace(llm=llm, huggingfacehub_api_token=hf_token)


def _create_hf_model_with_fallback(model_id: str):
    """Try to create an HF model, falling back through alternatives on failure."""
    candidates = [model_id] + [fb for fb in HF_FALLBACKS if fb != model_id]
    last_error = None
    for candidate in candidates:
        try:
            model = _create_hf_chat_model(candidate)
            if candidate != model_id:
                print(f"Using fallback model: {candidate}")
            return model
        except Exception as e:
            print(f"Failed to load {candidate}: {e}")
            last_error = e
    raise last_error


def setup_model(model: str):
    if model == "GPT-3.5":
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, api_key=openai.api_key)
    elif model in HF_MODELS:
        llm = _create_hf_model_with_fallback(HF_MODELS[model])
    else:
        # Unknown model name — try GPT-3.5 as default
        print(f"Unknown model '{model}', defaulting to GPT-3.5")
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, api_key=openai.api_key)

    return llm


def setup_langchain_without_rag(model):
    # All models now support chat format (ChatHuggingFace or ChatOpenAI)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_MESSAGE),
            ("human", "{input}"),
        ])
    model_chain = prompt | model

    return model_chain
