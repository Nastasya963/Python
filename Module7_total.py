print("\n------- Игра в Крестики-нолики для двух игроков -------\n")

board = list(range(1, 10))

"""Выводим поле на печать"""
def build_board(board):
    print("-------------")
    for i in range(3):
        print(f'| {board[0+i*3]} | {board[1+i*3]} | {board[2+i*3]} |')
        print("+---+---+---+")
    
    
"""Проверка выигрышных комбинаций"""
def check_win(board):
   win_combine = ((0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6))
   for с in win_combine:
       if board[с[0]] == board[с[1]] == board[с[2]]:
          return board[с[0]]
   return False

"""Проверка введенных значений"""
def check_input(cur_player):
    valid = True
    while valid:
        player_answer = input(f'В какую ячейку поставим {cur_player}?')
        try:
            player_answer = int(player_answer)
        except:
            print("Введенный символ не является числом. Повторите ввод.")
            continue
        if player_answer >= 1 and player_answer <= 9:
            if str(board[player_answer-1]) not in "XO":
                board[player_answer-1] = cur_player
                valid = False
            else:
                print("Эта клетка уже занята! Повторите ввод.")
        else:
            print("Некорректный номер ячейки. Повторите ввод (число от 1 до 9).")
        
    
"""Основная функция"""
def main(board):
    count = 0
    game_over = False
    while not game_over:
        build_board(board)
        if count == 0 or count % 2 == 0:
            check_input("X")
        else:
            check_input("O")
        count += 1
        if count > 4:
            res = check_win(board)
            if res:
                print(f'Выиграл {res}!')
                game_over = True
                break
        if count == 9:
            print("Ничья!")
            break
    build_board(board)
    
main(board)

input("Нажмите Enter для выхода!")