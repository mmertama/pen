#!/usr/bin/python3
import Gempyre
import os
import sys
import math
import datetime
import inspect
import re
from Gempyre import resource

GUI = '''
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Pen</title>
        <style>
        div.note {
            position: absolute;
            top: 0;
            left: 0;
            z-index: 9999;
            background-color: yellow;
            padding: 5px;
            }
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
        <div class="note" id="info"></div>
    </body>
</html>
'''


MAX = float(0xFFFFFF)
GUI_MARGIN = 20

offy = 0.
offx = 0.
scale = 1.
invx = False
invy = True


def get_rest(it):
    p = 0
    try:
        while True:
            next(it)
            p += 1
    except StopIteration:
        pass
    return p        
        

def get_pos(args, it):
    tail_len = get_rest(it)
    pos = len(args) - tail_len
    # restore
    new_it = iter(args)
    for _ in range(pos):
        next(new_it)
    return pos, new_it    

def tail(args, pos, tail_len = 20):
    debug_it = iter(args)
    tail = args[:tail_len]
    debug_pos = 0
    try:
        while debug_pos < pos:
            debug_pos += 1
            v = next(debug_it)
            if debug_pos > tail_len:
                tail.pop(0)
                tail.append(v)        
    except StopIteration:
        pass
    return ' '.join(tail)    

