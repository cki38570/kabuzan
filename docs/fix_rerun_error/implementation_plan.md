# Fix deprecated st.experimental_rerun

## Goal Description
The Streamlit app is encountering an `AttributeError` because `st.experimental_rerun()` has been deprecated and removed in recent Streamlit versions. This change replaces it with the modern `st.rerun()`.

## User Review Required
No critical user review required, this is a standard API update.

## Proposed Changes
### kabuzan
#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- Replace `st.experimental_rerun()` with `st.rerun()` in `load_watchlist` (if applicable) and other locations.
- Locations identified: Line 121, 129, 421, 441.

## Verification Plan
### Manual Verification
- **Watchlist Clear**: Click "List Clear" button and verify no error occurs.
- **Comparison Mode**: Toggle usage and verify rerun works.
- **Portfolio Add/Remove**: Add/Remove items and verify rerun works.
