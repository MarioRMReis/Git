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
        
    # Chech if the HEAD file contains the path to the main  
    if head_path_data == '':
        raise ValueError(f"The HEAD file is empty.")
    
    # Check if main exists
    if not os.path.exists(os.path.join('.myvcs', head_path_data)):
        raise FileNotFoundError(f"The HEAD file '{head_path_data}' does not exist.")

    # Main path is the contents of head_date
    main_path = os.path.join('.myvcs', head_path_data)
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"The main file '{main_path}' does not exist.")
    
    # Read the main file and get the commit hash
    with open(main_path, 'r') as main:
        hash_path = main.read().strip()

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
            os.makedirs('.myvcs/refs/branches')
            with open('.myvcs/HEAD', 'w') as head_file:
                # Create the HEAD file with default branch
                head_file.write('refs/branches/main\n')
        else:
            # In case the directory exists, we can check if the necessary subdirectories and files exist and create them if they don't
            os.makedirs('.myvcs/objects', exist_ok=True)
            os.makedirs('.myvcs/refs', exist_ok=True)
            if not os.path.exists('.myvcs/HEAD'):
                with open('.myvcs/HEAD', 'w') as head_file:
                    # Create the HEAD file with default branch
                    head_file.write('refs/branches/main\n')
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
    if not os.path.exists('.myvcs/refs/branches/main') or os.path.getsize('.myvcs/refs/branches/main') == 0:
        commit_content = f"""
                tree {tree_hash}
                author {aurhor_name} <{author_email}> 
                timestamp {timestamp}
                message {message}
            """
    else:
        # Get the hash of the previous commit (in refs/main)
        with open('.myvcs/refs/branches/main', 'r') as main:
            main_hash = main.read().strip()
        # Commit content with the previous commit's hash
        commit_content = f"""
            tree {tree_hash}
            parent {main_hash}
            author {aurhor_name} <{author_email}> 
            timestamp {timestamp}
            message {message}
        """
    commit_hash = hashlib.sha1(commit_content.encode()).hexdigest()
    
    # Create the commit object   
    commit_path = f'.myvcs/objects/{commit_hash}'
    with open(commit_path, 'w') as commit_file:
        commit_file.write(commit_content)
        
    # Update HEAD to point to the new commit (in refs/main)
    with open('.myvcs/refs/branches/main', 'w') as ref_file:
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
    ignore_list.extend(['.myvcs', '.git', 'myvcs.py', '.myvcsignore', '.vscode'])
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

def status_check(log_status=True):
    with open('.myvcs/HEAD','r') as head_file:
        main_path = head_file.read().strip()
    
    if main_path == '':
        print('No commits yet!')
        return
    else:
        with open(os.path.join('.myvcs', main_path), 'r') as main_file:
            main_hash = main_file.read().lstrip()
    
    with open(os.path.join('.myvcs/objects', main_hash)) as commit_content:
        commit = commit_content.read().strip().splitlines()
    
    if os.path.exists('.myvcsignore'):
        with open('.myvcsignore') as ignore_file:
            ignore_content = ignore_file.read().strip().splitlines()
    else:
        ignore_content = None
    all_files = list_all_files(ignore_list=ignore_content)
    
    tree_hash = next((ln for ln in commit if "tree" in ln), None).split()[1]
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
    
    if log_status == True:
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
    else:
        return status_bulk

