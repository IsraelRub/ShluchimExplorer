import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Any

class ShluchimDatabase:
    def __init__(self) -> None:
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="shluchim"
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
            self.cursor = self.connection.cursor()
        except Error as err:
            print(f"Error connecting to MySQL database: {err}")

    def __del__(self) -> None:
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection is closed")

    def authenticate_user(self, email: str, password: str) -> bool:
        try:
            sql = """
            SELECT ch.id 
            FROM chabad_houses ch
            JOIN shluchim_accounts sa ON ch.id = sa.chabad_house_id
            WHERE ch.email = %s AND sa.passwords = %s
            """
            self.cursor.execute(sql, (email, password))
            result = self.cursor.fetchone()
            return result is not None
        except Error as err:
            print(f"Error during authentication: {err}")
            return False

    def print_all_chabad_houses(self) -> None:
        try:
            sql = "SELECT * FROM chabad_houses"
            self.cursor.execute(sql)
            chabad_houses = self.cursor.fetchall()
            for chabad_house in chabad_houses:
                print(f"Country: {chabad_house[1]}, City: {chabad_house[2]}, Rabbi: {chabad_house[3]}, "
                      f"Phone: {chabad_house[4]}, Email: {chabad_house[5]}, Website: {chabad_house[6]}, Established: {chabad_house[7]}\n")
        except Error as err:
            print(f"Error: {err}")



    def add_chabad_house(self, country: str, city: str, rabbi: str, phone: str, email: str, website: str, established: str) -> None:
        try:
            sql = """INSERT INTO chabad_houses (country, city, rabbi_name, phone, email, website, establishment_year) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (country, city, rabbi, phone, email, website, established)
            self.cursor.execute(sql, values)
            chabad_house_id = self.cursor.lastrowid

            password = input("Enter your password: \n")
            sql_account = """INSERT INTO shluchim_accounts (chabad_house_id, users, passwords) 
                             VALUES (%s, %s, %s)"""
            self.cursor.execute(sql_account, (chabad_house_id, email, password))

            self.connection.commit()
            print(f"Chabad house added successfully. The Chabad house ID's is {chabad_house_id}")
        except Error as err:
            print(f"Error: {err}")


    def update_chabad_house(self, id: int) -> None:
        try:
            self.cursor.execute("SELECT * FROM chabad_houses WHERE id = %s", (id,))
            current_data = self.cursor.fetchone()
            
            if not current_data:
                print("Chabad house not found.")
                return

            updates: dict[str, Any] = {}
            
            fields = ['country', 'city', 'rabbi_name', 'phone', 'email', 'website', 'establishment_year']
            for i, field in enumerate(fields, 1):
                new_value = input(f"Enter new {field} (or press Enter to keep current '{current_data[i]}'): ")
                if new_value:
                    updates[field] = new_value

            if not updates:
                print("No changes made.")
                return

            sql = "UPDATE chabad_houses SET "
            sql += ", ".join([f"{field} = %s" for field in updates])
            sql += " WHERE id = %s"

            values = list(updates.values()) + [id]

            self.cursor.execute(sql, tuple(values))

            if 'email' in updates:
                sql_update_account = "UPDATE shluchim_accounts SET users = %s WHERE chabad_house_id = %s"
                self.cursor.execute(sql_update_account, (updates['email'], id))

            self.connection.commit()
            print("Chabad house updated successfully.")
        except Error as err:
            print(f"Error: {err}")

    def delete_chabad_house(self, id: int) -> None:
        try:
            # First, delete related activities
            sql_delete_activities = "DELETE FROM chabad_house_activities WHERE chabad_house_id = %s"
            self.cursor.execute(sql_delete_activities, (id,))

            # Then, delete the account
            sql_delete_account = "DELETE FROM shluchim_accounts WHERE chabad_house_id = %s"
            self.cursor.execute(sql_delete_account, (id,))

            # Finally, delete the Chabad house
            sql_delete_house = "DELETE FROM chabad_houses WHERE id = %s"
            self.cursor.execute(sql_delete_house, (id,))
            
            self.connection.commit()
            print("Chabad house, associated activities, and account deleted successfully.")
        except Error as err:
            print(f"Error: {err}")

    def search_chabad_houses(self, country: Optional[str] = None, city: Optional[str] = None) -> None:
        try:
            sql = "SELECT * FROM chabad_houses WHERE 1=1"
            params: List[str] = []
            if country:
                sql += " AND country = %s"
                params.append(country)
            if city:
                sql += " AND city = %s"
                params.append(city)

            self.cursor.execute(sql, tuple(params))
            results = self.cursor.fetchall()
            for chabad_house in results:
                print(f"Country: {chabad_house[1]}, City: {chabad_house[2]}, Rabbi: {chabad_house[3]}\n")
        except Error as err:
            print(f"Error: {err}")

    def search_activity_by_chabad_houses(self, city: str) -> None:
        try:
            sql_get_id = "SELECT id FROM chabad_houses WHERE city = %s LIMIT 1"
            self.cursor.execute(sql_get_id, (city,))
            chabad_house_id = self.cursor.fetchone()
            
            if chabad_house_id:
                sql_get_activities = """
                SELECT ca.activity_name, ca.frequency 
                FROM chabad_activities ca
                JOIN chabad_house_activities cha ON ca.id = cha.activity_id
                WHERE cha.chabad_house_id = %s
                """
                self.cursor.execute(sql_get_activities, (chabad_house_id[0],))
                activities = self.cursor.fetchall()
                
                if activities:
                    print(f"Activities for Chabad house in {city}:\n")
                    print(f"{'Activity Name':<20} | {'Frequency':<10}")
                    print("-" * 32)
                    for activity in activities:
                        print(f"{activity[0]:<20} | {activity[1]:<10}")
                else:
                    print(f"No activities found for Chabad house in {city}")
            else:
                print(f"No Chabad house found in {city}")
        except Error as err:
            print(f"Error: {err}")

    def search_chabad_houses_by_activity(self, activity: str) -> None:
        try:
            sql = """
            SELECT DISTINCT ch.id, ch.country, ch.city, ch.rabbi_name
            FROM chabad_houses ch
            JOIN chabad_house_activities cha ON ch.id = cha.chabad_house_id
            JOIN chabad_activities ca ON cha.activity_id = ca.id
            WHERE ca.activity_name = %s
            """
            self.cursor.execute(sql, (activity,))
            results = self.cursor.fetchall()
            if results:
                print(f"\nChabad houses offering '{activity}':")
                for i, chabad_house in enumerate(results, 1):
                    print(f"{i}. Country: {chabad_house[1]}, City: {chabad_house[2]}, Rabbi: {chabad_house[3]}")
            else:
                print(f"No Chabad houses found offering '{activity}'")
        except Error as err:
            print(f"Error: {err}")

    def add_activity(self, activity_name: str, chabad_house_id: int) -> None:
        try:
            # Check if the activity exists in the chabad_activities table
            self.cursor.execute("SELECT id FROM chabad_activities WHERE activity_name = %s", (activity_name,))
            activity = self.cursor.fetchone()
            
            if not activity:
                print(f"Error: Activity '{activity_name}' does not exist in the system. Please choose an existing activity.")
                return

            activity_id = activity[0]

            # Check if the activity is already associated with the Chabad house
            self.cursor.execute("SELECT * FROM chabad_house_activities WHERE chabad_house_id = %s AND activity_id = %s", 
                                (chabad_house_id, activity_id))
            existing_activity = self.cursor.fetchone()

            if existing_activity:
                print(f"Activity '{activity_name}' is already associated with this Chabad house.")
            else:
                # Add the activity to the chabad house
                self.cursor.execute("INSERT INTO chabad_house_activities (chabad_house_id, activity_id) VALUES (%s, %s)", 
                                    (chabad_house_id, activity_id))
                self.connection.commit()
                print(f"Activity '{activity_name}' added successfully to Chabad house ID {chabad_house_id}")

        except Error as err:
            print(f"Error adding activity: {err}")


    def remove_activity(self, activity_name: str, chabad_house_id: int) -> None:
        try:
            # Get the activity ID
            self.cursor.execute("SELECT id FROM chabad_activities WHERE activity_name = %s", (activity_name,))
            activity = self.cursor.fetchone()
            
            if not activity:
                print(f"Activity '{activity_name}' does not exist.")
                return

            activity_id = activity[0]

            # Remove the activity from the chabad house
            self.cursor.execute("DELETE FROM chabad_house_activities WHERE chabad_house_id = %s AND activity_id = %s", 
                                (chabad_house_id, activity_id))

            if self.cursor.rowcount == 0:
                print(f"Activity '{activity_name}' was not associated with Chabad house ID {chabad_house_id}")
            else:
                self.connection.commit()
                print(f"Activity '{activity_name}' removed successfully from Chabad house ID {chabad_house_id}")

            # Check if the activity is associated with any other Chabad houses
            self.cursor.execute("SELECT * FROM chabad_house_activities WHERE activity_id = %s", (activity_id,))
            if not self.cursor.fetchone():
                # If not, remove the activity from chabad_activities
                self.cursor.execute("DELETE FROM chabad_activities WHERE id = %s", (activity_id,))
                self.connection.commit()
                print(f"Activity '{activity_name}' removed from the system as it's no longer associated with any Chabad house.")

        except Error as err:
            print(f"Error removing activity: {err}")


About_Chabad_Houses = """
About Chabad Houses