## this function has get too big - make as class!
def command(ui, rect, args, enable_auto, from_pos = 0):
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

    global offy, offx, scale, invx, invy

    is_fill = False
    is_vertex = False
    vertices = []
    
    def boolean(value) -> bool:
        FALSE = [ 'no', 'false', 'off', '0' ]
        TRUE = [ 'yes', 'true', 'false', 'on', '1' ]
        if value.lower() not in [ x for x in FALSE + TRUE]:
            raise ValueError("Not a boolean")
        return value in TRUE

    def posx(x):
        global offx, scale, invx
        nonlocal minx, maxx
        v = float(x)
        minx = min(minx, v)
        maxx = max(maxx, v)
        screenx = (v - offx) * scale
        return rect.width - screenx if invx else screenx  

    def posy(y):
        global offy, scale, invy
        nonlocal miny, maxy
        v = float(y)
        miny = min(miny, v)
        maxy = max(maxy, v)
        screeny = (v - offy) * scale
        print("invvy", invy)
        return rect.height - screeny if invy else screeny      

    def end_path():
        nonlocal in_line
        nonlocal is_fill
        nonlocal is_vertex
        nonlocal vertices
        if in_line:
            if is_fill:
                fc.fill()
            else:    
                fc.stroke()
            in_line = False
        if len(vertices) > 0:
            #fc.save();        # Save current canvas state
            for x, y in vertices:
                fc.begin_path()
                fc.ellipse( x, y, 5, 5, math.pi * 2, 0, math.pi * 2)
                fc.stroke()
            #fc.restore()
            vertices = []  
 

    def read_text():
        nonlocal it
        text = next(it)
        if text[0] == '"':
            start = '"' 
        elif text[0] == "'":
            start = "'"
        else:
            raise ValueError('Not a string:' + text)
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
        
                  
    canvas = Gempyre.CanvasElement(ui, "canvas")
     
    try:
        for _ in range(from_pos):
            next(it) # consume
        while it:
            cmd = next(it) # change to match - case when applicable
            match cmd:
                case 'color':
                    ## c - use a given color (HTML color name or HTML color format).
                    end_path()
                    is_fill = False
                    fc.stroke_style(next(it))
                case 'width':
                    ## w - line width.
                    fc.line_width(float(next(it)))    
                case 'fill':
                    ## c - the polygons are filles with the color until 'color' is called. 
                    end_path()
                    is_fill = True
                    fc.fill_style(next(it))
                case 'erase':
                    ## Erase off drawings
                    canvas.erase()        
                case 'off':
                    ## * x y - set offset of following coordinates. 
                    ## * auto - automatically centers graphics. (auto is default - so normally you not need to provide offset )
                    param = next(it)
                    if param == 'auto':
                        auto_offset = enable_auto
                    else: 
                        offx = float(param)
                        offy = float(next(it))
                case 'scale':
                    ##  * s - scales drawing with a given factor. Default is 1.0.
                    ## * auto - scales drawing automatically. (auto is default - so normally you may not need provide scale)
                    param = next(it)
                    if param == 'auto':
                        auto_scale = enable_auto
                    else:  
                        scale = float(param)
                case 'move':
                    ##  x y - move a line start position. I.e. 'line x1 y1 x2 y2' and 'move x1 y1 ln x2 y2' are equal expressions. 
                    begin_path()
                    x = posx(next(it))
                    y = posy(next(it))
                    fc.move_to( x, y )
                    if is_vertex:
                        vertices.append( ( x, y ) )
                case 'line':
                    ## x1 y1 x2 y2 - draw a line.
                    begin_path()
                    fc.move_to(posx(next(it)), posy(next(it)))
                    fc.line_to(posx(next(it)), posy(next(it)))
                case 'circle':
                    ## r x y - draw a circle.
                    begin_path()
                    radius = float(next(it))
                    fc.ellipse(posx(next(it)), posy(next(it)), radius, radius, math.pi * 2, 0, math.pi * 2)  
                case 'rect':
                    ## Draw a rect x1 y1 x2 y2 
                    begin_path()
                    tlx = posx(next(it))
                    tly = posx(next(it))
                    fc.rect(Gempyre.Rect(tlx, tly, posx(next(it) - tlx, posy(next(it)) - tly)))  
                case 'close':
                    ## close current line to a polygon.
                    if in_line:
                        fc.close_path()
                    end_path()
                case 'ln':
                    ## x y  - draw a joint line from a previous line position.
                    x = posx(next(it))
                    y = posy(next(it))
                    fc.line_to(x, y)
                    if is_vertex:
                        vertices.append( ( x, y ) )
                case 'polyline':
                    begin_path()
                    fc.move_to(posx(next(it)), posy(next(it)))
                    while True:
                        nxt = next(it)
                        if not nxt or nxt == 'end':
                            break
                        if nxt == 'close':
                            fc.close_path()
                            break
                        fc.line_to(posx(nxt), posy(next(it)))  
                    end_path()    
                case 'text':
                    ## "some text" x y - Double or quote text is written on position x y
                    if text_style == 'fill':
                        fc.fill_text(read_text(), posx(next(it)), posy(next(it)))   
                    elif text_style == 'stroke':
                        fc.stroke_text(read_text(), posx(next(it)), posy(next(it)))
                case 'font':
                    ## font_name - apply a given font name
                    fc.font(next(it))
                case 'text_align':
                    ##  see: https://www.w3schools.com/graphics/canvas_text_alignment.asp#:~:text=To%20align%20text%20in%20the,the%20horizontal%20alignment%20of%20text
                    fc.text_align(next(it))
                case 'text_baseline':
                    ##  see: https://www.w3schools.com/tags/canvas_textbaseline.asp
                    fc.text_baseline(next(it))             
                case 'text_style':
                    ## * fill - text is filled (default)
                    ## * stroke - text is stoked
                    text_style = next(it) 
                case 'invx':
                    ## mirror
                    invx = boolean(next(it))
                case 'invy':
                    ## flip
                    invy = boolean(next(it))
                case 'exit':
                    ## s - exit after s seconds (floating point of)
                    exit_time = float(next(it))
                    ui.after(datetime.timedelta(seconds=exit_time), lambda: sys.exit())
                case 'sleep':
                    ##  s - draws and wait s seconds before continue. Enables simple animations.
                    wait_time = float(next(it))
                    if enable_auto:
                        continue
                    new_pos, _ = get_pos(args, it)
                    ui.after(datetime.timedelta(seconds=wait_time), lambda: command(ui, rect, args, False, new_pos))    
                    raise StopIteration
                case 'info':
                    ## info - shows scale and offset
                    Gempyre.Element(ui, 'info').set_html(f"scale {round(scale, 2)} off {round(offx, 2)} {round(offy, 2)}")      
                case 'vertex':
                    ## on/off - draw a polygon vertices when constructed with a move, ln(s) and a close 
                    is_vertex = boolean( next(it) )
                case _:
                    if cmd.isprintable() and cmd != ' ':
                        pos, it = get_pos(args, it)
                        print(f"Not understood: '{cmd}' after: '{tail(args, pos, 5)}'", file=sys.stderr)
    except StopIteration:
        pass
    except ValueError as e:
        pos, it = get_pos(args, it)
        print(f"Value error:: '{e}' after: '{tail(args, pos, 5)}'", file=sys.stderr)
        sys.exit(1)
    end_path()
   
    if not (auto_scale and auto_offset):
       canvas.draw_frame(fc)
    else:
        width = maxx - minx
        height = maxy - miny
        if width <= 0:
            print(f"Width too small", file=sys.stderr)
            width = 10
        if height <= 0:
            print(f"Height too small", file=sys.stderr)
            height = 10
        rect = canvas.rect()
        rect.width -= GUI_MARGIN
        rect.height -= GUI_MARGIN
        if auto_scale: # scale is from drawing coordinates to screen coords
            scale = min(rect.width / width, rect.height / height)     
        if auto_offset: # offset is in drawing coordinates (not in canvas)
            offx = minx + (width - rect.width / scale) / 2
            offy = miny + (height - rect.height / scale) / 2
        command(ui, rect, args, False)                

