# Customer Segmentation Analysis Dashboard

## Overview
This interactive Streamlit dashboard visualizes customer segmentation analysis, highlighting differences between high-value loyalists (16%) and occasional buyers (84%). The analysis is based on RFM (Recency, Frequency, Monetary) metrics and additional derived features.

## Features
- **Interactive Filtering**: Filter by customer segment and date range
- **Key Metrics**: View total customers, revenue, average order value, and purchase frequency
- **Segment Visualization**: Visual comparison of customer segments with donut and radar charts
- **RFM Analysis**: Interactive scatter plot of monetary value vs. frequency
- **Feature Distribution**: Compare any feature across segments with histograms and box plots
- **Time Series Analysis**: Track revenue, customer activity, and order value over time

## Getting Started

### Prerequisites
- Python 3.6+
- Required packages: streamlit, pandas, numpy, plotly, matplotlib, seaborn

### Installation
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
streamlit run streamlit_app.py
```

### Data Requirements
The dashboard expects two dataframes:
1. `data`: Contains transaction data with columns:
   - customer_id
   - order_date (datetime)
   - purchase_amount
   - currency

2. `customer_features_clustered`: Contains customer metrics with columns:
   - customer_id
   - recency
   - frequency
   - monetary
   - purchase_variability
   - first_purchase (datetime)
   - last_purchase (datetime)
   - tenure_days
   - purchases_per_day
   - spend_per_day
   - recency_ratio
   - customer_value_score
   - cluster (binary: 0 or 1)

## Deployment
This dashboard can be deployed on Streamlit Community Cloud by connecting this GitHub repository to your Streamlit account.

## Acknowledgements
- This dashboard was created as part of a customer segmentation analysis project
- Visualization powered by Plotly and Streamlit
