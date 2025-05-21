import math
import os
import time

def load_index():
    """Load the index file and return the list of staged files and their hashes."""
    index_path = '.myvcs/index'
    index_data = []
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"The index file '{index_path}' does not exist.")
    with open(index_path, 'r') as index_file:
        for line in index_file:
            path, hashed_content = line.strip().split()
            index_data.append([path,hashed_content])
    return index_data
            
def update_index(filepath, hash):
    """Update the index with the file path and its hash."""
    index_path = '.myvcs/index'
    with open(index_path, 'a') as index_file:
        index_file.write(f"{filepath} {hash}\n")
    
#! add cases where the file does not exist or is empty
def log_commit(n_commit):
    head_path = ".myvcs/HEAD"
    with open(head_path, 'r') as head:
        head_data = head.read().strip()
    if head_data == '':
        raise ValueError(f"The HEAD file is empty.")
    master_path = os.path.join('.myvcs', head_data)
    with open(master_path, 'r') as master:
        master_data = master.read().strip()
    
    commit_path = os.path.join('.myvcs/objects', master_data)
    with open(commit_path, 'r') as commit:
        
        commit_data = commit.read().strip()
    while n_commit > 0 and commit_data.startswith('parent'):
        n_commit -= 1
        commit_path = os.path.join('.myvcs/objects', commit_data)
        with open(commit_path, 'r') as commit:
            commit_data = commit.read().strip()
            
        print("Log commit data:")
        print(commit_data)

def list_all_files(root_dir=".", ignore_list=None):
    """
    Return a list of *relative* file paths for everything under root_dir,
    excluding any files or folders in ignore_list.
    
    ignore_list: list of folder or file names to ignore (e.g. ['.myvcs', 'temp.txt'])
    """
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

if __name__ == "__main__":

    commit_data = """tree 355f4349419e523a9b254e4b13ebb98fff5dc363
                author marioRMReis <mario_rmr@hotmail.com> 
                timestamp 1747578311
                message First commit
            """
    
    ignore_list = ['.myvcs', '.git', 'myvcs.py', 'myvcs.py', '.vscode', '.myvcsignore']
    all_files = list_all_files(ignore_list=ignore_list)
    print(all_files)
    
            
