# Linux Mint & XFCE Do Not Disturb (DND) Setup Guide

To protect your deep writing sessions from banner notifications, sound alerts, and update popups, configure the native XFCE notification system.

---

## 1. Quick One-Click Toggle from System Tray
1. Look at your panel (bottom or top right near the clock).
2. Click on the **Notification Icon** (bell or conversation bubble icon).
3. Toggle the switch for **Do Not Disturb** to **ON**.
4. While enabled:
   - All visual popup alerts are suppressed.
   - All notification chimes are muted.
   - Notifications are silently queued in the log so you can review them after your writing session.

---

## 2. Setting a Dedicated Keyboard Shortcut (Optional)
To toggle Do Not Disturb instantly from your keyboard without touching the mouse:
1. Open **Settings** -> **Keyboard** -> **Application Shortcuts**.
2. Click **Add**.
3. In the Command field, enter:
   ```bash
   xfconf-query -c xfce4-notifyd -p /do-not-disturb -T
   ```
4. Click **OK**, then press your desired key combination (e.g., `Super + D` or `Ctrl + Alt + D`).

---

## 3. FocusWriter Fullscreen Deep Focus
When drafting deep prose in FocusWriter:
- Press **F11** to toggle full screen.
- Move mouse to edges to reveal menus, or stay in center for a pure, distraction-free page with word count targets and ambient typing sound effects.
