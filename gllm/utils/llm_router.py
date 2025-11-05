"""
LLM Router Architecture for G-code Generation

This module implements an intelligent routing system that selects the most appropriate
LLM model based on the type of query:
- G-code Generation: Specialized code models (Fine-tuned StarCoder, CodeLlama)
- Machine-specific Knowledge: RAG-enhanced models with domain knowledge
- General Purpose Queries: General LLMs (GPT-3.5, Zephyr-7b)
- Parameter Extraction: Fast, efficient models (Phi-3-Mini, DeepSeek-Coder)

The router uses a classification system to determine query intent and routes to
the optimal model for best performance and accuracy.

Authors: Enhanced architecture for GLLM project
"""

import os
import toml
from typing import Dict, Tuple, Optional, List
from enum import Enum
from dataclasses import dataclass
import openai
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFaceEndpoint
from huggingface_hub import login


# Load secrets
secrets_file_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '.streamlit', 'secrets.toml'))
secrets = toml.load(secrets_file_path)
openai.api_key = secrets["openai_token"]
hf_token = secrets.get("huggingface_token")

if hf_token:
    try:
        login(hf_token, add_to_git_credential=True)
        print("Successfully logged in to Hugging Face")
    except Exception as e:
        print(f"Warning: Could not login to Hugging Face: {e}")


class QueryType(Enum):
    """Types of queries the system can handle"""
    GCODE_GENERATION = "gcode_generation"
    PARAMETER_EXTRACTION = "parameter_extraction"
    MACHINE_KNOWLEDGE = "machine_knowledge"
    GENERAL_QUERY = "general_query"
    CODE_REFINEMENT = "code_refinement"
    VALIDATION = "validation"


class ModelCapability(Enum):
    """Model capabilities"""
    CODE_SPECIALIST = "code_specialist"  # Best for code generation
    FAST_EFFICIENT = "fast_efficient"    # Best for quick tasks
    KNOWLEDGE_RICH = "knowledge_rich"    # Best with RAG
    GENERAL_PURPOSE = "general_purpose"  # Best for general tasks
    DOMAIN_EXPERT = "domain_expert"      # Fine-tuned for G-code


@dataclass
class ModelConfig:
    """Configuration for each model"""
    name: str
    capability: ModelCapability
    description: str
    use_cases: List[QueryType]
    endpoint_url: Optional[str] = None
    model_id: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.1
    priority: int = 1  # Higher priority = preferred choice


# Model Registry - Define all available models with their capabilities
MODEL_REGISTRY = {
    "fine-tuned-starcoder": ModelConfig(
        name="Fine-tuned StarCoder",
        capability=ModelCapability.DOMAIN_EXPERT,
        description="Fine-tuned specifically for G-code generation",
        use_cases=[QueryType.GCODE_GENERATION, QueryType.CODE_REFINEMENT],
        model_id="ArneKreuz/starcoderbase-finetuned-thestack",
        priority=5
    ),
    "codellama-7b": ModelConfig(
        name="CodeLlama-7b",
        capability=ModelCapability.CODE_SPECIALIST,
        description="Meta's code generation specialist",
        use_cases=[QueryType.GCODE_GENERATION, QueryType.CODE_REFINEMENT],
        endpoint_url="https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-hf",
        priority=4
    ),
    "gpt-3.5": ModelConfig(
        name="GPT-3.5",
        capability=ModelCapability.KNOWLEDGE_RICH,
        description="OpenAI's versatile model, best overall performance",
        use_cases=[QueryType.MACHINE_KNOWLEDGE, QueryType.GENERAL_QUERY, 
                   QueryType.GCODE_GENERATION, QueryType.PARAMETER_EXTRACTION],
        model_id="gpt-3.5-turbo-0125",
        priority=4
    ),
    "zephyr-7b": ModelConfig(
        name="Zephyr-7b",
        capability=ModelCapability.GENERAL_PURPOSE,
        description="Reliable general-purpose model with good instruction following",
        use_cases=[QueryType.GENERAL_QUERY, QueryType.PARAMETER_EXTRACTION, 
                   QueryType.MACHINE_KNOWLEDGE],
        endpoint_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
        priority=3
    ),
    "phi-3-mini": ModelConfig(
        name="Phi-3-Mini",
        capability=ModelCapability.FAST_EFFICIENT,
        description="Microsoft's efficient small model for quick tasks",
        use_cases=[QueryType.PARAMETER_EXTRACTION, QueryType.VALIDATION],
        endpoint_url="https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct",
        max_tokens=256,
        priority=3
    ),
    "deepseek-coder-1b": ModelConfig(
        name="DeepSeek-Coder-1B",
        capability=ModelCapability.FAST_EFFICIENT,
        description="Lightweight code model for fast parameter extraction",
        use_cases=[QueryType.PARAMETER_EXTRACTION, QueryType.VALIDATION],
        endpoint_url="https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-1.3b-base",
        max_tokens=256,
        priority=2
    ),
    "wizardcoder-1b": ModelConfig(
        name="WizardCoder-1B",
        capability=ModelCapability.FAST_EFFICIENT,
        description="Lightweight fallback for code tasks",
        use_cases=[QueryType.PARAMETER_EXTRACTION, QueryType.CODE_REFINEMENT],
        endpoint_url="https://api-inference.huggingface.co/models/WizardLM/WizardCoder-1B-V1.0",
        priority=1
    )
}


