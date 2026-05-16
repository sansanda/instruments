from termcolor import colored

def print_message(message:str = "", header:str = "", footer:str = ""):
    print("\n")
    print(colored(len(message) * header, "magenta"))
    print(colored(message, "magenta"))
    print(colored(len(message) * footer, "magenta"))
    print("\n")