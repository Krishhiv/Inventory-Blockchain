import hashlib
import base64

class MerkleNode:
    def __init__(self, value):
        self.data = value
        self.left = None
        self.right = None
        self.parent = None

class MerkleTree:
    def __init__(self):
        self.public_keys = []  # List of Tuples, each a leaf node
        self.root = None

    def add_block_keys(self, creation_pubkey_b64, sale_pubkey_b64=None):
        """ Adds new public key pair to the tree and rebuilds it. """
        self.public_keys.append((creation_pubkey_b64, sale_pubkey_b64 or ""))
        self._build_merkle_tree()

    def _build_merkle_tree(self):
        """ Constructs a Merkle Tree from the stored keys. """
        if not self.public_keys:
            return

        # Step 1: Create leaf nodes
        nodes = []
        for creation_key, sale_key in self.public_keys:
            node0 = MerkleNode(creation_key)  
            node1 = MerkleNode(sale_key)
            parent_hash = hashlib.sha256((creation_key + sale_key).encode()).hexdigest()
            parent = MerkleNode(parent_hash)
            parent.left = node0
            parent.right = node1
            node0.parent = parent
            node1.parent = parent
            nodes.append(parent)

        # Step 2: Build tree upwards until root is reached
        while len(nodes) > 1:
            new_level = []
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])  # Duplicate last node if odd number
            
            for i in range(0, len(nodes), 2):
                combined_hash = hashlib.sha256((nodes[i].data + nodes[i+1].data).encode()).hexdigest()
                parent = MerkleNode(combined_hash)
                parent.left = nodes[i]
                parent.right = nodes[i+1]
                nodes[i].parent = parent
                nodes[i+1].parent = parent
                new_level.append(parent)

            nodes = new_level  # Move to the next level

        self.root = nodes[0]  # Final root node

from collections import deque

def print_merkle_tree(root):
    """Prints the Merkle tree in a level-wise format."""
    if not root:
        print("The Merkle tree is empty.")
        return

    queue = deque([(root, 0)])  # (node, level)
    current_level = 0
    result = []

    while queue:
        node, level = queue.popleft()

        # Move to a new level in the output
        if level > current_level:
            print(" | ".join(result))  # Print current level
            result = []  # Reset list for new level
            current_level = level

        # Add node data (shorten hash for readability)
        result.append(node.data[:8] + "..." if len(node.data) > 8 else node.data)

        # Add children to the queue
        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))

    # Print last level
    if result:
        print(" | ".join(result))

def print_merkle_tree_recursive(node, level=0):
    """Prints the Merkle tree in an indented hierarchical format."""
    if node is None:
        return
    
    print(" " * (4 * level) + "|-- " + (node.data[:8] + "..." if len(node.data) > 8 else node.data))
    
    # Print left and right children
    if node.left or node.right:  # Only print children if they exist
        print_merkle_tree_recursive(node.left, level + 1)
        print_merkle_tree_recursive(node.right, level + 1)


def main():
    merkle_tree = MerkleTree()
    
    while True:
        print("\nOptions:")
        print("1. Add a new block (public keys)")
        print("2. Print Merkle tree (level-order)")
        print("3. Print Merkle tree (hierarchical)")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            creation_key = input("Enter creation public key (base64): ").strip()
            sale_key = input("Enter sale public key (base64) [Press Enter to skip]: ").strip() or None
            
            merkle_tree.add_block_keys(creation_key, sale_key)
            print("\n✅ Block added! Merkle tree updated.\n")

        elif choice == "2":
            print("\n--- Level Order Merkle Tree ---")
            print_merkle_tree(merkle_tree.root)

        elif choice == "3":
            print("\n--- Hierarchical Merkle Tree ---")
            print_merkle_tree_recursive(merkle_tree.root)

        elif choice == "4":
            print("Exiting program.")
            break

        else:
            print("❌ Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
