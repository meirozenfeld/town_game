import random
import time
from collections import Counter

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import socketio

from kivy.uix.togglebutton import ToggleButton

sio = socketio.Client()
UPDATE_DELAY = 1.0

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)

        # Set the background image
        with self.canvas.before:
            # Replace 'background_image.png' with the path to your image file
            Rectangle(pos=(0,0), size=Window.size, source='wolf.jpg')

        # Check if the screen is one of the screens where the button should appear
        if self.name not in ['main_screen', 'role_screen', 'settings_screen', 'end_dead_screen']:
            # Create a small square-shaped button
            info_button = Button(
                text=app.reverse_text("תפקיד"),  # Unicode character for information symbol
                size_hint=(None, None),
                size=(100, 50),  # Adjust size as needed
                pos=(10, Window.height - 60),  # Adjust position as needed
                background_color=(0, 0.5, 1, 1),  # Adjust color as needed
                font_name='Arial'
            )
            info_button.bind(on_press=self.show_information_popup)

            # Add the button to the screen
            self.add_widget(info_button)

    def show_information_popup(self, instance):
        # Create and configure the pop-up
        role = app.player_names_roles.get(app.current_name, {}).get('role')
        print("Role var:  ", role)
        if role == app.reverse_text('זאב מנהיג הלהקה'):
            popup = RolePopUp(message=app.reverse_text("הסבר זאב מנהיג להקה"))
            popup.open()
            # content = Label(text=app.reverse_text("הסבר זאב מנהיג להקה"), font_name='Arial')
        if role == app.reverse_text('זאב'):
            popup = RolePopUp(message=app.reverse_text("הסבר זאב"))
            popup.open()
        if role == app.reverse_text('זקן השבט'):
            popup = RolePopUp(message=app.reverse_text("הסבר זקן השבט"))
            popup.open()
        if role == app.reverse_text('מגן'):
            popup = RolePopUp(message=app.reverse_text("הסבר מגן"))
            popup.open()
        if role == app.reverse_text('מכשפה'):
            popup = RolePopUp(message=app.reverse_text("הסבר מכשפה"))
            popup.open()
        if role == app.reverse_text('מגדת עתידות'):
            popup = RolePopUp(message=app.reverse_text("הסבר מגדת עתידות"))
            popup.open()
        if role == app.reverse_text('קופידון'):
            popup = RolePopUp(message=app.reverse_text('הסבר קופידון'))
            popup.open()
        if role == app.reverse_text('עלוקה'):
            popup = RolePopUp(message=app.reverse_text('הסבר עלוקה'))
            popup.open()
        if role == app.reverse_text('אזרח פשוט'):
            popup = RolePopUp(message=app.reverse_text('הסבר אזרח פשוט'))
            popup.open()


class RolePopUp(Popup):
    def __init__(self, message, **kwargs):
        super(RolePopUp, self).__init__(**kwargs)
        self.title_font = 'Arial'
        self.title = 'Role'

        # Create a Label widget with the specified font
        label = Label(text=message, font_name='Arial', font_size=16)

        # Create a Button widget to close the Popup
        close_button = Button(text=app.reverse_text('סגור'), on_press=self.dismiss, font_name='Arial')

        # Add the Label and Button to the Popup content
        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(label)
        self.content.add_widget(close_button)

# Create a layout for the main screen
class MainScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Create a layout for the main screen
        layout = BoxLayout(orientation='vertical', padding=10)

        # Create a text input for player name
        self.text_input = TextInput(multiline=False, hint_text=app.reverse_text('הכנס את שמך'), size_hint_y=None, height=50,
                                    font_name='Arial',size_hint=(0.5, None),pos_hint={'center_x': 0.5})
        layout.add_widget(self.text_input)

        # Create an "Enter" button to submit the name
        enter_button = Button(text=app.reverse_text('הצטרף'), size_hint=(None, None), size=(200, 80), pos_hint={'center_x': 0.5}, background_color=(0, 0.7, 0, 1),font_name= 'Arial')
        enter_button.bind(on_press=self.handle_ok_button)
        layout.add_widget(enter_button)

        # Create a "Game Settings" button (initially disabled)
        self.game_settings_button = Button(text=app.reverse_text('הגדרות המשחק'), size_hint=(None, None), size=(200, 80), disabled=True,
                                           pos_hint={'center_x': 0.5}, background_color=(128 / 255, 128 / 255, 128 / 255, 1), font_name='Arial')
        self.game_settings_button.bind(on_press=self.handle_game_settings_button)
        layout.add_widget(self.game_settings_button)
        # widget = Widget()
        # layout.add_widget(widget)
        # Create a ScrollView to enable scrolling
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_x=0.8, pos_hint={'center_x': 0.5})
        self.names_label = Label(text='', font_size=45, font_name='Arial', size_hint_y=None,
                                 height=dp(300),color=(0, 0.8, 0, 1))  # Adjust the height as needed

        scroll_view.add_widget(self.names_label)
        layout.add_widget(scroll_view)

        # Create a "Start Game" button (initially disabled)
        self.start_game_button = Button(text=app.reverse_text('התחל משחק'), size_hint=(None, None), size=(200, 80), disabled=True,
                                        pos_hint={'center_x': 0.5}, background_color=(0, 0.7, 0, 1), font_name='Arial')
        self.start_game_button.bind(on_press=self.handle_start_game_button)
        layout.add_widget(self.start_game_button)
        self.add_widget(layout)
        # Flag to track if the current player is the first player
        self.is_first_player = False

        # Set the layout as the content of the screen


    def handle_ok_button(self, instance):
        name = app.reverse_text(self.text_input.text)
        if name:
            sio.emit('submit_name', {'name': name})

    def handle_game_settings_button(self, instance):
        # Add logic to handle the "Game Settings" button press
        if self.is_first_player:
            # Only the first player can access the game settings
            print("Opening game settings...")
            app.screen_manager.current = 'settings_screen'

        else:
            print("You are not the first player, cannot access game settings.")

    def enable_game_settings_button(self):
        # Enable the "Game Settings" button only for the first player
        self.game_settings_button.disabled = not self.is_first_player

    def handle_start_game_button(self, instance):
        if self.is_first_player:
            # Only the first player can start the game
            print("Starting the game...")
            sio.emit('start_game')  # Emit the 'start_game' event to the server


