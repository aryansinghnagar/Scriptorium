# Scriptorium — Finishing Touches (Linux-Host Only Manual)

> Location: project root (`Finishing_Touches.md`).
> Audience: you, on Linux Mint XFCE (primary) or Debian 13 XFCE (secondary).
> Purpose: finish the 5 items that cannot be verified from Windows: Typst compile,
> LeechBlock import, novelWriter project, full setup run, validators + first commit.
> Static work (sanitization, traps, NUL-safe listing, git fallback, Wayland detect,
> arch detect, XDG dir, `verify.sh`, `LICENSE`, `.gitattributes`) is already done
> and passes `bash -n` + `pandoc -t typst` on Windows via Git Bash.

Time budget: ~60–90 min total (setup run dominates). Do sections in order.
Stop and fix before proceeding if any ACCEPT gate fails.

Conventions in this guide:

- `~/Scriptorium` = wherever you cloned this repo on Linux (adjust paths).
- `~/Worlds` = runtime data created by `init_world.sh` (not in git).
- Commands assume `bash`. Copy-paste blocks as given.
- `[EXPECT]` = output you must see. `[ACCEPT]` = gate to pass.

---

## 0. Safety and rollback (2 min)

You have two Windows-side backups (do not delete until Linux gates pass):

- `.../Temp/opencode/scriptorium-backup-20260904` — pre-hardening baseline.
- `.../Temp/opencode/scriptorium-backup-pass3` — pre-pass-3 baseline.

On Linux, create a third backup before touching anything:

```bash
cd ~
cp -a ~/Scriptorium /tmp/Scriptorium-backup-$(date +%Y%m%d-%H%M%S)
ls -d /tmp/Scriptorium-backup-*
# [EXPECT] one timestamped directory
```

Rollback on Linux (if a section corrupts the repo):

```bash
rm -rf ~/Scriptorium
cp -a /tmp/Scriptorium-backup-<stamp> ~/Scriptorium
cd ~/Scriptorium && git status --short 2>/dev/null | head
```

Do not run `setup_scriptorium.sh` with uncommitted writing in `~/Worlds` —
it only installs packages and copies launchers, but `apt-get update` needs
sudo and network. Plug in power + Ethernet/Wi-Fi first.

---

## 1. Environment prep (5 min)

### 1.1 Confirm OS and arch

```bash
lsb_release -a 2>/dev/null || cat /etc/os-release
uname -m
# [EXPECT] Linux Mint 21.x/22.x XFCE or Debian 13; arch x86_64 (or aarch64)
echo $XDG_CURRENT_DESKTOP $DESKTOP_SESSION
which bash git python3 pandoc xdg-user-dir gio zenity notify-send
```

Record versions for the commit message later:

```bash
bash --version | head -1
git --version
python3 --version
pandoc --version | head -2
pandoc --list-output-formats | grep -i typst
# [EXPECT] a line reading exactly: typst
# If missing, your pandoc is <2.16 — upgrade via apt or leave the sed fallback
# in export_book.sh (it handles this automatically).
```

### 1.2 Install validators (needed for Section 2)

```bash
sudo apt-get update -y
sudo apt-get install -y shellcheck desktop-file-utils xdg-user-dirs
shellcheck --version
desktop-file-validate --version
# [EXPECT] both print versions, no errors
```

Leave Typst/novelWriter/Obsidian/Calibre to Section 5 (setup script installs them).

---

## 2. Static verification on Linux (10 min)

### 2.1 Canonical harness (must pass)

```bash
cd ~/Scriptorium
bash scripts/verify.sh 2>&1 | tee /tmp/verify.log
```

[EXPECT]:

