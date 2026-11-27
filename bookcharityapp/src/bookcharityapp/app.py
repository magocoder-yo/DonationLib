import toga # pyright: ignore[reportMissingImports]
import requests
from toga.style.pack import COLUMN, ROW # pyright: ignore[reportMissingImports]
from toga.colors import rgb # pyright: ignore[reportMissingImports]
import json

from pathlib import Path

SERVER_URL = "donationlib-production.up.railway.app"

class BookCharityApp(toga.App):
    def startup(self):
        self.main_box = toga.Box(direction=COLUMN)

        self.load_user_login()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def load_user_login(self):
        self.main_box.clear()

        #Page setup
        user_login_page = toga.Box(vertical_align_items="center", direction=ROW, background_color=rgb(20, 150, 20), flex=1)
        left_empty_box = toga.Box(flex=0.2)
        self.user_login_box = toga.Box(horizontal_align_items="center", direction=COLUMN, flex=0.6)
        right_empty_box = toga.Box(flex=0.2)
        user_login_page.add(left_empty_box)
        user_login_page.add(self.user_login_box)
        user_login_page.add(right_empty_box)

        #User Login Label
        user_login_label_main = toga.Label("User Login", color=rgb(255, 255, 255), align_items="center", text_align="center", font_size=20, font_weight="bold", margin=(10,0))

        #User credential input (User ID)
        user_login_id_box = toga.Box(direction=ROW, margin=(5,0))
        user_login_id_label = toga.Label("User ID:", font_size=12, color=rgb(255, 255, 255))
        self.user_login_id_input = toga.TextInput(flex=1, margin=(0,5), font_size=12)
        user_login_id_box.add(user_login_id_label)
        user_login_id_box.add(self.user_login_id_input)

        #User credential input (User Pwd)
        user_login_pw_box = toga.Box(direction=ROW, margin=(5,0))
        user_login_pw_label = toga.Label("Password:", font_size=12, color=rgb(255, 255, 255))
        self.user_login_pw_input = toga.PasswordInput(flex=1, margin=(0,5), font_size=12)
        user_login_pw_box.add(user_login_pw_label)
        user_login_pw_box.add(self.user_login_pw_input)

        #User Login Button
        user_login_button = toga.Button("Confirm", on_press=self.verify_user, background_color=rgb(100, 100, 250), color=rgb(255, 255, 255), align_items="center", text_align="center", font_size=15, font_weight="bold", margin=(10,0))

        #Create Account Button
        create_account_button = toga.Button("Create an Account", on_press=self.create_account, background_color=rgb(220, 220, 220), align_items="center", text_align="center")

        self.user_login_box.add(user_login_label_main)
        self.user_login_box.add(user_login_id_box)
        self.user_login_box.add(user_login_pw_box)
        self.user_login_box.add(user_login_button)
        self.user_login_box.add(create_account_button)

        self.main_box.add(user_login_page)

    def load_main_page_template(self):
        userID = int(self.user_login_id_input.value)
        
        self.main_box.clear()

        self.title_bar = toga.Box(direction=ROW, background_color=rgb(20, 20, 150), height=24, align_items="start")

        self.main_page_box = toga.Box(direction=COLUMN, flex=1, background_color=rgb(255, 255, 255))

        self.home_page_instance = HomePage(userID, self.main_page_box, self)
        self.library_page_instance = LibraryPage(userID, self.main_page_box, self)
        self.map_page_instance = MapPage(userID, self.main_page_box, self)
        self.account_page_instance = AccountPage(userID, self.main_page_box, self)

        self.bottom_bar = toga.Box(direction=ROW, background_color=rgb(255, 255, 255), height=32)
        self.home_button = toga.Button(icon=toga.Icon("res/icons/home"), on_press=self.home_page_instance.load_page, flex=0.25, height=32)
        self.library_button = toga.Button(icon=toga.Icon("res/icons/book"), on_press=self.library_page_instance.load_page, flex=0.25, height=32)
        self.map_button = toga.Button(icon=toga.Icon("res/icons/map"), on_press=self.map_page_instance.load_page, flex=0.25, height=32)
        self.account_button = toga.Button(icon=toga.Icon("res/icons/user"), on_press=self.account_page_instance.load_page, flex=0.25, height=32)

        self.bottom_bar.add(self.home_button)
        self.bottom_bar.add(self.library_button)
        self.bottom_bar.add(self.map_button)
        self.bottom_bar.add(self.account_button)

        self.main_box.add(self.title_bar)
        self.main_box.add(self.main_page_box)
        self.main_box.add(self.bottom_bar)

        self.library_page_instance.load_page(None)

    async def verify_user(self, widget):
        try:
            userID = int(self.user_login_id_input.value)
        except ValueError:
            await self.main_window.dialog(
                toga.InfoDialog("Bad Input", "The User ID provided is not a number, please enter a valid user ID!")
            )
            return
        
        userPW = str(self.user_login_pw_input.value)

        if len(userPW) == 0:
            await self.main_window.dialog(
                toga.InfoDialog("Bad Input", "No password was provided, please enter a password!")
            )
            return
        
        params = {'userid': userID, 'password': userPW}

        response = requests.post(f"http://{SERVER_URL}/authuser", params=params)

        if response.status_code == 401:
            #Invalid credentials
            await self.main_window.dialog(
                toga.InfoDialog("Incorrect Credentials", "The following credentials failed, please check the entered values and try again!")
            )
        elif response.status_code == 500:
            #Server Error
            await self.main_window.dialog(
                toga.InfoDialog("Server Error", "The server had some issues, please try again later!")
            )
        elif response.status_code == 200:
            #Success
            self.load_main_page_template()
        else:
            #Some error/unexpected result
            await self.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unexpected error/result occurred, please try again later!")
            )

    async def create_account(self, widget):
        self.main_box.clear()

        self.title_label = toga.Label("User Creation", font_weight="bold", font_size=23, align_items="center", text_align="center", margin=(10,10))
        self.main_box.add(self.title_label)

        #Account name box
        self.account_name_box = toga.Box(direction=ROW, margin=(10,10))
        self.account_name_label = toga.Label("Please enter your name:")
        self.account_name_input = toga.TextInput()
        self.account_name_box.add(self.account_name_label)
        self.account_name_box.add(self.account_name_input)

        #Account grade level box
        self.account_grade_level_box = toga.Box(direction=ROW, margin=(10,10))
        self.account_grade_level_label = toga.Label("Please enter your grade level:")
        self.account_grade_level_input = toga.TextInput()
        self.account_grade_level_box.add(self.account_grade_level_label)
        self.account_grade_level_box.add(self.account_grade_level_input)

        #Account school box
        self.account_school_box = toga.Box(direction=ROW, margin=(10,10))
        self.account_school_label = toga.Label("Please enter your school (with capitalization and in full form):")
        self.account_school_input = toga.TextInput()
        self.account_school_box.add(self.account_school_label)
        self.account_school_box.add(self.account_school_input)

        #Account city box
        self.account_city_box = toga.Box(direction=ROW, margin=(10,10))
        self.account_city_label = toga.Label("Please enter your city (with capitalization and in full form):")
        self.account_city_input = toga.TextInput()
        self.account_city_box.add(self.account_city_label)
        self.account_city_box.add(self.account_city_input)

        #Account password box
        self.account_pw_box = toga.Box(direction=ROW, margin=(10,10))
        self.account_pw_label = toga.Label("Please enter your password (ensure it is strong):")
        self.account_pw_input = toga.PasswordInput()
        self.account_pw_box.add(self.account_pw_label)
        self.account_pw_box.add(self.account_pw_input)

        #Add all to main box
        self.main_box.add(self.account_name_box)
        self.main_box.add(self.account_grade_level_box)
        self.main_box.add(self.account_school_box)
        self.main_box.add(self.account_city_box)
        self.main_box.add(self.account_pw_box)

        self.confirm_create_account_button = toga.Button("Create Account", on_press=self.confirm_create_account, align_items="center", text_align="center")
        self.main_box.add(self.confirm_create_account_button)

    async def confirm_create_account(self, widget):
        request_params = {}
        request_params["name"] = self.account_name_input.value
        request_params["grade_level"] = self.account_grade_level_input.value
        request_params["school"] = self.account_school_input.value
        request_params["city"] = self.account_city_input.value
        request_params["password"] = self.account_pw_input.value

        response = requests.post(f"http://{SERVER_URL}/adduser", params=request_params)

        if response.status_code == 201:
            result = response.json()
            user_id = result["user_id"]
            await self.main_window.dialog(
                toga.InfoDialog("Account Creation Successful", f"Congratulations, you successfully created an account! IMPORTANT: You will log in using your user ID, which is the following: {user_id}")
            )
            self.load_user_login()

