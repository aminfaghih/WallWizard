import os
import json
import bcrypt
import uuid
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()

USERS_FILE = "users.json"
GAMES_FILE = "games.json"
LEADERBOARD_FILE = "leaderboard.json"
SAVED_GAMES_FILE = "saved_games.json"
def save_current_game(player1, player2, board, walls, walls_h, walls_v, current_player, start_time):
    saved_games = load_json(SAVED_GAMES_FILE, [])

    end_time = datetime.now()
    duration = end_time - start_time

    game_state = {
        "id": str(uuid.uuid4()), 
        "players": {
            "player1": player1,
            "player2": player2
        },
        "board": board,
        "walls": walls,
        "walls_h": list(walls_h), 
        "walls_v": list(walls_v),
        "current_player": current_player,
        "timestamp": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": str(duration)
    }
    
    saved_games.append(game_state)
    
    save_json(SAVED_GAMES_FILE, saved_games)
    
    console.print(f"[green]Game saved with ID: {game_state['id']}[/green]")
    return game_state['id']

def load_saved_games():
    saved_games = load_json(SAVED_GAMES_FILE, [])
    
    if not saved_games:
        console.print("[yellow]No saved games found.[/yellow]")
        return None
    
    table = Table(title="Saved Games")
    table.add_column("ID", justify="left")
    table.add_column("Player 1", justify="left")
    table.add_column("Player 2", justify="left")
    table.add_column("Timestamp", justify="left")
    table.add_column("Duration", justify="left")
    
    for game in saved_games:
        table.add_row(
            game['id'], 
            game['players']['player1'], 
            game['players']['player2'], 
            game['timestamp'],
            game.get('duration', 'N/A')
        )
    
    console.print(table)
    return saved_games
def load_json(file_path, default_value):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            return default_value
    return default_value

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def initialize_files():
    for file_path, default_value in [(USERS_FILE, {}), (GAMES_FILE, []), (LEADERBOARD_FILE, {})]:
        if not os.path.exists(file_path):
            save_json(file_path, default_value)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def sign_up():
    users = load_json(USERS_FILE, {})
    console.print("[bold cyan]Sign-Up:[/bold cyan]")
    username = console.input("Enter username: ")
    if username == "":
        return '-'
    if username in users:
        console.print("[red]Username already exists![/red]")
        return None
    email = console.input("Enter email: ")
    password = console.input("Enter password: ", password=True)
    user_id = str(uuid.uuid4())
    users[username] = {
        "id": user_id,
        "email": email,
        "password": hash_password(password),
        "games": []
    }
    save_json(USERS_FILE, users)
    console.print("[green]Account created successfully![/green]")
    return username

def login():
    users = load_json(USERS_FILE, {})
    console.print("[bold cyan]Login:[/bold cyan]")
    username = console.input("Enter username: ")
    if username == "":
        return '-'
    if username not in users:
        console.print("[red]Username does not exist![/red]")
        return None
    password = console.input("Enter password: ", password=True)
    if not verify_password(password, users[username]["password"]):
        console.print("[red]Incorrect password![/red]")
        return None
    console.print("[green]Login successful![/green]")
    return username

def initialize_board():
    board = [["." for _ in range(9)] for _ in range(9)]
    board[0][4] = "P1"
    board[8][4] = "P2"
    return board
def resume_saved_game():
    saved_games = load_json(SAVED_GAMES_FILE, [])
    
    if not saved_games:
        console.print("[yellow]No saved games found.[/yellow]")
        return None
    
    table = Table(title="Saved Games")
    table.add_column("ID", justify="left")
    table.add_column("Player 1", justify="left")
    table.add_column("Player 2", justify="left")
    table.add_column("Timestamp", justify="left")
    table.add_column("Duration", justify='left')
    
    for game in saved_games:
        table.add_row(
            game['id'], 
            game['players']['player1'], 
            game['players']['player2'], 
            game['timestamp'],
            game.get('duration', 'N/A')  
        )
    
    console.print(table)
    
    game_id = console.input("Enter the ID of the game you want to resume: ")
    
    selected_game = next((game for game in saved_games if game['id'] == game_id), None)
    
    if not selected_game:
        console.print("[red]Invalid game ID![/red]")
        return None
    
    player1 = selected_game['players']['player1']
    player2 = selected_game['players']['player2']
    
    console.print("[yellow]Authentication required to resume the game:[/yellow]")
    
    console.print(f"[cyan]Login for Player 1 ({player1}):[/cyan]")
    authenticated_player1 = login()
    if authenticated_player1 != player1:
        console.print("[red]Authentication failed for Player 1![/red]")
        return None
    
    console.print(f"[cyan]Login for Player 2 ({player2}):[/cyan]")
    authenticated_player2 = login()
    if authenticated_player2 != player2:
        console.print("[red]Authentication failed for Player 2![/red]")
        return None
    
    board = selected_game['board']
    walls = selected_game['walls']
    
    walls_h = set(tuple(wall) if isinstance(wall, list) else wall for wall in selected_game['walls_h'])
    walls_v = set(tuple(wall) if isinstance(wall, list) else wall for wall in selected_game['walls_v'])
    
    current_player = selected_game['current_player']
    
    saved_games = [game for game in saved_games if game['id'] != game_id]
    save_json(SAVED_GAMES_FILE, saved_games)
    
    return {
        'board': board,
        'walls': walls,
        'walls_h': walls_h,
        'walls_v': walls_v,
        'current_player': current_player,
        'player1': player1,
        'player2': player2
    }
