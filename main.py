import sys
import database_helper  # handles database operations
import getpass # handles masking password inputs

ROLE_MAPPING = {"1": "Admin", "2": "Curator", "3": "EndUser"}

def login_user(role_name, email, password):
    """
    Simply hooks in to backend DB helper's authentication implementation.
    """
    return database_helper.authenticate_user(role_name, email, password)

def create_user():
    print("Creating a new EndUser...")
    name = ""
    while name == "":
        name = input("  Enter name: ").strip()
    email = ""
    while email == "":
        email = input("  Enter email: ").strip()

    # unlike "sign_up" admin can actually set the role
    role = input("  Enter role (\"EndUser\", \"Curator\", \"Admin\"): ").strip()
    while role not in ['EndUser', 'Curator', 'Admin']:
        print("Invalid role. Try again.")
        role = input("  Enter role (\"EndUser\", \"Curator\", \"Admin\"): ").strip()
    username = ""
    while username == "":
        username = input("  Enter username: ").strip()
    while True:
        password = input("  Enter password: ").strip()
        confirm_pw = input("  Confirm password: ").strip()

        if password != confirm_pw:
            print("    Password does not match...")
        else:
            break
    # return None is something went wrong or return the result row of the newly signed up end user
    # user_id, user_name, user_email, user_role, user_username, user_password
    return database_helper.ADMIN_user_create(name=name, email=email, role=role, username=username, password=password)

def create_doc():
    print("Adding a new Document...")
    # TODO

def sign_up():
    name = ""
    while name == "":
        name = input("  Enter name: ").strip()
    email = ""
    while email == "":
        email = input("  Enter email: ").strip()
    username = ""
    while username == "":
        username = input("  Enter username: ").strip()
    while True:
        password = input("  Enter password: ").strip()
        confirm_pw = input("  Confirm password: ").strip()

        if password != confirm_pw:
            print("    Password does not match...")
        else:
            break
    # return None is something went wrong or return the result row of the newly signed up end user
    # user_id, user_name, user_email, user_role, user_username, user_password
    return database_helper.handle_signup(name, email, username, password)

def update_user():
    print("Updating a User's information...")

    Update_ID = input("Enter the ID of the user you'd like to update: ").strip()
    if not Update_ID:
        print("User ID is required.")
        return

    print("Leave any field blank to keep it unchanged.\n")

    username = input("New username (or press Enter to skip): ").strip()
    name = input("New name (or press Enter to skip): ").strip()
    email = input("New email (or press Enter to skip): ").strip()
    while True:
        password = input("  Enter password: ").strip()
        confirm_pw = input("  Confirm password: ").strip()

        if password != confirm_pw:
            print("    Password does not match...")
        else:
            break

    return database_helper.ADMIN_user_update(user_id=Update_ID, name=name, email=email, username=username, password=password)

def delete_user():
    print("Deleting a User...")
    Delete_ID = input("Enter the ID of the user you'd like to delete: ").strip()
    if not Delete_ID:
        print("User ID is required.")
        return
    return database_helper.ADMIN_user_delete(Delete_ID)

def fetch_docs():
    print("  1. Fetch Your Documents")
    print("  2. Fetch All Documents")
    choice = None
    while choice != "X" and choice != "":
        choice = input("  Select an option (1-2, X to exit): ").strip()

        if choice == "1":
            print("  Your Documents: ")
            # TODO: output the documents
        elif choice == "2":
            print("  All Documents: ")
            # TODO: output all documents

def delete_doc():
    print("Deleting a Document...")
    # TODO: figure out which document to remove

def print_login_menu():
    print("\n=== Login Selection Menu ===")
    print("1. Admin")
    print("2. Curator")
    print("3. EndUser")
    print("S. Sign Up as EndUser")
    print("X. Exit")
    print("===========================")

def print_curator_menu():
    print("\n=== Curator Menu ===")
    print("1. Add New Document")
    print("2. Fetch Document List")
    print("3. Delete Document")
    print("X. Exit")
    print("=================")

def print_admin_menu():
    print("\n=== ADMIN Menu ===")
    print("1. Create User")
    print("2. Fetch Users")
    print("3. Update User")
    print("4. Delete User")
    print("X. Log Out")
    print("=================")

