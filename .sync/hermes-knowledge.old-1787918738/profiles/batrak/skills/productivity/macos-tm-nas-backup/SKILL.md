---
name: macos-tm-nas-backup
description: "Set up automated macOS Time Machine backups to a Synology NAS via LaunchAgent. Covers the safe tmutil pattern, the Finder-once-mount trick, and the mount_smbfs space-in-share-name pitfall."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [macos, time-machine, nas, synology, backup, launchagent, igor-infra]
    related_skills: [macos-maintenance, igor-proxy-network]
---

# Automated Time Machine → NAS Backup (macOS)

Schedule a daily Mac backup to a Synology NAS without manual intervention. Built and verified for Igor's DS720+ (2026-08-21).

## Architecture

- Backup target: Synology NAS SMB share (Time Machine over SMB — native Synology feature).
- Trigger: a user LaunchAgent (`~/Library/LaunchAgents/com.igor.nas-tm-backup.plist`) firing daily at 03:00 via `StartCalendarInterval`.
- The worker script (`~/nas-tools/nas-tm-backup.sh`) checks NAS reachability, confirms the share is mounted, attaches the TM destination if needed, then runs `tmutil startbackup --block`.

## SAFETY — what is safe vs what will bite you

- **`tmutil setdestination <mount>` does NOT delete existing backups.** It only attaches the disk as a destination. Re-running it is idempotent and safe.
- **Do NOT try to mount the share from the script via `mount_smbfs`.** Two reasons it fails:
  1. `mount_smbfs` cannot read the SMB password from the macOS Keychain, so you'd have to hardcode credentials in plaintext — reject that.
  2. If the share name contains a space (e.g. Igor's real share is literally `Time Mashine` — a typo, but that's the name), `mount_smbfs //user@host/Time Mashine /mnt` dies with `URL parsing failed`. You'd have to URL-encode the space as `%20`, and even then the password problem remains.
- **Correct mount approach:** mount ONCE through Finder (Go → Connect to Server → `smb://ds720.local` → pick the share → check "Remember this password in my keychain"). macOS keeps it mounted across logins and TM sees `/Volumes/<share>`. The script then only verifies + backs up.

## Key facts about Igor's NAS (verified)

- mDNS name `ds720.local` resolves to **192.168.0.108** — NOT 192.168.11.109 (that IP in memory is stale; the Mac is on 192.168.0.x). Always re-probe with `ping ds720.local` before assuming the IP.
- SMB user: `erik03132`. Share used for TM: `Time Mashine`.
- The NAS TM share was already mounted at one point (`/Volumes/.timemachine/DS720.../Time Mashine`), proving TM-on-NAS was previously configured. If `tmutil listdestinations` is empty but the share IS mounted, TM just isn't currently "attached" — `tmutil setdestination <mount>` re-attaches it.

## Reusable technique — probe NAS + mount state without auth

You can't list SMB shares without credentials, but you CAN:
- Confirm reachability: `ping -c 1 -W 2000 ds720.local`
- Confirm current mount: `mount | grep "Time Mashine"`
- Confirm what Finder already mounted: `ls /Volumes/`
- Check TM attachment: `tmutil currentdestination` and `tmutil listdestinations`

## LaunchAgent hygiene (Igor's rule: reversible, no surprise)

- Unload before editing, then reload: `launchctl unload ~/Library/LaunchAgents/<label>.plist` → edit → `launchctl load …`. Loading twice errors; unloading an already-unloaded plist errors with `I/O error 5` (harmless — means it's already out).
- `launchctl list | grep <label>` shows `-  0  <label>` when loaded-but-idle (the leading `-` = not currently running, which is correct for a calendar-scheduled agent).
- Always keep the plist file on disk even after unload, so it can be re-enabled. Don't delete plists to "disable" — unload them.

## Test the chain manually

After mounting the share once via Finder:
```bash
/bin/bash ~/nas-tools/nas-tm-backup.sh
tail -20 ~/nas-tools/tm-backup.log
```
Expected: "NAS reachable" → "share mounted" → "destination attached" (first run only) → "backup finished".

## PITFALL — TM appears "not set up" but share is mounted

If `tmutil listdestinations` returns empty yet `mount | grep Time` shows the share, TM simply isn't attached to that volume. Run `tmutil setdestination <mountpoint>` (or let the script do it). Don't assume the backup is broken — it's just unattached.

## One-line pointer to the worker script

The full script lives at `scripts/nas-tm-backup.sh` (copy it to `~/nas-tools/` and `chmod +x`). It is the safe, Keychain-respecting version described above.
