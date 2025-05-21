import argparse
import hashlib
import time
import os

def load_index():
    """Load the index file and return the list of staged files and their hashes."""
    index_path = '.myvcs/index'
    index_data = []
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"The index file '{index_path}' does not exist.")
    with open(index_path, 'r') as index_file:
        for line in index_file:
            path, hashed_content = line.strip().split()
            index_data.append([hashed_content, path])
            
    return index_data

def log_commit(n_commit):
    """Log commit prints out N most recent commits."""
    head_path = ".myvcs/HEAD"
    # Check if HEAD file exists
    if not os.path.exists(head_path):
        raise FileNotFoundError(f"The HEAD file does not exist.")
    with open(head_path, 'r') as head:
        head_path_data = head.read().strip()
        
    # Chech if the HEAD file contains the path to the master  
    if head_path_data == '':
        raise ValueError(f"The HEAD file is empty.")
    
    # Check if master exists
    if not os.path.exists(os.path.join('.myvcs', head_path_data)):
        raise FileNotFoundError(f"The HEAD file '{head_path_data}' does not exist.")

    # Master path is the contents of head_date
    master_path = os.path.join('.myvcs', head_path_data)
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"The master file '{master_path}' does not exist.")
    
    # Read the master file and get the commit hash
    with open(master_path, 'r') as master:
        hash_path = master.read().strip()

    for i in range(n_commit):
        # Parent flag initiated as False in each iteration of the loop, idicates the existance of a previous commit
        parent = False

        commit_path = os.path.join('.myvcs/objects', hash_path)
        
        # Raise error if the path doesn't exist
        if not os.path.exists(commit_path):
            raise FileNotFoundError(f"The commit file '{commit_path}' does not exist.")
    
        with open(commit_path, 'r') as commit:
            commit_data = commit.read().strip()
            
        lines = commit_data.split('\n')
        print(f"Commit: {hash_path}")
        for line in lines:
            line_data = line.strip().split()
            if line_data[0] == 'tree':
                print(f"Tree: {line_data[1]}")
                with open(os.path.join('.myvcs/objects', line_data[1]), 'r') as tree_content:
                    tree_files = tree_content.read().strip()
                for idx, file in enumerate(tree_files.splitlines()):
                    if idx == 0:
                        print(f"File(s): {file}")
                    else:
                        print(f"      {file}")
            elif line_data[0] == 'parent':
                print(f"Parent: {line_data[1]}")
                hash_path = line_data[1]
                # Flag set as true to indicate that the current commit has a parent
                parent = True
            elif line_data[0] == 'author':
                print(f"Author: {line_data[1]}")
                print(f"Email: {line_data[2]}")
            elif line_data[0] == 'timestamp':
                timestamp_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(line_data[1])))
                print(f"Timestamp: {timestamp_readable}")
            elif line_data[0] == 'message':
                print(f"Message: {' '.join(line_data[1:])}")

        # If no parent commit is found, print a message and return
        if parent == False:
            print("\n(No more commits to print.)")
            return
        print("\n")

def update_index(filepath, hash):
    """Update the index with the file path and its hash."""
    index_path = '.myvcs/index'
    with open(index_path, 'a') as index_file:
        index_file.write(f"{filepath} {hash}\n")
    
def add_file(filepath):
    """Add a file to the staging area."""
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
        
def initialize_vcs(author_name, author_email):
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
        with open('.myvcs/config', 'w') as config_file:
            # Create the config file with author information
            config_file.write(f"author_name={author_name}\n")
            config_file.write(f"author_email={author_email}\n")
    except PermissionError:
        print("Error: Permission denied. Please run this script with appropriate permissions.")
    except OSError as e:
        print(f"Error: {e.strerror}. Please check your file system.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def author_info():
    config_path = '.myvcs/config'
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The config file '{config_path}' does not exist.")
    with open(config_path, 'r') as config_file:
        config_data = config_file.readlines()
    author_name = config_data[0].split('=')[1].strip()
    author_email = config_data[1].split('=')[1].strip()
    
    return author_name, author_email

def create_commit(message):
    staged_files = load_index()
    
    if not staged_files:
        raise ValueError("No files staged for commit.")
    
    tree_content = "".join(f'{file[0]} {file[1]}\n' for file in staged_files)
    tree_hash = hashlib.sha1(tree_content.encode()).hexdigest()
    
    # Save the tree to the objects directory so we can know what has been modified in the commit
    with open(f".myvcs/objects/{tree_hash}", "w") as tree_file:
        tree_file.write(tree_content)

    aurhor_name, author_email = author_info()
    
    timestamp = int(time.time())
    if not os.path.exists('.myvcs/refs/master') or os.path.getsize('.myvcs/refs/master') == 0:
        commit_content = f"""
                tree {tree_hash}
                author {aurhor_name} <{author_email}> 
                timestamp {timestamp}
                message {message}
            """
    else:
        # Get the hash of the previous commit (in refs/master)
        with open('.myvcs/refs/master', 'r') as master:
            master_hash = master.read().strip()
        # Commit content with the previous commit's hash
        commit_content = f"""
            tree {tree_hash}
            parent {master_hash}
            author {aurhor_name} <{author_email}> 
            timestamp {timestamp}
            message {message}
        """
    commit_hash = hashlib.sha1(commit_content.encode()).hexdigest()
    
    # Create the commit object   
    commit_path = f'.myvcs/objects/{commit_hash}'
    with open(commit_path, 'w') as commit_file:
        commit_file.write(commit_content)
        
    # Update HEAD to point to the new commit (in refs/master)
    with open('.myvcs/refs/master', 'w') as ref_file:
        ref_file.write(commit_hash)

    # Clear the index after commit
    with open('.myvcs/index', 'w') as index_file:
        index_file.write("")
    
    print(f"Commit created with hash: {commit_hash}")
    
    return commit_hash

def list_all_files(root_dir=".", ignore_list=None):
    """
    Return a list of *relative* file paths for everything under root_dir,
    excluding any files or folders in ignore_list.
    
    ignore_list: list of folder or file names to ignore (e.g. ['.myvcs', 'temp.txt'])
    """
    ignore_list.extend(['.myvcs', '.git', 'myvcs.py', 'myvcs.py', '.myvcsignore'])
    if ignore_list is None:
        ignore_list = []

    all_paths = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove ignored folders from dirnames so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in ignore_list]

        for fname in filenames:
            # Skip ignored files
            if fname in ignore_list:
                continue

            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir)
            all_paths.append(rel_path)
            
    return all_paths

