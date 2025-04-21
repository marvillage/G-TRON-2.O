import pandas as pd
import random
import numpy as np

# Sample states and device types
states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'West Bengal',
          'Kerala', 'Gujarat', 'Uttar Pradesh', 'Punjab', 'Rajasthan']
device_types = ['Smartphone', 'Laptop', 'Television', 'Refrigerator', 'Air Conditioner', 'Printer', 'Monitor']

years = list(range(2018, 2024))

data = []

for _ in range(500):
    state = random.choice(states)
    year = random.choice(years)
    device = random.choice(device_types)

    # Base values by device type
    base_qty = {
        'Smartphone': 100000,
        'Laptop': 200000,
        'Television': 250000,
        'Refrigerator': 300000,
        'Air Conditioner': 280000,
        'Printer': 150000,
        'Monitor': 180000,
    }

    qty = int(np.random.normal(loc=base_qty[device] + year * 100, scale=20000))
    lead = round(np.random.uniform(500, 3500), 2)
    plastic = round(np.random.uniform(4000, 15000), 2)
    recovery_value = int(np.random.normal(loc=qty * 2.5, scale=50000))
    informal_rate = round(np.random.uniform(0.2, 0.65), 2)

    data.append({
        'state': state,
        'year': year,
        'device_type': device,
        'e_waste_quantity': max(qty, 10000),
        'lead_content_kg': lead,
        'plastic_content_kg': plastic,
        'economic_recovery_potential': max(recovery_value, 50000),
        'informal_collection_rate': informal_rate
    })

df = pd.DataFrame(data)
df.to_csv('e_waste_data.csv', index=False)

print("✅ e_waste_data.csv generated with", len(df), "rows.")
