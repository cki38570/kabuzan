# Deployment Fixes Task List

- [x] **Investigation**
    - [x] Analyze Streamlit Cloud logs
    - [x] Identify `TypeError` in `calculate_indicators`
    - [x] Identify Streamlit deprecation warnings (`use_container_width`)
    - [x] Identify DuckDB secret syntax error
    - [x] Identify FMP API 403 error loops

- [x] **Code Correction**
    - [x] Fix `modules/analysis.py`: Update `calculate_indicators` to accept `interval` and `**kwargs`.
    - [x] Fix `app.py`: Replace `use_container_width=True` with `width='stretch'` for `st.dataframe`.
    - [x] Fix `modules/defeatbeta_client.py`: dedicated `SET http_headers` instead of `CREATE SECRET` for robust DuckDB auth.
    - [x] Fix `modules/data_manager.py`: Suppress FMP 403 logging for cleaner output.

- [ ] **Verification**
    - [ ] Deploy to Streamlit Cloud
    - [ ] Verify Charts (Daily/Weekly) apply correctly without error.
    - [ ] Verify AI Analysis runs without crash.
