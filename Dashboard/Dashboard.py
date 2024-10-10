import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Custom color palette
palette = sns.color_palette("magma", as_cmap=True)

# Set style
sns.set(style='whitegrid')

# Helper functions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True)
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({"payment_value": "sum"})
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={"payment_value": "total_spend"}, inplace=True)
    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={"product_id": "product_count"}, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)
    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()
    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)
    return bystate_df, most_common_state

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "total_customer"}, inplace=True)
    most_common_city = bycity_df.loc[bycity_df['total_customer'].idxmax(), 'customer_city']
    bycity_df = bycity_df.sort_values(by='total_customer', ascending=False)
    return bycity_df, most_common_city

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()
    return order_status_df, most_common_status

# Load dataset
datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv('https://raw.githubusercontent.com/uray03/Analis_Data/main/Dashboard/all_data.csv')
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Convert columns to datetime
for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

# Filter Data
min_date = all_df["order_approved_at"].min().date()
max_date = all_df["order_approved_at"].max().date()

with st.sidebar:
    st.title("E-Commerce Dashboard")
    st.image("logo.png")  # Ensure the image path is correct or upload an image
    start_date, end_date = st.date_input(
        label="Filter by Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.markdown("---")
    st.caption("Custom controls can be added here")

# Filter the dataframe based on selected date range
main_df = all_df[(all_df["order_approved_at"].dt.date >= start_date) & (all_df["order_approved_at"].dt.date <= end_date)]

# Create DataFrames
daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
city, most_common_city = create_bycity_df(main_df)
order_status, common_status = create_order_status(main_df)

# E-commerce Income
st.subheader("E-commerce Income")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="pt_BR")
    st.metric("Total Income", total_spend)

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.metric("Average Income", avg_spend)

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x="order_approved_at", y="total_spend", data=sum_spend_df, marker='o', color="purple", ax=ax)
ax.set_title("Daily Revenue Trend", fontsize=18, fontweight='bold')
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Total Revenue (BRL)", fontsize=14)
plt.xticks(rotation=45)
st.pyplot(fig)

# Product Sales
st.subheader("Product Sales")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Product Sales: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Item Sales: **{avg_items:.2f}**")

fig, ax = plt.subplots(1, 2, figsize=(20, 10))

# Top 5 Product Categories
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="Blues_d", ax=ax[0])
ax[0].set_title("Top 5 Product Categories", fontsize=16, fontweight='bold')

# Bottom 5 Product Categories
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.tail(5), palette="Reds_d", ax=ax[1])
ax[1].set_title("Bottom 5 Product Categories", fontsize=16, fontweight='bold')
st.pyplot(fig)

# Customer Distribution
st.subheader("Customer Distribution")
tab1, tab2, tab3 = st.tabs(["State", "Top 10 City", "Order Status"])

with tab1:
    st.markdown(f"Most Common State: **{most_common_state}**")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(y=state.customer_state, x=state.customer_count, palette="magma", ax=ax)
    ax.set_title("Customers by State", fontsize=18, fontweight='bold')
    ax.set_xlabel("Number of Customers", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    st.markdown(f"Most Common City: **{most_common_city}**")
    top_10_cities = city.head(10)
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(y=top_10_cities.customer_city, x=top_10_cities.total_customer, palette="coolwarm", ax=ax)
    ax.set_title("Top 10 Cities by Customer Count", fontsize=18, fontweight='bold')
    ax.set_xlabel("Number of Customers", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    st.markdown(f"Most Common Order Status: **{common_status}**")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(y=order_status.index, x=order_status.values, palette="plasma", ax=ax)
    ax.set_title("Order Status Distribution", fontsize=18, fontweight='bold')
    ax.set_xlabel("Number of Orders", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    st.pyplot(fig)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("Created by **Uray Hafizh** © 2024 - Custom Data Solutions")
