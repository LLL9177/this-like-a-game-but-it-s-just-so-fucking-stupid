import pygame as pg

# So first we need to initialize the pygame
pg.init()

# Next we wanna create a screen using pg.displat.set_mode(screen_size(x, y))
screen = pg.display.set_mode((640, 640))

# Here i'm just creating an image
img = pg.image.load('syrniki.jpg').convert()

# This resizes the image. Using img.get_width() we are getting the width of image file. Then both height and width we are dividing by 2 to make the image 2
# times smaller.
img = pg.transform.scale(img, (img.get_width()*0.5, img.get_height()*0.5))

# This is a cordinate that we are gonna be changing later which is gonna let us move the image by the x cordinate.
x=-500
# This is a clock that we will be using as definding the frames per second so our image won't move too fast.
clock = pg.time.Clock()

# This is for fps like it will be changed depending on your monitor refresh rate. IDK what it is for actually but let's just assume i'm right
delta_time = 0.1

# This creates a default font that will be later used to display text
font = pg.font.Font(None, size=30)
# This is optional, cuz it is used to define if the program is running. But we can just break out of a loop if we need to quit the window.
running = True
# This is used to indicate if the x value of image being increased, or easier saying - moving.
moving = False
# This just stores a sound data into a sound variable.
sound = pg.mixer.Sound('happybday.mp3')
# This let's us do something without then exiting the.. Idk. Just needs to be used.
while running:
    # This fills the screen with in our case black rgb color (0, 0, 0). Used for image not being copied multiple times while moving.
    screen.fill((0, 0, 0))
    # This adds the image to the screen.
    screen.blit(img, (x, 30))
    # We are creating a hitbox that our image is gonna collide with.
    hitbox=pg.Rect(x, 30, img.get_width(), img.get_height())
    # Here we are definding mouse position and storing it into the mpos variable.
    mpos = pg.mouse.get_pos()
    # Creating a rectangle and storing it into the target variable. positional args: positionX, positionY, Width, Height
    target = pg.Rect(300, 0, 160, 280)
    # adding rectangle looking collision to a target variable aka to a rectangle and storing it into a collision.
    collision = hitbox.colliderect(target)
    # adding collision to a mouse as a dot-looking collision. 
    m_collision = target.collidepoint(mpos)
    # Drawing rectangle stored in a target variable. Positional arguments: target_sreen, color:tuple, rectangle_we_are_drawing
    pg.draw.rect(screen, (255*collision,255*m_collision,0), target)
    # increasing x if the moving is True
    if moving:
        x+=50*delta_time

    # creating text using that font variable. For more info read docs
    text = font.render("Hello, world", True, (255, 255, 255))
    # Drawing out that text (drawing a surface with that text)
    screen.blit(text, (300, 100))

    # storing pg.event into event variable and like doing smth with it:
    for event in pg.event.get():
        # If we press the exit button on the top left (or whatever setting you are using), exiting the loop aka quiting.
        if event.type == pg.QUIT:
            running = False
        # pg.KEYDOWN indicated a key is being pressed. Now the down arrow key
        if event.type == pg.KEYDOWN:
            # thats the pg. key d. letter d.
            if event.key == pg.K_d:
                moving = True
            # Key f
            if event.key == pg.K_f:
                # playing that sound
                sound.play()
        # if releasing the key
        if event.type == pg.KEYUP:
            # the key d
            if event.key == pg.K_d:
                # stop moving
                moving = False
    
    # refreshing the screen
    pg.display.flip()

    # thats for fps
    delta_time = clock.tick(60)
    delta_time = max(0.001, min(0.1, delta_time))

# quiting if the loop is ended
pg.quit()