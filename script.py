import mdl
from display import *
from matrix import *
from draw import *
import shutil, os

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1

    ifFrames = False
    ifVary = False

    #print(commands)
    for command in commands:
        op = command['op']
        if op == 'frames': 
            num_frames = int(command['args'][0])
            ifFrames = True
        if op == 'basename':
            name = command['args'][0]
        if op == 'vary':
            vary = True

    if ifVary and name == '':
        print("warning: empty basename")

    if ifVary and not ifFrames:
        raise Exception('vary but no frames')

    if num_frames < 1:
        raise Exception('invalid frames')

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for command in commands:
        op = command['op']
        if op == 'vary':
            knob = command['knob']
            args = command['args']
            startFrame = int(args[0])
            endFrame = int(args[1])
            startValue = args[2]
            endValue = args[3]

            if startFrame < 0:
                raise Exception('vary invalid start frame')
            if endFrame > num_frames:
                raise Exception('vary invalid end frame')

            diff = (endValue-startValue)/(endFrame-startFrame)
            
            if knob in frames[startFrame-1].keys():
                frames[startFrame][knob] = frames[startFrame-1][knob]
            else: 
                frames[startFrame][knob] = startValue
            for x in range(startFrame+1, endFrame +1):
                frames[x][knob] = frames[x-1][knob]+diff
    #print(frames)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'
    print(symbols)
    # if a knob is not set in frame 0, it will have a value of ['knob', 0] in symbol table
    for symbol in symbols:
        #print(symbol)
        #print(symbols[symbol])
        if symbols[symbol] == ['knob', 0]:
            symbols[symbol] = 0

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    #print(name)

    for x in range(num_frames):
        #print(symbols)
        #print(frames)
        for knob in frames[x]:
            #print(knob)
            #print(frames[x])
            symbols[knob] = frames[x][knob]
            #print(frames[x][knob])
        #print(symbols)


        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for command in commands:
            #print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                        args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                knob = command['knob']
                if knob != None:
                    knob_value = symbols[knob]
                tmp = make_translate(args[0]*knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                knob = command['knob']
                if knob != None:
                    knob_value = symbols[knob]
                #print(symbols)
                #print("scale: " + str(knob_value))
                tmp = make_scale(args[0]*knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                knob = command['knob']
                if knob != None:
                    knob_value = symbols[knob]
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            # end of commands loop
        if num_frames > 1: 
            saveName = name+f"%03d"%x
            save_extension(screen, saveName)
            if os.path.exists("anim/"+saveName):
                os.remove("anim/"+saveName)
            shutil.move(saveName, "anim")
            print(saveName)
        # end frames loop
    if num_frames > 1: 
        make_animation(name)
