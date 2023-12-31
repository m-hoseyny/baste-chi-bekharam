import pandas as pd
import pickle

isps = {
    'mtn': 'irancell.csv',
    'mci': 'mci.csv'
}

for isp, path in isps.items():
    packages_df = pd.read_csv(path)
    packages_df['price_per_gig'] = packages_df['price'] / (packages_df['volume'] / 1024)
    packages_df['price'] = packages_df['price'] * 1.09

    packages_df = packages_df[packages_df['is_nightly'] == False]
    packages = packages_df.to_dict('records')


    with open(f'{isp}.pk', 'wb') as f:
        pickle.dump(packages, f)