# React G-code Generator

A modern web application for generating CNC G-code using Large Language Models (LLMs). This React frontend communicates with a FastAPI backend that leverages the existing Streamlit application logic.

## Features

- **Natural Language Processing**: Describe machining tasks in natural language
- **Multiple LLM Support**: Choose from various models including GPT-3.5, Zephyr-7b, CodeLlama, and fine-tuned StarCoder
- **Parameter Extraction**: Automatically extract machining parameters from task descriptions
- **G-code Generation**: Generate production-ready G-code with proper formatting
- **3D Visualization**: Visualize the toolpath and machining parameters
- **PDF Integration**: Upload machining manuals for enhanced context
- **Task Decomposition**: Break down complex tasks into manageable subtasks

## Architecture

- **Frontend**: React 18 with Tailwind CSS
- **Backend**: FastAPI with Python
- **AI/ML**: Langchain, HuggingFace Transformers, OpenAI API
- **Visualization**: Plotly.js for 3D toolpath rendering

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Required Python packages (see backend/requirements.txt)

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Task Description**: Enter a detailed description of your machining task
2. **Model Selection**: Choose the appropriate LLM model for your use case
3. **Parameter Extraction**: Extract machining parameters automatically
4. **Visualization**: View the extracted parameters and toolpath
5. **G-code Generation**: Generate the final G-code program
6. **Download**: Save the G-code file for your CNC machine

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/models` - Get available models
- `POST /api/extract-parameters` - Extract parameters from task description
- `POST /api/parse-parameters` - Parse extracted parameters for visualization
- `POST /api/generate-gcode` - Generate G-code from parameters
- `POST /api/upload-pdf` - Upload PDF files for RAG functionality

## Model Options

- **Zephyr-7b**: General-purpose model, good balance of performance and speed
- **GPT-3.5**: Best overall performance (requires OpenAI API key)
- **Fine-tuned StarCoder**: Specialized for G-code generation (requires HuggingFace access)
- **CodeLlama**: Code-specialized model from Meta
- **DeepSeek-Coder-1B**: Lightweight and efficient
- **Phi-3-Mini**: Microsoft's efficient small model

## Environment Variables

Create a `.env` file in the backend directory:

```
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

## Development

The application is built with modern web technologies:

- **React Hooks** for state management
- **Tailwind CSS** for styling
- **React Hot Toast** for notifications
- **Lucide React** for icons
- **Plotly.js** for 3D visualization

## Troubleshooting

1. **Backend not responding**: Ensure the FastAPI server is running on port 8000
2. **Model loading errors**: Check your API keys and HuggingFace tokens
3. **File upload issues**: Verify the uploads directory exists and has write permissions
4. **CORS errors**: Ensure the backend CORS settings allow requests from localhost:3000

## Contributing

This application extends the original Streamlit G-code generator with a modern React frontend. Contributions are welcome!

## License

This project is part of the GLLM (G-code Large Language Models) research initiative.
