#./pipeline.py

"""Simple radar data capture pipeline with live visualization."""

import os
import time
import tyro

from pathlib import Path
import numpy as np

import xwr
from xwr.rsp import numpy as xwr_rsp

from src.config_util import load_config
from src.capture_util import (
    init_logger, save_frames, init_plot, live_capture_loop, q_capture_loop
)
from src.viz import VisualizationConfig


def cli_main(
    config: str = os.path.join(os.path.dirname(__file__), "config.yaml"),
    device: str = "AWR1843",
    rsp: str = "AWR1843AOP",
    duration: float = 30.0,
    output: str = "capture.npz",
    vis: VisualizationConfig = VisualizationConfig(),
    verbose: int = 20,
):
    """Capture radar data for a fixed duration and save to disk.

    - Data is captured immediately upon starting the script.
    - Live visualization shows the range-doppler spectrum and framerate.
    - Raw I/Q frames are saved
    """
    # Init logger
    log = init_logger(verbose)
    log.info(f"Capturing for {duration:.1f} seconds → {output}")

    # load config
    cfg = load_config(config)
    cfg["radar"]["device"] = device

    # Initialize radar system
    awr = xwr.XWRSystem(**cfg)
    log.info(f"Radar initialized: range_resolution={awr.config.range_resolution:.3f}m, "
             f"max_range={awr.config.max_range:.1f}m")

    # Initialize rsp and plot
    rsp_inst = getattr(xwr_rsp, rsp)(window=False, size={"azimuth": vis.azimuth})
    plot = init_plot(rsp, vis, awr, cfg, rsp_inst)

    # Capture loop
    # frames = live_capture_loop(log, awr, rsp_inst, plot, duration)
    frames, timestamps = q_capture_loop(log, awr, rsp_inst, plot, duration)

    awr.stop()

    # Save frames
    if not frames:
        log.error("ERROR??? No frames captured; nothing saved.")
        return
    else:
        save_frames(frames, timestamps, output, cfg, awr, log)


if __name__ == "__main__":
    tyro.cli(cli_main)
