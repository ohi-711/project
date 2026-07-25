import pygame


def apply_vision_zoom(display_screen, world_surface, center_pos, screen_w, screen_h, coverage=0.7):
    """Crops a box centered on `center_pos` out of `world_surface` and
    scales it up to fill the entire window, giving a "camera zoom"
    effect rather than just masking off the edges.

    - `world_surface` should be a surface the same size as the window
      that the room/npcs/player were drawn onto (NOT the real display).
    - `display_screen` is the actual window surface (from
      pygame.display.set_mode) that the zoomed result gets blitted to.
    - The crop box is `coverage` * screen size (0.7 = 70%) and is
      clamped so it never tries to read outside world_surface.

    Call this AFTER drawing the room to world_surface, and draw any UI
    (like the dialogue box) directly onto `display_screen` afterward so
    it stays full-size and readable.
    """
    box_w = int(screen_w * coverage)
    box_h = int(screen_h * coverage)

    box_rect = pygame.Rect(0, 0, box_w, box_h)
    box_rect.center = (int(center_pos.x), int(center_pos.y))
    box_rect.clamp_ip(world_surface.get_rect())

    cropped = world_surface.subsurface(box_rect).copy()
    zoomed = pygame.transform.smoothscale(cropped, (screen_w, screen_h))
    display_screen.blit(zoomed, (0, 0))