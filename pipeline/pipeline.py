import tyro
import os
import logging
import yaml
from rich.logging import RichHandler

import xwr



def cli_main(
    config: str = os.path.join(os.path.dirname(__file__), "config.yaml"),
    device: str = "AWR1843",
    rsp: str = "AWR1843AOP",
    verbose: int = 20
):
    """Main function to parse cli input to actuate data collection tool."""
    # Logging
    logging.basicConfig(
        level=verbose, format="%(name)-12s  %(message)s", datefmt="[%H:%M:%S]",
        handlers=[RichHandler()])
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    log = logging.getLogger("xwr/demo")

    with open(config) as f:
        cfg = yaml.safe_load(f)



if __name__ == "__main__":
    tyro.cli(cli_main)
