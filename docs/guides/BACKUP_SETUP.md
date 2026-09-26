# Déjà Dup Automated Backup Guide (The 3-2-1 Rule)

Your writing represents years of intellectual effort. Ars Arcanum adheres to the **3-2-1 Backup Rule**:
- **3** copies of your data (Working disk, external USB drive, offsite/cloud).
- **2** different storage media types.
- **1** copy stored offsite or on a detached external drive.

---

## Step 1: Initial Backup Setup with Déjà Dup

1. Plug in your external USB hard drive or flash drive.
2. Open **Menu** -> Search for **Backups** (Déjà Dup).
3. Click on **Create My First Backup** (or the gear icon for Settings).

---

## Step 2: Configure Backup Locations

### Folders to Save
1. In the **Folders to save** tab, click `+` (Add).
2. Select your `~/Universes` and `~/Manuscripts` folders (or your entire Home directory `/home/<username>`).
3. Under **Folders to ignore**, ensure temporary build folders or caches are listed (e.g., `Downloads`, `Trash`, `04-Publishing`).

### Storage Location
1. In the **Storage location** tab:
   - Select **Local Folder** or **External Drive**.
   - Choose your connected USB drive as the destination folder.
   - *(Optional cloud alternative: Nextcloud / Google Drive / WebDAV if you use an encrypted cloud provider).*

---

## Step 3: Encryption & Schedule

1. **Enable Password Protection (Encryption)**:
   - When prompted during the first backup, choose **Password Protect Backup**.
   - Enter a strong passphrase and save it in a safe place (or password manager).
   - This ensures that if the USB drive is ever lost or stolen, no one can read your manuscripts.
2. **Set Automated Schedule**:
   - In the **Schedule** tab, set **Automatic backup** to **ON**.
   - Select **Weekly** (or **Daily** if you write every day).
   - Set **Keep backups** to **At least a year** or **Forever** (depending on drive space).

---

## Native Ars Arcanum Dual-Target Disaster Recovery Backups

In addition to system-level Déjà Dup backups, Ars Arcanum includes a native, standalone dual-target archive manager (`arcanum backup`) with SHA-256 integrity validation.

### 1. Configure Secondary Secure Destination (External / USB)
You can configure a persistent secondary replication target via CLI or the GTK Desktop Control Center:

```bash
# Set secondary backup destination to an external drive or USB stick:
arcanum backup-dest set /media/username/SecureUSB/ArsArcanumBackups

# View currently configured backup destination:
arcanum backup-dest get

# Clear secondary backup destination:
arcanum backup-dest clear
```

In the **GTK Control Center** (Tab 4: Snapshots & Backups), click **"📁 Set Secondary Backup Path..."** to select your connected external storage volume.

### 2. Creating Verified Dual-Target Archives
Whenever you run `arcanum backup <project>` or click **"📦 Create Verified Backup Archive"** in the Control Center:
1. A compressed, standalone `.tar.gz` archive is compiled and stored in the primary project backup directory (`~/Backups/` or `<project>/05-Backups/`).
2. An SHA-256 checksum manifest (`.sha256`) is computed and validated immediately.
3. If a secondary destination is configured and mounted, the verified archive and checksum are automatically replicated to the external drive.
4. If the external drive is unmounted or unplugged, the tool logs an advisory warning without failing your primary local backup.

---

## Step 4: Testing Restoration (Fire Drill)

A backup is only as good as its restore test. Once a month:
1. **Via Ars Arcanum Restore Engine**:
   ```bash
   arcanum restore /path/to/backup_archive.tar.gz
   ```
2. **Via Déjà Dup**:
   - Open **Backups**.
   - Click **Restore...**
   - Select a previous date and choose a single test file to restore to `/tmp`.
   - Verify that the file opens cleanly in Obsidian or novelWriter.
