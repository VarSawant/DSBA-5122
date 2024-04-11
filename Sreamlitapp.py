import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go


st.title("Data App Assignment")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

# creating sales category 
category = df['Category'].unique()
option = st.selectbox('Select Category', category)


selected_category_df = df[df['Category']==option]

sub_category = selected_category_df['Sub_Category'].unique()
sub_option = st.multiselect('Select Sub Category', sub_category)

if sub_option:
    selected_sub_category_df = selected_category_df[selected_category_df['Sub_Category'].isin(sub_option)]
   
    sub_category_sales_by_month = selected_sub_category_df.filter(items=['Sales','Sub_Category'])
    
    #Sub category sales by month
    sub_category_sales_by_month = selected_sub_category_df.groupby('Sub_Category').resample('ME').sum()
    sub_category_sales_by_month = sub_category_sales_by_month[['Sales','Profit','Discount']]
    #print(type(sub_category_sales_by_month))
    sub_category_sales_by_month.reset_index(inplace=True)
   

    # Traces for each category
    traces = []
    for sub_category in sub_category_sales_by_month['Sub_Category'].unique():
        sub_category_df = sub_category_sales_by_month[sub_category_sales_by_month['Sub_Category'] == sub_category]
        trace = go.Scatter(x=sub_category_df['Order_Date'], y=sub_category_df['Sales'], mode='lines', name=sub_category)
        traces.append(trace)

    # Create the figure
    fig = go.Figure(data=traces)

    # Add title and labels
    fig.update_layout(title='Monthly Sales by selected Subcategory',
                      xaxis_title='Month',
                      yaxis_title='Sales')


    # Displaying the chart in Streamlit
    st.plotly_chart(fig)

    total_sales = sub_category_sales_by_month['Sales'].sum()
    total_profit = sub_category_sales_by_month['Profit'].sum()
    avg_profit = sub_category_sales_by_month['Profit'].mean()
    overall_avg_profit = df['Profit'].mean()
    profit_diff = total_profit / overall_avg_profit
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Overall Profit Margin (%)", f"{(total_profit/total_sales):.2%}", f"{profit_diff:,.2%}" )
