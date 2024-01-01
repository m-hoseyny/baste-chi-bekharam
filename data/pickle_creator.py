import pandas as pd
import pickle
import os, tqdm
from ortools.linear_solver import pywraplp

TIME_INTERVAL = 28
TOTAL_USAGE_LIMIT = 1000

def get_all_ips_csv_files():
    directory = os.path.join('.')
    files_path = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                files_path.append(file)
                
    return files_path
                

def save_pickle(path, obj):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def get_calculated_df_isp(file_path):
    packages_df = pd.read_csv(file_path)
    packages_df['price_per_gig'] = packages_df['price'] / (packages_df['volume'] / 1024)
    packages_df['price'] = packages_df['price'] * 1.09

    packages_df = packages_df[packages_df['is_nightly'] == False]
    packages = packages_df.to_dict('records')

    return packages

def read_packages(files):
    isp_packages = {}
    for file in files:
        isp_name = file.replace('.csv', '')
        isp_packages[isp_name] = get_calculated_df_isp(file)
    return isp_packages

def best_package_combination_finder(usage, duration, packages):
    solver = pywraplp.Solver.CreateSolver("SCIP")
    

    # Define the decision variables
    x = [solver.IntVar(0, solver.infinity(), i['name']) for i in packages]

    # Define the objective function
    solver.Minimize(solver.Sum([x[i] * packages[i]["price"] for i in range(len(packages))]))

    # Define the constraints
    solver.Add(solver.Sum([x[i] * packages[i]["volume"] for i in range(len(packages))]) >= usage*1024)
    solver.Add(solver.Sum([x[i] * packages[i]["duration"] for i in range(len(packages))]) >= duration)

    # Solve the problem
    status = solver.Solve()

    # Print the results
    if status == pywraplp.Solver.OPTIMAL:
        result = {'total_price': solver.Objective().Value(), 'packages': []}
        total_purchase = 0
        total_volume = 0
        for i in range(len(packages)):
            if x[i].solution_value() > 0:
                chosen_package = packages[i].copy()
                chosen_package.update({'count': x[i].solution_value()})
                total_purchase += x[i].solution_value()
                total_volume += (packages[i]['volume'] * x[i].solution_value())
                result['packages'].append(chosen_package)
        result.update({'total_purchase': total_purchase, 'total_volume': total_volume})
    else:
        result = {'total_price': None, 'packages': []}
    return result

def best_packages_combination(isp_packages):
    best_combinations = {}
    for isp, packages in isp_packages.items():
        print(f'Best combination for {isp}')
        if isp not in best_combinations:
                best_combinations[isp] = {}
        for usage in tqdm.tqdm(range(TOTAL_USAGE_LIMIT), desc=isp):
            result = best_package_combination_finder(usage, TIME_INTERVAL, packages)
            best_combinations[isp][usage] = result
    return best_combinations

if __name__ == '__main__':
    print('Reading csv files')
    files = get_all_ips_csv_files()
    print(f'There are {len(files)} files in the directory')
    print('Reading packages and calculate the price with tax and ...')
    isp_packages = read_packages(files)
    print('Finding the best package combination for different use usages')
    best_combinations = best_packages_combination(isp_packages)
    print('saving data.pk file for using in the web service')
    save_pickle('data.pk', best_combinations)
    
    