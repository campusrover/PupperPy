import py_trees
import time
import primitive_actions
import primitive_conditions
import pupper_tree_classes


if __name__ == '__main__':
    tsh = pupper_tree_classes.TreeStateHandler(None)
    id_count = 0

    tree_structure = {"Root":             (py_trees.composites.Sequence("Root"), ["2_then_1", "1_then_2"]),
                      "2_then_1":         (py_trees.composites.Sequence("2 Then 1"), ["move_2_seconds_a", "move_1_second_a"]),
                      "1_then_2":         (py_trees.composites.Sequence("1 Then 2"), ["move_1_second_b", "move_2_seconds_b"]),
                      "move_2_seconds_a":   (primitive_actions.MoveForwardNode(tsh, time_length=2), []),
                      "move_2_seconds_b":   (primitive_actions.MoveForwardNode(tsh, time_length=2), []),
                      "move_1_second_a":    (primitive_actions.MoveForwardNode(tsh, time_length=1), []),
                      "move_1_second_b":    (primitive_actions.MoveForwardNode(tsh, time_length=1), [])}

    def add_children(node_string):
        global id_count
        node = tree_structure[node_string][0]
        tsh.node_id_dict[node] = id_count
        for child_string in tree_structure[node_string][1]:
            child_node = tree_structure[child_string][0]
            node.add_child(child_node)
            id_count += 1
            add_children(child_string)

    def create_tree():

        if not tree_structure["Root"]:
            return

        add_children("Root")
        """
        for key in tsh.node_id_dict.keys():
            print(str(key.name) + ": " + str(tsh.node_id_dict[key]))
        print()
        """

        return py_trees.trees.BehaviourTree(tree_structure["Root"][0])

    def setup_and_print_tree_static(tree, level=0, is_root=True):
        if is_root:
            tree = tree.root

        print("\t" * level + tree.name)
        for child in tree.children:
            setup_and_print_tree_static(child, level + 1, False)

    def print_tree(tree):
        print(py_trees.display.unicode_tree(root=tree.root))

    def print_active_node(tree):
        print(tsh.get_active_node_id())

    behaviour_tree = create_tree()

    setup_and_print_tree_static(behaviour_tree)
    print("\n")
    behaviour_tree.setup(timeout=15)

    try:
        behaviour_tree.tick_tock(
            period_ms=500,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=None,
            post_tick_handler=print_active_node
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()