Introduction
============

Chabad Houses are a global network of outreach centers established by the Chabad-Lubavitch movement, one of the largest and most dynamic Jewish organizations in the world. These centers are known for their welcoming environment and dedication to providing Jewish education, support, and community services.

History and Background
======================

- Founded by the Chabad-Lubavitch Movement
  - Origins: The Chabad-Lubavitch movement was founded in the late 18th century by Rabbi Schneur Zalman of Liadi in Eastern Europe.
  - Expansion: Under the leadership of the seventh Rebbe, Rabbi Menachem Mendel Schneerson, the movement saw significant growth and established a presence worldwide.

Mission and Purpose
===================

- Outreach and Education
  - Jewish Awareness: Chabad Houses aim to raise awareness and pride in Jewish identity and heritage.
  - Education Programs: They offer a variety of educational programs for all ages, including Torah classes, Hebrew schools, and adult education.

- Community Services
  - Social Support: Providing assistance to those in need, such as food banks, counseling, and financial help.
  - Holiday Programs: Organizing events and services for Jewish holidays to foster community participation and celebration.

Global Presence
===============

- Worldwide Network
  - Over 5,000 Chabad Houses: Located in more than 100 countries, serving both local Jewish communities and travelers.
  - Key Locations: Major cities, university campuses, tourist destinations, and remote areas.