class HomePage:
    def __init__(self, userID, main_page_box, app):
        self.userID = userID
        self.main_page_box = main_page_box
        self.app = app

    def load_page(self, widget):
        self.main_page_box.clear()

        label = toga.Label("The home page is under construction.", flex=1, font_weight="bold")
        self.main_page_box.add(label)

class LibraryPage:
    def __init__(self, userID, main_page_box, app):
        self.userID = userID
        self.main_page_box = main_page_box
        self.app = app

        self.book_container = toga.Box(direction=COLUMN, flex=0.85, background_color=rgb(255, 255, 255))
        self.book_container_scroll = toga.ScrollContainer(horizontal=False, flex=1, content=self.book_container)

    def load_page(self, widget):
        self.main_page_box.clear()

        self.user_info = requests.get(f"http://{SERVER_URL}/user/{self.userID}").json()

        lib_header = toga.Label("Your books:", font_weight="bold", text_align="center", font_size=23)
        self.main_page_box.add(lib_header)

        self.main_page_box.add(self.book_container_scroll)

        add_button_box = toga.Box(background_color=rgb(0,0,0))
        add_button = toga.Button("Add a book", on_press=self.add_book, flex=1)
        add_button_box.add(add_button)
        self.main_page_box.add(add_button_box)

        self.show_books_from_cache()

    def show_books_from_cache(self):
        self.book_container.clear()
        book_cache_path = Path(__file__).parent / "res/cache_data/book_cache.json"
        
        book_cache_path.touch()

        response = requests.get(f"http://{SERVER_URL}/user/{self.userID}/books").json()

        with open(book_cache_path, "w") as f:
            f.write(json.dumps(response))

        with open(book_cache_path, "r") as f:
            book_data = json.loads(f.read())

        for book in book_data:
            self.book_container.add(Book(book, self))

    def add_book(self, widget):
        self.main_page_box.clear()

        header = toga.Label("Please enter book details:", font_weight="bold", text_align="left", font_size=23)
        self.main_page_box.add(header)

        name_box = toga.Box(direction=COLUMN, margin=(5,10))
        name_label = toga.Label("Book Name:", font_weight="bold")
        self.name_input = toga.TextInput()
        name_box.add(name_label)
        name_box.add(self.name_input)
        self.main_page_box.add(name_box)

        grade_box = toga.Box(direction=COLUMN, margin=(5,10))
        grade_label = toga.Label("Grade Level:", font_weight="bold")
        self.grade_input = toga.TextInput()
        grade_box.add(grade_label)
        grade_box.add(self.grade_input)
        self.main_page_box.add(grade_box)

        edition_box = toga.Box(direction=COLUMN, margin=(5,10))
        edition_label = toga.Label("Edition:", font_weight="bold")
        self.edition_input = toga.TextInput()
        edition_box.add(edition_label)
        edition_box.add(self.edition_input)
        self.main_page_box.add(edition_box)

        status_box = toga.Box(direction=COLUMN, margin=(5,10))
        status_label = toga.Label("Status:", font_weight="bold")
        self.status_input = toga.Selection(items=[{'formal_name': 'In Possesion', 'name': 'owned'}, {'formal_name': 'Desired', 'name': 'wanted'}], accessor='formal_name')
        status_box.add(status_label)
        status_box.add(self.status_input)
        self.main_page_box.add(status_box)

        confirm_button = toga.Button("Confirm", on_press=self.confirm_add_book)

        self.main_page_box.add(confirm_button)

    async def confirm_add_book(self, widget):
        try:
            self.grade_level = int(self.grade_input.value)
            self.edition = int(self.edition_input.value)
        except ValueError:
            #Invalid input, show error dialog
            await self.app.main_window.dialog(
                toga.InfoDialog("Bad Input", "The grade level and edition must be numbers, please enter valid values!")
            )
            return
        
        params = {'name': self.name_input.value, 'grade_level': self.grade_level, 'edition': self.edition, 'status': self.status_input.value.name}

        response = requests.post(f"http://{SERVER_URL}/user/{self.userID}/addbook", params=params)

        if response.status_code == 201:
            #Success
            await self.app.main_window.dialog(
                toga.InfoDialog("Success", "The book was successfully added to your library!")
            )
            self.load_page(None)
        else:
            #Some error/unexpected result
            await self.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unexpected error/result occurred, please try again later!")
            )

        self.name_input.value = ""
        self.grade_input.value = ""
        self.edition_input.value = ""
        self.status_input.value = self.status_input.items[0]