def status_check():
    with open('.myvcs/HEAD','r') as head_file:
        master_path = head_file.read().strip()
    
    if master_path == '':
        print('No commits yet!')
        return
    else:
        with open(os.path.join('.myvcs', master_path), 'r') as master_file:
            master_hash = master_file.read().lstrip()
    
    with open(os.path.join('.myvcs/objects', master_hash)) as commit_content:
        commit = commit_content.read().strip().splitlines()
        
    tree_hash = next((ln for ln in commit if "tree" in ln), None).split()[1]
    if os.path.exists('.myvcsignore'):
        with open('.myvcsignore') as ignore_file:
            ignore_content = ignore_file.read().strip().splitlines()
            all_files = list_all_files(ignore_list=ignore_content)

    with open(os.path.join('.myvcs/objects', tree_hash)) as tree:
        tree = tree.read().strip().splitlines()

    with open('.myvcs/index') as index:
        staged = index.read().strip().splitlines()
        
    tree_files = []
    hash_existFile = []
    for file in tree:
        tree_files.append(file.split()[1])
        hash_existFile.append(file.split()[0])

    staged_files = []
    for file_staged in staged:
        staged_files.append(file_staged.split()[0])
        
    status = []
    for a_file in all_files:
        if a_file in tree_files:
            idx = tree_files.index(a_file)
            with open(a_file, 'rb') as file:
                content = file.read()
            current_hash = hashlib.sha256(content).hexdigest()
            if hash_existFile[idx] != current_hash:
                status.append([a_file, 'modified'])
            else:
                status.append([a_file, 'unmodified'])
        elif a_file in staged_files:
            status.append([a_file, 'new'])
        elif a_file not in tree_files:
            status.append([a_file, 'untracked'])
            
    # =============================== Print out Status  ==============================
    # modified, unmodified, new, untracked
    status_bulk = [[],[],[],[]]
    for status_file in status:
        if status_file[1] == 'modified':
            status_bulk[0].append(status_file[0])
        elif status_file[1] == 'unmodified':
            status_bulk[1].append(status_file[0])
        elif status_file[1] == 'new':
            status_bulk[2].append(status_file[0])
        elif status_file[1] == 'untracked':
            status_bulk[3].append(status_file[0]) 
    
    # print out the status
    print("Status:")
    print("modified:\n", end="     ")
    for file in status_bulk[0]:
        print(file, end="\n")
    print()
    print("unmodified:\n", end="     ")
    for file in status_bulk[1]:
        print(file, end="\n")
    print()
    print("new:\n", end="     ")
    for file in status_bulk[2]:
        print(file, end="\n")
    print()
    print("untracked:\n", end="     ")
    for file in status_bulk[3]:
        print(file, end="\n")

def create_parser():
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Simple version control system")
    subparsers = parser.add_subparsers(dest="command")

    # 'init' command
    init_parser = subparsers.add_parser('init', help="Initialize a new version control repository")
    init_parser.add_argument("author_name", help="Your name (author)")
    init_parser.add_argument("author_email", help="Your email (author)")

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Stage a file for commit")
    add_parser.add_argument("filepath", help="Path to the file to add")

    # 'commit' command
    commit_parser = subparsers.add_parser("commit", help="Commit staged files")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    
    # 'log' command
    log_parser = subparsers.add_parser("log", help="Show commit logs")
    log_parser.add_argument("-n", "--number", type=int, default=1, help="Number of commits to show")
    
    # 'status' command
    subparsers.add_parser("status", help="Show the current status")
    
    return parser

def main():
    """Main function to handle the command-line interaction."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "init":
        initialize_vcs(args.author_name, args.author_email)
        print("Version control system initialized.")
    elif args.command == "add":
        add_file(args.filepath)
    elif args.command == "commit":
        create_commit(args.message)
    elif args.command == "log":
        log_commit(args.number)
    elif args.command == "status":
        status_check()

if __name__ == "__main__":
    main()