def draw_board(board, walls_h, walls_v):
    top_border = "┌───" + "┬───" * 8 + "┐\n"
    bottom_border = "└───" + "┴───" * 8 + "┘\n"
    visual = top_border
    for row in range(9):
        line = "│"
        for col in range(9):
            if (row,col) in walls_v:
                if board[row][col] == "P1":
                    line += "⚫ ┃"
                elif board[row][col] == "P2":
                    line += "⚪ ┃"
                else:
                    line += "   ┃"
            else:
                if board[row][col] == "P1":
                    line += "⚫ │"
                elif board[row][col] == "P2":
                    line += "⚪ │"
                else:
                    line += "   │"
                
        visual += line + "\n"
        if row < 8:
            horizontal_line = "├"
            for col in range(9):
                if (row, col) in walls_h:
                    horizontal_line += "═══"
                else:
                    horizontal_line += "───"
                horizontal_line += "┼" if col < 8 else "┤"
            visual += horizontal_line + "\n"
    visual += bottom_border
    console.print(Panel(visual, title="Game Board", expand=False))

def play_game(player1, player2):
    start_time = datetime.now()

    load_option = console.input("Do you want to load a saved game? (yes/no): ").lower()
    move_done = False
    wall_done = False
    if load_option == 'yes':
        loaded_game = resume_saved_game()
        if loaded_game:
            board = loaded_game['board']
            walls = loaded_game['walls']
            walls_h = loaded_game['walls_h']
            walls_v = loaded_game['walls_v']
            current_player = loaded_game['current_player']
            player1 = loaded_game['player1']
            player2 = loaded_game['player2']
        else:
            console.print("[yellow]Starting a new game instead.[/yellow]")
            board = initialize_board()
            walls = {"P1": 10, "P2": 10}
            walls_h = set()  
            walls_v = set() 
            current_player = "P1"
           
    else:
        board = initialize_board()
        walls = {"P1": 10, "P2": 10}
        walls_h = set()  
        walls_v = set()  
        current_player = "P1"    
    def dfs(new_walls_h, new_walls_v, i, j, playerName, visited):
        visited.append((i, j))
        
        if playerName == "P1" and i >= 8:
            return True
        if playerName == "P2" and i <= 0:
            return True
            
        if 0 <= i <= 8 and 0 <= j <= 8:
            if i + 1 <= 8 and (i + 1, j) not in visited and (i, j) not in new_walls_h:
                if dfs(new_walls_h, new_walls_v, i + 1, j, playerName, visited):
                    return True
            if i - 1 >= 0 and (i - 1, j) not in visited and (i - 1, j) not in new_walls_h:
                if dfs(new_walls_h, new_walls_v, i - 1, j, playerName, visited):
                    return True   
            if j + 1 <= 8 and (i, j + 1) not in visited and (i, j) not in new_walls_v:
                if dfs(new_walls_h, new_walls_v, i, j + 1, playerName, visited):
                    return True
            if j - 1 >= 0 and (i, j - 1) not in visited and (i, j - 1) not in new_walls_v:
                if dfs(new_walls_h, new_walls_v, i, j - 1, playerName, visited):
                    return True
                    
        return False

    def move_player(player):
        console.print(f"[cyan]{player}, enter your move direction (up/down/left/right):[/cyan]")
        direction = console.input()
        row, col = [(r, c) for r in range(9) for c in range(9) if board[r][c] == player][0]

        new_row, new_col = row, col
        if direction == "up" and row > 0 and (row - 1, col) not in walls_h:
            new_row -= 1
        elif direction == "down" and row < 8 and (row, col) not in walls_h:
            new_row += 1
        elif direction == "left" and col > 0 and (row, col - 1) not in walls_v:
            new_col -= 1
        elif direction == "right" and col < 8 and (row, col) not in walls_v:
            new_col += 1
        else:
            console.print("[red]Invalid move. Blocked by a wall or edge of the board. Try again.[/red]")
            return False

        if board[new_row][new_col] == ".":
            board[row][col] = "."
            board[new_row][new_col] = player
            return True
        elif board[new_row][new_col] == "P2" or board[new_row][new_col] == "P1":
    
            if direction == "up":
                if new_row >= 1 and (new_row-1,new_col) not in walls_h:
                    board[row][col] = "."
                    board[new_row-1][new_col] = player
                    return True
                else:
                    console.print("[red]You can't jump over the oponent!")
                    console.print("[cyan]You can diagonally move to left or right")
                    console.print("[cyan]enter your diagnoal move direction (right/left):")
                    diagonal_direction = console.input()
                    if diagonal_direction == "right":
                        if(new_col<8 and ((new_row,new_col) not in walls_v or (new_row,new_col+1) not in walls_h)):
                            board[row][col] = "."
                            board[new_row][new_col+1] = player
                            return True
                        else:
                            console.print("[red]Path is blocked by a wall or edge of the board. try something else.")
                            return False
                    elif diagonal_direction == "left":
                        if(new_col>0 and ((new_row,new_col-1) not in walls_v or (new_row,new_col-1) not in walls_h)):
                            board[row][col] = "."
                            board[new_row][new_col-1] = player
                            return True
                        else:
                            console.print("[red]Path is blocked by a wall or edge of the board. try something else.")
                            return False
                    
            elif direction == "down":
                if new_row <=7 and (new_row,new_col) not in walls_h:
                    board[row][col] = "."
                    board[new_row+1][new_col] = player
                    return True
                else:
                    console.print("[red]You can't jump over the oponent!")
                    console.print("[cyan]You can diagonally move to left or right")
                    console.print("[cyan]enter your diagnoal move direction (right/left):")
                    diagonal_direction = console.input()
                    if diagonal_direction == "right":
                        if(new_col<8 and ((new_row,new_col) not in walls_v or (new_row-1, new_col+1) not in walls_h)):
                            board[row][col] = "."
                            board[new_row][new_col+1] = player
                            return True
                        else:
                            console.print("[red]Path is blocked by a wall or edge of the board. try something else.")
                            return False
                    elif diagonal_direction == "left":
                        if(new_col>0 and ((new_row-1,new_col-1) not in walls_h or (new_row,new_col-1) not in walls_v)):
                            board[row][col] = "."
                            board[new_row][new_col-1] = player
                            return True
                        else:
                            console.print("[red]Path is blocked by a wall or edge of the board! try something else.")
                            return False
            else:
                return False
        else:
            console.print("[red]Move blocked. Try again.[/red]")
            return False
    def place_wall(player):
        console.print(f"[cyan]{player}, enter the wall position (row,col,orientation [h/v]):[/cyan]")
        try:
            row, col, orientation = console.input().strip().split(",")
            row, col = int(row)-1, int(col)-1
            if orientation not in ("h", "v"):
                raise ValueError("Invalid orientation")
            if walls[player] <= 0:
                console.print("[red]No walls left![/red]")
                return False
            
            if orientation == "h":
                if col>=0 and col <=7 and row<=7 and row>=0 and (row, col) not in walls_h and (row, col+1) not in walls_h:
                    if row<7 and (row,col) in walls_v and (row+1,col) in walls_v:
                        console.print("[red]Walls must not overlap!")
                        return False
                    hypothetical_walls_h = walls_h.copy()
                    hypothetical_walls_v = walls_v.copy()
                    hypothetical_walls_h.add((row,col))
                    hypothetical_walls_h.add((row,col+1))
                    player1Row, player1Col = [(r, c) for r in range(9) for c in range(9) if board[r][c] == "P1"][0]
                    player2Row, player2Col = [(r2, c2) for r2 in range(9) for c2 in range(9) if board[r2][c2] == "P2"][0]
                    visitedP1 = []
                    visitedP2 = []
                    if not dfs(hypothetical_walls_h , hypothetical_walls_v, player1Row, player1Col, "P1", visitedP1) or not dfs(hypothetical_walls_h , hypothetical_walls_v, player2Row, player2Col, "P2", visitedP2):
                        console.print("[red]You can't block all paths for a player!")
                        return False
                    walls_h.add((row, col))
                    walls_h.add((row, col+1))
                else:
                    console.print("[red]Wall already exists or invalid position![/red]")
                    return False
            elif orientation == "v":
                if row >=0 and row <= 7 and col>=0 and col<=7 and (row, col) not in walls_v and (row+1, col) not in walls_v:
                    if col<7 and (row,col) in walls_h and (row,col+1) in walls_h:
                        console.print("[red]Walls must not overlap!")
                        return False
                    hypothetical_walls_h = walls_h.copy()
                    hypothetical_walls_v = walls_v.copy()
                    hypothetical_walls_v.add((row,col))
                    hypothetical_walls_v.add((row+1,col))
                    player1Row, player1Col = [(r, c) for r in range(9) for c in range(9) if board[r][c] == "P1"][0]
                    player2Row, player2Col = [(r2, c2) for r2 in range(9) for c2 in range(9) if board[r2][c2] == "P2"][0]
                    visitedP1 = []
                    visitedP2 = []
                    if not dfs(hypothetical_walls_h , hypothetical_walls_v, player1Row, player1Col, "P1", visitedP1) or not dfs(hypothetical_walls_h , hypothetical_walls_v, player2Row, player2Col, "P2", visitedP2):
                        console.print("[red]You can't block all paths for a player!")
                        return False
                    walls_v.add((row, col))
                    walls_v.add((row+1, col))
                else:
                    console.print("[red]Wall already exists or invalid position![/red]")
                    return False

            walls[player] -= 1
            return True
        except ValueError:
            console.print("[red]Invalid input. Format should be row,col,orientation (e.g., 3,4,h).[/red]")
            return False
        except Exception:
            console.print("[red]Unexpected error. Try again.[/red]")
            return False
    while True:
        draw_board(board, walls_h, walls_v)
        
        action = console.input(f"{current_player}, choose action (move/wall/save/quit): ").strip().lower()

        if action == "save":
            save_current_game(player1, player2, board, walls, walls_h, walls_v, current_player, start_time)
            continue

        if action == "quit":
            console.print("[red]Game quit![/red]")
            return

        if action == "move":
            if move_player(current_player):
                p1r, p1c = [(ro, co) for ro in range(9) for co in range(9) if board[ro][co] == "P1"][0]
                p2r, p2c = [(ro2, co2) for ro2 in range(9) for co2 in range(9) if board[ro2][co2] == "P2"][0]
                
                if current_player == "P1" and p1r >= 8:
                    console.print("[green]P1 wins![/green]")
                    save_current_game(player1, player2, board, walls, walls_h, walls_v, current_player, start_time)
                    update_leaderboard(player1)
                    return
                elif current_player == "P2" and p2r <= 0:
                    console.print("[green]P2 wins![/green]")
                    save_current_game(player1, player2, board, walls, walls_h, walls_v, current_player, start_time)
                    update_leaderboard(player2)
                    return
                
                
                current_player = "P2" if current_player == "P1" else "P1"

        elif action == "wall":
            if walls[current_player] > 0:
                if place_wall(current_player):
                    
                    current_player = "P2" if current_player == "P1" else "P1"
            else:
                console.print("[red]No walls left![/red]")
