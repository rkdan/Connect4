# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:54:07 2018

This is my Connect 4 game.

What it *should* do:
    ~ The player has a choice of playing against another human, which is convenient for testing edge
      cases.
    ~ The player can choose between a dumb AI that picks a column at random, or;
    ~ The player can choose a 'smart' AI that is a little more descerning in it's choices. For
      details, see the relevant classes.
    ~ The player can choose a board size from 1 x 1 to 15 x 15.
    ~ The player can pick their name.
    ~ The player can choose whether to go first or second.
What it will NOT do:
    ~ This is Connect 4, not Connect 5, Connect 3 or Connect 1,000,000
    ~ The player cannot name the AI.
    ~ The player cannot change any colors on the board, or add additional players.
    
The program *should* run fine in Spyder3. But for a better experience, run in the command line. The
display tends to freeze for a few seconds at the start if run on Spyder. I set my line widths to 100
so if you're having any wrapping issues, that could be why.

"""
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==================================================================================================
# IMPORT STATEMENTS
# ==================================================================================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('classic')    # The best kind of style.


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==================================================================================================
# MAIN GAME
# ==================================================================================================
# 
# The main game consists of 5 classes:
#   1. Board
#   2. HumanPlayer
#   3. StupidMachinePlayer
#   4. NonStupidMachinePlayer
#   5. Game
# Originally intended to be stand alone, and it is to a certain extent, but in order to use some of
# the fancy graph functions, I had to embed function calls within this class. So if this class is to
# be fully stand alone, those function calls need to be commented out. I have highlighted these
# calls with # ***.
# ==================================================================================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Board:
    """Defines the board class.    
    Attr: board
    """   
    def __init__(self, columns, rows):
        """Initializer for the Board class"""
        self.rows = rows
        self.columns = columns
        self.board = np.zeros((rows, columns))
       
    def __str__(self):
        """string representation of the board."""
        string = ""
        for row in self.board:
            string += str(row) + '\n'
        return string
    
    def change_board(self, column, symbol):
        """Updates the board to reflect the most recent move."""
        if symbol == 'B':
            modifier = 1
        else:
            modifier = -1
        column_array = self.board[:,column]
        flipped_column = np.flip(column_array, 0)
        i = 0
        while i < self.rows:
            if flipped_column[i] == 0.0:
                self.board[self.rows-1-i][column] = modifier
                break
            else:
                i += 1
    
    def create_sub_arrays(self, size):
        """Called by the is_win() method to break up the main board into 4x4
        sub-arrays."""
        row_start = 0
        sub_boards = []       
        while row_start < ROWS-(size-1):
            col_start = 0
            while col_start < COLS-(size-1):
                sub_board = self.board[row_start:row_start+size, col_start:col_start+size]
                sub_boards.append(sub_board)
                col_start += 1
            row_start += 1
        return sub_boards
    
    def is_win(self, number):
        """Searches the boards for wins."""
        sub_boards = self.create_sub_arrays(number)
        win = False
        # diagonals
        for sub_board in sub_boards:
            if np.trace(sub_board) == number or np.trace(sub_board) == -number:
                return True
            flipped = np.fliplr(sub_board)
            if np.trace(flipped) == number or np.trace(flipped) == -number:
                return True
        # rows
            for row in sub_board:
                if sum(row) == number or sum(row) == -number:
                    return True
        # columns
            for row in sub_board.transpose():
                if sum(row) == number or sum(row) == -number:
                    return True
        return win

    def is_full(self, column):
        """Checks to see if a column is full. Returns True if full, False, otherwise."""
        result = False
        if 0. not in self.board.transpose()[column]:
                result = True
        return result
   
    
class HumanPlayer:
    """Defines the player class.  
    Attr: symbol
          name
    """
   
    def __init__(self, name, symbol):
        """Initializer for the Player class."""
        self.name = name
        self.symbol = symbol
        
    def get_move(self, board):
        """Takes raw input from the player and returns the column number.
        will only allow integers between 0 and 6."""
        result = None
        while result is None:
            prompt = "please enter a column number: "
            try:
                column = int(input(self.name + ', ' + prompt))
                if (1 <= column <= COLS) and board.is_full(column-1) is False:
                    return column - 1
                else:
                    raise ValueError
            except ValueError: 
                print("\n" + ("=" * 69))
                print("INVALID COLUMN NUMBER!")
                print("=" * 69)


class StupidMachinePlayer:
    """Defines the RetardedMachinePlayer class. This AI will just go anywhere at random.
    Attr: symbol
    Name: Forrest
    """
    
    def __init__(self, name, symbol):
        """Initializer for the StupidMachinePlayerClass."""
        self.symbol = symbol
        self.name = name
        
    def get_move(self, board):
        """Get a random column."""
        column = random.randint(0,board.columns - 1)
        while board.is_full(column):    # We need to check and make sure that the column isn't full.
            column = random.randint(0, board.columns - 1)
        return column


# =============================================================================
# THE MAIN AI
# This is one class that consists of a main function, get_move(), and helper functions to return the
# results of searching the sub-arrays for matching lines. From looking at the helper fuctions,
# I attempted to abstract a function from both, but I gave up after not being able to figure out
# the errors. Similarly the rowfinder function is horrendous. This is because of the large number
# cases that need to be considered - we need to check whether we're on the left edge, right edge,
# bottom edge, and whether there are empty slots below the potential move location.
# =============================================================================
    
class NonStupidMachinePlayer:
    """Defines a machine player that doesn't play like Forrest Gump.
    Attr: symbol
    Name: Albert
    """
    
    def __init__(self, name, symbol):
        """Initializer for the NonStupidMachinePlayer."""
        self.symbol = symbol
        self.name = name
    

    def get_move(self, board):
        """The AI follows a set of instructions. It first checks whether it can make a row of
        three, then a column of three. Then it checks to see if the
        opponent can make a four anywhere on the next move. If these statements all come back
        false, then it goes to 2s. It doesn't check the diagonals. It's not that smart."""
        move = self.row_finder(board, 3)    # Check the threes
        if move is None:
            move = self.col_finder(board, 3)
        if move is None:
            move = self.row_finder(board, 3, opfor=True)    # Check opponent threes
        if move is None:
            move = self.col_finder(board, 3, opfor=True)
        if move is None:
            move = self.row_finder(board, 2)  # Check the twos
        if move is None:
            move = self.col_finder(board, 2)
        if move is None:
            move = self.row_finder(board, 2, opfor=True)  # Check the opponent twos
        if move is None:
            move = self.col_finder(board, 2, opfor=True)
        if board.is_full(move):
            self.get_move(board)
        if move is None:
            move = random.randint(0,board.columns - 1)
            while board.is_full(move):
                move = random.randint(0, board.columns - 1) 
        return move
    
    def col_finder(self, board, sub_size, opfor=False):
        """Takes a board, specification of sub-array size, and whether we are seraching for the
        opponent's disks. Returns the position in the main array that the column starts at.
        """
        sub_boards = board.create_sub_arrays(sub_size)  # split main array into sub-arrays
        if opfor is True:
            target = (-1) * sub_size    # look for opponents disk
        else:
            target = sub_size
        result = None
        moves = set()   # moves are in a set to get rid of
        col_count = 0   # keep track of sub-arrays
        for sub in sub_boards:
            row_count = 0
            trans = sub.transpose()    # transpose array
            for row in trans:
                if sum(row) == target:
                    c = col_count
                    r = row_count
                    row_index = c // (COLS - sub_size + 1)      # Converts the number of times
                    col_index = c % (COLS - sub_size + 1) + r   # iterated through the arrays, into
                    moves.add((row_index, col_index))           # array coords. Kind of like finding
                row_count += 1                                  # the parent of tree node.
            col_count += 1
        for move in moves:
            row, column = move
            if board.board[row-1][column] == 0.:
                return column
        return result
                 
    def row_finder(self, board, sub_size, opfor=False):
        """Takes a board, sub_size, and whether we are searching for the opponent's disks. Returns
        the position in the main array that the column starts at."""
        sub_boards = board.create_sub_arrays(sub_size) 
        if opfor is True:
            target = (-1) * sub_size
        else:
            target = sub_size
        result = None
        moves = set()
        col_count = 0
        for sub in sub_boards:
            row_count = 0
            for row in sub:
                if sum(row) == target:
                    c = col_count
                    r = row_count
                    row_index = c//(COLS - sub_size + 1) + r  # Identify starting indices for 3-line
                    col_index = c % (COLS - sub_size + 1)
                    moves.add((row_index, col_index))
                row_count += 1
            col_count += 1
        # We now need to check if there is a valid move either side of each 3-line
        for move in moves:
            row, column = move
            right = column + sub_size    # The position to the right of the line
            left = column - 1            # The position to the left of the line
            if row == ROWS - 1:    # If we're on the bottom
                if left <= 0:   # Far left
                    if board.board[row][right] == 0.:
                        return right
                elif right == COLS:   # Far right
                        if board.board[row][left] == 0.:
                            return left
                else:   # In the middle of the board
                    if board.board[row][left] == 0.:
                        return left
                    elif board.board[row][right] == 0.:
                        return right
            else:
                if right == COLS:
                    if board.board[row][left] == 0. and board.board[row+1][left] != 0.:
                        return left
                elif left < 0:
                    if board.board[row][right] == 0. and board.board[row+1][right] != 0.:
                        return right
                else:
                    if board.board[row][left] == 0. and board.board[row+1][left] != 0.:
                        return left
                    elif board.board[row][right] == 0. and board.board[row+1][right] != 0.:
                        return right       
        return result
                    
        
        
class Game:
    """Defines the Game class.
    Attr: player1
          player2
          current_player
          board
    """
    
    def __init__(self, player1, player2, board):
        """"Initializer for the Game class."""
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
    
    def update_display_file(self):      # ***
        """Updates the save file with the current moves. It is called every time a move is made.
        Annoyingly, this wouldn't work outside of the Game class."""
        update = open('new.txt', 'w')
        row = 0
        while row < ROWS:
            col = 0
            while col < COLS:
                item = self.board.board[(ROWS-1)-row][col]
                if item == -1:
                    item = 'red'
                elif item == 1:
                    item = 'yellow'
                else:
                    item = 'w'
                update.write("{},{},{}\n".format(col + 1, row + 1, item))
                col += 1
            row += 1
        update.close()
    
    def play(self):
        """"Main method responisble for the game."""
        while not self.game_over():
            #print(self.board)
            self.update_display_file()  # ***
            update()    # ***
            column = self.current_player.get_move(self.board)
            self.board.change_board(column, self.current_player.symbol)
            self.next_player()
        #print('\n' + '='*29)   # Board can be printed to the console
        #print(self.board)
        print('='*29)
        self.update_display_file()  # ***
        update()    # ***
        if self.is_won():
            self.winner().name
        if self.is_draw():
            print("Nobody wins! How exciting... you must both be evenly matched.")
        else:
            print("{} wins! Good job buddy!".format(self.current_player.name))
            plt.show()  # Keeps the display from just randomly closing after the line is drawn.
    
    def game_over(self):
        """Decides the current state of the game. Returns True if the game is
        either won or drawn, else returns False."""
        return self.is_won() or self.is_draw()
        
    def is_won(self):
        """Determines whether game is won. Returns a boolean."""
        return self.board.is_win(4)
        
    def is_draw(self):
        """Determines whether the game is a draw. Returns a boolean."""
        full = True
        for column in range(COLS):
            if not self.board.is_full(column):
                full = False
                break
        return not self.is_won() and full
        
    def next_player(self):
        """Changes the current player to the next player."""
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1
            
    def winner(self):
        """Gets the winner."""
        self.next_player()
        return self.current_player
    
    
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
# =================================================================================================
#  INITIALIZER AND EXTRAS
#  The display section of code is a bit of a mess, because I couldn't get the
#  animation module of matplot to work inside of a function.
# =================================================================================================
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =============================================================================
# USER PARAMETERS
# This section grabs all the info from the user about board size.
# =============================================================================

