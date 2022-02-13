from datetime import datetime
import random


def is_valid_date(year, month, day):
    """Returns True if the given day, month, and year form a valid date"""
    day_count_for_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year%4==0 and (year%100 != 0 or year%400==0):
        day_count_for_month[2] = 29
    return (1 <= month <= 12 and 1 <= day <= day_count_for_month[month] and year>1850)

def print_separator():
    """Prints a separator to the terminal for better output clarity"""
    print()
    print("="*50)
    print()

class GameInitialization:
    """Implements functions for input checking"""
    # TODO: Understand whether I should use my date of birth or let the user pick one
    # keeps the input state here
    birth_day = None
    birth_month = None
    birth_year = None
    @classmethod
    def read_date_of_birth(cls):
        """
        Reads the date of birth input, checks its validity and returns the result
        """
        try:
            line = input("Enter your date of birth in the format DD-MM-YYYY:  ")
            day, month, year = map(int, line.split('-'))
            assert is_valid_date(year, month, day)

            cls.birth_day = day
            cls.birth_month = month
            cls.birth_year = year
            return day, month, year
        except KeyboardInterrupt:
            raise
        except:
            print("\nInvalid date input.\n")
            return cls.read_date_of_birth()


    @classmethod
    def read_initial_position(cls):
        """
        Reads the initial position and checks its validity
        """
        try:
            result = int(input(f"Enter the initial position (should be in the interval [1 .. {cls.birth_day + cls.birth_month + cls.birth_year}]): "))
            # TODO: Should we include the final position here?
            assert result >= 1 and result <= cls.birth_day + cls.birth_month + cls.birth_year
            return result
        except KeyboardInterrupt:
            raise
        except:
            print("\nInvalid input\n")
            return cls.read_initial_position()

    @classmethod
    def random_initial_position(cls):
        """Returns a random initial position"""
        result = random.randint(1, cls.birth_day + cls.birth_month + cls.birth_year)
        print(f"Randomly chosen initial position : {result}")
        return result

    @classmethod
    def define_intial_position(cls):
        """Prompts the user to choose either a random or user initial position, then returns either a read from the stdin or a random initial position"""
        try:
            result = input("Do you want to specify the intial position (otherwise it will be randomly initialized)? Enter either y or n:  ")
            assert result in ['y', 'n']
            if result == 'y':
                return cls.read_initial_position()
            return cls.random_initial_position()
        except KeyboardInterrupt:
            raise
        except:
            print("\nInvalid input.\n")
            return cls.define_intial_position()

    @classmethod
    def read_game_mode(cls):
        """Reads the game mode name and checks its validity"""
        try:
            print("The Game has the following modes:\n\t- smart (if possible, the program uses a winning strategy against user)")
            print("\t- random (program makes random moves)\n\t- advisor (if possible, the program advises a winning strategy for the user).\n")
            result = input(f"Choose the game mode (smart/random/advisor): ").strip()
            assert result in ['smart', 'random', 'advisor']
            return result
        except KeyboardInterrupt:
            raise
        except:
            print("\nInvalid game mode name.\n")
            return cls.read_game_mode()

    @classmethod
    def read_play_again(cls):
        """Reads the input for playing another game"""
        try:
            result = input("Do you want to play another game? (y/n): ")
            assert result in ['y', 'n']
            return result == 'y'
        except KeyboardInterrupt:
            raise
        except:
            print("\nInvalid input.\n")
            return cls.read_play_again()

class Game:
    """
    Implements the game logic as well as the file logging of the game's play
    """
    # The IDs should be consecutive
    DUPLICATOR_ID = 0
    SPOILER_ID = 1

    PLAYER_NAMES = {
        0: 'Duplicator', 1: 'Spoiler'
    }

    def __init__(self, day, month, year, initial_position) -> None:
        # Initialize game
        self.next_player = self.__class__.DUPLICATOR_ID
        self.winner = None
        self.current_position = initial_position
        self.initial_position  = initial_position
        self.final_position = day + month + year 
        self.max_move = day + month
        assert initial_position >= 1

        # Create and open the log file for writing
        self.log_file_name =  datetime.now().strftime("%d_%H_%M_%S.txt")
        self.log_file = open(self.log_file_name, 'a')
        print(f"-> Opened log for the current game at {self.log_file.name}")
        self.log_operation(f"Started Game at initial position {self.current_position}, with final position {self.final_position}")
        self.log_operation(f"Allowed moves are in [(+1) .. (+{self.max_move})], legal positions are [{self.current_position} .. {self.final_position}].")


    def __del__(self):
        # We need to make sure that the log file buffer is flushed and closed when the object is deleted
        self.log_file.flush()
        self.log_file.close()

    def log_operation(self, message):
        """Helper function to log output to both stdout and the log file"""
        print(message)
        self.log_file.write(message+'\n')

    def perform_move(self, move):
        """Performs a move and checks if a player wins after the move"""
        assert self.winner is None 
        assert move >= 1 and move <= self.max_move and self.current_position + move <= self.final_position, "Illegal move"
        self.current_position += move 
        self.log_operation(f"{self.__class__.PLAYER_NAMES[self.next_player]} moved by (+{move}) to {self.current_position}")
        # Check for winning
        if self.current_position == self.final_position:
            self.winner = self.next_player
            self.log_operation(f"{self.__class__.PLAYER_NAMES[self.winner]} WON!")
        self.next_player = (self.next_player+1)%2


