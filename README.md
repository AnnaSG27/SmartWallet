# SmartWallet

## Description

SmartWallet is a financial education and savings management application designed to help users track their income, expenses, and savings goals efficiently. With an intuitive interface and smart features, users can develop better financial habits and achieve their financial goals.

## Features

- **Expense Tracking**: Log and categorize daily expenses to monitor spending habits.
- **Savings Goals**: Set and track progress towards specific savings goals.
- **Financial Reports**: Generate visual reports to analyze financial trends.
- **Budget Planning**: Create and manage monthly budgets to optimize expenses.
- **User-Friendly Interface**: Simple and intuitive design for seamless navigation.

## Installation

Follow these steps to install and run SmartWallet on your local environment:

1. **Clone the repository**:
   
   ```bash
   git clone https://github.com/AnnaSG27/SmartWallet.git
   ```

2. **Navigate to the project directory**:
   
   ```bash
   cd SmartWallet
   ```

3. **Create a virtual environment** (recommended):
   
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies**:
   
   ```bash
   pip install -r requirements.txt
   ```

6. **Apply database migrations**:
   
   ```bash
   python manage.py migrate
   ```

7. **Start the Django backend**:
   
   ```bash
   python manage.py runserver
   ```

## Usage

Once the application is running, you can:

- **Log Expenses**: Record daily expenses and categorize them accordingly.
- **Set Savings Goals**: Define financial objectives and track your progress.
- **Analyze Financial Reports**: Generate visual insights to optimize spending.
- **Manage Budgets**: Set monthly budget limits and receive notifications.


## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