def get_user_parameters():
    """Asks the user for parameters:
        - Human vs Human, or Human vs Machine
            - Stupid Machine or Smart Machine (difficulty level)
        - Player 1 name
        - Player 2 name
        - Board size
        - Tokens to win
    """
    # 1.
    first = False
    human_or_machine = str.upper(raw_input("Are you playing with a friend (Y/N)? "))
    # AI or not
    while human_or_machine != 'Y' and human_or_machine != 'N':
        print("\nIt seems you cannot follow simple instructions. Enter either a 'Y' or a 'N'.")
        human_or_machine = str.upper(raw_input("Are you playing with a friend (Y/N)? "))
    # Human    
    if human_or_machine == 'Y':
        response = ("\nI'm not quite sure how you managed to convince another living person to play "
                    "this game with you. You must both be equally lonely...\n")
        player1 = raw_input(response + "\nPlease enter the name of player 1. ")
        player2 = raw_input("\nPlease enter the name of player 2. ")
    # AI    
    elif human_or_machine == 'N':
        response = ("\nSo sad that you have no friends to play with. Although, you are playing a "
                    "very low-budget version of Connect Four, so I shouldn't be surprised...\n")
        print(response)
        # Move first or second
        first_second = (raw_input("Do you want to move 1st or 2nd (1/2)? "))
        while first_second != '1' and first_second != '2':
            print("\nIt seems you cannot follow simple instructions. Enter either a '1' or a '2'.")       
            first_second = str.upper(raw_input("Do you want to move 1st or 2nd (1/2)? "))
        if first_second == '1':
            first = True 
        # Player name
        player1 = input("Please enter your name. ")
        difficulty_selection = ("\nOK, so there are basically two difficulty settings for this game: "
                                " 0 and 1. Setting 0 puts you against a machine player that will "
                                "pick a position entirely at random. Seriously, if you lose at this "
                                "difficulty, you should rethink your life. Setting 1 puts you "
                                "against a player that basically doesn't play like Forrest Gump. "
                                "Although, he WAS surprisingly good at ping-pong. It is unlikely "
                                "that you will win. Anyway, which "
                                "setting would you like to go with (0/1)? ")
        print(difficulty_selection)
        result = False
        while result is False:
            try:
                player2 = int(raw_input())
                if not (player2 == 0 or player2 == 1):
                    raise ValueError
                result = True
            except ValueError:
                print("\nEnter '0' for easy and '1' for hard, not 'whatever you feel like.' ")
    # Board size        
    cols = raw_input("\nOK, just one last thing. I need to know the size of the board that you want to "
                 "play on. The stanadard board size is 7 columns by 6 rows, but you can really "
                 "enter as many as you want up to 15. So, how many colummns do you want? ") 
    while not cols.isnumeric():
        cols = raw_input("\nYeah, so whatever that was, it sure as hell wasn't a valid number. "
                     "Please enter the number of columns that you want in INTEGER FORM. ")
    while not 0 < int(cols) < 16:
        cols = raw_input("\nCome on stop messing around. Pick a number between 1 and 15. ")
        
    rows = raw_input("\nAnd how many rows do you want? ")
    while not rows.isnumeric():
        rows = input("\nYeah, so whatever that was, it sure as hell wasn't a valid number. "
                     "Please enter the number of rows that you want in INTEGER FORM. ")
    while not 0 < int(rows) < 16:
        rows = raw_input("\nYou need to pick a number between 1 and 15. ")
    
    print("")
    
    return player1, player2, int(cols), int(rows), first
 
    
