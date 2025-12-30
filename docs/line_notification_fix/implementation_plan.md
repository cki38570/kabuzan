# Implementation Plan - Fix Duplicate Notifications

The user reports LINE notifications are sent every 5 minutes. This is caused by `process_morning_notifications` in `app.py` relying on ephemeral `st.session_state`. External uptime monitors or pings to the app trigger a new session, causing the notification logic to run repeatedly. Additionally, `auto_monitor.py` (running hourly) bypasses checks, which would cause hourly notifications.

## User Review Required
> [!IMPORTANT]
> This change introduces a `last_daily_report_date` field in your `settings.json` (or Google Sheet 'settings' tab). This ensures the report is sent exactly once per day, regardless of how many times the app is accessed or the bot runs.

## Proposed Changes

### Modules
#### [MODIFY] [notifications.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/notifications.py)
- Update `process_morning_notifications` to:
    1. Load `settings` from `storage`.
    2. Check if `settings['last_daily_report_date']` matches today's date.
    3. If matched, return immediately (skip notification).
    4. If not matched, send the report and **update** `settings['last_daily_report_date']` to today.

#### [MODIFY] [auto_monitor.py](file:///C:/Users/GORO/Desktop/kabuzan/auto_monitor.py)
- Change the direct call `send_daily_report(manual=True)` to `process_morning_notifications()`.
- This ensures the bot also respects the "once per day" rule and shares the same state as the app.

## Verification Plan

### Automated Tests
- None valid for this specific interaction (requires external pings).

### Manual Verification
1.  **Check Persistence**:
    - Trigger `process_morning_notifications` (by simulating a run or waiting for app reload).
    - Verify `last_daily_report_date` is updated in `settings.json` (or Google Sheet).
    - Reload the page immediately. Verify NO second notification is received.
2.  **Force Run**:
    - Verify the "Send Report" button in the UI still works (it uses `manual=True`).
