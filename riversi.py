"""Reversi board class file"""

class Pawn():
  """
    Class of a reversi Pawn.

    Use in the reversi Board
    """

  def __init__(self, color: int) -> None:
    assert isinstance(color, int)
    assert 0 <= color <= 1

    self.color = color  # 0 corresponds to black and 1 to white

  def reterned(self):
    """
        Allows you to transform a black pawn into white and vice versa.
        """
    self.color = 1 - self.color  # 1 - 0 = 1 ; 1 - 1 = 0

  def get_color(self):
    """
        Return the pawn color.
        """
    return self.color

  def __str__(self):
    return str(self.get_color())

class Board():
  """
    Abstract Class of a reversi Game Board. 
    """

  def __init__(self, size) -> None:
    assert size >= 4
    self.boardsize = size
    self.create_new_board()
    raise NotImplementedError

  def create_new_board(self)->None:
    """Procedure who permit the initialization of the board in the variable self.board.
    """
    self.board = [[None for _ in range(self.boardsize)] for _ in range(self.boardsize)]
    self.board[self.boardsize // 2 - 1][self.boardsize // 2 - 1] = Pawn(1)
    self.board[self.boardsize // 2][self.boardsize // 2] = Pawn(1)
    self.board[self.boardsize // 2 - 1][self.boardsize // 2] = Pawn(0)
    self.board[self.boardsize // 2][self.boardsize // 2 - 1] = Pawn(0)

    self.next_possible_move = []
    self.player = 0
    self.turn_pass = 0

  def list_empty_neighbor(self, row_index: int, column_index: int) -> list:
    """
        Function who return the list of all the empty cells next to a specific pown.

        row_index: an int who represents the row postion of the pown in the board
        column_index: an int who represents the column postion of the pown in the board
        """
    assert isinstance(row_index, int)
    assert isinstance(column_index, int)

    assert isinstance(self.board[row_index][column_index], Pawn)

    list_possible = []

    matrix = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
    matrix.remove((0, 0))

    for vector in matrix:
      try:
        if self.board[row_index + vector[0]][column_index + vector[1]] is None:
          list_possible.append(vector)
      except IndexError:
        pass
    return list_possible

  def is_possible_play(self, color: int, row_index: int, column_index: int,
                       vector: tuple) -> bool:
    """
        Recursive function who return a boolean. 

        Return true if it's possible to play in this empty cell
        and false if it's not possible. 

        color: int who represents a color, 0 corresponds to black and 1 to white
        row_index: an int who represents the row postion of the pown in the board
        column_index: an int who represents the column postion of the pown in the board
        vector: vector who defines the direction of the move
        """
    assert isinstance(color, int)
    assert 0 <= color <= 1

    assert isinstance(row_index, int)
    assert isinstance(column_index, int)

    assert isinstance(self.board[row_index][column_index], Pawn)
    assert isinstance(vector, tuple)

    assert len(vector) >= 2
    assert isinstance(vector[0], int) and isinstance(vector[1], int)

    try:
      cell = self.board[row_index + vector[0]][column_index + vector[1]]
      if cell is None:
        return False
      if cell.get_color() == color:
        return True
      return self.is_possible_play(color, row_index + vector[0],
                                   column_index + vector[1], vector)
    except IndexError:
      return False

  def add_next_move(self, color: int, row_index: int, column_index: int):
    """
        Procedure who add to the list 'next_possible_move' the next possible move of player 'color' 
        for one cell.

        color: int who represents a color, 0 corresponds to black and 1 to white
        row_index: an int who represents the row postion of the pown in the board
        column_index: an int who represents the column postion of the pown in the board
        """
    assert isinstance(color, int)
    assert 0 <= color <= 1

    assert isinstance(row_index, int)
    assert isinstance(column_index, int)

    assert isinstance(self.board[row_index][column_index], Pawn)

    assert self.board[row_index][column_index].get_color() == 1 - color, \
    "the color of the cell have to be at the oposite of the player color"

    empty_neighbor = self.list_empty_neighbor(row_index, column_index)
    other_neighbor = [
        tuple(-each for each in vector) for vector in empty_neighbor
    ]

    for i, vector in enumerate(other_neighbor):
      if self.is_possible_play(color, row_index, column_index, vector):
        cord = (row_index + empty_neighbor[i][0],
                column_index + empty_neighbor[i][1])

        # if (cord[0] + vector[0] or cord[1] + vector[1] or cord[0] or cord[1] > -1
        #     or cord[0] + vector[0] or cord[1] + vector[1] or cord[0] or cord[1]
        #     > self.boardsize - 1):

        if 0 <= cord[0] < self.boardsize and 0 <= cord[1] < self.boardsize:
          if cord not in self.next_possible_move:
            self.next_possible_move[cord] = [vector]
          else:
            self.next_possible_move[cord].append(vector)

  def next_move(self, color: int):
    """
        Add to the list 'next_possible_move' the next_possible_move of the player 'color' 
        for all the board.

        color: int who represents a color, 0 corresponds to black and 1 to white
        """
    assert isinstance(color, int)
    assert 0 <= color <= 1

    self.next_possible_move = {}

    inverse_color = 1 - color

    for row_index, row in enumerate(self.board):
      for column_index, cell in enumerate(
          row):  # go through the board cell by cell
        if cell is not None:
          if cell.get_color() == inverse_color:
            self.add_next_move(color, row_index, column_index)

  def choice_move(self):  #can be move into the class without GUI
    """Player choose what he play and verify is the move exist

        Return the index of the choosen move in the 'next_possible_move' dictionary."""
    not_play = True
    while not_play:
      max_index = len(self.next_possible_move) - 1
      letter = input("Choose your next move: ")
      index = ord(letter[0].upper()) - 65

      if 0 <= index <= max_index:
        return index
      print(
          f"The letter need to be between {chr(65)} and {chr(65 + max_index)}")

    return None

  def place_pawn(self, color: int, cord: tuple, vectors: list):
    """Function who place a pawn in the board and flip the pawn on is path 

        color: int who represents a color, 0 corresponds to black and 1 to white
        cord: tuple who reposents the coordinates where the pown have to be place
        vectors: list of path directions in which pawns must be flipped  
        """
    assert isinstance(color, int)
    assert 0 <= color <= 1

    assert isinstance(cord, tuple)

    assert len(cord) >= 2
    assert isinstance(cord[0], int) and isinstance(cord[1], int)

    assert isinstance(vectors, list)

    self.board[cord[0]][cord[1]] = Pawn(color)
    for vector in vectors:

      new_cord = (cord[0] + vector[0], cord[1] + vector[1])

      while self.board[new_cord[0]][new_cord[1]].get_color() != color:
        self.board[new_cord[0]][new_cord[1]].reterned()
        new_cord = (new_cord[0] + vector[0], new_cord[1] + vector[1])

  def nb_of_pawn_by_color(self) -> list:
    """
        Fonction who return a list containing the number of pawn of each color.
        """
    list_nb_of_pawn = [0, 0]
    for row in self.board:
      for cell in row:
        if cell is not None:
          list_nb_of_pawn[cell.get_color()] += 1

    return list_nb_of_pawn

  def __str__(self):
    str_row = "\n" + (2 * (self.boardsize) + 1) * '-' + "\n"
    str_board = str_row
    # print(f"""Next possible move dictionary:{self.next_possible_move}""")

    letter = 0

    for row_index, row in enumerate(self.board):
      str_board += "|"
      for column_index, cell in enumerate(row):
        position = (row_index, column_index)
        if position in self.next_possible_move:

          #print(f"""({chr(65 + letter)}) POSITION / VECTEUR : {position,
                                                #self.next_possible_move[position]}""")
          letter += 1

          index = list(self.next_possible_move.keys()).index(position)
          chara = chr(65 + index)
          str_board += f'{chara}|'
        else:
          str_board += f'{cell.get_color()}|' if cell is not None else " |"
      str_board += str_row
    return str_board

class BoardSize8(Board):
  """The riversi board with a 8x8 size.

    This class is inherited of the Abstract Class 'Board'"""
  def __init__(self) -> None:
    try:
      super().__init__(8)
    except NotImplementedError:
      pass
    self.boardsize = 8

class BoardWithoutGUI(Board):
  """The reversi game without graphical interface

    This class is inherited of the Abstract Class 'Board'"""

  def __init__(self, size) -> None:
    try:
      super().__init__(size)
    except NotImplementedError:
      pass

  def play_game(self):
    """
    Fonction who permit playing reversi game. 
    """
    while self.turn_pass <= 2:
      str_player = 'black' if self.player == 0 else 'white'
      self.next_move(self.player)

      if len(self.next_possible_move) == 0:
        self.turn_pass += 1
        print(self)
        print(f"{str_player.capitalize()} player can't play.")
      else:
        print(self)
        print(f"{str_player.capitalize()} pawn's turn.")

        index_of_move = self.choice_move()
        cord = list(self.next_possible_move.keys())[index_of_move]
        vector = self.next_possible_move[cord]
        self.place_pawn(self.player, cord, vector)

        self.turn_pass = 0
      self.player = 1 - self.player

      print("GAME OVER")
      black, white = self.nb_of_pawn_by_color()
      print(f"Number of black pawn : {black}\nNumber of white pawn : {white}")
      if black > white:
        print("Black wins")
      else:
        print("White wins")

if __name__ == '__main__':
  BoardWithoutGUI(8).play_game()
