"""
Quick script to disable old broken endpoints in main.py
"""
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Read the file
with open('api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match old endpoint definitions (from @app.get to the next @app or end)
revenue_pattern = r'@app\.get\(\s*"/api/revenue".*?\n(?=@app\.get|@app\.post|# =====|\Z)'
customers_pattern = r'@app\.get\(\s*"/api/customers".*?\n(?=@app\.get|@app\.post|# =====|\Z)'
products_pattern = r'@app\.get\(\s*"/api/products".*?\n(?=@app\.get|@app\.post|# =====|\Z)'

# Replacement for revenue endpoint
revenue_replacement = '''@app.get(
    "/api/revenue",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get revenue analytics",
    description="This endpoint is deprecated. Use /api/cbs/categories instead.",
    deprecated=True,
)
def get_revenue():
    """DEPRECATED: Use /api/cbs/categories for category-based revenue analysis."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/categories for revenue by category",
            "alternative": "/api/cbs/categories"
        }
    )


'''

# Replacement for customers endpoint
customers_replacement = '''@app.get(
    "/api/customers",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get customer analytics",
    description="This endpoint is deprecated. Use /api/cbs/quintiles instead.",
    deprecated=True,
)
def get_customers():
    """DEPRECATED: Use /api/cbs/quintiles for customer segmentation by income."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/quintiles for customer segmentation",
            "alternative": "/api/cbs/quintiles"
        }
    )


'''

# Replacement for products endpoint
products_replacement = '''@app.get(
    "/api/products",
    tags=["Deprecated"],
    summary="[DEPRECATED] Get product performance",
    description="This endpoint is deprecated. Use /api/cbs/categories instead.",
    deprecated=True,
)
def get_products():
    """DEPRECATED: Use /api/cbs/categories for product category performance."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "This endpoint is deprecated",
            "message": "Please use /api/cbs/categories for product performance",
            "alternative": "/api/cbs/categories"
        }
    )


'''

# Replace using regex
content = re.sub(revenue_pattern, revenue_replacement, content, flags=re.DOTALL)
content = re.sub(customers_pattern, customers_replacement, content, flags=re.DOTALL)
content = re.sub(products_pattern, products_replacement, content, flags=re.DOTALL)

# Write back
with open('api/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all old endpoints - they now return 501 with deprecation notices")
