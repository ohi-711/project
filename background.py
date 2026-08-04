import pygame
import gif_pygame
from PIL import Image
from resource_path import resource_path

decor_sprites = {}
background_surfaces = {}


def _load_gif_animation(path):
    image = Image.open(resource_path(path))
    frames = []

    try:
        for frame_index in range(image.n_frames):
            image.seek(frame_index)
            rgba_frame = image.convert("RGBA")
            surface = pygame.image.frombuffer(rgba_frame.tobytes(), rgba_frame.size, "RGBA")
            duration = image.info.get("duration", 1000) * 0.001
            frames.append([surface, duration])
    finally:
        image.close()

    return gif_pygame.GIFPygame(frames, -1)


def _load_gif_or_static(path):
    try:
        return _load_gif_animation(path)
    except Exception:
        try:
            return pygame.image.load(resource_path(path)).convert_alpha()
        except Exception:
            return None


def _load_background(path):
    try:
        surface = pygame.image.load(resource_path(path))
        return surface.convert()
    except Exception:
        return None


def load_decor_sprites():
    global decor_sprites
    decor_sprites = {
        "cloud": _load_gif_or_static("assets/environment/cloud1.gif"),
        "star": _load_gif_or_static("assets/environment/star1.gif"),
        "rock": pygame.image.load(resource_path("assets/environment/rock1.png")).convert_alpha(),
        "tree1": pygame.image.load(resource_path("assets/environment/tree1.png")).convert_alpha(),
        "tree2": pygame.image.load(resource_path("assets/environment/tree2.png")).convert_alpha(),
        "tree3": pygame.image.load(resource_path("assets/environment/tree3.png")).convert_alpha(),
        "catbuilding": pygame.image.load(resource_path("assets/environment/catbuilding.png")).convert_alpha(),
        "bunnybuilding": pygame.image.load(resource_path("assets/environment/bunnybuilding.png")).convert_alpha(),
    }


def get_native_size(item_type):
    #Return the native (width, height) of a decor asset. None if unknown.

    if not decor_sprites:
        load_decor_sprites()

    decor = decor_sprites.get(item_type)
    if decor is None:
        return None

    try:
        if hasattr(decor, "blit_ready"):
            frame = decor.blit_ready()
            return frame.get_size()
        if isinstance(decor, pygame.Surface):
            return decor.get_size()
    except Exception:
        return None

    return None


def draw(screen, item):
    if not decor_sprites:
        load_decor_sprites()

    item_type = item["type"]
    if item_type not in decor_sprites:
        raise ValueError(f"Unsupported decor type: {item_type}")

    decor = decor_sprites[item_type]
    if decor is None:
        return

    size = item.get("size")
    scale = item.get("scale")
    pos = (item["x"], item["y"])

    if hasattr(decor, "render"):
        if size is not None or scale is not None:
            frame = decor.blit_ready()
            if size is not None:
                frame = pygame.transform.smoothscale(frame, (size, size))
            elif scale is not None:
                width = int(frame.get_width() * scale)
                height = int(frame.get_height() * scale)
                frame = pygame.transform.smoothscale(frame, (width, height))
            screen.blit(frame, pos)
        else:
            decor.render(screen, pos)
    else:
        frame = decor
        if item_type == "rock" and (size is not None or scale is not None):
            if size is not None:
                frame = pygame.transform.smoothscale(frame, (size, size))
            elif scale is not None:
                width = int(frame.get_width() * scale)
                height = int(frame.get_height() * scale)
                frame = pygame.transform.smoothscale(frame, (width, height))
        elif size is not None:
            frame = pygame.transform.smoothscale(frame, (size, size))
        elif scale is not None:
            width = int(frame.get_width() * scale)
            height = int(frame.get_height() * scale)
            frame = pygame.transform.smoothscale(frame, (width, height))
        screen.blit(frame, pos)


def get_background_native_size(path):
    """Returns the native (width, height) of a background image, loading
    and caching it if needed. Used by rooms that draw their background at
    its own resolution instead of stretching it to fill the screen."""
    background_surface = background_surfaces.get(path)
    if background_surface is None:
        background_surface = _load_background(path)
        background_surfaces[path] = background_surface

    if background_surface is None:
        return None
    return background_surface.get_size()


def get_centered_rect(path, screen_w, screen_h):
    """The rect a native-size background occupies once centered on a
    screen_w x screen_h canvas. Returns None if the image can't be loaded."""
    size = get_background_native_size(path)
    if size is None:
        return None
    rect = pygame.Rect(0, 0, *size)
    rect.center = (screen_w // 2, screen_h // 2)
    return rect


def draw_room_background(screen, room):
    background_path = room.get("background_image")
    if not background_path:
        return False

    background_surface = background_surfaces.get(background_path)
    if background_surface is None:
        background_surface = _load_background(background_path)
        background_surfaces[background_path] = background_surface

    if background_surface is None:
        return False

    if room.get("native_size"):
        # Draw the room at its own resolution, centered on screen, and fill everything the image doesn't reach with black.
        screen.fill((0, 0, 0))
        rect = background_surface.get_rect(center=screen.get_rect().center)
        screen.blit(background_surface, rect.topleft)
        return True

    sky = room.get("sky")
    if sky:
        target_rect = pygame.Rect(0, sky["height"], screen.get_width(), screen.get_height() - sky["height"])
    else:
        target_rect = screen.get_rect()

    if background_surface.get_size() != (target_rect.width, target_rect.height):
        background_surface = pygame.transform.smoothscale(background_surface, (target_rect.width, target_rect.height))
        background_surfaces[background_path] = background_surface

    screen.blit(background_surface, target_rect.topleft)
    return True


decor_masks_cache = {}

# for letting the player go through transparent parts of the decor.
def get_collision_mask(item):
    if not decor_sprites:
        load_decor_sprites()

    item_type = item["type"]
    decor = decor_sprites.get(item_type)
    if decor is None:
        return None

    size = item.get("size")
    scale = item.get("scale")
    pos = (item["x"], item["y"])

    frame = decor.blit_ready() if hasattr(decor, "blit_ready") else decor
    if frame is None:
        return None

    if size is not None:
        frame = pygame.transform.smoothscale(frame, (size, size))
    elif scale is not None:
        w = int(frame.get_width() * scale)
        h = int(frame.get_height() * scale)
        frame = pygame.transform.smoothscale(frame, (w, h))

    cache_key = (item_type, frame.get_size())
    mask = decor_masks_cache.get(cache_key)
    if mask is None:
        mask = pygame.mask.from_surface(frame)
        decor_masks_cache[cache_key] = mask

    rect = pygame.Rect(pos[0], pos[1], frame.get_width(), frame.get_height())
    return mask, rect