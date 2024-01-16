"""ClientServeur class file"""

import threading
import socket
from riversi import BoardWithoutGUI

class ClientServeur():
    """Class for a clientServeur game logic
    """
    def __init__(self) -> None:
        self.player = 0

    def host_game(self,host, port=55555):
      """Procedure who permit to host a game 

      host: your own ip address
      port: the connection port 
      """

      print("Start server...")
      server = socket.socket()
      server.bind((host, port))
      server.listen()
      client, _ = server.accept()

      conn_thread = threading.Thread(target=self.handle_connection, args=(client, ))
      conn_thread.start()

    def connect_to_game(self, host, port=55555):
      """Procedure who permit to host a game 

      host: your own ip address
      port: the connection port 
      """
      client = socket.socket()
      client.connect((host, port))

      print("Connect to the server")

      self.player = 1
      conn_thread = threading.Thread(target=self.handle_connection, args=(client, ))
      conn_thread.start()

    def handle_connection(self, client):
        """Procedure for the client serveur game logic

        client: your game socket
        """
        raise NotImplementedError

class BoardWithoutGUIClientServer(BoardWithoutGUI, ClientServeur):
  """Class of a reversi Game Board for with a multiplayer connexion.
  
  This class is inherited of BoardWithoutGUI and ClientServeur.
  """

  def __init__(self, size) -> None:
      super().__init__(size)
      self.turn = 0
      self.turn_pass = 0

  def handle_connection(self, client):
      while self.turn_pass <= 2:
          str_player = 'black' if self.turn == 0 else 'white'
          self.next_move(self.turn)

          print(self)

          if len(self.next_possible_move) == 0:
              self.turn_pass += 1
              print(f"{str_player.capitalize()} player can't play.")
          else:
              print(f"{str_player.capitalize()} pawn's turn.")
              if self.turn == self.player:
                  index_of_move = self.choice_move()
                  cord = list(self.next_possible_move.keys())[index_of_move]
                  vector = self.next_possible_move[cord]
                  self.place_pawn(self.turn, cord, vector)

                  self.turn_pass = 0
                  self.turn = 1 - self.turn
                  client.send(str(index_of_move).encode('utf-8'))

              else:
                  data = client.recv(128)

                  if not data:
                      break

                  index_of_move = int(data.decode('utf-8'))
                  cord = list(self.next_possible_move.keys())[index_of_move]
                  vector = self.next_possible_move[cord]
                  self.place_pawn(self.turn, cord, vector)

                  self.turn_pass = 0
                  self.turn = 1 - self.turn

      client.close()

if __name__ == '__main__':
    board_server = BoardWithoutGUIClientServer(8)
    board_server.host_game("0.0.0.0", 55555)
