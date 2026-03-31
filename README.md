# AI-Powered Expense Tracker CLI

## 📌 Overview
This project is a Command Line Interface (CLI) application that helps users track and analyze their expenses. It uses basic AI techniques to automatically categorize expenses and provide spending insights.

---

## 🎯 Features
- Add expenses with automatic AI-based category prediction
- View and filter expenses
- Monthly and overall summaries
- Budget tracking system
- Export data (CSV/JSON)
- AI-based spending insights

---

## 🛠️ Requirements

Make sure you have the following installed:

- Python 3.x

To check:
(in command prompt)
python --version

⚙️ Setup Instructions
Step 1: Download the project

Clone the repository or download ZIP:
https://github.com/swastik25bac10033-tech/ai-expense-tracker-cli/blob/main/A.I.%20Powered%20Expense%20Tracker/exp2.py

Step 2: No additional dependencies required

This project uses only built-in Python libraries:

argparse
json
datetime
csv
os

So no need to install anything extra.

▶️ How to Run
Basic Command Format:
python exp2.py <command> [options]

1. Add Expense
  python exp2.py add --amount 200 --description "pizza"
  python exp2.py add --amount 100 --category Food --description "Lunch"

2. List Expenses 
  python exp2.py list
  python exp2.py list --category Food
  python exp2.py list --from 2026-03-01 --to 2026-03-31

3. Summary
  python exp2.py summary
  monthly:-
    python exp2.py summary --month 2026-03

4. Total
  python exp2.py total

5. Budget
   Set Budget:-
      python exp2.py budget --set Food --limit 500
   Show Budget:-
      python exp2.py budget --show

6. Delete Expense
  python exp2.py delete --id 1

7. Export data
  python exp2.py export --format csv

🤖 AI Features
1. Category Prediction

The system automatically predicts categories using keyword-based classification.

Example:
python exp2.py add --amount 200 --description "pizza"
🤖 Predicted Category: Food

2. Spending Insight

The system identifies the category with the highest spending and provides suggestions.

📁 Data Storage

Data is stored locally using JSON files:

expenses.json
budgets.json

These files are automatically created when the program runs.

🔮 Future Enhancements
Integration with bank APIs for automatic expense tracking
Advanced machine learning model for prediction
GUI or web-based interface


👨‍💻 Author
Swastik Gupta
