Name:           awips2-alr-qpid-config
Version:        0.32
Release:        2%{?dist}
Summary:        Java implementation of Apache Qpid Broker
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Source:         qpid-broker-%{version}-bin.tar.gz
Patch0:         awips.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Provides:       awips2-alr-qpid-config
Requires:       awips2-qpid-java-broker
Packager: %{_build_site}

%description
ALR special qpid config for SJU hydro processing

%prep

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/awips2/qpid/edex-alr/config
install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/alr/config.json.alr %{buildroot}/awips2/qpid
install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/alr/edex-alr/config/edex-alr.json %{buildroot}/awips2/qpid/edex-alr/config

%post
cp /awips2/qpid/config.json.alr /awips2/qpid/config.json

%files
%defattr(-,awips,awips,-)
/awips2/qpid

%changelog
* Thu Aug 27 2015 Sean Webb <Sean.Webb@noaa.gov>
- Initial build.
