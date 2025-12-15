# Fix AI Analysis KeyError Implementation Plan

## Problem
The user reported a `KeyError` when running the AI Analysis feature. The error occurs in `app.py` line 256 because the application expects a `type` key in the pattern dictionaries returned by `modules/patterns.py`, but this key is missing.

## Proposed Changes

### modules/patterns.py
Update `identify_candlestick_patterns` and `identify_chart_patterns` to include a `type` key in the returned dictionaries.

#### [MODIFY] [patterns.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/patterns.py)
- Add `'type': 'neutral'` for Doji
- Add `'type': 'bullish'` for Hammer and Bullish Engulfing
- Add `'type': 'bearish'` for Shooting Star and Bearish Engulfing
- Add `'type': 'bullish'` for Higher Lows (in `identify_chart_patterns`)
- Add `'type': 'bearish'` for Lower Highs (in `identify_chart_patterns`)

### app.py
Update the pattern display logic to handle missing keys gracefully and also display chart patterns which were previously ignored in the loop.

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- Change pattern iteration to include both `candlestick_patterns` and `chart_patterns`.
- Use `.get('type', 'neutral')` to prevent `KeyError`.
- Update the color logic to handle 'neutral' types (e.g., use a different icon or default to gray/warning color).

## Verification Plan

### Manual Verification
1.  Start the Streamlit app.
2.  Select a stock ticker (e.g., 7203 Toyota).
3.  Navigate to the "AI Analysis" (AI分析) tab.
4.  Confirm that the "Detected Patterns" section (if patterns are found) displays correctly without error.
5.  Verify that both candlestick and chart patterns are shown with appropriate icons/colors.
