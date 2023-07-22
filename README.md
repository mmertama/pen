# pen

Draw lines from command line.

Requires Gempyre-Python to be installed.

* off x y - does offset to parameters.

* scale s - scales drawing.

* line x1 y1 x2 y2 - draw a line.

* ln x y  - draw a jointed line from a previous line position.

* color c - use a given color (HTML color name or format).

e.g.

```bash

$ pen.py off 1000 0 line 1322 12 1350 100 ln 1200 200

```

or

```bash

$ pen.py < lines.txt

```

where 'lines'.txt contains draw commands