- Adaptability
  - Local Integration: Each Chabad House adapts to the local culture while maintaining core Jewish values and traditions.
  - Language and Accessibility: Services are often provided in multiple languages to accommodate diverse populations.

Activities and Services
=======================

- Religious Services
  - Shabbat and Holiday Services: Regular prayer services, communal meals, and holiday celebrations.
  - Life Cycle Events: Support and ceremonies for births, bar/bat mitzvahs, weddings, and funerals.

- Educational Initiatives
  - Children's Programs: Hebrew schools, day camps, and youth groups.
  - Adult Education: Torah classes, Jewish philosophy, and practical halacha (Jewish law) sessions.

- Social and Cultural Events
  - Community Dinners: Weekly Shabbat dinners and holiday meals open to everyone.
  - Cultural Programs: Lectures, concerts, and art exhibits celebrating Jewish culture and heritage.

Philosophy and Approach
=======================

- Inclusive and Non-Judgmental
  - Open to All: Chabad Houses welcome Jews from all backgrounds, regardless of their level of observance or affiliation.
  - Non-Judgmental Atmosphere: Emphasis on acceptance, love, and understanding.

- Personal Relationships
  - One-on-One Engagement: Personalized attention and relationships with community members.
  - Supportive Environment: Creating a sense of belonging and community for everyone.

