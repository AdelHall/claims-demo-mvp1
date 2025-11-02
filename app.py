import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Broker Claims Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Broker Claims Dashboard (Demo)")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('synthetic_claims_data.csv')
    
    # Data Cleaning
    # Convert dates to datetime
    df['DateOfLoss'] = pd.to_datetime(df['DateOfLoss'], errors='coerce')
    df['DateReported'] = pd.to_datetime(df['DateReported'], errors='coerce')
    
    # Ensure financial columns are numeric
    financial_cols = ['PaidIndemnity', 'PaidExpense', 'ReserveIndemnity', 'ReserveExpense']
    for col in financial_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Feature Engineering
    df['TotalIncurred'] = (
        df['PaidIndemnity'] + 
        df['PaidExpense'] + 
        df['ReserveIndemnity'] + 
        df['ReserveExpense']
    )
    df['TotalPaid'] = df['PaidIndemnity'] + df['PaidExpense']
    
    # Extract Loss Year
    df['LossYear'] = df['DateOfLoss'].dt.year
    
    return df

# Load the data
try:
    df = load_data()
    
    # Calculate KPIs
    total_incurred = df['TotalIncurred'].sum()
    total_paid = df['TotalPaid'].sum()
    total_open_claims = len(df[df['ClaimStatus'] == 'Open'])
    
    # Calculate average cost per open claim
    open_claims_incurred = df[df['ClaimStatus'] == 'Open']['TotalIncurred'].sum()
    avg_cost_per_open_claim = open_claims_incurred / total_open_claims if total_open_claims > 0 else 0
    
    # Display KPIs in 4 columns
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Incurred",
            value=f"${total_incurred:,.0f}"
        )
    
    with col2:
        st.metric(
            label="Total Paid",
            value=f"${total_paid:,.0f}"
        )
    
    with col3:
        st.metric(
            label="Total Open Claims",
            value=f"{total_open_claims:,}"
        )
    
    with col4:
        st.metric(
            label="Avg Cost per Open Claim",
            value=f"${avg_cost_per_open_claim:,.0f}"
        )
    
    st.markdown("---")
    
    # Create two columns for charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Chart 1: Top 5 Causes of Loss by Total Incurred
        st.markdown("### 🔥 Top 5 Causes of Loss by Total Incurred")
        cause_summary = df.groupby('CauseOfLoss')['TotalIncurred'].sum().sort_values(ascending=False).head(5)
        
        fig1 = px.bar(
            x=cause_summary.values,
            y=cause_summary.index,
            orientation='h',
            labels={'x': 'Total Incurred ($)', 'y': 'Cause of Loss'},
            color=cause_summary.values,
            color_continuous_scale='Blues'
        )
        fig1.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Chart 2: Open vs. Closed Claims (Pie Chart)
        st.markdown("### 📊 Open vs. Closed Claims")
        status_counts = df['ClaimStatus'].value_counts()
        
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        fig2.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col_right:
        # Chart 3: Top 5 Locations by Total Incurred
        st.markdown("### 🌎 Top 5 Locations by Total Incurred")
        location_summary = df.groupby('Location')['TotalIncurred'].sum().sort_values(ascending=False).head(5)
        
        fig3 = px.bar(
            x=location_summary.values,
            y=location_summary.index,
            orientation='h',
            labels={'x': 'Total Incurred ($)', 'y': 'Location'},
            color=location_summary.values,
            color_continuous_scale='Greens'
        )
        fig3.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Chart 4: Total Incurred by Loss Year
        st.markdown("### 📅 Total Incurred by Loss Year")
        year_summary = df.groupby('LossYear')['TotalIncurred'].sum().sort_index()
        
        fig4 = px.bar(
            x=year_summary.index,
            y=year_summary.values,
            labels={'x': 'Loss Year', 'y': 'Total Incurred ($)'},
            color=year_summary.values,
            color_continuous_scale='Reds'
        )
        fig4.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # Display the full dataset
    st.markdown("### 📋 Complete Claims Data")
    st.markdown(f"*Showing all {len(df)} claims*")
    
    # Format the dataframe for display
    display_df = df.copy()
    
    # Format dates
    display_df['DateOfLoss'] = display_df['DateOfLoss'].dt.strftime('%Y-%m-%d')
    display_df['DateReported'] = display_df['DateReported'].dt.strftime('%Y-%m-%d')
    
    # Format financial columns
    for col in ['PaidIndemnity', 'PaidExpense', 'ReserveIndemnity', 'ReserveExpense', 'TotalIncurred', 'TotalPaid']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Reorder columns for better display
    column_order = [
        'ClaimNumber', 'ClaimStatus', 'DateOfLoss', 'DateReported', 
        'CauseOfLoss', 'Location', 'LossYear',
        'TotalIncurred', 'TotalPaid',
        'PaidIndemnity', 'PaidExpense', 'ReserveIndemnity', 'ReserveExpense'
    ]
    
    display_df = display_df[column_order]
    
    st.data_editor(
        display_df,
        use_container_width=True,
        num_rows="fixed",
        disabled=True,
        height=400
    )
    
    # Footer
    st.markdown("---")
    st.markdown("**ClaimShape** | Broker Claims Dashboard | Demo Version")

except FileNotFoundError:
    st.error("❌ Error: 'synthetic_claims_data.csv' file not found. Please ensure the CSV file is in the same directory as this app.")
    st.info("💡 Tip: Upload your claims data file or check the file path.")
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("Please check your data file and try again.")