def checkout(commit, force):
    def get_user_confirmation(message):
        while True:
            response = input(message).strip().lower()
            if response == 'yes' or response == 'y':
                break
            elif response == 'no' or response == 'n':
                break
        if response == 'yes' or response == 'y':
            print('\n')
            pass
        elif response == 'no' or response == 'n':
            raise SystemExit("Checkout aborted.")
    
    # If force is True skips the warnings
    if not force:
        # [[modified], [unmodified], [new], [untracked]]
        status = status_check(log_status=False)
        if status[0] != [] or status[2] != [] or status[3] != []:
            if status[0] != []:
                print(f'The following files have been modified\n')
                for modified_file in status[0]:
                    print(f"{modified_file}\n")
                message = "These files will be OVERWRITTEN. Do you want to continue? (yes/no)/(y/n): "
                get_user_confirmation(message)
                
            if status[2] != []:
                print(f'The following files have been added\n')
                for added_file in status[2]:
                    print(f"{added_file}\n")
                message = "These files in the staged area will be DELETED. Do you want to continue? (yes/no)/(y/n): "
                get_user_confirmation(message)
            
            if status[3] != []:
                print(f'The following files have been untracked\n')
                for untracked_file in status[3]:
                    print(f"{untracked_file}\n")
                message = "These files will be DELETED. Do you want to continue? (yes/no)(y/n): "
                get_user_confirmation(message)

    # Get all files in the project, outside the .myvcsignore file
    if os.path.exists('.myvcsignore'):
        with open('.myvcsignore') as ignore_file:
            ignore_content = ignore_file.read().strip().splitlines()
    else:
        ignore_content = None
    all_files = list_all_files(ignore_list=ignore_content)
    
    # Remove all files from the project
    for file in all_files:
        os.remove(file)
        folder = os.path.dirname(file)
        if folder != '':
            if not os.listdir(folder):
                os.rmdir(folder)
                
    if os.path.exists('.myvcs/refs/tags'):
        tags = os.listdir('.myvcs/refs/tags')

    # If main was selected changes the commit_hash to the hash of the current main
    if commit == 'main':
        head_path = ".myvcs/HEAD"
        # Check if HEAD file exists
        if not os.path.exists(head_path):
            raise FileNotFoundError(f"The HEAD file does not exist.")
        with open(head_path, 'r') as head:
            head_path_data = head.read().strip()
        # Check if main exists
        if not os.path.exists(os.path.join('.myvcs', head_path_data)):
            raise FileNotFoundError(f"The HEAD file '{head_path_data}' does not exist.")
        # main path is the contents of head_date
        main_path = os.path.join('.myvcs', head_path_data)
        # Read the main file and get the commit hash
        with open(main_path, 'r') as main:
            commit = main.read().strip()
            
    elif commit in tags:
        tag_path = os.path.join('.myvcs/refs/tags',commit)
        with open(tag_path,'r') as tag:
            commit =tag.read().strip()
            
    # Get information about the commit about to be restored
    commit_path = os.path.join('.myvcs/objects',commit)
    with open(commit_path,'r') as commit_data:
        lines = commit_data.read().strip().splitlines()
    for line in lines:
        line_data = line.strip().split()
        if line_data[0] == 'tree':
            tree_hash = line_data[1]
            tree_path = os.path.join('.myvcs/objects',tree_hash)
            
    # Restore the files from the commit
    with open(tree_path, 'r') as tree_file:
        tree_data = tree_file.read().strip().splitlines()
        for line in tree_data:
            tree_line = line.strip().split()
            with open(os.path.join('.myvcs\objects',tree_line[0]), 'rb') as hash_file:
                hash_bytes = hash_file.read()
            
            # Make sure the folder exists before creating the file
            folder = os.path.dirname(tree_line[1])
            if folder != '':
                os.makedirs(folder, exist_ok=True)
            
            with open(tree_line[1], 'wb') as file:
                file.write(hash_bytes)

def add_tag(tag_name):
    os.makedirs('.myvcs/refs/tags', exist_ok=True)
    tags = os.listdir('.myvcs/refs/tags')
    
    # Invalid tag name check
    if '/' in tag_name or tag_name == '':
        raise ValueError("Invalid tag name.")
    
    if tag_name in tags:
        raise ValueError(f"Tag '{tag_name}' already exists.")
    
    with open('.myvcs/HEAD', 'r') as head:
        head_path = head.read().strip()
    if head_path == '':
        raise ValueError('HEAD file is empty.')
    
    with open(os.path.join('.myvcs', head_path), 'r') as main:
        main_hash = main.read().strip()
    
    with open('.myvcs/refs/tags/' + tag_name, 'w') as tag:
        tag.write(main_hash)
    
    print(f'Tag created successfully. Tag: {tag_name}')


