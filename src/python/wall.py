from pynput import mouse



def get_recording_wall()

class Wall:

    def __init__(self, num_instances, instance_width, instance_height):

        self.num_instances = num_instances
        self.is_interactive = False
        self.instance_pixel_width = instance_width
        self.instance_pixel_height = instance_height

        self.make_layout()
        self.initialize_instance_shown_states()

    def make_layout(self):
        self.tile_width, self.tile_height = tile(self.num_instances)

        self.pixel_width = self.instance_pixel_width * self.tile_width
        self.pixel_height = self.instance_pixel_height * self.tile_height
    
    def initialize_instance_shown_states(self):
        self.instance_shown_states = {i: False for i in range(self.num_instances)}
    
    def get_coords_for_instance(self, inst):
        idx = inst.num-1
        instance_row = int(idx // self.tile_width)
        instance_col = int(idx % self.tile_height)

        canvas_x = instance_col * self.instance_pixel_width
        canvas_y = instance_row * self.instance_pixel_height

        return (canvas_x, canvas_y)
    
    def get_all_coords(self):
        pass
    
    def get_pixel_dimensions(self):
        return (self.pixel_width, self.pixel_height)
    
    def press_instance_at_coords(self, x, y):
        x_ind = int(x // self.instance_x_height)
        y_ind = int(y // self.instance_y_height)
        instance_to_press = self.instances[x_ind][y_ind]
        self.press_instance(instance_to_press)

    def press_instance(self, inst):
        inst.mark_approved()
        inst.mark_hidden()

    def update_shown(self):
        for inst in queues.get_all_instances():
            if inst.isShownOnWall != self.instance_shown_states[inst.num]:
                # TODO - replace this with a call to helpers
                obs.set_scene_item_visible('tile{}'.format(inst.num), inst.isShownOnWall)
                self.instance_shown_states[inst.num] = inst.isShownOnWall

    def enable():
        register_mouse_listener(self)
        show()

    def disable(self):
        stop_mouse_listener()
        hide()
        # go to active


def register_mouse_listener(cur_wall):

    def on_click(x, y, button, pressed):
        if pressed:
            if pressed and button == mouse.Button.left:
                cur_wall.press_instance_at_coords(x, y)
                return False

    global mouse_listener
    with mouse.Listener(on_click=on_click) as mouse_listener:
        # listener.start()
        mouse_listener.join()


def stop_mouse_listener():
    global listener
    mouse.Listener.stop(mouse_listener)


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