class SpoilerBot:
    """
    Implements the playing bot that plays as the Spoiler
    """
    def __init__(self, day, month, year, initial_position, game_mode) -> None:
        # Initialize the game
        self.game = Game(day, month, year, initial_position)
        # The corresponding function to use for each playing mode
        self.mode_implementations = {
            'random': self.random_mode,
            'smart': self.smart_mode,
            'advisor': self.advisor_mode
        }
        self.play_mode = self.mode_implementations[game_mode]
        self.game.log_operation(f"Game started in {game_mode} mode.")


        self.winning_strategy = set()
        self.winning_strategy.update(range(max(self.game.final_position - self.game.max_move, initial_position), self.game.final_position))
        # Holds the winning moves from every winning positions
        self.winning_moves = {x: [self.game.final_position] for x in self.winning_strategy}
        
        self.find_winning_strategy()
        

    def find_winning_strategy(self):
        """
        Calculates the winning positions, as well as the winning moves, using Backwards-Induction
        """
        previous_positions = self.winning_strategy
        while True:
            new_positions = set()
            updated_strategy = False
            for i in previous_positions:
                for opponent_position in range(max(self.game.initial_position, i-self.game.max_move), i):
                    if opponent_position < self.game.initial_position or opponent_position in self.winning_strategy:
                        continue
                    all_winning = True
                    # Check that all opponent moves from this position lead to a winning position for the player
                    for potential_opponent_next_position in range(opponent_position+1, opponent_position+self.game.max_move+1):
                        if potential_opponent_next_position not in self.winning_strategy:
                            all_winning = False
                            break
                    if all_winning:
                        # Add all positions that lead the opponent to this position
                        new_positions.update(range(max(self.game.initial_position, opponent_position - self.game.max_move), opponent_position))
                        # Add all the moves
                        for x in range(opponent_position - self.game.max_move, opponent_position):
                            self.winning_moves[x] = (self.winning_moves.get(x) or [])  + [opponent_position]
                        updated_strategy = True
            self.winning_strategy.update(new_positions)
            previous_positions = new_positions

            # If we didn't find any new winning positions to explore, stop the backwards induction algorithm
            if not updated_strategy:
                break

    def play(self):
        """Plays the game"""
        print("GAME ON!")
        while self.game.winner is None:
            self.play_mode()
        if self.game.winner == Game.DUPLICATOR_ID:
            print("\nCONGRATULATIONS! YOU WON!\n")
        else:
            print("\nUNFORTUNATELY, YOU LOST AGAINST THE SPOILER ...\n")

    def read_next_move(self):
        """Takes the next player move"""
        try:
            result = int(input(f"You're at position {self.game.current_position}. Enter your next move (should be in range [1 .. {min(self.game.max_move, self.game.final_position - self.game.current_position)}]): "))
            assert result in range(1, min(self.game.max_move, self.game.final_position - self.game.current_position)+1)
            return result
        except KeyboardInterrupt:
            raise
        except:
            print("Invalid move.")
            return self.read_next_move()

    def pick_smart_move(self):
        """
        Picks the biggest position from the winning strategy that is accessible from the current position (to make the game end as fast as possible).
        Returns None in case the current position doesn't belong to the winning strategy
        """
        if self.game.current_position in self.winning_strategy:
            return max(self.winning_moves.get(self.game.current_position)) - self.game.current_position or None
        return None

    def pick_random_move(self):
        """Returns a random legal move from the current position"""
        return random.randint(1, min(self.game.max_move, self.game.final_position - self.game.current_position))

    def random_mode(self):
        """Plays in random mode"""
        # Duplicator move
        self.game.perform_move(self.read_next_move())
        if self.game.winner is not None:
            return
        # Spoiler move
        self.game.perform_move(self.pick_random_move())

    def smart_mode(self):
        """Plays in smart mode"""
        # Duplicator move
        self.game.perform_move(self.read_next_move())
        if self.game.winner is not None:
            return
        # Spoiler move (a winning move if it exists, otherwise a random move)
        self.game.perform_move(self.pick_smart_move() or self.pick_random_move())

    def advisor_mode(self):
        """Plays in advisor mode"""
        # Duplicator move
        # Give advice
        advised_move = self.pick_smart_move()
        if advised_move is None:
            self.game.log_operation(f"[ADVISOR] No winning strategy at the current position. Pick any moves. Fingers-crossed!")
        else:
            self.game.log_operation(f"[ADVISOR] We advise you to move by +{advised_move}")
        self.game.perform_move(self.read_next_move())
        if self.game.winner is not None:
            return
        # Spoiler move
        self.game.perform_move(self.pick_smart_move() or self.pick_random_move())
    




if __name__ == "__main__":
    print_separator()
    print("WELCOME TO THE DUPLICATOR-SPOILER GAME.")
    print("You're playing as the Duplicator.")
    print_separator()
    try:
        day, month, year = GameInitialization.read_date_of_birth()
        while True:
            print_separator()
            initial_position = GameInitialization.define_intial_position()
            print_separator()
            game_mode = GameInitialization.read_game_mode()
            print_separator()
            game_play = SpoilerBot(day, month, year, initial_position, game_mode)
            game_play.play()
            print_separator()
            if not GameInitialization.read_play_again():
                print("See you in another play!")
                break
    except KeyboardInterrupt:
        print_separator()
        print("Game aborted. See you soon!")
