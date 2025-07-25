import streamlit as st
import pandas as pd
import numpy as np
import joblib
from PIL import Image
from datetime import datetime
import calendar
import os

@st.cache_resource
def load_models():
    """Load and cache the ML models and preprocessing objects"""
    try:
        # Simple approach - no os module needed
        model = joblib.load('coffee_Sales_model.pkl')
        scaler = joblib.load('scaler.pkl')
        selector = joblib.load('feature_selector.pkl')
        
        return model, scaler, selector
        
    except FileNotFoundError as e:
        st.error(f"Model files not found: {str(e)}")
        st.error("Please ensure all .pkl files are in the same directory as your app.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading model files: {str(e)}")
        st.stop()
        
model, scaler, selector = load_models()

# Configure page
st.set_page_config(
    page_title="Coffee Shop Revenue Predictor", 
    page_icon="☕", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Add some styling
st.markdown("""
    <style>
    .big-font {
        font-size:18px !important;
    }
    .prediction {
        font-size:22px !important;
        color: #2e8b57;
    }
    .date-info {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://www.shutterstock.com/image-vector/coffee-shop-icon-design-isolated-260nw-2224458527.jpg", width=80)
with col2:
    st.title("Coffee Shop Revenue Predictor")
    st.markdown("Predict your shop's daily revenue based on operational factors")

# Sidebar with information
with st.sidebar:
    st.header("About This App")
    st.markdown("""
    This app predicts daily revenue for coffee shops using machine learning.
    Simply select a date and enter your shop's operational details to get an instant revenue prediction.
    """)
    st.markdown("**Model Details:**")
    st.markdown("- Algorithm: Linear Regression")
    st.markdown("- Features: 10+ operational factors")
    st.markdown("- Accuracy: 94.7%")
    st.markdown("---")
    st.markdown("Created by **Sankaran S**")

# Main content
st.subheader("Shop Details")

# Function to encode day name
def get_day_name_encoded(day_name):
    day_name_mapping = {
        "Monday": 1, 
        "Tuesday": 5, 
        "Wednesday": 6, 
        "Thursday": 4, 
        "Friday": 0, 
        "Saturday": 2, 
        "Sunday": 3
    }
    return day_name_mapping[day_name]

col1, col2 = st.columns(2)

with col1:
    # Date picker - this replaces all the manual temporal inputs
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date(),
        help="Choose the date for which you want to predict revenue"
    )
    
    # Auto-calculate all temporal features from selected date
    day_of_week = selected_date.weekday() + 1  # Monday=1, Sunday=7
    day_name = calendar.day_name[selected_date.weekday()]
    day_name_encoded = get_day_name_encoded(day_name)
    day_of_year = selected_date.timetuple().tm_yday
    week_of_year = selected_date.isocalendar()[1]
    month = selected_date.month
    quarter = (month - 1) // 3 + 1
    is_weekend = 1 if selected_date.weekday() >= 5 else 0  # Saturday=5, Sunday=6
    
    season_name = st.selectbox("Season", options=["Fall", "Spring", "Summer", "Winter"], index=0)
    season_mapping = {"Fall": 0, "Spring": 1, "Summer": 2, "Winter": 3}
    season = season_mapping[season_name]
    
    # Display auto-calculated information (SIMPLE theme-adaptive solution)
    date_info = f"""
    📅 **Date Information:**
    - **Day:** {day_name}
    - **Week:** {week_of_year} of {selected_date.year}
    - **Month:** {calendar.month_name[month]}
    - **Quarter:** Q{quarter}
    - **Season:** {season_name}
    - **Weekend:** {'Yes' if is_weekend else 'No'}
    """
    st.info(date_info)

    
    is_raining = st.radio("Is Raining?", options=["No", "Yes"])
    is_raining = 1 if is_raining == "Yes" else 0
    
    if is_raining == 1:
        rainfall = st.slider("Rainfall (mm)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
    else:
        rainfall = 0.0

with col2:
    temperature = st.slider("Temperature (°C)", min_value=-10.0, max_value=40.0, value=25.0, step=0.5)
    
    promotion_active = st.radio("Promotion Active?", options=["No", "Yes"])
    promotion_active = 1 if promotion_active == "Yes" else 0
    
    nearby_events = st.radio("Nearby Events?", options=["No", "Yes"])
    nearby_events = 1 if nearby_events == "Yes" else 0
    
    staff_count = st.slider("Staff Count", min_value=1, max_value=10, value=3)
    
    machine_issues = st.radio("Machine Issues?", options=["No", "Yes"])
    machine_issues = 1 if machine_issues == "Yes" else 0
    
    num_customers = st.number_input("Number of Customers", min_value=0, max_value=1000, value=120)
    
    customer_satisfaction = st.slider("Customer Satisfaction (1-10)", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
    
    is_holiday = st.radio("Is Holiday?", options=["No", "Yes"])
    is_holiday = 1 if is_holiday == "Yes" else 0

st.markdown("---")
st.subheader("Product Sales")

col3, col4, col5 = st.columns(3)
with col3:
    coffee_sales = st.number_input("Coffee Sales (units)", min_value=0, value=60)
with col4:
    pastry_sales = st.number_input("Pastry Sales (units)", min_value=0, value=30)
with col5:
    sandwich_sales = st.number_input("Sandwich Sales (units)", min_value=0, value=20)

# Add a predict button
predict_button = st.button("Predict Revenue", use_container_width=True)

# Prediction Logic
if predict_button:
    # Create input data dictionary
    input_data = {
        'Day_of_Week': day_of_week,
        'Is_Weekend': is_weekend,
        'Month': month,
        'Temperature_C': temperature,
        'Is_Raining': is_raining,
        'Rainfall_mm': rainfall,
        'Is_Holiday': is_holiday,
        'Promotion_Active': promotion_active,
        'Nearby_Events': nearby_events,
        'Staff_Count': staff_count,
        'Machine_Issues': machine_issues,
        'Num_Customers': num_customers,
        'Coffee_Sales': coffee_sales,
        'Pastry_Sales': pastry_sales,
        'Sandwich_Sales': sandwich_sales,
        'Customer_Satisfaction': customer_satisfaction,
        'Day_of_Year': day_of_year, 
        'Week_of_Year': week_of_year,   
        'Quarter': quarter,       
        "Day_Name_Encoded": day_name_encoded,  
        'Season_Encoded': season 
    }


    input_df = pd.DataFrame([input_data])

    # Create DataFrame and display
    st.markdown("---")
    
    # Preprocess input
    scaled_input = scaler.transform(input_df)
    selected_input = selector.transform(scaled_input)

    # Predict
    prediction = model.predict(selected_input)[0]
    
    # Display prediction
    st.subheader("Prediction Result")
    
    col_pred1, col_pred2 = st.columns([1, 2])
    with col_pred1:
        st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=100)
    with col_pred2:
        st.markdown(f"""
        <div class='big-font'>
        Based on the input data for <strong>{selected_date.strftime('%B %d, %Y')}</strong> ({day_name}), your predicted revenue is:
        </div>
        <div class='prediction'>
        ${prediction:,.2f}
        </div>
        """, unsafe_allow_html=True)
        
        # Add some interpretation
        if prediction > 1000:
            st.success("This is an excellent revenue day! Consider increasing staff to handle the volume.")
        elif prediction > 600:
            st.info("This is a good revenue day. Typical performance for your shop.")
        else:
            st.warning("Revenue is below average. Consider promotions or checking operational issues.")
