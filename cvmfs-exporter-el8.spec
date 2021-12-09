Name:	  cvmfs-exporter
Version:  0.0.2
%global gittag 0.0.2
Release:  1%{?dist}
Summary:  Prometheus exporter for cvmfs client stats

License:  Apache License 2.0
URL:      https://github.com/guilbaults/cvmfs-exporter
Source0:  https://github.com/guilbaults/%{name}/archive/v%{gittag}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:	systemd
Requires:       python36
Requires:       python3-prometheus_client
Requires:       python3-pyxattr
Requires:       python3-psutil

%description
Prometheus exporter for cvmfs client stats

%prep
%autosetup -n %{name}-%{gittag}
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_unitdir}

sed -i -e '1i#!/usr/bin/python3.6' cvmfs-exporter.py
install -m 0755 %{name}.py %{buildroot}/%{_bindir}/%{name}
install -m 0644 cvmfs-exporter.service %{buildroot}/%{_unitdir}/cvmfs-exporter.service

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}/%{name}
%{_unitdir}/cvmfs-exporter.service

%changelog
* Thu Dec 9 2021 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.2-1
- Using port 9868, reserved in prometheus wiki
* Thu Dec 9 2021 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.1-1
- Initial release
