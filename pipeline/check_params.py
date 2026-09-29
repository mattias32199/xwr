# ./check_params.py
"""Computes radar performance from config and checks values against requirements."""

import os
from src.config_util import load_config, compute_performance, run_config_test_cases

def main():
    """Config checker pipeline."""
    # config
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    cfg = load_config(config_path)
    print("\nCONFIG:")
    print(cfg)
    print('\n')

    # compute radar performance values
    values = compute_performance(cfg["radar"])

    # check against requirements (test cases)
    _pass = run_config_test_cases(values)
    if _pass:
        print("\nTime to try running with demo...\n")

if __name__ == "__main__":
    main()
