import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BankMind Analytics", page_icon="🏦", layout="wide")

st.title("🏦 BankMind: Cross-Sell Insights Dashboard")
st.markdown("Analyzing historical campaign data to identify optimal cross-selling opportunities for term deposits.")

# --- DATA LOADING & PROCESSING ---
@st.cache_data
def load_data():
    # The UCI dataset uses semicolons, not commas!
    df = pd.read_csv("bank-full.csv", sep=";") 
    
    # Map the target variable to binary (1/0) to easily calculate percentages
    df['subscribed'] = df['y'].map({'yes': 1, 'no': 0})
    
    # Bin the age groups exactly as requested in the prompt
    bins = [17, 30, 45, 60, 120]
    labels = ['18-30', '31-45', '46-60', '60+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)
    
    return df

# Load the data
try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Data file not found. Please ensure 'bank-full.csv' is in the same directory as this script.")
    st.stop()

# --- INTERACTIVE SIDEBAR ---
st.sidebar.header("Filter Data")
marital_filter = st.sidebar.multiselect(
    "Filter by Marital Status",
    options=df['marital'].unique(),
    default=df['marital'].unique()
)

# Apply the filter to our working dataframe
df_filtered = df[df['marital'].isin(marital_filter)]

# --- TOP-LEVEL METRICS ---
total_customers = len(df_filtered)
sub_rate = df_filtered['subscribed'].mean() * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Overall Subscription Rate", f"{sub_rate:.2f}%")
col3.metric("Total Subscriptions", f"{df_filtered['subscribed'].sum():,}")

st.markdown("---")

# --- BUSINESS QUESTIONS & VISUALIZATIONS ---

# Q1: Which job types have the highest subscription rate?
st.subheader("1. Which job types have the highest subscription rate?")
job_rates = df_filtered.groupby('job')['subscribed'].mean().reset_index()
job_rates['subscribed'] *= 100
job_rates = job_rates.sort_values(by='subscribed', ascending=False)

fig_job = px.bar(job_rates, x='job', y='subscribed', 
                 labels={'subscribed': 'Subscription Rate (%)', 'job': 'Job Category'},
                 color='subscribed', color_continuous_scale='Blues')
st.plotly_chart(fig_job, use_container_width=True)

# Q2: Is there a pattern between account balance and likelihood to subscribe?
st.subheader("2. Account Balance vs. Likelihood to Subscribe")
st.markdown("*(Y-axis capped at €10,000 to filter extreme outliers and improve readability)*")
fig_bal = px.box(df_filtered, x='y', y='balance', 
                 labels={'y': 'Did they subscribe?', 'balance': 'Average Yearly Balance (€)'},
                 color='y', color_discrete_map={'yes': '#2ca02c', 'no': '#d62728'})
fig_bal.update_yaxes(range=[-1000, 10000]) 
st.plotly_chart(fig_bal, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    # Q3: How does subscription rate differ across age groups?
    st.subheader("3. Subscription Rate by Age Group")
    age_rates = df_filtered.groupby('age_group', observed=False)['subscribed'].mean().reset_index()
    age_rates['subscribed'] *= 100
    
    fig_age = px.bar(age_rates, x='age_group', y='subscribed',
                     labels={'subscribed': 'Subscription Rate (%)', 'age_group': 'Age Group'},
                     color='age_group', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_age, use_container_width=True)

with col_b:
    # Q4: Does having an existing housing loan make someone less likely to take a new product?
    st.subheader("4. Impact of Existing Housing Loans")
    housing_rates = df_filtered.groupby('housing')['subscribed'].mean().reset_index()
    housing_rates['subscribed'] *= 100
    
    fig_housing = px.bar(housing_rates, x='housing', y='subscribed',
                         labels={'subscribed': 'Subscription Rate (%)', 'housing': 'Has Existing Housing Loan?'},
                         color='housing', color_discrete_map={'yes': '#ff7f0e', 'no': '#1f77b4'})
    st.plotly_chart(fig_housing, use_container_width=True)