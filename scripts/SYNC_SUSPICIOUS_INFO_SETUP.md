# Automatic Execution Setup for Suspicious Information Sync

This document explains how to set up automatic execution of the suspicious information photo sync script.

## Overview

The sync script `sync_suspicious_info_cron.py` fetches suspicious information records from the external API and downloads their associated photos to the local media folder. This document describes how to schedule automatic execution.

## Windows Task Scheduler Setup

To run the script automatically on Windows:

1. Open Task Scheduler (taskschd.msc)
2. Click "Create Basic Task" in the right panel
3. Name: "SACIP Suspicious Info Sync"
4. Description: "Sync suspicious information photos from external API"
5. Trigger: Choose "Daily" or "Weekly" based on your preference
6. Set the desired start time
7. Action: "Start a program"
8. Program/script: `python`
9. Add arguments: `scripts\sync_suspicious_info_cron.py`
10. Start in: `C:\Users\Alvaro\Music\PNA\SACIP\backend-v2` (or your project path)

## Alternative: Using a Batch File

Create a batch file to run the script with the correct path:

```batch
@echo off
cd /d "C:\Users\Alvaro\Music\PNA\SACIP\backend-v2"
python scripts\sync_suspicious_info_cron.py
```

Then schedule this batch file in Task Scheduler instead of the Python script directly.

## Linux Cron Setup (if applicable)

If running on Linux, you can use cron to schedule execution:

```bash
# Edit crontab
crontab -e

# Add line to run the script every hour
0 * * * * cd /path/to/backend-v2 && python scripts/sync_suspicious_info_cron.py

# Or to run every day at 2 AM
0 2 * * * cd /path/to/backend-v2 && python scripts/sync_suspicious_info_cron.py
```

## Script Features

- Checks API connectivity before attempting sync
- Only downloads new images that don't already exist
- Updates existing records with new information
- Implements retry logic for failed downloads
- Handles missing image files by re-downloading them
- Uses proper URL encoding for the API proxy endpoint