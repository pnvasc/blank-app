import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="Customer Segmentation Analysis",
    page_icon="📊",
    layout="wide"
)

# Load your dataframes
# Assuming these are already loaded in your environment
# If not, you'll need to add code to load them from files
data = pd.read_csv('NoA-Connect-JrDataScience-Case(in).csv')  # Original dataframe with order_date, currency, and purchase_amount
customer_features_clustered = pd.read_csv('customer_features_clustered.csv')  # Dataframe with features and clusters
data['order_date'] = pd.to_datetime(data['order_date'])

# Make sure date columns in customer_features are also datetime if needed
if 'first_purchase' in customer_features_clustered.columns:
    customer_features_clustered['first_purchase'] = pd.to_datetime(customer_features_clustered['first_purchase'])
    
if 'last_purchase' in customer_features_clustered.columns:
    customer_features_clustered['last_purchase'] = pd.to_datetime(customer_features_clustered['last_purchase'])

# Title and description
st.title("Customer Segmentation Analysis Dashboard")
st.markdown("""
This dashboard provides insights into customer segmentation analysis:
- **High-Value Loyalists (16%)**: Frequent buyers with high spending
- **Occasional Buyers (84%)**: Infrequent buyers with lower spending
""")

# Sidebar for filtering
st.sidebar.header("Filters")

# Filter by cluster
cluster_filter = st.sidebar.multiselect(
    "Select Customer Segments",
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: "High-Value Loyalists" if x == 1 else "Occasional Buyers"
)

# Filter by time period
min_date = data['order_date'].min().date()
max_date = data['order_date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = data[(data['order_date'].dt.date >= start_date) & 
                         (data['order_date'].dt.date <= end_date)]
    # Assuming there's a customer_id in both dataframes to join on
    filtered_customers = customer_features_clustered[
        customer_features_clustered['customer_id'].isin(filtered_data['customer_id'].unique()) &
        customer_features_clustered['cluster'].isin(cluster_filter)
    ]
else:
    filtered_data = data.copy()
    filtered_customers = customer_features_clustered[
        customer_features_clustered['cluster'].isin(cluster_filter)
    ]

# Main dashboard
# Top row with KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Customers",
        f"{filtered_customers['customer_id'].nunique():,}",
        f"{filtered_customers['customer_id'].nunique() / customer_features_clustered['customer_id'].nunique() * 100:.1f}%"
    )

with col2:
    st.metric(
        "Total Revenue",
        f"${filtered_data['purchase_amount'].sum():,.2f}",
        f"{filtered_data['purchase_amount'].sum() / data['purchase_amount'].sum() * 100:.1f}%"
    )

with col3:
    avg_order_value = filtered_data['purchase_amount'].mean()
    overall_avg = data['purchase_amount'].mean()
    st.metric(
        "Average Order Value",
        f"${avg_order_value:.2f}",
        f"{(avg_order_value - overall_avg) / overall_avg * 100:.1f}%"
    )

with col4:
    avg_frequency = filtered_customers['frequency'].mean()
    overall_freq = customer_features_clustered['frequency'].mean()
    st.metric(
        "Average Purchase Frequency",
        f"{avg_frequency:.2f}",
        f"{(avg_frequency - overall_freq) / overall_freq * 100:.1f}%"
    )

