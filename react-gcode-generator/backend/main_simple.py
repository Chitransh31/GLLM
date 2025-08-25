"""
Simplified FastAPI Backend for React G-code Generator

This backend provides REST API endpoints with mock responses initially,
allowing the React frontend to be tested while the full ML integration
is developed separately.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import time
import asyncio

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
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Mock parameter extraction based on description keywords
        parameters = []
        missing = []
        
        description_lower = request.description.lower()
        
        # Mock material detection
        if "aluminum" in description_lower or "aluminium" in description_lower:
            parameters.append("Material: Aluminum")
        elif "steel" in description_lower:
            parameters.append("Material: Steel")
        elif "brass" in description_lower:
            parameters.append("Material: Brass")
        else:
            missing.append("Material")
        
        # Mock tool detection
        if "end mill" in description_lower:
            if "6mm" in description_lower:
                parameters.append("Tool: 6mm End Mill")
            elif "8mm" in description_lower:
                parameters.append("Tool: 8mm End Mill")
            else:
                parameters.append("Tool: End Mill")
        elif "drill" in description_lower:
            parameters.append("Tool: Drill Bit")
        else:
            missing.append("Tool Type")
        
        # Mock feed rate detection
        if "feed" in description_lower or "mm/min" in description_lower:
            import re
            feed_match = re.search(r'(\d+)\s*mm/min', description_lower)
            if feed_match:
                parameters.append(f"Feed Rate: {feed_match.group(1)}mm/min")
            else:
                parameters.append("Feed Rate: 1000mm/min")
        else:
            missing.append("Feed Rate")
        
        # Mock spindle speed detection
        if "rpm" in description_lower or "spindle" in description_lower:
            import re
            rpm_match = re.search(r'(\d+)\s*rpm', description_lower)
            if rpm_match:
                parameters.append(f"Spindle Speed: {rpm_match.group(1)}RPM")
            else:
                parameters.append("Spindle Speed: 8000RPM")
        else:
            missing.append("Spindle Speed")
        
        # Mock dimensions detection
        if "x" in description_lower and "mm" in description_lower:
            import re
            dim_match = re.search(r'(\d+)\s*mm\s*x\s*(\d+)\s*mm', description_lower)
            if dim_match:
                parameters.append(f"Dimensions: {dim_match.group(1)}mm x {dim_match.group(2)}mm")
        
        # Mock depth detection
        if "deep" in description_lower or "depth" in description_lower:
            import re
            depth_match = re.search(r'(\d+(?:\.\d+)?)\s*mm\s+deep', description_lower)
            if depth_match:
                parameters.append(f"Depth: {depth_match.group(1)}mm")
        
        extracted_text = "\n".join(parameters) if parameters else "No parameters extracted"
        
        return ParameterExtractionResponse(
            extractedParameters=extracted_text,
            missingParameters=missing
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract parameters: {str(e)}")

@app.post("/api/parse-parameters", response_model=ParameterParsingResponse)
async def parse_parameters(request: ParameterParsingRequest):
    """
    Parse extracted parameters for visualization
    """
    try:
        parsed = {}
        
        lines = request.extractedParameters.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert numerical values
                if 'mm/min' in value:
                    parsed[key] = int(value.replace('mm/min', ''))
                elif 'RPM' in value:
                    parsed[key] = int(value.replace('RPM', ''))
                elif 'mm' in value and 'x' in value:
                    # Handle dimensions like "50mm x 30mm"
                    dims = value.replace('mm', '').split('x')
                    if len(dims) == 2:
                        parsed[key] = [float(d.strip()) for d in dims]
                elif 'mm' in value:
                    try:
                        parsed[key] = float(value.replace('mm', ''))
                    except:
                        parsed[key] = value
                else:
                    parsed[key] = value
        
        return ParameterParsingResponse(parsedParameters=parsed)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse parameters: {str(e)}")

@app.post("/api/generate-gcode", response_model=GCodeGenerationResponse)
async def generate_gcode(request: GCodeGenerationRequest):
    """
    Generate G-code based on task description and parameters
    """
    try:
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Mock G-code generation
        gcode_lines = [
            "; G-code generated by GLLM",
            f"; Model: {request.model}",
            f"; Prompt Type: {request.promptType}",
            "",
            "G21 ; Set units to mm",
            "G90 ; Absolute positioning", 
            "G17 ; XY plane selection",
            "M3 S8000 ; Start spindle at 8000 RPM",
            "",
            "G0 X0 Y0 Z5 ; Rapid to start position",
            "G1 Z-0.5 F300 ; Plunge to depth",
        ]
        
        # Add machining moves based on description
        description_lower = request.description.lower()
        if "pocket" in description_lower:
            gcode_lines.extend([
                "G1 X50 F1000 ; Mill to X50",
                "G1 Y30 ; Mill to Y30", 
                "G1 X0 ; Mill back to X0",
                "G1 Y0 ; Mill back to start",
                "G1 Z-1.0 ; Next depth pass",
                "G1 X50 ; Mill to X50",
                "G1 Y30 ; Mill to Y30",
                "G1 X0 ; Mill back to X0", 
                "G1 Y0 ; Mill back to start"
            ])
        elif "drill" in description_lower:
            gcode_lines.extend([
                "G83 X10 Y10 Z-10 Q2 R5 ; Peck drilling",
                "G83 X20 Y20 Z-10 Q2 R5 ; Peck drilling",
                "G83 X30 Y30 Z-10 Q2 R5 ; Peck drilling"
            ])
        else:
            gcode_lines.extend([
                "G1 X50 F1000 ; Linear move",
                "G1 Y50 ; Linear move",
                "G1 X0 ; Return to start",
                "G1 Y0 ; Return to start"
            ])
        
        gcode_lines.extend([
            "",
            "G0 Z5 ; Retract",
            "M5 ; Stop spindle",
            "M30 ; End program"
        ])
        
        gcode = "\n".join(gcode_lines)
        
        return GCodeGenerationResponse(gcode=gcode)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate G-code: {str(e)}")

@app.post("/api/upload-pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Handle PDF file uploads for RAG functionality
    """
    try:
        uploaded_files = []
        
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
            # Mock file storage
            file_id = str(uuid.uuid4())
            uploaded_files.append(f"uploads/{file_id}_{file.filename}")
        
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
