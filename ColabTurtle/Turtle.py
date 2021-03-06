from IPython.display import display, HTML
import time
import math

# Created at: 23rd October 2018
#         by: Tolga Atam

# Edited: December 2020
#             by: Jaron Ma 

# Module for drawing classic Turtle figures on Google Colab notebooks.
# It uses html capabilites of IPython library to draw svg shapes inline.
# Looks of the figures are inspired from Blockly Games / Turtle (blockly-games.appspot.com/turtle)

#original tools written by Tolga Atam at https://github.com/tolgaatam/ColabTurtle
#Jaron's modifications include adding in circle(), begin_fill(), end_fill(),
#easing some of the errors raised, and changing the default display settings


#All the following defaults can be changed pretty readily
DEFAULT_WINDOW_SIZE = (600, 600) #any larger than this, and I think some screens may not accommodate the full vertical size of the drawing window
DEFAULT_SPEED = 6 
DEFAULT_TURTLE_VISIBILITY = True
DEFAULT_PEN_COLOR = 'black'
DEFAULT_TURTLE_DEGREE = 0
DEFAULT_BACKGROUND_COLOR = 'whitesmoke'
DEFAULT_IS_PEN_DOWN = True
DEFAULT_PEN_WIDTH = 3

#the following are less convenient to change
DEFAULT_SVG_LINES_STRING = ""
VALID_COLORS = ('white', 'yellow', 'orange', 'red', 'green', 'blue', 'purple', 'grey', 'black')
SVG_TEMPLATE = """
      <svg width="{window_width}" height="{window_height}">
        <rect width="100%" height="100%" fill="{background_color}"/>
        {lines}
        {turtle}
      </svg>
    """
#This is svg-formatted description of the turtle's appearance
TURTLE_SVG_TEMPLATE = """
      <g visibility={visibility} transform="rotate({degrees},{turtle_x},{turtle_y}) translate({turtle_x}, {turtle_y})">
        <ellipse stroke="{turtle_color}" stroke-width="2" fill="transparent" rx="5" ry="6" cx="0" cy="15"/>
        <circle stroke="{turtle_color}" stroke-width="2" fill="transparent" r="4" cx="7.5" cy="-7.5"/>
        <circle stroke="{turtle_color}" stroke-width="2" fill="transparent" r="4" cx="-7.5" cy="-7.5"/>
        <circle stroke="{turtle_color}" stroke-width="2" fill="transparent" r="4" cx="7.5" cy="7.5"/>
        <circle stroke="{turtle_color}" stroke-width="2" fill="transparent" r="4" cx="-7.5" cy="7.5"/>
        <ellipse stroke="{turtle_color}" stroke-width="2" fill="transparent" rx="2" ry="4" cx="0" cy="-12"/>
        <ellipse stroke="{turtle_color}" stroke-width="2" fill="transparent" rx="6" ry="7.2" cx="0" cy="0"/>
        <ellipse stroke="{turtle_color}" stroke-width="2" fill="transparent" rx="10" ry="12" cx="0" cy="0"/>
      </g>
    """

SPEED_TO_SEC_MAP = {1: 1.5, 2: 0.9, 3: 0.7, 4: 0.5, 5: 0.3, 6: 0.18, 7: 0.12, 8: 0.06, 9: 0.04, 10: 0.02, 11: 0.01, 12: 0.001, 13: 0.0001}


# helper function that maps [1,13] speed values to ms delays
def _speedToSec(speed):
    return SPEED_TO_SEC_MAP[speed]


