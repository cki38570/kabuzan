# Implementation Plan - Deployment Fixes

## Problem Description
The deployed Streamlit application (`kabuzan-ai`) encountered multiple critical errors:
1. **TypeError in Analysis Module**: `calculate_indicators()` failed when called with `interval="1wk"`, causing the app to crash on load.
2. **Streamlit Deprecation Warnings**: Repeated warnings about `use_container_width` needing replacement.
3. **DuckDB Syntax Error**: The `defeatbeta_client` failed to initialize DuckDB secrets due to parsing errors.
4. **API Limitation Noise**: Excessive logs from FMP API returning 403 Forbidden for Japanese tickers.

## Proposed Changes

### 1. Fix `modules/analysis.py`
- **Change**: Update `calculate_indicators` function signature.
- **Detail**: Explicitly include `interval="1d"` and `**kwargs` to prevent `TypeError` when extra arguments are passed by `app.py`.

### 2. Update `app.py`
- **Change**: Replace deprecated arguments.
- **Detail**: Swap `use_container_width=True` with `width='stretch'` for `st.dataframe` calls to comply with Streamlit v1.52+ standards.

### 3. Stabilize `modules/defeatbeta_client.py`
- **Change**: Simplify DuckDB authentication.
- **Detail**: Replace the fragile `CREATE SECRET` SQL command with the robust `SET http_headers` command to ensure the HuggingFace token is correctly recognized without syntax errors.

### 4. Optimize `modules/data_manager.py`
- **Change**: Improve Error Handling.
- **Detail**: Catch `403 Forbidden` errors from FMP API and suppress them from the logs to reduce noise, as the fallback to `yfinance` is already in place.

## Verification Plan

### Automated Tests
- None specific (Visual/Runtime verification required).

### Manual Verification
1. **Deploy**: Push changes to GitHub -> Streamlit Cloud.
2. **Load App**: Ensure the app loads without the "Oh no" error screen.
3. **Check Logs**: Verify no more traceback for `TypeError`.
4. **Check Charts**: Switch between "Daily" and "Weekly" tabs to ensure indicators calculate correctly.
5. **Check AI Tab**: Verify the "AI Analysis" tab generates a report (indicating successful data pipeline).
