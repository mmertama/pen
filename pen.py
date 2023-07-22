#!/usr/bin/python3
import Gempyre
import os
import sys
from Gempyre_utils import resource


def command(ui, args):
    canvas = Gempyre.CanvasElement(ui, "canvas")

    fc = Gempyre.FrameComposer()
    it = iter(args)

    offy = 0.
    offx = 0.
    scale = 1.


    def posx(x):
        return (float(x) - offx) * scale

    def posy(y):
        return (float(y) - offy) * scale    

    try:
        while it:
            cmd = next(it) 
            if cmd == 'color':
                fc.stroke_style(next(it));
            elif(cmd == 'off'):
                offx = float(next(it))
                offy = float(next(it))
            elif(cmd == 'scale'):
                scale = float(next(it))
            elif(cmd == 'line'):
                fc.move_to(posx(next(it)), posy(next(it)))
                fc.line_to(posx(next(it)), posy(next(it)))
            elif(cmd == 'ln'):
                fc.line_to(posx(next(it)), posy(next(it)))
            else:
                print("Not understood: ", cmd, file=sys.stderr)
    except (StopIteration):
        pass
    fc.stroke()
    #print(fc.composed())        
    canvas.draw_frame(fc)    


if __name__ == "__main__":
    name = os.path.join(os.path.dirname(sys.argv[0]), "ui", "ui.html")
    map, names = resource.from_file(name)
    ui = Gempyre.Ui(map, names[name])
    # read from arguments or stdin - stdin is tokenized.
    params = sys.argv[1:] if len(sys.argv) > 1 else ' '.join(sys.stdin.readlines()).replace('\n', '').rstrip().split(' ')
    
    ui.on_open(lambda: command(ui, params))

    ui.run()
