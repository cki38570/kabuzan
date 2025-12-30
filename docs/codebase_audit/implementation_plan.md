# Implementation Plan - Fix Repetitive LINE Notifications

The previous fix failed because the storage module's settings parser was discarding non-numeric values (like the date string), preventing the "already sent" check from working.

## User Review Required
> [!IMPORTANT]
> - **Bug in Storage**: The current code attempts to convert ALL settings to float numbers. This means the last notification date ("2025-12-31") is discarded, leading the system to think a report hasn't been sent.
> - **Verification**: I will fix the parser to handle strings and booleans correctly.

## Proposed Changes

### [Robustness] Storage Module
#### [MODIFY] [storage.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/storage.py)
- Update `parse_kv` inside `load_settings` to support string and boolean values.
- Ensure that `last_daily_report_date` and `notify_line` (if stored as strings) are correctly interpreted.

### [Logic] Notification Module
#### [MODIFY] [notifications.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/notifications.py)
- Add more explicit logging to `process_morning_notifications` to show when a report is skipped or sent, helping debug future issues.

## Verification Plan

### Automated Tests
- Create a test script `verify_storage_fix.py` to:
    1. Save a date string to settings.
    2. Reload it and verify it's still a string and matches the original.
    3. Verify that boolean settings are also preserved.

### Manual Verification
- I will check the logs (if possible) or rely on the user's feedback that the 5-minute interval has stopped.
