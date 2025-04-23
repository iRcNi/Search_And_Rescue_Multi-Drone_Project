from shapely.geometry import Polygon, LineString
from shapely.ops import split

padding = 10

def split_polygon_into_equal_areas(polygon_points, num_parts):
    polygon = Polygon(polygon_points)
    if not polygon.is_valid or not polygon.is_simple:
        return [polygon]

    min_x, min_y, max_x, max_y = polygon.bounds
    width = max_x - min_x
    step = width / num_parts

    split_lines = [
        LineString([ (min_x + i * step, min_y), (min_x + i * step, max_y) ])
        for i in range(1, num_parts)
    ]

    result = [polygon]
    for line in split_lines:
        new_result = []
        for poly in result:
            split_poly = split(poly, line)
            polygons = [p for p in split_poly.geoms if p.geom_type == 'Polygon']
            new_result.extend(polygons)
        result = new_result

    return result



def boustrophedon_decomposition(polygon):
    buffered_polygon = polygon.buffer(-padding)
    if buffered_polygon.is_empty or not buffered_polygon.is_valid:
        buffered_polygon = polygon

    min_x, min_y, max_x, max_y = buffered_polygon.bounds
    cells = []
    x = min_x
    step_size = 20
    while x <= max_x:
        line = LineString([(x, min_y), (x, max_y)])
        intersections = buffered_polygon.intersection(line)
        if intersections.is_empty:
            x += step_size
            continue
        if intersections.geom_type == 'MultiLineString':
            cells.extend([seg for seg in intersections.geoms if seg.geom_type == 'LineString'])
        elif intersections.geom_type == 'LineString':
            cells.append(intersections)
        x += step_size
    return cells

def generate_coverage_path(cells):
    path = []
    direction = 1
    for cell in cells:
        x, y = cell.xy
        path.extend(zip(x, y) if direction == 1 else zip(x[::-1], y[::-1]))
        direction *= -1
    return path
