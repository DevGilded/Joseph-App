import flet as ft
import main as m
import sqlite3
from typing import Any

def main(page: ft.Page, username: str, password: str):
    page.title = f"{username} InstaVault"
    page.window.icon = 'src/assets/Logo.png'
    page.window.width = 800
    page.window.height = 500
    page.window.maximizable = False
    page.window.resizable = False

    def route_change(route):
        page.views.clear()
        page.views.append(HomeView(page, username, password))

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
    def __init__(self, page: ft.Page, username: str, password: str):
        super().__init__()
        self.page = page
        self.current_selected: TableRow | None = None
        self.admin = username
        self.admin_pass = password
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
        self.username = FormOne('Username:', button_text='Review Pass', on_click=self.view_account_password)
        self.password = FormOne('Password:', button_text='Update', on_click=self.update_account, can_reveal_password=True)
        self.search = FormOne('Search:', button_text='Delete', on_click=self.delete_account,
                              on_change=self.load_accounts)

        self.table = ft.DataTable(
            [
                ft.DataColumn(ft.Text('App')),
                ft.DataColumn(ft.Text('Username')),
                ft.DataColumn(ft.Text('Password')),
            ],
            width=800,
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
                                                        height=45,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        ),
                                                        on_click=self.clear_field
                                                    ),
                                                    ft.ElevatedButton(
                                                        'Log Out',
                                                        width=100,
                                                        scale=1.2,
                                                        height=45,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        ),
                                                        on_click=lambda e: m.main(self.page)
                                                    ),
                                                    ft.ElevatedButton(
                                                        'Change Password',
                                                        width=175,
                                                        scale=1.2,
                                                        height=45,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=5)
                                                        ),
                                                        on_click=self.change_account_password
                                                    )
                                                ],
                                                alignment=ft.MainAxisAlignment.END,
                                                width=600,
                                                spacing=30
                                            )
                                        ],
                                        spacing=12
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                left=150,
                            )
                        ],
                        expand=True,
                        width=800,
                        height=285
                    ),
                    ft.Card(
                        ft.Column(
                            [
                                self.table
                            ],
                            height=145,
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        height=145
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
            self.page.snack_bar = ft.SnackBar(ft.Text('Account added successfully!', color='green'))
            self.page.snack_bar.open = True
            self.page.update()
            self.clear_field(event)
            self.load_accounts()
        else:
            m.ErrorDialog(self.page, 'Error', 'App Name, Username, Password are required')
    
    def view_account_password(self, event: ft.ControlEvent):
        if not self.current_selected:
            return # return if there are no selected row

        def verify_check(textfield):
            if self.admin_pass == textfield.value:
                m.ErrorDialog(self.page, 'Success',f'Password: {self.current_selected.password.value}')
                self.load_accounts()
            else:
                m.ErrorDialog(self.page, 'Error', 'Invalid Password')

        VerifyDialog(self.page, 'Verify Password', 'Enter Password to Delete', on_verify=verify_check)

    def update_account(self, event: ft.ControlEvent):
        if not self.current_selected:
            return # return if there are no selected row

        def verify_check(textfield):
            if self.admin_pass == textfield.value:
                UpdateAccountDialog(self.page, self.admin, self.current_selected.app_name.value, on_save=self.load_accounts)
            else:
                m.ErrorDialog(self.page, 'Error', 'Invalid Password')

        VerifyDialog(self.page, 'Verify Password', 'Enter Password to Delete', on_verify=verify_check)

    def delete_account(self, event: ft.ControlEvent):
        if not self.current_selected:
            return # return if there are no selected row

        appname = self.current_selected.app_name.value
        username = self.current_selected.username.value
        password = self.current_selected.password.value

        def verify_check(textfield):
            if self.admin_pass == textfield.value:
                delete_account_from_db(self.admin, appname, username, password)
                self.page.snack_bar = ft.SnackBar(ft.Text('deleted successfully!', color='green'))
                self.page.snack_bar.open = True
                self.page.update()
                self.load_accounts()
            else:
                m.ErrorDialog(self.page, 'Error', 'Invalid Password')

        VerifyDialog(self.page, 'Verify Password', 'Enter Password to Delete', on_verify=verify_check)

    def change_account_password(self, event: ft.ControlEvent):
        if not self.current_selected:
            return # return if there are no selected row

        ChangAccountPassDialog(self.page, self.admin, self.load_accounts)

    def load_accounts(self, search_query: ft.ControlEvent | None = None):
        self.table.rows = []

        accounts = get_data(f'{self.admin} Accounts')
        if search_query:
            accounts = [account for account in accounts if search_query.control.value.lower() in account[0].lower()]

        for row in accounts:
            self.table.rows.append(TableRow(row[0], row[1], row[2], self.on_row_select))
        self.page.update()

    def on_row_select(self, event: ft.OptionalEventCallable):
        self.current_selected = event.control
        for row in self.table.rows:
            row.selected = False

        self.current_selected.selected = True
        self.update()

class TableRow(ft.DataRow):
    def __init__(self, appname: str, username: str, password: str, on_select: Any):
        self.app_name = ft.Text(appname)
        self.username = ft.Text(username)
        self.password = ft.TextField(password, read_only=True, border_width=0, selection_color=ft.colors.TRANSPARENT, password=True)

        self.cells = [
            ft.DataCell(self.app_name),
            ft.DataCell(self.username),
            ft.DataCell(self.password),
        ]

        super().__init__(self.cells, on_select_changed=on_select)

class FormOne(ft.Row):
    def __init__(self, label: str, button_text: str | None = None, on_click: Any | None = None, on_change: Any | None = None,
                 can_reveal_password: bool = False):
        super().__init__()

        self.spacing = 20
        self.alignment = ft.MainAxisAlignment.END
        self.width = 600
        self.run_spacing = 10
        self.changes = on_change

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
            border_width=0,
            height=48,
            password=can_reveal_password,
            on_change=self.changes
        )
        self.field_eye = ft.IconButton(ft.icons.REMOVE_RED_EYE, icon_color='black',
                                       on_click=lambda e: toggle_password(e, self.field, self.field_eye))

        self.button = ft.ElevatedButton(
            button_text if button_text else 'BUTTON',
            width=125,
            scale=1.2,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                alignment=ft.alignment.center
            ),
            height=48,
            on_click=on_click
        )

        self.controls = [
                self.label,
                (self.field if not can_reveal_password else ft.Stack(
                    [
                        self.field,
                        ft.Container(
                            self.field_eye,
                            right=2,
                            top=4,
                        )
                    ]
                )),
                self.button
        ]

class VerifyDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, title: str | None = None, label: str | None = None, 
                 on_close: Any | None = None, on_verify: Any | None = None):
        super().__init__()
        self.page = page
        self.modal = True
        self.close = on_close
        self.verify = on_verify

        self.title = ft.Text(
            value=title
        )

        self.TextField = ft.TextField(
            label=label,
            password=True,
        )
        self.eye_button = ft.IconButton(ft.icons.REMOVE_RED_EYE, on_click=lambda e: toggle_password(e, self.TextField, self.eye_button))
        self.content = ft.Stack(
            [
                self.TextField,
                ft.Container(
                    self.eye_button,
                    right=2,
                    top=4,
                )
            ]
        )

        self.actions = [
            ft.ElevatedButton(
                text='Cancel', 
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=100,
                on_click=self.on_close
            ),
            ft.ElevatedButton(
                text='Verify', 
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=100,
                on_click=self.on_verify
            )
        ]

        self.page.open(self)

    def on_close(self, event: ft.ControlEvent):
        self.page.close(self)
        if self.close:
            self.close()

    def on_verify(self, event: ft.ControlEvent):
        if self.verify:
            self.verify(self.TextField)
        self.page.close(self)

class UpdateAccountDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, user_db: str, app_name: str | None = None, on_save: Any | None = None):
        super().__init__()
        self.page = page
        self.modal = True
        self.user_db = user_db
        self.app_name = app_name
        self.save = on_save

        self.new_username = ft.TextField(
            label = 'New Username (Optional)'
        )
        self.new_password = ft.TextField(
            label = 'New Password (Optional)',
            password = True
        )
        self.new_password_eye = ft.IconButton(ft.icons.REMOVE_RED_EYE,
                                              on_click=lambda e: toggle_password(e, self.new_password, self.new_password_eye))

        self.title = ft.Text(
            value=f'Updating Account: {app_name.title()}'
        )

        self.content = ft.Column(
            [
                self.new_username,
                ft.Stack(
                    [
                        self.new_password,
                        ft.Container(
                            self.new_password_eye,
                            right=2,
                            top=4,
                        )
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            height=100
        )

        self.actions = [
            ft.ElevatedButton(
                text='Discard',
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=120,
                on_click=lambda e: self.page.close(self)
            ),
            ft.ElevatedButton(
                text='Save Changes',
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=150,
                on_click=self.on_save
            )
        ]

        self.page.open(self)

    def on_save(self, event: ft.ControlEvent):
        conn = sqlite3.connect(f"src/assets/database/{self.user_db} Accounts.db")
        cursor = conn.cursor()

        if self.new_username.value:
            cursor.execute(
                "UPDATE accounts SET Username = ? WHERE App = ?",
                (self.new_username.value, self.app_name)
            )

        if self.new_password.value:
            cursor.execute(
                "UPDATE accounts SET Password = ? WHERE App = ?",
                (self.new_password.value, self.app_name)
            )

        conn.commit()
        conn.close()

        self.page.snack_bar = ft.SnackBar(ft.Text('Account successfully changed!', color='green'))
        self.page.snack_bar.open = True
        self.page.update()
        if self.save:
            self.save()
        self.page.close(self)

class ChangAccountPassDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, user_db: str, on_change: Any | None = None):
        super().__init__()
        self.page = page
        self.modal = True
        self.user_db = user_db
        self.change = on_change

        self.old_password = ft.TextField(
            label = 'Enter Current Password',
            password = True
        )
        self.old_password_eye = ft.IconButton(ft.icons.REMOVE_RED_EYE,
                                              on_click=lambda e: toggle_password(e, self.old_password, self.old_password_eye))
        self.new_password = ft.TextField(
            label = 'Enter New Password',
            password = True
        )
        self.new_password_eye = ft.IconButton(ft.icons.REMOVE_RED_EYE,
                                              on_click=lambda e: toggle_password(e, self.new_password, self.new_password_eye))
        self.confirmation_password = ft.TextField(
            label = 'Confirm New Password',
            password = True
        )
        self.confirmation_password_eye = ft.IconButton(ft.icons.REMOVE_RED_EYE,
                                              on_click=lambda e: toggle_password(e, self.confirmation_password, self.confirmation_password_eye))

        self.title = ft.Text(
            value='Change Passwor'
        )

        self.content = ft.Column(
            [
                ft.Stack(
                    [
                        self.old_password,
                        ft.Container(
                            self.old_password_eye,
                            right=2,
                            top=4,
                        )
                    ]
                ),
                ft.Stack(
                    [
                        self.new_password,
                        ft.Container(
                            self.new_password_eye,
                            right=2,
                            top=4,
                        )
                    ]
                ),
                ft.Stack(
                    [
                        self.confirmation_password,
                        ft.Container(
                            self.confirmation_password_eye,
                            right=2,
                            top=4,
                        )
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            height=150
        )

        self.actions = [
            ft.ElevatedButton(
                text='Cancel',
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=100,
                on_click=lambda e: self.page.close(self)
            ),
            ft.ElevatedButton(
                text='Change Password',
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=175,
                on_click=self.on_change
            )
        ]

        self.page.open(self)

    def reset_textfield(self):
        self.old_password.value = ''
        self.new_password.value = ''
        self.confirmation_password.value = ''

    def on_change(self, event: ft.ControlEvent):
        conn = sqlite3.connect(f"src/assets/database/{self.user_db} Accounts.db")
        cursor = conn.cursor()

        # help in this part
        cursor.execute("SELECT password FROM accounts WHERE password = ?", (self.old_password.value,))
        stored_password = cursor.fetchone()

        if not stored_password:
            # Old password doesn't match any record
            self.page.snack_bar = ft.SnackBar(ft.Text('Invalid Old Password'))
            self.page.snack_bar.open = True
            self.reset_textfield()
            self.page.update()
            conn.close()
            return

        if self.new_password.value != self.confirmation_password.value:
            # New passwords do not match
            self.page.snack_bar = ft.SnackBar(ft.Text('New password and confirmation password do not match.'))
            self.page.snack_bar.open = True
            self.reset_textfield()
            self.page.update()
            conn.close()
            return

        cursor.execute(
            "UPDATE accounts SET password = ? WHERE password = ?",
            (self.new_password.value, self.old_password.value)
        )

        conn.commit()
        conn.close()

        self.page.snack_bar = ft.SnackBar(ft.Text('Password successfully changed!', color='green'))
        self.page.snack_bar.open = True
        self.page.update()
        if self.change:
            self.change()
        self.page.close(self)

def toggle_password(event: ft.ControlEvent, text_field: ft.TextField, eye_button: ft.IconButton):
    text_field.password = not bool(text_field.password)
    if text_field.password:
        eye_button.icon = ft.icons.REMOVE_RED_EYE
    else:
        eye_button.icon = ft.icons.REMOVE_RED_EYE_OUTLINED
    text_field.update()
    eye_button.update()

def insert_account(user_db, AppName, username, password):
    conn = sqlite3.connect(f"src/assets/database/{user_db}.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO accounts (App, Username, Password)
        VALUES (?, ?, ?)
    """, (AppName, username, password))
    conn.commit()
    conn.close()

def delete_account_from_db(user_db, AppName, username, password):
    conn = sqlite3.connect(f"src/assets/database/{user_db} Accounts.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE App = ? AND Username = ? AND Password = ?", (AppName, username, password))
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