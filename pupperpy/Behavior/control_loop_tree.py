# example from https://py-trees.readthedocs.io/en/devel/trees.html

import py_trees
import time
from action_nodes import level_1_actions, primitive_actions
from condition_nodes import primitive_conditions


class TreeStateHandler():
    """
    Keeps track of the active node and what commands are supposed to be sent based off which node is running.
    """
    pass


if __name__ == '__main__':

    def create_tree():
        root = py_trees.composites.Sequence("Sequence")

        # look_for_ball = level_1_actions.LookForBallNode()
        # move_towards_ball = level_1_actions.MoveTowardsBallNode()

        move_1_second_a = primitive_actions.MoveForwardNode(2)
        move_1_second_b = primitive_actions.MoveForwardNode(1)

        root.add_children([move_1_second_a, move_1_second_b])
        # look_for_ball.add_children([move_1_second_a])
        # move_towards_ball.add_children([move_1_second_b])

        return py_trees.trees.BehaviourTree(root)

    def setup_and_print_tree_static(tree, level=0, is_root=True):
        if is_root:
            tree = tree.root

        print("\t" * level + tree.name)
        for child in tree.children:
            setup_and_print_tree_static(child, level + 1, False)

    def print_tree(tree):
        print(py_trees.display.unicode_tree(root=tree.root))

    behaviour_tree = create_tree()

    setup_and_print_tree_static(behaviour_tree)
    print("\n")
    behaviour_tree.setup(timeout=15)

    try:
        behaviour_tree.tick_tock(
            period_ms=500,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=None,
            post_tick_handler=None
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()