# New Screen for Game Settings
class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        # Create a layout for the settings screen
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # # Add a label for the title "Settings"
        title_label = Label(text=app.reverse_text('הגדרות'), font_size=dp(50), font_name='Arial', color=(0, 0.7, 0, 1), bold=True, pos_hint = {'center_y':2})
        layout.add_widget(title_label)

        # Add a label and text input for "Number of Wolves"
        wolfs_layout = BoxLayout(orientation="horizontal", pos_hint={'center_x': 0.5}, size_hint=(0.7, None), height=40,
                                padding=1, spacing=1)
        self.number_of_wolves = 1

        plus_button =Button(text='+', on_press=self.increment_wolves,background_color=(0, 1, 0, 1))

        self.number_of_wolves_label = Label(text=str(self.number_of_wolves), font_name='Arial')

        minus_button =Button(text='-', on_press=self.decrement_wolves, background_color=(1, 0, 0, 1))

        wolves_label = Label(text=app.reverse_text('מספר הזאבים:'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)

        wolfs_layout.add_widget(plus_button)
        wolfs_layout.add_widget(self.number_of_wolves_label)
        wolfs_layout.add_widget(minus_button)
        wolfs_layout.add_widget(wolves_label)
        layout.add_widget(wolfs_layout)

        # Add a label, toggle button, and corresponding variable for "old"
        old_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.old_button = ToggleButton(text=app.reverse_text('כן'), group='old_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_old)
        self.old_flag = True  # Variable to store leech status
        old_label = Label(text=app.reverse_text('זקן השבט?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        old_layout.add_widget(self.old_button)
        old_layout.add_widget(old_label)
        layout.add_widget(old_layout)


        # Add a label, toggle button, and corresponding variable for "shield"
        shield_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.shield_button = ToggleButton(text=app.reverse_text('כן'), group='shield_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_shield)
        self.shield_flag = True  # Variable to store leech status
        shield_label = Label(text=app.reverse_text('מגן?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        shield_layout.add_widget(self.shield_button)
        shield_layout.add_widget(shield_label)
        layout.add_widget(shield_layout)

        # Add a label, toggle button, and corresponding variable for "seer"
        seer_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.seer_button = ToggleButton(text=app.reverse_text('כן'), group='seer_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_seer)
        self.seer_flag = True  # Variable to store leech status
        seer_label = Label(text=app.reverse_text('מגדת עתידות?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        seer_layout.add_widget(self.seer_button)
        seer_layout.add_widget(seer_label)
        layout.add_widget(seer_layout)

        # Add a label, toggle button, and corresponding variable for "witch"
        witch_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.witch_button = ToggleButton(text=app.reverse_text('כן'), group='witch_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_witch)
        self.witch_flag = True  # Variable to store leech status
        witch_label = Label(text=app.reverse_text('מכשפה?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        witch_layout.add_widget(self.witch_button)
        witch_layout.add_widget(witch_label)
        layout.add_widget(witch_layout)

        # Add a label, toggle button, and corresponding variable for "hunter"
        hunter_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.hunter_button = ToggleButton(text=app.reverse_text('כן'), group='hunter_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_hunter)
        self.hunter_flag = True  # Variable to store leech status
        hunter_label = Label(text=app.reverse_text('צייד?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        hunter_layout.add_widget(self.hunter_button)
        hunter_layout.add_widget(hunter_label)
        layout.add_widget(hunter_layout)

        # Add a label, toggle button, and corresponding variable for "cupid"
        cupid_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.cupid_button = ToggleButton(text=app.reverse_text('כן'), group='cupid_toggle', font_name='Arial', background_color=(0, 1, 0, 1), on_press=self.toggle_cupid)
        self.cupid_flag = True  # Variable to store leech status
        cupid_label = Label(text=app.reverse_text('קופידון?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        cupid_layout.add_widget(self.cupid_button)
        cupid_layout.add_widget(cupid_label)
        layout.add_widget(cupid_layout)

        # Add a label, toggle button, and corresponding variable for "Leech"
        leech_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.leech_button = ToggleButton(text=app.reverse_text('לא'), group='leech_toggle', font_name='Arial', background_color=(1, 0, 0, 1), on_press=self.toggle_leech)
        self.leech_flag = False  # Variable to store leech status
        leech_label = Label(text=app.reverse_text('עלוקה?'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        leech_layout.add_widget(self.leech_button)
        leech_layout.add_widget(leech_label)
        layout.add_widget(leech_layout)

        # Add a label and text input for "Discussion Time"
        time_layout = BoxLayout(orientation='horizontal', pos_hint={'center_x': 0.5}, size_hint=(0.5, None), height=40,
                                padding=1, spacing=1)
        self.discussion_time = 1
        self.discussion_time_label = Label(text=str(self.discussion_time), font_name='Arial')
        time_layout.add_widget(
            Button(text='+', on_press=self.increment_time, font_name='Arial', background_color=(0, 1, 0, 1)))
        time_layout.add_widget(self.discussion_time_label)
        time_layout.add_widget(
            Button(text='-', on_press=self.decrement_time, font_name='Arial', background_color=(1, 0, 0, 1)))
        discussion_label = Label(text=app.reverse_text('זמן דיונים:'), font_name='Arial', color=(1, 1, 0, 1), font_size=30)
        time_layout.add_widget(discussion_label)
        layout.add_widget(time_layout)

        # Add a button to confirm and save data
        confirm_button = Button(text=app.reverse_text('אישור'), on_press=self.confirm_settings, size_hint=(0.3, None),
                                pos_hint={'center_x': 0.5}, font_name='Arial', background_color=(0, 1, 0, 1))
        layout.add_widget(confirm_button)

        # Add a button to go back without saving
        back_button = Button(text=app.reverse_text('חזור'), on_press=self.go_back, size_hint=(0.3, None),
                             pos_hint={'center_x': 0.5}, font_name='Arial')
        layout.add_widget(back_button)

        # Set the layout as the content of the screen
        self.add_widget(layout)

    def increment_wolves(self, instance):
        if self.number_of_wolves < len(app.player_names)-2:
            self.number_of_wolves += 1
            self.number_of_wolves_label.text = str(self.number_of_wolves)

    def decrement_wolves(self, instance):
        if self.number_of_wolves > 1:
            self.number_of_wolves -= 1
            self.number_of_wolves_label.text = str(self.number_of_wolves)

    def increment_time(self, instance):
        self.discussion_time += 1
        self.discussion_time_label.text = str(self.discussion_time)

    def decrement_time(self, instance):
        if self.discussion_time > 1:
            self.discussion_time -= 1
            self.discussion_time_label.text = str(self.discussion_time)

    def toggle_old(self, instance):
        # Toggle the old status and update the button text
        self.old_flag = not self.old_flag
        instance.text = 'ןכ' if self.old_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.old_flag else (1, 0, 0, 1)


    def toggle_shield(self, instance):
        # Toggle the shield status and update the button text
        self.shield_flag = not self.shield_flag
        instance.text = 'ןכ' if self.shield_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.shield_flag else (1, 0, 0, 1)

    def toggle_seer(self, instance):
        # Toggle the seer status and update the button text
        self.seer_flag = not self.seer_flag
        instance.text = 'ןכ' if self.seer_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.seer_flag else (1, 0, 0, 1)

    def toggle_witch(self, instance):
        # Toggle the 'witch' status and update the button text
        self.witch_flag = not self.witch_flag
        instance.text = 'ןכ' if self.witch_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.witch_flag else (1, 0, 0, 1)

    def toggle_hunter(self, instance):
        # Toggle the hunter status and update the button text
        self.hunter_flag = not self.hunter_flag
        instance.text = 'ןכ' if self.hunter_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.hunter_flag else (1, 0, 0, 1)

    def toggle_cupid(self, instance):
        # Toggle the cupid status and update the button text
        self.cupid_flag = not self.cupid_flag
        instance.text = 'ןכ' if self.cupid_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.cupid_flag else (1, 0, 0, 1)

    def toggle_leech(self, instance):
        # Toggle the leech status and update the button text
        self.leech_flag = not self.leech_flag
        instance.text = 'ןכ' if self.leech_flag else 'אל'
        instance.background_color = (0, 1, 0, 1) if self.leech_flag else (1, 0, 0, 1)



    def confirm_settings(self, instance):
        # Save data and go back to the main screen
        app.number_of_wolves = int(self.number_of_wolves)
        app.old_flag = self.old_flag
        app.witch_flag = self.witch_flag
        app.shield_flag = self.shield_flag
        app.seer_flag = self.seer_flag
        app.hunter_flag = self.hunter_flag
        app.cupid_flag = self.cupid_flag
        app.leech_flag = self.leech_flag
        app.discussion_time = int(self.discussion_time)
        print( f"Confirm:  Wolves: {app.number_of_wolves }\n leech: {app.leech_flag}\n time: {app.discussion_time}\n witch_flag: {app.witch_flag}\n shield_flag: {app.shield_flag},\n hunter_flag: {app.hunter_flag}")

        app.screen_manager.current = 'main_screen'

    def go_back(self, instance):
        # Go back to the main screen without saving data
        print( f"Back: Wolves: {app.number_of_wolves }\n leech: {app.leech_flag}\n time: {app.discussion_time}\n witch_flag: {app.witch_flag}\n shield_flag: {app.shield_flag}")
        # print("Age of Alice:", app.player_names_roles[app.player_names[0]])
        app.screen_manager.current = 'main_screen'


class RoleScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(RoleScreen, self).__init__(**kwargs)
        # layout = BoxLayout(orientation='vertical')
        # layout.add_widget(Label(text='Game Screen'))
        # self.add_widget(layout)
        self.selected_lover = ''
        self.vote_buttons = []
        self.previous_button = None  # Keep track of the previously pressed button
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def on_enter(self, *args):

        # self.ready_button_cupid = ToggleButton(
        #     text=app.reverse_text("מצב: לא מוכן"),
        #     on_press=self.toggle_ready,
        #     background_color=[1, 0, 0, 1],
        #     disabled=True,  # Initially disable the button
        #     font_name='Arial'
        # )
        # main_screen = self.screen_manager.get_screen('main_screen')
        if app.is_first_player:
            self.init_roles()
            self.select_roles_to_players()
        for name, role in app.player_names_roles.items():
            print(f"name: {name} role:  {role['role']}")
        self.handle_roles_page()

    def select_roles_to_players(self):
        app.general = {
            'time': app.discussion_time,
            'manager': '',
            'wolf_final_choice': '',
            'town_final_choice': '',
            'shield_defender': '',
            'mayor': '',
            'is_mayor': False,
            'old_is_alive': True,
            'first_player_finished': False,
            'continue_time': False,
            'who_is_win': '',
            'selected_dead': False,
            'hunterEnd': True,
            'hunterVote': ''
        }
        sio.emit('update_general', {'general': app.general})
        random.shuffle(app.roles)
        wolf_number = 2
        for i, player in enumerate(app.player_names):

            if app.reverse_text('מנהיג הלהקה') in app.roles[i]:
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': False,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,

                    'wolf_choice': '',
                    'town_votes': "",
                    'mayor_votes': "",
                    'wolf_number': 1
                }

            elif app.roles[i] == app.reverse_text('זאב'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 2,
                    'ready_role': False,
                    'ready_night': False,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'wolf_choice': '',
                    'town_votes': "",
                    'mayor_votes': "",
                    'wolf_number': wolf_number
                }
                wolf_number += 1

            elif app.roles[i] == app.reverse_text('זקן השבט'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 2,
                    'ready_role': False,
                    'ready_night': True,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                }

            elif app.roles[i] == app.reverse_text('מגדת עתידות'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': False,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                }

            elif app.roles[i] == app.reverse_text('מכשפה'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': False,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                    'live_poison': "",
                    'live_poison_flag': True,
                    'dead_poison': "",
                    'dead_poison_flag': True,
                    'old_is_alive': True
                }

            elif app.roles[i] == app.reverse_text('מגן'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': False,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'pre_defender': '',
                    'defense_on': '',
                    'town_votes': "",
                    'mayor_votes': "",
                    'shield_defender': False,
                    'old_is_alive': True
                }

            elif app.roles[i] == app.reverse_text('צייד'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': True,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                    'live_poison': True,
                    'dead_poison': True,
                    'old_is_alive': True
                }
                app.general['hunterEnd'] = False
                sio.emit('update_general', {'general': app.general})

            elif app.roles[i] == app.reverse_text('קופידון'):
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': True,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                    'lover': '',
                    'first_night': True
                }

            else:
                app.player_names_roles[player] = {
                    'role': app.roles[i],
                    'is_alive': 1,
                    'ready_role': False,
                    'ready_night': True,
                    'ready_morning': False,
                    'ready_mayor': False,
                    'ready_mayor2': False,
                    'ready_election': False,
                    'ready_election2': False,
                    'town_votes': "",
                    'mayor_votes': "",
                }

        # Iterating over the names and ages
        sio.emit('update_roles', {'roles': app.player_names_roles})
        for name, role in app.player_names_roles.items():
            print(f"name: {name} role:  {role['role']}")


    def init_roles(self):
        len_players = len(app.player_names)
        len_wolf = app.number_of_wolves
        print("len_players: ", len_players)
        print("len_wolf: ", len_wolf)

        print("in init")
        while len_players != 0:
            while len_wolf != 0:
                if len_wolf == app.number_of_wolves:
                    app.roles.append(app.reverse_text('זאב מנהיג הלהקה'))
                    len_wolf = len_wolf - 1
                    len_players = len_players - 1
                else:
                    app.roles.append(app.reverse_text('זאב'))
                    len_players = len_players - 1
                    len_wolf = len_wolf - 1

            if len_players != 0 and app.old_flag:
                app.roles.append(app.reverse_text('זקן השבט'))
                len_players = len_players - 1

            if len_players != 0 and app.shield_flag:
                app.roles.append(app.reverse_text('מגן'))
                len_players = len_players - 1

            if len_players != 0 and app.witch_flag:
                app.roles.append(app.reverse_text('מכשפה'))
                len_players = len_players - 1

            if len_players != 0 and app.seer_flag:

                app.roles.append(app.reverse_text('מגדת עתידות'))
                len_players = len_players - 1

            if len_players != 0 and app.hunter_flag:
                app.roles.append(app.reverse_text('צייד'))
                len_players = len_players - 1

            if len_players != 0 and app.cupid_flag:
                app.roles.append(app.reverse_text('קופידון'))
                len_players = len_players - 1

            if len_players != 0 and app.leech_flag:

                app.roles.append(app.reverse_text('עלוקה'))
                len_players = len_players - 1

            while len_players != 0:
                app.roles.append(app.reverse_text('אזרח פשוט'))
                len_players = len_players - 1

        print("ROLES : ",app.roles)

    def handle_roles_page(self):
        print("Updated roles:", app.player_names_roles)
        role = app.player_names_roles.get(app.current_name, {}).get('role')
        print("Role var:  ", role)
        if role == app.reverse_text('זאב מנהיג הלהקה'):
            self.main_wolf_screen()
        if role == app.reverse_text('זאב'):
            self.wolf_screen()
        if role == app.reverse_text('זקן השבט'):
            self.old_screen()
        if role == app.reverse_text('מגן'):
            self.shield_screen()
        if role == app.reverse_text('מכשפה'):
            self.witch_screen()
        if role == app.reverse_text('מגדת עתידות'):
            self.magedet_screen()
        if role == app.reverse_text('צייד'):
            self.hunter_screen()
        if role == app.reverse_text('קופידון'):
            self.copidon_screen()
        if role == app.reverse_text('עלוקה'):
            self.leech_screen()
        if role == app.reverse_text('אזרח פשוט'):
            self.simple_screen()

    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_role', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            print("All players are ready!")
            # Do something when all players are ready
            # if app.player_names_roles[app.current_name]['role'] == app.reverse_text('קופידון'):

            Clock.unschedule(self.check_readiness)  # Stop the scheduled check
            app.screen_manager.current = 'night_screen'


    def main_wolf_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='main_wolf_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("main wolf screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def wolf_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='wolf_screen '+str(app.player_names_roles[app.current_name]['wolf_number'])))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("wolf screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def old_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='old_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("old screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def shield_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='shield_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("shield screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def witch_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='witch_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("witch screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def magedet_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='magedet_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("magedet screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def hunter_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='hunter_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("hunter screen")
        Clock.schedule_interval(self.check_readiness, 1)

    def copidon_screen(self):
        # if self.ready_button_cupid.parent:
        #     self.remove_widget(self.ready_button_cupid)
        self.ready_button_cupid = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            disabled=True,  # Initially disable the button
            font_name='Arial'
        )
        cupid_layout = BoxLayout(orientation='vertical')
        votes_label1 = Label(text=app.reverse_text("בחר נאהב:"), font_size=35, font_name='Arial')
        cupid_layout.add_widget(votes_label1)

        def on_vote_button_press(button):
            self.selected_lover = button.text

            # Reset color of the previous button
            if self.previous_button != None:
                if self.previous_button.text != self.selected_lover:
                    self.previous_button.background_color = [0.5, 0, 0, 1]  # Reset to default

            # Change the color of the current button to red
            button.background_color = [0, 0.5, 0, 1]  # Red color in RGBA format

            # Update the previous_button to the current button
            self.previous_button = button
            print(f"Lover : {self.selected_lover}")
            # Assuming you have a 'defense_on' attribute in app.player_names_roles[app.current_name]
            app.player_names_roles[app.current_name]['lover'] = self.selected_lover
            # Emit 'update_roles' instead of 'ready_updated'
            sio.emit('update_wolf', {'wolf': app.player_names_roles})
            # Enable the ready_button when a vote is selected
            self.ready_button_cupid.disabled = False

        for player, info in app.player_names_roles.items():
            is_alive_value = info.get('is_alive', '')
            if is_alive_value > 0 and player != app.current_name:
                vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0.5, 0, 0, 1])
                # Set the on_press callback for the button
                vote_label.bind(on_press=on_vote_button_press)
                self.vote_buttons.append(vote_label)
                cupid_layout.add_widget(vote_label)

        cupid_layout.add_widget(self.ready_button_cupid)
        self.add_widget(cupid_layout)
        app.player_names_roles[app.current_name]['ready_role'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

        print("After ready update for role screen: ", app.player_names_roles)
        Clock.schedule_interval(self.check_readiness, 1)

        print("copidon screen")

    def leech_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='leech_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color = [1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        Clock.schedule_interval(self.check_readiness, 1)

        print("leech screen")

    def simple_screen(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='simple_screen'))

        self.ready_button = ToggleButton(text=app.reverse_text("מצב: לא מוכן"), on_press=self.toggle_ready, background_color=[1, 0, 0, 1], font_name='Arial')
        layout.add_widget(self.ready_button)
        self.add_widget(layout)
        print("simple screen")
        Clock.schedule_interval(self.check_readiness, 1)

        print("wrong#####################")

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            if self.vote_buttons:
                for b in self.vote_buttons:
                    b.disabled = False
            app.player_names_roles[app.current_name]['ready_role'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            if self.vote_buttons:
                for b in self.vote_buttons:
                    b.disabled = True
            app.player_names_roles[app.current_name]['ready_role'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

class NightScreen(BaseScreen):
    first_night_popup_shown = False  # Class variable to track if the popup has been shown

    def __init__(self, **kwargs):
        super(NightScreen, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()
    def change_to_minus1(self):
        for player, info in app.player_names_roles.items():
            if app.player_names_roles[player]['is_alive'] == 0:
                app.player_names_roles[player]['is_alive'] = -1
        sio.emit('update_wolf', {'wolf': app.player_names_roles})
    def on_enter(self, *args):
        self.clear_widgets()  # Clear existing widgets from the screen

        # time.sleep(1)
        self.change_to_minus1()
        self.selected_votes_wolf = ''
        self.selected_defender = ''
        self.selected_lover = ''
        self.selected_dead_poison = ''
        self.previous_button = None  # Keep track of the previously pressed button
        self.vote_buttons = []
        app.player_names_roles[app.current_name]['ready_morning'] = False
        self.ready_button = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            disabled=True,  # Initially disable the button
            font_name='Arial'
        )
        self.handle_night_screen()
        # Show popup for lover
        # Show popup for lover only on the first night
        if not NightScreen.first_night_popup_shown:
            matching_keys = [key for key, value in app.player_names_roles.items() if value.get('role') == app.reverse_text('קופידון')]
            if matching_keys:
                if app.current_name == app.player_names_roles[matching_keys[0]]['lover']:
                    popup = PopUp(message=app.reverse_text('בחר בך כנאהב') + " " + matching_keys[0] + " " + app.reverse_text("הקופידון"))
                    popup.open()
                    NightScreen.first_night_popup_shown = True

    def handle_night_screen(self):
        role = app.player_names_roles.get(app.current_name, {}).get('role')
        print("Role var:  ", role)

        if role == app.reverse_text('זאב מנהיג הלהקה'):
            # app.player_names_roles[app.current_name]['ready'] = False
            # sio.emit('update_ready', {'ready': app.player_names_roles})
            wolf_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב זאב מנהיג הלהקה!"), font_size=50, font_name='Arial')
            header_label2 = Label(text=app.reverse_text("הזאבים שאיתך:"), font_size=35, font_name='Arial')
            wolf_layout.add_widget(header_label1)
            wolf_layout.add_widget(header_label2)
            flag_is_wolf = False
            # Iterate through player names and roles
            for player, info in app.player_names_roles.items():
                role_value = info.get('role', '')
                is_alive_value = info.get('is_alive', '')
                # Check if the role is "זאב"
                if role_value == app.reverse_text('זאב') and is_alive_value > 0:
                    # Create a label for the player
                    player_label = Label(text=player, font_size=30, font_name='Arial')
                    wolf_layout.add_widget(player_label)
                    flag_is_wolf = True
            if not flag_is_wolf:
                flag_label = Label(text=app.reverse_text('אין איתך זאבים'), font_size=30, font_name='Arial')
                wolf_layout.add_widget(flag_label)

            votes_label1 = Label(text=app.reverse_text("סמן באדום את מי שתרצה לטרוף הלילה:"), font_size=35, font_name='Arial')
            wolf_layout.add_widget(votes_label1)


            def on_vote_button_press(button):
                self.selected_votes_wolf = button.text

                # Reset color of the previous button
                if self.previous_button != None:
                    if self.previous_button.text != self.selected_votes_wolf:
                        self.previous_button.background_color = [0, 0.5, 0, 1]  # Reset to default

                # Change the color of the current button to red
                button.background_color = [0.5, 0, 0, 1]  # Red color in RGBA format

                # Update the previous_button to the current button
                self.previous_button = button
                print(f"Vote for: {self.selected_votes_wolf}")
                # Assuming you have a 'wolf_choice' attribute in app.player_names_roles[app.current_name]
                app.player_names_roles[app.current_name]['wolf_choice'] = self.selected_votes_wolf
                # Emit 'update_roles' instead of 'ready_updated'
                sio.emit('update_wolf', {'wolf': app.player_names_roles})
                # Enable the ready_button when a vote is selected
                self.ready_button.disabled = False

            for player, info in app.player_names_roles.items():
                role_value = info.get('role', '')
                is_alive_value = info.get('is_alive', '')
                if player != app.current_name  and is_alive_value > 0:
                    vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0, 0.5, 0, 1])
                    # Set the on_press callback for the button
                    vote_label.bind(on_press=on_vote_button_press)
                    self.vote_buttons.append(vote_label)
                    wolf_layout.add_widget(vote_label)

            wolf_layout.add_widget(self.ready_button)

            self.add_widget(wolf_layout)

            app.player_names_roles[app.current_name]['ready_night'] = False
            # sio.emit('update_ready', {'ready': app.player_names_roles})
            self.send_update_to_server(dt=UPDATE_DELAY)
            print("After ready update for night screen: ", app.player_names_roles)


            Clock.schedule_interval(self.check_readiness, 1)


        if role == app.reverse_text('זאב'):
            # app.player_names_roles[app.current_name]['ready_night'] = False
            # sio.emit('update_ready', {'ready': app.player_names_roles})
            wolf_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב זאב!"), font_size=50, font_name='Arial')
            header_label2 = Label(text=app.reverse_text("הזאבים שאיתך:"), font_size=35, font_name='Arial')
            wolf_layout.add_widget(header_label1)
            wolf_layout.add_widget(header_label2)
            flag_is_wolf = False
            # Iterate through player names and roles
            for player, info in app.player_names_roles.items():
                role_value = info.get('role', '')
                is_alive_value = info.get('is_alive', '')
                # Check if the role is "זאב"
                if player != app.current_name and app.reverse_text('זאב') in role_value and is_alive_value > 0:
                    # Create a label for the player
                    player_label = Label(text=player, font_size=30, font_name='Arial')
                    wolf_layout.add_widget(player_label)
                    flag_is_wolf = True
            if not flag_is_wolf:
                flag_label = Label(text=app.reverse_text('אין איתך זאבים'), font_size=30, font_name='Arial')
                wolf_layout.add_widget(flag_label)

            votes_label1 = Label(text=app.reverse_text("סמן באדום את מי שתרצה לטרוף הלילה:"), font_size=35, font_name='Arial')
            wolf_layout.add_widget(votes_label1)


            def on_vote_button_press(button):
                self.selected_votes_wolf = button.text

                # Reset color of the previous button
                if self.previous_button != None:
                    if self.previous_button.text != self.selected_votes_wolf:
                        self.previous_button.background_color = [0, 0.5, 0, 1]  # Reset to default

                # Change the color of the current button to red
                button.background_color = [0.5, 0, 0, 1]  # Red color in RGBA format

                # Update the previous_button to the current button
                self.previous_button = button
                print(f"Vote for: {self.selected_votes_wolf}")
                # Assuming you have a 'wolf_choice' attribute in app.player_names_roles[app.current_name]
                app.player_names_roles[app.current_name]['wolf_choice'] = self.selected_votes_wolf
                # Emit 'update_roles' instead of 'ready_updated'
                sio.emit('update_wolf', {'wolf': app.player_names_roles})
                # Enable the ready_button when a vote is selected
                self.ready_button.disabled = False

            for player, info in app.player_names_roles.items():
                role_value = info.get('role', '')
                is_alive_value = info.get('is_alive', '')
                if player != app.current_name and is_alive_value > 0:
                    vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0, 0.5, 0, 1])
                    # Set the on_press callback for the button
                    vote_label.bind(on_press=on_vote_button_press)
                    self.vote_buttons.append(vote_label)
                    wolf_layout.add_widget(vote_label)

            wolf_layout.add_widget(self.ready_button)

            self.add_widget(wolf_layout)

            app.player_names_roles[app.current_name]['ready_night'] = False
            # sio.emit('update_ready', {'ready': app.player_names_roles})
            self.send_update_to_server(dt=UPDATE_DELAY)

            print("After ready update for night screen: ", app.player_names_roles)


            Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('זקן השבט'):
            #לשים קצת דברים מעניינים פה
            old_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב זקן השבט!"), font_size=50, font_name='Arial')
            old_layout.add_widget(header_label1)

            self.add_widget(old_layout)
            app.player_names_roles[app.current_name]['ready_night'] = True
            sio.emit('update_ready', {'ready': app.player_names_roles})
            print("After ready update for night screen: ", app.player_names_roles)
            Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('מגן'):

            if app.general['old_is_alive']:
                # app.player_names_roles[app.current_name]['ready'] = False
                # sio.emit('update_ready', {'ready': app.player_names_roles})
                shield_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מגן!"), font_size=50, font_name='Arial')
                shield_layout.add_widget(header_label1)
                votes_label1 = Label(text=app.reverse_text("סמן בירוק את מי שתרצה להגן עליו בלילה: ") + "\n" + app.reverse_text(" לא יכול פעמיים ברצף על עצמך"), font_size=35, font_name='Arial')
                shield_layout.add_widget(votes_label1)

                def on_vote_button_press(button):
                    self.selected_defender = button.text

                    # Reset color of the previous button
                    if self.previous_button != None:
                        if self.previous_button.text != self.selected_defender:
                            self.previous_button.background_color = [0.5, 0, 0, 1]  # Reset to default

                    # Change the color of the current button to red
                    button.background_color = [0, 0.5, 0, 1] # Red color in RGBA format

                    # Update the previous_button to the current button
                    self.previous_button = button
                    print(f"Defense on : {self.selected_defender}")
                    # Assuming you have a 'defense_on' attribute in app.player_names_roles[app.current_name]
                    app.player_names_roles[app.current_name]['defense_on'] = self.selected_defender
                    app.player_names_roles[app.current_name]['pre_defender'] = self.selected_defender
                    # Emit 'update_roles' instead of 'ready_updated'
                    sio.emit('update_wolf', {'wolf': app.player_names_roles})
                    # Enable the ready_button when a vote is selected
                    self.ready_button.disabled = False

                for player, info in app.player_names_roles.items():
                    is_alive_value = info.get('is_alive', '')
                    if is_alive_value > 0:
                        if player == app.player_names_roles[app.current_name]['pre_defender']:
                            vote_label = Button(text=player, font_size=30, font_name='Arial',
                                                background_color=[0.5, 0, 0, 1], disabled=True)
                        else:
                            vote_label = Button(text=player, font_size=30, font_name='Arial',
                                                background_color=[0.5, 0, 0, 1])

                        # Set the on_press callback for the button
                        vote_label.bind(on_press=on_vote_button_press)
                        self.vote_buttons.append(vote_label)
                        shield_layout.add_widget(vote_label)

                shield_layout.add_widget(self.ready_button)

                self.add_widget(shield_layout)
                app.player_names_roles[app.current_name]['ready_night'] = False
                # sio.emit('update_ready', {'ready': app.player_names_roles})
                self.send_update_to_server(dt=UPDATE_DELAY)

                print("After ready update for night screen: ", app.player_names_roles)
                Clock.schedule_interval(self.check_readiness, 1)
                # Clock.schedule_once(self.update_after_shield_layout_added, 1)
            else:
                # לשים קצת דברים מעניינים פה
                shield_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מגן!"), font_size=50, font_name='Arial')
                shield_layout.add_widget(header_label1)
                self.add_widget(shield_layout)
                app.player_names_roles[app.current_name]['ready_night'] = True
                sio.emit('update_ready', {'ready': app.player_names_roles})
                print("After ready update for night screen: ", app.player_names_roles)
                Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('מכשפה'):

            if app.general['old_is_alive']:
                time.sleep(1.2)
                # app.player_names_roles[app.current_name]['ready'] = False
                # sio.emit('update_ready', {'ready': app.player_names_roles})
                witch_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מכשפה!"), font_size=50, font_name='Arial')
                witch_layout.add_widget(header_label1)
                live_layout =BoxLayout(orientation='horizontal')
                live_poison = app.player_names_roles[app.current_name]['live_poison']
                dead_poison = app.player_names_roles[app.current_name]['dead_poison']
                live_poison_flag = app.player_names_roles[app.current_name]['live_poison_flag']
                dead_poison_flag = app.player_names_roles[app.current_name]['dead_poison_flag']
                print("live_poison ", live_poison)
                print("dead_poison ", dead_poison)

                if live_poison_flag or dead_poison_flag:
                    if dead_poison_flag:

                        votes_label2 = Label(text=app.reverse_text("האם תרצי לתת שיקוי מוות?"), font_size=35, font_name='Arial')
                        witch_layout.add_widget(votes_label2)

                        def on_vote_button_press(button):
                            self.selected_dead_poison = button.text

                            # Reset color of the previous button
                            if self.previous_button != None:
                                if self.previous_button.text != self.selected_dead_poison:
                                    self.previous_button.background_color = [0, 0.5, 0, 1]  # Reset to default

                            # Change the color of the current button to red
                            button.background_color = [0, 0, 0, 1]  # Red color in RGBA format

                            # Update the previous_button to the current button
                            self.previous_button = button
                            print(f"Witch kill for: {self.selected_dead_poison}")
                            # Assuming you have a 'wolf_choice' attribute in app.player_names_roles[app.current_name]
                            app.player_names_roles[app.current_name]['dead_poison'] = self.selected_dead_poison
                            app.player_names_roles[app.current_name]['dead_poison_flag'] = False
                            # Emit 'update_roles' instead of 'ready_updated'
                            sio.emit('update_wolf', {'wolf': app.player_names_roles})
                            # Enable the ready_button when a vote is selected

                        for player, info in app.player_names_roles.items():
                            is_alive_value = info.get('is_alive', '')
                            if player != app.current_name and is_alive_value != 0:
                                vote_label = Button(text=player, font_size=30, font_name='Arial',
                                                    background_color=[0, 0.5, 0, 1])
                                # Set the on_press callback for the button
                                vote_label.bind(on_press=on_vote_button_press)
                                self.vote_buttons.append(vote_label)
                                witch_layout.add_widget(vote_label)

                    if live_poison_flag:
                        votes_label1 = Label(text=app.reverse_text("המתיני שהזאבים יחליטו את מי לטרוף") + "\n" + app.reverse_text(
                            "ובחרי האם לתת שיקוי חיים:"), font_size=35, font_name='Arial')
                        witch_layout.add_widget(votes_label1)
                        wolf_votes_label1 = Label(text="", font_size=30, font_name='Arial')
                        self.flag_votes = False

                        def check_wolf_readiness(dt):
                            wolf_arr = [info.get('ready_night', False) for player, info in app.player_names_roles.items() if
                                        info.get('is_alive', '') and app.reverse_text('זאב') in info.get('role', '')]
                            self.flag_votes = all(wolf_arr)
                            print("WOLF FLAGS:  ", wolf_arr)

                            if self.flag_votes:
                                self.ready_button.disabled = False
                                wolf_select = self.wolf_choice()
                                wolf_select_label1 = Label(text=wolf_select + " " + app.reverse_text("הזאבים החליט לטרוף את"), font_name='Arial')
                                wolf_select_label2 = Label(text=app.reverse_text(",האם תרצי להעניק שיקוי חיים?"), font_name='Arial')
                                witch_select_label1 = Button(text="ןכ", font_name='Arial', background_color=[1, 0, 0, 1])
                                witch_select_label2 = Button(text="אל", font_name='Arial', background_color=[1, 0, 0, 1])
                                self.vote_buttons.append(witch_select_label1)
                                self.vote_buttons.append(witch_select_label2)

                                live_layout.add_widget(witch_select_label2)
                                live_layout.add_widget(witch_select_label1)
                                live_layout.add_widget(wolf_select_label2)
                                live_layout.add_widget(wolf_select_label1)

                                print("WOLF_select: " , wolf_select)
                                Clock.unschedule(check_wolf_readiness)
                                app.player_names_roles[app.current_name]['ready_night'] = False
                                # sio.emit('update_ready', {'ready': app.player_names_roles})
                                self.send_update_to_server(dt=UPDATE_DELAY)

                                print("After ready update for night screen: ", app.player_names_roles)
                                Clock.schedule_interval(self.check_readiness, 1)

                                def on_witch_select_label1(instance):
                                    print("yes")
                                    instance.background_color = [0, 1, 0, 1]  # Green
                                    witch_select_label2.background_color = [1, 0, 0, 1]  # Red
                                    app.player_names_roles[app.current_name]['live_poison'] = wolf_select
                                    app.player_names_roles[app.current_name]['live_poison_flag'] = False
                                    sio.emit('update_ready', {'ready': app.player_names_roles})

                                def on_witch_select_label2(instance):
                                    print("no")
                                    instance.background_color = [0, 1, 0, 1]  # Green
                                    witch_select_label1.background_color = [1, 0, 0, 1]  # Red
                                    app.player_names_roles[app.current_name]['live_poison'] = ""
                                    app.player_names_roles[app.current_name]['live_poison_flag'] = True
                                    sio.emit('update_ready', {'ready': app.player_names_roles})

                                witch_select_label1.bind(on_release=on_witch_select_label1)
                                witch_select_label2.bind(on_release=on_witch_select_label2)

                        # Schedule the check_wolf_readiness function to be called every second
                        Clock.schedule_interval(check_wolf_readiness, 1)
                        witch_layout.add_widget(live_layout)
                    self.ready_button.disabled = False
                    witch_layout.add_widget(self.ready_button)
                    self.add_widget(witch_layout)
                    app.player_names_roles[app.current_name]['ready_night'] = False
                    # sio.emit('update_ready', {'ready': app.player_names_roles})
                    self.send_update_to_server(dt=UPDATE_DELAY)

                    Clock.schedule_interval(self.check_readiness, 1)

                else:
                    # לשים קצת דברים מעניינים פה
                    witch_layout = BoxLayout(orientation='vertical')
                    header_label1 = Label(text=app.reverse_text("לילה טוב מכשפה!"), font_size=50, font_name='Arial')
                    witch_layout.add_widget(header_label1)
                    self.add_widget(witch_layout)
                    app.player_names_roles[app.current_name]['ready_night'] = True
                    sio.emit('update_ready', {'ready': app.player_names_roles})
                    print("After ready update for night screen: ", app.player_names_roles)
                    Clock.schedule_interval(self.check_readiness, 1)

            else:
                # לשים קצת דברים מעניינים פה
                witch_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מכשפה!"), font_size=50, font_name='Arial')
                witch_layout.add_widget(header_label1)
                self.add_widget(witch_layout)
                app.player_names_roles[app.current_name]['ready_night'] = True
                sio.emit('update_ready', {'ready': app.player_names_roles})
                print("After ready update for night screen: ", app.player_names_roles)
                Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('מגדת עתידות'):

            if app.general['old_is_alive']:
                # app.player_names_roles[app.current_name]['ready_night'] = False
                # sio.emit('update_ready', {'ready': app.player_names_roles})
                seer_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מגדת עתידות!"), font_size=50, font_name='Arial')
                seer_layout.add_widget(header_label1)
                seer_label1 = Label(text=app.reverse_text("בחרי את השחקן שתרצי לחשוף את תפקידו:"), font_size=35, font_name='Arial')
                seer_layout.add_widget(seer_label1)
                self.player_to_seer = Label(text='', font_size=35, font_name='Arial')
                self.seer_flag = 0
                def on_vote_button_press(button):
                    if self.seer_flag == 0:
                        player_name = button.text
                        button.background_color = [0, 0.5, 0, 1] # Green color in RGBA format
                        print("seer- Player  : ", player_name)
                        self.seer_flag += 1
                        self.player_to_seer.text = app.player_names_roles[player_name]['role'] + " " + "אוה" + " " +  player_name + " " + app.reverse_text("התפקיד של")
                        self.ready_button.disabled = False

                for player, info in app.player_names_roles.items():
                    is_alive_value = info.get('is_alive', '')
                    if is_alive_value > 0:
                        if player != app.current_name:
                            vote_label = Button(text=player, font_size=30, font_name='Arial',
                                                background_color=[0.5, 0, 0, 1])

                            vote_label.bind(on_press=on_vote_button_press)
                            seer_layout.add_widget(vote_label)

                seer_layout.add_widget(self.player_to_seer)
                seer_layout.add_widget(self.ready_button)
                self.add_widget(seer_layout)
                # app.player_names_roles[app.current_name]['ready'] = False
                # sio.emit('update_ready', {'ready': app.player_names_roles})
                print("After ready update for night screen: ", app.player_names_roles)
                Clock.schedule_interval(self.check_readiness, 1)
            else:
                # לשים קצת דברים מעניינים פה
                seer_layout = BoxLayout(orientation='vertical')
                header_label1 = Label(text=app.reverse_text("לילה טוב מגדת עתידות!"), font_size=50, font_name='Arial')
                seer_layout.add_widget(header_label1)
                self.add_widget(seer_layout)
                app.player_names_roles[app.current_name]['ready_night'] = True
                sio.emit('update_ready', {'ready': app.player_names_roles})
                print("After ready update for night screen: ", app.player_names_roles)
                Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('צייד'):
            #לשים קצת דברים מעניינים פה
            hunter_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב צייד!"), font_size=50, font_name='Arial')
            hunter_layout.add_widget(header_label1)
            self.add_widget(hunter_layout)
            app.player_names_roles[app.current_name]['ready_night'] = True
            sio.emit('update_ready', {'ready': app.player_names_roles})
            print("After ready update for night screen: ", app.player_names_roles)
            Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('קופידון'):

            # לשים קצת דברים מעניינים פה
            cupid_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב קופידון!"), font_size=50, font_name='Arial')
            cupid_layout.add_widget(header_label1)
            self.add_widget(cupid_layout)
            app.player_names_roles[app.current_name]['ready_night'] = True
            sio.emit('update_ready', {'ready': app.player_names_roles})
            print("After ready update for night screen: ", app.player_names_roles)
            Clock.schedule_interval(self.check_readiness, 1)


        if role == app.reverse_text('עלוקה'):
            #לשים קצת דברים מעניינים פה
            leech_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב עלוקה!"), font_size=50, font_name='Arial')
            leech_layout.add_widget(header_label1)
            self.add_widget(leech_layout)
            app.player_names_roles[app.current_name]['ready_night'] = True
            sio.emit('update_ready', {'ready': app.player_names_roles})
            print("After ready update for night screen: ", app.player_names_roles)
            Clock.schedule_interval(self.check_readiness, 1)

        if role == app.reverse_text('אזרח פשוט'):
            #לשים קצת דברים מעניינים פה
            simple_layout = BoxLayout(orientation='vertical')
            header_label1 = Label(text=app.reverse_text("לילה טוב אזרח!"), font_size=50, font_name='Arial')
            simple_layout.add_widget(header_label1)
            self.add_widget(simple_layout)
            app.player_names_roles[app.current_name]['ready_night'] = True
            sio.emit('update_ready', {'ready': app.player_names_roles})
            print("After ready update for night screen: ", app.player_names_roles)
            Clock.schedule_interval(self.check_readiness, 1)

    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_night', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            print("All players are ready!")
            if app.player_names_roles[app.current_name]['is_alive'] > 0:
                print("All players are ready!")
                is_end_game = self.check_end_game()
                if is_end_game[0]:
                    print("END GAME ", is_end_game[1])
                    app.is_end_game = is_end_game[1]  # Store the value in the app instance
                    app.screen_manager.current = 'end_game_screen'
                else:
                    app.screen_manager.current = 'day_screen'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check

    def check_end_game(self):
        end_game_flag = [False, ""]
        roles_alive = []
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                roles_alive.append(app.player_names_roles[player]['role'])
        print("roles_alive: ", roles_alive)

        if not roles_alive:
            print("Condition no one won")
            return [True, app.reverse_text("אף אחד לא ניצח")]
        # Condition 1: When there are only words containing the word "זאב" in the array
        if len(roles_alive) == 2:
            if app.reverse_text("קופידון") in roles_alive:
                return [True, app.reverse_text("הנאהבים ניצחו")]
        # Condition 1: When there are only words containing the word "זאב" in the array
        condition1 = all(app.reverse_text('זאב') in role for role in roles_alive)

        # Condition 2: When there are only words containing the word "זאב" and the word "עלוקה" in the array
        condition2 = all(app.reverse_text('זאב') in role or app.reverse_text('עלוקה') in role for role in roles_alive) and any(
            app.reverse_text('זאב') in role for role in roles_alive) and any(app.reverse_text('עלוקה') in role for role in roles_alive)

        # Condition 3: When there are no words containing "זאב" in the array
        condition3 = not any(app.reverse_text('זאב') in role for role in roles_alive)

        # Check conditions
        if condition1:
            print("Condition 1 met")
            # Perform actions when condition 1 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים ניצחו")

        elif condition2:
            print("Condition 2 met")
            # Perform actions when condition 2 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים והעלוקה")

        elif condition3:
            print("Condition 3 met")
            # Perform actions when condition 3 is met
            end_game_flag[0] = True
            if app.reverse_text('עלוקה') in roles_alive:
                end_game_flag[1] = app.reverse_text("האזרחים והעלוקה ניצחו")
            else:
                end_game_flag[1] = app.reverse_text("האזרחים ניצחו")


        else:
            print("No condition met")
            # Perform actions when none of the conditions are met

        return end_game_flag

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            if self.vote_buttons:
                for b in self.vote_buttons:
                    b.disabled = False
            app.player_names_roles[app.current_name]['ready_night'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            if self.vote_buttons:
                for b in self.vote_buttons:
                    b.disabled = True
            app.player_names_roles[app.current_name]['ready_night'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

    def wolf_choice(self):
        for player, info in app.player_names_roles.items():
            role = info.get('role', '')
            is_alive_value = info.get('is_alive', '')
            if is_alive_value and app.reverse_text('זאב') in role:
                wolf_list = {}
                # Loop through wolves
                selected_name = app.player_names_roles[player]['wolf_choice']
                wolf_num = app.player_names_roles[player]['wolf_number']

                        # Initialize the entry in wolf_list if not present
                if selected_name not in wolf_list:
                    wolf_list[selected_name] = {'count': 0, 'min_wolf': float('inf')}

                        # Update count and min_wolf fields
                wolf_list[selected_name]['count'] += 1
                wolf_list[selected_name]['min_wolf'] = min(wolf_list[selected_name]['min_wolf'], wolf_num)

                # Find the name with the maximum count and minimum min_wolf
        max_count_name = max(wolf_list, key=lambda x: (wolf_list[x]['count'], -wolf_list[x]['min_wolf']))
            # Print the result
        print(wolf_list)
        print(f"The name that the most wolves wanted to eat is: {max_count_name}")
        return str(max_count_name)

class DayScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(DayScreen, self).__init__(**kwargs)
        self.dead_players = []
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def on_enter(self, *args):
        self.clear_widgets()  # Clear existing widgets from the screen
        app.player_names_roles[app.current_name]['ready_mayor'] = False
        app.player_names_roles[app.current_name]['ready_mayor2'] = False
        self.selected_dead = False

        self.ready_button_mayor = ToggleButton(
            text=app.reverse_text("לבחירת ראש העיר"),
            on_press=self.toggle_ready_mayor,
            background_color=[1, 0, 0, 1],
            font_name='Arial'
        )
        self.ready_button_election = ToggleButton(
            text=app.reverse_text("לדיונים ובחירת השחקן שיצא"),
            on_press=self.toggle_ready_election,
            background_color=[1, 0, 0, 1],
            font_name='Arial'
        )
        day_layout = BoxLayout(orientation='vertical')
        day_label = Label(text="!"+app.player_names_roles[app.current_name]['role']+" "+app.reverse_text("בוקר טוב"), font_name='Arial')
        day_layout.add_widget(day_label)
        wolf_choice = self.wolf_choice()
        witch_player = [name for name, info in app.player_names_roles.items() if info.get('role', '') == app.reverse_text('מכשפה')]
        dead_choice = ''
        if witch_player:
            dead_choice = app.player_names_roles[witch_player[0]]['dead_poison']
        first_alive_player = None
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0 and wolf_choice != player and dead_choice != player:
                first_alive_player = player
                print("first_alive_player:   ", first_alive_player)
                break

        if app.current_name == first_alive_player:
            # Call the player-specific code
            print("wolf_choice: ", wolf_choice)
            self.check_if_dead(wolf_choice=wolf_choice)
            # self.change_to_minus1()
            # Schedule the continuation for all players
            # for player, info in app.player_names_roles.items():
            #     app.player_names_roles[player]['ready']=False
        while not self.selected_dead:
            time.sleep(1)  # Wait for 1 second before checking again
            self.selected_dead = app.general['selected_dead']
        self.continue_for_all(day_layout)
        # else:
        #     # Schedule for all players
        #     Clock.schedule_once(lambda dt: self.continue_for_all(day_layout), 0)

    def continue_for_all(self, day_layout):
        # Continue with the code for all players

        dead_label = Label(text=app.reverse_text("הלילה יצאו מהמשחק:"), font_name='Arial')
        day_layout.add_widget(dead_label)
        self.dead_players = []
        print("self.dead_players 1:  ",self.dead_players )
        for player, info in app.player_names_roles.items():
            is_alive_value = info.get('is_alive', '')
            if is_alive_value == 0:
                self.dead_players.append(player)
        print("self.dead_players 2:  ",self.dead_players)

        if self.dead_players:
            for p in self.dead_players:
                if p == app.general['mayor']:
                    app.general['is_mayor'] = False
                    app.player_names_roles['mayor'] = ''
                    sio.emit('update_general', {'general': app.general})

                if app.player_names_roles[p]['role'] == app.reverse_text('זקן השבט'):
                    dead_label3 = Label(text=app.reverse_text('מכיוון שזקן השבט יצא מהמשחק,\n המגן, המכשפה, המגדת עתידות והצייד מאבדים את כוחם'), font_name='Arial')
                    day_layout.add_widget(dead_label3)

                dead_label2 = Label(text=app.reverse_text("יצא מהמשחק הלילה") + " " + app.player_names_roles[p]['role'] + " " + app.reverse_text("בתפקיד") + " " + p, font_name='Arial')
                day_layout.add_widget(dead_label2)

        else:
            print("self.dead_players 3:  ", self.dead_players)

            dead_label2 = Label(text=app.reverse_text("אף אחד לא יצא מהמשחק הלילה"), font_name='Arial')
            day_layout.add_widget(dead_label2)

        is_alive_value = app.player_names_roles[app.current_name]['is_alive']
        print(f'Player is_alive value: {is_alive_value}')
        if is_alive_value == 0:
            app.screen_manager.current = 'end_dead_screen'

        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        else:
            if not app.general['is_mayor']:
                day_layout.add_widget(self.ready_button_mayor)
            else:
                day_layout.add_widget(self.ready_button_election)


            self.add_widget(day_layout)
            Clock.schedule_interval(self.check_readiness, 1)
    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_morning', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):

        if self.are_all_players_ready(app.player_names_roles):
            if app.player_names_roles[app.current_name]['is_alive'] > 0:
                print("All players are ready!")
                is_end_game = self.check_end_game()
                if is_end_game[0]:
                    print("END GAME ", is_end_game[1])
                    app.is_end_game = is_end_game[1]  # Store the value in the app instance
                    app.screen_manager.current = 'end_game_screen'
                else:
                    if app.general['is_mayor']:
                        app.screen_manager.current = 'time_screen'
                    else:
                        app.screen_manager.current = 'mayor_screen'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check


    def check_end_game(self):
        end_game_flag = [False, ""]
        roles_alive = []
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                roles_alive.append(app.player_names_roles[player]['role'])
        print("roles_alive: ", roles_alive)

        if not roles_alive:
            print("Condition no one won")
            return [True, app.reverse_text("אף אחד לא ניצח")]
        # Condition 1: When there are only words containing the word "זאב" in the array
        if len(roles_alive) == 2:
            if app.reverse_text("קופידון") in roles_alive:
                return [True, app.reverse_text("הנאהבים ניצחו")]

        condition1 = all(app.reverse_text('זאב') in role for role in roles_alive)

        # Condition 2: When there are only words containing the word "זאב" and the word "עלוקה" in the array
        condition2 = all(
            app.reverse_text('זאב') in role or app.reverse_text('עלוקה') in role for role in roles_alive) and any(
            app.reverse_text('זאב') in role for role in roles_alive) and any(
            app.reverse_text('עלוקה') in role for role in roles_alive)

        # Condition 3: When there are no words containing "זאב" in the array
        condition3 = not any(app.reverse_text('זאב') in role for role in roles_alive)

        # Check conditions
        if condition1:
            print("Condition 1 met")
            # Perform actions when condition 1 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים ניצחו")

        elif condition2:
            print("Condition 2 met")
            # Perform actions when condition 2 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים והעלוקה")

        elif condition3:
            print("Condition 3 met")
            # Perform actions when condition 3 is met
            end_game_flag[0] = True
            if app.reverse_text('עלוקה') in roles_alive:
                end_game_flag[1] = app.reverse_text("האזרחים והעלוקה ניצחו")
            else:
                end_game_flag[1] = app.reverse_text("האזרחים ניצחו")


        else:
            print("No condition met")
            # Perform actions when none of the conditions are met

        return end_game_flag

    def toggle_ready_election(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("לדיונים ובחירת השחקן שיצא")
            instance.background_color = [1, 0, 0, 1]
            app.player_names_roles[app.current_name]['ready_morning'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            app.player_names_roles[app.current_name]['ready_morning'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

    def toggle_ready_mayor(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("לבחירת ראש העיר")
            instance.background_color = [1, 0, 0, 1]
            app.player_names_roles[app.current_name]['ready_morning'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            app.player_names_roles[app.current_name]['ready_morning'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

    def change_to_minus1(self):
        for player, info in app.player_names_roles.items():
            if app.player_names_roles[player]['is_alive'] == 0:
                app.player_names_roles[player]['is_alive'] = -1
        sio.emit('update_wolf', {'wolf': app.player_names_roles})

    def check_if_dead(self, wolf_choice):
        witch_name = ""
        shield_name = ""
        cupid_name = ""
        defense_on = ""
        lover = ""
        live_poison = ""
        dead_poison = ""
        for player, info in app.player_names_roles.items():
            # app.player_names_roles[player]['ready'] = False
            role = info.get('role', '')
            if app.reverse_text('מכשפה') == role:
                live_poison = app.player_names_roles[player]['live_poison']
                dead_poison = app.player_names_roles[player]['dead_poison']
                witch_name = player
            elif app.reverse_text('קופידון') == role:
                lover = app.player_names_roles[player]['lover']
                cupid_name = player
            elif app.reverse_text('מגן') == role:
                shield_name = player
                defense_on = app.player_names_roles[player]['defense_on']

        print("defense_onprint ",defense_on,"wolf_choice ", wolf_choice)
        if live_poison != wolf_choice and defense_on != wolf_choice:
            app.player_names_roles[wolf_choice]['is_alive'] -= 1
            if witch_name != "":
                app.player_names_roles[witch_name]['live_poison'] = ""
            if app.player_names_roles[wolf_choice]['is_alive'] == 0 and (wolf_choice == lover or wolf_choice == cupid_name):
                app.player_names_roles[lover]['is_alive'] = 0
                app.player_names_roles[cupid_name]['is_alive'] = 0
            print(" if 1")


        if dead_poison != "":
            dead_poison = app.player_names_roles[witch_name]['dead_poison']
            app.player_names_roles[dead_poison]['is_alive'] = 0
            if dead_poison == lover or dead_poison == cupid_name:
                app.player_names_roles[lover]['is_alive'] = 0
                app.player_names_roles[cupid_name]['is_alive'] = 0
            print(" if 2")
        if witch_name != "":
            app.player_names_roles[witch_name]['live_poison'] = ""
            app.player_names_roles[witch_name]['dead_poison'] = ""
        sio.emit('update_wolf', {'wolf': app.player_names_roles})
        app.general['selected_dead'] = True
        sio.emit('update_general', {'general': app.general})

    def wolf_choice(self):
        wolf_list = {}  # Initialize wolf_list outside the loop
        for player, info in app.player_names_roles.items():
            role = info.get('role', '')
            is_alive_value = info.get('is_alive', 0)
            if is_alive_value > 0 and app.reverse_text('זאב') in role:
                selected_name = app.player_names_roles[player]['wolf_choice']
                wolf_num = app.player_names_roles[player]['wolf_number']

                # Initialize the entry in wolf_list if not present
                if selected_name not in wolf_list:
                    wolf_list[selected_name] = {'count': 0, 'min_wolf': float('inf')}

                # Update count and min_wolf fields
                wolf_list[selected_name]['count'] += 1
                wolf_list[selected_name]['min_wolf'] = min(wolf_list[selected_name]['min_wolf'], wolf_num)

        # Check if wolf_list is not empty before finding the max
        if wolf_list:
            max_count_name = max(wolf_list, key=lambda x: (wolf_list[x]['count'], -wolf_list[x]['min_wolf']))
            print(wolf_list)
            print(f"The name that the most wolves wanted to eat is: {max_count_name}")
            return str(max_count_name)
        else:
            print("No wolves made a choice.")
            return ""


class PopUp(Popup):
    def __init__(self, message, **kwargs):
        super(PopUp, self).__init__(**kwargs)
        self.title_font = 'Arial'
        self.title = 'Massage'

        # Create a Label widget with the specified font
        label = Label(text=message, font_name='Arial', font_size=16)

        # Create a Button widget to close the Popup
        close_button = Button(text=app.reverse_text('סגור'), on_press=self.dismiss, font_name='Arial')

        # Add the Label and Button to the Popup content
        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(label)
        self.content.add_widget(close_button)

class ElectionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(ElectionScreen, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def change_to_minus1(self):
        for player, info in app.player_names_roles.items():
            if app.player_names_roles[player]['is_alive'] == 0:
                app.player_names_roles[player]['is_alive'] = -1
        sio.emit('update_wolf', {'wolf': app.player_names_roles})

    def on_enter(self, *args):
        self.change_to_minus1()
        app.player_names_roles[app.current_name]['ready_night'] = False
        print("mayor screen")
        self.clear_widgets()  # Clear existing widgets from the screen
        time.sleep(1)
        self.selected_votes_dead = ''
        self.previous_button = None  # Keep track of the previously pressed button
        self.vote_buttons = []
        self.ready_button = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            disabled=True,  # Initially disable the button
            font_name='Arial'
        )

        town_layout = BoxLayout(orientation="vertical")
        votes_label1 = Label(text=app.reverse_text("בחר\י באדום את מי שאת\ה רוצה שיצא מהמשחק:"), font_size=35,
                             font_name='Arial')
        town_layout.add_widget(votes_label1)

        # app.player_names_roles[app.current_name]['ready_election'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})

        def on_vote_button_press(button):

            self.selected_votes_dead = button.text

            # Reset color of the previous button
            if self.previous_button != None:
                if self.previous_button.text != self.selected_votes_dead:
                    self.previous_button.background_color = [0, 0.5, 0, 1]  # Reset to default

            # Change the color of the current button to red
            button.background_color = [0.5, 0, 0, 1]  # Red color in RGBA format

            # Update the previous_button to the current button
            self.previous_button = button
            print(f"Vote for town dead: {self.selected_votes_dead}")
            app.player_names_roles[app.current_name]['town_votes'] = self.selected_votes_dead
            sio.emit('update_wolf', {'wolf': app.player_names_roles})
            # Enable the ready_button when a vote is selected
            self.ready_button.disabled = False

        for player, info in app.player_names_roles.items():
            role_value = info.get('role', '')
            is_alive_value = info.get('is_alive', '')
            if player != app.current_name and is_alive_value > 0:
                vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0, 0.5, 0, 1])
                # Set the on_press callback for the button
                vote_label.bind(on_press=on_vote_button_press)
                self.vote_buttons.append(vote_label)
                town_layout.add_widget(vote_label)
        town_layout.add_widget(self.ready_button)
        self.add_widget(town_layout)

        app.player_names_roles[app.current_name]['ready_election'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

        print("After ready update for mayor screen: ", app.player_names_roles)

        Clock.schedule_interval(self.check_readiness, 1)



    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_election', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            print("All players are ready!")
            app.screen_manager.current = 'election_screen2'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            for b in self.vote_buttons:
                b.disabled = False
            app.player_names_roles[app.current_name]['ready_election'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            for b in self.vote_buttons:
                b.disabled = True
            app.player_names_roles[app.current_name]['ready_election'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)


class ElectionScreen2(BaseScreen):
    def __init__(self, **kwargs):
        super(ElectionScreen2, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
        self.check_hunter_end_timer = None
        self.hunter_vote_check_timer = Clock.schedule_interval(self.check_hunter_vote, 1)

        self.hunter_present = False
        self.hunter_alive = False


    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def check_hunter_end(self, dt):
        if app.general.get('hunterEnd', False):
            self.ready_button.disabled = False
            self.check_hunter_end_timer.cancel()

    def check_hunter_vote(self, dt):
        if self.hunter_present:
            if app.general.get('hunterVote', '') != '':
                self.hunter_vote_check_timer.cancel()
                self.update_screen_with_hunter_vote()  # Method to handle updates

                # Enable the ready button after the hunter has voted
                if self.hunter_alive:
                    self.ready_button.disabled = False

    def update_screen_with_hunter_vote(self):
        town_layout = self.children[0]  # Assuming the town layout is the first child
        # Clear previous hunter vote widgets
        for widget in [child for child in town_layout.children if 'vote_hunter' in child.text]:
            town_layout.remove_widget(widget)

        if app.general['hunterVote']:
            vote_hunter_label = Label(
                text=app.general['hunterVote'] + " " + app.reverse_text("הצייד החליט להוציא את"),
                font_size=35,
                font_name='Arial'
            )
            town_layout.add_widget(vote_hunter_label)
            vote_hunter_label1 = Label(
                text=app.player_names_roles[app.general['hunterVote']]['role'] + " " + app.reverse_text("בתפקיד"),
                font_size=35,
                font_name='Arial'
            )
            town_layout.add_widget(vote_hunter_label1)

            # Handle special case for Cupid and lover
            if app.player_names_roles[app.general['hunterVote']]['role'] == app.reverse_text('קופידון'):
                lover = app.player_names_roles[app.general['hunterVote']].get('lover', '')
                votes_label_lover_hunt = Label(
                    text=app.reverse_text("גם יצא\ה מהמשחק") + " " + app.reverse_text("הנאהב של הקופידון") + " " + lover,
                    font_size=35,
                    font_name='Arial'
                )
                town_layout.add_widget(votes_label_lover_hunt)
                votes_label_lover_hunt1 = Label(
                    text=app.player_names_roles[lover]['role'] + " " + app.reverse_text("בתפקיד"),
                    font_size=35,
                    font_name='Arial'
                )
                town_layout.add_widget(votes_label_lover_hunt1)

            if app.general['hunterVote'] == app.player_names_roles[app.general['hunterVote']].get('lover', ''):
                cupid_name = next(
                    (player for player, info in app.player_names_roles.items() if
                     info['lover'] == app.general['hunterVote']),
                    ''
                )
                votes_label_cupid_hunt = Label(
                    text=app.reverse_text("גם יצא\ה מהמשחק") + " " + app.reverse_text(
                        "הקופידון של הנאהב") + " " + cupid_name,
                    font_size=35,
                    font_name='Arial'
                )
                town_layout.add_widget(votes_label_cupid_hunt)

    def check_hunter_status(self):
        # Check if hunter exists and is alive
        self.hunter_present = any(info.get('role', '') == app.reverse_text('צייד') for info in app.player_names_roles.values())
        self.hunter_alive = any(info.get('role', '') == app.reverse_text('צייד') and info.get('is_alive', 0) > 0 for info in app.player_names_roles.values())

        # Disable the ready button if the hunter is present and alive
        if self.hunter_alive:
            self.ready_button.disabled = True
        else:
            self.ready_button.disabled = False
    def setup_screen(self):
        # Check if the hunter is supposed to vote
        if self.hunter_alive:
            self.ready_button.disabled = True
            Clock.schedule_once(self.check_hunter_vote)
        else:
            self.ready_button.disabled = False
    def on_enter(self, *args):
        self.clear_widgets()  # Clear existing widgets from the screen
        time.sleep(1)
        self.selected_votes_town = ''
        self.town_list = []
        self.previous_button = None  # Keep track of the previously pressed button
        self.ready_button = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            font_name='Arial'
        )
        self.check_hunter_status()
        self.setup_screen()
        self.selected_votes_town = ''
        self.town_list = []
        first_alive_player = None
        self.flag_cupid_dead = False
        self.flag_lover_dead = False
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                first_alive_player = player
                print("first_alive_player:   ", first_alive_player)
                break

        if app.current_name == first_alive_player:
            self.check_town_votes()

        while not self.selected_votes_town:
            time.sleep(1)  # Wait for 1 second before checking again
            self.selected_votes_town = app.general['town_final_choice']



        if app.current_name == app.general['town_final_choice'] or app.current_name == app.general['hunterVote']:
            app.player_names_roles[app.current_name]['is_alive'] = 0
            cupid_name = ''
            lover = ''

            for player, info in app.player_names_roles.items():
                role = info.get('role', '')
                if app.reverse_text('קופידון') == role:
                    lover = app.player_names_roles[player]['lover']
                    cupid_name = player

            if app.current_name == cupid_name:
                app.player_names_roles[lover]['is_alive'] = 0
            if app.current_name == lover:
                app.player_names_roles[cupid_name]['is_alive'] = 0

            sio.emit('update_wolf', {'wolf': app.player_names_roles})
            app.screen_manager.current = 'end_dead_screen'
        time.sleep(2)  # Wait for 2 second before checking again


        if app.player_names_roles[app.current_name]['is_alive'] == 0:
            app.screen_manager.current = 'end_dead_screen'


        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})

        town_layout = BoxLayout(orientation="vertical")
        votes_label1 = Label(text=app.general['town_final_choice'] + " " + app.reverse_text("העיירה החליטה להוציא את"), font_size=35, font_name='Arial')
        town_layout.add_widget(votes_label1)
        votes_label4 = Label(text=app.player_names_roles[app.general['town_final_choice']]['role'] + " " + app.reverse_text("בתפקיד"), font_size=35, font_name='Arial')
        town_layout.add_widget(votes_label4)

        lover = ''
        cupid_name = ''
        for player, info in app.player_names_roles.items():
            role = info.get('role', '')
            if app.reverse_text('קופידון') == role:
                lover = app.player_names_roles[player]['lover']
                cupid_name = player
        if app.player_names_roles[app.general['town_final_choice']]['role'] == app.reverse_text('קופידון'):
            votes_label_lover = Label(text= app.reverse_text("גם יצא\ה מהמשחק") + " " + app.reverse_text("הנאהב של הקופידון") + " " + lover, font_size=35, font_name='Arial')
            town_layout.add_widget(votes_label_lover)
            votes_label_lover1 = Label(text=app.player_names_roles[lover]['role'] + " " + app.reverse_text("בתפקיד"), font_size=35, font_name='Arial')
            town_layout.add_widget(votes_label_lover1)

        if app.general['town_final_choice'] == lover:
            votes_label_cupid = Label(text=app.reverse_text("גם יצא\ה מהמשחק") + " " + app.reverse_text("הקופידון של הנאהב") + " " + cupid_name, font_size=35, font_name='Arial')
            town_layout.add_widget(votes_label_cupid)

        votes_label2 = Label(text=app.reverse_text("פירוט ההצבעות:"), font_size=35, font_name='Arial')
        town_layout.add_widget(votes_label2)
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                votes_label3 = Label(text=app.player_names_roles[player]['town_votes'] + " " + app.reverse_text("בחר\ה את") + " " + player, font_size=25,font_name='Arial')
                town_layout.add_widget(votes_label3)
        votes_label_dead_player = Label(text=app.player_names_roles[app.general['town_final_choice']]['town_votes'] + " " + app.reverse_text("בחר\ה את") + " " + app.general['town_final_choice'], font_size=25,font_name='Arial')
        town_layout.add_widget(votes_label_dead_player)
        town_layout.add_widget(self.ready_button)
        self.add_widget(town_layout)



        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        # print("After ready update for town2 screen: ", app.player_names_roles)

        Clock.schedule_interval(self.check_readiness, 1)


    def check_town_votes(self):
        self.town_list = []
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                if player == app.general['mayor']:
                    self.town_list.append(app.player_names_roles[player]['town_votes'])
                    self.town_list.append(app.player_names_roles[player]['town_votes'])
                else:
                    self.town_list.append(app.player_names_roles[player]['town_votes'])

        counter = Counter(self.town_list)

        most_common = counter.most_common()

        max_count = most_common[0][1]

        most_frequent = [item for item, count in most_common if count == max_count]

        # If there is a tie, randomly select one element
        if len(most_frequent) > 1:
            if app.player_names_roles[app.general['mayor']]['town_votes'] in most_frequent:
                most_frequent.remove(app.player_names_roles[app.general['mayor']]['town_votes'])
            most_frequent = [random.choice(most_frequent)]

        print("Most frequent element(s):", most_frequent)
        app.general['town_final_choice'] = most_frequent[0]
        sio.emit('update_general', {'general': app.general})


    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():

            if not info.get('ready_election2', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            if app.player_names_roles[app.current_name]['is_alive'] > 0:
                print("All players are ready!")
                is_end_game = self.check_end_game()
                if is_end_game[0]:
                    print("END GAME ", is_end_game[1])
                    app.is_end_game = is_end_game[1]  # Store the value in the app instance
                    app.screen_manager.current = 'end_game_screen'
                else:
                    app.screen_manager.current = 'night_screen'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check

    def check_end_game(self):
        end_game_flag = [False, ""]
        roles_alive = []
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                roles_alive.append(app.player_names_roles[player]['role'])
        print("roles_alive: ", roles_alive)

        if not roles_alive:
            print("Condition no one won")
            return [True, app.reverse_text("אף אחד לא ניצח")]

        # Condition 1: When there are only words containing the word "זאב" in the array
        if len(roles_alive) == 2:
            if app.reverse_text("קופידון") in roles_alive:
                return [True, app.reverse_text("הנאהבים ניצחו")]
        # Condition 1: When there are only words containing the word "זאב" in the array
        condition1 = all(app.reverse_text('זאב') in role for role in roles_alive)

        # Condition 2: When there are only words containing the word "זאב" and the word "עלוקה" in the array
        condition2 = all(app.reverse_text('זאב') in role or app.reverse_text('עלוקה') in role for role in roles_alive) and any(
            app.reverse_text('זאב') in role for role in roles_alive) and any(app.reverse_text('עלוקה') in role for role in roles_alive)

        # Condition 3: When there are no words containing "זאב" in the array
        condition3 = not any(app.reverse_text('זאב') in role for role in roles_alive)

        # Check conditions
        if condition1:
            print("Condition 1 met")
            # Perform actions when condition 1 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים ניצחו")

        elif condition2:
            print("Condition 2 met")
            # Perform actions when condition 2 is met
            end_game_flag[0] = True
            end_game_flag[1] = app.reverse_text("הזאבים והעלוקה")

        elif condition3:
            print("Condition 3 met")
            # Perform actions when condition 3 is met
            end_game_flag[0] = True
            if app.reverse_text('עלוקה') in roles_alive:
                end_game_flag[1] = app.reverse_text("האזרחים והעלוקה ניצחו")
            else:
                end_game_flag[1] = app.reverse_text("האזרחים ניצחו")


        else:
            print("No condition met")
            # Perform actions when none of the conditions are met

        return end_game_flag

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            app.player_names_roles[app.current_name]['ready_election2'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            app.player_names_roles[app.current_name]['ready_election2'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)


class MayorScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(MayorScreen, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def on_enter(self, *args):
        print("mayor screen")
        self.clear_widgets()  # Clear existing widgets from the screen
        time.sleep(1)

        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.selected_votes_mayor = ''
        self.previous_button = None  # Keep track of the previously pressed button
        self.vote_buttons = []
        self.ready_button = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            disabled=True,  # Initially disable the button
            font_name='Arial'
        )
        mayor_layout = BoxLayout(orientation="vertical")
        votes_label1 = Label(text=app.reverse_text("בחר\י בירוק ראש עיר שיקבל 2 קולות בהצבעת העיירה:"), font_size=35,
                             font_name='Arial')
        mayor_layout.add_widget(votes_label1)



        def on_vote_button_press(button):

            self.selected_votes_mayor = button.text

            # Reset color of the previous button
            if self.previous_button != None:
                if self.previous_button.text != self.selected_votes_mayor:
                    self.previous_button.background_color = [0.5, 0, 0, 1]  # Reset to default

            # Change the color of the current button to red
            button.background_color = [0, 0.5, 0, 1]  # Red color in RGBA format

            # Update the previous_button to the current button
            self.previous_button = button
            print(f"Vote for mayor: {self.selected_votes_mayor}")
            app.player_names_roles[app.current_name]['mayor_votes'] = self.selected_votes_mayor
            sio.emit('update_wolf', {'wolf': app.player_names_roles})
            # Enable the ready_button when a vote is selected
            self.ready_button.disabled = False

        for player, info in app.player_names_roles.items():
            role_value = info.get('role', '')
            is_alive_value = info.get('is_alive', '')
            if player != app.current_name and is_alive_value > 0:
                vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0.5, 0, 0, 1])
                # Set the on_press callback for the button
                vote_label.bind(on_press=on_vote_button_press)
                self.vote_buttons.append(vote_label)
                mayor_layout.add_widget(vote_label)
        mayor_layout.add_widget(self.ready_button)
        self.add_widget(mayor_layout)

        app.player_names_roles[app.current_name]['ready_mayor'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

        print("After ready update for mayor screen: ", app.player_names_roles)

        Clock.schedule_interval(self.check_readiness, 1)



    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_mayor', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            print("All players are ready!")
            app.screen_manager.current = 'mayor_screen2'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            for b in self.vote_buttons:
                b.disabled = False
            app.player_names_roles[app.current_name]['ready_mayor'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            for b in self.vote_buttons:
                b.disabled = True
            app.player_names_roles[app.current_name]['ready_mayor'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

class MayorScreen2(BaseScreen):
    def __init__(self, **kwargs):
        super(MayorScreen2, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
    def send_update_to_server(self, dt):
        # Your update logic here
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def on_enter(self, *args):
        self.clear_widgets()  # Clear existing widgets from the screen
        time.sleep(1)

        self.selected_votes_mayor = ''
        self.mayor_list = []
        self.previous_button = None  # Keep track of the previously pressed button
        self.ready_button = ToggleButton(
            text=app.reverse_text("מצב: לא מוכן"),
            on_press=self.toggle_ready,
            background_color=[1, 0, 0, 1],
            font_name='Arial'
        )

        first_alive_player = None
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                first_alive_player = player
                print("first_alive_player:   ", first_alive_player)
                break
        if app.current_name == first_alive_player:
            self.check_mayor_votes()

        while not self.selected_votes_mayor:
            time.sleep(1)  # Wait for 1 second before checking again
            self.selected_votes_mayor = app.general['mayor']

        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})

        mayor_layout = BoxLayout(orientation="vertical")
        votes_label1 = Label(text=app.general['mayor'] + " " + app.reverse_text("ראש העיר הנבחר:"), font_size=35, font_name='Arial')
        mayor_layout.add_widget(votes_label1)
        votes_label2 = Label(text=app.reverse_text("פירוט ההצבעות:"), font_size=35, font_name='Arial')
        mayor_layout.add_widget(votes_label2)
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                votes_label3 = Label(text=app.player_names_roles[player]['mayor_votes'] + " " + app.reverse_text("בחר\ה את") + " " + player, font_size=25,font_name='Arial')
                mayor_layout.add_widget(votes_label3)

        mayor_layout.add_widget(self.ready_button)
        self.add_widget(mayor_layout)

        # app.player_names_roles[app.current_name]['ready'] = False
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        # print("After ready update for mayor2 screen: ", app.player_names_roles)

        Clock.schedule_interval(self.check_readiness, 1)
    def check_mayor_votes(self):
        self.mayor_list = []
        for player, info in app.player_names_roles.items():
            if info.get('is_alive', 0) > 0:
                self.mayor_list.append(app.player_names_roles[player]['mayor_votes'])

        counter = Counter(self.mayor_list)

        most_common = counter.most_common()

        max_count = most_common[0][1]

        most_frequent = [item for item, count in most_common if count == max_count]

        # If there is a tie, randomly select one element
        if len(most_frequent) > 1:
            most_frequent = [random.choice(most_frequent)]

        print("Most frequent element(s):", most_frequent)
        app.general['mayor'] = most_frequent[0]
        app.general['is_mayor'] = True
        sio.emit('update_general', {'general': app.general})


    def are_all_players_ready(self,player_info):
        for player, info in player_info.items():
            if not info.get('ready_mayor2', False) and app.player_names_roles[player]['is_alive'] > 0:
                return False
        return True

    def check_readiness(self, dt):
        if self.are_all_players_ready(app.player_names_roles):
            print("All players are ready!")
            app.screen_manager.current = 'time_screen'
            # Do something when all players are ready
            Clock.unschedule(self.check_readiness)  # Stop the scheduled check

    def toggle_ready(self, instance):
        if instance.state == 'normal':
            instance.text = app.reverse_text("מצב: לא מוכן")
            instance.background_color = [1, 0, 0, 1]
            app.player_names_roles[app.current_name]['ready_mayor2'] = False
        else:
            instance.text = app.reverse_text("מוכן, מחכה לשאר השחקנים")
            instance.background_color = [0, 1, 0, 1]
            app.player_names_roles[app.current_name]['ready_mayor2'] = True
        # sio.emit('update_ready', {'ready': app.player_names_roles})
        self.send_update_to_server(dt=UPDATE_DELAY)

class TimeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(TimeScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        app.player_names_roles[app.current_name]['ready_election'] = False
        app.player_names_roles[app.current_name]['ready_election2'] = False

        app.general['selected_dead'] = False
        sio.emit('update_general', {'general': app.general})

        self.clear_widgets()  # Clear existing widgets from the screen
        self.time_label = Label(text='', font_size=40, font_name='Arial')
        self.add_widget(self.time_label)
        self.timer_event = None  # Initialize timer_event attribute

        print("Time Screen")
        self.remaining_time = app.general['time'] * 60  # Convert minutes to seconds
        self.update_time_display()
        self.timer_event = Clock.schedule_interval(self.update_time_display, 1)

        # Create a "Game Settings" button (initially disabled)
        stop_time_button = Button(text=app.reverse_text('המשך'), size_hint=(None, None), size=(200, 80), disabled=True,
                                           pos_hint={'center_x': 0.5}, background_color=(128 / 255, 128 / 255, 128 / 255, 1), font_name='Arial')
        stop_time_button.bind(on_press=self.stop_time)
        if app.is_first_player or app.current_name == app.general['manager']:
            stop_time_button.disabled = False
        self.add_widget(stop_time_button)

    def update_time_display(self, dt=None):
        if app.general['continue_time'] == False:
            if self.remaining_time > 0:
                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                self.time_label.text = f'{minutes:02d}:{seconds:02d}'
                self.remaining_time -= 1
            else:
                if self.timer_event:
                    self.timer_event.cancel()  # Stop updating the time
                app.screen_manager.current = 'election_screen'
        else:
            if self.timer_event:
                self.timer_event.cancel()  # Stop updating the time
            app.screen_manager.current = 'election_screen'

    def stop_time(self, instance):
        # Add logic to handle the "Game Settings" button press
        # Only the first player can access the game settings
        print("Opening Election screen...")
        app.general['continue_time'] = True
        sio.emit('update_general', {'general': app.general})
        app.screen_manager.current = 'election_screen'


class EndDeadScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(EndDeadScreen, self).__init__(**kwargs)
        self.update_timer = Clock.schedule_interval(self.send_update_to_server, UPDATE_DELAY)
        self.selected_votes_dead = ""

    def send_update_to_server(self, dt):
        sio.emit('update_ready', {'ready': app.player_names_roles})

    def stop_update_timer(self):
        self.update_timer.cancel()

    def on_enter(self, *args):
        app.player_names_roles[app.current_name]['ready_role'] = True
        app.player_names_roles[app.current_name]['ready_night'] = True
        app.player_names_roles[app.current_name]['ready_morning'] = True
        app.player_names_roles[app.current_name]['ready_mayor'] = True
        app.player_names_roles[app.current_name]['ready_mayor2'] = True
        app.player_names_roles[app.current_name]['ready_election'] = True
        app.player_names_roles[app.current_name]['ready_election2'] = True

        self.send_update_to_server(dt=UPDATE_DELAY)

        end_dead_layout = BoxLayout(orientation='vertical')
        dead_label = Label(text=app.reverse_text("אתה מחוץ למשחק"), font_size=40, font_name='Arial')
        end_dead_layout.add_widget(dead_label)

        self.add_widget(end_dead_layout)

        first_alive_player = ""
        if app.is_first_player or app.general['manager'] == app.current_name:
            for player, info in app.player_names_roles.items():
                if info.get('is_alive', 0) > 0:
                    first_alive_player = player
                    break
            if first_alive_player:
                app.general['manager'] = first_alive_player
                sio.emit('update_general', {'general': app.general})

        if app.player_names_roles[app.current_name]['role'] == app.reverse_text('זקן השבט'):
            app.general['old_is_alive'] = False
            sio.emit('update_general', {'general': app.general})
        if app.player_names_roles[app.current_name]['role'] == app.reverse_text('מכשפה'):
            app.player_names_roles[app.current_name]['dead_poison_flag'] = False
            app.player_names_roles[app.current_name]['dead_poison'] = ''
            app.player_names_roles[app.current_name]['live_poison_flag'] = False
            app.player_names_roles[app.current_name]['live_poison'] = ''

        if app.player_names_roles[app.current_name]['role'] == app.reverse_text('מגן'):
            app.player_names_roles[app.current_name]['pre_defender'] = ''
            app.player_names_roles[app.current_name]['defense_on'] = ''

        if app.player_names_roles[app.current_name]['role'] == app.reverse_text('צייד') and app.general['old_is_alive']:
            self.vote_buttons = []
            town_layout = BoxLayout(orientation="vertical")
            votes_label1 = Label(text=app.reverse_text("לחץ על מי שאתה רוצה שיצא מהמשחק:"), font_size=35,
                                 font_name='Arial')
            town_layout.add_widget(votes_label1)

            def on_vote_button_press(button):
                self.selected_votes_dead = button.text
                app.general['hunterVote'] = self.selected_votes_dead
                app.general['hunterEnd'] = True
                sio.emit('update_general', {'general': app.general})
                app.player_names_roles['hunterVote']['is_alive'] = 0
                first_alive_player2 = ""
                if app.is_first_player or app.general['manager'] == app.current_name:
                    for player, info in app.player_names_roles.items():
                        if info.get('is_alive', 0) > 0:
                            first_alive_player2 = player
                            break
                    if first_alive_player2:
                        app.general['manager'] = first_alive_player2
                        sio.emit('update_general', {'general': app.general})
                # Remove town_layout and display end_dead_layout
                self.clear_widgets()
                self.add_widget(end_dead_layout)

            for player, info in app.player_names_roles.items():
                is_alive_value = info.get('is_alive', 0)
                if player != app.current_name and is_alive_value > 0:
                    vote_label = Button(text=player, font_size=30, font_name='Arial', background_color=[0, 0.5, 0, 1])
                    vote_label.bind(on_press=on_vote_button_press)
                    self.vote_buttons.append(vote_label)
                    town_layout.add_widget(vote_label)

            self.add_widget(town_layout)

        time.sleep(2)
        sio.emit('update_wolf', {'wolf': app.player_names_roles})


class EndGameScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(EndGameScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        app = App.get_running_app()

        # Create a BoxLayout for vertical alignment
        layout = BoxLayout(orientation='vertical')

        # Add header and reason labels
        header_label = Label(text=app.reverse_text("נגמר המשחק"), font_name='Arial')
        reason_label = Label(text=app.is_end_game, font_name='Arial')
        layout.add_widget(header_label)
        layout.add_widget(reason_label)

        # Add player roles and names
        for name, details in app.player_names_roles.items():
            role_label = Label(text=f"{name}: {details['role']}", font_name='Arial')
            layout.add_widget(role_label)
            print(f"all roles {name}: {details['role']}")

        # Add the layout to the screen
        self.add_widget(layout)

# Kivy App
class MultiplayerApp(App):
    def build(self):
        # Add attributes to store settings data
        self.number_of_wolves = 0
        self.is_first_player = False
        self.old_flag = True
        self.shield_flag = True
        self.seer_flag = True
        self.witch_flag = True
        self.hunter_flag = True
        self.cupid_flag = True
        self.leech_flag = False
        self.discussion_time = 0
        self.general = {}
        self.player_names = []
        self.player_names_roles = {}
        self.current_name = None
        self.roles =[]

        # Create a ScreenManager
        self.screen_manager = ScreenManager()

        # Create the main screen
        main_screen = MainScreen(name='main_screen')
        self.screen_manager.add_widget(main_screen)

        # Create the role screen
        role_screen = RoleScreen(name='role_screen')
        self.screen_manager.add_widget(role_screen)

        # Create the settings screen
        settings_screen = SettingsScreen(name='settings_screen')
        self.screen_manager.add_widget(settings_screen)

        # Create the night screen
        night_screen = NightScreen(name='night_screen')
        self.screen_manager.add_widget(night_screen)

        # Create the day screen
        day_screen = DayScreen(name='day_screen')
        self.screen_manager.add_widget(day_screen)

        # Create the election screen
        election_screen = ElectionScreen(name='election_screen')
        self.screen_manager.add_widget(election_screen)

        # Create the election screen
        election_screen2 = ElectionScreen2(name='election_screen2')
        self.screen_manager.add_widget(election_screen2)

        # Create the mayor screen
        mayor_screen = MayorScreen(name='mayor_screen')
        self.screen_manager.add_widget(mayor_screen)

         # Create the mayor screen
        mayor_screen2 = MayorScreen2(name='mayor_screen2')
        self.screen_manager.add_widget(mayor_screen2)

         # Create the time screen
        time_screen = TimeScreen(name='time_screen')
        self.screen_manager.add_widget(time_screen)

        # Create the end_dead screen
        end_dead_screen = EndDeadScreen(name='end_dead_screen')
        self.screen_manager.add_widget(end_dead_screen)

        # Create the end_game screen
        end_game_screen = EndGameScreen(name='end_game_screen')
        self.screen_manager.add_widget(end_game_screen)

        # Check if not already connected
        if not sio.connected:
            sio.connect('http://127.0.0.1:5000')

        return self.screen_manager

        # Add this method to update the main_screen attribute
    def update_main_screen(self, names, is_first_player):
        main_screen = self.screen_manager.get_screen('main_screen')
        main_screen.names_label.text = '\n'.join(names)
        self.player_names = names
        print(names)
        self.is_first_player = is_first_player
        main_screen.is_first_player = is_first_player
        main_screen.enable_game_settings_button()
        main_screen.start_game_button.disabled = not main_screen.is_first_player

    def set_general(self, data):
        self.general = data
        print("General:", self.general)

    # Add this method to set the player's entered name
    def set_player_name(self, name):
        self.current_name = app.reverse_text(name)
        print("current player: ", self.current_name)

    # Add this method to set the player's entered name
    def set_name_roles(self, roles):
        self.player_names_roles = roles
        print("Player roles updated:", self.player_names_roles)

    def set_ready(self,ready):
        # ready_player = list(ready.keys())[0]
        # ready_value = ready[self.current_name]['ready']
        # self.player_names_roles[self.current_name]['ready'] = ready_value
        self.player_names_roles = ready
        print("Player ready updated:", self.player_names_roles)

    def set_wolf_choice(self,wolf):
        # ready_player = list(ready.keys())[0]
        # ready_value = ready[self.current_name]['ready']
        # self.player_names_roles[self.current_name]['ready'] = ready_value
        self.player_names_roles = wolf
        print("new data:", self.player_names_roles)


    def reverse_text(self, text):
        # Split the text into words
        words = text.split()

        # Reverse the order of words
        reversed_words = reversed(words)

        # Reverse the letters in each word
        reversed_words_with_letters = [''.join(reversed(word)) for word in reversed_words]

        # Join the reversed words back into a single string
        reversed_text = ' '.join(reversed_words_with_letters)

        return reversed_text


# Handling the update_general event
@sio.on('general_updated')
def update_general(data):
    general = data.get('general', {})
    app.set_general(data=general)
    # print("data***********: ", data)
    print("general_updated***********: ", general)
# Define the SocketIO event handler for updating player names

@sio.on('update_names')
def update_names(data):
    names = data.get('names', [])
    game_manager = data.get('game_manager', '')

    # Access the MultiplayerApp instance and update the main_screen
    app.update_main_screen(names, app.reverse_text(game_manager) == app.screen_manager.get_screen('main_screen').text_input.text)
    app.set_player_name(app.screen_manager.get_screen('main_screen').text_input.text)


@sio.on('game_started')
def handle_game_started():
    app = App.get_running_app()

    # Schedule the screen transition in the main thread using Clock
    Clock.schedule_once(lambda dt: setattr(app.screen_manager, 'current', 'role_screen'), 0)

@sio.on('roles_updated')
def update_roles(data):
    roles = data.get('roles', {})
    # print("data***********: ", data)
    print("roles_updated***********: ", roles)

    app.set_name_roles(roles=roles)
    role_screen = app.screen_manager.get_screen('role_screen')
    Clock.schedule_once(lambda dt: role_screen.handle_roles_page(), 0)

@sio.on('ready_updated')
def update_ready(data):
    ready = data.get('ready', {})
    # print("data***********: ", data)
    print("ready_updated***********: ", ready)

    app.set_ready(ready=ready)
    role_screen = app.screen_manager.get_screen('role_screen')
    # Clock.schedule_once(lambda dt: role_screen.main_wolf_screen(),lambda dt: role_screen.handle_roles_page(),lambda dt: role_screen.wolf_screen(),lambda dt: role_screen.old_screen(),lambda dt: role_screen.witch_screen(),lambda dt: role_screen.magedet_screen(), 0)

@sio.on('wolf_updated')
def update_wolf(data):
    wolf = data.get('wolf', {})
    # print("data***********: ", data)
    print("wolf_updated***********: ", wolf)

    app.set_wolf_choice(wolf=wolf)
    # night_screen = app.screen_manager.get_screen('night_screen')
    # Clock.schedule_once(lambda dt: night_screen.handle_night_screen(), 0)


if __name__ == '__main__':
    app = MultiplayerApp()
    app.run()