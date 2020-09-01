import click
import yaml
import pychrome
import logging
from watchdog.observers import Observer
from pathlib import Path
from watchdog.events import PatternMatchingEventHandler
from threading import Event
from utils import config_schema
from voluptuous import Invalid

configs = {}
config_event = Event()


def reload_configs(path: Path):
    global configs
    result_configs = {}
    for config_path in path.glob("*.yaml"):
        name = config_path.stem
        with open(config_path) as f:
            logging.info(f"Loading config: {name}")
            try:
                config = yaml.safe_load(f)
                config = config_schema(config)
            except (yaml.YAMLError, Invalid) as e:
                logging.error(f"Failed to load config {name}: {e}")
                continue

            result_configs[name] = config

    configs = result_configs


class ConfigUpdateHandler(PatternMatchingEventHandler):
    def __init__(self, path: Path):
        super().__init__(patterns=["*.yaml"])
        self.path = path

    def on_any_event(self, event):
        reload_configs(self.path)


def main_loop(timeout=5.0):
    logging.debug("Starting main loop.")
    while True:
        # execute configs
        # Get reference to configs before we execute.
        c_copy = configs

        for name, config in c_copy.items():
            logging.debug(f"Running config: {name}")
            bans = config["bans"]
            try:
                browser = pychrome.Browser(config["host"])
                for tab in browser.list_tab(timeout=5.0):
                    url = tab._kwargs.get("url")
                    if url is None:
                        continue
                    if any(ban in url for ban in bans):
                        browser.close_tab(tab)
                        logging.info(f"Closed tab {url} on {name}")
            except Exception as e:
                logging.warning(f"{name} failed to execute: {e}")

        config_event.wait(timeout=timeout)
        config_event.clear()


@click.command()
@click.option("-t", "--timeout", type=float, default=5.0)
@click.option("-l", "--log-file", type=click.Path(resolve_path=True, dir_okay=False))
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
@click.argument("config-dir", type=click.Path(exists=True, file_okay=False, resolve_path=True), default='.')
def main(config_dir, timeout, log_file, verbose, quiet):
    level = logging.WARNING + 10 * (quiet - verbose)
    logging.basicConfig(filename=log_file, level=level)
    config_dir = Path(config_dir)
    event_handler = ConfigUpdateHandler(config_dir)
    observer = Observer()
    observer.schedule(event_handler, str(config_dir))
    observer.start()

    reload_configs(config_dir)
    config_event.clear()

    main_loop(timeout)


if __name__ == "__main__":
    main()


