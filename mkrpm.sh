#!/bin/bash

# Build RPM for RHEL/CentOS
# eg. ./mkrpm_el.sh el7
dist=$1
[ -z "$dist" ] && echo "$0 {dist}" && exit 1

spectool -g -R cvmfs-exporter-$dist.spec
rpmbuild --define "dist .$dist" -ba cvmfs-exporter-$dist.spec
