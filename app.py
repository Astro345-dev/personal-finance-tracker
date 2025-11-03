from flask import Flask, request, render_template, request, redirect, url_for,flash
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route("/")
def index():
    return render_template("index.html")

def budget(income):
    needs = income * 0.5
    wants = income * 0.3
    savings = income * 0.2

    return {"Needs": needs, "Wants": wants, "Savings": savings}

def chart(budget_dict):
    labels = list(budget_dict.keys())
    sizes = list(budget_dict.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99']

    plt.figure(figsize=(8,6))

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'${val:,}\n({pct:.1f}%)'
        return my_autopct
    plt.pie(sizes, labels=labels, autopct=make_autopct(sizes), startangle=140, colors=colors)
    plt.title("50/30/20 Budget Breakdown", fontsize=16, fontweight='bold')
    plt.axis('equal')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches ='tight', dpi=150)
    buf.seek(0)
    plt.close()

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def debt_payoff(principal, apr_percent, monthly_payment, max_months=1000*12):
    """
    principal: starting balance (float)
    apr_percent: APR as percentage (e.g. 10 for 10%)
    monthly_payment: amount user pays each month (float)
    returns: dict with months, years, rem_months, total_interest, balances
    """
    if principal <= 0:
        return {"error": "Principal must be > 0."}
    if apr_percent < 0:
        return {"error": "APR must be >= 0."}
    if monthly_payment <= 0:
        return {"error": "Monthly payment must be > 0."}

    apr = apr_percent / 100.0
    monthly_rate = apr / 12.0

    balance = float(principal)
    balances = [balance]            # include starting balance for plotting
    total_interest = 0.0
    months = 0

    # If payment is not greater than the first month's interest -> never paid off
    if monthly_payment <= balance * monthly_rate:
        min_payment = balance * monthly_rate
        return {
            "error": "Payment too small to ever pay off the debt.",
            "min_payment": round(min_payment, 2)
        }

    while balance > 1e-8 and months < max_months:
        interest = balance * monthly_rate
        total_interest += interest

        payment = monthly_payment
        if payment > balance + interest:
            payment = balance + interest

        balance = balance + interest - payment
        balance = max(balance, 0.0)   # avoid tiny negatives from floating point
        balances.append(balance)
        months += 1

    if months >= max_months:
        return {"error": "Exceeded maximum simulation length. Check inputs."}

    years = months // 12
    rem_months = months % 12

    return {
        "months": months,
        "years": years,
        "rem_months": rem_months,
        "total_interest": total_interest,
        "balances": balances,
        "principal": principal,
        "monthly_payment": monthly_payment
    }


def plot_debt_balance(balances, title="Debt Balance Over Time"):
    months = list(range(len(balances)))
    plt.figure(figsize=(8,4))
    plt.plot(months, balances, marker='o', linewidth=2, markersize=4, color='#e74c3c')
    plt.fill_between(months, balances, alpha=0.3, color='#e74c3c')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Balance ($)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

def investment(principal, apr_percent, recurr, time_years):
    apr = apr_percent / 100.0
    monthly_rate = apr / 12
    total_months = time_years * 12

    balance = principal
    balances = [balance]
    contributions = [principal]

    for month in range(1, total_months + 1):
        balance *= 1 + monthly_rate   # apply monthly growth
        balance += recurr             # add recurring contribution

        balances.append(balance)
        contributions.append(principal + recurr * month)

    return {
        "balances": balances,
        "contributions": contributions,
        "final_balance": balances[-1],
        "total_contributions": contributions[-1],
        "growth": balances[-1] - contributions[-1],
        "principal": principal,
        "monthly_contribution": recurr,
        "apr": apr_percent,
        "years": time_years
    }

def investment_chart(balances, contributions, title="Your Investments"): 
    months = list(range(len(balances)))
    years = [m / 12 for m in months]
    growth = [b - c for b, c in zip(balances, contributions)]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,8))

    ax1.plot(years, balances, linewidth=3, color='#2ecc71', label='Total Balance')
    ax1.plot(years, contributions, linewidth=2, color='#3498db', label='Total Contributions')
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Balance ($)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    ax2.stackplot(years, contributions, growth,
                  labels=["Contributions", "Investment Gains"],
                  alpha=0.8, colors=['#3498db', '#2ecc71'])
    ax2.set_title("Contributions vs Investment Gains", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Years")
    ax2.set_ylabel("Amount ($)")
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    plt.tight_layout
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

@app.route("/budget", methods=["GET", "POST"])
def budget_route():
    if request.method == "POST":
        try:
            income = request.form.get("income", type=float)
            if income and income > 0:
                budget_data = budget(income)   # no naming conflict
                chart_img = chart(budget_data)
                return render_template("chart.html", 
                                chart=chart_img, 
                                income=income, 
                                budget=budget_data)
            else:
                flash("Please enter a valid positive income!")
                return redirect(url_for('budget_route'))
        except (ValueError, TypeError):
            flash("Please enter a valid number!")
            return redirect(url_for('budget_route'))
    
    return render_template("budget_form.html")

@app.route('/debt', methods=['GET', 'POST'])
def debt_route():
    if request.method == 'POST':
        try:
            principal = request.form.get('principal', type=float)
            apr = request.form.get('apr', type=float)
            payment = request.form.get('payment', type=float)

            if principal is None or apr is None or payment is None:
                flash("Please fill in all fields with valid numbers")
                return redirect(url_for('debt'))
        
            result = debt_payoff(principal, apr, payment)

            if 'error' in result:
                error_msg = result['error']
                if 'min_payment' in result:
                    error_msg += f" Minimum payment needed: ${result['min_payment']:,.2f}"
                return render_template('debt.html', error=error_msg)
        
            img_uri = plot_debt_balance(result['balances'], title="Debt Payoff Timeline")

            months = result['months']
            years, rem = result['years'], result['rem_months']
            total_interest = result['total_interest']

            message = (
                f"At ${payment:,.2f}/month you will be debt-free in "
                f"{years} years and {rem} months ({months} months). "
                f"Total interest paid: ${total_interest:,.2f}."
            )

            return render_template(
                'debt_report.html',
                principal=principal,
                apr=apr,
                payment=payment,
                message=message,
                chart=img_uri,
                result=result
            )
        except (ValueError, TypeError):
            flash("Please enter valid numeric values!")
            return redirect(url_for('debt_route'))
        
    return render_template('debt.html')


@app.route('/investment', methods=['GET', 'POST'])
def investment_route():
    if request.method == "POST":
        try:
            principal = float(request.form.get("principal", 0))
            apr = float(request.form.get("apr", 0))
            recurr = float(request.form.get("recurr", 0))
            time = int(request.form.get("time", 0))

            if principal == 0 and recurr == 0:
                flash("Please enter either an initial investment or monthly contribution (or both)!")
                return redirect(url_for('investment_route'))

            if principal < 0 or apr < 0 or recurr < 0 or time <= 0:
                flash("Please enter valid positive values!")
                return redirect(url_for('investment_route'))

            result = investment(principal, apr, recurr, time)
            chart_img = investment_chart(result["balances"], result["contributions"])

            return render_template(
                "investment_results.html",
                result=result,
                chart=chart_img
             )
        except (ValueError, TypeError):
            flash("Please enter valid numeric values!")
            return redirect(url_for('investment_route'))

    return render_template("investment.html")

if __name__ == "__main__":
    app.run(debug=True)
