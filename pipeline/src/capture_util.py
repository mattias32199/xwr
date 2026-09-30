# ./src/capture_util.py

"""Utils for data capture pipeline."""

import logging
import numpy as np
from pathlib import Path
from rich.logging import RichHandler
import time
from queue import Empty


from src.viz import RadarPlot, FrameRateLogger



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


def live_capture_loop(log, awr, rsp_inst, plot, duration):
    """Live capture loop, loses frames for saving."""
    framerate = FrameRateLogger(log)
    frames = []
    start_time = time.time()
    try:
        log.info("Starting capture...")
        for frame in awr.dstream(numpy=True):
            # Store raw frame
            frames.append(frame.copy())
            # Process and visualize
            dear = np.abs(rsp_inst(frame[None, ...]))
            framerate.tick()
            plot.update(dear, framerate.fps)
            # Check if duration exceeded
            elapsed = time.time() - start_time
            if elapsed >= duration:
                log.info(f"Capture complete ({elapsed:.1f}s, {len(frames)} frames)")
                break
    except KeyboardInterrupt:
        log.warning("Capture interrupted by user")
        awr.stop()
        raise
    return frames


def q_capture_loop(log, awr, rsp_inst, plot, duration):
    """Queues every frame to avoid drops."""
    framerate = FrameRateLogger(log)
    frames, timestamps = [], []
    q = awr.qstream(numpy=True)
    log.info("Waiting for first frame...")
    start_time = None
    try:
        while True:
            try:
                frame = q.get(timeout=5.0)
            except Empty:
                log.error("No frame received for 5 s; stopping.")
                break
            if frame is None:
                break
            now = time.time()
            if start_time is None:
                start_time = now
                log.info("Starting capture...")
            frames.append(frame.copy())
            timestamps.append(now)
            framerate.tick()
            # Preview only when caught up, so plotting never delays saving
            if q.empty():
                dear = np.abs(rsp_inst(frame[None, ...]))
                plot.update(dear, framerate.fps)
            if now - start_time >= duration:
                break
    except KeyboardInterrupt:
        log.warning("Capture interrupted by user; saving frames captured so far")

    elapsed = timestamps[-1] - timestamps[0] if timestamps else 0.0
    expected = int(round(elapsed * awr.fps)) + 1
    log.info(f"Captured {len(frames)}/{expected} frames in {elapsed:.1f}s")
    return frames, timestamps

def save_frames(frames, timestamps, output, cfg, awr, log):
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
        timestamps=timestamps
    )
    log.info(f"Saved {len(frames)} frames → {output_path} ({frames_array.nbytes / 1e6:.1f} MB)")
    log.info(f"Data shape: {frames_array.shape} [n_frames, doppler, tx, rx, range]")
