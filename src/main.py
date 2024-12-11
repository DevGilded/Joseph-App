import flet as ft
import sqlite3
from typing import Any
import account_manager

def main(page: ft.Page):
    page.title = "InstaVault"
    page.window.icon = 'src/assets/Logo.png'
    page.window.width = 800
    page.window.height = 500
    page.window.maximizable = False
    page.window.resizable = False

    def route_change(route):
        page.views.clear()
        page.views.append(LoginView(page))

        match page.route:
            case '/sign_up':
                page.views.append(SignUpView(page))
            case _:
                pass

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go('/login')

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.route = '/login'

        self.background = ft.Container(
            ft.Image(
                'src/assets/images/WELCOME4.png',
                scale=0.99,
                expand=True,
                fit=ft.ImageFit.CONTAIN,
            ),
            top=-30,
            left=-20
        )

        self.username = ft.TextField(
                width=225,
                border_width=0,
                text_size=18
        )
        self.password = PasswordField()

        self.login_btn = ft.Container(
            content=ft.ElevatedButton(
                'LOGIN',
                color='white',
                bgcolor='black',
                scale=1.2,
                width=150,
                on_click=self.on_login
            ),
            top=335,
            left=75
        )
        self.sign_up_btn = ft.Container(
            content=ft.ElevatedButton(
                'SIGN UP',
                color='white',
                bgcolor='black',
                scale=1.2,
                width=150,
                on_click=lambda e: self.page.go('/sign_up')
            ),
            top=380,
            left=75
        )

        self.controls = [
            ft.Stack(
                [
                    self.background,
                    ft.Container(
                        self.username,
                        top=174,
                        left=40
                    ),
                    ft.Container(
                        self.password,
                        width=245,
                        top=262,
                        left=40
                    ),

                    self.login_btn,
                    self.sign_up_btn,
                ]
            )
        ]

    def on_login(self, event: ft.ControlEvent):
        username = self.username.value
        password = self.password.text_field.value

        if user_authentication(username, password):
            ErrorDialog(self.page, 'Success', f'Welcome back! {username}',
                        on_close=lambda: account_manager.main(self.page, username, password))
        else:
            ErrorDialog(self.page, 'Error', 'Wrong Username or Password')

class SignUpView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.route = '/sign_up'

        self.background = ft.Container(
            ft.Image(
                'src/assets/images/WELCOME4.png',
                scale=0.99,
                expand=True,
                fit=ft.ImageFit.CONTAIN,
            ),
            top=-30,
            left=-20
        )

        self.username = ft.TextField(
            width=225,
            border_width=0,
            text_size=18
        )
        self.password = PasswordField()

        self.login_btn = ft.Container(
            content=ft.ElevatedButton(
                'CREATE',
                color='white',
                bgcolor='black',
                scale=1.2,
                width=150,
                on_click=self.on_create
            ),
            top=335,
            left=75
        )
        self.sign_up_btn = ft.Container(
            content=ft.ElevatedButton(
                'BACK',
                color='white',
                bgcolor='black',
                scale=1.2,
                width=150,
                on_click=lambda e: self.page.go('/login')
            ),
            top=380,
            left=75
        )

        self.controls = [
            ft.Stack(
                [
                    self.background,
                    ft.Container(
                        self.username,
                        top=174,
                        left=40
                    ),
                    ft.Container(
                        self.password,
                        width=245,
                        top=262,
                        left=40
                    ),

                    self.login_btn,
                    self.sign_up_btn,
                ]
            )
        ]

    def on_create(self, event: ft.ControlEvent):
        username = self.username.value
        password = self.password.text_field.value

        print('Trying...')
        try:
            # Connect to SQLite database
            conn = sqlite3.connect("src/assets/database/users.db")
            cursor = conn.cursor()

            # Create table if it doesn't exist
            create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
                """
            cursor.execute(create_table_query)

            # Insert user data
            print('3')
            insert_query = "INSERT INTO users (username, password) VALUES (?, ?);"
            print('4')
            cursor.execute(insert_query, (username, password))

            # Commit and close connection
            conn.commit()
            conn.close()

            conn = sqlite3.connect(f"src/assets/database/{username} Accounts.db")
            cursor = conn.cursor()
            # Create table if it doesn't exist
            create_table_query = """
                CREATE TABLE IF NOT EXISTS accounts (
                    App TEXT NOT NULL,
                    Username TEXT NOT NULL,
                    Password TEXT NOT NULL
                );
                """
            cursor.execute(create_table_query)
            conn.commit()
            conn.close()

            ErrorDialog(self.page, 'Success', 'User inserted successfully', on_close=lambda: self.page.go('/login'))
        except sqlite3.IntegrityError:
            ErrorDialog(self.page, 'Error', 'Username already exists')
        except Exception as e:
            ErrorDialog(self.page, 'Error', f"An unexpected error occurred: {e}")

class PasswordField(ft.Stack):
    def __init__(self):
        super().__init__()

        self.text_field = ft.TextField(
            width=210,
            border_width=0,
            text_size=18,
            password=True,
        )
        self.eye_button = ft.IconButton(
            ft.icons.REMOVE_RED_EYE,
            top=5,
            left=185,
            on_click=self.on_show
        )

        self.controls = [
            self.text_field,
            self.eye_button
        ]

    def on_show(self, event: ft.ControlEvent):
        self.text_field.password = not bool(self.text_field.password)
        if self.text_field.password:
            self.eye_button.icon = ft.icons.REMOVE_RED_EYE
        else:
            self.eye_button.icon = ft.icons.REMOVE_RED_EYE_OUTLINED
        self.update()

class ErrorDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, title: str | None = None, text: str | None = None, on_close: Any | None =None):
        super().__init__()
        self.page = page
        self.modal = True
        self.close = on_close

        self.title = ft.Text(
            value=title
        )

        self.content = ft.Text(
            value=text
        )

        self.actions = [
            ft.ElevatedButton(
                'Close',
                on_click=self.on_close
            )
        ]

        self.page.open(self)

    def on_close(self, event: ft.ControlEvent):
        self.page.close(self)
        if self.close:
            self.close()

def user_authentication(username, password):
    conn = sqlite3.connect("src/assets/database/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE Username = ? AND Password = ?
    """, (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

if __name__ == '__main__':
    ft.app(main)