# pen

Draw simple from command line or from file.

This application has been implemented to help generate visualization from debug
printouts. Sometimes there are just too much information to see what numbers mean, and
then visualization may help to see the big picture.


Requires Gempyre-Python to be installed. (e.g. pip install gempyre) 

## Commands

* off 
    * x y - set offset of following coordinates. 
    * auto - automatically centers graphics. (auto is default - so normally you not need to provide offset )
  
* scale 
    * s - scales drawing with a given factor. Default is 1.0.
    * auto - scales drawing automatically. (auto is default - so normally you may not need provide scale)

* line x1 y1 x2 y2 - draw a line.

* ln x y  - draw a joint line from a previous line position.

* move x y - move a line start position. I.e. 'line x1 y1 x2 y2' and 'move x1 y1 ln x2 y2' are equal expressions.  
  
* color c - use a given color (HTML color name or HTML color format).

* close -  close current line to a polygon.

* circle r x y - draw a circle.

* text "some text" x y - Double or quote text is written on position x y

* text_style
    * fill - text is filled (default)
    * stroke - text is stoked

* font font_name - apply a given font name

* text_align - see: [align at w3schools](https://www.w3schools.com/graphics/canvas_text_alignment.asp#:~:text=To%20align%20text%20in%20the,the%20horizontal%20alignment%20of%20text)
* text_baseline - see: [baseline at w3schools](https://www.w3schools.com/tags/canvas_textbaseline.asp)

* exit s - exit after s seconds (floating point of)

* info - shows scale and offset

e.g.

```bash

$ pen.py off 1000 0 line 1322 12 1350 100 ln 1200 200

```

is pretty equal with 

```bash

$ pen.py off 1000 0 move 1322 12 ln 1350 100 ln 1200 200

```

The values can read from command line or from file, or both!

```bash
$ poetry run python3 pen.py < /tmp/doom_nav.txt
```

```bash
$ poetry run python3 pen.py /tmp/doom_nav.txt
```

"Both" let you inject zoom from the command line 
```bash
$ poetry run python3 pen.py scale 1.2 off -856 2700 info /tmp/doom_nav.txt
```

Example file

```
text_align center
text_baseline middle

text "Hello world!" 1544 2560
line 1552 2560 1536 2560
```

Read from file:

```bash

$ pen.py < lines.txt

```

... or with poetry:

```bash

$ poetry run python3 ../pen.py < ~/lines/nav_line16.txt

```


