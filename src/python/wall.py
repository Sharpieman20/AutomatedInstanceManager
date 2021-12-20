from pynput import mouse
import obs as obs
import math
import queues
import time
import settings
import keyboard as kb

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
        self.instance_shown_states = {i+1: False for i in range(self.num_instances)}

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
        print('press instance at coords offset {} {}'.format(x, y))
        x_ind = int(x // self.instance_pixel_width)
        y_ind = int(y // self.instance_pixel_width)
        inst_ind = y_ind * self.tile_width + x_ind + 1
        instance_to_press = None
        print('press instance at ind {} {} {}'.format(x_ind, y_ind, inst_ind))
        for inst in queues.get_all_instances():
            if inst.num == inst_ind:
                instance_to_press = inst
                break
        self.press_instance(instance_to_press)

    def press_instance(self, inst):
        # TODO @Sharpieman20 - replace this with hotkey event
        print('press instance inner {}'.format(inst))
        if inst is None:
            return
        print('press instance inner {}'.format(self.is_active()))
        if not self.is_active():
            return
        print('press instance inner {}'.format(self.instance_shown_states[inst.num]))
        if not self.instance_shown_states[inst.num]:
            return
        print('pressed on {}'.format(inst.num))
        if kb.is_pressed(settings.get_hotkeys()['wall-reset-modifier']):
            inst.release()
            return
        if inst.is_ready() or inst.is_paused():
            inst.mark_approved()
        if settings.wall_single_select_mode():
            obs.set_primary_instance(inst)
            obs.exit_wall()

    def update_shown(self):
        for inst in queues.get_all_instances():
            if inst.isShownOnWall != self.instance_shown_states[inst.num]:
                print('update {} to {}'.format(inst.num, inst.isShownOnWall))
                inst.update_obs_wall_visibility()
                time.sleep(0.1)
                self.instance_shown_states[inst.num] = inst.isShownOnWall

    def is_active(self):
        return self.active

    def show(self):
        self.active = True
        self.update_shown()
    
    def hide(self):
        self.active = False

    def enable(self):
        self.show()

    def disable(self):
        self.hide()
        # go to active

class SquareWall(Wall):

    def make_layout(self):
        self.pixel_width = self.instance_pixel_width
        self.pixel_height = self.instance_pixel_height

        self.instance_pixel_width = calculate_square_side(self.num_instances, self.pixel_width, self.pixel_height)
        self.instance_pixel_height = self.instance_pixel_width

        self.tile_width, self.tile_height = tile_fill(self.num_instances, self.instance_pixel_width, self.pixel_width, self.pixel_height)

class ScreenWall(SquareWall):

    def __init__(self, square_wall, num_instances, x_offset, width, y_offset, height):
        self.horizontal_bar = x_offset
        self.vertical_bar = y_offset

        self.num_instances = num_instances
        self.is_interactive = False
        self.pixel_width = width
        self.pixel_height = height

        self.make_layout(square_wall)
        self.initialize_instance_shown_states()

        self.active = False

    def make_layout(self, obs_wall):
        ratio_1 = self.pixel_width / obs_wall.pixel_width
        ratio_2 = self.pixel_height / obs_wall.pixel_height

        my_ratio = min(ratio_1, ratio_2)

        self.horizontal_bar += (self.pixel_width - obs_wall.pixel_width * my_ratio) / 2
        self.vertical_bar += (self.pixel_height - obs_wall.pixel_height * my_ratio) / 2

        self.instance_pixel_width = obs_wall.instance_pixel_width * my_ratio
        self.instance_pixel_height = obs_wall.instance_pixel_width * my_ratio

        self.tile_width = obs_wall.tile_width
        self.tile_height = obs_wall.tile_height
    
    def update_shown(self):
        for inst in queues.get_all_instances():
            if inst.isShownOnWall != self.instance_shown_states[inst.num]:
                self.instance_shown_states[inst.num] = inst.isShownOnWall

    def press_instance_at_coords(self, x, y):
        super().press_instance_at_coords(x - self.horizontal_bar, y - self.vertical_bar)
    
    def enable(self):
        self.active = True
        obs.register_mouse_listener(self)
    
    def disable(self):
        self.active = False
        obs.stop_mouse_listener()


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
