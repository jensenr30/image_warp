# used to receive arguments from the command line 
import sys
argv = sys.argv
print("argv = " + str(argv))
# used to calculate how long image rendering takes.
import time
# used for displaying graphics and loading images.
import pygame
# used for debugging - breakpoints.
import pdb
# calculating ceil() and floor() of floating-point numbers for interpolating. 
import math
# used for enumerations
from enum import Enum



#===============================================================================
# define globals
#===============================================================================
CYCLE_PERIOD_TARGET = 1/10




#===============================================================================
# functions
#===============================================================================
class interp_method(Enum):
    none = 0
    linear = 1


def get_color_at_x_y(dest, coords_float, interpolation=interp_method.none):
    """get the interpolated color of the image at floating-point coordinates.
    
    inputs:
        - dest - the surface (image) which will be used 
        - coords_float=[float x, float y].
    output:
        color of your surface (interpolated) at coordinates <float_x, float_y>"""
    
    dest_size = dest.get_size()
    x1 = math.floor(coords_float[0])
    y1 = math.floor(coords_float[1])
    #x2 = math.ceil (coords_float[0])
    #y2 = math.ceil (coords_float[1])
    
    # if the user selected no interpolation
    if interpolation == interp_method.none:
        x1 = min(x1, dest_size[0]-1)
        y1 = min(y1, dest_size[1]-1)
        index = [x1,y1]
        return dest.get_at(index)
    
    # TODO: write the linear interpolation case
    elif interpolation == interp_method.linear:
        raise ValueError("TODO: write linear interpolation code!")
    
    # unknown interpolation type
    else:
        raise ValueError("unknown interpolation type!")


def clean_up_and_exit(with_an_argument=None):
    """clean up and exit... with an argument!
    
    by default there is no argument."""
    exit(with_an_argument)


def get_input_coords(input_image_size, rend_coords):
    """Transforms the render-surface coordinates to input-image coordinates.
    
    [x_rend, y_rend]  >>>  Transform!  >>>  [x_input, y_input]
    All variables are treated as 1-dimensional scalars in floating-point domain."""
    
    input_w = input_image_size[0]
    input_h = input_image_size[1]
    # calculate if we need to mirror the x and y coordinates respectively
    x_mirror = ((rend_coords[0]//input_w) % 2) == 1
    y_mirror = ((rend_coords[1]//input_h) % 2) == 1
    # the simplest possible transformation... 1:1
    x_input = rend_coords[0] % input_w
    y_input = rend_coords[1] % input_h
    # mirror the x and y coordinates if necessary
    if x_mirror:
        x_input = input_w - x_input
    if y_mirror:
        y_input = input_h - y_input
    # handle special-case where the coordinate is exactly the size of the input image
#     if x_input == input_w:
#         x_input = 0
#     if y_input == input_h:
#         y_input = 0
    
    return [x_input,y_input]




#===============================================================================
# main program function, graphics display, and user-interface loop:
#===============================================================================
def main():
    
    # pygame module init
    pygame.init()
    # screen size definition
    screen_size = [960, 540]#[1280, 720] 
    # create variables to help keep track of FPS
    frames = 0
    FPS = 0
    # variable to hold fraction of the render that is done
    fraction_done = 0.0
    # create the screen and associated program GUI window
    screen = pygame.display.set_mode(screen_size)
    # set the caption of your program window
    program_title = "Image Warp - version 0.1"
    pygame.display.set_caption(program_title + " - FPS=" + str(FPS))
    # load your source image
    input_image = pygame.image.load('img_src/green_wide.png')
    input_image_size = input_image.get_size()
    
    # set up image surface to which our warped image will be rendered
    render_size = [1920*2, 1080*2]
    rend = pygame.Surface(render_size)
    print("render_size = " + str(render_size))
    
    # calculate the pixel colors
    calculating = True
    # stores the current x_rend and y_rend coordinates
    coords_rend = [0,0]
    # this controls if we are supposed to be displaying the rendered image
    displaying  = True
    # this tells you how many output-image pixels you should be coloring per frame
    pxls_per_frame = 10
    # max change per frame.  0.5 indicates a 50% growth/shrinkage possibility.
    pxls_max_change_per_frame = 0.5
    change_max = (1 + pxls_max_change_per_frame)
    change_min = 1/(1 + pxls_max_change_per_frame)
    t_last_FPS_calc = time.time()
    while calculating:
        
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                print("received quit signal; terminating program.")
                calculating = False
                displaying  = False
                clean_up_and_exit()
        
        t_calc_start = time.time()
        for _ in range(pxls_per_frame):
            if coords_rend[0] >= render_size[0]:
                coords_rend[0] = 0
                coords_rend[1] += 1
                if coords_rend[1] >= render_size[1]:
                    # we are done rendering the image
                    calculating = False
            # calculate the input_image coordinates that correspond to the render_coordinates
            coords_input = get_input_coords(input_image_size, coords_rend)
            
            # attempt to get the pixel color from input_image
            try:
                rend.set_at(coords_rend, get_color_at_x_y(input_image, coords_input))
            except:
                pdb.set_trace()
            
            # move to the next pixel
            coords_rend[0] += 1
        t_calc_total = time.time() - t_calc_start
        
        # display time stats
        #print("cycle (s) = " + str(t_calc_total) + "  pxls/frame = " + str(pxls_per_frame))
        # re-calculate how many pixels you should be calculating per cycle in order to achieve your desired target cycle time.
        try:
            change_factor = CYCLE_PERIOD_TARGET / t_calc_total
            if change_factor > change_max:
                pxls_per_frame *= change_max
            elif change_factor < change_min:
                pxls_per_frame *= change_min
            else:
                pxls_per_frame *= change_factor
        except ZeroDivisionError:
            pxls_per_frame *= (1 + pxls_max_change_per_frame)
        pxls_per_frame = round(pxls_per_frame)
        frames += 1
        
        # display the image on the screen
        #pdb.set_trace()
        screen.blit(rend, [0, 0])
        # show the screen to the user
        pygame.display.flip()
        
        now = time.time()
        # perform 1 frame-per-second calculation per second 
        if now - t_last_FPS_calc > 1:
            t_last_FPS_calc = now
            FPS = frames
            fraction_done = (coords_rend[0] + coords_rend[1]*render_size[0])/(render_size[0]*render_size[1])
            pygame.display.set_caption(program_title + " - FPS=" + str(FPS) + "  done=" + str(fraction_done*100.0) + "%")
            frames = 0
            
        
    # end while running
    
    # final window caption update:
    pygame.display.set_caption(program_title + " - FPS=" + "off" + "  done=100%")
    
    # save image to file
    pygame.image.save(rend,"output.jpg")
        
    print("exiting main()")
    exit()
# end main()

if __name__ == "__main__":
    main()