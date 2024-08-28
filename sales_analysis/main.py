from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monthly import (
    total_sales,
    sales_by_products,
    quantity_pie_chart,
    weekly_sales,
    sales_comparison
)
from quarterly import (
    total_quarterly_sales,
    sales_quarterly_by_products,
    quantity_quarterly_pie_chart,
    quarterly_sales_comparison,
    quarterly_monthly_comparison
)
from halfyearly import (
    halfyearly_total_sales,
    halfyearly_sales_by_products,
    halfyearly_quantity_pie_chart,
    halfyearly_sales_comparison,
    halfyearly_monthly_comparison
)
from annual import (
    annual_total_sales,
    annual_sales_by_products,
    annual_quantity_pie_chart,
    annual_sales_comparison,
    annual_monthly_comparison
)

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

# Include monthly sales routes
app.add_api_route("/sales/total/", total_sales)
app.add_api_route("/sales/by-products/", sales_by_products)
app.add_api_route("/sales/quantity-pie/", quantity_pie_chart)
app.add_api_route("/sales/weekly/", weekly_sales)
app.add_api_route("/sales/comparison/", sales_comparison)

# Include quarterly sales routes
app.add_api_route("/sales/quarterly/total/", total_quarterly_sales)
app.add_api_route("/sales/quarterly/by-products/", sales_quarterly_by_products)
app.add_api_route("/sales/quarterly/quantity-pie/", quantity_quarterly_pie_chart)
app.add_api_route("/sales/quarterly/comparison/", quarterly_sales_comparison)
app.add_api_route("/sales/quarterly/monthly-comparison/", quarterly_monthly_comparison)

# Include half-yearly sales routes
app.add_api_route("/sales/halfyearly/total/", halfyearly_total_sales)
app.add_api_route("/sales/halfyearly/by-products/", halfyearly_sales_by_products)
app.add_api_route("/sales/halfyearly/quantity-pie/", halfyearly_quantity_pie_chart)
app.add_api_route("/sales/halfyearly/comparison/", halfyearly_sales_comparison)
app.add_api_route("/sales/halfyearly/monthly-comparison/", halfyearly_monthly_comparison)

# Include annual sales routes
app.add_api_route("/sales/annual/total/", annual_total_sales)
app.add_api_route("/sales/annual/by-products/", annual_sales_by_products)
app.add_api_route("/sales/annual/quantity-pie/", annual_quantity_pie_chart)
app.add_api_route("/sales/annual/comparison/", annual_sales_comparison)
app.add_api_route("/sales/annual/monthly-comparison/", annual_monthly_comparison)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
