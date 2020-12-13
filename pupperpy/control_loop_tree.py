import py_trees
import time
from Behavior import primitive_actions
from Behavior import primitive_conditions, pupper_actions
from Behavior import pupper_tree_classes
from CommandInterface import Control
from UDPComms import timeout

from subprocess import Popen
import os

RUN_ROBOT_PATH = '/home/cerbaris/pupper_code/StanfordQuadruped/run_robot.py'
PATH = os.path.dirname(os.path.abspath(__file__))
VISION_SCRIPT = os.path.join(PATH, 'Vision', 'pupper_vision.py')


class TreeControl(Control):
    """
    Control extension that updates on command with behavior tree ticks.
    """

    def __init__(self):
        super(TreeControl, self).__init__()
        self.data = {}
        self.active_node = -1
        self.last_obj = None
        self.last_pos = None
        self.last_cv = []

    def update_data(self):
        # grab data
        self.last_obj = self.obj_sensors.read()
        self.last_pos = self.pos.data
        try:
            self.last_cv = self.cv_sub.get()
        except timeout:
            self.last_cv = []

    def _step(self, tree):
        js_msg = self.joystick.get_input()

        # Force stop moving
        if js_msg['button_l2']:
            self.user_stop = True
            self.stop_walk()
            return

        # User activate
        if js_msg['button_l1']:
            self.user_stop = False
            self.activate()
            return

        if self.user_stop or not self.active:
            self.reset()
            self.send_cmd()
            return

        if not self.walking:
            self.start_walk()
            return

        #print(str(time.time()) +': ' + self.state)
        self.send_cmd()
        self.send_pusher_message(self.last_pos, self.last_obj, self.last_cv)

    def send_pusher_message(self, pos, obj, cv):
        bbox = self.current_target
        timestamp = time.time()
        if bbox is None:
            bbox = {'bbox_x': None,
                    'bbox_y': None,
                    'bbox_h': None,
                    'bbox_w': None,
                    'bbox_label': None,
                    'bbox_confidence': None}

        message = {'time': timestamp,
                   'x_pos': pos['x'],
                   'y_pos': pos['y'],
                   'x_vel': pos['x_vel'],
                   'y_vel': pos['y_vel'],
                   'x_acc': pos['x_acc'],
                   'y_acc': pos['y_acc'],
                   'yaw': pos['yaw'],
                   'yaw_rate': pos['yaw_rate'],
                   'left_sensor': obj['left'],
                   'center_sensor': obj['center'],
                   'right_sensor': obj['right'],
                   'state': self.state,
                   'active_node': self.active_node,
                   **bbox}

        self.pusher_client.send(message)


"""
        # grab data
        obj = self.obj_sensors.read()
        pos = self.pos.data
        try:
            cv = self.cv_sub.get()
        except timeout:
            cv = []
"""


if __name__ == '__main__':
    control = TreeControl()
    tsh = pupper_tree_classes.TreeStateHandler(control)
    vis_p = Popen(['python3', VISION_SCRIPT])
    robo_p = Popen(['python3', RUN_ROBOT_PATH])
    time.sleep(5)
    # control.run_loop()
    # tsh = pupper_tree_classes.TreeStateHandler(None)
    id_count = 0

    tree_structure_1 = {"Root":             (py_trees.composites.Sequence("Root"), ["2_then_1", "1_then_2"]),
                        "2_then_1":         (py_trees.composites.Sequence("2 Then 1"), ["move_2_seconds_a", "turn_1_second_a"]),
                        "1_then_2":         (py_trees.composites.Sequence("1 Then 2"), ["move_1_second_b", "turn_2_seconds_b"]),
                        "move_2_seconds_a":   (primitive_actions.MoveForwardNode(tsh, time_length=2), []),
                        "turn_2_seconds_b":   (primitive_actions.TurnRightNode(tsh, time_length=2), []),
                        "turn_1_second_a":    (primitive_actions.TurnRightNode(tsh, time_length=1), []),
                        "move_1_second_b":    (primitive_actions.MoveForwardNode(tsh, time_length=1), [])}

    tree_structure = {"Root":                     (py_trees.composites.Sequence("Root"), ["Avoid", "Go", "Go to target"]),
                      "Avoid":                    (pupper_actions.AvoidObstaclesNode(tsh), []),
                      "Go":                       (pupper_actions.MoveTargetFoundNode(tsh), []),
                      "Go to target":             (pupper_actions.GoToTargetNode(tsh), [])}

    tree_structure_hard = {"Root":                     (py_trees.composites.Sequence("Root"), ["Look for ball", "Move toward ball"]),
                           "Look for ball":            (py_trees.composites.Sequence("Look for ball"), ["Move forward A", "Detect ball A"]),
                           "Move toward ball":         (py_trees.composites.Selector("Move toward ball"), ["Handle left", "Handle center", "Handle right"]),
                           "Move forward A":           (primitive_actions.MoveForwardNode(tsh), []),
                           "Detect ball A":            (primitive_conditions.TargetFoundNode(tsh), []),
                           "Handle left":              (py_trees.composites.Sequence("Handle left"), ["Detect left sensor A", "Turn right A"]),
                           "Handle center":            (py_trees.composites.Sequence("Handle center"), ["Detect center sensor A", "Turn right B"]),
                           "Handle right":             (py_trees.composites.Sequence("Handle right"), ["Detect right sensor A", "Turn left A"]),
                           "Detect left sensor A":     (primitive_conditions.LeftObstacleNode(tsh), []),
                           "Detect center sensor A":   (primitive_conditions.FrontObstacleNode(tsh), []),
                           "Detect right sensor A":    (primitive_conditions.RightObstacleNode(tsh), []),
                           "Turn right A":             (primitive_actions.TurnRightNode(tsh), []),
                           "Turn right B":             (primitive_actions.TurnRightNode(tsh), []),
                           "Turn left A":              (primitive_actions.TurnLeftNode(tsh), [])}

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

        # see numbers
        for key in tsh.node_id_dict.keys():
            print(str(key.name) + ": " + str(tsh.node_id_dict[key]))
        print()

        return py_trees.trees.BehaviourTree(tree_structure["Root"][0])

    """
    def parseTree(tokens, index):
        node = (tokens[index].value, tokens[index].type)
        if (len(tokens) <= index + 1 or tokens[index + 1].tabs <= tokens[index].tabs):
            node.children = []
            return node
        childIndex = index + 1
        children = []
        while (childIndex < tokens.length and tokens[childIndex].tabs > tokens[index].tabs):
            if (tokens[childIndex].tabs === tokens[index].tabs + 1) {
              children.push(this.parseTree(tokens, childIndex))
            }
            childIndex += 1
        node.children = children
        return node

        parseTree(tokens, index) {
        let node = {
          value: tokens[index].value,
          type: tokens[index].type,
        }
        // base case: leaf node; no next elt or next elt's tabs <= curr elt's tabs
        if (tokens.length <= index + 1 || tokens[index + 1].tabs <= tokens[index].tabs) {
          node.children = []
          return node
        } else {
          // loop through children and call recursively
          let childIndex = index + 1
          let children = []
          while (childIndex < tokens.length && tokens[childIndex].tabs > tokens[index].tabs) {
            if (tokens[childIndex].tabs === tokens[index].tabs + 1) {
              children.push(this.parseTree(tokens, childIndex))
            }
            childIndex++
          }
          node.children = children
          return node
        }
      }
      """

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
            pre_tick_handler=tsh.update_data,
            post_tick_handler=control._step
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()
