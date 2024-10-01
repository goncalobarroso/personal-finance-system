import matplotlib as mpl
from datetime import datetime
import json
import os
import shlex
import pandas as pd

#load categories from categories.json
def loadCategories():
    with open('categories.json', 'r') as file:
        return json.load(file)

CATEGORIES = loadCategories()

def loadTransactions(file_name='transactions.json'):
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            if not content.strip(): 
                return []  
            return json.loads(content) 
    except FileNotFoundError:
        print("Error: JSON File not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return [] 

#save the transactions to the transactions.json (atomic writing implemented)
def saveTransactions(transactions, fileName='transactions.json'):
    tempFileName = fileName + '.tmp'
    try:
        with open(tempFileName, 'w') as tempFile:
            json.dump(transactions, tempFile, indent=4)
        os.replace(tempFileName, fileName)
        print(f"Transactions saved successfully to {fileName}.")
    except Exception as e:
        print(f"Error saving transactions: {e}")

#add a new transaction
def addTransaction(date, transactionType, amount, category, description=""):
    transactions = loadTransactions() 
    newTransaction = {
        "date": date.strftime("%d-%m-%Y"),
        "type": transactionType,
        "amount": amount,
        "category": category,
        "description": description
    }
    transactions.append(newTransaction) 
    saveTransactions(transactions)

#view all
def handleViewAll(dataFrame):
    print(dataFrame)
    return 1

#view date <operator> <date>
#   <operator> <, >, =
#   <date> the day, month and year in '%d-%m-%Y' format
def handleDate(dataFrame, parsedString):
    if len(parsedString)!= 4:
        print('Error: Invalid amount of arguments')
        return 0
    try:
        date = pd.to_datetime(parsedString[3], format='%d-%m-%Y')
    except:
        print('Error: Invalid date (date format: \"%d-%m-%Y\")')
        return 0
    if parsedString[2] == '<':
        print(dataFrame[dataFrame['date'] < date])
    elif parsedString[2] == '>':
        print(dataFrame[dataFrame['date'] > date])
    elif parsedString[2] == '=':
        print(dataFrame[dataFrame['date'] == date])
    else:
        print("Error: Invalid operator (valid operators: <, >, =)")
        return 0
    return 1

#view type <type>
#   <type> income, expense
def handleType(dataFrame, parsedString):
    transactionType = parsedString[2].lower()
    if len(parsedString) != 3:
        print('Error: Invalid amount of arguments')
        return 0
    if transactionType == 'income' or transactionType == 'expense':        
        print(dataFrame[dataFrame['type'] == transactionType])
        return 1
    print("Error: Invalid type (valid type: income, expense)")
    return 0

#view category <category>
#   <category> any category
def handleCategory(dataFrame, parsedString):
    expense_categories = CATEGORIES["expense_categories"]
    income_categories = CATEGORIES["income_categories"]
    category = parsedString[2].lower()
    if len(parsedString) != 3:
        print('Error: Invalid amount of arguments')
        return 0
    if category in expense_categories or category in income_categories:        
        print(dataFrame[dataFrame['category'] == category])
        return 1
    print(f"Error: Invalid category (valid categories: {', '.join(expense_categories)}, {', '.join(income_categories)})")
    return 0

#handle the view command
def handleView(parsedString):
    filePath = 'transactions.json'
    if os.stat(filePath).st_size == 0:
        print(f"The file '{filePath}' is empty")
        return 0
    else:
        dataFrame = pd.read_json(filePath)
    
    try:
        action = parsedString[1].lower()
    except:
        print('Error: Invalid input')
        return 0
    
    if action == 'all':
        return handleViewAll(dataFrame)
    elif action == 'date':
        return handleDate(dataFrame, parsedString)
    elif action == 'type':
        return handleType(dataFrame, parsedString)
    elif action == 'category':
        return handleCategory(dataFrame, parsedString)
    else:
        print('Error: Invalid arguments')
        return 0
    return 1

#add <date> <type> <amount> <category> <description>
#   <date> the day, month and year in '%d-%m-%Y' format of the transaction
#   <type> either 'expense' or 'income'
#   <amount> amount of the transaction
#   <category> category of the transaction
#   <description> any message in quotes i.e. "this is a message". Optional argument
def handleAdd(parsedString):
    #Divide CATEGORIES into two arrays for ease of access 
    expense_categories = CATEGORIES["expense_categories"]
    income_categories = CATEGORIES["income_categories"]
    #Check if args length is correct
    if len(parsedString)<5 and len(parsedString)>6:
        print('Error: Invalid amount of arguments')
        return 0
    #Check if date is valid
    try:
        date = datetime.strptime(parsedString[1], "%d-%m-%Y")
    except:
        print('Error: Invalid date (date format: \"%d-%m-%Y\")')
        return 0
    #Check if type is valid
    transactionType = parsedString[2]
    if transactionType != 'income' and transactionType != 'expense':
        print('Error: Invalid type')
        return 0
    #Check if amount is int or float
    amount = parsedString[3]
    try:
        amount = float(amount)
    except ValueError:
        print('Error: Invalid amount')
        return 0
    #Check if category is a string
    category = parsedString[4]
    if transactionType == 'income' and category not in income_categories:
        print(f'Error: Invalid income category (valid categories: {", ".join(income_categories)})')
        return 0
    elif transactionType == 'expense' and category not in expense_categories:
        print(f'Error: Invalid expense category (valid categories: {", ".join(expense_categories)})')
        return 0
    #Get description if exists
    if len(parsedString) == 6:
        description = parsedString[5]
        addTransaction(date, transactionType, amount, category, description)
    else:
        addTransaction(date, transactionType, amount, category)
    return 1

#handle the user input (add, view and quit)
def handleInput():
    print('Input: ')
    inputString = input()
    parsedString = shlex.split(inputString)
    try:
        action = parsedString[0].lower()
    except:
        print('Error: Invalid input')
        return
    if  action =='add':
        handleAdd(parsedString)
    elif action == 'view':
        handleView(parsedString)
    elif action == 'quit' or action == 'q':
        return 1  
    else:
        print('Error: Invalid input')

def main():
    while(1):
        if(handleInput()):
            break
    

if __name__ == "__main__":
    main()