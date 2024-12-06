import flet as ft
import main as m
import sqlite3
from typing import Any

def main(page: ft.Page, username: str):
    page.title = f"{username} InstaVault"
    page.window.icon = 'src/assets/Logo.png'
    page.window.width = 800
    page.window.height = 500
    page.window.maximizable = False
    page.window.resizable = False

    def route_change(route):
        page.views.clear()
        page.views.append(HomeView(page, username))

        match page.route:
            case '/option?': # if you want to create a new route inside the manager
                pass
            case _:
                pass

        page.update()

    def view_pop(view):
        try:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        except Exception as e:
            print(f'Something minor: {e}')

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go('/home')

class HomeView(ft.View):
    def __init__(self, page: ft.Page, username: str):
        super().__init__()
        self.page = page
        self.admin = username
        self.route = '/home'
        print(self.route)

        self.icon = ft.Container(
            ft.Image(
                'src/assets/images/InstaVaulta.png',
                width=300,
                height=300,
                expand=True,
                fit=ft.ImageFit.CONTAIN,
            ),
            top=-30,
            left=-10
        )

        self.app_name = FormOne('App Name:', button_text='Add', on_click=self.add_account)
        self.username = FormOne('Username:', button_text='Review Pass')
        self.password = FormOne('Password:', button_text='Update')
        self.search = FormOne('Search:', button_text='Delete')

        self.table = ft.DataTable(
            [
                ft.DataColumn(ft.Text('App')),
                ft.DataColumn(ft.Text('Username')),
                ft.DataColumn(ft.Text('Password')),
            ],
            width=800
        )

        self.controls = [
            ft.Column(
                [
                    ft.Stack(
                        [
                            self.icon,
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            self.app_name,
                                            self.username,
                                            self.password,
                                            self.search,
                                            ft.Row(
                                                [
                                                    ft.ElevatedButton(
                                                        'Clear',
                                                        width=100,
                                                        scale=1.2,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        ),
                                                        on_click=self.clear_field
                                                    ),
                                                    ft.ElevatedButton(
                                                        'Log Out',
                                                        width=100,
                                                        scale=1.2,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        ),
                                                        on_click=lambda e: m.main(self.page)
                                                    ),
                                                    ft.ElevatedButton(
                                                        'Change Password',
                                                        width=130,
                                                        scale=1.15,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        )
                                                    )
                                                ],
                                                alignment=ft.MainAxisAlignment.END,
                                                width=600,
                                                spacing=25
                                            )
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                left=150,
                            )
                        ],
                        expand=True,
                        width=800,
                        height=280
                    ),
                    ft.Card(
                        ft.Column(
                            [
                                self.table
                            ],
                        height=150,
                        scroll=ft.ScrollMode.ALWAYS
                        ),
                        height=150
                    )
                ]
            )
        ]
        
        self.load_accounts()

    def clear_field(self, event: ft.ControlEvent):
        self.app_name.field.value = ''
        self.username.field.value = ''
        self.password.field.value = ''
        self.search.field.value = ''
        self.update()

    def add_account(self, event: ft.ControlEvent):
        appname = self.app_name.field.value
        username = self.username.field.value
        password = self.password.field.value
        if appname and username and password:
            insert_account(f'{self.admin} Accounts', appname, username, password)
            m.ErrorDialog(self.page, "Success", "Account added successfully!")
            self.clear_field(event)
            self.load_accounts()
        else:
            m.ErrorDialog(self.page, 'Error', 'App Name, Username, Password are required')

    def load_accounts(self):
        self.table.rows = []

        for row in get_data(f'{self.admin} Accounts'):
            self.table.rows.append(TableRow(row[0], row[1], row[2]))
        self.page.update()


class TableRow(ft.DataRow):
    def __init__(self, appname: str, username: str, password: str):
    
        self.cells = [
            ft.DataCell(ft.Text(appname)),
            ft.DataCell(ft.Text(username)),
            ft.DataCell(ft.Text(password)),
        ]

        super().__init__(self.cells)


class FormOne(ft.Row):
    def __init__(self, label: str, button_text: str | None = None, on_click: Any | None = None):
        super().__init__()

        self.spacing = 20
        self.alignment = ft.MainAxisAlignment.END
        self.width = 600

        self.label = ft.Text(
            label,
            scale=1.2,
            weight=ft.FontWeight.BOLD,
        )

        self.field = ft.TextField(
            bgcolor='white',
            color='black',
            width=250,
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            border_width=0
        )

        self.button = ft.ElevatedButton(
            button_text if button_text else 'BUTTON',
            width=100,
            scale=1.2,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=on_click
        )

        self.controls = [
                self.label,
                self.field,
                self.button
        ]

def insert_account(user_db, AppName, username, password):
    conn = sqlite3.connect(f"src/assets/database/{user_db}.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO accounts (App, Username, Password)
        VALUES (?, ?, ?)
    """, (AppName, username, password))
    conn.commit()
    conn.close()

def get_data(user_db):
    conn = sqlite3.connect(f"src/assets/database/{user_db}.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    data = cursor.fetchall()


    conn.commit()
    conn.close()

    return data