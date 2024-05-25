import pygame, math, sys, time

pygame.init()
win = pygame.display.set_mode([500, 500], pygame.RESIZABLE)
pygame.display.set_caption("Project: Omikron")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
pygame.font.init()

"""Define all runtime variables"""
xvel = 0
yvel = 0


class timer():
    def __init__(self):
        self.curTime = time.time()
        self.deltaTime = 0
        self.fps = 0
    def frame(self):
        self.deltaTime = time.time() - self.curTime
        self.fps = 1/self.deltaTime
        self.curTime = time.time()

class camera():
    def __init__(self):
        self.position = {"x": 0, "y": 0}
    def render(self, gameObjects):
        for obj in gameObjects:
            win.blit(obj.sprite, (obj.rotated_rect.topleft[0]+obj.position["x"]+self.position["x"], obj.rotated_rect.topleft[1]+obj.position["y"]+self.position["y"]))

class uiForm():
    button = 0
    panel = 1
    text = 2

class uiHandler():
    def __init__(self):
        pass
    def render(self, uiElems):
        for element in uiElems:
            if not element.hidden:
                win.blit(element.sprite, (element.position["x"], element.position["y"]))
            

class uiElement():
    def __init__(self, form = uiForm, scale = tuple, position = tuple, color = tuple, fontcolor = tuple, fontsize = int, hovercolor = tuple, text=str, onclick = list):
        font = pygame.font.Font(None, fontsize)
        self.fontsize = fontsize
        self.form = form
        self.scale = {"x":scale[0],"y":scale[1]}
        self.position = {"x":position[0],"y":position[1]}
        self.color = color
        self.fontcolor = fontcolor
        self.hovercolor = hovercolor
        self.text = text
        self.hidden = False
        self.onclick = onclick
        if form == uiForm.button:
            presprite = pygame.Surface((1000,1000), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (self.position["x"], self.position["y"], self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.position["x"]+self.scale["x"]/2, self.position["y"]+self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite
        if form == uiForm.panel:
            presprite = pygame.Surface((1000,1000), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (self.position["x"], self.position["y"], self.scale["x"], self.scale["y"]), 0, 10)
            self.sprite = presprite
    def frame(self):
        if self.form == uiForm.button:
            mousex, mousey = pygame.mouse.get_pos()
            if mousex > self.position["x"] and mousex < self.position["x"]+self.scale["x"] and mousey > self.position["y"]*2 and mousey < self.position["y"]*2+self.scale["y"]:
                font = pygame.font.Font(None, self.fontsize)
                presprite = pygame.Surface((500,500), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.hovercolor, (self.position["x"], self.position["y"], self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                text_rect = text.get_rect(center=(self.position["x"]+self.scale["x"]/2, self.position["y"]+self.scale["y"]/2))
                presprite.blit(text, text_rect)
                self.sprite = presprite

                if pygame.mouse.get_pressed()[0]:
                    for event in self.onclick:
                        event(self)
            else:
                font = pygame.font.Font(None, self.fontsize)
                presprite = pygame.Surface((500,500), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.color, (self.position["x"], self.position["y"], self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                presprite.blit(text, (self.position["x"]+self.scale["x"]/3, self.position["y"]+self.scale["y"]/3))
                self.sprite = presprite

class gameObject():
    def __init__(self, x, y, shape, angle, scale, scripts):
        winx, winy = win.get_size()
        self.position = {"x": x, "y": y}
        self.scale = scale
        self.scripts = scripts

        presprite = pygame.Surface((500, 500), pygame.SRCALPHA)
        presprite.fill(pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(presprite, (0, 0, 0), (winx/2-25*scale, winy/2-25*scale), 25*scale)
        elif shape == "square":
            # Load the original image
            img = pygame.image.load('player.png')

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.1)
            new_height = int(img.get_height() * 0.1)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (winx/2-new_width/2*scale, winy/2-new_height/2*scale))

        # Rotate the presprite
        self.original_sprite = presprite
        self.sprite = pygame.transform.rotate(self.original_sprite, angle)
        self.rect = self.sprite.get_rect(center=(0,0))
        self.rotated_rect = self.rect.copy()  # Create a copy of the rectangle
        self.rotated_rect.center = (0,0)     # Set the center
    def frame(self):
        for script in self.scripts:
            script(self)
def player(self):
    winx, winy = win.get_size()
    global xvel
    global yvel
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        yvel -= 1
    if keys[pygame.K_s]:
        yvel += 1
    if keys[pygame.K_d]:
        xvel += 1
    if keys[pygame.K_a]:
        xvel -= 1

    self.position["y"] += yvel
    self.position["x"] += xvel

    xvel *= 0.97
    yvel *= 0.97

    gameCamera.position["x"] = -self.position["x"] + winx/2
    gameCamera.position["y"] = -self.position["y"] + winy/2

    mx, my = pygame.mouse.get_pos()
    mx -= gameCamera.position["x"]
    my -= gameCamera.position["y"]
    vx = mx - self.position["x"]
    vy = my - self.position["y"]
    
    angle_rad = math.atan2(vy, vx)
    angle_deg = math.degrees(angle_rad)
    #angle_deg = (angle_deg + 360) % 360

    self.sprite = pygame.transform.rotate(self.original_sprite, -angle_deg)
    self.rotated_rect = self.sprite.get_rect(center=self.rect.center)

def orbit(self):
    self.position["x"] += 5
    self.position["y"] += 5

def quitGame(self):
    pygame.quit()
    sys.exit()

def openSettings(self):
    pass

gameTimer = timer()
gameCamera = camera()
gameUiHandler = uiHandler()
gameObjects = []

gameObjects.append(gameObject(250, 250, "circle", 0, 5, []))
gameObjects.append(gameObject(250, 250, "circle", 0, 1, [orbit]))
gameObjects.append(gameObject(250, 250, "square", 0, 1, [player]))

uiElements = []

uiElements.append(uiElement(uiForm.panel, (75, 1000), (0, -5), (100, 100, 100), (0,0,0), 24, (45,45,45), "", []))
uiElements.append(uiElement(uiForm.button, (100, 50), (5, 5), (145, 145, 145), (0,0,0), 24, (45,45,45), "Null", []))
uiElements.append(uiElement(uiForm.button, (100, 50), (5, 35), (145, 145, 145), (0,0,0), 24, (45,45,45), "Null", []))
uiElements.append(uiElement(uiForm.button, (100, 50), (5, 65), (145, 145, 145), (0,0,0), 24, (45,45,45), "Settings", [openSettings]))
uiElements.append(uiElement(uiForm.button, (100, 50), (5, 95), (145, 145, 145), (0,0,0), 24, (45,45,45), "Quit", [quitGame]))

uiElements[0].hidden = True
uiElements[1].hidden = True
uiElements[2].hidden = True
uiElements[3].hidden = True
uiElements[4].hidden = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                uiElements[0].hidden = not uiElements[0].hidden
                uiElements[1].hidden = not uiElements[1].hidden
                uiElements[2].hidden = not uiElements[2].hidden
                uiElements[3].hidden = not uiElements[3].hidden
                uiElements[4].hidden = not uiElements[4].hidden

    pygame.time.Clock().tick(60)
    gameTimer.frame()

    for obj in gameObjects:
        obj.frame()
    for elem in uiElements:
        elem.frame()

    win.fill((255, 255, 255))
    gameCamera.render(gameObjects)
    gameUiHandler.render(uiElements)
    pygame.display.flip()

pygame.quit()
sys.exit()