def update_leaderboard(winner):
    leaderboard = load_json(LEADERBOARD_FILE, {})
    if winner not in leaderboard:
        leaderboard[winner] = {"wins": 0, "losses": 0}
    leaderboard[winner]["wins"] += 1
    save_json(LEADERBOARD_FILE, leaderboard)

def show_leaderboard():
    leaderboard = load_json(LEADERBOARD_FILE, {})
    table = Table(title="Leaderboard")
    table.add_column("Player", justify="left")
    table.add_column("Wins", justify="right")
    for player, stats in sorted(leaderboard.items(), key=lambda x: -x[1]["wins"]):
        table.add_row(player, str(stats["wins"]))
    console.print(table)

def main_menu():
    initialize_files()
    while True:
        console.print("[bold magenta]Main Menu:[/bold magenta]")
        console.print("1. Sign Up")
        console.print("2. Login")
        console.print("3. Show Leaderboard")
        console.print("4. Quit")
        choice = console.input("Choose an option: ")

        if choice == "1":
            sign_up()

        elif choice == "2":
            username1 = login()
            while(username1==None):
                username1 = login()
            if username1 == '-' :
                continue    
            console.print("[yellow]Now for player 2:")
            console.print("[yellow]Enter 1 to log in and 2 to sign up:")
            player2option = console.input()
            while(player2option != '1' and player2option != '2'):
                console.print("[red]Invalid option! Try again.")
                player2option = console.input()
            if(player2option == "1"):
                username2 = login()  
            if(player2option == "2"):
                username2 = sign_up()
            while(username2==None or username2 == username1):
                if(username2 == username1):
                    console.print("[red]Player 1 has already picked this account! You must try another one.")
                console.print("[yellow]Player 2:")
                console.print("[yellow]Enter 1 to log in and 2 to sign up:")
                player2option = console.input()
                while(player2option != '1' and player2option != '2'):
                    console.print("[red]Invalid option! Try again.")
                    player2option = console.input()
                if(player2option == "1"):
                    username2 = login()  
                if(player2option == "2"):
                    username2 = sign_up()
            if(username2 == '-'):
                continue
                
            play_game(username1, username2)  

        elif choice == "3":
            show_leaderboard()

        elif choice == "4":
            console.print("[bold green]Goodbye![/bold green]")
            break

        else:
            console.print("[red]Invalid option![/red]")

if __name__ == "__main__":
    main_menu()
