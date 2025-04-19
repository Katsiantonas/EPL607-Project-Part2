from PIL import Image, ImageDraw


WIDTH, HEIGHT = 800, 800
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FOCAL_LENGTH = 1
INFINITY = float('inf')


class Point:

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

class Shape:

    def __init__(self, points: list[Point], color: tuple):
        self.points = points
        self.color = color


def project_point(point: Point):
    f = FOCAL_LENGTH

    x, y, z = point.x, point.y, point.z

    return Point(
        x=(f * x) / z,
        y=(f * y) / z,
        z=1 / z
    )


def project_shape(shape: Shape):
    return Shape(
        points=[project_point(point) for point in shape.points], color=shape.color
    )


def viewport_transform_point(point: Point):
    x, y, z = point.x, point.y, point.z

    return Point(
        x=int((x + 1) * 0.5 * WIDTH),
        y=int((1 - y) * 0.5 * HEIGHT),
        z=z
    )


def viewport_transform_shape(shape: Shape):
    return Shape(
        points=[viewport_transform_point(point) for point in shape.points], color=shape.color
    )


def edge_function(vertex1: Point, vertex2: Point, point: Point):
    v1, v2, p = vertex1, vertex2, point
    return (p.x - v1.x) * (v2.y - v1.y) - (p.y - v1.y) * (v2.x - v1.x)


def get_barycentric_weights(shape: Shape, point: Point):
    w0 = edge_function(shape.points[1], shape.points[2], point)
    w1 = edge_function(shape.points[2], shape.points[0], point)
    w2 = edge_function(shape.points[0], shape.points[1], point)

    return w0, w1, w2


def get_inverse_depth(shape, w0, w1, w2):
    z0, z1, z2 = shape.points[0].z, shape.points[1].z, shape.points[2].z

    return w0 * z0 + w1 * z1 + w2 * z2


def rasterize_shape(shape, image, z_buffer):
    min_x = min([point.x for point in shape.points])
    max_x = max([point.x for point in shape.points])
    min_y = min([point.y for point in shape.points])
    max_y = max([point.y for point in shape.points])

    area = edge_function(*shape.points)

    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            point = Point(x=x, y=y, z=0)

            w0, w1, w2 = get_barycentric_weights(shape, point)

            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                w0 /= area
                w1 /= area
                w2 /= area

                point.z = get_inverse_depth(shape, w0, w1, w2)

                if point.z > z_buffer[y][x]:
                    z_buffer[y][x] = point.z
                    image.putpixel((x, y), shape.color)



def render(shapes: list[Shape]):
    image = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    z_buffer = [[-INFINITY for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for shape in shapes:
        projected_shape = project_shape(shape)
        screen_shape = viewport_transform_shape(projected_shape)

        rasterize_shape(screen_shape, image, z_buffer)

    image.show()
    image.save("rasterized_shapes.png")


render([
    Shape([
        Point(x=-0.6, y=-0.6, z=3.0),
        Point(x=0.4, y=-0.6, z=3.0),
        Point(x=-0.1, y=0.4, z=3.0),
    ], BLUE),
    Shape([
        Point(x=-0.2, y=-0.4, z=2.9),
        Point(x=0.8, y=-0.4, z=3.5),
        Point(x=0.3, y=0.6, z=3.5),
    ], RED),
])
