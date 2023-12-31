from flask import Flask, render_template, request
from ortools.linear_solver import pywraplp
import pickle


app = Flask(__name__)

ISP_PACKAGES = {}  

isp_data_paths = {
    'MCI - همراه‌اول': 'data/mci.pk',
    'MTN - ایرانسل': 'data/mtn.pk'
}

def load_isp_data():
    print('Reading the isps')
    for isp, path in isp_data_paths.items():
        with open(path, 'rb') as f:
            ISP_PACKAGES[isp] = pickle.load(f)
    print(f'The ISPs {len(ISP_PACKAGES)}')
    
def calculator(usage, duration, isp):
    solver = pywraplp.Solver.CreateSolver("SCIP")
    
    packages = ISP_PACKAGES[isp]

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
        print("The optimal solution is:")
        result = {'total_price': solver.Objective().Value(), 'packages': []}
        total_purchase = 0
        total_volume = 0
        for i in range(len(packages)):
            if x[i].solution_value() > 0:
                chosen_package = packages[i].copy()
                chosen_package.update({'count': x[i].solution_value()})
                total_purchase += x[i].solution_value()
                total_volume += (packages[i]['volume'] * x[i].solution_value())
                # print(f"  {x[i].solution_value()} package(s) of type {packages[i]['name']}")
                result['packages'].append(chosen_package)
        result.update({'total_purchase': total_purchase, 'total_volume': total_volume})
        # print(f"The total cost is {solver.Objective().Value()} for {usage} GB")
        # print("Per GB: {}".format(solver.Objective().Value()/usage))
    else:
        result = {'total_price': None, 'packages': []}
        # print("The problem does not have an optimal solution.")
    
    
    return result


@app.route("/")
def index():
    isps = list(ISP_PACKAGES.keys())
    return render_template("index.html", isps=isps)


@app.route("/calculate", methods=["POST"])
def calculate():
    usage = int(request.form["usage"])
    isp = request.form["isp"]
    
    results = calculator(usage=usage, duration=30, isp=isp)
    optimal_combination = results['packages']
    print(optimal_combination)
    total_price = results['total_price']
    total_purchases = results['total_purchase']
    total_volume = float(results['total_volume'] / 1024)
    return render_template("_results_table.html", optimal_combination=optimal_combination, total_price=total_price, total_purchases=total_purchases, total_volume=total_volume)


load_isp_data()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)