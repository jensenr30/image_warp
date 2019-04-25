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


# define the number of dimensions your space has:
N_DIMENSIONS = 2


#===============================================================================
# set up the objects
#===============================================================================
class particle:
    def reset(self):
        self.position = [0] * N_DIMENSIONS
        self.velocity = [0] * N_DIMENSIONS
        self.force    = [0] * N_DIMENSIONS
        self.mass = 1
        self.color = [255, 255, 255]
    
    def __init__(self):
        self.reset()
    
    def calculate_force(self, others):
        """Calculates the force acting on the particle by a group of "other" particles."""
        # reset the force vector
        for d in range(N_DIMENSIONS):
            self.force[d] = 0
        dist = [0] * N_DIMENSIONS
        # for each particle in the "others" list,
        for othr in others:
            dist_squared = 0
            # calculate the distance squared:
            for d in range(N_DIMENSIONS):
                # calculate the square of the distance between the two particles
                dist[d] = self.position[d] - othr.position[d]
                dist_squared += dist[d] ** 2
                # add the force in this dimensions from this particle and the current other particle:
            # calculate the magnitude of the force
#             if dist_squared > 0:
#                 forcemag = self.mass * othr.mass / dist_squared
#             else:
#                 forcemag = 0
#             
            distmag = math.sqrt(dist_squared)
            if distmag == 0:
                distmag = 1
            
            # calculate each component of the force vector
            for d in range(N_DIMENSIONS):
                self.force[d] += self.mass * othr.mass * dist[d] / distmag
                
            

    
    def calculate_position_next(self, time_step):
        for d in range(N_DIMENSIONS):
            self.position[d] += self.force[d] * time_step 


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
    xf = coords_float[0]
    yf = coords_float[1]
    x1 = math.floor(xf)
    y1 = math.floor(yf)
    x2 = math.ceil (coords_float[0])
    y2 = math.ceil (coords_float[1])
    
    # get the information after the decimal point
    xp = xf % 1.0
    yp = yf % 1.0
    
    # if the user selected no interpolation
    if interpolation == interp_method.none:
        x1 = min(x1, dest_size[0]-1)
        y1 = min(y1, dest_size[1]-1)
        index = [x1,y1]
        return dest.get_at(index)
    
    # TODO: write the linear interpolation case
    elif interpolation == interp_method.linear:
        
        # calculate the distance away from each pixel
        black = [0, 0, 0]
        dists_squared = [0] * 4
        colors = black * 4
        
        dists_squared[0] = (  (xp)**2 +   (yp)**2)
        dists_squared[1] = (  (xp)**2 + (1-yp)**2)
        dists_squared[2] = ((1-xp)**2 +   (yp)**2)
        dists_squared[3] = ((1-xp)**2 + (1-yp)**2)
        
        inv_dists_squared = [0] * 4
        sum_invdist_squared = 0
        for i in range(4):
            if dists_squared[i] > 0:
                inv_dists_squared[i] = 1 / dists_squared[i] 
            else:
                inv_dists_squared[i] = 0
            sum_invdist_squared += inv_dists_squared[i]
        
        
        
        
        colors[0] = dest.get_at([x1,y1])
        colors[1] = dest.get_at([x1,y2])
        colors[2] = dest.get_at([x2,y1])
        colors[3] = dest.get_at([x2,y2])
        
        color = [0, 0, 0]
        for c in range(3):
            for p in range(4):
                color[c] += colors[p][c] * dists_squared[p] / sum_invdist_squared
            color[c] = min(color[c],255)
        return color
        
    # unknown interpolation type
    else:
        raise ValueError("unknown interpolation type!")


def clean_up_and_exit(with_an_argument=None):
    """clean up and exit... with an argument!
    
    by default there is no argument."""
    exit(with_an_argument)


def get_warped_coords(projectile, targets, time_step=1, iterations=1):
    """Calculate the warped coordinates. 
    
    """
    # move the projectile N times as requested by the user.
    for i in range(iterations):
        projectile.calculate_force(targets)
        projectile.calculate_position_next(time_step)
    return projectile.position


def infinite_mirror_get_coords(input_image_size, coords_input):
    """
    
    [x_rend, y_rend]  >>>  Transform!  >>>  [x, y]
    All variables are treated as 1-dimensional scalars in floating-point domain."""
    #---------------------------------------------------------------------------
    # perform mirroring of input image space
    #---------------------------------------------------------------------------
    w = input_image_size[0]
    h = input_image_size[1]
    # calculate if we need to mirror the x and y coordinates respectively
    x_mirror = ((coords_input[0]//w) % 2) == 1
    y_mirror = ((coords_input[1]//h) % 2) == 1
    # the simplest possible transformation... 1:1
    x = coords_input[0] % w
    y = coords_input[1] % h
    # mirror the x and y coordinates if necessary
    if x_mirror:
        x = w - x
    if y_mirror:
        y = h - y
    
    x = round(x)
    y = round(y)
    # handle special-case where the coordinate is exactly the size of the input image
    if x == w:
        x = 0
    if y == h:
        y = 0

    
    
    return [x,y]




#===============================================================================
# main program function, graphics display, and user-interface loop:
#===============================================================================
def main():
    
    # pygame module init
    pygame.init()
    # screen size definition
    screen_size = [1920//2, 1080//2]#[1280, 720] 
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
    input_image = pygame.image.load('img_src/green.png')
    input_image_size = input_image.get_size()
    
    # set up image surface to which our warped image will be rendered
    render_size = [1920//2, 1080//2]
    rend = pygame.Surface(render_size)
    print("render_size = " + str(render_size))
    
    
    #---------------------------------------------------------------------------
    # set up the target particles (units are normalized to 1)
    #---------------------------------------------------------------------------
    targets = []
    
#     # upper left corner
#     p = particle()
#     p.position = [0.333,0.333]
#     p.color = [0, 0, 255]
#     targets.append(p)
#     
#     # upper right corner
#     p = particle()
#     p.position = [0.667,0.333]
#     p. mass = 1
#     p.color = [0, 128, 128]
#     targets.append(p)
#     
#     # bottom right corner
#     p = particle()
#     p.position = [0.333,0.667]
#     p.color = [0, 255, 0]
#     targets.append(p)
#     
#     # bottom left corner
#     p = particle()
#     p.position = [0.667,0.667]
#     p.color = [128, 128, 0]
#     targets.append(p)
    
    p = particle()
    p.position = [0.5, 0.5]
    targets.append(p)
    
    #---------------------------------------------------------------------------
    # transform particle dimensions from unit-space to screen-space.  1:screen_width
    #---------------------------------------------------------------------------
    for p in targets:
        for d in range(N_DIMENSIONS):
            p.position[d] *= render_size[d]
            p.velocity[d] *= render_size[d]
    
    #---------------------------------------------------------------------------
    # set up other assorted variables
    #---------------------------------------------------------------------------
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
    projectile = particle()
    projectile.mass = -100
    # define number of iterations for each test projectile
    ITT = 1
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
            projectile.position = coords_rend.copy()
            projectile.velocity = [0] * N_DIMENSIONS
            #print("projectile.position = " + str(projectile.position))
            coords_warped = get_warped_coords(projectile, targets, time_step=1, iterations=ITT)
            #print("coords_warped = " + str(coords_warped))
            coords_input = infinite_mirror_get_coords(input_image_size, coords_warped)
            #print("coords_input = " + str(coords_input))
            # attempt to get the pixel color from input_image
            #try:
            rend.set_at(coords_rend, get_color_at_x_y(input_image, coords_input, interpolation=interp_method.linear))
            #except:
                #pdb.set_trace()
            
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