```text
[1/7] bash -n syntax validation...
  OK scripts/backup_world.sh
  OK scripts/control_center.sh
  OK scripts/export_book.sh
  OK scripts/init_universe.sh
  OK scripts/init_world.sh
  OK scripts/restore_world.sh
  OK scripts/save_snapshot.sh
  OK scripts/scriptorium_doctor.sh
  OK scripts/setup_scriptorium.sh
  OK scripts/uninstall_scriptorium.sh
  OK scripts/verify.sh
  OK scripts/wordcount_report.sh
  OK scripts/world_doctor.sh
  OK scripts/scriptorium
[2/7] JSON & XML schema validation...
  OK leechblock JSON schema
  OK nwProject XML fileVersion 1.5
  OK Obsidian pre-configured plugin suite schema
[3/7] Pandoc Markdown->Typst smoke test...
  OK pandoc typst writer present
  OK pandoc conversion
[4/7] Typst compile smoke test (if installed)...
  OK typst compile
[5/7] Desktop launcher validation...
  OK desktop files
[6/7] Functional Universe, World lifecycle, diagnostics & recovery (sandboxed HOME)...
  OK init_universe (Universe directory + Universe Git repository)
  OK init_world (Multi-tier Universe, World & Manuscript Git repositories)
  OK export_book (exit 0)
  OK PDF + EPUB produced and verified non-empty
  OK multi-volume + tag stripping verified in EPUB
  OK world_doctor --json valid
  OK world_doctor functional run
  OK wordcount_report (markdown + json)
  OK save_snapshot (multi-tier Git snapshots recorded)
  OK backup_world (archive + sha256 created)
  OK restore_world (drill verified: archive -> wipe -> restore -> verify content)
  OK scriptorium_doctor diagnostics
  OK setup & uninstall --dry-run simulations
[7/7] Scriptorium CLI facade tests...
  OK scriptorium CLI entrypoint (with universe command)
ALL-CHECKS-PASS
```

[ACCEPT] `ALL-CHECKS-PASS` in `/tmp/verify.log`. If `[4/5]` says SKIP now,
that is normal — it must say OK after Section 5. Keep `/tmp/verify.log`
for the final commit message.

### 2.2 Shellcheck (warnings only, fix errors)

```bash
cd ~/Scriptorium
shellcheck -S warning scripts/*.sh 2>&1 | tee /tmp/shellcheck.log
echo "exit=$?"
```

[EXPECT] Zero `error` lines. Typical acceptable `warning`s (do not chase
unless trivial):

- `SC2312` on `... | head -n 1` (masked-field false positive) — leave.
- `SC2086` if ever reported on `select w in ...` — already quoted; leave.

If an `error` appears, fix the file, re-run `bash -n` + `verify.sh`,
and note the fix in `status.md` before continuing.

### 2.3 Function unit checks (D1/D2/D3 proof)

```bash
cd ~/Scriptorium
printf '%s' 'a:b[c]d?e@f' | tr -cd 'A-Za-z0-9_-' | cut -c1-64; echo
# [EXPECT] abcdef  (proves D1 dash-last fix; old pattern printed a:b[c]...)

printf '%s' '../etc' | tr -cd 'A-Za-z0-9_-' | cut -c1-64; echo
# [EXPECT] etc

bash -c '
source <(sed -n "/^safe_filename/,/^}/p" scripts/export_book.sh)
safe_filename "My Book! v2"; echo " expect My_Book_v2"
safe_filename "   "; echo " expect book"
'
```

[ACCEPT] All three match. If not, stop — your repo copy predates pass 3.

---

## 3. Typst typesetting verification (15 min, HIGH priority)

This validates `templates/typst/book_template.typ` Section M2/M3/M4 fixes:
`locate` → `context`, stray-par removal, front-matter `header:none` + body
`set page` + `counter(page).update(1)`, plus `chapter-title` compat alias.

### 3.1 Version and fonts

```bash
typst --version 2>/dev/null || echo "TYPST-MISSING (run Section 5 first)"
fc-list | grep -ci "libertine\|libertinus\|eb garamond\|alegreya"
typst fonts 2>/dev/null | grep -i "libertine\|libertinus\|garamond" | head
```

[EXPECT] After Section 5: Typst ≥0.11 (ideally ≥0.12), `fc-list` count ≥3,
`typst fonts` lists at least one serif. If Libertine is missing, setup
installed the Libertinus fallback — update
`resources/typography_and_fonts_guide.md` accordingly (one-line edit).

### 3.2 Compile the preview sample

```bash
cd ~/Scriptorium/templates/typst
typst compile preview_sample.typ /tmp/preview.pdf && echo TYPST-OK
ls -lh /tmp/preview.pdf
# [EXPECT] TYPST-OK, PDF >10 KB
xdg-open /tmp/preview.pdf &
```

Inspect visually (5 checks):

