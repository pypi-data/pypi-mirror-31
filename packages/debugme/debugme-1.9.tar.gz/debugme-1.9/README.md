Interactive debugger, but different
===================================

Python has a great debugger in pdb, but sometimes you only want to inspect and
buck about with the state. The pdb REPL is a bit inconvenient for that, so
here's a different approach. Instead of

```
import pdb
pdb.set_trace()
```

Just do

```
import debugme
```

This starts an interactive interpreter and exits the program when the
interpreter ends. If you want to continue, run this in that interpreter

```
debugme.exit = False
```

The variables available in the interactive interpreter are the locals and
globals of the frame you imported debugme from.

The debugme object has a few more attributes:

`debugme.frame`     The stack frame that was executing at the time of import
`debugme.traceback` A formatted traceback of the current callstack
`debugme.exc_info`  If debugme was imported from sys.excepthook, this will be set to the uncaught exception
`debugme.back`      Starts a new interactive interpreter the calling frame

To start a debugme shell automatically when an uncaught exception would
terminate your application, you can install an excepthook as follows:

```
import sys
def excepthook(tp, val, tb):
    sys.__excepthook__(tp, val, tb)
    import debugme
sys.excepthook = excepthook
```