class Book(toga.Box):
    def __init__(self, book_data, parent):
        super().__init__(direction=ROW, background_color=rgb(240, 240, 240), margin=(5,2))

        self.book_data = book_data
        self.parent_instance = parent

        info_box = toga.Box(direction=COLUMN, margin=(5, 5), flex=0.7)
        button_box = toga.Box(direction=COLUMN, margin=(5,5), flex=0.3)
        name_label = toga.Label(book_data['name'], font_weight="bold", font_size=15)
        info_box.add(name_label)

        #Additional Info in info_box
        additional_info = toga.Box(direction=ROW)
        grade_level_label = toga.Label(f"Grade Level: {str(book_data['grade_level'])}", flex=0.5, font_weight="bold")
        edition_label = toga.Label(f"Edition: {str(book_data['edition'])}", flex=0.5, font_weight="bold")
        additional_info.add(grade_level_label)
        additional_info.add(edition_label)
        info_box.add(additional_info)

        #Status Info in info_box
        status_box = toga.Box(direction=ROW)
        status_static_label = toga.Label("Book's Status:", font_weight="bold")
        if book_data['status'] == "owned":
            status_label = toga.Label("In Possession", color=rgb(20, 100, 20), flex=1, font_weight="bold")
        elif book_data['status'] == "wanted":
            status_label = toga.Label("Requested", color=rgb(100, 20, 20), flex=1, font_weight="bold")
        elif book_data['status'] == "fulfilling":
            status_label = toga.Label(f"Promised to {book_data["pledged_school"]}, not yet fulfilled", color=rgb(100, 100, 20), flex=1, font_weight="bold")
        elif book_data['status'] == "in fulfillment":
            status_label = toga.Label("Donation pledged, not yet delivered", color=rgb(100, 100, 20), flex=1, font_weight="bold")
        elif book_data['status'] == "donated":
            status_label = toga.Label("Donation made!", color=rgb(20, 100, 20), flex=1, font_weight="bold")
        elif book_data['status'] == "delivered":
            status_label = toga.Label("The donator has delivered the book!", color=rgb(50, 100, 20), flex=1, font_weight="bold")
        else:
            status_label = toga.Label("Other", color=rgb(30, 30, 30), flex=1, font_weight="bold")
        status_box.add(status_static_label)
        status_box.add(status_label)
        info_box.add(status_box)

        #Buttons in button_box
        if book_data['status'] == "owned":
            donate_button = toga.Button("Donate", on_press=self.donate_book, flex=1)
            remove_button = toga.Button("Remove this book from your library", on_press=self.remove_book, flex=1)
            button_box.add(donate_button)
            button_box.add(remove_button)
        elif book_data['status'] == "wanted":
            remove_button = toga.Button("Remove this book from your library", on_press=self.remove_book, flex=1)
            button_box.add(remove_button)
        elif book_data['status'] == "fulfilling":
            deliver_button = toga.Button("Mark as delivered", on_press=self.deliver_book, flex=1)
            button_box.add(deliver_button)
        elif book_data['status'] == "donated":
            remove_button = toga.Button("Remove this book from your library", on_press=self.remove_book, flex=1)
            button_box.add(remove_button)
        elif book_data['status'] == "delivered":
            confirm_delivery_button = toga.Button("Confirm delivery", on_press=self.confirm_delivery, flex=1)
            button_box.add(confirm_delivery_button)

        self.add(info_box)
        self.add(button_box)

    async def donate_book(self, widget):
        user_info = self.parent_instance.user_info

        if self.book_data['edition'] == 1:
            response = requests.get(f"http://{SERVER_URL}/{user_info['city']}/find_match/{self.book_data['name']}")
        else:
            response = requests.get(f"http://{SERVER_URL}/{user_info['city']}/find_match/{self.book_data['name']}/edition/{self.book_data['edition']}")

        if response.status_code != 200:
            await self.parent_instance.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unknown error occured.")
            )
            return

        self.parent_instance.main_page_box.clear()

        self.candidate_donation_schools = response.json()

        self.schools_box = toga.Box(direction=COLUMN, flex=1, background_color=rgb(255, 255, 255))
        self.schools_box_scroll = toga.ScrollContainer(horizontal=False, flex=1, content=self.schools_box)

        if len(self.candidate_donation_schools) == 0:
            empty_label = toga.Label("There is currently no location to donate this book in your city. Feel free to try again in a few days.", text_align="center", flex=1)
            self.parent_instance.main_page_box.add(empty_label)
        else:
            for school_name, school_num in self.candidate_donation_schools.items():
                school_box = toga.Box(direction=ROW, background_color=rgb(240, 240, 240), margin=(5,2))
                school_info_box = toga.Box(direction=COLUMN, flex=0.7)
                school_button_box = toga.Box(flex=0.3)
                school_name_label = toga.Label(f"School Name: {school_name}", font_weight="bold", font_size=15)
                school_num_label = toga.Label(f"Number of students who need this book: {str(school_num)}")
                school_pledge_button = toga.Button(f"Pledge donation to {school_name}", on_press=self.pledge_book, flex=1)

                school_info_box.add(school_name_label)
                school_info_box.add(school_num_label)
                school_button_box.add(school_pledge_button)
                school_box.add(school_info_box)
                school_box.add(school_button_box)
                self.schools_box.add(school_box)

        self.parent_instance.main_page_box.add(self.schools_box_scroll)
        return_button = toga.Button("Return to Library", on_press=self.parent_instance.load_page, text_align="center", align_items="center", margin=(10,5))
        self.parent_instance.main_page_box.add(return_button)

    async def pledge_book(self, widget):
        user_info = self.parent_instance.user_info
        target_school = widget.text[19:]
        
        if self.book_data['edition'] == 1:
            response = requests.get(f"http://{SERVER_URL}/from/{self.parent_instance.userID}/to/{target_school}/pledge/{self.book_data['name']}")
        else:
            response = requests.get(f"http://{SERVER_URL}/from/{self.parent_instance.userID}/to/{target_school}/pledge/{self.book_data['name']}/edition/{self.book_data['edition']}")

        if response.status_code != 200:
            await self.parent_instance.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unknown error occured.")
            )
            return

        await self.parent_instance.app.main_window.dialog(
            toga.InfoDialog("Congratulations!", "The book has successfully been pledged!")
        )
        self.parent_instance.load_page(None)
        return

    async def remove_book(self, widget):
        user_ID = self.parent_instance.userID
        book_ID = self.book_data['id']

        response = requests.post(f"http://{SERVER_URL}/user/{user_ID}/removebook/{book_ID}")

        if response.status_code != 200:
            await self.parent_instance.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unknown error occured.")
            )
            return

        await self.parent_instance.app.main_window.dialog(
            toga.InfoDialog("Congratulations!", "The book has been successfully removed from your library.")
        )
        self.parent_instance.load_page(None)
        return

    async def deliver_book(self, widget):
        book_ID = self.book_data['id']

        response = requests.post(f"http://{SERVER_URL}/deliver_book/{book_ID}")

        if response.status_code != 200:
            await self.parent_instance.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unknown error occured.")
            )
            return
        
        await self.parent_instance.app.main_window.dialog(
            toga.InfoDialog("Congratulations!", "The book was successfully marked as delivered.")
        )
        self.parent_instance.load_page(None)
        return

    async def confirm_delivery(self, widget):
        book_ID = self.book_data['id']

        response = requests.post(f"http://{SERVER_URL}/confirm_delivery/{book_ID}")

        if response.status_code != 200:
            await self.parent_instance.app.main_window.dialog(
                toga.InfoDialog("Unknown Error", "An unknown error occured.")
            )
            return
        
        await self.parent_instance.app.main_window.dialog(
            toga.InfoDialog("Congratulations!", "The book is officially in your possession.")
        )
        self.parent_instance.load_page(None)
        return