1. Half-title page, blank verso, full title page, copyright page — **no**
   headers or footers on any of them (M4 fix).
2. Dedication + epigraph page (present in `preview_sample.typ`) — also no
   header/footer, regardless of length.
3. Body pages: even pages center-header AUTHOR, odd pages center-header TITLE,
   page numbers centered in footer.
4. `= Chapter One` / `= Chapter Two` start on odd pages with centered
   small-caps-style titles and 1.5in top space.
5. `✦ ✦ ✦` scene breaks render centered.

[ACCEPT] All five. Keep `/tmp/preview.pdf` path for the final report.

### 3.3 If compile fails (two known failure modes, try in order)

**Failure A — `unknown variable: first` or `counter(page).get` type error:**

Your Typst predates `.first()` on arrays. Patch one file:

```bash
cd ~/Scriptorium
sed -i 's/counter(page).get().first()/counter(page).get().at(0)/g' templates/typst/book_template.typ
grep -n 'counter(page).get' templates/typst/book_template.typ
# [EXPECT] two lines with .at(0)
typst compile templates/typst/preview_sample.typ /tmp/preview.pdf && echo TYPST-OK-RETRY
```

**Failure B — `locate` deprecation as hard error on very new Typst:**

You should not see this (we already migrated to `context`), but if stderr
mentions `locate`, ensure you are on the pass-3 template:

```bash
grep -c 'locate(loc' templates/typst/book_template.typ
# [EXPECT] 0
grep -c 'header: context' templates/typst/book_template.typ
# [EXPECT] 1
```

If both retries fail, paste full `typst compile` stderr + `typst --version`
into `status.md` under `blocked` and stop — do not invent Typst syntax.

### 3.4 Pandoc bridge check (M1 path used by `export_book.sh`)

```bash
printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown -t typst
# [EXPECT] first line "= Ch1", emphasis as #emph[world]
```

This is the exact code path `export_book.sh:193-201` prefers. The `sed`
fallback below it is only for pandoc without a Typst writer.

---

## 4. End-to-end pipeline: init → export → snapshot (20 min, HIGH)

### 4.1 Create a test world

```bash
cd ~/Scriptorium
bash scripts/init_world.sh
# GUI: enter TestWorld  (or CLI: type TestWorld at prompt)
ls ~/Worlds/TestWorld
# [EXPECT] 00-World-Bible 01-Manuscript 02-Maps 03-Art 04-Publishing 05-Backups .git .gitignore
ls ~/Worlds/TestWorld/00-World-Bible | head
# [EXPECT] includes Characters/ AND .obsidian-recommended-plugins.md (H1 dotfile proof)
cat ~/Worlds/TestWorld/.gitignore
```

Try the traversal guard (must be rejected or sanitized):

```bash
printf '../evil\n' | bash scripts/init_world.sh || true
ls -d ~/evil ~/Worlds/evil 2>/dev/null && echo "FAIL-TRAVERSAL" || echo "TRAVERSAL-BLOCKED"
# [EXPECT] TRAVERSAL-BLOCKED (name sanitizes to "evil" under ~/Worlds, or aborts)
# If it created ~/Worlds/evil, delete it: rm -rf ~/Worlds/evil
```

### 4.2 Export PDF + EPUB

```bash
bash scripts/export_book.sh ~/Worlds/TestWorld
ls -lh ~/Worlds/TestWorld/04-Publishing/
# [EXPECT] one .pdf (if Typst installed) + one .epub (if Pandoc installed),
# stem derived from title, e.g. TestWorld.pdf / TestWorld.epub
# Re-run to prove D3 collision guard:
bash scripts/export_book.sh ~/Worlds/TestWorld
ls ~/Worlds/TestWorld/04-Publishing/ | sort
# [EXPECT] second run adds *_YYYYMMDD-HHMMSS.pdf/.epub instead of overwriting
```

Open the PDF, repeat the 5 visual checks from 3.2. Open the EPUB in Calibre
(`calibre ~/Worlds/TestWorld/04-Publishing/*.epub &`) and confirm TOC depth 2.

### 4.3 Snapshot (spaces + identity guards)

