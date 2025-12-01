import psycopg2

conn = psycopg2.connect(database="postgres",
        host="localhost",
        user="postgres",
        password="postgres",
        port="5432",
        options="-c search_path=cs480_finalproject,public")

def authenticate_user(role, email, password):
    """
    Authenticate a user by role, email, and password.
    Returns the row if credentials are valid, None otherwise.
    """
    print(f"Authenticating {role} with email={email}...")
    cur = conn.cursor()

    # fetch a user with the defined email, password, and role
    users_select = """
        SELECT * FROM cs480_finalproject.users
        WHERE email = %s AND password = %s AND role = %s;
    """

    cur.execute(users_select, (email, password, role))
    result = cur.fetchone()
    print(result)
    cur.close()

    return result

def handle_signup(name, email, username, password):
    """
    Create a new EndUser by role, email, and password.
    Returns the full user row if successful, False otherwise.
    """
    print(f"Signing up a new EndUser with email={email}")
    try:
        with conn.cursor() as cur:
            # check email uniqueness
            cur.execute("SELECT 1 FROM cs480_finalproject.users WHERE email = %s;", (email,))
            if cur.fetchone() is not None:
                print("Error: Account with that email already exists.")
                return None

            # check username uniqueness
            cur.execute("SELECT 1 FROM cs480_finalproject.users WHERE username = %s;", (username,))
            if cur.fetchone() is not None:
                print("Error: Account with that username already exists.")
                return None

            # email and username are good, now actually insert it into the DB
            insert_query = """
                INSERT INTO cs480_finalproject.users (username, name, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            """
            cur.execute(insert_query, (username, name, email, password, 'EndUser')) # design choice, sign up can only add EndUser

            new_user_row = cur.fetchone()  # grab full row so main.py caller has all info
            user_id, _, _, _, _, _ = new_user_row
            # just added to Users, now add to EndUser
            insert_enduser_query = """
                INSERT INTO cs480_finalproject.enduser (end_id, latest_activity)
                VALUES (%s, NULL);
            """
            # explicitly make a new EndUser have Null
            cur.execute(insert_enduser_query, (user_id,))

            conn.commit()
            return new_user_row
    except Exception as e:
        # this should really never happen
        print("Database error during signup:", e)
        conn.rollback()
        return None

# ADMIN can create a new user
# Difference between this and handle_signup is that admin user create can make new users that aren't EndUsers
def ADMIN_user_create(name, email, role, username, password):
    """
    Create a new user in the Users table.

    Only Admins can call this.
    """
    try:
        cur = conn.cursor()
        insert_users_query = """
            INSERT INTO cs480_finalproject.users (name, email, role, username, password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
        """
        cur.execute(insert_users_query, (name, email, role, username, password))
        new_user_row = cur.fetchone()
        user_id, _, _, _, _, _ = new_user_row

        # now add the user in to the role specific table they belong to
        if role == 'EndUser':
            insert_enduser_query = """
                INSERT INTO cs480_finalproject.enduser (end_id, latest_activity)
                VALUES (%s, NULL);
            """
            # explicitly make a new EndUser have Null
            cur.execute(insert_enduser_query, (user_id,))

        elif role == 'Admin':
            insert_admin_query = """
                INSERT INTO cs480_finalproject.admin (admin_id)
                VALUES (%s);
            """
            cur.execute(insert_admin_query, (user_id,))

        elif role == 'Curator':
            insert_curator_query = """
                INSERT INTO cs480_finalproject.curator (curator_id)
                VALUES (%s);
            """
            cur.execute(insert_curator_query, (user_id,))

        conn.commit()
        cur.close()

        print(f"User created with ID {user_id}")
        return new_user_row
    except Exception as e:
        # this should really never happen
        print("Database error during Users creation:", e)
        conn.rollback()
        return None
    
# ADMIN can fetch all Users
def ADMIN_users_fetch():
    """
    Fetches all users from the Users table.
    """
    cur = conn.cursor()
    select_query = "SELECT * FROM cs480_finalproject.users;"
    cur.execute(select_query)
    users = cur.fetchall()
    cur.close()
    return users

# ADMIN can perform Users UPDATE
# we have all this optional fields because an Admin might not want to change everything, just some things
# DESIGN CHOICE: it is impossible for an admin to upgrade or degrade another user's permissions
# in other words, there is no way to change a user's role without deleting and remaking an account with that new role
def ADMIN_user_update(user_id, name=None, email=None, username=None, password=None):
    """
    Update fields for a given user_id.

    Only Admins are allowed to call this.
    """
    # print(f"User {user_id} updated successfully.")
    # all fields that we allow to be updated
    try:
        fields = {
            "username": username,
            "email": email,
            "name": name,
            "password": password,
        }

        # which fields are actually getting updated
        updates = {key: val for key, val in fields.items() if val is not None and val != ""} # disallow None of an empty string

        if not updates:
            return None

        set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
        query = f"""
            UPDATE cs480_finalproject.users
            SET {set_clause}
            WHERE user_id = %s
            RETURNING user_id;
        """
        params = list(updates.values()) + [user_id]

        with conn.cursor() as cur:
            cur.execute(query, params)
            updated_row = cur.fetchone()
            conn.commit()
        print(f"User {user_id} updated successfully.")
        return updated_row
    
    except Exception as e:
        # this could be reached if the user tries to update an email to one that already exists
        print("Database error during Users update:", e)
        conn.rollback()
        return None