def user_params():
    """Instantiates the players, board, and sets up the game."""
    p1, p2, cols, rows, first  = get_user_parameters()
    if type(p2) is int:
        if p2 == 0:
            player2 = StupidMachinePlayer('Forrest', 'B')
        else:
            player2 = NonStupidMachinePlayer('Albert', 'B')
    else:
        player2 = HumanPlayer(p2, 'B')
    player1 = HumanPlayer(p1, 'R')  
    board = Board(cols, rows)
    if first is False:
        player1, player2 = player2, player1
    game = Game(player1, player2, board) 
    return cols, rows, game

global COLS, ROWS, GAME             # This is horrible practice, I know, but I couldn't really find
COLS, ROWS, GAME = user_params()    # another way to do this. Placement also had to be specific to
                                    # avoid reference errors. 


# =============================================================================
# PLOTTING THE GAME BOARD
# Calls the FuncAnimation method from matplotlibs animation library. To be perfectly honest, I'm 
# still not 100% sure how it works, but it does, so that's nice. Interestingly, this code also works
# with collecting data in real time from some other source, and updating a display.
# =============================================================================

fig = plt.figure(figsize=(COLS+1,ROWS))     # Sets up the graph. The figure size will expand with
ax1 = fig.add_subplot(1,1,1)                # the number of rows and columns.

