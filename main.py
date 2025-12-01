import sys
import database_helper  # handles database operations

ROLE_MAPPING = {"1": "Admin", "2": "Curator", "3": "EndUser"}

def authenticate_user(role, email, password):
    """
    Stub for authentication logic.
    Replace with actual backend check.
    Return True if credentials are valid, False otherwise.
    """
    print(f"Authenticating {role} with email={email} (stub).")
    assert(False);
    # TODO: implement actual authentication
    return False   # always fail for now, so user bounces back


def create_user():
    print("Creating a new EndUser...")
    res = sign_up()
    if res:
        print("New EndUser successfully made.\n")
    else:
        print("ERROR: New EndUser was NOT created.\n")
    

def sign_up():
    name = input("  Enter name: ").strip()
    email = input("  Enter email: ").strip()
    # TODO: check email is unique
    # print("Account with that email already exists. Try again.")
    username = input("  Enter username: ").strip()
    # TODO: check username is unique
    while True:
        password = input("  Enter password: ").strip()
        confirm_pw = input("  Confirm password: ").strip()

        if password != confirm_pw:
            print("    Password does not match...")
        else:
            break;
    # TODO: add new user to database with name, email, username, and password
    # if the database has an error return False
    return True


def fetch_users():
    print("Fetching all Users...")
    # TODO: implement a SELECT on the Users table in database_helper
    assert(False)


def update_user():
    print("Updating a User's information...")
    # TODO: first prompt for ID or email of who to change
    # then prompt for new user info
    assert(False)


def delete_user():
    print("Deleting a User...")
    # TODO: figure out who to remove, if its an EndUser, make sure to remove all their QueryLogs too
    assert(False)


def print_login_menu():
    print("\n=== Login Selection Menu ===")
    print("1. Admin")
    print("2. Curator")
    print("3. EndUser")
    print("S. Sign Up")
    print("X. Exit")
    print("===========================")


def print_crud_menu():
    print("\n=== Curator Menu ===")
    print("1. Create")
    print("2. Read")
    print("3. Update")
    print("4. Delete")
    print("X. Exit")
    print("=================")

def print_admin_menu():
    print("\n=== ADMIN Menu ===")
    print("1. Create")
    print("2. Read")
    print("3. Update")
    print("4. Delete")
    print("X. Log Out")
    print("=================")

def print_user_menu():
    print("\n=== USER Menu ===")
    while True:
        query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->")
        if query != "X":
            print(f"DEBUG Query is: {query}")
            # TODO: convert query string to an embedding eg embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
            # where model is the SentenceTransformer. You can then plug in the embedding into a SQL SELECT statement
        query = input("Would you like to enter another query? (Y or Yes for a new query or anything else to exit) ")
        if query != "Y" or query != "Yes":
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
            result = sign_up()
            # res = handle_signup(email, password)
            if result == True:
                print("New EndUser successfully made.\n")
                continue    # Allow user to select a new menu option
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
        if not authenticate_user(role, email, password):
            print("Invalid credentials. Try again.")
            continue

        # successful log in
        return role_choice

# can do CRUD on the Users table
def admin_loop():
    choice = None
    while choice != "X" and choice != "":
        print_admin_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            create_user()
        elif choice == "2":
            fetch_users()
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
    pass

# can submit queries
def enduser_loop():
    # print_crud_menu():
    # print("\n=== CRUD Menu ===")
    # print("1. Create")
    # print("2. Read")
    # print("3. Update")
    # print("4. Delete")
    # print("X. Exit")
    # print("=================")
    choice = None
    while choice != "X" and choice != "":
        print_user_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            create_user()
        elif choice == "2":
            fetch_users()
        elif choice == "3":
            update_user()
        elif choice == "4":
            delete_user()
        elif choice == "X" or choice == "":
            print("Returning to role selection...")
        else:
            print("Invalid choice. Please try again.")

def main():
    """
    Handle main workflow of program. 

    Admins can do CRUD on Users table. Curators can do CRUD on Documents table.
    EndUsers can make queries.
    """
    # Step 1. Ask user for role
    # Step 2. Authenticate user credentials
    while True:
        user_role = landing_loop()
        print(f"Successfully logged in as {ROLE_MAPPING[user_role]}!")

        # Step 3. Prompt user with role specific menu
        # Step 4. Accept user input and perform specified action
        # Step 5. Repeat Step 3-4 until we recieve a log out action or program terminates
        if user_role == 1:
            admin_loop()   # can do CRUD on the Users table
        elif user_role == 2:
            curator_loop() # can do CRUD on the Documents table
        elif user_role == 3:
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