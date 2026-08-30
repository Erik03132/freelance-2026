---
name: macos-maintenance
description: "macOS maintenance: disk monitor, cache cleanup, app removal."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [macos, maintenance, cleanup, disk-space, cache, apps, uninstall]
    related_skills: [systematic-debugging, plan]
---

# macOS Maintenance

## Overview

Maintain a healthy macOS system: monitor disk, clean safe junk, remove unused apps/games, and offload large folders to external storage (NAS).

**Safety rules:**
- Cache cleanup: only remove files older than AGE_DAYS (default 7) — protects active app caches
- Never delete system files, user data, or application support directories
- When NAS/storage is unreachable: stop after 2-3 attempts, report blocker, pivot to local cleanup
- Games: ask first if user plays; if not, remove all
- Applications: use `kMDItemLastUsedDate` from `mdls` to identify unused (>6 months = safe removal candidates)

## When to Use

- Disk usage above 80% (critical above 95%)
- User asks to remove unused apps, games, or old software
- System feels sluggish due to low disk space
- User wants routine maintenance / weekly cleanup

## The Iron Rule — Stop After 3

```
IF a resource (NAS, SSH share, remote API) is unreachable after 3 attempts:
  STOP probing
  Report the blocker clearly (subnet mismatch, ports closed, auth failed)
  PIVOT to what CAN be done locally (cache cleanup, app removal)
  Ask user for next direction
```

Looping on unreachable networks wastes the user's time and erodes trust.

## Workflow

### Phase 1: Assess Disk & Memory

```bash
# Disk usage
df -h /

# Memory
vm_stat | head -10

# Top space consumers in home
du -sh ~/Downloads ~/Desktop ~/Documents ~/Library/Caches ~/Library/Application\ Support 2>/dev/null | sort -hr
```

### Phase 2: Safe Cache Cleanup

Build an age-gated script that:
1. Scans `~/Library/Caches`, `~/Library/Logs`, `~/.Trash`
2. Only touches files older than 7 days
3. Protects system caches (`com.apple.*`)
4. Runs dry first, reports reclaimable space
5. Re-runs with `--clean` flag for actual removal

See `scripts/maintenance_agent.py` for the reference implementation.

### Phase 3: Identify Unused Applications

```bash
# List ALL apps with last used date (sorted by date)
find /Applications -maxdepth 1 -name "*.app" -type d | while read app; do
  echo "$(mdls -raw -name kMDItemLastUsedDate "$app" 2>/dev/null || echo "never")|$app"
done | sort
```

Apps with `(null)` or dates older than 6 months = safe removal candidates.

```bash
# Find games by name patterns
find /Applications -maxdepth 1 -name "*.app" | grep -iE \
  "game|play|arcade|stickman|superhero|sprint|gun|jetpack|shuriken|duelist|survival|sniper|race|drift|battle|war|craft|mine"
```

### Phase 4: Present Removal Plan

Group candidates by category with sizes:
- **Games** — all, if user doesn't play
- **Large unused** (>100MB, not used >6 months) — one table
- **VPNs/utilities/duplicates** — another table
- **Total reclaimable space**

Ask user to confirm BEFORE deleting anything.

```bash
# Get size of a specific app
du -sh "/Applications/AppName.app"
```

### Phase 5: Remove Applications

```bash
# Safe removal (move to trash, not permanent delete)
osascript -e 'tell application "Finder" to delete POSIX file "/Applications/AppName.app"'

# Or use trash CLI if available
# trash "/Applications/AppName.app"
```

After removal:
```bash
# Also clean associated files
rm -rf ~/Library/Application\ Support/AppName
rm -rf ~/Library/Caches/com.developer.AppName
rm -rf ~/Library/Preferences/com.developer.AppName.plist
```

### Phase 6: Offload to NAS (when accessible)

If NAS is reachable:
1. Use `rsync` for large folders: `rsync -avh --progress ~/LargeFolder/ user@nas:/share/`
2. Or mount SMB share and use `cp`/`rsync`
3. Verify copy succeeded before deleting local originals

If NAS is unreachable (subnet mismatch):
- Report blocker clearly
- Suggest VPN/port-forwarding
- Pivot to local cleanup

## Automation

For recurring maintenance, create a cron job:
- Daily at 09:00
- Runs maintenance script in dry-run mode
- Reports disk status, reclaimable space, any alerts
- Does NOT auto-delete (user must approve)

See `references/cronjob-setup.md` for exact configuration.

## Key User Preferences (from Igor Vasin)

- **Speaks Russian** — respond in Russian
- **Practical action > diagnostics** — do the thing, stop after a few failed attempts
- **Does not play games** — all games are removal candidates
- **NAS**: Synology DS720+ at 192.168.11.109 (different subnet — requires VPN or gateway access)
- **Disk is critically full** — recurring issue, needs monitoring

## Common Pitfalls

| Mistake | Correct Approach |
|---|---|
| Looping on unreachable NAS | Stop after 3 attempts, report, pivot |
| Deleting caches without age gate | Only remove files >7 days old |
| Removing apps without checking last-used date | Always check `kMDItemLastUsedDate` first |
| Permanent delete instead of trash | Use Finder trash so user can recover |
| Not presenting a plan before destructive ops | Always show categorized table + total size, ask confirmation |