def branch(name, list_flag, delete, switch, merge, into):
    """[name:Str, list_flag:bool, delete:str, switch:str, merge:str]"""
    os.makedirs('.myvcs/refs/branches', exist_ok=True)

    def branch_create(branch_name_create):
        with open('.myvcs/HEAD', 'r') as head:
            current_head = head.read().strip()  
            
        with open(f'.myvcs/refs/branches/{current_head}', 'r') as main:
            main_hash = main.read().strip()
        with open(f'.myvcs/refs/branches/{branch_name_create}', 'w') as new_branch:
            new_branch.write(main_hash)
        with open('.myvcs/HEAD', 'w') as head:
            head.write(f'.myvcs/refs/branches/{branch_name_create}')    
        print(f'From {current_head}, branch {branch_name_create} was created successfully.')
        
    def branch_list():
        print('Branches:')
        branches = os.listdir('.myvcs/refs/branches')
        for branch in branches:
            print('     ' + branch)
            
    def branch_delete(branch_name_delete):
        if os.path.exists(f'.myvcs/refs/branches/{branch_name_delete}'):
            os.remove(f'.myvcs/refs/branches/{branch_name_delete}')
            with open('.myvcs/HEAD', 'w') as head:
                head.write('.myvcs/refs/branches/main') 
        else:
            raise ValueError(f'The given branch does not exist.{branch_name_delete}')
        
        print(f'Branch {branch_name_delete} deleted successfully.')
    
    def branch_switch(branch_name_switch):
        if os.path.exists(f'.myvcs/refs/branches/{branch_name_switch}'):
            with open('.myvcs/HEAD', 'w') as head:
                head.write(f'.myvcs/refs/branches/{branch_name_switch}') 
        else:
            raise ValueError(f'The given branch does not exist.{branch_name_switch}')
        print(f'Switched to branch: {branch_name_switch}')
    
    def branch_merge(branch_name_merge, branch_into):
        if not os.path.exists(f'.myvcs/refs/branches/{branch_name_merge}'):
            raise ValueError(f'The given branch does not exist.{branch_name_merge}')
        if not os.path.exists(f'.myvcs/refs/branches/{branch_into}'):
            raise ValueError(f'The given branch does not exist.{branch_into}')
        
        with open(f'.myvcs/refs/branches/{branch_name_merge}', 'r') as merge:
            hash_merge = merge.read().strip()
        with open(f'.myvcs/refs/branches/{branch_into}', 'w') as into:
            into.write(hash_merge)
        
        print(f"Branch '{branch_name_merge}' merged into '{branch_into}' successfully.")
        
    if name != None:
        branch_create(name)
    elif delete != None:
        branch_delete(delete)
    elif switch != None:
        branch_switch(switch)
    elif merge != None:
        branch_merge(merge, into)
    elif list_flag:
        branch_list()
    else:
        raise ValueError("Invalid command.")
    
def create_parser():
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Simple version control system")
    subparsers = parser.add_subparsers(dest="command")

    # 'init' command
    init_parser = subparsers.add_parser('init', help="Initialize a new version control repository")
    init_parser.add_argument("-n", "--author_name", help="Your name (author)")
    init_parser.add_argument("-e","--author_email", help="Your email (author)")

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
    
    # 'checkout' command
    checkout_parser = subparsers.add_parser("checkout", help="Restore Files from a given commit.")
    checkout_parser.add_argument("-ch", "--commit_hash", type=str, default=None, help="Use log command to see copy the hash.")
    checkout_parser.add_argument("-f", "--force", action='store_true', help="Force checkout.")
    
    # 'tag' command
    tag_parser = subparsers.add_parser("tag", help="Add a tag to the current commit.")
    tag_parser.add_argument("-tn", "--tag_name", type=str, default=None, help="Name of the tag.") 
    
    # 'branch' command
    branch_parser = subparsers.add_parser("branch", help="")
    branch_parser.add_argument("-cb", "--name", type=str, default=None, help="Creates a new branch with the given name.")
    branch_parser.add_argument("-l", "--list", default=None, help="Lists all the branches.", action='store_true')
    branch_parser.add_argument("-d", "--delete", type=str, default=None, help="Deletes the branch with the given name, if exists.")
    branch_parser.add_argument("-ch","--change_branch", type=str, default=None, help="Changes from the current brange to the given branch.")
    branch_parser.add_argument("-m","--merge", type=str, default=None, help="Merges the current branch with the given branch")
    branch_parser.add_argument("-i", "--into", type=str, default='main', help="The default merge will be MAIN, but you can pick another branch to merge into.")
    return parser  
    
def func_main():
    """Main function to handle the command-line interaction."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == 'init':
        initialize_vcs(args.author_name, args.author_email)
        print("Version control system initialized.")
    elif args.command == 'add':
        add_file(args.filepath)
    elif args.command == 'commit':
        create_commit(args.message)
    elif args.command == 'log':
        log_commit(args.number)
    elif args.command == 'status':
        status_check()
    elif args.command == 'checkout':
        checkout(args.commit_hash, args.force)
    elif args.command == 'tag':
        add_tag(args.tag_name)
    elif args.command == 'branch':
        branch(args.name, args.list, args.delete, args.change_branch, args.merge, args.into)
    else:
        print("Invalid command. Use 'help' for a list of commands.")
        
if __name__ == "__main__":
    func_main()