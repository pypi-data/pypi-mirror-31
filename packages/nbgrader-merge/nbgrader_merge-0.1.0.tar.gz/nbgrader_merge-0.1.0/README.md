# nbgrader_merge
Copy nbgrader solutions from jupyter notebooks.

## What's going on?
Don't you just hate it having to copy paste your old answers when a bug in the
exercise notebooks is found?
Well, no more.

## What kind of sorcery is this?
The *dangerous* kind.
Make a backup of your work before venturing any further.

Have you backed up everything?

Are you sure?

Double check just to be on the safe side.

Now proceed with the following incantation:
1. Install this package using pip
1. Clone the learning unit repository again with the updates
1. Run `nbgrader_merge <source> <destination>`, where source is the directory containing your answers (the one you backed up just a moment ago, right?) and destination is the new clone of the learning unit
1. ???
1. Profit
1. Check if everything is in order

## What to do when this goes wrong?
You have a backup, cool.

Try it again with `--debug` and open a ticket [here](https://github.com/LDSSA/nbgrader_merge.git).


## License

* Free software: MIT license

