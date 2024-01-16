"""Riversi App file"""

from ast import literal_eval

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock, mainthread

from riversi import BoardSize8
from clientserver import ClientServeur, threading

class StartScreen(Screen):
    """The start screen of the Reversi app.

    This class is inherited of the kivy Screen class.

    game_screen : The game screen instance to switch to.
    """
    def __init__(self, game_screen, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.game_screen = game_screen
        layout = GridLayout(cols=1)

        self.game_type_label = Label(text="Choose Game Type:")
        layout.add_widget(self.game_type_label)

        self.game_type_button_group = BoxLayout(orientation='horizontal',
                                                 size_hint_y=None, height=60)

        self.game_screen_button = Button(text="Local Game")
        self.game_screen_button.bind(on_press=self.switch_to_game_screen)
        self.game_type_button_group.add_widget(self.game_screen_button)

        self.game_screen_connection_button = Button(text="Network Game")
        self.game_screen_connection_button.bind(on_press=self.switch_to_network_game_screen)
        self.game_type_button_group.add_widget(self.game_screen_connection_button)

        layout.add_widget(self.game_type_button_group)
        self.add_widget(layout)

    def switch_to_game_screen(self, instance):
        """Switch to the local game screen."""
        self.game_screen.play_game()
        self.manager.current = 'game'

    def switch_to_network_game_screen(self, instance):
        """Switch to the network game screen."""
        self.manager.current = 'network_game_selection'

class NetworkGameScreenSelection(Screen):
    """Screen for selecting the network game type.
    
    This class is inherited of the kivy Screen class.

    game_screen : The game screen instance to switch to."""

    def __init__(self, game_screen, **kwargs):
        super(NetworkGameScreenSelection, self).__init__(**kwargs)

        self.game_screen = game_screen
        layout = BoxLayout(orientation='horizontal')

        self.host_button = Button(text="Host Game")
        self.host_button.bind(on_press=self.switch_to_host_game)
        layout.add_widget(self.host_button)

        self.connect_button = Button(text="Connect to Game")
        self.connect_button.bind(on_press=self.switch_to_connect_game)
        layout.add_widget(self.connect_button)

        self.add_widget(layout)

    def switch_to_host_game(self, instance):
        """Switch to the network game screen"""
        self.game_screen.host_game("0.0.0.0")
        self.manager.current = 'network_game'

    def switch_to_connect_game(self, instance):
        """Switch to the connect menu game screen"""
        self.manager.current = 'connect_game'

class ConnectScreen(Screen):
    """Screen for selecting the ip to connect.
    
    This class is inherited of the kivy Screen class.

    game_screen : The game screen instance to switch to."""
    def __init__(self, game_screen, **kwargs):
        super(ConnectScreen, self).__init__(**kwargs)
        self.game_screen = game_screen

        layout = BoxLayout(orientation='vertical')

        self.ip_label = Label(text="Enter IP Address:")
        layout.add_widget(self.ip_label)

        self.ip_input = TextInput(multiline=False)
        layout.add_widget(self.ip_input)

        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.connect_to_game)
        layout.add_widget(self.connect_button)

        self.add_widget(layout)

    def connect_to_game(self, instance):
        """Switch to the multiplayer game screen"""
        self.manager.current = 'network_game'
        self.game_screen.connect_to_game(self.ip_input.text)

class GameScreen(Screen, BoardSize8):
    """Screen who we can play the game on local.
    
    This class is inherited of the BoardSize8 class
    """
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.player = 0
        self.turn_pass = 0

        self.layout = GridLayout(cols=8)
        self.add_widget(self.layout)

        self.label_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.player_label = Label(text="")
        self.label_layout.add_widget(self.player_label)
        self.add_widget(self.label_layout)

    @mainthread
    def graphical_board(self):
      """Procedure who display the graphical game board"""
      for row_index, row in enumerate(self.board):
        for column_index, cell in enumerate(row):
            position = (row_index, column_index)
            button = Button(text='', size_hint=(1/8, 1/8))
            setattr(button, 'gridpos', position)
            if cell is not None:
                button.background_color = (0.2, 0.2, 0.2) if cell.get_color() == 0 else (1, 1, 1)
            else:
                button.background_color = (0, 1, 0)
            if position in self.next_possible_move:
                button.background_color = (1, 0, 0, 1)
                button.bind(on_press=self.make_move)
                self.turn_pass = 0
            self.layout.add_widget(button)

    def play_game(self):
        """The logic of the game"""
        self.next_move(self.player)
        if self.turn_pass >= 2:
            self.manager.current = 'end'
        else:
          if len(self.next_possible_move) == 0:
              self.turn_pass += 1
              self.update_layout()
          else:
            str_player = 'black' if self.player == 0 else 'white'
            self.player_label.text = f"{str_player.capitalize()} pawn's turn."
            self.graphical_board()

    def update_layout(self):
        """Procedure who permit the graphical update of the layout"""
        self.layout.clear_widgets()
        self.play_game()

    def make_move(self, button):
        """Procedure call when we click on a button
        
        button : the button on which we click
        """
        cord = button.gridpos
        vector = self.next_possible_move[cord]
        self.place_pawn(self.player, cord, vector)

        self.player = 1 - self.player
        self.update_layout()

