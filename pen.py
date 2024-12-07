#!/usr/bin/python3
import Gempyre
import os
import sys
import math
import datetime
from Gempyre import resource

GUI = '''
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Pen</title>
        <style>
        body { 
            display: flex; 
            justify-content: center; /* Center horizontally */ 
            align-items: center; /* Center vertically */ 
            height: 100vh; /* Make the body full height */ 
            margin: 0; /* Remove default margin */ 
        }
        </style>
    </head>
    <body>
        <script type="text/javascript" src="gempyre.js"></script>
        <canvas id="canvas" width="1280" height="1024"></canvas>
    </body>
</html>
'''


MAX = float(0xFFFFFF)
GUI_MARGIN = 20

offy = 0.
offx = 0.
scale = 1.

def command(ui, args, enable_auto = True):

    fc = Gempyre.FrameComposer()
    it = iter(args)

    text_style = 'fill'
   
    in_line = False
    auto_offset = False
    auto_scale = False

    minx = MAX
    maxx = -MAX
    miny = MAX
    maxy = -MAX

    global offy, offx, scale

    def posx(x):
        global offx, scale
        nonlocal minx, maxx
        v = float(x)
        minx = min(minx, v)
        maxx = max(maxx, v)
        return (v - offx) * scale

    def posy(y):
        global offy, scale
        nonlocal miny, maxy
        v = float(y)
        miny = min(miny, v)
        maxy = max(maxy, v)
        return (v - offy) * scale    

    def end_path():
        nonlocal in_line
        if in_line:
            fc.stroke()
            in_line = False

    def read_text():
        nonlocal it
        text = next(it)
        if text[0] == '"':
            start = '"' 
        elif text[0] == "'":
            start = "'"
        else:
            raise Exception('Not a string:' + text)
        text = text[1:]
       
        while not (text[-1] == start and (len(text) == 1 or text[-2] != '\\')): 
            text += ' ' + next(it)

        text = str(text[:-1])
        return text            

    def begin_path():
        nonlocal in_line
        end_path()
        fc.begin_path()
        in_line = True          

    try:
        while it:
            cmd = next(it) # change to match - case when applicable
            if cmd == 'color':
                end_path()
                fc.stroke_style(next(it))
            elif cmd == 'off':
                param = next(it)
                if param == 'auto':
                    auto_offset = enable_auto
                else: 
                    offx = float(param)
                    offy = float(next(it))
            elif cmd == 'scale':
                param = next(it)
                if param == 'auto':
                    auto_scale = enable_auto
                else:  
                    scale = float(param)
            elif cmd == 'move':
                begin_path()
                fc.move_to(posx(next(it)), posy(next(it)))    
            elif cmd == 'line':
                begin_path()
                fc.move_to(posx(next(it)), posy(next(it)))
                fc.line_to(posx(next(it)), posy(next(it)))
            elif cmd == 'circle':
                begin_path()
                radius = float(next(it))
                fc.ellipse(posx(next(it)), posy(next(it)), radius, radius, math.pi * 2, 0, math.pi * 2)  
            elif cmd == 'close':
                if in_line:
                    fc.close_path()
                end_path()
            elif cmd == 'ln':
                fc.line_to(posx(next(it)), posy(next(it)))
            elif cmd == 'text':
                if text_style == 'fill':
                    fc.fill_text(read_text(), posx(next(it)), posy(next(it)))   
                elif text_style == 'stroke':
                    fc.stroke_text(read_text(), posx(next(it)), posy(next(it)))
            elif cmd == 'font':
                fc.font(next(it))
            elif cmd == 'text_align':
                fc.text_align(next(it))
            elif cmd == 'text_baseline':
                fc.text_baseline(next(it))             
            elif cmd == 'text_style':
                text_style = next(it)    
            elif cmd.isprintable() and cmd != ' ':
                print("Not understood: '", cmd, "'", file=sys.stderr)
    except (StopIteration):
        pass
    end_path()

    canvas = Gempyre.CanvasElement(ui, "canvas")
    if not (auto_scale and auto_offset):
       canvas.draw_frame(fc)
    else:
        width = maxx - minx
        height = maxy - miny
        assert width > 0
        assert height > 0
        if width == 0 or height == 0:
            return
        rect = canvas.rect()
        rect.width -= GUI_MARGIN
        rect.height -= GUI_MARGIN
        if auto_scale: # scale is from drawing coordinates to screen coords
            scale = min(rect.width / width, rect.height / height)     
        if auto_offset: # offset is in drawing coordinates (not in canvas)
            offx = minx + (width - rect.width / scale) / 2
            offy = miny + (height - rect.height / scale) / 2
           
        command(ui, args, False)                


if __name__ == "__main__":
    def main():
        map, names = resource.from_bytes({"ui.html": bytes(GUI, 'utf-8')})
        ui = Gempyre.Ui(map, names["ui.html"])
        # read from arguments or stdin - stdin is tokenized.
        params = sys.argv[1:] if len(sys.argv) > 1 else ' '.join((ln for ln in sys.stdin.readlines() if ln[0] != '#')).replace('\n', '').rstrip().split()

        wrect = Gempyre.Rect(0, 0, 0 ,0)
        
        def on_resize():
            nonlocal wrect
            new_rect = ui.root().rect()
            if new_rect != wrect:
                wrect = new_rect
                canvas = Gempyre.CanvasElement(ui, "canvas")
                canvas.set_attribute("width", str(wrect.width - GUI_MARGIN))
                canvas.set_attribute("height", str(wrect.height - GUI_MARGIN))
                canvas.erase()
                command(ui, params)

        # works only with non-browser UI servers
        ui.root().subscribe("resize", lambda _: on_resize(), [], datetime.timedelta(milliseconds=500))

        def on_open():
            on_resize()

        ui.on_open(on_open)

        ui.run()
    main()    
