# cvmfs-exporter
This is a prometheus exporter to gather the stats of CVMFS clients. 

## About CVMFS
The CernVM File System provides a scalable, reliable and low-maintenance software distribution service. It was developed to assist High Energy Physics (HEP) collaborations to deploy software on the worldwide-distributed computing infrastructure used to run data processing applications. CernVM-FS is implemented as a POSIX read-only file system in user space (a FUSE module). Files and directories are hosted on standard web servers and mounted in the universal namespace /cvmfs.

[CVMFS documentation](https://cernvm.cern.ch/fs/)

## Requirements
* prometheus_client
* psutil
* pyxattr

The dependencies are available with RPMs in EPEL or can be installed with `pip`.

## Usage
```
usage: cvmfs-exporter [-h] [--port PORT] [--verbose]

CVMFS exporter for Prometheus

optional arguments:
  -h, --help   show this help message and exit
  --port PORT  Collector http port, default is 9868
  --verbose    increase output verbosity
```

## Metrics
Metrics are prefixed with cvmfs_. Tags for each metric are per repo and proxy (as needed). 

### Example
```
# HELP cvmfs_expires Shows the remaining life time of the mounted root file catalog in minutes.
# TYPE cvmfs_expires gauge
cvmfs_expires{repo="soft.computecanada.ca"} 3.0
# HELP cvmfs_inode_max Shows the highest possible inode with the current set of loaded catalogs.
# TYPE cvmfs_inode_max gauge
cvmfs_inode_max{repo="soft.computecanada.ca"} 3.6235641e+07
# HELP cvmfs_maxfd Shows the maximum number of file descriptors available to file system clients.
# TYPE cvmfs_maxfd gauge
cvmfs_maxfd{repo="soft.computecanada.ca"} 130560.0
# HELP cvmfs_ncleanup24 Shows the number of cache cleanups in the last 24 hours.
# TYPE cvmfs_ncleanup24 gauge
cvmfs_ncleanup24{repo="soft.computecanada.ca"} 0.0
# HELP cvmfs_nclg Shows the number of currently loaded nested catalogs.
# TYPE cvmfs_nclg gauge
cvmfs_nclg{repo="soft.computecanada.ca"} 38.0
# HELP cvmfs_ndiropen Shows the overall number of opened directories.
# TYPE cvmfs_ndiropen gauge
cvmfs_ndiropen{repo="soft.computecanada.ca"} 4.416883e+06
# HELP cvmfs_ndownload_total Shows the overall number of downloaded files since mounting.
# TYPE cvmfs_ndownload_total counter
cvmfs_ndownload_total{repo="soft.computecanada.ca"} 17038.0
# HELP cvmfs_nioerr_total Shows the total number of I/O errors encoutered since mounting.
# TYPE cvmfs_nioerr_total counter
cvmfs_nioerr_total{repo="soft.computecanada.ca"} 7.0
# HELP cvmfs_nopen_total Shows the overall number of open() calls since mounting.
# TYPE cvmfs_nopen_total counter
cvmfs_nopen_total{repo="soft.computecanada.ca"} 8.370649e+06
# HELP cvmfs_revision Shows the file catalog revision of the mounted root catalog, an auto-increment counter increased on every repository publish.
# TYPE cvmfs_revision gauge
cvmfs_revision{repo="soft.computecanada.ca"} 5953.0
# HELP cvmfs_rx_total Shows the overall amount of downloaded kilobytes.
# TYPE cvmfs_rx_total counter
cvmfs_rx_total{repo="soft.computecanada.ca"} 1.508687e+06
# HELP cvmfs_speed Shows the average download speed.
# TYPE cvmfs_speed gauge
cvmfs_speed{repo="soft.computecanada.ca"} 1039.0
# HELP cvmfs_timeout Shows the timeout for proxied connections in seconds.
# TYPE cvmfs_timeout gauge
cvmfs_timeout{repo="soft.computecanada.ca"} 5.0
# HELP cvmfs_timeout_direct Shows the timeout for direct connections in seconds.
# TYPE cvmfs_timeout_direct gauge
cvmfs_timeout_direct{repo="soft.computecanada.ca"} 10.0
# HELP cvmfs_uptime_total Shows the time passed since mounting in minutes.
# TYPE cvmfs_uptime_total counter
cvmfs_uptime_total{repo="soft.computecanada.ca"} 33089.0
# HELP cvmfs_usedfd Shows the number of file descriptors currently issued to file system clients.
# TYPE cvmfs_usedfd gauge
cvmfs_usedfd{repo="soft.computecanada.ca"} 3341.0
# HELP cvmfs_cached_bytes CVMFS cached bytes
# TYPE cvmfs_cached_bytes gauge
cvmfs_cached_bytes{repo="soft.computecanada.ca"} 1.1337860946e+010
# HELP cvmfs_pinned_bytes CVMFS pinned bytes
# TYPE cvmfs_pinned_bytes gauge
cvmfs_pinned_bytes{repo="soft.computecanada.ca"} 2.33975808e+08
# HELP cvmfs_total_cache_size_bytes CVMFS configured cache size in bytes
# TYPE cvmfs_total_cache_size_bytes gauge
cvmfs_total_cache_size_bytes{repo="soft.computecanada.ca"} 4.6661632e+010
# HELP cvmfs_cache_hit_ratio CVMFS cache hit ratio
# TYPE cvmfs_cache_hit_ratio gauge
cvmfs_cache_hit_ratio{repo="soft.computecanada.ca"} 99.806
# HELP cvmfs_active_proxy CVMFS active proxy, 1 mean active
# TYPE cvmfs_active_proxy gauge
cvmfs_active_proxy{host="proxy1",repo="soft.computecanada.ca"} 1.0
cvmfs_active_proxy{host="proxy2",repo="soft.computecanada.ca"} 0.0
cvmfs_active_proxy{host="proxy3",repo="soft.computecanada.ca"} 0.0
# HELP cvmfs_proxy_time CVMFS proxy time
# TYPE cvmfs_proxy_time gauge
cvmfs_proxy_time{host="proxy1",repo="soft.computecanada.ca"} 420.0
cvmfs_proxy_time{host="proxy2",repo="soft.computecanada.ca"} -673200.0
cvmfs_proxy_time{host="proxy3",repo="soft.computecanada.ca"} -673200.0
# HELP cvmfs_cpu_user_total CPU time used in userspace
# TYPE cvmfs_cpu_user_total counter
cvmfs_cpu_user_total{repo="soft.computecanada.ca"} 757.77
# HELP cvmfs_cpu_system_total CPU time used by the system
# TYPE cvmfs_cpu_system_total counter
cvmfs_cpu_system_total{repo="soft.computecanada.ca"} 2845.21
``` 