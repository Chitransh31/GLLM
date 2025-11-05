"""
Test script for LLM Router Architecture

This script tests the intelligent routing system with various
query types and validates model selection logic.

Run this script to ensure the router is working correctly:
    python test_llm_router.py
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gllm.utils.llm_router import LLMRouter, QueryType, MODEL_REGISTRY


def test_query_classification():
    """Test that queries are correctly classified"""
    print("\n" + "="*60)
    print("TEST 1: Query Classification")
    print("="*60)
    
    router = LLMRouter()
    
    test_cases = [
        ("Generate G-code for milling a rectangular pocket", QueryType.GCODE_GENERATION),
        ("Mill a circle with 50mm diameter", QueryType.GCODE_GENERATION),
        ("Extract machining parameters", QueryType.PARAMETER_EXTRACTION, {'task': 'parameter_extraction'}),
        ("What is the maximum spindle speed for Siemens 840D?", QueryType.MACHINE_KNOWLEDGE),
        ("Optimize this G-code for faster execution", QueryType.CODE_REFINEMENT),
        ("Validate the G-code syntax", QueryType.VALIDATION),
        ("What is the difference between G0 and G1?", QueryType.GENERAL_QUERY),
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        if len(test_case) == 3:
            query, expected_type, context = test_case
        else:
            query, expected_type = test_case
            context = None
        
        result = router.classify_query(query, context)
        status = "✓" if result == expected_type else "✗"
        
        if result == expected_type:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Test {i}: {query[:50]}...")
        print(f"   Expected: {expected_type.value}")
        print(f"   Got:      {result.value}")
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_model_selection():
    """Test that the best models are selected for each task"""
    print("\n" + "="*60)
    print("TEST 2: Model Selection")
    print("="*60)
    
    router = LLMRouter()
    
    test_cases = [
        (QueryType.GCODE_GENERATION, "fine-tuned-starcoder", "Domain expert for G-code"),
        (QueryType.PARAMETER_EXTRACTION, "phi-3-mini", "Fast and efficient"),
        (QueryType.MACHINE_KNOWLEDGE, "gpt-3.5", "Knowledge-rich model"),
        (QueryType.GENERAL_QUERY, "gpt-3.5", "Best for general questions"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (query_type, expected_model, reason) in enumerate(test_cases, 1):
        result = router.get_best_model_for_task(query_type)
        status = "✓" if result == expected_model else "✗"
        
        if result == expected_model:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Test {i}: {query_type.value}")
        print(f"   Expected: {expected_model} ({reason})")
        print(f"   Got:      {result}")
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_user_preference():
    """Test that user preferences are respected when suitable"""
    print("\n" + "="*60)
    print("TEST 3: User Preference Override")
    print("="*60)
    
    router = LLMRouter()
    
    # Test valid preference
    result = router.get_best_model_for_task(
        QueryType.GCODE_GENERATION,
        user_preference='GPT-3.5'
    )
    test1 = result == 'gpt-3.5'
    print(f"{'✓' if test1 else '✗'} Test 1: Valid preference (GPT-3.5 for G-code)")
    print(f"   Expected: gpt-3.5")
    print(f"   Got:      {result}")
    print()
    
    # Test unsuitable preference (should use best model instead)
    result = router.get_best_model_for_task(
        QueryType.GCODE_GENERATION,
        user_preference='InvalidModel'
    )
    test2 = result == 'fine-tuned-starcoder'
    print(f"{'✓' if test2 else '✗'} Test 2: Invalid preference (fallback to best)")
    print(f"   Expected: fine-tuned-starcoder")
    print(f"   Got:      {result}")
    print()
    
    passed = sum([test1, test2])
    failed = 2 - passed
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_routing_explanation():
    """Test that routing explanations are generated"""
    print("\n" + "="*60)
    print("TEST 4: Routing Explanations")
    print("="*60)
    
    router = LLMRouter()
    
    explanation = router.get_routing_explanation(
        "Generate G-code for milling",
        context={'task': 'gcode_generation'}
    )
    
    # Check that explanation contains key information
    has_query_type = "Query Type" in explanation
    has_model = "Selected Model" in explanation
    has_reason = "Reason" in explanation
    
    print(f"{'✓' if has_query_type else '✗'} Contains query type")
    print(f"{'✓' if has_model else '✗'} Contains selected model")
    print(f"{'✓' if has_reason else '✗'} Contains reasoning")
    print()
    print("Sample explanation:")
    print(explanation)
    print()
    
    passed = sum([has_query_type, has_model, has_reason])
    failed = 3 - passed
    print(f"Results: {passed}/3 checks passed")
    return failed == 0


def test_model_recommendations():
    """Test that model recommendations are provided"""
    print("\n" + "="*60)
    print("TEST 5: Model Recommendations")
    print("="*60)
    
    router = LLMRouter()
    
    recommendations = router.get_model_recommendations(QueryType.GCODE_GENERATION)
    
    print(f"Recommendations for G-code generation:")
    for i, model_name in enumerate(recommendations, 1):
        print(f"  {i}. {model_name}")
    print()
    
    # Check that Fine-tuned StarCoder is first (highest priority)
    test1 = recommendations[0] == "Fine-tuned StarCoder"
    print(f"{'✓' if test1 else '✗'} Fine-tuned StarCoder is top recommendation")
    
    # Check that we have multiple recommendations
    test2 = len(recommendations) >= 2
    print(f"{'✓' if test2 else '✗'} Multiple recommendations provided ({len(recommendations)})")
    print()
    
    passed = sum([test1, test2])
    failed = 2 - passed
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_model_registry():
    """Test that the model registry is properly configured"""
    print("\n" + "="*60)
    print("TEST 6: Model Registry Validation")
    print("="*60)
    
    print(f"Total models in registry: {len(MODEL_REGISTRY)}")
    print()
    
    passed = 0
    failed = 0
    
    for model_key, config in MODEL_REGISTRY.items():
        # Check required fields
        has_name = bool(config.name)
        has_capability = bool(config.capability)
        has_use_cases = len(config.use_cases) > 0
        has_priority = config.priority > 0
        
        all_valid = all([has_name, has_capability, has_use_cases, has_priority])
        
        status = "✓" if all_valid else "✗"
        if all_valid:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {config.name}")
        print(f"   Capability: {config.capability.value}")
        print(f"   Use cases: {len(config.use_cases)}")
        print(f"   Priority: {config.priority}")
        print()
    
    print(f"Results: {passed} models valid, {failed} models invalid")
    return failed == 0


def test_full_routing():
    """Test end-to-end routing with realistic scenarios"""
    print("\n" + "="*60)
    print("TEST 7: End-to-End Routing")
    print("="*60)
    
    router = LLMRouter()
    
    scenarios = [
        {
            "description": "Mill a rectangular pocket 50mm x 30mm x 5mm deep in aluminum",
            "context": {'task': 'parameter_extraction'},
            "expected_capability": "FAST_EFFICIENT"
        },
        {
            "description": "Generate G-code for the above milling operation",
            "context": {'task': 'gcode_generation'},
            "expected_capability": "DOMAIN_EXPERT"
        },
        {
            "description": "What are the feed rate recommendations for Siemens 840D?",
            "context": {'task': 'machine_knowledge'},
            "expected_capability": "KNOWLEDGE_RICH"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(scenarios, 1):
        try:
            model_key = router.get_best_model_for_task(
                router.classify_query(scenario["description"], scenario["context"])
            )
            config = MODEL_REGISTRY[model_key]
            
            is_correct = config.capability.value == scenario["expected_capability"]
            status = "✓" if is_correct else "✗"
            
            if is_correct:
                passed += 1
            else:
                failed += 1
            
            print(f"{status} Scenario {i}: {scenario['description'][:50]}...")
            print(f"   Expected capability: {scenario['expected_capability']}")
            print(f"   Selected model: {config.name}")
            print(f"   Model capability: {config.capability.value}")
            print()
        except Exception as e:
            print(f"✗ Scenario {i}: ERROR - {str(e)}")
            failed += 1
    
    print(f"Results: {passed} scenarios passed, {failed} scenarios failed")
    return failed == 0


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("LLM ROUTER ARCHITECTURE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Query Classification", test_query_classification),
        ("Model Selection", test_model_selection),
        ("User Preference", test_user_preference),
        ("Routing Explanation", test_routing_explanation),
        ("Model Recommendations", test_model_recommendations),
        ("Model Registry", test_model_registry),
        ("End-to-End Routing", test_full_routing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} CRASHED: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print()
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! The LLM router is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
