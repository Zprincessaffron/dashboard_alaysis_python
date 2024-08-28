from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from pymongo import MongoClient

# Initialize FastAPI
app = FastAPI()
# CORS setup

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to a specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['Sales']
collection = db['Sales_data']

# Helper function to fetch and prepare data from MongoDB
def fetch_and_prepare_data():
    all_documents = collection.find()
    data_list = list(all_documents)
    df = pd.DataFrame(data_list)

    # Drop '_id' column and handle date formatting
    df.drop(['_id'], axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    
    # Drop rows with invalid dates
    df.dropna(subset=['Date'], inplace=True)
    return df

# Endpoint for total sales
@app.get("/sales/total/")
async def total_sales(selected_month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        df = fetch_and_prepare_data()
        df['YearMonth'] = df['Date'].dt.to_period('M')

        # Log the filtered dataframe for debugging
        print(f"Filtered data for {selected_month}:")
        print(df[df['YearMonth'] == selected_month])

        # Filter the data for the selected month
        specific_month_data = df[df['YearMonth'] == selected_month]

        if specific_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected month.")

        # Sum the sales from columns 'S-P1', 'S-P2', 'S-P3', 'S-P4'
        total_sales = specific_month_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        return {"total_sales": total_sales}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for sales by different products (Bar Chart)
@app.get("/sales/by-products/")
async def sales_by_products(selected_month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        df = fetch_and_prepare_data()
        df['YearMonth'] = df['Date'].dt.to_period('M')

        # Filter the data for the selected month
        specific_month_data = df[df['YearMonth'] == selected_month]

        if specific_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected month.")

        # Sum the sales for each product
        product_sales = specific_month_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()

        # Plot the bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x=product_sales.index, y=product_sales.values, palette='Blues_d')
        plt.title(f'Sales Distribution by Products in {selected_month}')
        plt.xlabel('Product Categories')
        plt.ylabel('Total Sales')

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"sales_by_products_chart": img_base64}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for quantity sales (Pie Chart)
@app.get("/sales/quantity-pie/")
async def quantity_pie_chart(selected_month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        df = fetch_and_prepare_data()
        df['YearMonth'] = df['Date'].dt.to_period('M')

        # Filter the data for the selected month
        specific_month_data = df[df['YearMonth'] == selected_month]

        if specific_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected month.")

        # Sum the quantities for Q-P1 to Q-P4
        quantities = specific_month_data[['Q-P1', 'Q-P2', 'Q-P3', 'Q-P4']].sum()

        # Plot the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(quantities, labels=quantities.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        plt.title(f'Quantity Sales Distribution for {selected_month}')

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"quantity_sales_pie_chart": img_base64}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/weekly/")
async def weekly_sales(selected_month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        df = fetch_and_prepare_data()  # Replace with your data loading logic
        df['YearMonth'] = df['Date'].dt.to_period('M')

        # Filter data for the selected month
        specific_month_data = df[df['YearMonth'] == selected_month]

        if specific_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected month.")

        # Set 'Date' as index
        specific_month_data.set_index('Date', inplace=True)

        # Initialize the list with zero for the starting point
        weekly_totals = [0]
        weeks = [f"Start of {selected_month}"]

        # Get the start and end date of the month
        start_date = specific_month_data.index.min().normalize()
        end_date = start_date + pd.DateOffset(weeks=1) - pd.DateOffset(days=1)

        # Calculate sales for the first week (from start_date to end_date)
        if start_date <= specific_month_data.index.max():
            week_data = specific_month_data[start_date:end_date]
            weekly_sales = week_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()
            weekly_totals.append(weekly_sales)
            weeks.append(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        start_date = end_date + pd.DateOffset(days=1)

        # Calculate weekly sales for each week of the month
        while start_date <= specific_month_data.index.max():
            end_date = start_date + pd.DateOffset(weeks=1) - pd.DateOffset(days=1)

            if end_date > specific_month_data.index.max():
                end_date = specific_month_data.index.max()

            week_data = specific_month_data[start_date:end_date]
            weekly_sales = week_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()
            weekly_totals.append(weekly_sales)
            weeks.append(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

            start_date = end_date + pd.DateOffset(days=1)

        # Create the line graph
        plt.figure(figsize=(12, 6))
        plt.plot(weeks, weekly_totals, marker='o', color='blue', linestyle='-', linewidth=2)

        plt.title(f'Weekly Sales in {selected_month}')
        plt.xlabel('Weeks')
        plt.ylabel('Weekly Sales')

        for i, v in enumerate(weekly_totals):
            plt.text(i, v, str(int(v)), ha='center', va='bottom', fontsize=12)

        plt.grid(True)
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"weekly_sales_chart": img_base64}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/comparison/")
async def sales_comparison(selected_month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        df = fetch_and_prepare_data()
        df['YearMonth'] = df['Date'].dt.to_period('M')

        # Filter data for the selected month
        specific_month_data = df[df['YearMonth'] == selected_month]

        if specific_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected month.")

        # Calculate total sales for the selected month
        total_sales_selected_month = specific_month_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        # Calculate the previous month
        previous_month = (pd.to_datetime(f"{selected_month}-01") - pd.DateOffset(months=1)).strftime('%Y-%m')

        # Filter data for the previous month
        previous_month_data = df[df['YearMonth'] == previous_month]

        if previous_month_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the previous month.")

        # Calculate total sales for the previous month
        total_sales_previous_month = previous_month_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        # Calculate percentage change
        if total_sales_previous_month == 0:
            percentage_change = float('inf') if total_sales_selected_month != 0 else 0
        else:
            percentage_change = ((total_sales_selected_month - total_sales_previous_month) / total_sales_previous_month) * 100

        comparison_text = (
            f"Sales for {selected_month}: ${total_sales_selected_month:.2f}\n"
            f"Sales for {previous_month}: ${total_sales_previous_month:.2f}\n"
            f"Change: {'Increase' if total_sales_selected_month > total_sales_previous_month else 'Decrease'}\n"
            f"Percentage Change: {percentage_change:.2f}%"
        )

        return {"sales_comparison_text": comparison_text}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
