from collections import deque
from io import BytesIO
from PIL import Image, ImageDraw

ROOM_SIZE = 48
PADDING = 24
CONNECTION_WIDTH = 6
PLAYER_MARKER_RADIUS = 6

CONNECTION_GAP = 24  # Расстояние между комнатами, можно сделать равным PADDING
CELL_SIZE = ROOM_SIZE + CONNECTION_GAP  # Полный размер ячейки грида (комната + зазор)

COLOR_BACKGROUND = "#212121"
COLOR_ROOM = "#5a5a5a"
COLOR_ROOM_CURRENT = "#e0e0e0"
COLOR_CONNECTION = "#8d8d8d"
COLOR_PLAYER = "#ffc107"

DIRECTION_DELTA = {
    "forward":  (0, -1),
    "backward": (0,  1),
    "left":     (-1, 0),
    "right":    (1,  0),
}

def _should_render(log: dict, state: dict) -> bool:
    menu_context = state["menu_context"]
    opened_menu = menu_context["opened_menu"]

    log_type = log["type"]
    if log_type == "entrance":
        return True
    if log_type == "move":
        if log.get("event") != "combat":
            return True
    if log_type == "combat" and log.get("combat_ended"):
        return True
    if log_type == "continue" and state["menu_context"]["type"] in ("explore", "entrance"):
        if opened_menu not in ("menu_recall", "menu_expanse", "menu_help"):
            return True
    return False

def _compute_grid_positions(rooms: list[dict], start_idx: int) -> dict[int, tuple[int, int]]:
    if start_idx >= len(rooms): return {}
    positions = {start_idx: (0, 0)}
    queue = deque([start_idx])
    while queue:
        room_idx = queue.popleft()
        room, (x, y) = rooms[room_idx], positions[room_idx]
        for direction, neighbor_idx in room["doors"].items():
            if not isinstance(neighbor_idx, int) or neighbor_idx >= len(rooms) or neighbor_idx in positions:
                continue
            dx, dy = DIRECTION_DELTA.get(direction, (0, 0))
            positions[neighbor_idx] = (x + dx, y + dy)
            queue.append(neighbor_idx)
    return positions

def _collect_visible_indices(rooms: list[dict], start_idx: int, depth: int) -> set[int]:
    if start_idx >= len(rooms): return set()
    queue, visited = deque([(start_idx, 0)]), {start_idx}
    while queue:
        room_idx, current_depth = queue.popleft()
        if current_depth >= depth: continue
        for neighbor_idx in rooms[room_idx]["doors"].values():
            if isinstance(neighbor_idx, int) and neighbor_idx < len(rooms) and neighbor_idx not in visited:
                visited.add(neighbor_idx)
                queue.append((neighbor_idx, current_depth + 1))
    return visited

def generate_map_image(log: dict, state: dict) -> bytes | None:
    if not _should_render(log, state):
        return None

    floor, rooms = state["floor"], state["floor"]["rooms"]
    current_room_idx = floor["current_room_index"]
    if current_room_idx is None: return None

    visible_indices = _collect_visible_indices(rooms, current_room_idx, depth=2)
    grid_positions = _compute_grid_positions(rooms, current_room_idx)
    visible_positions = {idx: grid_positions[idx] for idx in visible_indices if idx in grid_positions}
    if not visible_positions: return None

    xs = [pos[0] for pos in visible_positions.values()]
    ys = [pos[1] for pos in visible_positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    img_width  = (max_x - min_x) * CELL_SIZE + ROOM_SIZE + PADDING * 2
    img_height = (max_y - min_y) * CELL_SIZE + ROOM_SIZE + PADDING * 2

    image = Image.new("RGB", (img_width, img_height), color=COLOR_BACKGROUND)
    draw = ImageDraw.Draw(image)

    for room_idx in visible_positions:
        room = rooms[room_idx]
        x, y = visible_positions[room_idx]
        for neighbor_idx in room["doors"].values():
            if neighbor_idx not in visible_positions: continue

            nx, ny = visible_positions[neighbor_idx]

            center_x = (x - min_x) * CELL_SIZE + PADDING + ROOM_SIZE / 2
            center_y = (y - min_y) * CELL_SIZE + PADDING + ROOM_SIZE / 2

            n_center_x = (nx - min_x) * CELL_SIZE + PADDING + ROOM_SIZE / 2
            n_center_y = (ny - min_y) * CELL_SIZE + PADDING + ROOM_SIZE / 2

            draw.line([(center_x, center_y), (n_center_x, n_center_y)], fill=COLOR_CONNECTION, width=CONNECTION_WIDTH)

    for room_idx, (x, y) in visible_positions.items():
        x0 = (x - min_x) * CELL_SIZE + PADDING
        y0 = (y - min_y) * CELL_SIZE + PADDING

        color = COLOR_ROOM_CURRENT if room_idx == current_room_idx else COLOR_ROOM
        draw.rectangle([x0, y0, x0 + ROOM_SIZE, y0 + ROOM_SIZE], fill=color)

        if room_idx == current_room_idx:
            cx, cy = x0 + ROOM_SIZE / 2, y0 + ROOM_SIZE / 2
            r = PLAYER_MARKER_RADIUS
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COLOR_PLAYER)

    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()
