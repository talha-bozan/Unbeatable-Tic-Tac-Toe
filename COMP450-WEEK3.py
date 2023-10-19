from tkinter import *
import numpy as np
import random
import time
import asyncio

size_of_board = 600
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 50
symbol_X_color = '#EE4035'
symbol_O_color = '#0492CF'
Green_color = '#7BC043'

winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)]


class Tic_Tac_Toe():
    def __init__(self):
        self.window = Tk()
        self.window.title('Tic-Tac-Toe')
        self.canvas = Canvas(
            self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        self.window.bind('<Button-1>', self.click)

        self.initialize_board()
        self.player_X_turns = True
        self.board_status = np.zeros(shape=(3, 3))

        self.player_X_starts = True
        self.reset_board = False
        self.gameover = False

        self.tie = False
        self.X_wins = False
        self.O_wins = False

        self.X_score = 0
        self.O_score = 0
        self.tie_score = 0

        self.control_frame = Frame(self.window)
        self.control_frame.pack(side=TOP)

        self.algorithm_choice = StringVar(value="rule")
        Radiobutton(self.control_frame, text="Rule-Based",
                    variable=self.algorithm_choice, value="rule").pack(side=LEFT, padx=20)
        Radiobutton(self.control_frame, text="HeuristicAStar",
                    variable=self.algorithm_choice, value="HeuristicAStar").pack(side=LEFT, padx=20)

    def mainloop(self):
        self.window.mainloop()

    def initialize_board(self):
        for i in range(2):
            self.canvas.create_line(
                (i + 1) * size_of_board / 3, 0, (i + 1) * size_of_board / 3, size_of_board)
        for i in range(2):
            self.canvas.create_line(
                0, (i + 1) * size_of_board / 3, size_of_board, (i + 1) * size_of_board / 3)

    def play_again(self):
        self.initialize_board()
        self.player_X_starts = self.player_X_starts
        self.player_X_turns = self.player_X_starts
        self.board_status = np.zeros(shape=(3, 3))

    def draw_O(self, logical_position):

        logical_position = np.array(logical_position)
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.window.after(200, lambda: self.canvas.create_oval(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                                               grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                                               outline=symbol_O_color))

    def draw_X(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                fill=symbol_X_color)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] + symbol_size,
                                grid_position[0] + symbol_size, grid_position[1] - symbol_size, width=symbol_thickness,
                                fill=symbol_X_color)

    def display_gameover(self, winner):
        if winner == 'X':
            self.X_score += 1
            text = 'Winner: Player 1 (X)'
            color = symbol_X_color
        elif winner == 'O':
            self.O_score += 1
            if (self.algorithm_choice.get() == "HeuristicAStar"):
                text = 'Winner: A* Agent (O)'
                color = symbol_O_color
            else:
                text = 'Winner: Rule-Based Agent (O)'
                color = symbol_O_color
        else:
            tempTieScore = self.tie_score
            self.tie_score += 1
            text = 'It\'s a tie'
            color = 'gray'

        self.canvas.delete("all")

        text_length = len(text)
        font_size = min(60, int(size_of_board / text_length))

        self.canvas.create_text(
            size_of_board / 2, size_of_board / 2, font=f"cmr {font_size} bold", fill=color, text=text)

        score_text = '           Scores \n'
        score_text += 'Player 1 (X)\t:' + str(self.X_score) + '\n'
        score_text += 'Player 2 (O)\t:' + str(self.O_score) + '\n'
        score_text += 'Tie\t\t:' + str(self.tie_score)

        if (not (winner == 'X')) and (not (winner == 'O')):
            self.canvas.create_text(size_of_board / 2, 6 * size_of_board / 8,
                                    font="cmr 20 bold", fill='gray', text=score_text)
        else:
            self.canvas.create_text(size_of_board / 2, 6 * size_of_board / 8,
                                    font="cmr 20 bold", fill=Green_color, text=score_text)

        self.reset_board = True

        score_text = 'Click to play again \n'
        self.canvas.create_text(size_of_board / 2, 15 * size_of_board / 16, font="cmr 20 bold", fill="gray",
                                text=score_text)

    def convert_logical_to_grid_position(self, logical_position):
        logical_position = np.array(logical_position, dtype=int)
        return (size_of_board / 3) * logical_position + size_of_board / 6

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        return np.array(grid_position // (size_of_board / 3), dtype=int)

    def is_grid_occupied(self, logical_position):
        if self.board_status[logical_position[0]][logical_position[1]] == 0:
            return False
        else:
            return True

    def is_winner(self):
        for combo in winning_combinations:
            if self.board_status.reshape(9)[combo[0]] == self.board_status.reshape(9)[combo[1]] == \
                    self.board_status.reshape(9)[combo[2]] != 0:
                return self.board_status.reshape(9)[combo[0]]

        return 0

    def computer_play(self):

        # Check if 'O' can win in the next move and place 'O' there
        for i in range(3):
            for j in range(3):
                if self.board_status[i][j] == 0:
                    self.board_status[i][j] = 1
                    if self.is_winner() == 1:
                        self.draw_O([i, j])
                        return
                    self.board_status[i][j] = 0

        # Check if 'X' can win in the next move and block it
        for i in range(3):
            for j in range(3):
                if self.board_status[i][j] == 0:
                    self.board_status[i][j] = -1
                    if self.is_winner() == -1:
                        self.board_status[i][j] = 1
                        self.draw_O([i, j])
                        return
                    self.board_status[i][j] = 0

        # Check for center availability
        if self.algorithm_choice.get() == "HeuristicAStar":
            best_move = self.find_best_move()
            self.draw_O(best_move)
            self.board_status[best_move[0]][best_move[1]] = 1
            return

        if self.board_status[1][1] == 0:
            self.board_status[1][1] = 1
            self.draw_O([1, 1])
            return

        # Check for corner and opposite corner strategy
        corner_positions = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for corner in corner_positions:
            if self.board_status[corner[0]][corner[1]] == -1:
                opposite_corner = (2 - corner[0], 2 - corner[1])
                if self.board_status[opposite_corner[0]][opposite_corner[1]] == 0:
                    self.board_status[opposite_corner[0]
                                      ][opposite_corner[1]] = 1
                    self.draw_O(opposite_corner)
                    return

        # Check for corner and center strategy
        for corner in corner_positions:
            if self.board_status[corner[0]][corner[1]] == -1:
                side_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
                for side in side_positions:
                    if self.board_status[side[0]][side[1]] == 0:
                        self.board_status[side[0]][side[1]] = 1
                        self.draw_O(side)
                        return

        # Choose any empty corner or side
        for i in range(3):
            for j in range(3):
                if self.board_status[i][j] == 0:
                    self.board_status[i][j] = 1
                    self.draw_O([i, j])
                    return

    def HeuristicAStar(self, board, depth, is_maximizing):
        winner = self.is_winner()

        # Check if current board state is a terminal state and return a value accordingly
        if winner != 0:
            if winner == 1:
                return -10 + depth
            else:
                return 10 - depth

        if len(np.where(self.board_status == 0)[0]) == 0:
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == 0:
                        board[i][j] = -1
                        eval = self.HeuristicAStar(board, depth + 1, False)
                        board[i][j] = 0
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == 0:
                        board[i][j] = 1
                        eval = self.HeuristicAStar(board, depth + 1, True)
                        board[i][j] = 0
                        min_eval = min(min_eval, eval)
            return min_eval

    def find_best_move(self):
        best_move = (-1, -1)
        best_value = float('-inf')
        for i in range(3):
            for j in range(3):
                if self.board_status[i][j] == 0:
                    self.board_status[i][j] = -1
                    move_value = self.HeuristicAStar(
                        self.board_status, 0, False)
                    self.board_status[i][j] = 0

                    if move_value > best_value:
                        best_move = (i, j)
                        best_value = move_value
        return best_move

    def click(self, event):
        """
        if (str(self.algorithm_choice.get()) == "HeuristicAStar"):
            title = "Playing Against A* Agent"
        else:
            title = "Playing Against Rule-Based Agent"
        self.window.title(self.window.title() + " - " + title)
        """
        if not self.gameover and event.widget == self.canvas:
            grid_position = [event.x, event.y]
            logical_position = self.convert_grid_to_logical_position(
                grid_position)
            if not self.reset_board:
                if self.player_X_turns:
                    if not self.is_grid_occupied(logical_position):
                        self.draw_X(logical_position)
                        self.board_status[logical_position[0]
                                          ][logical_position[1]] = -1
                        winner = self.is_winner()
                        if winner:
                            self.gameover = True
                            if winner == -1:
                                self.window.after(
                                    200, lambda: self.display_gameover('X'))
                                return
                            else:
                                self.window.after(
                                    200, lambda: self.display_gameover('O'))
                                return
                        else:
                            if len(np.where(self.board_status == 0)[0]) == 0:
                                self.gameover = True
                                self.window.after(
                                    200, lambda: self.display_gameover('tie'))
                                return

                        # Hide the radio buttons after player X has played
                        self.control_frame.pack_forget()

                        # Now computer's turn to play
                        self.player_X_turns = not self.player_X_turns
                        self.computer_play()
                        # Set back to player's turn after computer has played
                        self.player_X_turns = True
                        winner = self.is_winner()
                        if winner:
                            self.gameover = True
                            if winner == 1:
                                self.window.after(
                                    200, lambda: self.display_gameover('O'))
                                return
                            else:
                                self.window.after(
                                    200, lambda: self.display_gameover('tie'))
                                return
        else:

            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False
            self.gameover = False


game_instance = Tic_Tac_Toe()
game_instance.mainloop()
