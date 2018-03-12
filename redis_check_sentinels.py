#!/usr/bin/env python
# encoding: utf-8
"""
redis_check_sentinels.py

Check number of sentinel nodes

@author Carlos Garcia <cgarciaarano@gmail.com>
"""

# 3rd parties
from redis import StrictRedis
from sensu_plugin import SensuPluginCheck


class CheckSentinels(SensuPluginCheck):

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
        self.parser.add_argument(
            '-w',
            '--warning',
            required=True,
            type=int,
            help='Integer warning level to output'
        )
        self.parser.add_argument(
            '-d',
            '--checkdead',
            required=False,
            action='store_true',
            default=False,
            help='Check for dead sentinels'
        )

    def run(self):
        self.conn = StrictRedis(host=self.options.host, port=self.options.port, socket_timeout=5)

        sentinels = self.conn.sentinel_sentinels(self.options.cluster)

        if self.options.checkdead:
            dead_sentinels = filter(lambda x: x.get('is_disconnected', True), sentinels)
            count_dead_sentinels = len(dead_sentinels)

            if count_dead_sentinels >= self.options.critical:
                self.critical("The number of dead sentinels ({n}) is above critical ({c})".format(n=count_dead_sentinels, c=self.options.critical))
            elif count_dead_sentinels >= self.options.warning:
                self.warning("The number of dead sentinels is {n}, above warning ({w}) and below critical ({c})".format(n=count_dead_sentinels, w=self.options.warning, c=self.options.critical))
            elif count_dead_sentinels < self.options.warning:
                self.ok("The number of dead sentinels ({n}) is below warning ({w})".format(n=count_dead_sentinels, w=self.options.warning))
            else:
                self.unknown("Can't get number of live sentinels")
        else:
            live_sentinels = filter(lambda x: not x.get('is_disconnected', True), sentinels)
            count_live_sentinels = len(live_sentinels) + 1

            if count_live_sentinels > self.options.warning:
                self.ok("The number of live sentinels ({n}) is above warning ({w})".format(n=count_live_sentinels, w=self.options.warning))
            elif count_live_sentinels <= self.options.critical:
                self.critical("The number of live sentinels ({n}) is below critical ({c})".format(n=count_live_sentinels, c=self.options.critical))
            elif count_live_sentinels <= self.options.warning:
                self.warning("The number of live sentinels is {n}, below warning ({w}) and above critical ({c})".format(n=count_live_sentinels, w=self.options.warning, c=self.options.critical))
            else:
                self.unknown("Can't get number of live sentinels")


if __name__ == '__main__':
    f = CheckSentinels()
