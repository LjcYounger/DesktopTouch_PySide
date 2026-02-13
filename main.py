import pygame as pg
import time
import math

from img_utils import *

from components.mesh_tri import MeshTri
from components.ring import Ring
from components.ringx import RingX
from components.trail import Trail

#from utils import get_fps

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((960, 540))
pg.display.set_caption("ljc")
#pg.display.set_icon(pg.image.load("pictures/icon.ico"))
screen.fill((0, 0, 0))
touch_screen = pg.Surface(screen.get_size(), pg.SRCALPHA)
pg.display.flip()
clock = pg.time.Clock()


def sign(x):
    if x < 0:
        return -1
    else:
        return 1

touches = pg.sprite.Group()
spark_texture = pg.image.load("pictures/effects/FX_TEX_Triangle_02.png").convert_alpha()

effect_patterns = [pg.image.load("pictures/effects/FX_TEX_Circle_01.png").convert_alpha(),
                   pg.transform.flip(spark_texture, False, True),
                   spark_texture,
                   pg.image.load("pictures/effects/FX_TEX_Trail_03.png").convert_alpha()]

running = True
animation_speed = 120  # 120
max_size = 512

mouse_clicked = False
click_count = 999999
trail_active = False
mouse_pressed = False
trail_sprites = []

trail_colors = [[(0, 100, 255), 0],
                [(0, 100, 255), 0.21],
                [(0, 24, 72), 0.421],
                [(0, 0, 0), 1],
                [(0, 0, 0), 1.1]]

trail_pattern_size = effect_patterns[3].get_size()
trail_time = 0
trail_delta_time = 1 / trail_pattern_size[0]
for x_coord in range(0, trail_pattern_size[0]):
    sprite_slice = effect_patterns[3].subsurface(x_coord, 0, 1, trail_pattern_size[1])
    color = change_color(trail_colors, trail_time)
    sprite_slice = pg.transform.scale(sprite_slice, (1, max_size / 512 * 4))
    sprite_slice = change_image_by_grayscale(sprite_slice, color, 255, 1, True)
    trail_sprites.append(sprite_slice)
    trail_time += trail_delta_time

mouse_pos = pg.mouse.get_pos()
initial_position = final_position = None
distance_threshold = max_size / 8
accumulated_distance = 0

#fps = get_fps()
n = 0
while running:
    clock.tick(60)
    touch_screen.fill((0, 0, 0))
    screen.fill((0, 0, 0))
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            time.sleep(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            pg.mixer.Sound("audios/UI/UI_Button_Touch.ogg").play()
            mouse_pressed = True

            previous_pos = mouse_pos
            initial_position = mouse_pos = pg.mouse.get_pos()
            distance = math.sqrt(sum((px - qx) ** 2 for px, qx in zip(previous_pos, mouse_pos)))
            delta_pos = tuple(px - qx for px, qx in zip(previous_pos, mouse_pos))

            touch_ring_effect = Ring(animation_speed, max_size, effect_patterns, mouse_pos)
            touch_trail_effect = Trail(animation_speed, max_size, trail_sprites, screen.get_size(), trail_pattern_size)
            touches.add(touch_ring_effect, touch_trail_effect)

            click_count = 0
            start_time = time.perf_counter()
        if event.type == pg.MOUSEBUTTONUP:
            mouse_pressed = False

    previous_pos = mouse_pos
    mouse_pos = pg.mouse.get_pos()
    distance = math.sqrt(sum((px - qx) ** 2 for px, qx in zip(previous_pos, mouse_pos)))
    delta_pos = tuple(px - qx for px, qx in zip(mouse_pos, previous_pos))
    if mouse_pressed:
        # pg.draw.circle(screen, (0, 0, 255), pg.mouse.get_pos(), 6)
        if accumulated_distance + distance >= distance_threshold:
            times, remainder = divmod(accumulated_distance + distance, distance_threshold)
            times = int(times)
            for time_index in range(0, times):
                delta_x = delta_pos[0] * (distance_threshold * time_index + remainder) / distance
                delta_y = delta_pos[1] * (distance_threshold * time_index + remainder) / distance
                final_position = (mouse_pos[0] - delta_x, mouse_pos[1] - delta_y)
                touch_ring_effect_4 = RingX(animation_speed, max_size, effect_patterns, final_position, 4)
                # pg.draw.circle(screen, (255, 0, 0), final_position, 5)
                touches.add(touch_ring_effect_4)
            accumulated_distance = remainder
        else:
            accumulated_distance += distance

    if click_count < 4:
        delta_time = time.time() - start_time
        if delta_time >= 0.01:
            touch_ring_effect_3 = RingX(animation_speed, max_size, effect_patterns, initial_position, 3)
            touches.add(touch_ring_effect_3)
            if click_count < 2:
                touch_mesh_tri_effect = MeshTri(animation_speed, max_size, effect_patterns, initial_position)
                touches.add(touch_mesh_tri_effect)
            start_time = time.time()
            click_count += 1

    touches.update(delta_pos=delta_pos, 
                   distance=distance, 
                   previous_pos=previous_pos, 
                   mouse_pos=mouse_pos, 
                   mouse_pressed=mouse_pressed)
    
    touches.draw(touch_screen)
    screen.blit(touch_screen, (0, 0))
    pg.display.flip()
"""
    if n % 30 == 0:
        print(fps())
    else:
        fps()
    n += 1
"""