Conclusion
==========

Chabad Houses play a vital role in fostering Jewish identity, education, and community support around the world. Their inclusive philosophy and wide range of activities make them a cornerstone of Jewish communal life, welcoming individuals from all walks of life to connect with their heritage and each other.
"""

def get_input(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt)
        if value or allow_empty:
            return value
        print("This field cannot be empty. Please try again.")


def main_menu() -> None:
    db = ShluchimDatabase()

    while True:
        print("\n--- Chabad Houses Management System ---")
        print("1. Guest Access")
        print("2. Shluchim Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            guest_menu(db)
        elif choice == '2':
            email = get_input("Enter user: ")
            password = get_input("Enter password: ")
            if db.authenticate_user(email, password):
                print("Login successful.")
                shluchim_menu(db)
            else:
                print("Invalid user or password.")
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

def guest_menu(db: ShluchimDatabase) -> None:
    while True:
        print("\n--- Guest Menu ---")
        print("1. View all Chabad Houses")
        print("2. Search Chabad Houses")
        print("3. Search Chabad Houses activities")
        print("4. About Chabad Houses")
        print("5. Return to Main Menu")

        choice = input("Enter your choice: ")
        match choice:
            case '1':
                db.print_all_chabad_houses()

            case '2':
                country = get_input("Enter country (or press Enter to skip): ", allow_empty=True)
                city = get_input("Enter city (or press Enter to skip): ", allow_empty=True)
                db.search_chabad_houses(country, city)

            case '3':
                city = get_input("Enter city: ").capitalize()
                db.search_activity_by_chabad_houses(city)

            case '4':
                print(About_Chabad_Houses)

            case '5':
                return

            case _:
                print("Invalid choice. Please try again.")


def shluchim_menu(db: ShluchimDatabase) -> None:
    while True:
        print("\n--- Registered User Menu ---")
        print("1. View all Chabad Houses")
        print("2. Search Chabad Houses")
        print("3. Search Chabad Houses activities")
        print("4. Search Chabad Houses by Activity")
        print("5. Add new Chabad House")
        print("6. Update Chabad House")
        print("7. Delete Chabad House")
        print("8. Add Activity to Chabad House")
        print("9. Remove Activity from Chabad House")
        print("10. Return to Main Menu")

        choice = input("Enter your choice: ")

        match choice:
            case '1':
                db.print_all_chabad_houses()

            case '2':
                country = get_input("Enter country (or press Enter to skip): ", allow_empty=True)
                city = get_input("Enter city (or press Enter to skip): ", allow_empty=True)
                db.search_chabad_houses(country, city)

            case '3':
                city = get_input("Enter city: ")
                db.search_activity_by_chabad_houses(city)

            case '4':
                activity = get_input("Enter activity to search for: ")
                db.search_chabad_houses_by_activity(activity)

            case '5':
                country = get_input("Enter country: ")
                city = get_input("Enter city: ")
                rabbi = get_input("Enter rabbi name: ")
                phone = get_input("Enter phone: ")
                email = get_input("Enter email: ")
                website = get_input("Enter website: ", allow_empty=True)
                established = get_input("Enter establishment year: ")
                db.add_chabad_house(country, city, rabbi, phone, email, website, established)

            case '6':
                id = int(get_input("Enter ID of Chabad house to update: "))
                db.update_chabad_house(id)

            case '7':
                id = int(get_input("Enter ID of Chabad house to delete: "))
                db.delete_chabad_house(id)
            case '8':
                chabad_house_id = int(get_input("Enter Chabad house ID: "))
                activity_name = get_input("Enter activity name from the list above: ")
                db.add_activity(activity_name, chabad_house_id)

            case '9':
                chabad_house_id = int(get_input("Enter Chabad house ID: "))
                activity_name = get_input("Enter activity name to remove: ")
                db.remove_activity(activity_name, chabad_house_id)

            case '10':
                return

            case _:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
