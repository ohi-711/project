import pygame


def apply_vision_zoom(display_screen, world_surface, center_pos, screen_w, screen_h, coverage=0.7):
    """
    Call after drawing the room to world_surface, and draw any UI directly onto `display_screen` afterward.
    """
    box_w = int(screen_w * coverage)
    box_h = int(screen_h * coverage)

    box_rect = pygame.Rect(0, 0, box_w, box_h)
    box_rect.center = (int(center_pos.x), int(center_pos.y))
    box_rect.clamp_ip(world_surface.get_rect())

    cropped = world_surface.subsurface(box_rect).copy()
    zoomed = pygame.transform.smoothscale(cropped, (screen_w, screen_h))
    display_screen.blit(zoomed, (0, 0))