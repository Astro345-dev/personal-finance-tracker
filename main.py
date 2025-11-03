from datetime import datetime
import matplotlib.pyplot as plt
file = open("reports.txt", "a")
file.write("Your report goes here")
def tracker(user_name, job, hour_income):
    if 1 <= hour_income <= 10:
        response = "How are you surviving!"
    elif 11 <= hour_income <= 20:
        response = "Ehhh, manageable"
    elif 21 <= hour_income <= 30:
        response = "Ooooh, you're making bank!"
    else:
        response = "Wow, that's impressive!"
    
    return f"{user_name}, as a {job}, {response}"

def hour_to_annual(hour_income):
    return hour_income * 2080

def advice(hour_income):
    annual_income = hour_to_annual(hour_income)
    bills_money = 0.50 * annual_income
    wants_money = 0.30 * annual_income
    savings = 0.20 * annual_income
    return bills_money, wants_money, savings
def get_user_input():
    name = input("What's your name?: ")
    job = input("What do you work as?: ")
    hour_income = float(input("How much do you make per hour?: "))
    return name, job, hour_income
def plot_budget(bills, wants, savings, name="User"):
    labels = ['Bills/Needs', 'Wants', 'Savings']
    values = [bills, wants, savings]
    colors = ['#ff9999','#66b3ff','#99ff99']

    def value_and_percent(val):
        total = sum(values)
        absolute = int(round(val/100 * total, 0)) 
        return f"${absolute:,}\n({val:.1f}%)"    

    plt.figure(figsize=(6,6))
    plt.pie(values, labels=labels, autopct=value_and_percent,
            startangle=140, colors=colors, textprops={'fontsize': 12})
    plt.title(f"{name}'s 50/30/20 Budget Breakdown")
    plt.show()
def generate_report(name, job, hour_income):
    tracker_msg = tracker(name, job, hour_income)
    annual_income = hour_to_annual(hour_income)
    bills_money, wants_money, savings = 0.50 * annual_income, 0.30 * annual_income, 0.20 * annual_income
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = (
    f"\n--- Income & Budget Report ({timestamp}) ---\n"
    f"Name: {name}\n"
    f"Job: {job}\n"
    f"Hourly Income: ${hour_income:.2f}\n"
    f"Annual Income: ${annual_income:.2f}\n"
    f"Tracker Message: {tracker_msg}\n"
    "50/30/20 Plan:\n"
    f"- Bills/Needs: ${bills_money:,.2f}\n"
    f"- Wants: ${wants_money:,.2f}\n"
    f"- Savings: ${savings:,.2f}\n"
    f"-----------------------------\n"
    )
    return report
def main():
    while True:
        name, job, hour_income = get_user_input()
        bills, wants, savings = advice(hour_income)
        report = generate_report(name, job, hour_income) 
        print(report)
        plot_budget(bills, wants, savings, name=name)
        with open("reports.txt", "a") as file:
            file.write(report)
        another = input("Do you want to enter another person? (y/n): ").lower()
        if another != 'y':
            print("Goodbye!")
            break
main()
