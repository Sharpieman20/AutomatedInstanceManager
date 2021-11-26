from pynput import mouse
import obs as obs
import math
import queues
import time

class Wall:

    def __init__(self, num_instances, instance_width, instance_height):

        self.num_instances = num_instances
        self.is_interactive = False
        self.instance_pixel_width = instance_width
        self.instance_pixel_height = instance_height

        self.make_layout()
        self.initialize_instance_shown_states()

        self.active = False

    def make_layout(self):
        self.tile_width, self.tile_height = tile(self.num_instances)

        self.pixel_width = self.instance_pixel_width * self.tile_width
        self.pixel_height = self.instance_pixel_height * self.tile_height
    
    def initialize_instance_shown_states(self):
        self.instance_shown_states = {i+1: True for i in range(self.num_instances)}
    
    def get_coords_for_instance(self, inst):
        idx = inst.num-1

        instance_row = int(idx / self.tile_width)
        instance_col = int(idx % self.tile_width)

        canvas_x = instance_col * self.instance_pixel_width
        canvas_y = instance_row * self.instance_pixel_height

        print('inst {} at coords {},{} grid size {},{}'.format(inst.num, canvas_x, canvas_y, self.tile_width, self.tile_height))

        return (canvas_x, canvas_y)
    
    def get_all_coords(self):
        pass
    
    def get_pixel_dimensions(self):
        return (self.pixel_width, self.pixel_height)
    
    def press_instance_at_coords(self, x, y):
        # TODO - convert from screen coords to canvas coords
        x_ind = int(x // self.instance_x_height)
        y_ind = int(y // self.instance_y_height)
        instance_to_press = self.instances[x_ind][y_ind]
        self.press_instance(instance_to_press)

    def press_instance(self, inst):
        inst.mark_approved()

    def update_shown(self):
        if not self.is_active():
            return
        for inst in queues.get_all_instances():
            if inst.isShownOnWall != self.instance_shown_states[inst.num]:
                inst.update_obs_wall_visibility()
                time.sleep(0.25)
                self.instance_shown_states[inst.num] = inst.isShownOnWall
    
    def is_active(self):
        return self.active
    
    def show(self):
        self.active = True
    
    def hide(self):
        self.active = False
        for inst in queues.get_all_instances():
            if inst.isShownOnWall:
                obs.set_scene_item_visible('tile{}'.format(inst.num), False)
                time.sleep(0.25)

    def enable(self):
        obs.register_mouse_listener(self)
        show()

    def disable(self):
        obs.stop_mouse_listener()
        hide()
        # go to active

class SquareWall(Wall):

    def make_layout(self):
        self.pixel_width = self.instance_pixel_width
        self.pixel_height = self.instance_pixel_height

        self.instance_pixel_width = calculate_square_side(self.num_instances, self.pixel_width, self.pixel_height)
        self.instance_pixel_height = self.instance_pixel_width

        self.tile_width, self.tile_height = tile_fill(self.num_instances, self.instance_pixel_width, self.pixel_width, self.pixel_height)


def setup_wall_scenes():
    pass


def tile(count):
    width = 1
    height = 1

    while width * height < count:
        if width == height:
            width += 1
        else:
            height += 1

    return (width, height)


def calculate_square_side(count, width, height):
    longer_dim = max(width, height)
    shorter_dim = min(width, height)

    lower_bound_square_side = math.floor(shorter_dim/math.ceil(math.sqrt(count)))
    upper_bound_square_side = math.ceil(math.sqrt(width * height / count))

    for i in range(lower_bound_square_side, upper_bound_square_side+1):
        num_across = math.floor(width / i)
        num_down = math.floor(height / i)

        if (num_across * num_down) < count:
            return i-1
    
    return upper_bound_square_side


def tile_fill(count, square_side, width, height):
    return (int(width/square_side), int(height/square_side))
