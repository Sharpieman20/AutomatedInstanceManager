


class Wall:

    def __init__(self):

        self.num_instances = 0
        self.is_interactive = False

    def make_layout():
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