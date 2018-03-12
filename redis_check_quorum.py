#!/usr/bin/env python
# encoding: utf-8
"""
redis_check_quorum.py

Check number of sentinel nodes

@author Carlos Garcia <cgarciaarano@gmail.com>
"""

# 3rd parties
from redis import StrictRedis
from redis.exceptions import ResponseError
from sensu_plugin import SensuPluginCheck


class CheckSentinelQuorum(SensuPluginCheck):

    def setup(self):
        # Setup is called with self.parser set and is responsible for setting up
        # self.options before the run method is called

        self.parser.add_argument(
            '-H',
            '--host',
            required=True,
            type=str,
            help='Hostname or IP address of one sentinel server'
        )
        self.parser.add_argument(
            '-p',
            '--port',
            required=True,
            type=int,
            help='Port number of one sentinel server'
        )
        self.parser.add_argument(
            '-C',
            '--cluster',
            required=True,
            type=str,
            help='Cluster name of one sentinel server'
        )
        self.parser.add_argument(
            '-c',
            '--critical',
            required=True,
            type=int,
            help='Integer critical level to output'
        )

    def run(self):
        self.conn = StrictRedis(host=self.options.host, port=self.options.port, socket_timeout=5)

        try:
            response = self.conn.execute_command("SENTINEL CKQUORUM {0}".format(self.options.cluster))
        except ResponseError as e:
            response = e.message

        quorum = response.startswith('OK')
        if quorum != self.options.critical:
            self.ok("Quorum is OK: {0}".format(response))
        else:
            self.critical("Quorum is KO: {0}".format(response))

if __name__ == '__main__':
    f = CheckSentinelQuorum()
