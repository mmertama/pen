# pen

Draw lines from command line.

Requires Gempyre-Python to be installed.

* off x y - does offset to parameters.

* scale s - scales drawing.

* line x1 y1 x2 y2 - draw a line.

* ln x y  - draw a jointed line from a previous line position.

* move x y - move a line start position

* color c - use a given color (HTML color name or format).

* close -  close current line to a polygon

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