def as_file(name):
    with open(name) as f:
         return ' '.join((ln for ln in f.readlines() if ln[0] != '#')).replace('\n', '').rstrip().split()

def print_help():
    print("Draw from command line or from file.")   
    src = inspect.getsource(command)
    cmd = False
    has_doc = False
    for ln in src.split('\n'):
        if cmd:
            m = re.match(r'\s*##\s*(.*)', ln )
            if m:
                print( '\t', m[1])
                has_doc = True
            else: 
                if not has_doc: 
                    print( '\t', 'Undocumented')
                cmd = False
                has_doc = False    
        m = re.match(r'\s+case .([a-z_0-9]+).:', ln)
        if m:
            cmd = m[1]
            print(cmd)
    sys.exit()

if __name__ == "__main__":
    def main():
        last_mouse = None
        map, names = resource.from_bytes({"ui.html": bytes(GUI, 'utf-8')})
        ui = Gempyre.Ui(map, names["ui.html"])
        # read from arguments or stdin - stdin is tokenized.
        if len(sys.argv) > 1:
            if sys.argv[1] == '--help' or sys.argv[1] == '-h' or sys.argv[1] == '?':
                print_help()
            params = []
            for p in  sys.argv[1:]:
                if os.path.exists(p):
                    params.extend(as_file(p))
                else:
                    params.append(p)            
        else:    
            params = ' '.join((ln for ln in sys.stdin.readlines() if ln[0] != '#')).replace('\n', '').rstrip().split()

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
                command(ui, wrect, ['scale', 'auto', 'off', 'auto'] + params, True)

        def on_mouse_move(p):
            nonlocal last_mouse
            last_mouse = (float(p.properties['clientX']), float(p.properties['clientY']))
            
        def on_key(p):
            key = p.properties['key']
            if key.upper() == 'Q':
                Gempyre.CanvasElement(ui, "canvas").erase()
                command(ui, wrect,['scale', str(scale * 1.2), 'off', str(offx), str(offy)] + params, True)
            if key.upper() == 'W':
                Gempyre.CanvasElement(ui, "canvas").erase()
                command(ui, wrect,['scale', str(scale * 0.9), 'off', str(offx), str(offy)] + params, True)    
        
        def on_mouse_click(p):
            on_mouse_move(p)
            dx = (last_mouse[0] - (wrect.x + wrect.width / 2)) / scale
            dy = (last_mouse[1] - (wrect.y + wrect.height / 2)) / scale
            #print(dx, dy, wrect.x, wrect.y, wrect.width, wrect.height)
            Gempyre.CanvasElement(ui, "canvas").erase()
            command(ui, wrect,['scale', str(scale), 'off', str(offx - dx), str(offy + dy)] + params, True)
                    

        # works only with non-browser UI servers
        ui.root().subscribe("resize", lambda _: on_resize(), [], datetime.timedelta(milliseconds=500))
        
        ui.root().subscribe("mousemove", on_mouse_move, ['clientX', 'clientY'], datetime.timedelta(milliseconds=100))
        ui.root().subscribe("keyup", on_key, ['key'])
        ui.root().subscribe("click", on_mouse_click, ['clientX', 'clientY'])
        
        def on_open():
            on_resize()

        ui.on_open(on_open)
        ui.run()
    main()    
