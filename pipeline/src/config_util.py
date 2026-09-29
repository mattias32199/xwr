# ./src/config_util.py
"""Contains modular functions for check_params pipeline."""

import yaml

from src.radar_equations import (
    calculate_bandwidth,
    calculate_chirp_period,
    calculate_doppler_resolution,
    calculate_fps,
    calculate_max_range,
    calculate_max_velocity,
    calculate_range_resolution,
    calculate_sample_time,
    calculate_wavelength,
    get_ideal_range_resolution,
    get_ideal_doppler_resolution
)


REQUIREMENTS = {
    "fps": 10.0,           # R1
    "min_bins": 32,        # R2
    "tolerance": 0.05, # R3 & R4 (resolutions)
    "max_range_m": 5.0,    # R5
    "max_velocity_mps": 4.75,  # R6
}



def load_config(config_path):
    """Loads radar config from yaml"""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return cfg

def compute_performance(cfg):
    """Compute the radar performance values needed for R1-R6."""
    sample_time = calculate_sample_time(cfg["adc_samples"], cfg["sample_rate"])
    bandwidth = calculate_bandwidth(cfg["freq_slope"], sample_time)
    chirp_period = calculate_chirp_period(cfg["idle_time"], cfg["ramp_end_time"])
    wavelength = calculate_wavelength(cfg["frequency"], cfg["freq_slope"],
                                      cfg["adc_start_time"], sample_time)
    range_resolution = calculate_range_resolution(bandwidth)

    return {
        "fps": calculate_fps(cfg["frame_period"]), # R1
        "range_bins": cfg["adc_samples"], # R2
        "doppler_bins": cfg["frame_length"], # R2
        "range_resolution": range_resolution, # R3
        "max_range": calculate_max_range(range_resolution, cfg["adc_samples"]), # R5
        "doppler_resolution": calculate_doppler_resolution(
            wavelength, chirp_period, cfg["frame_length"]
        ), # R4
        "max_velocity": calculate_max_velocity(wavelength, chirp_period), # R6

        # extras for R3
        "sample_time": sample_time,
        "ramp_end_time": cfg["ramp_end_time"],
    }


def run_config_test_cases(values):
    """Runs test cases to confirm requirements R1-R6. Returns True if all pass."""
    print(f"\nREQUIREMENTS:\n{REQUIREMENTS}\n")
    # Additional calculations
    ideal_range_res = get_ideal_range_resolution(
        REQUIREMENTS["max_range_m"], values["range_bins"],
        values["sample_time"], values["ramp_end_time"]
    )
    ideal_doppler_res = get_ideal_doppler_resolution(
        REQUIREMENTS["max_velocity_mps"], values["doppler_bins"]
    )

    # R1
    val = values['fps']
    req = REQUIREMENTS["fps"]
    assert val >= req, f"FAILED R1: FPS={val} is < {req}"
    print(f"PASSED R1: FPS={val} is sufficient")

    # R2
    val_range = values["range_bins"]
    val_doppler = values["doppler_bins"]
    req = REQUIREMENTS["min_bins"]
    assert val_range >= req, f"FAILED R2: Range bins={val_range} < {req}"
    assert val_doppler >= req, f"FAILED R2: Doppler bins={val_doppler} < {req}"
    print(f"PASSED R2: Range bins={val_range} and Doppler bins={val_doppler} are sufficient")

    # R3
    val = values["range_resolution"]
    tol = REQUIREMENTS["tolerance"]
    req = ideal_range_res * (1 + tol)
    assert val <= req, f"FAILED R3: Range res={val} > {req}"
    print(f"PASSED R3: Range resolution={val} is sufficient (ideal={ideal_range_res})")


    # R4
    val = values["doppler_resolution"]
    req = ideal_doppler_res * (1 + tol)
    assert val <= req, f"FAILED R4: Doppler res={val} > {req}"
    print(f"PASSED R4: Doppler resolution={val} is sufficient (ideal={ideal_doppler_res})")


    # R5
    val = values["max_range"]
    req = REQUIREMENTS["max_range_m"]
    assert val >= req, f"FAILED R5: Range err={val} < {req}"
    print(f"PASSED R5: Range={val} is sufficient")

    # R6
    val = values["max_velocity"]
    req = REQUIREMENTS["max_velocity_mps"]
    assert val >= req, f"FAILED R6: Range={val} < {req}"
    print(f"PASSED R6: Max velocity={val} is sufficient")

    print("\nALL TESTS PASSED")
    return True