def print_user_menu():
    print("\n=== USER Menu ===")
    while True:
        query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->").strip()
        if query != "X" or query != "":
            print(f"DEBUG Query is: {query}")
            # TODO: convert query string to an embedding eg embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
            # where model is the SentenceTransformer. You can then plug in the embedding into a SQL SELECT statement
        else:
            break


# When program starts, have the user login as a particular role before they can do something
# Returns number representing the user's role
def landing_loop():
    while True:
        # Step 1. Ask user for role
        print_login_menu()
        role_choice = input("Select an option: ").strip()

        if role_choice == "X" or role_choice == "":
            print("Exiting program...")
            sys.exit(1)

        # sign up can only create new EndUsers
        if role_choice == "S":
            result_row = sign_up()
            print(result_row)
            if result_row is not None:
                print("New EndUser successfully made.\n")
                return result_row    # we are signed up now, which will auto log us in as the newly made user
            else:
                print("ERROR: New EndUser was NOT created.\n")
                continue    # database error occurred

        role = ROLE_MAPPING.get(role_choice, None)  # set to None if not found

        if not role:
            print("Invalid role choice. Try again.")
            continue

        # Prompt for login credentials
        email = input(f"Enter {role} email: ").strip()
        password = input(f"Enter {role} password: ").strip()

        # Try inputted credentials against the selected role table
        # Step 2. Authenticate user credentials
        user_row = login_user(role, email, password)
        if user_row is None:
            print("Invalid credentials. Try again.")
            continue

        # successful log in
        return user_row

# can do CRUD on the Users table
def admin_loop():
    choice = None
    while choice != "X" and choice != "":
        print_admin_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            create_user()
        elif choice == "2":
            for row in database_helper.ADMIN_users_fetch():
                print(row)
        elif choice == "3":
            update_user()
        elif choice == "4":
            delete_user()
        elif choice == "X" or choice == "":
            print("Returning to role selection...")
        else:
            print("Invalid choice. Please try again.")

# can do CRUD on the Documents table
def curator_loop():
    choice = None
    while choice != "X" and choice != "":
        print_curator_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            create_doc()
        elif choice == "2":
            fetch_docs()
        elif choice == "3":
            delete_doc()
        elif choice == "X" or choice == "":
            print("Returning to role selection...")
        else:
            print("Invalid choice. Please try again.")

# can submit queries
def enduser_loop():
    choice = None
    while choice != "X" and choice != "":
        print_user_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            while True:
                query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->")
                if query != "X":
                    print(f"----DEBUG Query is: {query}") # TODO remove this!
                    # TODO: convert query string to an embedding eg embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
                    # where model is the SentenceTransformer. You can then plug in the embedding into a SQL SELECT statement
                else:
                    break
        elif choice == "X" or choice == "":
            print("Returning to role selection...")
        else:
            print("Invalid choice. Please try again.")

def main():
    print(database_helper.ADMIN_users_fetch())
    """
    Handle main workflow of program.

    Admins can do CRUD on Users table. Curators can do CRUD on Documents table.
    EndUsers can make queries.
    """
    # Step 1. Ask user for role
    # Step 2. Authenticate user credentials
    while True:
        user_row = landing_loop()
        user_id, user_name, user_email, user_role, user_username, user_password = user_row
        print(f"Hello, {user_name} you are successfully logged in as {user_role}!")

        # Step 3. Prompt user with role specific menu
        # Step 4. Accept user input and perform specified action
        # Step 5. Repeat Step 3-4 until we recieve a log out action or program terminates
        if user_role == "Admin":
            admin_loop()   # can do CRUD on the Users table
        elif user_role == "Curator":
            curator_loop() # can do CRUD on the Documents table
        elif user_role == "EndUser":
            enduser_loop() # can submit queries
        else:
            assert(False)   # dead code

# when program starts, user will need to log in as a certain role
# For simplicity:
# Admin: Can do CRUD operations on Users table, but nothing else
# Curator: Can do CRUD operations on the Documents table, but nothing else
# EndUser: Can make queries
if __name__ == "__main__":
    # main program workflow
    # Step 1. Ask user for role
    # Step 2. Authenticate user credentials
    # Step 3. Prompt user with role specific menu
    # Step 4. Accept user input and perform specified action
    # Step 5. Repeat Step 3-4 until we recieve a log out action or program terminates
    main()