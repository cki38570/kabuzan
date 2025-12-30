# Implementation Plan - Codebase Audit & Improvement

Based on the codebase audit, several critical and minor issues were identified. This plan aims to improve performance (especially mobile sidebar loading), data robustness, and code quality.

## User Review Required
> [!IMPORTANT]
> - **Sidebar Performance**: I will implement caching for the watchlist cards to prevent repeated `yfinance` calls, which currently slow down the app and risk rate limits.
> - **Data Reliability**: I will fix the "data overwriting" bug in `data_manager.py` to ensure financial data from multiple sources (FMP/DefeatBeta) is properly merged rather than discarded.
> - **AI Model Updates**: I will update the Gemini model names in `llm.py` to the latest stable ones (e.g., `gemini-1.5-flash`).

## Proposed Changes

### [Performance] Sidebar & Watchlist
#### [MODIFY] [app.py](file:///C:/Users/GORO/Desktop/kabuzan/app.py)
- Wrap the watchlist card data fetching logic in `st.cache_data` or use a ttl-based cache to avoid per-render API calls.
- Optimize the layout for mobile responsiveness if possible.

### [Robustness] Data Management
#### [MODIFY] [data_manager.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/data_manager.py)
- Fix the `get_financial_data` method to use `.update()` instead of re-initializing the `details` dictionary, ensuring data from FMP/DefeatBeta is preserved.
- Improve fallback logic in `get_market_data` to handle cases where both FMP and yfinance history fail.

### [Code Quality] AI & Global
#### [MODIFY] [llm.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- Update `MODEL_CANDIDATES` to standard stable names: `['gemini-1.5-flash', 'gemini-1.5-pro']`.
- Remove the duplicated return statement at the end of the file.
#### [MODIFY] [storage.py](file:///C:/Users/GORO/Desktop/kabuzan/modules/storage.py)
- Add basic error handling to the GSpread update logic to prevent data loss on failed updates.

## Verification Plan

### Automated Tests
- None, but I will perform manual verification of the cached data loading.

### Manual Verification
1.  **Sidebar Speed**: Observe the sidebar loading speed; it should be near-instant after the first load.
2.  **Data Completeness**: Verify that financial metrics (Market Cap, etc.) are correctly displayed even when switching between tickers.
3.  **AI Analysis**: Run a sample AI analysis to ensure the updated model names work correctly.
