import re
import mysql.connector
from datetime import datetime, timedelta
from _decimal import Decimal

# Establishing a connection to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="040828",
    database="library_db"
)

login = db.cursor()

# Creating Admin table
login.execute("""
CREATE TABLE IF NOT EXISTS Admin (
    ADMIN_ID INT AUTO_INCREMENT PRIMARY KEY,
    Firstname VARCHAR(300),
    Lastname VARCHAR(300),
    Password VARCHAR(300),
    Email VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Subscriptions (
    SUB_ID INT AUTO_INCREMENT PRIMARY KEY,
    Start_Date DATE,
    Renewal_Date DATE,
    Renewal_Status VARCHAR(20),
    PLANS VARCHAR(20)
)
""")


login.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    CUST_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(300),
    Last_Name VARCHAR(300),
    Password VARCHAR(300),
    Email VARCHAR(300),
    SUB_ID INT,
    REG_Date DATE,
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions (SUB_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Authors (
    AUTHOR_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Category (
    CAT_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Genre (
    GEN_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Books (
    BOOK_ID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(300),
    Author_Name VARCHAR(300),
    Price VARCHAR(20),
    CAT_ID INT,
    GEN_ID INT,
    FOREIGN KEY (CAT_ID) REFERENCES Category(CAT_ID),
    FOREIGN KEY (GEN_ID) REFERENCES Genre(GEN_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Rentals (
    RENTAL_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    BOOK_ID INT,
    Rent_Date DATE,
    Return_Date DATE,
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (BOOK_ID) REFERENCES Books(BOOK_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Reminders (
    REM_ID INT AUTO_INCREMENT PRIMARY KEY,
    ADMIN_ID INT,
    Rem_Date DATE,
    FOREIGN KEY (ADMIN_ID) REFERENCES Admin(ADMIN_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Sub_Reminders (
    SREM_ID INT AUTO_INCREMENT PRIMARY KEY,
    SUB_ID INT,
    Rem_Date DATE,
    Rem_Status VARCHAR(300),
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions(SUB_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Memberships (
    MEM_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    Start_Date DATE,
    Renewal_Status VARCHAR(300),
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Payments (
    PAYMENT_ID INT AUTO_INCREMENT PRIMARY KEY,
    SUB_ID INT,
    CUST_ID INT,
    MEM_ID INT,
    Amount VARCHAR(20),
    Payment_Date DATE,
    Payment_Method VARCHAR(300),
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions(SUB_ID),
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (MEM_ID) REFERENCES Memberships(MEM_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Reviews (
    REVIEW_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    BOOK_ID INT,
    Review_Text VARCHAR(500),
    Rating VARCHAR(300),
    Review_Date DATE,
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (BOOK_ID) REFERENCES Books(BOOK_ID)
)
""")


# Function to update customer details
def update_cust():
    print("Update Existing Customer")
    cust_id = input("Enter customer user ID: ")

    # Input for new first name
    while True:
        new_first_name = input("Enter the first name: ")
        if re.fullmatch("[A-Za-z]{2,25}", new_first_name):
            break
        else:
            print("INVALID! Enter only alphabets of length 2 to 25")

    # Input for new last name
    while True:
        new_last_name = input("Enter the last name: ")
        if re.fullmatch("[A-Za-z]{2,25}", new_last_name):
            break
        else:
            print("INVALID! Enter only alphabets of length 1 to 25")

    # Input for new email
    while True:
        new_email = input("Enter new email: ")
        if re.fullmatch(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', new_email):
            break
        else:
            print("INVALID! Enter a valid email id")

    # Input for new password
    while True:
        new_password = input("Enter the password: ")
        if " " not in new_password:
            if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_]).{6,16}$', new_password):
                break
            else:
                print("""The password should contain at least:
                        - One capital letter
                        - One small letter
                        - One number
                        - One special character [@#$%^&+!_]
                        It should be 6 to 16 characters long.""")
        else:
            print("INVALID! Password should not contain spaces")

    # Input for new subscription ID
    new_subscription_id = int(input("Enter new subscription ID (211 - Monthly / 212 - Yearly): "))

    # Automatically set the new registration date
    reg_date = datetime.now().date()

    # Calculate renewal date based on new subscription plan
    if new_subscription_id == 211:
        renewal_date = reg_date + timedelta(days=30)  # Monthly plan
    elif new_subscription_id == 212:
        renewal_date = reg_date + timedelta(days=365)  # Yearly plan
    else:
        print("Invalid Subscription Plan!")
        return

    # Update the subscription details
    try:
        sub_update_query = """
            UPDATE Subscriptions
            SET Start_Date = %s, Renewal_Date = %s, PLANS = %s
            WHERE SUB_ID = (SELECT SUB_ID FROM Customer WHERE CUST_ID = %s)
        """
        login.execute(sub_update_query,
                      (reg_date, renewal_date, "Monthly" if new_subscription_id == 211 else "Yearly", cust_id))

        # Update the customer details
        update_query = """
            UPDATE Customer
            SET Email = %s, First_Name = %s, Last_Name = %s, Password = %s, SUB_ID = %s
            WHERE CUST_ID = %s
        """
        login.execute(update_query,
                      (new_email, new_first_name, new_last_name, new_password, new_subscription_id, cust_id))

        db.commit()
        print("Customer updated successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to delete a customer
def delete_cust():
    print("Delete a Customer")
    cust_id = input("Enter customer user ID to delete: ")

    delete_query = """
        DELETE FROM Customer
        WHERE CUST_ID = %s
    """
    try:
        login.execute(delete_query, (cust_id,))
        db.commit()
        print("Customer deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to add a new book
def add_book():
    print("Add a New Book")
    title = input("Enter book title : ")
    author_name = input("Enter author name : ")
    price = float(input("Enter the price : "))
    cat_id = int(input("Enter category ID : "))
    gen_id = int(input("Enter genre ID : "))

    insert_query = """
        INSERT INTO Books (Title, Author_Name, Price, CAT_ID, GEN_ID)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        login.execute(insert_query, (title, author_name, price, cat_id, gen_id))
        db.commit()
        print("Book added successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to update an existing book
def update_book():
    print("Update Existing Book")
    book_id = input("Enter book ID: ")
    new_title = input("Enter new title: ")
    new_price = float(input("Enter new price: "))

    update_query = """
        UPDATE Books
        SET Title = %s,
        Price = %s
        WHERE BOOK_ID = %s
    """
    try:
        login.execute(update_query, (new_title, new_price, book_id))
        db.commit()
        print("Book updated successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to dlete a book
def delete_book():
    print("Delete a Book")
    book_id = input("Enter book ID to delete: ")

    # Check if the book is rented out
    check_rentals_query = """
        SELECT COUNT(*)
        FROM rentals
        WHERE BOOK_ID = %s
    """
    delete_book_query = """
        DELETE FROM Books
        WHERE BOOK_ID = %s
    """

    try:
        login.execute(check_rentals_query, (book_id,))
        count = login.fetchone()[0]

        if count > 0:
            print("Cannot delete the book because it is currently rented out.")
            return

        login.execute(delete_book_query, (book_id,))
        db.commit()
        print("Book deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to view rental history
def view_rent_history():
    print("Rental History:")
    query = """
        SELECT Rentals.RENTAL_ID, Customer.First_Name, Customer.Last_Name, Books.Title, Rentals.Rent_Date, Rentals.Return_Date
        FROM Rentals
        JOIN Customer ON Rentals.CUST_ID = Customer.CUST_ID
        JOIN Books ON Rentals.BOOK_ID = Books.BOOK_ID
    """
    try:
        login.execute(query)
        for (rental_id, firstname, lastname, title, rent_date, return_date) in login:
            print(f"Rental ID: {rental_id}\nCustomer: {firstname} {lastname}\nBook: {title}\nRent Date: {rent_date}\nReturn Date: {return_date}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def send_subscription_reminders():
    print("Sending Subscription Renewal Reminders")
    today = datetime.now().date()

    try:
        login.execute("""
            SELECT CONCAT(Customer.first_name, ' ', Customer.last_name) AS full_name,
                   Subscriptions.SUB_ID, 
                   Subscriptions.Start_Date, 
                   Subscriptions.Renewal_Status
            FROM Subscriptions
            JOIN Customer ON Subscriptions.SUB_ID = Customer.SUB_ID
            WHERE Subscriptions.Renewal_Status = 'Active'
        """)
        subscriptions = login.fetchall()

        for subscription in subscriptions:
            full_name, sub_id, start_date, renewal_status = subscription
            next_renewal_date = start_date + timedelta(days=365)

            if next_renewal_date <= today + timedelta(days=7):
                login.execute("""
                    INSERT INTO Sub_Reminders (SUB_ID, Rem_Date, Rem_Status)
                    VALUES (%s, %s, %s)
                """, (sub_id, today, 'Pending'))
                db.commit()
                print(f"Reminder sent for customer {first_name}.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to list books
def list_books():
    print("List of Books:")

    query = """
        SELECT Books.BOOK_ID, Books.Title, Books.Author_Name, Category.Name, Genre.Name, Books.Price
        FROM Books
        JOIN Category ON Books.CAT_ID = Category.CAT_ID
        JOIN Genre ON Books.GEN_ID = Genre.GEN_ID
    """

    try:
        login.execute(query)
        books = login.fetchall()
        for book in books:
            print(f"Book ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Category: {book[3]}, Genre: {book[4]}, Price: {book[5]}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")



def list_of_rented_books():
    print("List of Rented Books")
    cust_id = input("Enter your user ID: ")

    query = """
        SELECT Books.BOOK_ID, Books.Title, Books.Author_Name, Rentals.Rent_Date
        FROM Rentals
        JOIN Books ON Rentals.BOOK_ID = Books.BOOK_ID
        WHERE Rentals.CUST_ID = %s
    """

    try:
        login.execute(query, (cust_id,))
        rented_books = login.fetchall()

        if rented_books:
            print(f"Books rented by Customer ID {cust_id}:")
            for book in rented_books:
                print(f"Book ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Rent Date: {book[3]}")
        else:
            print("No rented books found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to rent a book
def rent_book():
    print("Rent a Book")
    cust_id = input("Enter your user ID: ")
    book_title = input("Enter the title of the book you want to rent: ")
    rent_date = datetime.now().date()

    # Query to find the BOOK_ID based on the book title
    query = """
        SELECT BOOK_ID FROM Books WHERE Title = %s
    """

    try:
        login.execute(query, (book_title,))
        result = login.fetchone()

        if result:
            book_id = result[0]

            # Proceed to insert the rental record
            insert_query = """
                INSERT INTO Rentals (CUST_ID, BOOK_ID, Rent_Date)
                VALUES (%s, %s, %s)
            """
            login.execute(insert_query, (cust_id, book_id, rent_date))
            db.commit()
            print("Book rented successfully.")
        else:
            print("Book not found. Please check the title and try again.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to search for books
def search_book():
    print("Search for Books")
    search_term = input("Enter title or part of title to search: ")

    search_query = """
        SELECT * FROM Books
        WHERE Title LIKE %s
    """
    try:
        login.execute(search_query, ("%" + search_term + "%",))
        books = login.fetchall()
        for book in books:
            print(book)
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to add reviews
def add_review():
    print("Add a Review")
    cust_id = input("Enter your user ID: ")
    book_title = input("Enter the book title: ")

    # Query to find the book ID based on the title
    book_id_query = """
        SELECT BOOK_ID FROM Books WHERE Title = %s
    """
    try:
        login.execute(book_id_query, (book_title,))
        result = login.fetchone()
        if result:
            book_id = result[0]
            review_text = input("Enter your review: ")
            rating = input("Enter your rating: ")
            review_date = datetime.now().date()

            insert_query = """
                INSERT INTO Reviews (Cust_ID, BOOK_ID, Review_Text, Rating, Review_Date)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                login.execute(insert_query, (cust_id, book_id, review_text, rating, review_date))
                db.commit()
                print("Review added successfully.")
            except mysql.connector.Error as err:
                print(f"Error: {err}")
        else:
            print("Book title not found. Please check the title and try again.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to view book details
def book_details():
    print("View Book Details")
    book_title = input("Enter book title: ")

    query = """
        SELECT Books.BOOK_ID, Books.Title, Books.Author_Name, Category.Name, Genre.Name
        FROM Books
        JOIN Category ON Books.CAT_ID = Category.CAT_ID
        JOIN Genre ON Books.GEN_ID = Genre.GEN_ID
        WHERE Books.Title = %s
    """

    try:
        login.execute(query, (book_title,))
        book = login.fetchone()
        if book:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Category: {book[3]}")
            print(f"Genre: {book[4]}")
        else:
            print("Book not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to list all customers
def list_all_customers():
    print("List of All Customers")
    query = """
        SELECT CUST_ID, First_Name, Last_Name, Email, SUB_ID
        FROM Customer
    """
    try:
        login.execute(query)
        customers = login.fetchall()
        if customers:
            print("Customer List:")
            for customer in customers:
                print(
                    f"Customer ID: {customer[0]}, Name: {customer[1]} {customer[2]}, Email: {customer[3]}, SUB_ID: {customer[4]}")
        else:
            print("No customers found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def sign_up():
    try:
        print("""
                          ----------------------------
                                  SIGN UP HERE
                          ----------------------------
            """)

        # Input for first name
        while True:
            first_name = input("Enter the first name: ")
            if re.fullmatch("[A-Za-z]{2,25}", first_name):
                break
            else:
                print("INVALID! Enter only alphabets of length 2 to 25")

        # Input for last name
        while True:
            last_name = input("Enter the last name: ")
            if re.fullmatch("[A-Za-z]{2,25}", last_name):
                break
            else:
                print("INVALID! Enter only alphabets of length 2 to 25")

        # Input for email
        while True:
            email = input("Enter the email id : ")
            if re.fullmatch(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', email):
                break
            else:
                print("INVALID !! Enter a valid email id")

        # Input for password
        while True:
            password = input("Enter the password: ")
            if " " not in password:
                if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+!_]).{6,16}$', password):
                    break
                else:
                    print("""The password should contain at least:
                                - One capital letter
                                - One small letter
                                - One number
                                - One special character [@#$%^&+!_]
                                It should be 6 to 16 characters long.""")
            else:
                print("INVALID! Password should not contain spaces")

        sub_id = int(input("Select Subscription Plans\n(211 - Monthly / 212 - Yearly) : "))

        # Automatically set registration date
        reg_date = datetime.now().date()

        # Calculate renewal date based on subscription plan and set amount
        if sub_id == 211:
            renewal_date = reg_date + timedelta(days=30)  # Monthly plan
            amount = "90"
        elif sub_id == 212:
            renewal_date = reg_date + timedelta(days=365)  # Yearly plan
            amount = "1000"
        else:
            print("Invalid Subscription Plan!")
            return

        # Insert subscription details into the Subscriptions table
        sub_insert_query = """
            INSERT INTO Subscriptions (Start_Date, Renewal_Date, Renewal_Status, PLANS)
            VALUES (%s, %s, %s, %s)
        """
        login.execute(sub_insert_query, (reg_date, renewal_date, "Active", "Monthly" if sub_id == 211 else "Yearly"))

        new_sub_id = login.lastrowid  # Get the newly inserted subscription ID

        # Insert customer details into the Customer table
        cust_insert_query = """
            INSERT INTO Customer (First_Name, Last_Name, Email, Password, SUB_ID, REG_Date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        login.execute(cust_insert_query, (first_name, last_name, email, password, new_sub_id, reg_date))
        new_cust_id = login.lastrowid  # Get the newly inserted customer ID

        # Payment method selection
        print("Select Payment Method:\n1. GPay\n2. Debit Card\n3. Visa Card")
        payment_method = input("Enter your choice (1/2/3): ")

        if payment_method == '1':
            while True:
                upi_id = input("Enter your UPI ID: ")
                if re.fullmatch(r'^[\w\.-]+@[\w\.-]+$', upi_id):
                    payment_method_name = "GPay"
                    payment_details = upi_id
                    break
                else:
                    print("INVALID! Enter a valid UPI ID (e.g., username@bankname)")
        elif payment_method == '2':
            while True:
                card_number = input("Enter your Debit Card Number: ")
                if re.fullmatch(r'^\d{16}$', card_number):
                    cvv = input("Enter your CVV: ")
                    if re.fullmatch(r'^\d{3}$', cvv):
                        payment_method_name = "Debit Card"
                        payment_details = f"Card Number: {card_number}, CVV: {cvv}"
                        break
                    else:
                        print("INVALID! CVV must be 3 digits")
                else:
                    print("INVALID! Card number must be 16 digits")
        elif payment_method == '3':
            while True:
                visa_card_number = input("Enter your Visa Card Number: ")
                if re.fullmatch(r'^\d{16}$', visa_card_number):
                    cvv = input("Enter your CVV: ")
                    if re.fullmatch(r'^\d{3}$', cvv):
                        payment_method_name = "Visa Card"
                        payment_details = f"Card Number: {visa_card_number}, CVV: {cvv}"
                        break
                    else:
                        print("INVALID! CVV must be 3 digits")
                else:
                    print("INVALID! Card number must be 16 digits")
        else:
            print("Invalid payment method!")
            return

        payment_date = datetime.now().date()

        # Insert payment details into the Payments table
        payment_insert_query = """
            INSERT INTO Payments (SUB_ID, CUST_ID, Amount, Payment_Date, Payment_Method)
            VALUES (%s, %s, %s, %s, %s)
        """
        login.execute(payment_insert_query, (new_sub_id, new_cust_id, amount, payment_date, payment_details))
        db.commit()

        print("You have successfully registered !!!")
        cust_login()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print("User ID already exists")


def admin_pg():
    while True:
        print("""
                              -----------------------------
                                      WELCOME ADMIN
                              -----------------------------
        -> Choose an option to continue:
        1. Update existing Customer
        2. Delete a Customer
        3. Add a new Book
        4. Update existing Book
        5. Delete a Book
        6. List all Customers
        7. View Rental History
        8. Send Subscription Reminders
        9. Exit
        """)
        choice = input("Enter your choice from above list: ")
        if choice == "1":
            update_cust()
        elif choice == "2":
            delete_cust()
        elif choice == "3":
            add_book()
        elif choice == "4":
            update_book()
        elif choice == "5":
            delete_book()
        elif choice == "6":
            list_all_customers()
        elif choice == "7":
            view_rent_history()
        elif choice == "8":
            send_subscription_reminders()
        elif choice == "9":
            print("Logging Out....")
            break
        else:
            print("Invalid! Enter numbers from 1 to 9 only.")


def admin_login():
    while True:
        admin_id = input("Enter the user ID: ")
        if admin_id == "":
            print("This field cannot be empty.")
        else:
            break

    while True:
        password = input("Enter the password: ")
        if password == "":
            print("This field cannot be empty.")
        else:
            break

    select_query = """
        SELECT * FROM Admin 
        WHERE ADMIN_ID = %s COLLATE utf8mb4_bin 
        AND Password = %s COLLATE utf8mb4_bin
    """
    login.execute(select_query, (admin_id, password))
    result = login.fetchone()

    if result is not None:
        print("Admin Login Successfully")
        admin_pg()
    else:
        print("Incorrect user ID or password!")


def cust_pg():
    while True:
        print("""
                              --------------------------------
                                      WELCOME CUSTOMER
                              --------------------------------
        -> Choose an option to continue:
        1. List All Books
        2. View List of Rented Books
        3. Rent a Book
        4. Search for Books
        5. Add Reviews
        6. Update Details
        7. Logout
        """)
        choice = input("Enter your choice from above list: ")
        if choice == "1":
            list_books()
        elif choice == "2":
            list_of_rented_books()
        elif choice == "3":
            rent_book()
        elif choice == "4":
            search_book()
        elif choice == "5":
            add_review()
        elif choice == "6":
            update_cust()
        elif choice == "7":
            print("You have been logged out!")
            break
        else:
            print("Invalid! Enter numbers from 1 to 6 only.")


def cust_login():
    while True:
        email = input("Enter your email: ")
        if email == "":
            print("This field cannot be empty.")
        else:
            break

    while True:
        password = input("Enter the password: ")
        if password == "":
            print("This field cannot be empty.")
        else:
            break

    select_query = """
        SELECT * FROM Customer 
        WHERE Email = %s COLLATE utf8mb4_bin 
        AND Password = %s COLLATE utf8mb4_bin
    """
    login.execute(select_query, (email, password))
    result = login.fetchone()

    if result is not None:
        print("Customer Login Successful ")
        cust_pg()
    else:
        print("Incorrect email or password!")

def guest():
    while True:
        print("""
                              ----------------------------------
                                      WELCOME GUEST USER
                              ----------------------------------
        -> Choose an option to continue:
        1. View List of Books
        2. View Book Details
        3. Register for an Account
        4. Exit
        """)
        choice = input("Enter your choice from above list: ")
        if choice == "1":
            list_books()
        elif choice == "2":
            book_details()
        elif choice == "3":
            sign_up()
        elif choice == "4":
            print("You have been logged out!")
            break
        else:
            print("Invalid! Enter numbers from 1 to 4 only.")

# Main function
def main():
    while True:
        print("""
                                      -------------------------------------------------------
                                            WELCOME TO ONLINE LIBRARY MANAGEMENT SYSTEM
                                      -------------------------------------------------------
                  -> Choose an option:
                  1. Admin Login
                  2. Customer Login
                  3. New User? Register Here
                  4. Guest User
                  5. Exit
            """)
        choice = input("Enter your choice : ")

        if choice == "1":
            admin_login()
        elif choice == "2":
            cust_login()
        elif choice == "3":
            sign_up()
        elif choice == "4":
            guest()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")
    db.close()

if __name__ == "__main__":
    main()
