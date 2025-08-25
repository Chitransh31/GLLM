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
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, pipeline, AutoTokenizer
from langchain_openai import ChatOpenAI
from utils.prompts_utils import SYSTEM_MESSAGE
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFaceEndpoint, HuggingFacePipeline
from langchain_community.chat_models.huggingface import ChatHuggingFace
from huggingface_hub import login


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


def setup_model(model:str):
    if model == "Zephyr-7b":
        ENDPOINT_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)
        
    elif model == "Fine-tuned StarCoder":
        try:
            # First try to access the gated repository
            config = PeftConfig.from_pretrained("ArneKreuz/starcoderbase-finetuned-thestack", token=hf_token)
            base_model = AutoModelForCausalLM.from_pretrained("bigcode/starcoderbase-3b", token=hf_token)
            # Load the fine tuned model
            llm = PeftModel.from_pretrained(base_model, "ArneKreuz/starcoderbase-finetuned-thestack", token=hf_token, force_download=True)
        except Exception as e:
            print(f"Error loading Fine-tuned StarCoder: {e}")
            print("This might be due to:")
            print("1. Missing Hugging Face token")
            print("2. No access to gated repository 'bigcode/starcoderbase-3b'")
            print("3. Visit https://huggingface.co/bigcode/starcoderbase-3b to request access")
            print("Falling back to publicly available StarCoder alternative...")
            
            # Try alternative open-source code models
            try:
                print("Trying WizardCoder-1B as alternative...")
                ENDPOINT_URL = "https://api-inference.huggingface.co/models/WizardLM/WizardCoder-1B-V1.0"
                llm = HuggingFaceEndpoint(
                    endpoint_url=ENDPOINT_URL,
                    task="text-generation",
                    max_new_tokens=512,
                    top_k=50,
                    temperature=0.1,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=hf_token)
            except Exception as e2:
                print(f"WizardCoder also failed: {e2}")
                print("Final fallback to Zephyr-7b model...")
                # Final fallback to a publicly available model
                ENDPOINT_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
                llm = HuggingFaceEndpoint(
                    endpoint_url=ENDPOINT_URL,
                    task="text-generation",
                    max_new_tokens=512,
                    top_k=50,
                    temperature=0.1,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=hf_token)

    elif model == "GPT-3.5":
        #llm = OpenAI(api_key=openai.api_key)
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, api_key=openai.api_key)

    elif model == 'CodeLlama':
        try:
            print("Loading CodeLlama via Hugging Face Inference API (recommended for memory efficiency)...")
            # Use Hugging Face Inference API instead of loading locally to avoid memory issues
            ENDPOINT_URL = "https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-hf"
            llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)
            print("Successfully loaded CodeLlama via API")
        except Exception as e:
            print(f"Error loading CodeLlama via API: {e}")
            print("Trying local CodeLlama with memory optimizations...")
            
            try:
                # Try loading locally with memory optimizations
                model_name = "codellama/CodeLlama-7b-hf"
                print("Loading with memory optimizations...")
                
                # Load with memory optimizations (without 8-bit for Mac compatibility)
                base_model = AutoModelForCausalLM.from_pretrained(
                    model_name, 
                    token=hf_token,
                    device_map="auto",  # Automatically distribute across available devices
                    low_cpu_mem_usage=True,  # Reduce CPU memory usage
                    torch_dtype="auto"  # Let torch choose the best dtype
                )
                
                tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
                
                # Create pipeline with memory-efficient settings
                llm = pipeline(
                    "text-generation",
                    model=base_model,
                    tokenizer=tokenizer,
                    max_new_tokens=256,  # Reduced from 512
                    do_sample=True,
                    temperature=0.1,
                    pad_token_id=tokenizer.eos_token_id
                )
                print("Successfully loaded CodeLlama locally with optimizations")
                
            except Exception as e2:
                print(f"Error loading CodeLlama locally: {e2}")
                print("This is likely due to insufficient memory (CodeLlama-7B requires ~13GB RAM)")
                print("Falling back to lighter alternative: WizardCoder-1B...")
                
                # Fallback to a smaller code model
                try:
                    ENDPOINT_URL = "https://api-inference.huggingface.co/models/WizardLM/WizardCoder-1B-V1.0"
                    llm = HuggingFaceEndpoint(
                        endpoint_url=ENDPOINT_URL,
                        task="text-generation",
                        max_new_tokens=512,
                        top_k=50,
                        temperature=0.1,
                        repetition_penalty=1.03,
                        huggingfacehub_api_token=hf_token)
                    print("Loaded WizardCoder-1B as fallback")
                except Exception as e3:
                    print(f"WizardCoder also failed: {e3}")
                    print("Final fallback to Zephyr-7b model...")
                    # Final fallback
                    ENDPOINT_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
                    llm = HuggingFaceEndpoint(
                        endpoint_url=ENDPOINT_URL,
                        task="text-generation",
                        max_new_tokens=512,
                        top_k=50,
                        temperature=0.1,
                        repetition_penalty=1.03,
                        huggingfacehub_api_token=hf_token)
        ## llm = pipeline("text-generation", model="codellama/CodeLlama-7b-hf")
        
    elif model == "DeepSeek-Coder-1B":
        try:
            print("Loading DeepSeek-Coder-1B (lightweight code model)...")
            ENDPOINT_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-1.3b-base"
            llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)
        except Exception as e:
            print(f"Error loading DeepSeek-Coder: {e}")
            print("Falling back to Zephyr-7b...")
            ENDPOINT_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
            llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)
    
    elif model == "Phi-3-Mini":
        try:
            print("Loading Phi-3-Mini (Microsoft's efficient code model)...")
            ENDPOINT_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
            llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)
        except Exception as e:
            print(f"Error loading Phi-3-Mini: {e}")
            print("Falling back to Zephyr-7b...")
            ENDPOINT_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
            llm = HuggingFaceEndpoint(
                endpoint_url=ENDPOINT_URL,
                task="text-generation",
                max_new_tokens=512,
                top_k=50,
                temperature=0.1,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token)


    return llm

def setup_langchain_without_rag(model):
    # create a prompt
    prompt = ChatPromptTemplate.from_messages(
            [
                (
                 "system", SYSTEM_MESSAGE),
                ("human", "{input}"),
            ])
    model_chain =  prompt | model
    
    # Here we assume the model name is compatible with Hugging Face's interfac
    #model_chain = ChatHuggingFace(llm=model) 

    return model_chain