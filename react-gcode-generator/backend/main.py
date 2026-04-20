"""
FastAPI Backend for React G-code Generator

This backend provides REST API endpoints to interface with the existing 
Streamlit application logic, allowing the React frontend to use the same 
LLM pipelines for G-code generation.

Authors: Enhanced from original Streamlit application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import uuid
import asyncio
from pathlib import Path

# Add the parent directory to the path to import the existing modules
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, _project_root)
# Also add gllm/ so internal 'from utils.' imports resolve (used by model_utils etc.)
sys.path.insert(0, os.path.join(_project_root, 'gllm'))

from gllm.utils.rag_utils import setup_langchain_with_rag
from gllm.utils.model_utils import setup_model, setup_langchain_without_rag
from gllm.utils.params_extraction_utils import extract_parameters_logic, parse_extracted_parameters, extract_numerical_values
from gllm.utils.gcode_utils import generate_gcode_unstructured_prompt, generate_task_descriptions
from gllm.utils.plot_utils import refine_gcode
from gllm.utils.graph_utils import construct_graph
from gllm.utils.params_extraction_utils import from_dict_to_text
from gllm.utils.llm_router import LLMRouter, QueryType
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

app = FastAPI(title="G-code Generator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ParameterExtractionRequest(BaseModel):
    description: str
    model: str
    decomposeTask: str = "Yes"
    pdfFiles: Optional[List[str]] = []

class ParameterExtractionResponse(BaseModel):
    extractedParameters: str
    missingParameters: List[str]

class ParameterParsingRequest(BaseModel):
    extractedParameters: str

class ParameterParsingResponse(BaseModel):
    parsedParameters: Dict[str, Any]

class GCodeGenerationRequest(BaseModel):
    description: str
    model: str
    promptType: str = "Structured"
    extractedParameters: Optional[str] = None
    pdfFiles: Optional[List[str]] = []

class GCodeGenerationResponse(BaseModel):
    gcode: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "Auto"

class ChatResponse(BaseModel):
    message: str
    model_used: str
    query_type: Optional[str] = None

# Global state to store models and chains (in production, use a proper cache/session store)
model_cache = {}
chain_cache = {}

# Chat system prompt for the TEC Lab assistant
CHAT_SYSTEM_PROMPT = (
    "You are a helpful assistant for the TEC (Technology and Equipment Center) Lab. "
    "You help users with questions about machines, manufacturing processes, NC code, "
    "tools, and lab operations. Be concise and helpful. "
    "Answer in the same language the user writes in."
)

# Shared LLM router instance for chat auto-routing
chat_router = LLMRouter()

# Maps LLMRouter model keys (from MODEL_REGISTRY) to setup_model() names
# (from model_utils.py HF_MODELS). Router keys reference older/unavailable models,
# so we map them to the closest available equivalents.
ROUTER_KEY_TO_MODEL_NAME = {
    "gpt-3.5": "GPT-3.5",
    "zephyr-7b": "Zephyr-7b",
    "fine-tuned-starcoder": "Qwen2.5-Coder-7B",
    "codellama-7b": "Qwen2.5-Coder-7B",
    "phi-3-mini": "Qwen2.5-Coder-1.5B",
    "deepseek-coder-1b": "Qwen2.5-Coder-1.5B",
    "wizardcoder-1b": "Llama-3.2-1B",
}

@app.get("/")
async def root():
    return {"message": "G-code Generator API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/extract-parameters", response_model=ParameterExtractionResponse)
async def extract_parameters(request: ParameterExtractionRequest):
    """
    Extract parameters from task description using the selected model
    """
    try:
        # Setup model if not cached
        model_key = f"model_{request.model}"
        if model_key not in model_cache:
            try:
                model_cache[model_key] = setup_model(model=request.model)
            except Exception as model_err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load model '{request.model}': {str(model_err)}"
                )

        model = model_cache[model_key]

        # Setup langchain chain
        chain_key = f"chain_{request.model}_{len(request.pdfFiles)}"
        if chain_key not in chain_cache:
            if request.pdfFiles:
                chain_cache[chain_key] = setup_langchain_without_rag(model=model)
            else:
                chain_cache[chain_key] = setup_langchain_without_rag(model=model)

        chain = chain_cache[chain_key]

        # Extract parameters using existing logic
        try:
            extracted_parameters, missing_parameters = extract_parameters_logic(chain, request.description)
        except Exception as inference_err:
            # Clear cached model/chain in case it's in a bad state
            model_cache.pop(model_key, None)
            chain_cache.pop(chain_key, None)
            raise HTTPException(
                status_code=500,
                detail=f"Model '{request.model}' failed during inference: {str(inference_err)}"
            )

        # Convert to text format
        extracted_parameters_text = from_dict_to_text(extracted_parameters)

        # Handle task decomposition if requested
        if request.decomposeTask == "Yes":
            values_in_number_shapes = extract_numerical_values(extracted_parameters, 'Number of Shapes')
            number_shapes = values_in_number_shapes[0] if isinstance(values_in_number_shapes, list) else values_in_number_shapes

            if number_shapes and number_shapes > 1:
                task_descriptions = generate_task_descriptions(model, request.model, request.description)
                extracted_parameters_text += f"\nSubtasks: {task_descriptions}\n"

        return ParameterExtractionResponse(
            extractedParameters=extracted_parameters_text,
            missingParameters=missing_parameters or []
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract parameters: {str(e)}")

@app.post("/api/parse-parameters", response_model=ParameterParsingResponse)
async def parse_parameters(request: ParameterParsingRequest):
    """
    Parse extracted parameters for visualization
    """
    try:
        parsed_parameters = parse_extracted_parameters(request.extractedParameters)
        
        if parsed_parameters is None:
            parsed_parameters = {}
        
        return ParameterParsingResponse(parsedParameters=parsed_parameters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse parameters: {str(e)}")

@app.post("/api/generate-gcode", response_model=GCodeGenerationResponse)
async def generate_gcode(request: GCodeGenerationRequest):
    """
    Generate G-code based on task description and parameters
    """
    try:
        # Setup model if not cached
        model_key = f"model_{request.model}"
        if model_key not in model_cache:
            model_cache[model_key] = setup_model(model=request.model)
        
        model = model_cache[model_key]
        
        # Setup langchain chain
        chain_key = f"chain_{request.model}_{len(request.pdfFiles or [])}"
        if chain_key not in chain_cache:
            chain_cache[chain_key] = setup_langchain_without_rag(model=model)
        
        chain = chain_cache[chain_key]
        
        generated_gcode = ""
        
        if request.promptType == "Unstructured":
            # Direct text-to-G-code generation
            generated_gcode = generate_gcode_unstructured_prompt(chain, request.description)
        else:
            # Structured approach with parameter extraction
            if request.extractedParameters:
                # Use existing extracted parameters
                extracted_parameters = request.extractedParameters
                
                # Parse the extracted parameters
                parsed_parameters = parse_extracted_parameters(extracted_parameters)
                
                if parsed_parameters:
                    # Generate G-code using the graph-based approach
                    thread_id = str(uuid.uuid4())
                    config = {
                        "configurable": {
                            "thread_id": thread_id,
                        },
                        "recursion_limit": 1000
                    }
                    
                    with SqliteSaver.from_conn_string(":memory:") as memory:
                        # Create a mock user_inputs dict from extracted parameters
                        user_inputs = {}
                        for line in extracted_parameters.split('\n'):
                            if ': ' in line:
                                key, value = line.split(': ', 1)
                                user_inputs[key.strip()] = value.strip()
                        
                        # Construct the graph
                        graph_builder = construct_graph(
                            chain,
                            user_inputs,
                            extracted_parameters
                        )
                        
                        # Compile the graph with the checkpointer
                        graph = graph_builder.compile(checkpointer=memory)
                        
                        # Stream events from the compiled graph
                        events = graph.stream(
                            {"messages": [("user", request.description)], "iterations": 0},
                            config,
                            stream_mode="values"
                        )

                        try:
                            for event in events:
                                if "generation" in event:
                                    generated_gcode += f"\n{event['generation']}"
                                    generated_gcode = refine_gcode(generated_gcode)
                        except (StopIteration, RuntimeError) as stream_err:
                            print(f"Graph streaming error: {stream_err}")
                            if not generated_gcode.strip():
                                generated_gcode = generate_gcode_unstructured_prompt(chain, request.description)
                else:
                    # Fallback to unstructured approach
                    generated_gcode = generate_gcode_unstructured_prompt(chain, request.description)
            else:
                # No extracted parameters, use unstructured approach
                generated_gcode = generate_gcode_unstructured_prompt(chain, request.description)
        
        # Clean up the generated G-code
        generated_gcode = refine_gcode(generated_gcode)
        
        return GCodeGenerationResponse(gcode=generated_gcode)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate G-code: {str(e)}")

@app.post("/api/upload-pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Handle PDF file uploads for RAG functionality
    """
    try:
        uploaded_files = []
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
            file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append(str(file_path))
        
        return {"files": uploaded_files, "message": f"Uploaded {len(uploaded_files)} files successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")

