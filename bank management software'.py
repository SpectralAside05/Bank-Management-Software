import csv
import os

CUST_FILE = "customers.csv"
EMP_FILE = "employees.csv"
TRANS_FILE = "transactions.csv"

def init_files():
    if not os.path.exists(CUST_FILE):
        with open(CUST_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Acc_No", "Name", "Phone", "Aadhaar", "Acc_Type", "Init_Deposit", "Password", "Reward", "Blocked"])
    if not os.path.exists(EMP_FILE):
        with open(EMP_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Emp_ID", "Name", "Phone", "Aadhaar", "Reg_Code", "Password"])
    if not os.path.exists(TRANS_FILE):
        with open(TRANS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Acc_No", "Trans_Type", "Amount"])

def gen_id(filename):
    with open(filename, 'r') as file:
        rows = list(csv.reader(file))
        if len(rows) == 1:
            return "0001"
        else:
            last_id = int(rows[-1][0])
            return f"{last_id + 1:04d}"

def reg_customer():
    name = input("Name: ")
    phone = input("Phone: ")
    aadhaar = input("Aadhaar: ")
    acc_type = input("Acc Type (S/C): ")
    deposit = float(input("Initial Deposit: "))
    password = input("Password: ")
    acc_no = gen_id(CUST_FILE)
    reward = int(deposit // 500)
    
    with open(CUST_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([acc_no, name, phone, aadhaar, acc_type, deposit, password, reward, "No"])
    
    print(f"Customer Registered! Acc No: {acc_no}")

def reg_employee():
    name = input("Name: ")
    phone = input("Phone: ")
    aadhaar = input("Aadhaar: ")
    reg_code = input("Reg Code: ")
    if reg_code != "6098":
        print("Invalid code!")
        return
    password = input("Password: ")
    emp_id = gen_id(EMP_FILE)
    
    with open(EMP_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([emp_id, name, phone, aadhaar, reg_code, password])
    
    print(f"Employee Registered! Emp ID: {emp_id}")

def cust_login():
    acc_no = input("Acc No: ")
    password = input("Password: ")
    with open(CUST_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == acc_no and row[6] == password:
                if row[8] == "Yes":
                    print("Account blocked!")
                    return
                print("Login successful!")
                cust_menu(acc_no)
                return
    print("Invalid details!")

def cust_menu(acc_no):
    while True:
        print("\n1. Deposit\n2. Withdraw\n3. Transfer\n4. View Trans\n5. Points\n6. FD\n7. Logout")
        choice = input("Choice: ")
        if choice == "1":
            deposit(acc_no)
        elif choice == "2":
            withdraw(acc_no)
        elif choice == "3":
            transfer(acc_no)
        elif choice == "4":
            view_trans(acc_no)
        elif choice == "5":
            points(acc_no)
        elif choice == "6":
            fixed_deposit(acc_no)
        elif choice == "7":
            print("Logged out!")
            break
        else:
            print("Invalid choice!")

def deposit(acc_no):
    amt = float(input("Amount: "))
    update_trans(acc_no, "Deposit", amt)
    update_points(acc_no, amt)
    print(f"₹{amt} deposited!")

def withdraw(acc_no):
    amt = float(input("Amount: "))
    with open(CUST_FILE, 'r') as file:
        rows = list(csv.reader(file))
    for row in rows:
        if row[0] == acc_no:
            balance = float(row[5])
            if amt > balance:
                print(f"Insufficient balance! Balance: ₹{balance}")
                return
            row[5] = str(balance - amt)
    
    with open(CUST_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    
    update_trans(acc_no, "Withdraw", amt)
    print(f"₹{amt} withdrawn! New balance: ₹{balance - amt}")

def transfer(acc_no):
    target_acc = input("Target Acc: ")
    amt = float(input("Amount: "))
    with open(CUST_FILE, 'r') as file:
        rows = list(csv.reader(file))
    
    sender = target = None
    for row in rows:
        if row[0] == acc_no:
            sender = row
        if row[0] == target_acc:
            target = row

    if not sender or not target:
        print("Account not found!")
        return

    sender_balance = float(sender[5])
    if amt > sender_balance:
        print(f"Insufficient balance! Balance: ₹{sender_balance}")
        return
    
    sender[5] = str(sender_balance - amt)
    target[5] = str(float(target[5]) + amt)
    
    with open(CUST_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    
    update_trans(acc_no, "Transfer", amt)
    update_trans(target_acc, "Received", amt)
    update_points(acc_no, amt)
    print(f"₹{amt} transferred!")

def view_trans(acc_no):
    with open(TRANS_FILE, 'r') as file:
        reader = csv.reader(file)
        print(f"Transactions for {acc_no}:")
        for row in reader:
            if row[0] == acc_no:
                print(f"{row[1]}: ₹{row[2]}")

def points(acc_no):
    with open(CUST_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == acc_no:
                print(f"Points: {row[7]}")
                return

def fixed_deposit(acc_no):
    amt = float(input("FD Amount: "))
    with open(CUST_FILE, 'r') as file:
        rows = list(csv.reader(file))
    for row in rows:
        if row[0] == acc_no:
            balance = float(row[5]) 
            if amt > balance:
                print(f"Insufficient balance! Available balance: ₹{balance}")
                return
            break
    else:
        print("Account not found!")
        return

    for row in rows:
        if row[0] == acc_no:
            row[5] = str(balance - amt)  

    with open(CUST_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    interest = amt * 0.07
    print(f"FD created. Interest: ₹{interest}. New balance: ₹{balance - amt}")
def update_trans(acc_no, trans_type, amt):
    with open(TRANS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([acc_no, trans_type, amt])

def update_points(acc_no, amt):
    points = int(amt // 500)
    with open(CUST_FILE, 'r') as file:
        rows = list(csv.reader(file))
    
    with open(CUST_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] == acc_no:
                row[7] = str(int(row[7]) + points)
            writer.writerow(row)

def emp_login():
    emp_id = input("Emp ID: ")
    password = input("Password: ")
    with open(EMP_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == emp_id and row[5] == password:
                print("Login successful!")
                emp_menu()
                return
    print("Invalid details!")

def emp_menu():
    while True:
        print("\n1. Search Cust\n2. Block Cust\n3. Register Cust\n4. Logout")
        choice = input("Choice: ")
        if choice == "1":
            search_cust()
        elif choice == "2":
            block_cust()
        elif choice == "3":
            reg_customer()
        elif choice == "4":
            print("Logged out!")
            break
        else:
            print("Invalid choice!")

def search_cust():
    acc_no = input("Acc No: ")
    with open(CUST_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == acc_no:
                print(f"Customer found: {row}")
                return
    print("Not found!")

def block_cust():
    acc_no = input("Acc No to block: ")
    with open(CUST_FILE, 'r') as file:
        rows = list(csv.reader(file))
    with open(CUST_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] == acc_no:
                row[8] = "Yes"
            writer.writerow(row)
    print(f"Account {acc_no} blocked.")

def main_menu():
    while True:
        print("\n1. Register\n2. Customer Login\n3. Employee Login\n4. Exit")
        choice = input("Choice: ")
        if choice == "1":
            reg_menu()
        elif choice == "2":
            cust_login()
        elif choice == "3":
            emp_login()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

def reg_menu():
    print("\n1. Customer\n2. Employee")
    choice = input("Choice: ")
    if choice == "1":
        reg_customer()
    elif choice == "2":
        reg_employee()
    else:
        print("Invalid choice!")

init_files()
main_menu()
