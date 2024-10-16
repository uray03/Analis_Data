import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import ssl

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Set uniform style and color palette
sns.set(style='whitegrid')

# Helper functions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True)
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({"payment_value": "sum"}).reset_index()
    sum_spend_df.rename(columns={"payment_value": "total_spend"}, inplace=True)
    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={"product_id": "product_count"}, inplace=True)
    return sum_order_items_df.sort_values(by='product_count', ascending=False)

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    return review_scores, review_scores.idxmax()

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bystate_df.sort_values(by='customer_count', ascending=False), bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "total_customer"}, inplace=True)
    return bycity_df.sort_values(by='total_customer', ascending=False), bycity_df.loc[bycity_df['total_customer'].idxmax(), 'customer_city']

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    return order_status_df, order_status_df.idxmax()

# Load dataset
datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv('https://raw.githubusercontent.com/uray03/Analis_Data/main/Dashboard/all_data.csv')
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Convert columns to datetime
for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

# Filter Data
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.title("Dicoding E-Commerce")
    st.image('https://raw.githubusercontent.com/uray03/Analis_Data/blob/main/Dashboard/logo.png')
    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]

# Create DataFrames for analysis
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
    st.markdown(f"Total Income: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.markdown(f"Average Income: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker='o',
    color="#FE0000",
    linewidth=2
)
ax.set_title("Monthly Total Income", fontsize=20, weight='bold')
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Total Income (BRL)", fontsize=14)
ax.tick_params(axis="x", rotation=45, labelsize=12)
ax.tick_params(axis="y", labelsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig)

# Visualisasi top 10 kategori produk terlaris
products_url = 'https://raw.githubusercontent.com/uray03/Submission_analisis_data_python/main/.ipynb_checkpoints/Data/E-Commerce_Public_Dataset/products_dataset.csv'
products_df = pd.read_csv(products_url)

# Menggabungkan kedua DataFrame
merged_df = main_df.merge(products_df, on='product_id')

# Menghitung jumlah penjualan berdasarkan kategori produk
top_categories = merged_df['product_category_name_english'].value_counts().head(10)

# Visualisasi Top 10 Kategori Produk Terlaris
st.title('Top 10 Kategori Produk Terlaris')
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x=top_categories.values, y=top_categories.index, palette='viridis', ax=ax)
ax.set_title('Top 10 Kategori Produk Terlaris', fontsize=16)
ax.set_xlabel('Jumlah Penjualan', fontsize=14)
ax.set_ylabel('Kategori Produk', fontsize=14)
st.pyplot(fig)

# Visualisasi distribusi status pesanan
st.title('Distribusi Status Pesanan')
fig, ax = plt.subplots(figsize=(10, 6))
order_status_distribution = main_df['order_status'].value_counts()
order_status_distribution.plot(kind='bar', color=sns.color_palette('Set2'), ax=ax)
ax.set_title('Distribusi Status Pesanan')
ax.set_xlabel('Status Pesanan')
ax.set_ylabel('Jumlah Pesanan')
st.pyplot(fig)

# Product Sales - Top 5 and Bottom 5 Products
st.subheader("Product Sales")

def plot_top_bottom_5_products(df):
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

    # Top 5 Products
    sns.barplot(x="product_count", y="product_category_name_english", 
                data=df.head(5), palette=sns.color_palette("viridis", 5), ax=ax[0])
    ax[0].set_xlabel("Number of Products Sold", fontsize=14)
    ax[0].set_title("Top 5 Best-Selling Products", fontsize=20, weight='bold')
    ax[0].tick_params(axis='y', labelsize=12)
    ax[0].tick_params(axis='x', labelsize=12)
    ax[0].bar_label(ax[0].containers[0], fmt='%d', label_type='edge', fontsize=12)

    # Bottom 5 Products
    sns.barplot(x="product_count", y="product_category_name_english", 
                data=df.sort_values(by="product_count", ascending=True).head(5), palette=sns.color_palette("viridis_r", 5), ax=ax[1])
    ax[1].set_xlabel("Number of Products Sold", fontsize=14)
    ax[1].set_title("Bottom 5 Least-Selling Products", fontsize=20, weight='bold')
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].tick_params(axis='y', labelsize=12)
    ax[1].tick_params(axis='x', labelsize=12)
    ax[1].bar_label(ax[1].containers[0], fmt='%d', label_type='edge', fontsize=12)

    plt.suptitle("Sales Performance of Product Categories", fontsize=26, weight='bold')
    plt.subplots_adjust(top=0.85)
    st.pyplot(fig)

plot_top_bottom_5_products(sum_order_items_df)

# Customer Distribution
st.subheader("Customer Distribution")
tab1, tab2, tab3 = st.tabs(["State", "Top 10 City", "Order Status"])

with tab1:
    st.markdown(f"Most Common State: **{most_common_state}**")
    fig, ax = plt.subplots(figsize=(12, 8))

    color_palette = ["#FF4500" if state == most_common_state else "#87CEFA" for state in state['customer_state']]

    sns.barplot(x='customer_count', y='customer_state', data=state, palette=color_palette, orient='h', ax=ax)
    ax.set_title("Customer Distribution by State", fontsize=16)
    ax.set_xlabel("Number of Customers", fontsize=14)
    ax.set_ylabel("States", fontsize=14)
    st.pyplot(fig)

with tab2:
    st.markdown(f"Most Common City: **{most_common_city}**")
    fig, ax = plt.subplots(figsize=(12, 8))

    color_palette = ["#FF4500" if city == most_common_city else "#87CEFA" for city in city['customer_city']]

    sns.barplot(x='total_customer', y='customer_city', data=city, palette=color_palette, orient='h', ax=ax)
    ax.set_title("Customer Distribution by City", fontsize=16)
    ax.set_xlabel("Number of Customers", fontsize=14)
    ax.set_ylabel("Cities", fontsize=14)
    st.pyplot(fig)

with tab3:
    st.markdown(f"Most Common Order Status: **{common_status}**")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=order_status.index, y=order_status.values, palette='viridis', ax=ax)
    ax.set_title("Distribution of Order Status", fontsize=16)
    ax.set_xlabel("Order Status", fontsize=14)
    ax.set_ylabel("Count", fontsize=14)
    st.pyplot(fig)

# Product Review Analysis
st.subheader("Product Review Analysis")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=review_score.index, y=review_score.values, palette='viridis', ax=ax)
ax.set_title("Distribution of Review Scores", fontsize=16)
ax.set_xlabel("Review Score", fontsize=14)
ax.set_ylabel("Count", fontsize=14)
st.pyplot(fig)
