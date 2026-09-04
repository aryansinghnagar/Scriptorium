# Déjà Dup Automated Backup Guide (The 3-2-1 Rule)

Your writing represents years of intellectual effort. Scriptorium adheres to the **3-2-1 Backup Rule**:
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
2. Select your `~/Worlds` folder (or your entire Home directory `/home/<username>`).
3. Under **Folders to ignore**, ensure temporary build folders or caches are listed (e.g., `Downloads`, `Trash`).

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

## Step 4: Testing Restoration (Fire Drill)

A backup is only as good as its restore test. Once a month:
1. Open **Backups**.
2. Click **Restore...**
3. Select a previous date and choose a single test file to restore to `/tmp`.
4. Verify that the file opens cleanly in Obsidian or novelWriter.