def animate(i):   
    """Main function that creates the graph. Essentially, it takes all of the data from a saved
    file and plots them to a scatter plot. Each point has one attribute: color."""
    graph_data = open('new.txt', 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    zs = []
    for line in lines:
        if len(line)>1:
            x, y, z = line.split(',')
            xs.append(float(x) + 0.5)
            ys.append(float(y) + 0.5)
            zs.append(z)
    ax1.clear()
    plt.xlim(1, COLS+1)
    plt.ylim(1, ROWS+1)
    ax1.set_facecolor('blue')
    ax1.scatter(xs, ys, s=2500, c=zs, linestyle='None')
    if GAME.is_won():                                   # Plot the winning line.
        a, b = update_final_win()                       # Head over to the section responsible for
        plt.plot(a, b, linestyle='-', color='k', lw=5)
        winner = GAME.current_player.name
        plt.title(s="{}, wins!".format(winner))# Plot winner.
        
def update():
    """Function responsible for updating the graph in real time."""
    ani = animation.FuncAnimation(fig, animate, interval=1000)  # This should display the yellow
    fig.canvas.draw()                                           # warning symbol. Not sure why...but
    plt.pause(0.01)                                             # it still seems to work.
  
    
# =============================================================================
# GETTING INFO AFTER A WIN
# Grabs all the info about the win. The main function is update_final_win() with the remaining three
# being the helper functions.
#
# The functions repsonsible for getting the rows, columns
# and traces were all slightly different that made them difficult to abstract into one function.
# =============================================================================
   

def update_final_win():
    """Grabs the coordinates from the arrays, and converts them into actual coordinates to be
    plotted on the graph."""
    rows = get_win_row()    # Call to the helper functions
    cols = get_win_col()
    trace = get_win_trace()
    if rows is not None:
        row, column = rows
        x_i = column + 1.5
        x_f = x_i + 3
        y_i = (ROWS - row) + 0.5
        a = [x_i, x_f]      # Start point
        b = [y_i, y_i]      # End point
        return a, b
    elif cols is not None:
        row, column = cols
        y_i = (ROWS - row) + 0.5
        y_f = y_i - 3
        x_i = column + 1.5
        a = [x_i, x_i]
        b = [y_i, y_f]
        return a, b
    else:
        row, column, flipped = trace   # We have to know whether we looking at a normal trace, or
        if flipped is False:           # the trace of the flipped matrix
            x_i = column + 1.5
            x_f = x_i + 3
            y_i = (ROWS - row) + 0.5
            y_f = y_i - 3
        else:
            x_f = column + 1.5
            x_i = x_f - 3
            y_f = (ROWS - row) + 0.5
            y_i = y_f - 3
        a = [x_i, x_f]
        b = [y_i, y_f]
        return a, b
    
def get_win_row():
    """Cuts the array into sub-arrays in order to search row by row, returns the coordinates as they
    are in the array system."""
    sub_size = 4
    sub_boards = GAME.board.create_sub_arrays(sub_size) 
    target1 = 4   # Looking for both red disks and yellow disks.
    target2 = -4
    win = None
    col_count = 0
    for sub in sub_boards:
        row_count = 0
        for row in sub:
            if sum(row) == target1 or sum(row) == target2:
                c = col_count
                r = row_count
                row_index = c//(COLS - sub_size + 1) + r 
                col_index = c % (COLS - sub_size + 1)
                win = (row_index, col_index)
            row_count += 1
        col_count += 1
    return win

def get_win_col():
    """Cuts the array into sub-arrays in order to search column by column, returns the coordinates 
    as they are in the array system."""
    sub_size = 4
    sub_boards = GAME.board.create_sub_arrays(sub_size)
    target1 = 4
    target2 = -4
    win = None
    col_count = 0
    for sub in sub_boards:
        row_count = 0
        trans = sub.transpose()
        for row in trans:
            if sum(row) == target1 or sum(row) == target2:
                c = col_count
                r = row_count
                row_index = c // (COLS - sub_size + 1)
                col_index = c % (COLS - sub_size + 1) + r
                win = row_index, col_index
            row_count += 1
        col_count += 1
    return win

def get_win_trace():
    """Cuts the array into sub-arrays in order to search the trace of the arrays, and the traces
    of the flipped arrays, returns coordinates as they are in the array system."""
    sub_size = 4
    sub_boards = GAME.board.create_sub_arrays(sub_size)
    target1 = 4
    target2 = -4
    sub_count = 0
    for sub in sub_boards:   
        if np.trace(sub) == target1 or np.trace(sub) == target2:  
            c = sub_count
            row_index = c//(COLS - sub_size + 1)
            col_index = c % (COLS - sub_size + 1)
            return row_index, col_index, False
        flipped = np.fliplr(sub)
        if np.trace(flipped) == target1 or np.trace(flipped) == target2:
            c = sub_count
            c = sub_count
            row_index = c//(COLS - sub_size + 1)
            col_index = c % (COLS - sub_size + 1) + 3
            return row_index, col_index, True
        sub_count += 1
  
      
# =============================================================================
# INITIALIZER
# create_game() is the main function that sets the ball rolling.
# =============================================================================
     
def create_game():
    """This function is responsible for starting everything up."""
    save_file = open('new.txt', 'w+')   # Create new savefile 
    for row in range(1, ROWS+1):
        for col in range(1, COLS+1):
            save_file.write('{},{},w\n'.format((col), (row)))   # Fill the save file with the rows
    save_file.close()                                           # and give all data points the
    GAME.update_display_file()                                  # the attribute of whiteness.
    update()                                                    # Also grabs user parameters, and
    GAME.play()                                                 # creates the 'graph'.

create_game()     # Fire it up!

    
# =============================================================================








