# Model Loading Issues - Solutions and Fixes

## Issues Fixed

### 1. OSError: Gated Repository Access (StarCoder)
**Problem**: `bigcode/starcoderbase-3b` requires special permissions and access request.

**Solutions Applied**:
- ✅ Enhanced error handling with detailed error messages
- ✅ Added fallback to `WizardCoder-1B` as alternative
- ✅ Added multiple fallback layers to ensure robustness
- ✅ Uses HuggingFace Inference API instead of local loading

### 2. Memory Issues with CodeLlama (OOM/Killed)
**Problem**: CodeLlama-7B requires ~13GB RAM, causing system to kill the process.

**Solutions Applied**:
- ✅ **Primary**: Use HuggingFace Inference API (recommended)
- ✅ **Fallback 1**: Local loading with 8-bit quantization (`load_in_8bit=True`)
- ✅ **Fallback 2**: Automatic device mapping (`device_map="auto"`)
- ✅ **Fallback 3**: Lighter alternatives (WizardCoder-1B, DeepSeek-Coder)
- ✅ **Final Fallback**: Zephyr-7B as reliable backup

## New Models Added

### DeepSeek-Coder-1B
- **Purpose**: Lightweight code generation model
- **Memory**: ~2GB RAM required
- **Access**: Public, no special permissions needed
- **Performance**: Good for code tasks, much faster than CodeLlama

### Phi-3-Mini
- **Purpose**: Microsoft's efficient small model
- **Memory**: ~4GB RAM required  
- **Access**: Public, no special permissions needed
- **Performance**: Excellent instruction following, good for structured tasks

## Model Recommendations by Use Case

### 🔧 **Code Generation Tasks**
1. **CodeLlama** (via API) - Best performance for code
2. **DeepSeek-Coder-1B** - Good balance of speed and quality
3. **Fine-tuned StarCoder** - If you have access to gated repo

### 🖥️ **Low Memory Systems (< 8GB RAM)**
1. **Zephyr-7b** (via API) - General purpose, reliable
2. **DeepSeek-Coder-1B** (via API) - For code tasks
3. **GPT-3.5** - If you have OpenAI API key

### 📊 **General Tasks**
1. **GPT-3.5** - Best overall performance (requires API key)
2. **Zephyr-7b** - Good open-source alternative
3. **Phi-3-Mini** - Good for structured tasks

### 🏠 **Local Development (High Memory Systems)**
1. **CodeLlama** with 8-bit quantization
2. **Phi-3-Mini** locally
3. **DeepSeek-Coder-1B** locally

## Updated Model Selection

The application now includes these models in the dropdown:
```
- Zephyr-7b ✅
- GPT-3.5 ✅ (requires OpenAI API key)
- Fine-tuned StarCoder ✅ (requires HF access)
- CodeLlama ✅ (now with API fallback)
- DeepSeek-Coder-1B ✅ (new)
- Phi-3-Mini ✅ (new)
```

## Implementation Details

### Robust Fallback Chain
Each model now has a multi-level fallback system:

1. **Primary**: Try the requested model
2. **Fallback 1**: Try alternative implementation (API vs local)
3. **Fallback 2**: Try similar model with different approach
4. **Fallback 3**: Try lighter alternative
5. **Final**: Fall back to reliable Zephyr-7b

### Memory Optimization
For local models:
- `load_in_8bit=True` - Reduces memory by ~50%
- `device_map="auto"` - Distributes across available devices
- `low_cpu_mem_usage=True` - Reduces CPU memory usage
- Reduced `max_new_tokens` for efficiency

### Error Handling
- Clear error messages explaining the issue
- Suggestions for fixing access problems
- Automatic fallbacks with user notification
- Graceful degradation to working alternatives

## Quick Start Guide

### For MacBook Pro with 16GB RAM (like yours):
1. **Recommended**: Use **CodeLlama** (will use API automatically)
2. **Alternative**: Use **DeepSeek-Coder-1B** for faster responses
3. **Backup**: Use **Zephyr-7b** for general tasks

### Immediate Actions:
1. ✅ Updated model loading with robust fallbacks
2. ✅ Added new lightweight models
3. ✅ Enhanced error messages and guidance
4. ✅ Cleared Python cache to ensure fixes load
5. ✅ Updated UI to include new model options

## Testing

Run the application and test different models:
```bash
poetry run streamlit run gllm/code_generator_streamlit_reasoning_langchain_langgraph.py
```

The system will now:
- Handle gated repository issues gracefully
- Avoid memory issues with smart fallbacks
- Provide clear feedback on what's happening
- Always have a working model available

## Troubleshooting

### If models still fail:
1. Check your HuggingFace token in `.streamlit/secrets.toml`
2. Try the API-based models first (CodeLlama, DeepSeek-Coder)
3. Monitor memory usage during model loading
4. Use lighter models for development/testing

### For production use:
- Use GPT-3.5 with OpenAI API key for best results
- Use CodeLlama via HuggingFace API for code generation
- Keep Zephyr-7b as reliable fallback