```bash
mkdir -p ~/Worlds/"Space Probe"
echo "hello" > ~/Worlds/"Space Probe"/note.md
bash scripts/save_snapshot.sh
# GUI: pick a world from the list (names with spaces must appear intact).
# CLI (no DISPLAY): use the numbered select menu.
cd ~/Worlds/TestWorld && git log --oneline -3
# [EXPECT] at least "Initial Scriptorium scaffolding for world: TestWorld"
echo "edit" >> ~/Worlds/TestWorld/01-Manuscript/Book-01/01_Act_I/01_Chapter_01.md
bash ~/Scriptorium/scripts/save_snapshot.sh
cd ~/Worlds/TestWorld && git log --oneline -3
# [EXPECT] new Snapshot: entry on top, even without global git identity
# (fallback user Scriptorium <scriptorium@localhost> is used — check with git log --format=%an\ %ae -1)
```

[ACCEPT] All three scripts run without `set -e` aborts, spaces survive,
identity fallback works. Save `git log` excerpts for the final report.

---

## 5. Full setup run (25 min, HIGH — only on a disposable Mint/VM first)

> Warning: installs system packages + Flatpaks (~1–2 GB). Snapshot the VM
> or use `apt-get --dry-run` first if cautious.

### 5.1 Dry run (optional but recommended)

```bash
cd ~/Scriptorium
sudo apt-get update -y
sudo apt-get install --dry-run -y git zenity xdg-user-dirs flatpak pandoc focuswriter 2>&1 | tail -5
```

### 5.2 Live run

```bash
cd ~/Scriptorium
sudo bash scripts/setup_scriptorium.sh 2>&1 | tee /tmp/setup.log
tail -15 /tmp/setup.log
# [EXPECT] ends with [SUCCESS] Scriptorium Writing Setup Installed Successfully!
```

Verify each layer:

```bash
typst --version && pandoc --version | head -1
flatpak list --system 2>/dev/null | grep -Ei 'obsidian|novelwriter|calibre'
flatpak list --user 2>/dev/null | grep -Ei 'obsidian|novelwriter|calibre'
# [EXPECT] all three IDs in system OR user scope (fallback in 4.x is intentional)
echo $DESKTOP_DIR; xdg-user-dir DESKTOP
ls "$(xdg-user-dir DESKTOP)" | grep -i "World\|Export\|Snapshot"
ls ~/.local/share/applications/ | grep -i "world\|export\|snapshot"
```

Font check (D8b — names drift across releases):

```bash
apt-cache policy fonts-linuxlibertine fonts-libertinus fonts-ebgaramond fonts-alegreya fonts-sil-charis fonts-sil-gentiumplus fonts-bitter fonts-cmu 2>&1 | grep -E 'Candidate|Unable'
fc-list | grep -ci "libertine\|libertinus"
```

- If `fonts-linuxlibertine` shows `Unable to locate` but `fonts-libertinus`
  has a Candidate, the setup fallback already handled it. Record the
  substitution in `resources/software_catalog.md` + `resources/typography_and_fonts_guide.md`.
- If `fonts-bitter` is missing on your release, same procedure (warn-only is
  by design; body falls back to DejaVu Serif).

[ACCEPT] `/tmp/setup.log` ends SUCCESS, launchers on Desktop + applications
dir, `typst` + `pandoc` print versions. Keep the log.

---

## 6. LeechBlock NG import (10 min, HIGH — manual by nature)

LeechBlock's export format is version-specific and undocumented for stable
scripting (verified against proginosko.com docs 2026-09-04: times `0900-1300`
and bare domains are correct, but the JSON envelope is not a portable import).
Treat the repo file as a **specification**, not a guaranteed import.

### 6.1 Attempt direct import

1. Firefox → Add-ons → LeechBlock NG → Options. Note the version number.
2. General tab → Export/Import → Import → select
   `~/Scriptorium/configs/leechblock_scriptorium_rules.json`.
3. Outcome A (success): Block Set appears named `Scriptorium Focus Block`,
   sites list matches, times `0900-1300,1400-1700`, days all selected.
   Test at a writing hour (or temporarily set a 1-min test window):
   `youtube.com` shows the block page (`wikipedia.org/wiki/Special:Random`
   per our `blockPage`).
4. Outcome B (import error / empty set): do 6.2, do not force the JSON.

### 6.2 Manual recreation (fallback, 5 min)

