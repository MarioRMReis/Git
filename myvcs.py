import argparse
import hashlib
import time
import os

def load_index():
    """Load the index file and return the list of staged files and their hashes."""
    index_path = '.myvcs/index'
    index_data = {}
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"The index file '{index_path}' does not exist.")
    with open(index_path, 'r') as index_file:
        for line in index_file:
            path, hashed_content = line.strip().split()
            index_data[path] = hashed_content
    return index_data
            

def update_index(filepath, hash):
    """Update the index with the file path and its hash."""
    index_path = '.myvcs/index'
    with open(index_path, 'a') as index_file:
        index_file.write(f"{filepath} {hash}\n")
    
def add_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    if not os.path.isfile(filepath):
        raise ValueError(f"The path '{filepath}' is not a file.")
    # Inform the user that the file is being added to the staging area
    print(f"Adding file '{filepath}' to the staging area...")  
    
    with open(filepath, 'rb') as file:
        content = file.read()
        
    hashed_content = hashlib.sha1(content).hexdigest()
    # Create the object file in the .myvcs/objects directory
    with open(f'.myvcs/objects/{hashed_content}', 'wb') as object_file:
        object_file.write(content)
    
    # Update the index with the file path and its hash
    update_index(filepath, hashed_content)
        
def initialize_vcs():
    """Initialize the version control system by creating necessary directories and files."""
    try:
        # Check if .myvcs/ already exists
        if not os.path.exists('.myvcs'):
            # If not, create the directory structure
            os.makedirs('.myvcs/objects', exist_ok=True)
            os.makedirs('.myvcs/refs', exist_ok=True)
            with open('.myvcs/HEAD', 'w') as head_file:
                # Create the HEAD file with default branch
                head_file.write('refs/master\n')
        else:
            # In case the directory exists, we can check if the necessary subdirectories and files exist and create them if they don't
            os.makedirs('.myvcs/objects', exist_ok=True)
            os.makedirs('.myvcs/refs', exist_ok=True)
            if not os.path.exists('.myvcs/HEAD'):
                with open('.myvcs/HEAD', 'w') as head_file:
                    # Create the HEAD file with default branch
                    head_file.write('refs/master\n')
    except PermissionError:
        print("Error: Permission denied. Please run this script with appropriate permissions.")
    except OSError as e:
        print(f"Error: {e.strerror}. Please check your file system.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def create_parser():
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Simple version control system")
    subparsers = parser.add_subparsers(dest="command")

    # 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize the version control system")
    init_parser.set_defaults(func=initialize_vcs)
    
    # 'add' command
    add_parser = subparsers.add_parser("add", help="Stage a file for commit")
    add_parser.add_argument("filepath", help="Path to the file to add")

    # 'commit' command
    commit_parser = subparsers.add_parser("commit", help="Commit staged files")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    
    return parser

def main():
    """Main function to handle the command-line interaction."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "init":
        initialize_vcs()
        print("Version control system initialized.")
    elif args.command == "add":
        add_file(args.filepath)
    elif args.command == "commit":
        create_commit(args.message)

if __name__ == "__main__":
    main()