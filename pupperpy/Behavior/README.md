This module should contain logic classes and instruction definitions necessary to construct on-demand decision trees based on English commands. To use this module:

-import Behavior
-pass your given command to the parser with Parser.parse_command()
-retrieve your updated tree with Parser.get_tree()
-to run the decision tree on a given set of inputs, run Tree.decide(data)

The decision tree will look a lot like the control loop, with conditionals and state transitions.

Commands should consist only of words in the dictionary, with the following supported syntax:
...TBA...

This module should also have the capability to pass tree information in a readbale format to the web server.
If the web server somehow makes adjustments to the tree, the parser should update with that also in the control loop.
