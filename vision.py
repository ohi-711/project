import pygame


def apply_vision_zoom(display_screen, world_surface, center_pos, screen_w, screen_h, coverage=0.7):
    """
    Call after drawing the room to world_surface, and draw any UI directly onto `display_screen` after.
    """
    box_w = int(screen_w * coverage)
    box_h = int(screen_h * coverage)

    box_rect = pygame.Rect(0, 0, box_w, box_h)
    box_rect.center = (int(center_pos.x), int(center_pos.y))
    box_rect.clamp_ip(world_surface.get_rect())

    cropped = world_surface.subsurface(box_rect).copy()
    zoomed = pygame.transform.smoothscale(cropped, (screen_w, screen_h))
    display_screen.blit(zoomed, (0, 0))


def apply_vision_circle(display_screen, world_surface, center_pos, screen_w, screen_h,
                         radius=140, edge_softness=60):
    """
    Draws the room at normal scale, then covers everything except a small circle 
    """
    display_screen.blit(world_surface, (0, 0))

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 255))

    cx, cy = int(center_pos.x), int(center_pos.y)

    if edge_softness > 0:
        # adds fade effect to vision circle
        steps = 12
        for i in range(steps, -1, -1):
            r = radius + int(edge_softness * i / steps)
            alpha = int(255 * i / steps)
            pygame.draw.circle(overlay, (0, 0, 0, alpha), (cx, cy), r)
    else:
        pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), radius)

    display_screen.blit(overlay, (0, 0))