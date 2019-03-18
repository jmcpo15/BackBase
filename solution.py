import csv
import datetime

# Current date and time formatted correctly as a string
dt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()

def set_csv(file):
    global csv_file, current_id, savings_id
    csv_file = file

    # Creates global variables containing ID of current and savings account
    with open(csv_file, 'r') as get_id:
        reader = csv.reader(get_id)
        row = next(reader)
        current_id = 0
        savings_id = 0
        while current_id == 0 or savings_id == 0:
            row = next(reader)
            if(row[1] == 'CURRENT'):
                current_id = int(row[0])
            elif(row[1] == 'SAVINGS'):
                savings_id = int(row[0])
    # Inserts blank line at bottom of ledger on opening to ensure
    # all transactions will display on a new line
    with open(csv_file, 'a', newline='') as new_line:
        writer = csv.writer(new_line)
        writer.writerow('')
              
    return True


# Returns a tuple of total balance, balance of current account
# and balance of saving account in that order.
def current_balance():
    with open(csv_file, 'r') as ledger:
        reader = csv.DictReader(ledger)
        total = 0
        total_current = 0
        total_savings = 0
        for row in reader:
            total += float(row['TransactionValue'])
            if(row['AccountType'] == 'CURRENT'):
                total_current += float(row['TransactionValue'])
            elif(row['AccountType'] == 'SAVINGS'):
                total_savings += float(row['TransactionValue'])
        return(total, total_current, total_savings)


def withdraw(account, amount):
    account = account.upper()
    
    if(account == 'CURRENT'):
        # Has enough money in current account to not be overdrawn
        if(current_balance()[1] > 0 and current_balance()[1] >= amount): 
            new_row(current_id, account, amount * -1)
            return 'Withdrawn: £{}'.format(amount)
        
        # Has enough money in current account and savings account combined,
        # so money is transfered out of savings into current account before transaction
        elif(current_balance()[0] >= amount): 
            transfer = amount - current_balance()[1]
            withdraw('savings', transfer)
            deposit('current', transfer)
            withdraw(account, amount)
            return 'Withdrawn: £{}. £{} had to be moved from your savings'.format(amount, transfer)
        
        # Is going to go into overdraft so transfer entire savings
        # into current to limit fees paid
        else:
            transfer = current_balance()[2]
            withdraw('savings', transfer)
            deposit('current', transfer)
            new_row(current_id, account, amount * -1)
            return 'Withdrawn: £{}. All of the money in your savings was moved to you current account'.format(amount)
        
    elif(account == 'SAVINGS'):
        # Ensures savings accout does not drop below 0
        if(current_balance()[2] >= amount):
            new_row(savings_id, account, amount * -1)
        else:
            return 'You do not have enough money.'
        
    else:
        raise Exception('That account does not exist')


def deposit(account, amount):
    account = account.upper()
    
    if(account == 'CURRENT'):
        new_row(current_id, account, amount)
        
    elif(account == 'SAVINGS'):
        # Puts enough money into current account to not be overdrawn
        # and the rest into savings account
        if(current_balance()[1] < 0 and amount + current_balance()[1] > 0): 
            left_over = amount + current_balance()[1]
            deposit('current', -current_balance()[1])
            deposit('savings', left_over)
        # Amount being deposit is not enough to get out of overdraft,
        # so the entire amount is being put into current account
        elif(current_balance()[1] < 0):
            deposit('current', amount)
        # Is not overdrawn so all money goes into saving account
        else:
            new_row(savings_id, account, amount)
            
    else:
        raise Exception('That account does not exist')
    

# Create new transaction in ledger formatted correctly
def new_row(ID, account, amount):
    with open(csv_file, 'a', newline='') as ledger:
        writer = csv.writer(ledger)
        amount = float('{:.2f}'.format(amount))
        writer.writerow([ID, account, 'SYSTEM', dt, amount])

              