class GameScreenConnection(GameScreen, ClientServeur):
    """Screen who we can play the game on local.
    
    This class is inherited of the GameScreen and ClientServeur class
    """
    def __init__(self, **kwargs):
        self.turn = 0
        super().__init__(**kwargs)

    @mainthread
    def graphical_board_no_move(self):
        """Display de game board without the next possible move"""
        for row_index, row in enumerate(self.board):
            for column_index, cell in enumerate(row):
                position = (row_index, column_index)
                button = Button(text='', size_hint=(1/8, 1/8))
                setattr(button, 'gridpos', position)
                if cell is not None:
                    button.background_color = (0.2, 0.2, 0.2
                                               ) if cell.get_color() == 0 else (1, 1, 1)
                else:
                    button.background_color = (0, 1, 0)
                self.layout.add_widget(button)

    def handle_connection(self, client):
        self.client = client
        self.play_game()

    @mainthread
    def play_game(self):
        str_player = 'black' if self.turn == 0 else 'white'
        self.player_label.text = f"{str_player.capitalize()} pawn's turn."

        self.next_move(self.turn)

        if self.turn_pass >= 2:
            self.manager.current = 'end_connection'
        else:
            if self.turn == self.player:
                if len(self.next_possible_move) == 0:
                    self.turn_pass += 1
                    self.turn = 1 - self.turn
                    self.client.send("NO MOVE".encode('utf-8'))
                    self.update_layout()
                else:
                    self.graphical_board()
            else:
                self.graphical_board_no_move()
                Clock.schedule_once(lambda x: threading.Thread(target=self.receive_move).start())

    @mainthread
    def receive_move(self, *args):
        """Procedure who permit to receive the move of the other player with socket"""
        data = self.client.recv(128)

        if not data:
            self.client.close()

        data_decode = data.decode('utf-8')
        if data_decode != 'NO MOVE':
            cord = literal_eval(data_decode)
            #literal_eval is better than eval because it blocks bad intentioned code.
            vector = self.next_possible_move[cord]
            self.place_pawn(self.turn, cord, vector)
            self.turn_pass = 0
        else:
            self.turn_pass += 1
        self.turn = 1 - self.turn

        self.update_layout()

    def make_move(self, button):
        cord = button.gridpos
        vector = self.next_possible_move[cord]
        self.place_pawn(self.turn, cord, vector)

        self.client.send(str(cord).encode('utf-8'))

        self.turn = 1 - self.turn
        self.turn_pass = 0

        self.update_layout()

class EndScreen(Screen):
    """Screen for the end of the game.
    
    This class is inherited of the kivy Screen class.

    game_screen : The game screen instance to switch to."""
    def __init__(self, game_screen, **kwargs):
        super(EndScreen, self).__init__(**kwargs)
        self.game_screen = game_screen

        layout = GridLayout(cols=1)
        self.restart_button = Button(text="Replay")
        self.restart_button.bind(on_press=self.switch_to_new_game)
        layout.add_widget(self.restart_button)
        self.add_widget(layout)

        self.label_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        self.victory_label = Label(text="")
        self.label_layout.add_widget(self.victory_label)
        self.add_widget(self.label_layout)

    def on_pre_enter(self, *args):
        self.victory_label.text = ""

        black, white = self.game_screen.nb_of_pawn_by_color()
        label_str = f"Number of black pawn : {black}\nNumber of white pawn : {white}"
        label_str = "Black wins\n" + label_str if black > white else "White wins\n" + label_str

        self.victory_label.text = label_str

    def switch_to_new_game(self, instance):
        """Switch to a new game screen"""
        self.game_screen.create_new_board()
        self.game_screen.update_layout()
        self.manager.current = 'game'

class EndScreenConnection(EndScreen):
    """Screen for the end of the multiplayer game . 
    
    This class is inherited of the kivy Screen class."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def switch_to_new_game(self, instance):
        self.game_screen.create_new_board()
        self.game_screen.update_layout()
        self.manager.current = 'network_game'

class ReversiApp(App):
    """The kivy App class for loading the game
    
    This class is inherited of the kivy App class
    """
    def build(self):
        sm = ScreenManager()

        game_screen = GameScreen(name='game')
        start_screen = StartScreen(name='start', game_screen=game_screen)

        game_screen_connection = GameScreenConnection(name='network_game')
        network_game_screen_selection = NetworkGameScreenSelection(
            name='network_game_selection', game_screen=game_screen_connection)

        connect_game = ConnectScreen(name="connect_game", game_screen=game_screen_connection)

        end_screen = EndScreen(name='end', game_screen=game_screen)
        end_screen_connection = EndScreenConnection(name='end_connection',
                                                    game_screen=game_screen_connection)

        sm.add_widget(start_screen)
        sm.add_widget(network_game_screen_selection)
        sm.add_widget(connect_game)
        sm.add_widget(game_screen)
        sm.add_widget(end_screen)
        sm.add_widget(game_screen_connection)
        sm.add_widget(end_screen_connection)

        return sm

if __name__ == '__main__':
    ReversiApp().run()
