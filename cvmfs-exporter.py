import argparse
import subprocess
import logging as log
import xattr
import re
import os
import psutil

from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server, WSGIRequestHandler

# Mapping from
# https://cvmfs.readthedocs.io/en/stable/cpt-details.html#getxattr
# https://gitlab.cern.ch/cloud/cvmfs-prometheus-exporter
CVMFS_EXTENDED_ATTRIBUTES = {
    'expires': 'Shows the remaining life time of the '
               'mounted root file catalog in minutes.',
    'inode_max': 'Shows the highest possible inode with '
                 'the current set of loaded catalogs.',
    'maxfd': 'Shows the maximum number of file '
             'descriptors available to file system clients.',
    'ncleanup24': 'Shows the number of cache '
                  'cleanups in the last 24 hours.',
    'nclg': 'Shows the number of currently loaded nested catalogs.',
    'ndiropen': 'Shows the overall number of opened directories.',
    'ndownload': 'Shows the overall number '
                 'of downloaded files since mounting.',
    'nioerr': 'Shows the total number of I/O '
              'errors encoutered since mounting.',
    'nopen': 'Shows the overall number of open() calls since mounting.',
    'revision': 'Shows the file catalog revision of the mounted root catalog, '
                'an auto-increment counter increased on every repository '
                'publish.',
    'rx': 'Shows the overall amount of downloaded kilobytes.',
    'speed': 'Shows the average download speed.',
    'timeout': 'Shows the timeout for proxied connections in seconds.',
    'timeout_direct': 'Shows the timeout for direct connections in seconds.',
    'uptime': 'Shows the time passed since mounting in minutes.',
    'usedfd': 'Shows the number of file descriptors currently '
              'issued to file system clients.',
}


def exec_command(command):
    log.debug('Executing command: %s', command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    process_stdout, process_stderr = process.communicate()
    return process_stdout.decode("utf-8").split('\n')


def mounted_repos():
    cmd_out = exec_command(['cvmfs_config', 'status'])
    return list(map(lambda x: x.split(' ')[0], filter(lambda x: x != '', cmd_out)))


def convert_time(time):
    if time.endswith('m'):
        return int(time[:-1])*60
    elif time.endswith('h'):
        return int(time[:-1])*60*60
    elif time.endswith('d'):
        return int(time[:-1])*60*60*24
    else:
        return int(time[:-1])


class CVMFSCollector(object):
    def collect(self):
        log.debug('Start of collection cycle')

        gauges = {}
        for metric in CVMFS_EXTENDED_ATTRIBUTES:
            if metric in ['uptime', 'ndownload', 'nioerr', 'nopen', 'rx']:
                gauges[metric] = CounterMetricFamily(
                    'cvmfs_' + metric, CVMFS_EXTENDED_ATTRIBUTES[metric], labels=['repo'])
            else:
                gauges[metric] = GaugeMetricFamily(
                    'cvmfs_' + metric, CVMFS_EXTENDED_ATTRIBUTES[metric], labels=['repo'])
        cached_bytes = GaugeMetricFamily('cvmfs_cached_bytes', 'CVMFS cached bytes', labels=['repo'])
        pinned_bytes = GaugeMetricFamily('cvmfs_pinned_bytes', 'CVMFS pinned bytes', labels=['repo'])
        quota = GaugeMetricFamily('cvmfs_total_cache_size_bytes', 'CVMFS configured cache size in bytes', labels=['repo'])
        hit_ratio = GaugeMetricFamily('cvmfs_cache_hit_ratio', 'CVMFS cache hit ratio', labels=['repo'])
        active_proxy = GaugeMetricFamily('cvmfs_active_proxy', 'CVMFS active proxy, 1 mean active', labels=['repo', 'host'])
        proxy_time = GaugeMetricFamily('cvmfs_proxy_time', 'CVMFS proxy time', labels=['repo', 'host'])
        cpu_user = CounterMetricFamily('cvmfs_cpu_user', 'CPU time used in userspace', labels=['repo'])
        cpu_system = CounterMetricFamily('cvmfs_cpu_system', 'CPU time used by the system', labels=['repo'])

        for repo in mounted_repos():
            log.debug('Collecting metrics for repo: %s', repo)
            for metric in CVMFS_EXTENDED_ATTRIBUTES:
                try:
                    value = xattr.getxattr('/cvmfs/' + repo, 'user.' + metric)
                    log.debug('Metric: %s, value: %s', metric, float(value))
                    gauges[metric].add_metric([repo], float(value))
                except Exception as e:
                    log.error('Error while collecting metric %s for repo %s: %s',
                              metric, repo, e)

            cache_out = exec_command(['cvmfs_talk', '-i', repo, 'cache', 'size'])[0].split(' ')
            log.debug('cache_out: %s', cache_out)
            cached_bytes.add_metric([repo], float(cache_out[5].lstrip('(')))
            pinned_bytes.add_metric([repo], float(cache_out[9].lstrip('(')))

            parameters = exec_command(['cvmfs_talk', '-i', repo, 'parameters'])
            for line in parameters:
                if 'CVMFS_QUOTA_LIMIT' in line:
                    # convert to bytes
                    quota.add_metric([repo], float(line.split('=')[1].split(' ')[0])*1024*1024)

            stats = exec_command(['cvmfs_config', 'stat', repo])
            log.debug('stats: %s', stats)
            hit_ratio.add_metric([repo], float(stats[1].split(' ')[13]))

            proxies = exec_command(['cvmfs_talk', '-i', repo, 'proxy', 'info'])
            log.debug('proxies: %s', proxies)
            groups = proxies[1].lstrip("Load-balance groups: '[0]").split('), ')
            active_proxy_str = proxies[-2].split(' ')[-1]
            log.debug('groups: %s', groups)
            log.debug('active_proxy: %s', active_proxy_str)

            for proxy in groups:
                match = re.match(r'(.*) \((.*), (.*)', proxy)
                url = match.group(1)
                host = match.group(2)
                time = match.group(3).rstrip(')')
                log.debug('match: url=%s host=%s time=%s', url, host, time)
                if(match.group(1) == active_proxy_str):
                    active_proxy.add_metric([repo, host], 1)
                else:
                    active_proxy.add_metric([repo, host], 0)
                proxy_time.add_metric([repo, host], convert_time(time))
            
            pid = int(xattr.getxattr('/cvmfs/' + repo, 'user.pid'))
            cpu_time = psutil.Process(pid).cpu_times()
            cpu_user.add_metric([repo], float(cpu_time.user))
            cpu_system.add_metric([repo], float(cpu_time.system))

        for gauge in gauges.values():
            yield gauge
        yield cached_bytes
        yield pinned_bytes
        yield quota
        yield hit_ratio
        yield active_proxy
        yield proxy_time
        yield cpu_user
        yield cpu_system
        log.debug('End of collection cycle')


class NoLoggingWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CVMFS exporter for Prometheus')
    log_levels = ['critical', 'error', 'warning', 'info', 'debug']
    parser.add_argument(
        '--port',
        type=int,
        default=9868,
        help='Collector http port, default is 9868')
    parser.add_argument("--verbose", help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = make_wsgi_app(CVMFSCollector())
    httpd = make_server('', args.port, app,
                        handler_class=NoLoggingWSGIRequestHandler)
    httpd.serve_forever()

