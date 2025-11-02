"""
Run examples for both Predict Agent and Risk Agent
"""
import sys

def run_predict_examples():
    """Run Predict Agent examples"""
    print("=" * 70)
    print("PREDICT AGENT EXAMPLES")
    print("=" * 70)
    try:
        from predict_agent.example_usage import main
        main()
        return True
    except Exception as e:
        print(f"Error running Predict Agent examples: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_risk_examples():
    """Run Risk Agent examples"""
    print("\n" + "=" * 70)
    print("RISK AGENT EXAMPLES")
    print("=" * 70)
    try:
        from risk_agent.example_usage import main
        main()
        return True
    except Exception as e:
        print(f"Error running Risk Agent examples: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("RUNNING ALL EXAMPLES")
    print("=" * 70)
    
    results = {
        'predict': run_predict_examples(),
        'risk': run_risk_examples()
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Predict Agent examples: {'[PASS]' if results['predict'] else '[FAIL]'}")
    print(f"Risk Agent examples:    {'[PASS]' if results['risk'] else '[FAIL]'}")
    print("=" * 70)
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
