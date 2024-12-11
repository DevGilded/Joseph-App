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
        self.current_selected = None
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
        self.search = FormOne('Search:', button_text='Delete', on_click=self.delete_account)

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
    
    def print_parent(self):
        print('printing... from parent')

    def delete_account(self, event: ft.ControlEvent):
        if not self.current_selected:
            return # return if there are no selected row
        
        VerifyDialog(self.page, 'Verify Password', 'Enter Password to Delete')

        # try:
        #     SelectItem = AccountsTreeView.selection()[0]  # Get the selected item
        #     AppName = AccountsTreeView.item(SelectItem, "values")[0]

        #     # Password verification popup
        #     def verify_and_delete():
        #         EnteredPassword = PasswordEntry.get()
        #         if validate_user(username, EnteredPassword):
        #             PassVerificationWindow.destroy()  # Close the verification window
        #             delete_account_from_db(user_db, AppName)  # Delete the account from the database
        #             messagebox.showinfo("Success", f"Account '{AppName}' deleted successfully!")
        #             load_accounts()  # Refresh the Treeview
        #         else:
        #             messagebox.showerror("Error", "Invalid Password.")

        #     # Create password verification window
        #     PassVerificationWindow = tk.Toplevel(root)
        #     PassVerificationWindow.title("Verify Password")
        #     PassVerificationWindow.configure(bg="black")
        #     PassVerificationWindow.geometry("300x150")

        #     tk.Label(PassVerificationWindow, text="Enter Password To Delete:", font=("Arial", 12, "bold"), fg="white",
        #              bg="black").pack(pady=10)
        #     PasswordEntry = tk.Entry(PassVerificationWindow, show="•")
        #     PasswordEntry.pack(pady=5)
        #     tk.Button(PassVerificationWindow, text="Verify and Delete", width=20, pady=3, bg="Black", fg="White",
        #               border=1, font=("Arial", 10), command=verify_and_delete).pack(pady=10)

        # except IndexError:
        #     messagebox.showerror("Error", "No account selected.")

    def load_accounts(self):
        self.table.rows = []

        for row in get_data(f'{self.admin} Accounts'):
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
            width=125,
            scale=1.2,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                alignment=ft.alignment.center
            ),
            on_click=on_click
        )

        self.controls = [
                self.label,
                self.field,
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

        self.content = ft.TextField(
            label=label
        )

        self.actions = [
            ft.ElevatedButton(
                text='Cancel', 
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=75,
                on_click=self.on_close
            ),
            ft.ElevatedButton(
                text='Verify', 
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                width=75,
                on_click=self.on_verify
            )
        ]

        self.page.open(self)

    def on_close(self, event: ft.ControlEvent):
        self.page.close(self)
        if self.close:
            self.close()

    def on_verify(self, event: ft.ControlEvent):
        self.page.close(self)
        if self.verify:
            self.verify()

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