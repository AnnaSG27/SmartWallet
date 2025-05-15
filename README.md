# SmartWallet : Small Savings, Big Goals
## Team Members
 - Laura Sofía Jiménez París
 - Maria Fernanda Álvarez Marín
 - Anna Sofía Giraldo Carvajal
## Versions
 - **Operating Systems:** macOS 14.3.1 and Windows 11 Pro 24H2
 - **Languages Used:** Python 3.13.1 , JavaScript , CSS , HTML
 - **Tool Used:** Visual Studio Code 1.91.1
 
## Instructions for project execution

### Initial configuration
1. Create a folder
2. In this folder clone the repository using GitBash
	```bash
   git clone https://github.com/AnnaSG27/SmartWallet.git
   ```
### Execution process

1. **Navigate to the Project Directory**:
   - Switches to the project directory (folder navigation)
	   ```bash
	 # Windows/Mac 
	   cd SmartWallet
	   ```   

2.  **Create Virtual Environment:**
	- Create a Python virtual environment to isolate dependencie
	     ```bash
		 # Windows
		python -m venv Environment_Name
		# Mac/Linux
		python3 -m venv Environment_Name  
	     ```
3. **Activates the Virtual Environment:** 
	- Activates the newly created virtual environment. 
	   ```bash
		# Windows
		Environment_Name\Scripts\activate
		# Mac/Linux
		source Environment_Name/bin/activate  
	     ```
4. **Install Dependencies**:
	- Installs all required packages listed in requirements.txt
	     ```bash
	     pip install -r requirements.txt
	     ```
5. **Start the development server**:
	- We start the local Django server for development.
	     ```bash
	     py manage.py runserver
	     ```

## Description

SmartWallet is a financial education and savings management application designed to help users track their income, expenses, and savings goals efficiently. With an intuitive interface and smart features, users can develop better financial habits and achieve their financial goals.


## Features

#### **Registration and Security**
The system allows users to register by validating a username (which accepts letters, numbers and characters such as underscores or periods) along with personal data such as full names, email and document type. The login is secure and offers the option to recover passwords, which must meet requirements such as a minimum of 8 characters and not be exclusively numeric.

#### **Basic Financial Management**
* **Savings Pockets:** Users can create personalized spaces to organize their financial goals (e.g. "Savings 2025" with a goal of $1,000,000), visualizing progress in percentages and amounts.
* **Bank Comparator:** Detailed table comparing interest rates (EA), costs and requirements of Colombian banks such as Bancolombia (3.2% EA), BBVA (2.9% EA) or Nequi (5.0% EA), including user ratings.

#### **Advanced Tools**
* **Financial Education:** Explains concepts such as the 50/30/20 rule for budgeting, automatic savings methods and investment options for beginners (index funds, real estate).
- **Virtual Assistant:** Chatbot that answers questions about budgets, debts or investments, with practical examples such as "How to reduce entertainment expenses?
- **Infographics Generator:** Creates visual representations of topics such as savings plans or compound interest, downloadable in PNG or PDF format.

#### Customization and Analysis
Users receive recommendations based on their goals (e.g., "Save $500,000 per month") and can generate categorized spending reports, with alerts when they exceed established limits. The interface is intuitive, with options such as dark mode and integrated tutorials.

#### Easy-to-use interface
Simple and intuitive design for smooth navigation.

## Usage

Once the application is running, you can:

1. **User Registration**
 - **Function:** Allows the user to create an account in the application.
 - **Description:** The user must enter data such as username (with character restrictions), first name, last name, email and document type to register.

2. **Login**
 - **Function:** Allows the user to log in to their existing account.
 - **Description:** The user enters their username and password to authenticate. It also includes a link to redirect to registration.

3. **Personal Information**
 - **Function:** Displays and allows editing of the user's profile data.
 - **Description:** Includes fields such as user name, last name, cell phone number and email, with an option to save changes.

4. **Change Password**
 - **Function:** Allows the user to update his/her password.
 - **Description:** The user must enter his current password, then the new one (with security requirements) and confirm it.

5. **Pocket Management**
 - **Function:** Organizes and manages funds or savings goals.
 - **Description:** Allows to create new pockets with name, type and optional goal, and view existing ones with details such as progress and creation date.

6. **Bank Comparison**
 - **Function:** Compares savings options in Colombian banks.
 - **Description:** Displays a table with interest rates, requirements, costs and ratings of different banks to help the user make informed decisions.

7. **Financial Education**
 - **Function:** Educates the user on key financial concepts.
 - **Description:** Includes sections on budgeting, strategic savings and investments, with practical tips and relevant data.

8. **Financial Calculator**
 - **Function:** Helps the user calculate budgets and emergency funds.
 - **Description:** Offers tools such as the 50/30/20 rule and calculations for earmarking income for specific goals.

9. **Financial Assistant**
 - **Function:** Provides personalized financial advice.
 - **Description:** An interactive chatbot that answers questions about budgeting, investing, debt and planning.

10. **Infographic Generator**
 - **Function:** Creates visualizations of financial concepts.
 -  **Description:** Allows the user to generate infographics on topics such as savings, inflation or investments for better understanding.

11. **Financial Recommendations**
 - **Function:** Provides personalized advice based on the user's objectives.
 - **Description:** The user describes his or her goal (e.g. save $500 per month) and receives recommendations tailored to his or her situation.
