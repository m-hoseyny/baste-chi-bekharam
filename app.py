from flask import Flask, render_template, request
import pickle


app = Flask(__name__)

ISP_PACKAGES = {}  

isp_name_mapper = {
    'mci': 'MCI - همراه‌اول',
    'mtn': 'MTN - ایرانسل'
}


def get_isp_name(isp):
    if isp in isp_name_mapper:
        return isp_name_mapper[isp]
    return isp

def get_isp_reverse_name(isp_name):
    for isp, name in isp_name_mapper.items():
        if isp_name == name:
            return isp

def load_isp_data():
    global ISP_PACKAGES
    with open('data/data.pk', 'rb') as f:
        ISP_PACKAGES = pickle.load(f)
    
def give_best_package_combination(usage, duration, isp):
    result = ISP_PACKAGES[isp][usage]
    return result


@app.route("/")
def index():
    isps = list(map(get_isp_name, isp_name_mapper.keys()))
    return render_template("index.html", isps=isps)


@app.route("/calculate", methods=["POST"])
def calculate():
    usage = int(request.form["usage"])
    isp = get_isp_reverse_name(request.form["isp"])
    if usage >= 1000:
        return render_template("not_supported.html")
    
    results = give_best_package_combination(usage=usage, duration=28, isp=isp)
    optimal_combination = results['packages']
    total_price = results['total_price']
    total_purchases = results['total_purchase']
    total_volume = float(results['total_volume'] / 1024)
    return render_template("_results_table.html", optimal_combination=optimal_combination, total_price=total_price, total_purchases=total_purchases, total_volume=total_volume)


load_isp_data()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)