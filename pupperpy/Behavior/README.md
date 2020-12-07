**Decision Trees**

Complex behavior for the CERBaris is a behavior tree implementation dependent on py_trees. To run the current behavior iteration, simply run control_loop.py from the main pupperpy directory.

```bash
cd /your/path/to/PupperPy
python3 control_loop.py
```

[insert visual diagram of current behavior tree here]

- All action leaves are subscribed to the incoming data stream from CommandInterface.

- The structure of the behavior tree can be expressed as an indented file, which is parsed and read by the CERBaris web service.

- Every node in the behavior tree is labelled as running, succeeded, or failed, depending on whether its conditions for completion are met. This code assigns ids to each node in the tree and highlights the active path.
