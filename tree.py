class Node:

    regions = ['NE', 'NW', 'SE', 'SW']

    def __init__(self, parent):
        self.maze = None
        self.parent = parent
        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None

    def subdivide(self):
        """Create 4 regions inside this node"""
        self.south_east = Node(self)
        self.south_west = Node(self)
        self.north_west = Node(self)
        self.north_east = Node(self)

    def find_region(self):
        """Get the region that this node is contained in, relative to the parent of this node"""
        if not self.parent:
            return None

        for dir in Node.regions:
            if self.parent.get_child(dir):
                return dir

        return None

    def get_child(self, region):
        """

        Args:
            dir (str): The region of the child node

        Returns:
            Node: The child node in the given region
        """
        if region == 'NE':
            return self.north_east

        if region == 'NW':
            return self.north_west

        if region == 'SE':
            return self.south_east

        if region == 'SW':
            return self.south_west

        return None

    def get_innermost_chlld(self, region):
        child = None
        while self.has_child(region):
            child = child.get_child(region)
        return child

    def has_child(self, region):
        if self.get_child(region):
            return True

        return False


def find_available_subtree(current_node: Node, exit_dir: str) -> Node:
    """TODO"""

    if not current_node.parent:
        return None

    parent = current_node.parent

    current_region = current_node.find_region()

    return None


root = Node(None)  # Tree
