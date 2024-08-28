from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from pymongo import MongoClient

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

# Endpoint for total quarterly sales
@app.get("/sales/quarterly/total/")
async def total_quarterly_sales(selected_quarter: str = Query(..., regex=r"^\d{4}-Q[1-4]$")):
    try:
        df = fetch_and_prepare_data()
        df['YearQuarter'] = df['Date'].dt.to_period('Q')

        # Filter the data for the selected quarter
        specific_quarter_data = df[df['YearQuarter'] == selected_quarter]

        if specific_quarter_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected quarter.")

        # Sum the sales from columns 'S-P1', 'S-P2', 'S-P3', 'S-P4'
        total_sales = specific_quarter_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        return {"total_sales": total_sales}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for quarterly sales by different products (Bar Chart)
@app.get("/sales/quarterly/by-products/")
async def sales_quarterly_by_products(selected_quarter: str = Query(..., regex=r"^\d{4}-Q[1-4]$")):
    try:
        df = fetch_and_prepare_data()
        df['YearQuarter'] = df['Date'].dt.to_period('Q')

        # Filter the data for the selected quarter
        specific_quarter_data = df[df['YearQuarter'] == selected_quarter]

        if specific_quarter_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected quarter.")

        # Sum the sales for each product
        product_sales = specific_quarter_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()

        # Plot the bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x=product_sales.index, y=product_sales.values, palette='Blues_d')
        plt.title(f'Sales Distribution by Products in {selected_quarter}')
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
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for quarterly quantity sales (Pie Chart)
@app.get("/sales/quarterly/quantity-pie/")
async def quantity_quarterly_pie_chart(selected_quarter: str = Query(..., regex=r"^\d{4}-Q[1-4]$")):
    try:
        df = fetch_and_prepare_data()
        df['YearQuarter'] = df['Date'].dt.to_period('Q')

        # Filter the data for the selected quarter
        specific_quarter_data = df[df['YearQuarter'] == selected_quarter]

        if specific_quarter_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected quarter.")

        # Sum the quantities for Q-P1 to Q-P4
        quantities = specific_quarter_data[['Q-P1', 'Q-P2', 'Q-P3', 'Q-P4']].sum()

        # Plot the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(quantities, labels=quantities.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        plt.title(f'Quantity Sales Distribution for {selected_quarter}')

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"quantity_sales_pie_chart": img_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for quarterly sales comparison (with structured data for chart)
@app.get("/sales/quarterly/comparison/")
async def quarterly_sales_comparison(selected_quarter: str = Query(..., regex=r"^\d{4}-Q[1-4]$")):
    try:
        df = fetch_and_prepare_data()
        df['YearQuarter'] = df['Date'].dt.to_period('Q')

        # Filter data for the selected quarter
        specific_quarter_data = df[df['YearQuarter'] == selected_quarter]

        if specific_quarter_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected quarter.")

        # Calculate total sales for the selected quarter
        total_sales_selected_quarter = specific_quarter_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        # Calculate the previous quarter
        prev_quarter_year = int(selected_quarter[:4])
        prev_quarter_num = int(selected_quarter[-1])
        if prev_quarter_num == 1:
            previous_quarter = f"{prev_quarter_year - 1}-Q4"
        else:
            previous_quarter = f"{prev_quarter_year}-Q{prev_quarter_num - 1}"

        # Filter data for the previous quarter
        previous_quarter_data = df[df['YearQuarter'] == previous_quarter]

        if previous_quarter_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the previous quarter.")

        # Calculate total sales for the previous quarter
        total_sales_previous_quarter = previous_quarter_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        # Calculate percentage change
        if total_sales_previous_quarter == 0:
            percentage_change = float('inf') if total_sales_selected_quarter != 0 else 0
        else:
            percentage_change = ((total_sales_selected_quarter - total_sales_previous_quarter) / total_sales_previous_quarter) * 100

        # Return both textual comparison and structured data for the chart
        return {
            "sales_comparison_text": (
                f"Sales for {selected_quarter}: ${total_sales_selected_quarter:.2f}\n"
                f"Sales for {previous_quarter}: ${total_sales_previous_quarter:.2f}\n"
                f"Change: {'Increase' if total_sales_selected_quarter > total_sales_previous_quarter else 'Decrease'}\n"
                f"Percentage Change: {percentage_change:.2f}%"
            ),
            "quarterly_comparison_chart_data": {
                "selected_quarter": total_sales_selected_quarter,
                "previous_quarter": total_sales_previous_quarter,
                "previous_quarter_label": previous_quarter
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for quarterly monthly sales comparison
@app.get("/sales/quarterly/monthly-comparison/")
async def quarterly_monthly_comparison(selected_quarter: str = Query(..., regex=r"^\d{4}-Q[1-4]$")):
    try:
        df = fetch_and_prepare_data()

        # Extract the year and quarter
        year = int(selected_quarter[:4])
        quarter = selected_quarter[-2:]

        # Define the months for each quarter
        quarter_months_map = {
            'Q1': [1, 2, 3],
            'Q2': [4, 5, 6],
            'Q3': [7, 8, 9],
            'Q4': [10, 11, 12]
        }

        # Get the months for the selected quarter
        if quarter not in quarter_months_map:
            raise HTTPException(status_code=400, detail="Invalid quarter format.")

        months = quarter_months_map[quarter]

        # Filter data for the selected months and year
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df_filtered = df[(df['Year'] == year) & (df['Month'].isin(months))]

        if df_filtered.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected quarter.")

        # Sum the sales for each month and each product
        monthly_sales = df_filtered.groupby('Month')[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()
        monthly_sales['Total'] = monthly_sales.sum(axis=1)

        # Prepare data for the frontend
        monthly_sales_chart = monthly_sales.reset_index().to_dict(orient='list')
        monthly_sales_data = {
            'months': monthly_sales.index.tolist(),
            'S-P1': monthly_sales['S-P1'].tolist(),
            'S-P2': monthly_sales['S-P2'].tolist(),
            'S-P3': monthly_sales['S-P3'].tolist(),
            'S-P4': monthly_sales['S-P4'].tolist(),
            'Total': monthly_sales['Total'].tolist()
        }

        return {"monthly_sales_chart": monthly_sales_chart, "monthly_sales_data": monthly_sales_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
