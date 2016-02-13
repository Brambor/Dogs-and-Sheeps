import sys

from stuff import main, values

ver = "graphic"
picnames = ["Play","Quit"]
try:
    import pygame

    x, y = values.map_x*12, values.map_y*8
    pygame.init()
    screen = pygame.display.set_mode((x, y))
    pygame.display.set_caption("Dogs & Sheeps")
    pygame.display.init()
    #pygame.display.set_icon(pygame.image.load("pic/corpse.png")) #Later, I don't want to do it now...
    bg_color=(0,0,0)


    buttons = pygame.sprite.Group()
    place = y/2 - 10 * (len(picnames) - 1) - 8
    for picname in picnames:
        button = pygame.sprite.Sprite()
        button.name = picname
        button.image = pygame.image.load("stuff/pic/{}.PNG".format(picname)).convert_alpha()
        button.rect = button.image.get_rect()
        button.rect.center = (x/2, place)
        place += 20
        buttons.add(button)

    buttons.draw(screen)

except ImportError:
    ver = "text"
    print("Graphic version is not suported because pygame is not instaled. Swiching to text version.")

while True:
    if ver == "graphic":
        pygame.display.update()
        for event in pygame.event.get():
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.rect.left < pos[0] < button.rect.right and button.rect.top < pos[1] < button.rect.bottom:
                        if button.name == "Play":
                            print("press ESC to open menu")
                            main.Run(ver)
                        elif button.name == "Quit":
                            sys.exit()
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):#() not needed
                #print("Thanks for using!")
                #sleep(2)
                sys.exit()
        buttons.draw(screen)
    elif ver == "text":
        for i in range(len(picnames)):
            print("{}. {}".format(i + 1, picnames[i]))
        choice = input()
        if choice == "1" or choice == "Play":
            main.Run(ver)
        elif choice == "2" or choice == "Quit":
            sys.exit()
        else:
            print("Pick agin!")
