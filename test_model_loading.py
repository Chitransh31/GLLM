#!/usr/bin/env python3
"""
Test script to verify model loading works correctly
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

def test_model_loading():
    """Test different model configurations"""
    print("="*60)
    print("TESTING MODEL LOADING")
    print("="*60)
    
    try:
        from gllm.utils.model_utils import setup_model
        
        models_to_test = [
            "Zephyr-7b",
            "GPT-3.5", 
            "Fine-tuned StarCoder",
            "CodeLlama"
        ]
        
        for model_name in models_to_test:
            print(f"\n🔧 Testing {model_name}...")
            print("-" * 40)
            
            try:
                model = setup_model(model_name)
                if model is not None:
                    print(f"✅ {model_name} loaded successfully")
                    print(f"   Model type: {type(model).__name__}")
                else:
                    print(f"❌ {model_name} returned None")
                    
            except Exception as e:
                print(f"❌ {model_name} failed to load: {e}")
        
        print(f"\n{'='*60}")
        print("MODEL LOADING TEST COMPLETED")
        print(f"{'='*60}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def print_system_info():
    """Print system information for debugging"""
    import psutil
    import platform
    
    print("\n📊 SYSTEM INFORMATION")
    print("-" * 40)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"CPU: {platform.processor()}")
    print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB total")
    print(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    print(f"RAM Usage: {psutil.virtual_memory().percent}%")

def main():
    """Main test function"""
    try:
        print_system_info()
    except ImportError:
        print("Note: Install psutil for system info: pip install psutil")
    
    test_model_loading()
    
    print("\n💡 RECOMMENDATIONS:")
    print("- For low memory systems: Use 'Zephyr-7b' or 'GPT-3.5'")
    print("- For code generation: Use 'CodeLlama' (via API) or 'Fine-tuned StarCoder'")
    print("- For general tasks: Use 'Zephyr-7b'")
    print("- If you have OpenAI API access: Use 'GPT-3.5'")

if __name__ == "__main__":
    main()
