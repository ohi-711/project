import pygame
import gif_pygame
from PIL import Image

decor_sprites = {}


def _load_gif_animation(path):
    image = Image.open(path)
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
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return None


def load_decor_sprites():
    global decor_sprites
    decor_sprites = {
        "cloud": _load_gif_or_static("assets/environment/cloud1.gif"),
        "star": _load_gif_or_static("assets/environment/star1.gif"),
    }


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
        if size is not None:
            frame = pygame.transform.smoothscale(frame, (size, size))
        elif scale is not None:
            width = int(frame.get_width() * scale)
            height = int(frame.get_height() * scale)
            frame = pygame.transform.smoothscale(frame, (width, height))
        screen.blit(frame, pos)