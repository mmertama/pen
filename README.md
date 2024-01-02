# pen

Draw simple from command line or from file.

This application has been implemented to help generate visualization from debug
printouts. Sometimes there are just too much information to see what numbers mean, and
then visualization may help to see the big picture.


Requires Gempyre-Python to be installed.

* off x y - does offset to parameters.

* scale s - scales drawing.

* line x1 y1 x2 y2 - draw a line.

* ln x y  - draw a jointed line from a previous line position.

* move x y - move a line start position

* color c - use a given color (HTML color name or format).

* close -  close current line to a polygon.

* circle r x y - draw a circle.

e.g.

```bash

$ pen.py off 1000 0 line 1322 12 1350 100 ln 1200 200

```

is pretty equal with 

```bash

$ pen.py off 1000 0 move 1322 12 ln 1350 100 ln 1200 200

```

Read from file:

```bash

$ pen.py < lines.txt

```

