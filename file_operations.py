import os
import tempfile


# Function to log a user's reaction to a file
def log_reaction(user_id, reaction):
    with open("reactions.txt", "a") as file:
        file.write(f"{user_id},{reaction}\n")
    print(f"Logged reaction {reaction} from user {user_id}")


# Function to read reactions from a file
def read_reactions():
    reactions = {}
    try:
        with open("reactions.txt", "r") as file:
            for line in file:
                user_id, reaction = line.strip().split(',')
                if user_id in reactions:
                    reactions[user_id].append(reaction)
                else:
                    reactions[user_id] = [reaction]
    except FileNotFoundError:
        print("No reactions file found.")
    return reactions


# Function to clear reaction logs
def clear_reaction_logs():
    open("reactions.txt", "w").close()


# Function to store the timestamp of the last post
def store_message_ts(timestamp):
    temp_file_path = ""
    try:
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', dir='.') as tmpfile:
            temp_file_path = tmpfile.name
            tmpfile.write(timestamp)

        # Rename temp file replacing the old file
        os.replace(temp_file_path, "timestamp_of_last_post.txt")
    except Exception as e:
        print(f"Failed to write timestamp: {e}")
        # Cleanup if the rename failed
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


# Function to get the weekly timestamp from the last post
def get_current_weekly_message_ts():
    try:
        with open("timestamp_of_last_post.txt", "r") as file:
            timestamp = file.read().strip()
            print(f"Found timestamp from file: {timestamp}")
            return timestamp
    except FileNotFoundError:
        print("Timestamp file not found. Ensure the message is posted first.")
        return None
    except IOError as e:
        print(f"Error reading timestamp file: {e}")
        return None