1. In LeechBlock Options → Block Set 1: name `Scriptorium Focus Block`,
   paste one domain per line from the JSON `sites` array **without**
   `*` wildcards or protocol (docs: `youtube.com`, not `*youtube.com*`),
   times `0900-1300,1400-1700`, select all days, block page
   `https://en.wikipedia.org/wiki/Special:Random`.
2. Save, then Export to `/tmp/leechblock-working-export.txt`.
3. Diff and replace:
```bash
diff -u ~/Scriptorium/configs/leechblock_scriptorium_rules.json /tmp/leechblock-working-export.txt | head -60
cp /tmp/leechblock-working-export.txt ~/Scriptorium/configs/leechblock_scriptorium_rules.json
# Or, if the working export is .txt/plain, save it alongside and update README's import path.
```
4. Re-import the replaced file on a second Firefox profile to prove round-trip.

[ACCEPT] Either Outcome A verified with a live block, or Outcome B file
replaced + round-trip import passes. Record LeechBlock version + outcome
in `status.md`.

---

## 7. novelWriter real project (10 min, HIGH — intentional placeholder)

`templates/manuscript/nwProject.nwx` is a documented placeholder (real format
is `<novelWriterXML fileVersion="1.5">` + `content/*.nwd` + `meta/` + `ToC.txt`).
Do not hand-edit XML to look real — either keep the placeholder or generate
a real project. Steps for the real-project option:

```bash
novelWriter --version
# GUI:
# 1. novelWriter → New Project → ~/Worlds/TestWorld/01-Manuscript-Real/
# 2. Add one Novel root → one Chapter → one Document, type one sentence, save, quit.
ls ~/Worlds/TestWorld/01-Manuscript-Real/
# [EXPECT] nwProject.nwx + content/ + meta/ + ToC.txt
head -5 ~/Worlds/TestWorld/01-Manuscript-Real/nwProject.nwx
# [EXPECT] <novelWriterXML ... fileVersion="1.5" ...>, NOT <novelWriterRoot>
```

Decision:

- **Option A (keep, recommended):** leave the placeholder. Exporter reads
  `Book-01/*/*.md` directly, so `.nwx` is optional. No change needed.
- **Option B (replace):** copy the generated `nwProject.nwx` (only the file,
  not `content/`) into `templates/manuscript/nwProject.nwx`, commit with
  message `docs: real nwProject skeleton from novelWriter <version>`.
  Update `tasks.md` line for `nwProject.nwx` to the real version.

[ACCEPT] Explicit A/B recorded in `decisions.md` or commit message. Do not
ship a half-edited XML that opens neither here nor there.

---

## 8. Launchers, exec bits, validators (5 min)

```bash
cd ~/Scriptorium
git update-index --chmod=+x scripts/*.sh
chmod +x scripts/*.sh
desktop-file-validate launchers/*.desktop && echo DESKTOP-OK
grep -H '^TryExec=bash$' launchers/*.desktop
# [EXPECT] three TryExec lines, validator clean
gio set "$(xdg-user-dir DESKTOP)"/*.desktop metadata::trusted true 2>/dev/null || \
  echo "gio trust skipped (Nemo/Nautilus version — launch once via right-click Allow Launching)"
# Double-click each launcher: New World Creator, Export Book, Save Snapshot.
# [EXPECT] Zenity dialogs appear, no terminal window.
```

---

## 9. First commit (5 min)

```bash
cd ~/Scriptorium
cat .gitattributes
cat LICENSE | head -3
# [EXPECT] LF rules present, MIT header present
git status --short | head -30
git add -A
git commit -m "docs: add Finishing_Touches manual + verify Linux gates

Verify: $(bash scripts/verify.sh 2>&1 | tail -1)
Typst: $(typst --version 2>/dev/null || echo missing)
Pandoc: $(pandoc --version 2>/dev/null | head -1)
LeechBlock: <version + import outcome A/B>
novelWriter: <version + placeholder decision A/B>"
git log --oneline -3
git status --short
# [EXPECT] clean tree after commit
```

If `git commit` complains about identity, set it once (this is the human's
identity, unlike the ephemeral `Scriptorium@localhost` used inside worlds):

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

Do not push until you have created the GitHub repo and replaced
`<your-username>` in `README.md:44`.

