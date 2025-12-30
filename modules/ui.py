import streamlit as st

def get_card_css():
    """Return CSS for stock cards and responsive layout."""
    return """
    <style>
    /* Card Button Style Overrides */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid #30363d;
        background-color: #0d1117;
        color: #e6edf3;
        padding: 12px 16px;
        text-align: left;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        height: auto;
        line-height: 1.4;
    }
    
    div.stButton > button:hover {
        border-color: #58a6ff;
        background-color: #161b22;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    div.stButton > button:active {
         transform: translateY(0);
    }

    /* Small text specific class (can't target inner button text easily vs generic stButton, 
       but we format the label string to help) */

    /* Responsive Grid for Foldable */
    @media (max-width: 768px) {
        /* On standard mobile, force stacking if not already */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    
    /* Pixel Fold Unfolded (Large Inner Screen) approx 1200px or so vs Tablet */
    @media (min-width: 769px) and (max-width: 1200px) {
         /* Adjust font sizes for tablet/foldable open state */
         .stMetrics { font-size: 0.9em; }
    }
    </style>
    """

def render_stock_card(code, name, price, change, percent, key):
    """
    Render a stock card using st.button with formatted multi-line label.
    """
    # Color logic for icon
    icon = "📈" if change > 0 else "📉"
    color_emoji = "🟢" if change > 0 else "🔴"
    
    # Format Label
    # Line 1: Name (Code)
    # Line 2: Price | Change (Percent)
    label = f"{name} ({code})\n¥{price:,.0f} | {change:+,.0f} ({percent:+.2f}%) {icon}"
    
    # We rely on the CSS in get_card_css to make this button look like a card
    if st.button(label, key=key, use_container_width=True):
        return True
    return False
