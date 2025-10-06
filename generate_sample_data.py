import pandas as pd
from datetime import datetime, timedelta
import random

# --- Configuration ---
NUM_MONTHS = 1
WEEKS_IN_MONTH = 4
TOTAL_WEEKS = NUM_MONTHS * WEEKS_IN_MONTH
START_DATE = datetime(2025, 3, 1)

# --- Data for XLSM (Supplier Orders) ---
SUPPLIERS = ["Beverage World", "Snack Masters", "Party Supplies Co.", "Fresh Foods Inc."]
PRODUCTS = {
    "Bevande": ["Coca-Cola", "Acqua Minerale", "Succo d'Arancia", "Birra Artigianale", "Vino Rosso", "Caffè in grani"],
    "Cibo": ["Cornetti", "Panini", "Insalate Pronte", "Patatine", "Biscotti"],
    "Forniture": ["Bicchieri di plastica", "Tovaglioli", "Posate di plastica", "Detersivo", "Sacchi per rifiuti"]
}

def generate_supplier_orders_data():
    """Generates supplier order data as a pandas DataFrame."""
    orders_data = []
    order_id_counter = 1
    
    for week in range(TOTAL_WEEKS):
        current_date = START_DATE + timedelta(weeks=week)
        
        # Simulate 1 to 3 orders per week
        for _ in range(random.randint(1, 3)):
            supplier = random.choice(SUPPLIERS)
            order_date = current_date + timedelta(days=random.randint(0, 4))
            
            # Add 2 to 8 items per order
            for _ in range(random.randint(2, 8)):
                category = random.choice(list(PRODUCTS.keys()))
                product_name = random.choice(PRODUCTS[category])
                
                orders_data.append({
                    "id_ordine": order_id_counter,
                    "data_ordine": order_date.strftime("%Y-%m-%d"),
                    "fornitore": supplier,
                    "prodotto": product_name,
                    "categoria": category,
                    "quantita": random.randint(1, 10) * 10,
                    "costo_unita": f"{random.uniform(0.5, 15.0):.2f}"
                })
            order_id_counter += 1
            
    return pd.DataFrame(orders_data)

# --- Data for XLSX (POS Transactions) ---
POS_PRODUCTS = {
    "Caffè": 1.20, "Cappuccino": 1.80, "Cornetto": 1.50, "Panino": 5.50,
    "Insalata": 7.00, "Coca-Cola": 2.50, "Acqua": 1.00, "Birra": 4.00,
    "Aperitivo": 8.00, "Tramezzino": 3.50
}

def generate_xlsx_data():
    transactions = []
    
    for day in range(TOTAL_WEEKS * 7):
        current_date = START_DATE + timedelta(days=day)
        
        # More transactions on weekends
        num_transactions = random.randint(50, 150) if current_date.weekday() < 5 else random.randint(150, 300)
        
        for _ in range(num_transactions):
            product = random.choice(list(POS_PRODUCTS.keys()))
            price = POS_PRODUCTS[product]
            quantity = random.randint(1, 3)
            
            # Add some small variation to the price
            final_price = price + random.uniform(-0.1, 0.1)
            
            transaction_time = (datetime.min + timedelta(hours=random.randint(7, 22), 
                                                        minutes=random.randint(0, 59))).time()

            transactions.append({
                "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "time": transaction_time.strftime("%H:%M:%S"),
                "datetime": datetime.combine(current_date, transaction_time).strftime("%Y-%m-%d %H:%M:%S"),
                "product_name": product,
                "quantity": quantity,
                "unit_price": f"{final_price:.2f}",
                "total_amount": f"{final_price * quantity:.2f}"
            })
            
    return pd.DataFrame(transactions)

# --- Main Execution ---
if __name__ == "__main__":
    # Generate and save XLSM for supplier orders
    df_orders = generate_supplier_orders_data()
    df_orders.to_excel(f"sample_data/{START_DATE.strftime('%Y_%m_%d')}_ordini_fornitori.xlsm", index=False, engine='openpyxl')
    print("File 'ordini_fornitori.xlsm' creato con successo.")

    # Generate and save XLSX
    df_pos = generate_xlsx_data()
    df_pos.to_excel(f"sample_data/{START_DATE.strftime('%Y_%m_%d')}_transazioni_pos.xlsx", index=False, engine='openpyxl')
    print("File 'transazioni_pos.xlsx' creato con successo.")
