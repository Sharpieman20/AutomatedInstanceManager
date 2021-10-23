from pynput import mouse


class Wall:

    def __init__(self, num_instances, instance_width, instance_height):

        self.num_instances = num_instances
        self.is_interactive = False
        self.instance_pixel_width = instance_width
        self.instance_pixel_height = instance_height

        self.make_layout()

    def make_layout(self):
        self.tile_width, self.tile_height = tile(self.num_instances)

        self.pixel_width = self.instance_pixel_width * self.tile_width
        self.pixel_height = self.instance_pixel_height * self.tile_height
    
    def get_coords_for_instance(inst):
        instance_row = int(instance.num // self.tile_width)
        instance_col = int(instance.num % self.tile_height)

        canvax_x = instance_col * self.instance_pixel_width
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
        instance_to_press.press()

def register_mouse_listener():

    def on_click(x, y, button, pressed):
        if pressed:
            if pressed and button == mouse.Button.left:
                cur_wall.press_instance_at_coords(x, y)
                return False

    with mouse.Listener(on_click=on_click) as listener:
        # listener.start()
        listener.join()


def stop_mouse_listener():
    global listener
    mouse.Listener.stop(listener)
    window.quit()


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

def get_coords_for_instance_recording_obs(instance):
    width, height = tile(settings.get_num_instances)

    instance_row = int(instance.num // width)
    instance_col = int(instance.num % height)

    canvax_x = instance_col * settings.get_recording_instance_height()
    canvas_y = instance_row * settings.get_recording_instance_width()

    return (canvas_x, canvas_y)
