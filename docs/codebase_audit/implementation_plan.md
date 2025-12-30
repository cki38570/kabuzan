# Implementation Plan - Fix Repetitive LINE Notifications

The previous fix failed because the storage module's settings parser was discarding non-numeric values (like the date string), preventing the "already sent" check from working.

## User Review Required
> [!IMPORTANT]
> - **Bug in Storage**: The current code attempts to convert ALL settings to float numbers. This means the last notification date ("2025-12-31") is discarded, leading the system to think a report hasn't been sent.
> - **Verification**: I will fix the parser to handle strings and booleans correctly.

## Proposed Changes

### [Robustness] Storage Module
#### [MODIFY] [storage.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/storage.py)
- Update `save_settings` to explicitly convert all values to `str` before saving to GSheets/Local. This prevents GSheets from rejecting updates due to "mixed types" in a column.
- Update `parse_kv` inside `load_settings` to handle `Timestamp` or `Date` objects gracefully (in case GSheets auto-detects the date string).

### [Logic] Notification Module
#### [MODIFY] [notifications.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/notifications.py)
- Use `str(last_sent)` in `process_morning_notifications` to ensure robust date comparison.
- Add a "Test Storage Connection" button in `show_notification_settings` to help the user verify if their GSheets allows writing.
- Add a time-window guard (9 AM - 11 PM JST) to prevent weird midnight triggers if server clocks drift.

### [UI] App Monitoring
#### [MODIFY] [app.py](file:///C:/Users/GORO/Desktop/kabuzan/app.py)
- Display a small status indicator in the sidebar if `last_daily_report_date` is not being saved correctly.

## Verification Plan

### Automated Tests
- Create a test script `verify_storage_fix.py` to:
    1. Save a date string to settings.
    2. Reload it and verify it's still a string and matches the original.
    3. Verify that boolean settings are also preserved.

### Manual Verification
- I will check the logs (if possible) or rely on the user's feedback that the 5-minute interval has stopped.
