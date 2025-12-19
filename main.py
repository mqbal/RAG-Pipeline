import sys
import database_helper  # handles database operations
import pdf_helper
import answer_queries

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

def create_doc(curator_id):
    print("Adding a new Document...")

    new_path = ""
    while new_path == "":
        new_path = input("  Provide path to pdf relative to project root: ").strip()    # path up to and including the .pdf file extension

    is_new_file = pdf_helper.extract_pdf(new_path)    # makes a .txt file in the TXT_OUTPUT_DIRECTORY, if not already existing

    if is_new_file is False:    # document already existed
        print("Document already exists in system...")
        return None

    title = ""
    while title == "":
        title = input("  Enter document title: ").strip()

    doc_type = ""
    while doc_type == "":
        doc_type = input("  Enter document type: ").strip()

    source = ""
    while source == "":
        source = input("  Enter source path: ").strip()

    ret = database_helper.CURATOR_document_create(title=title, doc_type=doc_type, source=source, added_by=curator_id, processed=False)
    # added new doc to Document table, now add to index
    if ret is not None:
        answer_queries.add_document_to_index(new_path)
    return ret
    
def fetch_docs(curator_id):
    print("  1. Fetch Your Documents")
    print("  2. Fetch All Documents")
    choice = None
    while choice != "X" and choice != "":
        choice = input("  Select an option (1-2, X to exit): ").strip()

        if choice == "1":
            print("  Your Documents: ")
            return database_helper.CURATOR_documents_fetch(cur_id=curator_id)
        elif choice == "2":
            print("  All Documents: ")
            return database_helper.CURATOR_documents_fetch()
        elif choice == "X" or choice != "":
            return None
        else:
            print("Invalid choice. Try again.")

def update_doc(curator_id):
    print("Updating a Document's information...")

    Update_ID = input("Enter the ID of the Document you'd like to update: ").strip()
    if not Update_ID:
        print("Document ID is required.")
        return

    print("Leave any field blank to keep it unchanged.\n")

    title = input("New title (or press Enter to skip): ").strip()
    doc_type = input("New type (or press Enter to skip): ").strip()
    source = input("New source (or press Enter to skip): ").strip()

    processed_input = input("Processed? (yes/no, or press Enter to skip): ").strip().lower()
    if processed_input == "yes":
        processed = True
    elif processed_input == "no":
        processed = False
    else:
        processed = None  # unchanged

    return database_helper.CURATOR_document_update(cur_id=curator_id, doc_id=Update_ID, title=title, doc_type=doc_type, source=source, processed=processed)

def delete_doc(curator_id):
    print("Deleting a Document...")
    delete_id = ""
    while delete_id == "":
        delete_id = input("Enter the ID of the Document you'd like to delete: ").strip()
    return database_helper.CURATOR_document_delete(curator_id, delete_id)

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
    print("4. Edit Document")
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
def curator_loop(curator_id):
    choice = None
    while choice != "X" and choice != "":
        print_curator_menu()
        choice = input("Select an option (1-4, X to exit): ").strip()

        if choice == "1":
            create_doc(curator_id)
        elif choice == "2":
            fetched = fetch_docs(curator_id)
            if fetched is not None:
                for doc in fetched:
                    print(doc)
        elif choice == "3":
            delete_doc(curator_id)
        elif choice == "4":
            update_doc(curator_id)
        elif choice == "X" or choice == "":
            print("Returning to role selection...")
        else:
            print("Invalid choice. Please try again.")

# can submit queries
def enduser_loop(enduser_id):
    print("\n=== USER Menu ===")
    top_k = answer_queries.queryDB(enduser_id)


def main():
    # print(database_helper.ADMIN_users_fetch())
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
            curator_loop(user_id) # can do CRUD on the Documents table
        elif user_role == "EndUser":
            enduser_loop(user_id) # can submit queries
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