---

## 10. Typography and backup drills (10 min, recurring)

```bash
# Fonts visible to both stacks?
fc-list | grep -i "libertine\|garamond\|alegreya" | head
typst fonts | grep -i "libertine\|libertinus\|garamond\|alegreya" | head
# If Typst misses a font that fc-list has, run: fc-cache -f -v
```

Déjà Dup fire drill (monthly, per `configs/deja_dup_backup_guide.md`):

1. Backups → Folders to save `~/Worlds`, destination USB, encryption ON,
   schedule Weekly.
2. Restore one file to `/tmp` and open it in Obsidian/novelWriter.
3. Record date + result in `status.md` recurring queue.

---

## 11. Final acceptance checklist (copy into PR or `status.md`)

- [ ] `bash scripts/verify.sh` → `ALL-CHECKS-PASS` (`/tmp/verify.log` kept)
- [ ] `shellcheck -S warning scripts/*.sh` → zero errors (`/tmp/shellcheck.log`)
- [ ] `typst compile preview_sample.typ` → PDF passes 5 visual checks (`/tmp/preview.pdf`)
- [ ] `init → export → snapshot` on `TestWorld` passes, dotfile present, collision guard seen, spaces + identity fallback seen
- [ ] `setup_scriptorium.sh` → SUCCESS (`/tmp/setup.log`), apps + launchers present
- [ ] LeechBlock import outcome A or B recorded + version noted
- [ ] novelWriter decision A or B recorded + version noted
- [ ] `desktop-file-validate` clean, launchers double-click to Zenity
- [ ] First commit clean (`git status` empty), logs referenced in message
- [ ] Rollback backups deletable only after all boxes ticked

---

## Appendix A. Command cheat sheet (one block)

```bash
cd ~/Scriptorium
bash scripts/verify.sh | tee /tmp/verify.log
shellcheck -S warning scripts/*.sh | tee /tmp/shellcheck.log
(cd templates/typst && typst compile preview_sample.typ /tmp/preview.pdf && echo TYPST-OK)
bash scripts/init_world.sh
bash scripts/export_book.sh ~/Worlds/TestWorld; ls -lh ~/Worlds/TestWorld/04-Publishing/
bash scripts/save_snapshot.sh; (cd ~/Worlds/TestWorld && git log --oneline -3)
sudo bash scripts/setup_scriptorium.sh | tee /tmp/setup.log
desktop-file-validate launchers/*.desktop && echo DESKTOP-OK
```

## Appendix B. Troubleshooting (symptom → fix, no loops)

| Symptom | Fix (one shot each) |
|---|---|
| `typst: command not found` | Run Section 5; check `ls -l /usr/local/bin/typst`; ARM needs `aarch64` build (auto) or `cargo install --locked typst-cli`. |
| `.first()` error in Typst | Apply 3.3 Failure A (`sed` to `.at(0)`), recompile once. |
| Front-matter headers appear | Confirm template has `header:none` front + body `set page` + `counter.update(1)`; re-copy template to `04-Publishing/typst-template/`. |
| `pandoc: Unknown output format typst` | Upgrade pandoc (need ≥2.16); exporter falls back to `sed` automatically. |
| LeechBlock import empty/error | Do 6.2 manual recreate; replace JSON with working export. |
| novelWriter won't open `nwProject.nwx` | Expected (placeholder). Use New Project flow (Section 7). |
| `flatpak install` password loop | Use `--user` fallback (already in script); check `flatpak remotes`. |
| `gio set` deprecation warning | Right-click launcher → Allow Launching (Nemo 6+). |
| `apt` font `Unable to locate` | Note substitution, continue (warn-only by design). |
| `git commit` identity error (repo) | Set user.name/email once (Section 9). Worlds use ephemeral fallback already. |

## Appendix C. What NOT to do

- Do not hand-write a fake `<novelWriterXML>` — generate it or keep the placeholder.
- Do not force the LeechBlock JSON to import by guessing keys — recreate via GUI.
- Do not re-run setup in a loop on font errors — one fallback pass is enough.
- Do not commit `~/Worlds/*`, `*.pdf`, `*.epub`, or `/tmp/*.log` — worlds are runtime data; logs stay in `/tmp` and are referenced by name in the commit message.
