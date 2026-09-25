Name:           ars-arcanum
Version:        1.6.1
Release:        1%{?dist}
Summary:        Sovereign 100% offline writing and speculative worldbuilding studio for fiction authors

License:        MIT
URL:            https://github.com/aryansinghnagar/Scriptorium
Source0:        https://github.com/aryansinghnagar/Scriptorium/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch

Requires:       bash >= 4.3
Requires:       python3 >= 3.10
Requires:       python3-gobject
Requires:       gtk3
Requires:       git >= 2.34
Requires:       pandoc >= 2.19
Requires:       jq
Requires:       zenity
Requires:       curl
Requires:       tar
Requires:       xz
Requires:       xdg-user-dirs
Requires:       libnotify

Recommends:     typst >= 0.11
Recommends:     focuswriter
Recommends:     libreoffice-writer
Recommends:     flatpak

Provides:       arcanum = %{version}-%{release}

%description
Ars Arcanum is an intuitive, sovereign, fail-safe Linux writing and
speculative worldbuilding studio. It provides distraction-free drafting,
OpenXML (.docx) bidirectional sync, multi-tier Git repository tracking,
deep worldbuilding simulation engines, automated concordance back-matter,
and publication-grade Typst PDF and EPUB compilation.

%prep
%autosetup -n Scriptorium-%{version}

%build
# No compiled artifacts — pure Python/Shell application

%install
rm -rf %{buildroot}

# Install application files into /usr/share/ars-arcanum
mkdir -p %{buildroot}%{_datadir}/ars-arcanum
cp -r scripts templates configs %{buildroot}%{_datadir}/ars-arcanum/

# Clean bytecode caches
find %{buildroot}%{_datadir}/ars-arcanum -type d -name '__pycache__' -prune -exec rm -rf {} +
find %{buildroot}%{_datadir}/ars-arcanum -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

# Ensure script permissions
chmod +x %{buildroot}%{_datadir}/ars-arcanum/scripts/*.sh
chmod +x %{buildroot}%{_datadir}/ars-arcanum/scripts/arcanum
chmod +x %{buildroot}%{_datadir}/ars-arcanum/scripts/ars-arcanum

# CLI entry points
mkdir -p %{buildroot}%{_bindir}
ln -sf %{_datadir}/ars-arcanum/scripts/arcanum %{buildroot}%{_bindir}/arcanum
ln -sf %{_datadir}/ars-arcanum/scripts/ars-arcanum %{buildroot}%{_bindir}/ars-arcanum

# Desktop launchers
mkdir -p %{buildroot}%{_datadir}/applications
for launcher in launchers/*.desktop; do
    if [ -f "$launcher" ]; then
        filename=$(basename "$launcher")
        sed "s|bash __PROJECT_ROOT__/scripts/arcanum|%{_bindir}/arcanum|g; s|bash __PROJECT_ROOT__/scripts/|%{_datadir}/ars-arcanum/scripts/|g; s|__PROJECT_ROOT__|%{_datadir}/ars-arcanum|g" \
            "$launcher" > "%{buildroot}%{_datadir}/applications/$filename"
    fi
done

# Systemd user units
mkdir -p %{buildroot}%{_userunitdir}
install -m 0644 configs/systemd/arcanum-backup.service %{buildroot}%{_userunitdir}/
install -m 0644 configs/systemd/arcanum-backup.timer %{buildroot}%{_userunitdir}/

%files
%license LICENSE
%doc README.md
%{_bindir}/arcanum
%{_bindir}/ars-arcanum
%{_datadir}/ars-arcanum
%{_datadir}/applications/*.desktop
%{_userunitdir}/arcanum-backup.service
%{_userunitdir}/arcanum-backup.timer

%changelog
* Mon Sep 21 2026 Aryan Singh Nagar <aryan@example.com> - 1.6.1-1
- Release version 1.6.1: Full architectural refactor, GPG backup encryption, and multi-distro packaging.
