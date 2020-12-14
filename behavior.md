---
layout: template
---
**Behavior Trees**

**Instructions**

Complex behavior for the CERBaris is a behavior tree implementation dependent on the py_trees library.

~~~bash
sudo pip install py-trees
~~~

To run the current behavior iteration, simply run control_loop_tree.py from the pupperpy directory after successfully connecting to the robot via SSH.
~~~bash
cd /your/path/to/PupperPy/pupperpy
sudo pigpiod
sudo python3 control_loop.py
~~~

Behavior trees are a way to compartmentalize code segments into nodes that can be manipulated. They were chosen over finite state machines and decision trees due to their comparative power, improved modularity, as well as ease of interpretation.

![](https://i.imgur.com/FaxbZai.png)

(The above diagram illustrates the default pupper behavior at a high level, with "meandering" being the current running action. In terms of composite node logic, this implies that avoiding obstacles has finished, and that turning around did not lead to finding the ball.)

**PyTrees**

PyTrees contains predefined classes for action and composite (sequence ->, selector ?, and parallel ||) nodes that are the building blocks for behavior trees. Information explaining the library as well as explanations of the theory behind using these trees can be found at: https://py-trees.readthedocs.io/en/devel/. The instantiation and running of our current behavior tree can be found in the main control_loop_tree.py loop, which can be done by:

~~~python
import py_trees
root = py_trees.composites.Sequence("Root")
root.add_children([BEHAVIOR_1, BEHAVIOR_2, BEHAVIOR_3])
behaviour_tree = py_trees.trees.BehaviourTree(py_trees.composites.Sequence("Root"))
behaviour_tree.tick_tock(
    period_ms=500,
    number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
    pre_tick_handler=None,
    post_tick_handler=None
)
~~~

where behavior can be action nodes, or other composite nodes.

Individual action nodes can be written up as classes that extend py_trees.behaviour.Behaviour, like so:

~~~python
import py_trees
class DoAThing(py_trees.behaviour.Behaviour):
    def __init__():
    super(DoAThing, self).__init__("Do A Thing")
    ...
~~~

Such actions can be found in the Behavior folder in the main pupperpy directory.

**Automatic initialization/visualization**

control_loop_tree allows developers to define trees in a more organized fashion with dictionary parsing:

~~~python
    tree_structure = {"Root":           (py_trees.composites.Sequence("Root"), ["A", "B", "C"]),
                      "A":              (ANode(), []),
                      "B":              (BNode(), []),
                      "C":              (CNode(), [])}
~~~

where each entry's key is the node's name, the first value mapped to it is the node reference, and the second value is a list of its children. The structure of this behavior tree can be expressed as an indented file, which is parsed and read by the CERBaris web service. Note that py_trees does not allow nodes to have multiple parents.

The TreeStateHandler in Behavior/pupper_tree_classes assigns integer node ids to every node added in this fashion, and uses those ids to identify and communicate which of those nodes is currently running at all times.

**Next Steps**

- More complex behaviors in nodes, such as backward dodging and pathing
- Real-time tree restructuring through the web interface
- English command integration, with syntactic tree parsing techniques
