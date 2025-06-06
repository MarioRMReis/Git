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
    
if __name__ == "__main__":

    commit_data = """tree 355f4349419e523a9b254e4b13ebb98fff5dc363
                author marioRMReis <mario_rmr@hotmail.com> 
                timestamp 1747578311
                message First commit
            """
    
    lines = commit_data.split('\n')
    for line in lines:
        print(line.strip().split())