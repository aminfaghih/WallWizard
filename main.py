from rich.console import console

def main_menu():
    while True:
        console.print("[bold magenta]Main Menu:[/bold magenta]")
        console.print("1. Sign Up")
        console.print("2. Login")
        console.print("3. Show Leaderboard")
        console.print("4. Quit")
        choice = console.input("Choose an option: ")

        if choice == "1":
            #tabe sign up khoondeh shavad
            pass

        elif choice == "2":
            #tabe login khoondeh shavad + sign up/log in baraye player2
            pass
        elif choice == "3":
            #namayesh leader board
            pass

        elif choice == "4":
            console.print("[bold green]Goodbye![/bold green]")
            break

        else:
            console.print("[red]Invalid option![/red]")


