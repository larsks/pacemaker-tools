from itertools import cycle
import colorsys

Kelly = cycle((
#    '#FFFFFF',  # White
#    '#000000',  # Black
    '#FFB300',  # Vivid Yellow
    '#803E75',  # Strong Purple
    '#FF6800',  # Vivid Orange
    '#A6BDD7',  # Very Light Blue
    '#C10020',  # Vivid Red
    '#CEA262',  # Grayish Yellow
    '#817066',  # Medium Gray
    '#007D34',  # Vivid Green
    '#F6768E',  # Strong Purplish Pink
    '#00538A',  # Strong Blue
    '#FF7A5C',  # Strong Yellowish Pink
    '#53377A',  # Strong Violet
    '#FF8E00',  # Vivid Orange Yellow
    '#B32851',  # Strong Purplish Red
    '#F4C800',  # Vivid Greenish Yellow
    '#7F180D',  # Strong Reddish Brown
    '#93AA00',  # Vivid Yellowish Green
    '#593315',  # Deep Yellowish Brown
    '#F13A13',  # Vivid Reddish Orange
    '#232C16',  # Dark Olive Green
))

class Simple (object):
    def __init__(self, steps=10):
            HSV_tuples = [(x*1.0/(steps), 0.3, 1.0)
                          for x in range((steps))]
            RGB_tuples = ('#%02X%02X%02X' % (int(255*r), int(255*g), int(255*b))
                          for r, g, b in (colorsys.hsv_to_rgb(*x)
                                          for x in HSV_tuples))

            self.colors = cycle(RGB_tuples)

    def __iter__(self):
        return self.colors

    def next(self):
        return self.colors.next()
