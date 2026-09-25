# Flathub Upstream Packaging & AppStream Specification Guide
`flatpak/org.arsarcanum.ArsArcanum.metainfo.xml` & `org.arsarcanum.ArsArcanum.yaml`

---

## 1. Overview & Upstream Architecture

Ars Arcanum distributes as a sandboxed Freedesktop Flatpak targeting Flathub and local Linux installations. Production distribution requires strict conformance with the **Freedesktop AppStream 0.16+ Specification**, **Open Age Rating Service (OARS 1.1)**, and reproducible sandbox finishes.

---

## 2. Component Specifications

### 2.1 AppStream Metainfo XML (`flatpak/org.arsarcanum.ArsArcanum.metainfo.xml`)

| Property | Value | Notes |
| :--- | :--- | :--- |
| **Component ID** | `org.arsarcanum.ArsArcanum` | Unique reverse-DNS identifier |
| **Type** | `desktop-application` | Standard GUI application specification |
| **Metadata License** | `CC0-1.0` | Required by Flathub / Freedesktop standards |
| **Project License** | `GPL-3.0-or-later` | Copyleft software license |
| **Launchable ID** | `arcanum-control-center.desktop` | Matches `.desktop` file installed in `/app/share/applications/` |
| **Content Rating** | `oars-1.1` | Clean rating for general authoring software |
| **Provides** | `arcanum`, `ars-arcanum` | Registered command-line binaries |

### 2.2 Flatpak Manifest (`org.arsarcanum.ArsArcanum.yaml`)

The manifest builds Ars Arcanum using `org.gnome.Platform` and `org.gnome.Sdk` runtime version `46`.

Key Build Directives:
```yaml
app-id: org.arsarcanum.ArsArcanum
runtime: org.gnome.Platform
runtime-version: '46'
sdk: org.gnome.Sdk
command: arcanum
finish-args:
  - --share=ipc
  - --socket=fallback-x11
  - --socket=wayland
  - --filesystem=home
  - --filesystem=xdg-desktop:ro
  - --talk-name=org.freedesktop.Notifications
  - --talk-name=org.freedesktop.Flatpak
```

Metainfo Installation Step:
```bash
cp flatpak/org.arsarcanum.ArsArcanum.metainfo.xml /app/share/metainfo/
```

---

## 3. Building & Validating Locally

To build and test the Flatpak bundle locally using `flatpak-builder`:

```bash
# 1. Install Flatpak GNOME 46 runtime and SDK
flatpak install flathub org.gnome.Platform//46 org.gnome.Sdk//46

# 2. Build in local sandbox directory
flatpak-builder --user --install --force-clean build-dir org.arsarcanum.ArsArcanum.yaml

# 3. Validate AppStream XML metainfo
appstream-util validate-relax flatpak/org.arsarcanum.ArsArcanum.metainfo.xml
# or:
appstreamcli validate flatpak/org.arsarcanum.ArsArcanum.metainfo.xml

# 4. Launch Flatpak container
flatpak run org.arsarcanum.ArsArcanum gui
```

---

## 4. Flathub Submission Checklist

- [x] Unique reverse-DNS App ID: `org.arsarcanum.ArsArcanum`.
- [x] Standard `CC0-1.0` metadata license.
- [x] OARS 1.1 content rating declared.
- [x] High-resolution screenshots hosted on reliable CDN / GitHub raw with HTTPS URLs.
- [x] Semver release tags with HTML `<description>` changelog notes.
- [x] Validated XML syntax with `tests/test_flathub_upstream.py`.
