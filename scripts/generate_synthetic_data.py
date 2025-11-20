import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('he_IL')

def generate_synthetic_data(num_records=10000):
    print(f'Generating {num_records} synthetic transactions...')

    data = {
        'transaction_id': range(1, num_records + 1),
        'customer_name': [fake.name() for _ in range(num_records)],
        'product': [random.choice(['מחשב נייד', 'טלפון סלולרי', 'אוזניות', 'מקלדת', 'עכבר']) for _ in range(num_records)],
        'amount': [round(random.uniform(50, 5000), 2) for _ in range(num_records)],
        'currency': ['ILS'] * num_records,
        'date': [(datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d') for _ in range(num_records)],
        'status': [random.choice(['completed', 'pending', 'cancelled']) for _ in range(num_records)]
    }

    df = pd.DataFrame(data)
    df.to_csv('data/raw/transactions.csv', index=False, encoding='utf-8-sig')
    print(f'Created data/raw/transactions.csv with {num_records} records')
    return df

if __name__ == '__main__':
    generate_synthetic_data()
