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

@app.get("/sales/halfyearly/total/")
async def halfyearly_total_sales(selected_halfyear: str = Query(..., regex=r"^\d{4}-H[12]$")):
    try:
        df = fetch_and_prepare_data()
        if selected_halfyear == "2011-H1":
            start_date = pd.Timestamp('2011-01-01')
            end_date = pd.Timestamp('2011-06-30')
        else:
            start_date = pd.Timestamp('2011-07-01')
            end_date = pd.Timestamp('2011-12-31')

        halfyear_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected half-year.")

        total_sales = halfyear_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        return {"total_sales": total_sales}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/halfyearly/by-products/")
async def halfyearly_sales_by_products(selected_halfyear: str = Query(..., regex=r"^\d{4}-H[12]$")):
    try:
        df = fetch_and_prepare_data()
        if selected_halfyear == "2011-H1":
            start_date = pd.Timestamp('2011-01-01')
            end_date = pd.Timestamp('2011-06-30')
        else:
            start_date = pd.Timestamp('2011-07-01')
            end_date = pd.Timestamp('2011-12-31')

        halfyear_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected half-year.")

        product_sales = halfyear_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()

        plt.figure(figsize=(10, 6))
        sns.barplot(x=product_sales.index, y=product_sales.values, palette='Blues_d')
        plt.title(f'Sales Distribution by Products in {selected_halfyear}')
        plt.xlabel('Product Categories')
        plt.ylabel('Total Sales')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"sales_by_products_chart": img_base64}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/halfyearly/quantity-pie/")
async def halfyearly_quantity_pie_chart(selected_halfyear: str = Query(..., regex=r"^\d{4}-H[12]$")):
    try:
        df = fetch_and_prepare_data()
        if selected_halfyear == "2011-H1":
            start_date = pd.Timestamp('2011-01-01')
            end_date = pd.Timestamp('2011-06-30')
        else:
            start_date = pd.Timestamp('2011-07-01')
            end_date = pd.Timestamp('2011-12-31')

        halfyear_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected half-year.")

        quantities = halfyear_data[['Q-P1', 'Q-P2', 'Q-P3', 'Q-P4']].sum()

        plt.figure(figsize=(8, 8))
        plt.pie(quantities, labels=quantities.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        plt.title(f'Quantity Sales Distribution for {selected_halfyear}')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"quantity_sales_pie_chart": img_base64}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/halfyearly/comparison/")
async def halfyearly_sales_comparison(selected_halfyear: str = Query(..., regex=r"^\d{4}-H[12]$")):
    try:
        df = fetch_and_prepare_data()
        if selected_halfyear == "2011-H1":
            start_date = pd.Timestamp('2011-01-01')
            end_date = pd.Timestamp('2011-06-30')
            prev_start_date = pd.Timestamp('2010-07-01')
            prev_end_date = pd.Timestamp('2010-12-31')
        else:
            start_date = pd.Timestamp('2011-07-01')
            end_date = pd.Timestamp('2011-12-31')
            prev_start_date = pd.Timestamp('2011-01-01')
            prev_end_date = pd.Timestamp('2011-06-30')

        halfyear_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        if halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected half-year.")

        total_sales_selected_halfyear = halfyear_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        previous_halfyear_data = df[(df['Date'] >= prev_start_date) & (df['Date'] <= prev_end_date)]
        if previous_halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the previous half-year.")

        total_sales_previous_halfyear = previous_halfyear_data[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum().sum()

        if total_sales_previous_halfyear == 0:
            percentage_change = float('inf') if total_sales_selected_halfyear != 0 else 0
        else:
            percentage_change = ((total_sales_selected_halfyear - total_sales_previous_halfyear) / total_sales_previous_halfyear) * 100

        comparison_text = (
            f"Sales for {selected_halfyear}: ${total_sales_selected_halfyear:.2f}\n"
            f"Sales for {selected_halfyear}: ${total_sales_previous_halfyear:.2f}\n"
            f"Change: {'Increase' if total_sales_selected_halfyear > total_sales_previous_halfyear else 'Decrease'}\n"
            f"Percentage Change: {percentage_change:.2f}%"
        )

        return {"sales_comparison_text": comparison_text}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/halfyearly/monthly-comparison/")
async def halfyearly_monthly_comparison(selected_halfyear: str = Query(..., regex=r"^\d{4}-H[12]$")):
    try:
        df = fetch_and_prepare_data()
        
        # Define start and end dates for the selected half-year
        if selected_halfyear == "2011-H1":
            start_date = pd.Timestamp('2011-01-01')
            end_date = pd.Timestamp('2011-06-30')
        else:
            start_date = pd.Timestamp('2011-07-01')
            end_date = pd.Timestamp('2011-12-31')

        # Filter data for the selected half-year
        halfyear_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        if halfyear_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the selected half-year.")

        # Aggregate monthly sales
        halfyear_data['Month'] = halfyear_data['Date'].dt.to_period('M')
        monthly_sales = halfyear_data.groupby('Month')[['S-P1', 'S-P2', 'S-P3', 'S-P4']].sum()
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

        # Create monthly sales comparison bar chart
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_sales.index.astype(str), monthly_sales['Total'], marker='o', color='skyblue', linestyle='-', label='Total Sales')
        plt.title(f'Monthly Sales Comparison in {selected_halfyear}')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)
        plt.grid(True)
        # Add the values of each point on the chart
        for i, value in enumerate(monthly_sales['Total']):
            plt.text(i, value, f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        plt.legend()

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Combine chart data and image into a JSON response
        return {
            "chart_data": monthly_sales_json,
            "sales_chart_base64": img_base64
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
