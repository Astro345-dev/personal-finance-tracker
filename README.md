# Personal Finance Tracker

A web-based financial planning tool built with Flask that helps users manage their budget, calculate debt payoff timelines, and project investment growth.

## Features

- **50/30/20 Budget Calculator**: Visualize your income breakdown following the popular budgeting rule
- **Debt Payoff Calculator**: Calculate how long it will take to pay off debt with custom payment amounts
- **Investment Growth Projector**: Model compound interest growth with recurring contributions

## Tech Stack

- **Backend**: Python, Flask
- **Data Visualization**: Matplotlib
- **Frontend**: HTML, CSS, Jinja2 templates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/personal-finance-tracker.git
cd personal-finance-tracker
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Usage

### Budget Calculator
Enter your monthly income to see a 50/30/20 breakdown with a visual pie chart.

### Debt Payoff Calculator
Input your principal balance, APR, and monthly payment to calculate your payoff timeline.

### Investment Projector
Enter your initial investment, expected return rate, monthly contributions, and time horizon to see projected growth.

## Possible Future Improvements

- User authentication and data persistence
- Export reports to PDF
- Mobile-responsive design
- React.js frontend (v2 in progress!)