# Row with cluster distribution and monetary value by cluster
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Customer Segment Distribution")
    
    # Count customers in each cluster
    cluster_counts = filtered_customers['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    cluster_counts['Segment'] = cluster_counts['Cluster'].map({
        1: "High-Value Loyalists",
        0: "Occasional Buyers"
    })
    cluster_counts['Percentage'] = cluster_counts['Count'] / cluster_counts['Count'].sum() * 100
    
    # Create donut chart
    fig = px.pie(
        cluster_counts, 
        values='Count', 
        names='Segment',
        hole=0.4,
        color='Segment',
        color_discrete_map={
            "High-Value Loyalists": "#1f77b4",
            "Occasional Buyers": "#ff7f0e"
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with row2_col2:
    st.subheader("Average Metrics by Segment")
    
    # Calculate average metrics for each cluster
    cluster_metrics = filtered_customers.groupby('cluster').agg({
        'monetary': 'mean',
        'frequency': 'mean',
        'recency': 'mean',
        'customer_value_score': 'mean'
    }).reset_index()
    
    cluster_metrics['Segment'] = cluster_metrics['cluster'].map({
        1: "High-Value Loyalists",
        0: "Occasional Buyers"
    })
    
    # Create radar chart
    categories = ['Monetary Value', 'Purchase Frequency', 'Recency', 'Customer Value Score']
    
    fig = go.Figure()
    
    for i, row in cluster_metrics.iterrows():
        # Normalize values for better visualization
        monetary_norm = row['monetary'] / cluster_metrics['monetary'].max()
        frequency_norm = row['frequency'] / cluster_metrics['frequency'].max()
        # Invert recency so lower is better
        recency_norm = 1 - (row['recency'] / cluster_metrics['recency'].max())
        value_norm = row['customer_value_score'] / cluster_metrics['customer_value_score'].max()
        
        fig.add_trace(go.Scatterpolar(
            r=[monetary_norm, frequency_norm, recency_norm, value_norm],
            theta=categories,
            fill='toself',
            name=row['Segment'],
            line_color="#1f77b4" if row['cluster'] == 1 else "#ff7f0e"
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


# Row with feature distributions
st.subheader("Feature Distributions by Segment")

# Select feature for histogram
selected_feature = st.selectbox(
    "Select Feature to Compare",
    options=[
        'monetary', 'frequency', 'recency', 'purchase_variability',
        'tenure_days', 'purchases_per_day', 'spend_per_day', 
        'recency_ratio', 'customer_value_score'
    ],
    format_func=lambda x: {
        'monetary': 'Total Spend ($)',
        'frequency': 'Purchase Frequency',
        'recency': 'Days Since Last Purchase',
        'purchase_variability': 'Purchase Variability',
        'tenure_days': 'Customer Tenure (days)',
    }[x]
)

# Create a distribution plot
fig = px.histogram(
    filtered_customers,
    x=selected_feature,
    color='cluster',
    marginal="box",
    barmode="overlay",
    histnorm="percent",
    color_discrete_map={1: "#1f77b4", 0: "#ff7f0e"},
    labels={
        'cluster': 'Customer Segment'
    },
    category_orders={"cluster": [1, 0]}
)

# Update legend labels
fig.update_layout(
    legend_title="Customer Segment",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    height=400
)

# Update legend item names
fig.for_each_trace(
    lambda t: t.update(
        name="High-Value Loyalists" if t.name == "1" else "Occasional Buyers" if t.name == "0" else t.name
    )
)

st.plotly_chart(fig, use_container_width=True)

# Time series analysis
st.subheader("Purchase Patterns Over Time")

# Group data by month and cluster
filtered_data_with_cluster = filtered_data.merge(
    customer_features_clustered[['customer_id', 'cluster']],
    on='customer_id',
    how='left'
)

filtered_data_with_cluster['year_month'] = filtered_data_with_cluster['order_date'].dt.to_period('M')
monthly_data = filtered_data_with_cluster.groupby(['year_month', 'cluster']).agg({
    'purchase_amount': ['sum', 'mean'],
    'customer_id': 'nunique',
    'order_date': 'count'
}).reset_index()

monthly_data.columns = ['year_month', 'cluster', 'total_revenue', 'avg_order_value', 'unique_customers', 'order_count']
monthly_data['year_month'] = monthly_data['year_month'].dt.to_timestamp()

# Tab layout for time series visualization
ts_tab1, ts_tab2, ts_tab3 = st.tabs(["Revenue Trends", "Customer Activity", "Average Order Value"])

with ts_tab1:
    # Revenue over time by segment
    revenue_fig = px.line(
        monthly_data,
        x='year_month',
        y='total_revenue',
        color='cluster',
        color_discrete_map={1: "#1f77b4", 0: "#ff7f0e"},
        labels={
            'year_month': 'Month',
            'total_revenue': 'Total Revenue ($)',
            'cluster': 'Customer Segment'
        }
    )
    
    revenue_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Revenue ($)",
        legend_title="Customer Segment",
        hovermode="x unified"
    )
    
    # Update legend item names
    revenue_fig.for_each_trace(
        lambda t: t.update(
            name="High-Value Loyalists" if t.name == "1" else "Occasional Buyers" if t.name == "0" else t.name
        )
    )
    
    st.plotly_chart(revenue_fig, use_container_width=True)

with ts_tab2:
    # Active customers over time by segment
    customers_fig = px.line(
        monthly_data,
        x='year_month',
        y='unique_customers',
        color='cluster',
        color_discrete_map={1: "#1f77b4", 0: "#ff7f0e"},
        labels={
            'year_month': 'Month',
            'unique_customers': 'Active Customers',
            'cluster': 'Customer Segment'
        }
    )
    
    customers_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Active Customers",
        legend_title="Customer Segment",
        hovermode="x unified"
    )
    
    # Update legend item names
    customers_fig.for_each_trace(
        lambda t: t.update(
            name="High-Value Loyalists" if t.name == "1" else "Occasional Buyers" if t.name == "0" else t.name
        )
    )
    
    st.plotly_chart(customers_fig, use_container_width=True)

with ts_tab3:
    # Average order value over time by segment
    aov_fig = px.line(
        monthly_data,
        x='year_month',
        y='avg_order_value',
        color='cluster',
        color_discrete_map={1: "#1f77b4", 0: "#ff7f0e"},
        labels={
            'year_month': 'Month',
            'avg_order_value': 'Average Order Value ($)',
            'cluster': 'Customer Segment'
        }
    )
    
    aov_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Order Value ($)",
        legend_title="Customer Segment",
        hovermode="x unified"
    )
    
    # Update legend item names
    aov_fig.for_each_trace(
        lambda t: t.update(
            name="High-Value Loyalists" if t.name == "1" else "Occasional Buyers" if t.name == "0" else t.name
        )
    )
    
    st.plotly_chart(aov_fig, use_container_width=True)

# Show raw data tables
if st.checkbox("Show Raw Data"):
    tab1, tab2 = st.tabs(["Customer Metrics", "Transaction Data"])
    
    with tab1:
        st.dataframe(filtered_customers)
    
    with tab2:
        st.dataframe(filtered_data)

# Add a footer
st.markdown("---")
st.markdown("Customer Segmentation Analysis Dashboard | Created with Streamlit")