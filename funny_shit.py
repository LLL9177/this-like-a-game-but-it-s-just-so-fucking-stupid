import pygame as pg

pg.init()

screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)

player = pg.image.load('syrniki.jpg').convert()
player = pg.transform.scale(player, (player.get_width()/2.5, player.get_height()/2.5))
player_x = 900
player_y = 480

clock = pg.time.Clock()
delta_time = 0.1

running = True
player_rightM = False
player_upM = False
player_downM = False
player_leftM = False
while running:
    screen.fill((0,0,0))

    screen.blit(player, (player_x, player_y))

    if player_upM: player_y -= 60*delta_time
    if player_leftM: player_x -= 60*delta_time
    if player_downM: player_y += 60*delta_time
    if player_rightM: player_x += 60*delta_time

    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_w:
                player_upM = True
            if e.key == pg.K_a:
                player_leftM = True
            if e.key == pg.K_s:
                player_downM = True
            if e.key == pg.K_d:
                player_rightM = True
        if e.type == pg.KEYUP:
            if e.key == pg.K_w:
                player_upM = False
            if e.key == pg.K_a:
                player_leftM = False
            if e.key == pg.K_s:
                player_downM = False
            if e.key == pg.K_d:
                player_rightM = False
    
    pg.display.flip()
    
    delta_time = clock.tick(60)
    delta_time = max(0.001, min(0.1, delta_time))

pg.quit()