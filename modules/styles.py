def get_custom_css():
    return """
    <style>
        /* Global Reset & Background */
        .stApp {
            background-color: #0a192f;
            color: #ffffff;
        }
        
        /* Text Colors */
        h1, h2, h3, h4, h5, h6, p, div, span, label, li {
            color: #ffffff !important;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input {
            background-color: #112240;
            color: #ffffff;
            border: 1px solid #233554;
            border-radius: 8px;
            font-size: 16px; /* Prevent zoom on mobile */
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }
        [data-testid="stMetricDelta"] {
            font-size: 1.2rem !important;
        }
        
        /* Tabs (Android Optimized) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0a192f;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #112240;
            border-radius: 5px 5px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: #8892b0;
            font-size: 1.1rem;
            flex-grow: 1; /* Full width tabs */
            justify-content: center;
        }
        .stTabs [aria-selected="true"] {
            background-color: #233554;
            color: #64ffda !important;
            border-bottom: 2px solid #64ffda;
        }
        
        /* Tables */
        .dataframe {
            background-color: #112240 !important;
            color: #ffffff !important;
        }
        th {
            background-color: #233554 !important;
            color: #ccd6f6 !important;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* header {visibility: hidden;}  <-- Removed to show hamburger menu on mobile */
        
        /* Mobile adjustments */
        @media (max-width: 640px) {
            [data-testid="stMetricValue"] {
                font-size: 2.8rem !important;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 0.9rem;
            }
        }
        
        /* Sidebar Fix */
        [data-testid="stSidebar"] {
            background-color: #0a192f !important;
            border-right: 1px solid #233554;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background-color: #112240 !important;
            color: #64ffda !important;
            border: 1px solid #233554 !important;
            width: 100%;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #233554 !important;
            border-color: #64ffda !important;
        }
        [data-testid="stSidebar"] input {
            background-color: #112240 !important;
            color: #ffffff !important;
            border: 1px solid #233554 !important;
        }
    </style>
    """
