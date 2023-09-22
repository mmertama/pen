# pen

Sometime ago I had need to visualize things (write lines) from Bash script, for that
I wrote this small application.  

Draw lines from command line.

Requires Gempyre-Python to be installed.

* off x y - set offset of following coordinates. Default is (0,0) helps you centrify/move drawing. 
  
* scale s - scales drawing with a given factor. Default is 1.0.

* line x1 y1 x2 y2 - draw a line.

* ln x y  - draw a joint line from a previous line position.

* move x y - move a line start position. I.e. 'line x1 y1 x2 y2' and 'move x1 y1 ln x2 y2' are equal expressions.  
  
* color c - use a given color (HTML color name or HTML color format).

* close -  close current line to form a polygon

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

