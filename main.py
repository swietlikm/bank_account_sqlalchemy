import os
import sys
from getpass import getpass

import bank

clear = lambda: os.system("cls")


def main_menu():
    clear()
    while True:
        print("----------------------------")
        print(" 1 - Login")
        print(" 2 - Create new account")
        print(" 0 - Exit")
        print("----------------------------")
        choice = input(">>> Your choice: ")
        clear()
        if choice == "1":
            username = input(">>> Username: ")
            password = getpass(">>> Password: ")
            account_management(username=username, password=password)
        elif choice == "2":
            bank.create_account()
        elif choice == "0":
            print("Goodbye!")
            sys.exit()
        else:
            print(f'"{choice}" is not valid option')


def account_management(username: str, password: str):
    clear()
    account = bank.Account()
    if account.login(username=username, password=password):
        while True:
            print("----------------------------")
            print("1 - Display your bank account details")
            print("2 - Display all transactions")
            print("3 - Deposit money")
            print("4 - Withdraw money")
            print("5 - Transfer money using username")
            print("6 - Transfer money using account number")
            print("")
            print("9 - Change account details")
            print("0 - Main menu")
            print("----------------------------")
            choice = input(">>> Your choice: ").strip()
            clear()
            if choice == "1":
                account.display_bank_account_details()
            elif choice == "2":
                account.display_all_transactions()
            elif choice == "3":
                amount = float(input(">>> Amount: $"))
                account.deposit(amount=amount)
            elif choice == "4":
                amount = float(input(">>> Amount: $"))
                account.withdraw(amount=amount)
            elif choice == "5":
                username = input(">>> Username: ")
                amount = float(input(">>> Amount: $"))
                description = input(">>> Message: ")
                account.transfer_to_username(username, amount, description)
            elif choice == "6":
                account_number = input(">>> Account number: ")
                amount = float(input(">>> Amount: $"))
                description = input(">>> Message: ")
                account.transfer_to_account_number(account_number, amount, description)
            elif choice == "9":
                account.modify_account()
            elif choice == "0":
                account.logout()
                break
            elif choice != "":
                print(f'"{choice}" is not valid option')


if __name__ == "__main__":
    main_menu()