class MapPage:
    def __init__(self, userID, main_page_box, app):
        self.userID = userID
        self.main_page_box = main_page_box
        self.app = app

    def load_page(self, widget):
        self.main_page_box.clear()

        label = toga.Label("The map page is under construction.")
        self.main_page_box.add(label)

class AccountPage:
    def __init__(self, userID, main_page_box, app):
        self.userID = userID
        self.main_page_box = main_page_box
        self.app = app

    def load_page(self, widget):
        self.main_page_box.clear()

        response = requests.get(f"http://{SERVER_URL}/user/{self.userID}").json()

        label = toga.Label("Account Information", font_weight="bold", text_align="center", font_size=23)
        self.main_page_box.add(label)

        name_box = toga.Box(direction=ROW, margin=(5,10))
        name_label = toga.Label("User Name:", font_weight="bold")
        name_value = toga.Label(response['name'])
        name_box.add(name_label)
        name_box.add(name_value)
        self.main_page_box.add(name_box)

        grade_box = toga.Box(direction=ROW, margin=(5,10))
        grade_label = toga.Label("Grade Level:", font_weight="bold")
        grade_value = toga.Label(str(response['grade_level']))
        grade_box.add(grade_label)
        grade_box.add(grade_value)
        self.main_page_box.add(grade_box)

        school_box = toga.Box(direction=ROW, margin=(5,10))
        school_label = toga.Label("School:", font_weight="bold")
        school_value = toga.Label(response['school'])
        school_box.add(school_label)
        school_box.add(school_value)
        self.main_page_box.add(school_box)

        city_box = toga.Box(direction=ROW, margin=(5,10))
        city_label = toga.Label("City:", font_weight="bold")
        city_value = toga.Label(response['city'])
        city_box.add(city_label)
        city_box.add(city_value)
        self.main_page_box.add(city_box)

def main():
    return BookCharityApp()