timeout = _speedToSec(DEFAULT_SPEED)
is_turtle_visible = DEFAULT_TURTLE_VISIBILITY
pen_color = DEFAULT_PEN_COLOR
window_size = DEFAULT_WINDOW_SIZE
turtle_pos = (DEFAULT_WINDOW_SIZE[0] // 2, DEFAULT_WINDOW_SIZE[1] // 2)
turtle_degree = DEFAULT_TURTLE_DEGREE
background_color = DEFAULT_BACKGROUND_COLOR
is_pen_down = DEFAULT_IS_PEN_DOWN
svg_lines_string = DEFAULT_SVG_LINES_STRING
pen_width = DEFAULT_PEN_WIDTH
is_filling = False

drawing_window = None


# construct the display for turtle, usually the first command after importing.
def initializeTurtle(initial_speed=DEFAULT_SPEED, initial_window_size=DEFAULT_WINDOW_SIZE):
    global window_size
    global drawing_window
    global timeout
    global is_turtle_visible
    global pen_color
    global turtle_pos
    global turtle_degree
    global background_color
    global is_pen_down
    global svg_lines_string
    global pen_width
    global is_filling
    global svg_fill_string

    if initial_speed not in range(1, 14):
        raise ValueError('initial_speed should be an integer in interval [1,13]')
    timeout = _speedToSec(initial_speed)
    if not (isinstance(initial_window_size, tuple) and len(initial_window_size) == 2 and isinstance(
            initial_window_size[0], int) and isinstance(initial_window_size[1], int)):
        raise ValueError('window_size should be a tuple of 2 integers')

    window_size = initial_window_size
    timeout = _speedToSec(initial_speed)
    
    is_turtle_visible = DEFAULT_TURTLE_VISIBILITY
    pen_color = DEFAULT_PEN_COLOR
    turtle_pos = (window_size[0] // 2, window_size[1] // 2)
    turtle_degree = DEFAULT_TURTLE_DEGREE
    background_color = DEFAULT_BACKGROUND_COLOR
    is_pen_down = DEFAULT_IS_PEN_DOWN
    svg_lines_string = DEFAULT_SVG_LINES_STRING
    pen_width = DEFAULT_PEN_WIDTH
    is_filling = False
    svg_fill_string = ''

    drawing_window = display(HTML(_generateSvgDrawing()), display_id=True)


# helper function for generating svg string of the turtle itself
def _generateTurtleSvgDrawing():
    if is_turtle_visible:
        vis = 'visible'
    else:
        vis = 'hidden'

    return TURTLE_SVG_TEMPLATE.format(turtle_color=pen_color, turtle_x=turtle_pos[0], turtle_y=turtle_pos[1], \
                                      visibility=vis, degrees=turtle_degree - 90)


# helper function for generating the whole svg string
def _generateSvgDrawing():
    return SVG_TEMPLATE.format(window_width=window_size[0], window_height=window_size[1],
                               background_color=background_color, lines=svg_lines_string,
                               turtle=_generateTurtleSvgDrawing())


# helper functions for updating the screen using the latest positions/angles/lines etc.
def _updateDrawing():
    if drawing_window == None:
        raise AttributeError("Display has not been initialized yet. Call initializeTurtle() before using.")
    time.sleep(timeout)
    drawing_window.update(HTML(_generateSvgDrawing()))


# helper function for managing forward/backward movement to 'new_pos' and draw lines if pen is down
def _moveToNewPosition(new_pos):
    global turtle_pos
    global svg_lines_string
    global svg_fill_string

    start_pos = turtle_pos
    if is_pen_down:
        svg_lines_string += """<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-linecap="round" style="stroke:{pen_color};stroke-width:{pen_width}"/>""".format(
            x1=start_pos[0], y1=start_pos[1], x2=new_pos[0], y2=new_pos[1], pen_color=pen_color, pen_width=pen_width)
    if is_filling:
        svg_fill_string += """ L {x1} {y1} """.format(x1=new_pos[0],y1=new_pos[1])

    turtle_pos = new_pos
    _updateDrawing()

# helper function for drawing arcs of radius 'r' to 'new_pos' and draw line if pen is down
def _arctoNewPosition(r,new_pos):
    global turtle_pos
    global svg_lines_string
    global svg_fill_string
    
    start_pos = turtle_pos
    if is_pen_down:
        svg_lines_string += """<path d="M {x1} {y1} A {rx} {ry} 0 0 1 {x2} {y2}" stroke-linecap="round" fill="transparent" style="stroke:{pen_color};stroke-width:{pen_width}"/>""".format(
            x1=start_pos[0], y1=start_pos[1],rx = r, ry = r, x2=new_pos[0], y2=new_pos[1], pen_color=pen_color, pen_width=pen_width)    
    if is_filling:
        svg_fill_string += """ A {rx} {ry} 0 0 1 {x2} {y2} """.format(rx=r,ry=r,x2=new_pos[0],y2=new_pos[1])
    
    turtle_pos = new_pos
    _updateDrawing()


#initialize the string for the svg path of the filled shape    
def begin_fill():
    global is_filling
    global svg_fill_string
    if not is_filling:
        svg_fill_string = """<path d="M {x1} {y1} """.format(x1=turtle_pos[0], y1=turtle_pos[1])
        is_filling = True

    
#terminate the string for the svg path of the filled shape and append to the list of drawn svg shapes    
def end_fill():
    global is_filling
    global svg_fill_string
    global svg_lines_string
    
    if is_filling:
        is_filling = False
        svg_fill_string += """"Z stroke="none" fill="{fillcolor}" />""".format(fillcolor=pen_color)
        svg_lines_string += svg_fill_string
        svg_fill_string = ''
        _updateDrawing()

#draws a circular arc, centered 90degrees to the right of the turtle
def arc(radius, degrees):
    global turtle_degree
    alpha = math.radians(turtle_degree)
    beta = alpha + math.radians(90)
    theta = math.radians(degrees)
    gamma = theta+alpha-math.radians(90)
    
    circle_center = (turtle_pos[0] + radius * math.cos(beta), turtle_pos[1] + radius * math.sin(beta))
    ending_point = (circle_center[0] + radius*math.cos(gamma) ,circle_center[1] + radius*math.sin(gamma))
    
    _arctoNewPosition(radius,ending_point)
    
    turtle_degree = (turtle_degree + degrees) % 360
    _updateDrawing()

#since SVG has some ambiguity when using an arc path for a complete circle...
#the circle function is broken into chunks of at most 90 degrees
def circle(radius, degrees=360):
    if not (isinstance(radius, int) or isinstance(radius, float)):
        raise ValueError('circle radius should be a number')
    if not (isinstance(degrees, int) or isinstance(degrees,float)):
        raise ValueError('degrees should be a number')
        
    if degrees < 0:
        raise ValueError('degrees should be a positive number')
    
    while degrees > 0:
        if degrees > 90:
            arc(radius, 90)
        else:
            arc(radius, degrees)
        degrees += -90

# makes the turtle move forward by 'units' units
def forward(units):
    if not (isinstance(units, int) or isinstance(units, float)):
        raise ValueError('units should be a number')

    alpha = math.radians(turtle_degree)
    ending_point = (turtle_pos[0] + units * math.cos(alpha), turtle_pos[1] + units * math.sin(alpha))

    _moveToNewPosition(ending_point)


# makes the turtle move backward by 'units' units
def backward(units):
    if not (isinstance(units, int) or isinstance(units, float)):
        raise ValueError('units should be a number')
    forward(-1 * units)


# makes the turtle turn right by 'degrees' degrees (NOT radians)
def right(degrees):
    global turtle_degree

    if not (isinstance(degrees, int) or isinstance(degrees, float)):
        raise ValueError('degrees should be a number')

    turtle_degree = (turtle_degree + degrees) % 360
    _updateDrawing()


# makes the turtle face a given direction
def face(degrees):
    global turtle_degree

    if not (isinstance(degrees, int) or isinstance(degrees, float)):
        raise ValueError('degrees should be a number')

    turtle_degree = degrees % 360
    _updateDrawing()


# makes the turtle turn left by 'degrees' degrees (NOT radians)
def left(degrees):
    if not (isinstance(degrees, int) or isinstance(degrees, float)):
        raise ValueError('degrees should be a number')
    right(-1 * degrees)


# raises the pen such that following turtle moves will not cause any drawings
def penup():
    global is_pen_down

    is_pen_down = False
    # TODO: decide if we should put the timout after lifting the pen
    # _updateDrawing()


# lowers the pen such that following turtle moves will now cause drawings
def pendown():
    global is_pen_down

    is_pen_down = True
    # TODO: decide if we should put the timout after releasing the pen
    # _updateDrawing()


# update the speed of the moves, [1,13]
def speed(speed):
    global timeout

    if speed not in range(1, 14):
        raise ValueError('speed should be an integer in the interval [1,13]')
    timeout = _speedToSec(speed)
    # TODO: decide if we should put the timout after changing the speed
    # _updateDrawing()


# move the turtle to a designated 'x' x-coordinate, y-coordinate stays the same
def setx(x):
    if not (isinstance(x, int) or isinstance(x,float)):
        raise ValueError('new x position should be a number')
    if not x >= 0:
        raise ValueError('new x position should be nonnegative')
    _moveToNewPosition((x, turtle_pos[1]))


# move the turtle to a designated 'y' y-coordinate, x-coordinate stays the same
def sety(y):
    if not (isinstance(y, int) or isinstance(y,float)):
        raise ValueError('new y position should be a number')
    if not y >= 0:
        raise ValueError('new y position should be nonnegative')
    _moveToNewPosition((turtle_pos[0], y))

# retrieve the turtle's currrent 'x' x-coordinate
def getx():
    return(turtle_pos[0])


# retrieve the turtle's currrent 'y' y-coordinate
def gety():
    return(turtle_pos[1])


# move the turtle to a designated 'x'-'y' coordinate
def goto(x, y):
    if not (isinstance(x, int) or isinstance(x,float)):
        raise ValueError('new x position should be a number')
    if not x >= 0:
        raise ValueError('new x position should be nonnegative')
    if not (isinstance(y, int) or isinstance(y,float)):
        raise ValueError('new y position sshould be a number')
    if not y >= 0:
        raise ValueError('new y position should be nonnegative')
    _moveToNewPosition((x, y))


# switch turtle visibility to ON
def showturtle():
    global is_turtle_visible

    is_turtle_visible = True
    _updateDrawing()


# switch turtle visibility to ON
def hideturtle():
    global is_turtle_visible

    is_turtle_visible = False
    _updateDrawing()


# change the background color of the drawing area; valid colors are defined at VALID_COLORS
def bgcolor(color):
    global background_color

    if not color in VALID_COLORS:
        print('Possible color error. Valid colors include: ' + str(VALID_COLORS))
    background_color = color
    _updateDrawing()


# change the color of the pen; valid colors are defined at VALID_COLORS
def color(color):
    global pen_color

    if not color in VALID_COLORS:
        print('Possible color error. Valid colors include: ' + str(VALID_COLORS))
    pen_color = color
    _updateDrawing()


# change the width of the lines drawn by the turtle, in pixels
def width(width):
    global pen_width

    if not isinstance(width, int):
        raise ValueError('new width position should be an integer')
    if not width > 0:
        raise ValueError('new width position should be positive')

    pen_width = width
    # TODO: decide if we should put the timout after changing the speed
    # _updateDrawing()
