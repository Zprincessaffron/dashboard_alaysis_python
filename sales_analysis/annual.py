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

    df.drop(['_id'], axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    
    df.dropna(subset=['Date'], inplace=True)
    return df

@app.get("/sales/annual/total/")
async def annual_total_sales(selected_year: str = Query(..., regex=r"^\d{4}$")):
    try:
        df = fetch_and_prepare_data()
        start_date = pd.Timestamp(f'{selected_year}-01-01')
        end_date = pd.Timestamp(f'{selected_year}-12-31')

        annual_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if annual_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected year.")

        total_sales = annual_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        return {"total_sales": total_sales}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/annual/by-products/")
async def annual_sales_by_products(selected_year: str = Query(..., regex=r"^\d{4}$")):
    try:
        df = fetch_and_prepare_data()
        start_date = pd.Timestamp(f'{selected_year}-01-01')
        end_date = pd.Timestamp(f'{selected_year}-12-31')

        annual_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if annual_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected year.")

        product_sales = annual_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()

        plt.figure(figsize=(10, 6))
        sns.barplot(x=product_sales.index, y=product_sales.values, palette='Blues_d')
        plt.title(f'Sales Distribution by Products in {selected_year}')
        plt.xlabel('Product Categories')
        plt.ylabel('Total Sales')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"sales_by_products_chart": img_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/annual/quantity-pie/")
async def annual_quantity_pie_chart(selected_year: str = Query(..., regex=r"^\d{4}$")):
    try:
        df = fetch_and_prepare_data()
        start_date = pd.Timestamp(f'{selected_year}-01-01')
        end_date = pd.Timestamp(f'{selected_year}-12-31')

        annual_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if annual_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected year.")

        quantities = annual_data[['Q-P1', 'Q-P2', 'Q-P3', 'Q-P4']].sum()

        plt.figure(figsize=(8, 8))
        plt.pie(quantities, labels=quantities.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        plt.title(f'Quantity Sales Distribution for {selected_year}')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"quantity_sales_pie_chart": img_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/annual/comparison/")
async def annual_sales_comparison(selected_year: str = Query(..., regex=r"^\d{4}$")):
    try:
        df = fetch_and_prepare_data()
        start_date = pd.Timestamp(f'{selected_year}-01-01')
        end_date = pd.Timestamp(f'{selected_year}-12-31')
        prev_year = str(int(selected_year) - 1)
        prev_start_date = pd.Timestamp(f'{prev_year}-01-01')
        prev_end_date = pd.Timestamp(f'{prev_year}-12-31')

        annual_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        if annual_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected year.")

        total_sales_selected_year = annual_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        previous_year_data = df[(df['Date'] >= prev_start_date) & (df['Date'] <= prev_end_date)]
        if previous_year_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the previous year.")

        total_sales_previous_year = previous_year_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        percentage_change = 0
        if total_sales_previous_year > 0:
            percentage_change = ((total_sales_selected_year - total_sales_previous_year) / total_sales_previous_year) * 100

        comparison_text = (
            f"Sales for {selected_year}: ${total_sales_selected_year:.2f}\n"
            f"Sales for {prev_year}: ${total_sales_previous_year:.2f}\n"
            f"Change: {'Increase' if total_sales_selected_year > total_sales_previous_year else 'Decrease'}\n"
            f"Percentage Change: {percentage_change:.2f}%"
        )

        # Data for bar chart
        comparison_chart_data = {
            "years": [selected_year, prev_year],
            "total_sales": [total_sales_selected_year, total_sales_previous_year]
        }

        return {
            "sales_comparison_text": comparison_text,
            "comparison_chart_data": comparison_chart_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sales/annual/monthly-comparison/")
async def annual_monthly_comparison(selected_year: str = Query(..., regex=r"^\d{4}$")):
    try:
        df = fetch_and_prepare_data()
        start_date = pd.Timestamp(f'{selected_year}-01-01')
        end_date = pd.Timestamp(f'{selected_year}-12-31')

        annual_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        if annual_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected year.")

        # Aggregate monthly sales
        annual_data['Month'] = annual_data['Date'].dt.to_period('M')
        monthly_sales = annual_data.groupby('Month')[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()
        monthly_sales['Total'] = monthly_sales.sum(axis=1)

        # Prepare the data for JSON response
        monthly_sales_json = {
            "months": [period.strftime('%B %Y') for period in monthly_sales.index],
            "sales": {
                "S-P1": monthly_sales['S-P1'].tolist(),
                "S-P2": monthly_sales['S-P2'].tolist(),
                "S-P3": monthly_sales['S-P3'].tolist(),
                "S-P4": monthly_sales['S-P4'].tolist(),
                "Total": monthly_sales['Total'].tolist()
            }
        }

        # Create monthly sales comparison chart
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_sales.index.astype(str), monthly_sales['Total'], marker='o', color='skyblue', linestyle='-', label='Total Sales')
        plt.title(f'Monthly Sales Comparison in {selected_year}')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)
        plt.grid(True)

        for i, value in enumerate(monthly_sales['Total']):
            plt.text(i, value, f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        plt.legend()

        # Save the plot as a base64-encoded image
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {
            "chart_data": monthly_sales_json,
            "sales_chart_base64": img_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
