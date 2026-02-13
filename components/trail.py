import pygame as pg
import math
import numpy as np

class Trail(pg.sprite.Sprite):
    def __init__(self, speed, allsize, tps, screensize, tp_size):
        super().__init__()
        self.type = "trail"
        self.life = 0.3
        self.size = 0.12 * allsize
        self.screensize = screensize
        self.image = pg.Surface(self.screensize, pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.dn = tp_size[0] / (speed * self.life)
        self.tps = [tps[int(i)] for i in np.arange(0, len(tps), self.dn)]
        self.tps.reverse()
        self.trails = [None] * len(self.tps)
        self.die = 0
        self.live = True

    def update(self, **kwargs):
        previous_pos, mouse_pos = kwargs["previous_pos"], kwargs["mouse_pos"]
        if previous_pos and mouse_pos:
            delta_pos = kwargs["delta_pos"]
            distance = kwargs["distance"]
            mouse_pressed = kwargs["mouse_pressed"]

            self.image.fill((0, 0, 0, 0))

            if self.live:
                angle = math.degrees(math.atan2(delta_pos[0], delta_pos[1]))
                slis = [pg.transform.rotate(pg.transform.scale(ix, (ix.get_size()[0], distance)), angle) for ix in self.tps]
                apos = tuple((x1 + x2) / 2 for x1, x2 in zip(previous_pos, mouse_pos))
                self.trails.append([slis, apos])
            if len(self.trails) >= len(self.tps) or not self.live and self.trails:
                self.trails.pop(0)
            for index, sli in enumerate(self.trails):
                if sli:
                    image = sli[0][index]
                    image.set_alpha(255 * index / len(self.trails))
                    self.image.blit(image, (sli[1][0] - image.get_size()[0] / 2, sli[1][1] - image.get_size()[1] / 2))
            # self.image = apply_glow_effect(self.image, 10, 10)
            if not mouse_pressed:
                self.live = False
            if not self.live:
                if self.die > len(self.tps):
                    self.kill()
                self.die += 1