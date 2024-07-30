import subprocess
import os
from termcolor import colored

def main():
    print(colored("Which direction do you want to implement?", 'yellow'))
    print(colored("1. UMM to ISO", 'yellow'))
    print(colored("2. ISO to UMM", 'yellow'))
    
    choice = input("Enter the number corresponding to your choice (1 or 2): ")
    if choice == '1':
        subprocess.run(["python", "generation/add_mapper_UMM2ISO.py"])
    elif choice == '2':
        subprocess.run(["python", "generation/add_mapper_ISO2UMM.py"])
    else:
        print(colored("Invalid choice. Please enter 1 or 2.", 'red'))

if __name__ == "__main__":
    main()