@app.get("/api/models")
async def get_available_models():
    """
    Get list of available models
    """
    models = [
        {
            "value": "Zephyr-7b",
            "label": "Zephyr-7b",
            "description": "Reliable general-purpose model",
            "type": "open"
        },
        {
            "value": "GPT-3.5",
            "label": "GPT-3.5",
            "description": "Best overall performance (requires API key)",
            "type": "api"
        },
        {
            "value": "Qwen2.5-Coder-7B",
            "label": "Qwen2.5-Coder-7B",
            "description": "Specialized code model (7B parameters)",
            "type": "open"
        },
        {
            "value": "Qwen2.5-Coder-1.5B",
            "label": "Qwen2.5-Coder-1.5B",
            "description": "Lightweight code model (1.5B parameters)",
            "type": "open"
        },
        {
            "value": "Llama-3.1-8B",
            "label": "Llama-3.1-8B",
            "description": "Meta's general-purpose model (8B parameters)",
            "type": "open"
        },
        {
            "value": "Llama-3.2-1B",
            "label": "Llama-3.2-1B",
            "description": "Ultra-lightweight model (1B parameters)",
            "type": "open"
        }
    ]
    
    return {"models": models}

def _format_history_as_text(messages: List[ChatMessage], max_turns: int = 10) -> str:
    """Format conversation history as a single text string for HuggingFace models."""
    recent = messages[-max_turns:]
    parts = []
    for msg in recent:
        prefix = "User" if msg.role == "user" else "Assistant"
        parts.append(f"{prefix}: {msg.content}")
    return "\n".join(parts)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with automatic model routing.
    Classifies the query and routes to the best-suited model.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array is required.")

    latest_message = request.messages[-1].content
    model_name = request.model
    query_type_str = None

    try:
        # Determine which model to use
        if model_name == "Auto":
            query_type = chat_router.classify_query(latest_message)
            query_type_str = query_type.value
            model_key_name = chat_router.get_best_model_for_task(query_type)
            model_name = ROUTER_KEY_TO_MODEL_NAME.get(model_key_name, "GPT-3.5")
            print(f"Auto-routed: query_type={query_type_str}, model={model_name}")
        else:
            print(f"Manual model selection: {model_name}")

        # Load the model
        cache_key = f"model_{model_name}"
        if cache_key not in model_cache:
            try:
                model_cache[cache_key] = setup_model(model=model_name)
            except Exception as model_err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load model '{model_name}': {str(model_err)}"
                )

        llm = model_cache[cache_key]

        # Build the prompt and invoke
        is_openai = isinstance(llm, ChatOpenAI)

        if is_openai:
            # ChatOpenAI supports native message objects
            langchain_messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]
            for msg in request.messages:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    langchain_messages.append(AIMessage(content=msg.content))
            response = llm.invoke(langchain_messages)
            response_text = response.content
        else:
            # HuggingFace models: use a chat prompt template with serialized history
            history_text = _format_history_as_text(request.messages)
            prompt = ChatPromptTemplate.from_messages([
                ("system", CHAT_SYSTEM_PROMPT),
                ("human", "{input}"),
            ])
            chain = prompt | llm
            response = chain.invoke({"input": history_text})
            # Extract text from response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

        return ChatResponse(
            message=response_text,
            model_used=model_name,
            query_type=query_type_str,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clear cached model in case it's in a bad state
        model_cache.pop(f"model_{model_name}", None)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