class LLMRouter:
    """
    Intelligent LLM Router that selects the best model for each task.
    
    Uses a multi-tiered approach:
    1. Classify the query type
    2. Filter models by capability
    3. Select based on availability and priority
    4. Fallback to alternatives if needed
    """
    
    def __init__(self, enable_rag: bool = False, pdf_files: List = None):
        self.enable_rag = enable_rag
        self.pdf_files = pdf_files or []
        self.model_cache = {}
        self.fallback_chain = ["gpt-3.5", "zephyr-7b", "wizardcoder-1b"]
        
    def classify_query(self, user_input: str, context: Dict = None) -> QueryType:
        """
        Classify the type of query to determine optimal model.
        
        Args:
            user_input: The user's input text
            context: Additional context (e.g., current step in workflow)
            
        Returns:
            QueryType enum indicating the query classification
        """
        input_lower = user_input.lower()
        
        # Check if it's parameter extraction
        if context and context.get('task') == 'parameter_extraction':
            return QueryType.PARAMETER_EXTRACTION
        
        # Check if it's G-code generation
        if any(keyword in input_lower for keyword in ['generate g-code', 'create g-code', 'mill', 'drill', 'cut', 'cnc']):
            return QueryType.GCODE_GENERATION
        
        # Check if it's code refinement
        if any(keyword in input_lower for keyword in ['refine', 'optimize', 'improve', 'fix', 'debug']):
            return QueryType.CODE_REFINEMENT
        
        # Check if it's machine-specific knowledge query
        if any(keyword in input_lower for keyword in ['siemens', 'fanuc', 'haas', 'machine', 'controller', 'specification']):
            return QueryType.MACHINE_KNOWLEDGE
        
        # Check if it's validation
        if any(keyword in input_lower for keyword in ['validate', 'check', 'verify', 'correct']):
            return QueryType.VALIDATION
        
        # Default to general query
        return QueryType.GENERAL_QUERY
    
    def get_best_model_for_task(self, query_type: QueryType, 
                                 user_preference: Optional[str] = None) -> str:
        """
        Select the best model for a given task.
        
        Args:
            query_type: The classified query type
            user_preference: Optional user-specified model preference
            
        Returns:
            Model key from MODEL_REGISTRY
        """
        # If user has a preference and it's suitable, use it
        if user_preference:
            user_pref_key = self._normalize_model_name(user_preference)
            if user_pref_key in MODEL_REGISTRY:
                model_config = MODEL_REGISTRY[user_pref_key]
                if query_type in model_config.use_cases:
                    return user_pref_key
        
        # Filter models that can handle this query type
        suitable_models = [
            (key, config) for key, config in MODEL_REGISTRY.items()
            if query_type in config.use_cases
        ]
        
        # Sort by priority (higher is better)
        suitable_models.sort(key=lambda x: x[1].priority, reverse=True)
        
        if not suitable_models:
            # Fallback to general purpose
            return "zephyr-7b"
        
        # Return the highest priority model
        return suitable_models[0][0]
    
    def _normalize_model_name(self, model_name: str) -> str:
        """Convert user-facing model name to registry key"""
        mapping = {
            "Fine-tuned StarCoder": "fine-tuned-starcoder",
            "CodeLlama": "codellama-7b",
            "GPT-3.5": "gpt-3.5",
            "Zephyr-7b": "zephyr-7b",
            "Phi-3-Mini": "phi-3-mini",
            "DeepSeek-Coder-1B": "deepseek-coder-1b",
            "WizardCoder-1B": "wizardcoder-1b"
        }
        return mapping.get(model_name, model_name.lower().replace(" ", "-"))
    
    def load_model(self, model_key: str):
        """
        Load a model from the registry.
        
        Args:
            model_key: Key from MODEL_REGISTRY
            
        Returns:
            Loaded LLM model instance
        """
        # Check cache first
        if model_key in self.model_cache:
            print(f"Using cached model: {model_key}")
            return self.model_cache[model_key]
        
        config = MODEL_REGISTRY.get(model_key)
        if not config:
            raise ValueError(f"Unknown model: {model_key}")
        
        print(f"Loading model: {config.name} for {config.capability.value}")
        
        try:
            # Load based on model type
            if model_key == "gpt-3.5":
                llm = ChatOpenAI(
                    model=config.model_id, 
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    api_key=openai.api_key
                )
            
            elif model_key == "fine-tuned-starcoder":
                # Import here to avoid loading if not needed
                from peft import PeftModel, PeftConfig
                from transformers import AutoModelForCausalLM
                
                try:
                    peft_config = PeftConfig.from_pretrained(config.model_id, token=hf_token)
                    base_model = AutoModelForCausalLM.from_pretrained(
                        "bigcode/starcoderbase-3b", 
                        token=hf_token
                    )
                    llm = PeftModel.from_pretrained(
                        base_model, 
                        config.model_id, 
                        token=hf_token
                    )
                except Exception as e:
                    print(f"Failed to load fine-tuned StarCoder: {e}")
                    print("Falling back to CodeLlama...")
                    return self.load_model("codellama-7b")
            
            else:
                # Use HuggingFace Endpoint
                llm = HuggingFaceEndpoint(
                    endpoint_url=config.endpoint_url,
                    task="text-generation",
                    max_new_tokens=config.max_tokens,
                    top_k=50,
                    temperature=config.temperature,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=hf_token
                )
            
            # Cache the model
            self.model_cache[model_key] = llm
            print(f"Successfully loaded: {config.name}")
            return llm
            
        except Exception as e:
            print(f"Error loading {config.name}: {e}")
            
            # Try fallback chain
            for fallback_key in self.fallback_chain:
                if fallback_key != model_key:
                    print(f"Attempting fallback to: {fallback_key}")
                    try:
                        return self.load_model(fallback_key)
                    except Exception as fallback_error:
                        print(f"Fallback failed: {fallback_error}")
                        continue
            
            raise Exception("All models failed to load")
    
    def route(self, user_input: str, context: Dict = None, 
              user_preference: Optional[str] = None):
        """
        Main routing method - classify query and return appropriate model.
        
        Args:
            user_input: User's input text
            context: Additional context dictionary
            user_preference: Optional user model preference
            
        Returns:
            Tuple of (model_instance, query_type, model_name)
        """
        # Classify the query
        query_type = self.classify_query(user_input, context)
        print(f"Query classified as: {query_type.value}")
        
        # Get the best model for this task
        model_key = self.get_best_model_for_task(query_type, user_preference)
        model_config = MODEL_REGISTRY[model_key]
        
        print(f"Selected model: {model_config.name}")
        print(f"Reason: {model_config.description}")
        
        # Load and return the model
        model = self.load_model(model_key)
        
        return model, query_type, model_config.name
    
    def get_model_recommendations(self, query_type: QueryType) -> List[str]:
        """
        Get all recommended models for a specific query type, sorted by priority.
        
        Args:
            query_type: The type of query
            
        Returns:
            List of model names suitable for this query type
        """
        suitable_models = [
            (config.name, config.priority) 
            for config in MODEL_REGISTRY.values()
            if query_type in config.use_cases
        ]
        
        # Sort by priority
        suitable_models.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, _ in suitable_models]
    
    def get_routing_explanation(self, user_input: str, context: Dict = None) -> str:
        """
        Get a human-readable explanation of why a particular model was chosen.
        
        Args:
            user_input: User's input text
            context: Additional context
            
        Returns:
            Explanation string
        """
        query_type = self.classify_query(user_input, context)
        model_key = self.get_best_model_for_task(query_type)
        config = MODEL_REGISTRY[model_key]
        
        explanation = f"""
🤖 **Model Routing Decision**

**Query Type Detected:** {query_type.value.replace('_', ' ').title()}

**Selected Model:** {config.name}
**Capability:** {config.capability.value.replace('_', ' ').title()}
**Reason:** {config.description}

**Alternative Models for this task:**
{chr(10).join('• ' + name for name in self.get_model_recommendations(query_type)[:3])}
        """
        
        return explanation.strip()


def get_optimal_model_for_step(step: str, user_preference: Optional[str] = None):
    """
    Helper function to get the optimal model for a specific workflow step.
    
    Args:
        step: Workflow step ('parameter_extraction', 'gcode_generation', etc.)
        user_preference: Optional user model preference
        
    Returns:
        Model instance
    """
    router = LLMRouter()
    
    context_mapping = {
        'parameter_extraction': {'task': 'parameter_extraction'},
        'gcode_generation': {'task': 'gcode_generation'},
        'refinement': {'task': 'refinement'},
        'validation': {'task': 'validation'},
    }
    
    context = context_mapping.get(step, {})
    model, query_type, model_name = router.route("", context, user_preference)
    
    return model, model_name
