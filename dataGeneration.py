import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Merchant categories with risk scores
merchant_categories = {
    'Food': 0.2,
    'Groceries': 0.1,
    'Transportation': 0.15,
    'Entertainment': 0.3,
    'Shopping': 0.4,
    'Electronics': 0.6,
    'Online Gaming': 0.7,
    'Crypto Exchange': 0.9,
    'Foreign Wallet': 1.0,
    'Wire Transfer': 0.85
}

# Locations (city names with approximate coordinates for distance calculation)
locations = {
    'Pune': (18.5204, 73.8567),
    'Mumbai': (19.0760, 72.8777),
    'Delhi': (28.7041, 77.1025),
    'Bangalore': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639),
    'Singapore': (1.3521, 103.8198),
    'Dubai': (25.2048, 55.2708)
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def generate_customer_transactions(customer_id, num_transactions, start_date, is_fraudster=False):
    """Generate transaction sequence for a customer"""
    transactions = []
    current_date = start_date
    current_location = 'Pune'
    
    # Customer profile
    if is_fraudster:
        avg_amount = random.randint(800, 2000)
        normal_txn_count = int(num_transactions * 0.7)  # 70% normal, 30% fraud
    else:
        avg_amount = random.randint(500, 3000)
        normal_txn_count = num_transactions
    
    # Track transactions for velocity calculation
    txn_times = []
    
    for i in range(num_transactions):
        # Generate timestamp
        if i == 0:
            timestamp = current_date
        else:
            # Random time gap (minutes to hours)
            gap = timedelta(minutes=random.randint(30, 480))
            timestamp = current_date + gap
            current_date = timestamp
        
        txn_times.append(timestamp)
        
        # Calculate velocity (transactions in last hour)
        one_hour_ago = timestamp - timedelta(hours=1)
        recent_txns = [t for t in txn_times if t > one_hour_ago and t < timestamp]
        txn_velocity = len(recent_txns)
        
        # Calculate velocity change
        if len(txn_times) > 10:
            historical_velocity = len([t for t in txn_times[-10:] if t > (txn_times[-10] - timedelta(hours=1))])
            rolling_mean_velocity = historical_velocity / 10
        else:
            rolling_mean_velocity = 0.2
        
        velocity_change = txn_velocity / (rolling_mean_velocity + 1)
        
        # Determine if this transaction should be fraudulent
        is_fraud_txn = is_fraudster and i >= normal_txn_count
        
        if is_fraud_txn:
            # Fraudulent transaction characteristics
            amount = random.choice([
                avg_amount * random.uniform(20, 50),  # Very large amount
                random.randint(20000, 100000)
            ])
            merchant = random.choice(['Crypto Exchange', 'Foreign Wallet', 'Wire Transfer', 'Online Gaming'])
            
            # Location change (sometimes international)
            if random.random() > 0.5:
                new_location = random.choice(['Singapore', 'Dubai', 'Delhi', 'Mumbai'])
            else:
                new_location = current_location
            
            # Unusual hours
            hour = random.choice([0, 1, 2, 3, 4, 23])
        else:
            # Normal transaction
            amount = np.random.normal(avg_amount, avg_amount * 0.3)
            amount = max(50, amount)  # Minimum transaction
            merchant = random.choice(['Food', 'Groceries', 'Transportation', 'Shopping', 'Entertainment'])
            
            # Mostly same location, occasionally nearby cities
            if random.random() > 0.9:
                new_location = random.choice(['Mumbai', 'Pune', 'Bangalore'])
            else:
                new_location = current_location
            
            # Normal hours
            hour = random.randint(8, 22)
        
        # Calculate location change
        if new_location != current_location:
            prev_coords = locations[current_location]
            new_coords = locations[new_location]
            location_change_km = haversine_distance(prev_coords[0], prev_coords[1], 
                                                     new_coords[0], new_coords[1])
            current_location = new_location
        else:
            location_change_km = 0
        
        # Amount deviation
        amount_deviation = amount / avg_amount
        
        # Create transaction record
        transaction = {
            'transaction_id': f'T{customer_id[1:]}_{i+1:03d}',
            'customer_id': customer_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_amount': round(amount, 2),
            'avg_transaction_amount_30d': avg_amount,
            'amount_deviation': round(amount_deviation, 2),
            'txn_velocity': txn_velocity,
            'velocity_change': round(velocity_change, 2),
            'location_change_km': round(location_change_km, 1),
            'merchant_category_risk': merchant_categories[merchant],
            'hour_of_day': hour
        }
        
        transactions.append(transaction)
    
    return transactions

# Generate dataset
all_transactions = []

# Generate data for multiple customers
start_date = datetime(2025, 11, 1, 8, 0, 0)

# Normal customers (80%)
for i in range(1, 1601):
    customer_id = f'C{i:04d}'
    num_txns = random.randint(12, 20)
    customer_start = start_date + timedelta(days=random.randint(0, 30))
    txns = generate_customer_transactions(customer_id, num_txns, customer_start, is_fraudster=False)
    all_transactions.extend(txns)
    
    if i % 200 == 0:
        print(f"Generated {i} normal customers...")

# Fraudulent customers (20%)
for i in range(1601, 2001):
    customer_id = f'C{i:04d}'
    num_txns = random.randint(12, 18)
    customer_start = start_date + timedelta(days=random.randint(0, 30))
    txns = generate_customer_transactions(customer_id, num_txns, customer_start, is_fraudster=True)
    all_transactions.extend(txns)
    
    if i % 50 == 0:
        print(f"Generated {i} customers (including fraudsters)...")

# Convert to DataFrame
df = pd.DataFrame(all_transactions)

# Sort by timestamp to maintain temporal order
df = df.sort_values('timestamp').reset_index(drop=True)

# Reorder columns
df = df[['transaction_id', 'customer_id', 'timestamp', 'transaction_amount', 
         'avg_transaction_amount_30d', 'amount_deviation', 'txn_velocity', 
         'velocity_change', 'location_change_km', 'merchant_category_risk', 'hour_of_day']]

# Save to CSV
df.to_csv('fraud_detection_dataset.csv', index=False)

print(f"Dataset generated successfully!")
print(f"Total transactions: {len(df)}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"\nFirst 10 rows:")
print(df.head(10))
print(f"\nDataset statistics:")
print(df.describe())
print(f"\nSample of suspicious transactions (high amount deviation):")
print(df[df['amount_deviation'] > 10].head())