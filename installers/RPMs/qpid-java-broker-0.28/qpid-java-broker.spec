Name:           awips2-qpid-java-broker
Version:        0.28
Release:        1%{?dist}
Summary:        Java implementation of Apache Qpid Broker
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Source:         qpid-java-broker-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  ant >= 1.6.5
BuildRequires:  ant-nodeps >= 1.6.5
BuildRequires:  java-devel >= 1.6.0
BuildRequires:  ant-trax >= 1.6.5

%description
Java implementation of Apache Qpid Broker.

%prep
%setup -n qpid-java-broker-%{version}

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/awips2/qpid/bin
install -pm 755 bin/* %{buildroot}/awips2/qpid/bin

mkdir -p %{buildroot}/awips2/qpid/etc
install -pm 755 etc/* %{buildroot}/awips2/qpid/etc

mkdir -p %{buildroot}/awips2/qpid/lib
install -pm 755 lib/*.jar %{buildroot}/awips2/qpid/lib

mkdir -p %{buildroot}/awips2/qpid/lib/plugins
install -pm 755 lib/plugins/* %{buildroot}/awips2/qpid/lib/plugins

install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/etc/* %{buildroot}/awips2/qpid/etc

# install the wrapper script
install -pm 755 %{_patchdir}/qpid-java-broker-%{version}/wrapper/qpid-wrapper %{buildroot}/awips2/qpid/bin

# add the yajsw distribution
tar -xf %{_patchdir}/qpid-java-broker-%{version}/wrapper/yajsw-distribution.tar -C %{buildroot}/awips2/qpid/bin

# service script
mkdir -p %{buildroot}/etc/init.d
install -pm 755 %{_patchdir}/qpid-java-broker-%{version}/wrapper/qpidd %{buildroot}/etc/init.d

# logs directory
mkdir -p %{buildroot}/awips2/qpid/log

%clean
rm -rf %{buildroot}

%files
%defattr(-,awips,fxalpha,-)
/awips2/qpid
%defattr(755,root,root,755)
/etc/init.d/qpidd

%changelog
* Thu Jul 31 2014 Ron Anderson <ron.anderson@raytheon.com> - 0.28-1
- Initial build.
