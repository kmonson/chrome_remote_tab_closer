'''
Created on Mar 17, 2015

@author: Xistic
'''

import logging
from pathlib import Path
from importlib import resources
import os
from http import HTTPStatus
import json
import yaml
import sys
import asyncio
import time

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado_http_auth import BasicAuthMixin, auth_required

import click

from voluptuous import Invalid

from utils import config_schema

_log = logging.getLogger(__file__)
credentials = {'admin': 'password'}

configuration_dir = None


# class BaseHandler(BasicAuthMixin, tornado.web.RequestHandler):
#     def prepare(self):
#         self.get_authenticated_user(check_credentials_func=credentials.get, realm='Protected')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = [p.stem for p in configuration_dir.glob("*.yaml")]
        self.render("templates/main.html", items=items)


class ConfigHandler(tornado.web.RequestHandler):
    def get(self, name):
        bans = []
        host = ""

        target = configuration_dir / f"{name}.yaml"
        if target.exists() and target.is_file():
            with open(target) as f:
                try:
                    config = yaml.safe_load(f)
                    config = config_schema(config)
                    host = config["host"]
                    bans = config["bans"]
                except (yaml.YAMLError, Invalid) as e:
                    logging.error(f"Failed to load config {name}: {e}")

        self.render("templates/config.html", bans=bans, host=host)

    def post(self, name):
        _log.warning(f"Config {name} posted")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/([a-zA-Z_]+)", ConfigHandler),
    ])


@click.command()
@click.option("-l", "--log-file", type=click.Path(resolve_path=True, dir_okay=False))
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
@click.option("-p", "--port", type=int, default=8888)
@click.argument("config-dir", type=click.Path(exists=True, file_okay=False, resolve_path=True), default='.')
def main(config_dir, port, log_file, verbose, quiet):
    global configuration_dir
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    configuration_dir = Path(config_dir)
    level = logging.WARNING + 10 * (quiet - verbose)
    logging.basicConfig(filename=log_file, level=level)

    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
