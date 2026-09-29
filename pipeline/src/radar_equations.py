"""Radar equations for config check."""

C = 299_792_458.0  # speed of light, m/s
NUM_TX = 3         # AWR1843AOP transmit antennas (take turns, TDM-MIMO)
MAX_BANDWIDTH_MHZ = 4000.0 # hardware limit


# Intermediate values (not checked with requirements)
def calculate_sample_time(adc_samples: int, sample_rate: float) -> float:
    """ADC sampling time T_s (us) from samples per chirp and sample rate (ksps)."""
    return adc_samples / sample_rate * 1e3


def calculate_bandwidth(freq_slope: float, sample_time: float) -> float:
    """Effective bandwidth B (MHz) = slope (MHz/us) x T_s (us)."""
    return freq_slope * sample_time


def calculate_chirp_loop_time(idle_time: float, ramp_end_time: float) -> float:
    """Chirp loop time T_c (us): one chirp from each of the 3 TX antennas."""
    return (idle_time + ramp_end_time) * NUM_TX


def calculate_wavelength(frequency: float, freq_slope: float,
                         adc_start_time: float, sample_time: float) -> float:
    """Wavelength (m) at the center of the sampled part of the chirp."""
    center_time = adc_start_time + sample_time / 2               # us
    center_freq = frequency * 1e9 + freq_slope * 1e6 * center_time  # Hz
    return C / center_freq


# PERFORMANCE VALUES TIED TO REQUIREMENTS
# R2 is taken directly from config, no additional calculation required

# R1 (framerate)
def calculate_fps(frame_period: float) -> float:
    """Calculates fps from frame period (ms)."""
    return 1e3 / frame_period

# R3
def calculate_range_resolution(bandwidth: float) -> float:
    """Range resolution (m) = c / 2B."""
    return C / (2 * bandwidth * 1e6)

def get_ideal_range_resolution(req_max_range, val_range_bins) -> float:
    """Required max range spread across all range bins constrained by 4 GHz bandwidth limit."""
    return max(
        req_max_range / val_range_bins,
        C / (2 * MAX_BANDWIDTH_MHZ * 1e6)
    )

# R4
def calculate_doppler_resolution(
    wavelength: float, chirp_loop_time: float, frame_length: int
) -> float:
    """Doppler (velocity) resolution (m/s) = lambda / (2 L T_c)."""
    return wavelength / (2 * frame_length * chirp_loop_time * 1e-6)


def get_ideal_doppler_resolution(req_max_velocity, val_doppler_bins) -> float:
    """Required max range spread across all range bins constrained by 4 GHz bandwidth limit."""
    return 2 * req_max_velocity / val_doppler_bins

# R5
def calculate_max_range(range_resolution: float, adc_samples: int) -> float:
    """Max range (m) = range resolution x number of range bins."""
    return range_resolution * adc_samples


# R6
def calculate_max_velocity(wavelength: float, chirp_loop_time: float) -> float:
    """Max unambiguous velocity (m/s) = lambda / 4T_c. Measurable range is +/- this."""
    return wavelength / (4 * chirp_loop_time * 1e-6)
