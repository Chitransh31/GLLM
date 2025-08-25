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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from gllm.utils.rag_utils import setup_langchain_with_rag
from gllm.utils.model_utils import setup_model, setup_langchain_without_rag
from gllm.utils.params_extraction_utils import extract_parameters_logic, parse_extracted_parameters, extract_numerical_values
from gllm.utils.gcode_utils import generate_gcode_unstructured_prompt, generate_task_descriptions, refine_gcode
from gllm.utils.graph_utils import construct_graph
from gllm.utils.params_extraction_utils import from_dict_to_text
from langgraph.checkpoint.sqlite import SqliteSaver

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

# Global state to store models and chains (in production, use a proper cache/session store)
model_cache = {}
chain_cache = {}

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
            model_cache[model_key] = setup_model(model=request.model)
        
        model = model_cache[model_key]
        
        # Setup langchain chain
        chain_key = f"chain_{request.model}_{len(request.pdfFiles)}"
        if chain_key not in chain_cache:
            if request.pdfFiles:
                # In a real implementation, you'd handle PDF file uploads here
                chain_cache[chain_key] = setup_langchain_without_rag(model=model)
            else:
                chain_cache[chain_key] = setup_langchain_without_rag(model=model)
        
        chain = chain_cache[chain_key]
        
        # Extract parameters using existing logic
        extracted_parameters, missing_parameters = extract_parameters_logic(chain, request.description)
        
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
                        
                        for event in events:
                            if "generation" in event:
                                generated_gcode += f"\n{event['generation']}"
                                generated_gcode = refine_gcode(generated_gcode)
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
            "value": "Fine-tuned StarCoder",
            "label": "Fine-tuned StarCoder",
            "description": "Best for G-code (requires HF access)",
            "type": "gated"
        },
        {
            "value": "CodeLlama",
            "label": "CodeLlama",
            "description": "Specialized code model",
            "type": "open"
        },
        {
            "value": "DeepSeek-Coder-1B",
            "label": "DeepSeek-Coder-1B",
            "description": "Lightweight and efficient",
            "type": "open"
        },
        {
            "value": "Phi-3-Mini",
            "label": "Phi-3-Mini",
            "description": "Microsoft's efficient model",
            "type": "open"
        }
    ]
    
    return {"models": models}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
