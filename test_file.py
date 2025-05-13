import math
import os

def load_index():
    """Load the index file and return the list of staged files and their hashes."""
    index_path = '.myvcs/index'
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"The index file '{index_path}' does not exist.")
    with open(index_path, 'r') as index_file:
        for line in index_file:
            path, hashed_content = line.strip().split()

            
def update_index(filepath, hash):
    """Update the index with the file path and its hash."""
    index_path = '.myvcs/index'
    with open(index_path, 'a') as index_file:
        index_file.write(f"{filepath} {hash}\n")
        
if __name__ == "__main__":
    update_index('test.txt', '1234567890abcdef')
    update_index('test2.txt', 'abcdef1234567890')
    
    load_index()