# Fix deprecated st.experimental_rerun

## Changes
### kabuzan
#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- Replaced all 4 instances of `st.experimental_rerun()` with `st.rerun()`.

## Verification Results
### Automated Checks
- Ran `grep` search for `experimental_rerun` in `app.py` and found 0 matches.

### Manual Verification
- The changes are direct API replacements mandated by Streamlit version updates. The logic remains identical.
