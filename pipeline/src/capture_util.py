# ./src/capture_util.py

"""Utils for data capture pipeline."""

import logging
import numpy as np
from pathlib import Path
from rich.logging import RichHandler

from src.viz import RadarPlot



def init_logger(verbose):
    """Initialize logger."""
    # Logging
    logging.basicConfig(
        level=verbose, format="%(name)-12s  %(message)s", datefmt="[%H:%M:%S]",
        handlers=[RichHandler()])
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    log = logging.getLogger("xwr/capture")
    return log


def init_plot(rsp, vis, awr, cfg, rsp_inst):
    """Initializes plots for vis."""
    if rsp_inst.SAMPLE_TYPE == "I":
        Nr = cfg["radar"]["adc_samples"] // 2 + 1
    else:
        Nr = cfg["radar"]["adc_samples"]
    n_doppler = cfg["radar"]["frame_length"]
    plot = RadarPlot(
        n_range=Nr,
        n_doppler=n_doppler,
        n_azimuth=vis.azimuth,
        max_range=awr.config.max_range,
        max_doppler=awr.config.max_doppler,
        range_resolution=awr.config.range_resolution,
        pclip=vis.pclip,
        power=vis.power,
    )
    return plot


def save_frames(frames, output, cfg, awr, log):
    """Saves frames to npz."""
    frames_array = np.stack(frames, axis=0)  # shape: [n_frames, doppler, tx, rx, range]
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        frames=frames_array,
        n_frames=len(frames),
        adc_samples=cfg["radar"]["adc_samples"],
        frame_length=cfg["radar"]["frame_length"],
        sample_rate=awr.config.sample_rate,
        range_resolution=awr.config.range_resolution,
        max_range=awr.config.max_range,
        max_doppler=awr.config.max_doppler,
    )
    log.info(f"Saved {len(frames)} frames → {output_path} ({frames_array.nbytes / 1e6:.1f} MB)")
    log.info(f"Data shape: {frames_array.shape} [n_frames, doppler, tx, rx, range]")
