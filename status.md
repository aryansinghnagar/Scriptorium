# Operational Status & Momentum Queues: Scriptorium

## Real-Time State
- **Active Phase**: Docs refresh + declutter (legacy plans archived, root `.gitignore`, `Finishing_Touches.md`); pending live Linux verification
- **Status**: All resources, installation scripts, world scaffolding templates, Obsidian Vault templates, Typst book templates, desktop launchers, LeechBlock rules, and documentation guides created. Audit fixes: Typst import, dotfile copy, filename sanitization (+`tr` range fix), Typst escaping/newlines, collision-safe stems, temp trap, NUL-safe world listing, git identity fallback, Wayland GUI detect, Typst context migration, arch-aware setup, tolerant fonts, Flatpak fallback, XDG desktop dir. `verify.sh` passes static stages on Windows/Git Bash (Typst compile skips without Typst).
- **Last Action**: Archived `scriptorium_plan.*` to `docs/archive/`, added root `.gitignore`, refreshed README/project/knowledge/decisions, synced plan/tasks.

## Active Momentum Queues

### `now` (Active In-Flight Focus)
- [ ] Live-verify on Linux Mint XFCE per `Finishing_Touches.md`: `shellcheck`, `typst compile templates/typst/preview_sample.typ`, LeechBlock import test, novelWriter new-project test, full setup run (`bash -n` + Pandoc stages already green via `scripts/verify.sh`).

### `next` (Immediately Ready to Execute)
- [ ] User deployment on Linux Mint XFCE / Debian system.

### `blocked`
- None.

### `improve`
- [ ] Add pre-compiled binary bundling if offline installation media is requested.
- [ ] Zenity dialogs already present; consider Yad wizard polish only if user feedback requests it.

### `recurring`
- [ ] Regular template enhancements based on writing workflow feedback.
- [ ] Validate script syntax and template correctness (`bash -n`, `typst compile`, JSON/XML parse).
