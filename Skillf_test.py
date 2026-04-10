def print_board(board):
    """Выводит игровое поле в консоль."""
    print(f"{board[0]} | {board[1]} | {board[2]}")
    print("--+---+--")
    print(f"{board[3]} | {board[4]} | {board[5]}")
    print("--+---+--")
    print(f"{board[6]} | {board[7]} | {board[8]}")

def check_win(board):
    """Проверяет наличие победителя."""
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != ' ':
            return board[a]
    if ' ' not in board:
        return 'Ничья'
    return None

def tic_tac_toe():
    """Основная функция игры."""
    board = [' '] * 9
    current_player = 'X'
    game_over = False

    print("Добро пожаловать в Крестики-Нолики!")
    print("Выберите клетку от 1 до 9:")
    
    while not game_over:
        print_board(board)
        try:
            move = int(input(f"Ход {current_player}. Введите номер (1-9): ")) - 1
            if move >= 0 and move < 9 and board[move] == ' ':
                board[move] = current_player
            else:
                print("Неверный ход, попробуйте еще раз.")
                continue
        except ValueError:
            print("Введите число от 1 до 9.")
            continue

        winner = check_win(board)
        if winner:
            print_board(board)
            if winner == 'Ничья':
                print("Ничья!")
            else:
                print(f"Победили {winner}!")
            game_over = True
        else:
            current_player = 'O' if current_player == 'X' else 'X'

if __name__ == "__main__":
    tic_tac_toe()