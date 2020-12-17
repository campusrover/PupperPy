import py_trees


class TreeStateHandler():
    """
    Keeps track of the active node and what commands are supposed to be sent based off which node is running.
    """

    def __init__(self, control):
        self.node_count = 0
        self.active_node = None
        self.control = control
        self.node_id_dict = {}

    """
    def update_data(self):
        self.control.update_data()
    """

    # hack get into pre tick
    def update_data(self, tree):
        if self.active_node:
            self.control.active_node = self.node_id_dict[self.active_node]
        self.control.update_data()
        self.control.move_stop()
        self.control.turn_stop()

    def set_active_node(self, node):
        if not self.active_node is node:
            self.active_node = node
            if self.active_node:
                print("Active node is now: " +
                      str(self.active_node.name))

    def get_active_node_id(self):
        return self.node_id_dict[self.active_node]