# ADMIN performs Users DELETE
def ADMIN_user_delete(user_id):
    """
    Delete a user from the Users table.
    
    If User was an EndUser, delete all their QueryLogs and the logs of which documents were fetched too.
    This is handled by ON DELETE CASCADE, so we don't need additional implementation for it here.
    """
    try:
        with conn.cursor() as cur:
            # Check if the user exists and get their role
            cur.execute("SELECT 1 FROM cs480_finalproject.users WHERE user_id = %s;", (user_id,))
            result = cur.fetchone()

            if not result:
                return False  # No user with that ID

            # For EndUsers we need to get rid of all their QueryLogs, but this is handled by PostgreSQL because we have set up
            # ON DELETE CASCADE
            # if role == "EndUser":
            #     cur.execute("DELETE FROM QueryLog WHERE issuer_id = %s;", (user_id,))

            # Delete the user
            cur.execute("DELETE FROM cs480_finalproject.users WHERE user_id = %s RETURNING *;", (user_id,))
            deleted_row = cur.fetchone()

            print(f"User {user_id} delected successfully.")
            print(deleted_row)
            conn.commit()

            return deleted_row
    except Exception as e:
        # this could be reached if the user tries to update an email to one that already exists
        print("Database error during Users deletion:", e)
        conn.rollback()
        return None

# Document CREATE
def CURATOR_document_create(title, doc_type, source, added_by, processed=False):
    """
    Create a new Document in the Document table.
    Only Curators can call this.
    """
    try:
        cur = conn.cursor()
        insert_query = """
            INSERT INTO cs480_finalproject.document (title, type, source, added_by, processed)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
        """
        cur.execute(insert_query, (title, doc_type, source, added_by, processed))
        new_doc_row = cur.fetchone()
        doc_id, _, _, _, _, _, _ = new_doc_row
        conn.commit()
        cur.close()

        print(f"Document added with ID {doc_id}")
        return new_doc_row
    except Exception as e:
        print("Database error during document creation:", e)
        conn.rollback()
        return None

# Document READ
def CURATOR_documents_fetch(cur_id=None):
    """
    Fetches all documents from the Document table.

    Optional cur_id parameter to determine if we should fetch every document, or just ones that the caller had added.
    """
    cur = conn.cursor()
    select_query = ""
    if cur_id is not None:
        select_query = "SELECT * FROM cs480_finalproject.document WHERE added_by = %s"
        cur.execute(select_query, (cur_id,))
    else:
        select_query = "SELECT * FROM cs480_finalproject.document;"
        cur.execute(select_query)
    docs = cur.fetchall()
    cur.close()
    return docs

# Document UPDATE
# DESIGN CHOICE: Curators can not override "timestamp", "added_by", or "source"
# source indirectly determines document ID, so it must not be overridden
def CURATOR_document_update(cur_id, doc_id, title=None, doc_type=None, processed=None):
    """
    Update fields for a given document_id.
    Only Curators are allowed to call this.
    """
    try:
        with conn.cursor() as cur:
            # Check if the document exists and that caller curator owns the document
            cur.execute("SELECT 1 FROM cs480_finalproject.document WHERE added_by = %s AND doc_id = %s;", (cur_id, doc_id))
            result = cur.fetchone()

            if not result:
                print("Error: Curator does not own this document, or maybe it doesn't exist.")
                return None

            # Build update fields
            fields = {
                "title": title,
                "type": doc_type,
                "processed": processed,
            }
            updates = {key: val for key, val in fields.items() if val is not None and val != ""}
            if not updates:
                return None

            set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
            query = f"""
                UPDATE cs480_finalproject.document
                SET {set_clause}
                WHERE doc_id = %s
                RETURNING *;
            """
            params = list(updates.values()) + [doc_id]

            # Execute update on same cursor
            cur.execute(query, params)
            updated_row = cur.fetchone()

            conn.commit()
            print(f"Document {doc_id} updated successfully.")
            return updated_row

    except Exception as e:
        print("Database error during document update:", e)
        conn.rollback()
        return None


# Document DELETE
def CURATOR_document_delete(cur_id, doc_id):
    """
    Delete a document from the Document table.
    Only allows the owning Curator to delete the document.
    """
    try:
        with conn.cursor() as cur:
            # Check if the document exists and that caller curator owns the document
            cur.execute("SELECT 1 FROM cs480_finalproject.document WHERE added_by = %s AND doc_id = %s;", (cur_id, doc_id))
            result = cur.fetchone()

            if not result:
                print("Error: Curator does not own this document, or maybe it doesn't exist.")
                return None

            # Delete the document
            cur.execute("DELETE FROM cs480_finalproject.document WHERE doc_id = %s RETURNING *;", (doc_id,))
            deleted_row = cur.fetchone()
            print(f"Document {doc_id} deleted successfully.")
            print(deleted_row)
            conn.commit()

            return deleted_row
    except Exception as e:
        print("Database error during document delete:", e)
        conn.rollback()
        return None