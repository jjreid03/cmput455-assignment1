# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification on Canvas

import sys
import random

class CommandInterface:
    # The following is already defined and does not need modification
    # However, you may change or add to this code as you see fit, e.g. adding class variables to init

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "init_game" : self.init_game,
            "legal" : self.legal,
            "play" : self.play,
            "genmove" : self.genmove,
            "undo" : self.undo,
            "score" : self.score,
            "winner" : self.winner,
            "show" : self.show,
        }

      # Initialize game state variables
        self.board = None
        self.width = 0
        self.height = 0
        self.current_player = 1
        self.p2_handicap = 0.0
        self.score_cutoff = 0.0
        self.move_history = []
        self.game_over = False

    # Convert a raw string to a command and a list of arguments
    def process_command(self, string):
        string = string.lower().strip()
        command = string.split(" ")[0]
        args = [x for x in string.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + string + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Commands will automatically print '= 1' at the end of execution on success
    def main_loop(self):
        while True:
            string = input()
            if string.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(string):
                print("= 1\n")

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #======================================================================================
    # End of predefined functionality. You will need to implement the following functions.
    # Arguments are given as a list of strings
    # We will only test error handling of the play command
    #======================================================================================

    def init_game(self, args):
        '''
            >> init_game <num_cols> <num_rows> <handicap> <score_cutoff>
            Initializes the game board with the dimension (<num_cols>, <num_rows>).
            Sets the handicap for the second player as <handicap>.
            Sets the winning score as <score_cutoff>.
        '''
        try:
            if len(args) != 4:
                return False
            
            w = int(args[0])
            h = int(args[1])
            p = float(args[2])
            s = float(args[3])
            
            #Checks board dimensions
            if w < 1 or w > 20 or h < 1 or h > 20:
                return False
            
            #Check score cutoff
            if s < 0:
                return False
            
            #Initialize game state
            self.width = w
            self.height = h
            self.p2_handicap = p
            self.score_cutoff = s if s > 0 else float('inf')
            self.board = [[0 for _ in range(w)] for _ in range(h)]
            self.current_player = 1
            self.move_history = []
            self.game_over = False
            
            #Check if player 2 already wins with handicap
            if self.p2_handicap >= self.score_cutoff:
                self.game_over = True
            
            return True
        except:
            return False
    
    def legal(self, args):
        '''
            >> legal <col> <row>
            Checks if the current player can play at specified position on the board.
        '''
        try:
            if len(args) != 2:
                return False
            
            x = int(args[0])
            y = int(args[1])
            
            #Checks if coordinates are valid or not
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                print("no")
                return True
            
            #Checks if position is filled or not
            if self.board[y][x] != 0:
                print("no")
                return True
            
            #Checks if game is over
            if self.game_over:
                print("no")
                return True
            
            print("yes")
            return True
        except:
            return False
    
    def play(self, args):
        '''
            >> play <col> <row>
            Places the current player's piece at position (<col>, <row>). Check if the move is legal before playing it.
        '''
        try:
            if len(args) != 2:
                #Wrong # of arguments: print protocol failure and return False
                print("= -1\n")
                return False
            
            x = int(args[0])
            y = int(args[1])
            
            #Checks if coordinates are within bounds
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                # Illegal move: out of bounds
                print("= -1\n")
                return False
            
            #Check if position is empty
            if self.board[y][x] != 0:
                #Illegal move: position occupied
                print("= -1\n")
                return False
            
            #Check if game is over
            if self.game_over:
                #Illegal move: game already finished
                print("= -1\n")
                return False
            
            #Move
            self.board[y][x] = self.current_player
            self.move_history.append((x, y, self.current_player))
            
            #Check for winner after the move
            p1_score, p2_score = self.calculate_scores()
            if p1_score >= self.score_cutoff or p2_score >= self.score_cutoff:
                self.game_over = True
            elif self.is_board_full():
                self.game_over = True
            
            #Switch player
            self.current_player = 3 - self.current_player
            
            return True
        except Exception as e:
            #On exception and report failure
            print("= -1\n")
            return False
    
    def genmove(self, args):
        '''
            >> genmove
            Generates and plays a random valid move.
        '''
        try:
            # Find all legal moves
            legal_moves = []
            for y in range(self.height):
                for x in range(self.width):
                    if self.board[y][x] == 0 and not self.game_over:
                        legal_moves.append((x, y))
            
            # If no legal moves, resign
            if not legal_moves:
                print("resign")
                return True
            
            # Choose a random legal move
            x, y = random.choice(legal_moves)
            
            # Play the move
            self.board[y][x] = self.current_player
            self.move_history.append((x, y, self.current_player))
            
            # Check for winner after the move
            p1_score, p2_score = self.calculate_scores()
            if p1_score >= self.score_cutoff or p2_score >= self.score_cutoff:
                self.game_over = True
            elif self.is_board_full():
                self.game_over = True
            
            # Switch player
            self.current_player = 3 - self.current_player
            
            # Output the move
            print(f"{x} {y}")
            return True
        except:
            return False

    def undo(self, args):
        '''
            >> undo
            Undoes the last move.
        '''
        try:
            if not self.move_history:
                # No move to undo: print failure status per protocol and return False
                print("= -1\n")
                return False
            
            # Get the last move
            x, y, player = self.move_history.pop()
            
            # Remove the piece from the board
            self.board[y][x] = 0
            
            # Restore the player
            self.current_player = player
            
            # Reset game over status
            self.game_over = False
            
            return True
        except:
            return False

    def score(self, args):
        '''
            >> score
            Prints the scores.
        '''
        try:
            p1_score, p2_score = self.calculate_scores()
            print(f"{p1_score} {p2_score}")
            return True
        except:
            return False

    def winner(self, args):
        '''
            >> winner
            Prints the winner information.
        '''
        try:
            p1_score, p2_score = self.calculate_scores()
            
            # Check if someone has reached the score cutoff
            if p1_score >= self.score_cutoff:
                print("1")
            elif p2_score >= self.score_cutoff:
                print("2")
            elif self.is_board_full():
                # Board is full, highest score wins
                if p1_score > p2_score:
                    print("1")
                elif p2_score > p1_score:
                    print("2")
                else:
                    print("unknown")  # Draw case (not expected to handle)
            else:
                print("unknown")
            
            return True
        except:
            return False

    def show(self, args):
        '''
            >> show
            Shows the game board.
        '''
        try:
            for row in self.board:
                row_str = []
                for cell in row:
                    if cell == 0:
                        row_str.append("_")
                    else:
                        row_str.append(str(cell))
                print(" ".join(row_str))
            return True
        except:
            return False
        
    #======================================================================================
    # Helper functions
    #======================================================================================

    def calculate_scores(self):
        '''Calculate scores for both players'''
        p1_score = 0
        p2_score = self.p2_handicap
        
        # Track which cells have been counted as part of a line
        counted_p1 = [[False for _ in range(self.width)] for _ in range(self.height)]
        counted_p2 = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        #Find all lines for each player
        p1_lines = self.find_all_lines(1)
        p2_lines = self.find_all_lines(2)
        
        #Calculate score for player 1
        for line in p1_lines:
            length = len(line)
            if length >= 1:
                score_value = 2 ** (length - 1)
                p1_score += score_value
                for x, y in line:
                    counted_p1[y][x] = True
        
        #Calculate score for player 2
        for line in p2_lines:
            length = len(line)
            if length >= 1:
                score_value = 2 ** (length - 1)
                p2_score += score_value
                for x, y in line:
                    counted_p2[y][x] = True
        
        #Add single pieces not part of any line
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 1 and not counted_p1[y][x]:
                    p1_score += 1  # 2^0 = 1
                elif self.board[y][x] == 2 and not counted_p2[y][x]:
                    p2_score += 1  # 2^0 = 1
        
        return p1_score, p2_score
    
    def find_all_lines(self, player):
        '''Find all maximal lines for a player'''
        lines = []
        visited = set()
        
        #Check all directions
        directions = [
            (1, 0),   # horizontal
            (0, 1),   # vertical
            (1, 1),   # diagonal \
            (1, -1)   # diagonal /
        ]
        
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == player:
                    for dx, dy in directions:
                        #Check to see if this is the start of a line
                        prev_x = x - dx
                        prev_y = y - dy
                        
                        #Skip if there's a piece before this in the same direction since we want to start from the beginning of the line
                        
                        if (0 <= prev_x < self.width and 0 <= prev_y < self.height and
                            self.board[prev_y][prev_x] == player):
                            continue
                        
                        #Find the complete line in this direction
                        line = [(x, y)]
                        curr_x = x + dx
                        curr_y = y + dy
                        
                        while (0 <= curr_x < self.width and 0 <= curr_y < self.height and
                               self.board[curr_y][curr_x] == player):
                            line.append((curr_x, curr_y))
                            curr_x += dx
                            curr_y += dy
                        
                        #Only add lines 2 units or more long
                        if len(line) >= 2:
                            #Create a unique identifier for this line to prevent recounts
                            line_id = tuple(sorted(line))
                            if line_id not in visited:
                                visited.add(line_id)
                                lines.append(line)
        
        return lines
    
    def is_board_full(self):
        '''Check if the board is completely filled'''
        for row in self.board:
            for cell in row:
                if cell == 0:
                    return False
        return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
