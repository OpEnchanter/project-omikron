import pygame, math, sys, time, random, json

score = 0
ingame = True
tutorial = True

globalMenuPressed = False

pygame.mixer.pre_init(44100, -16, 1, 2048)  # Adjust buffer size as needed
pygame.init()
out = pygame.display.set_mode([1920, 1080], pygame.FULLSCREEN, pygame.DOUBLEBUF)
ox, oy = out.get_size()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN])
win = pygame.Surface((ox,oy))

pygame.display.set_caption("Project: Omikron")
icon = pygame.image.load("./resources/icon.png").convert_alpha()
pygame.display.set_icon(icon)
pygame.font.init()
pygame.joystick.init()

print(pygame.joystick.get_count())
joystick = False
if (pygame.joystick.get_count() > 0):
    joystick = pygame.joystick.Joystick(0)

shootsfx = pygame.mixer.Sound("./resources/audio/shoot.wav")
selectsfx = pygame.mixer.Sound("./resources/audio/select.wav")
explodesfx = pygame.mixer.Sound("./resources/audio/explosion.wav")
hitsfx = pygame.mixer.Sound("./resources/audio/hit.wav")
deathsfx = pygame.mixer.Sound("./resources/audio/death.wav")
noammosfx = pygame.mixer.Sound("./resources/audio/noammo.wav")
dingsfx = pygame.mixer.Sound("./resources/audio/complete.wav")
pygame.mixer.music.load('./resources/audio/project-omikron-menu.wav')
pygame.mixer.music.set_volume(0.2)
shootsfx.set_volume(0.4)
deathsfx.set_volume(0.8)
selectsfx.set_volume(0.4)
explodesfx.set_volume(0.8)
noammosfx.set_volume(0.8)
hitsfx.set_volume(0.8)

assets = {
    "planet":pygame.image.load("./resources/sprites/planets/planet.png").convert_alpha(),
    "planet-red":pygame.image.load("./resources/sprites/planets/planet-red.png").convert_alpha(),
    "planet-orange":pygame.image.load("./resources/sprites/planets/planet-orange.png").convert_alpha(),
    "planet-green":pygame.image.load("./resources/sprites/planets/planet-green.png").convert_alpha(),
    "planet-blue":pygame.image.load("./resources/sprites/planets/planet-blue.png").convert_alpha(),
    "planet-purple":pygame.image.load("./resources/sprites/planets/planet-purple.png").convert_alpha(),
    "planet-alt":pygame.image.load("./resources/sprites/planets/planet-alt.png").convert_alpha(),
    "planet-red-alt":pygame.image.load("./resources/sprites/planets/planet-red-alt.png").convert_alpha(),
    "planet-orange-alt":pygame.image.load("./resources/sprites/planets/planet-orange-alt.png").convert_alpha(),
    "planet-green-alt":pygame.image.load("./resources/sprites/planets/planet-green-alt.png").convert_alpha(),
    "planet-blue-alt":pygame.image.load("./resources/sprites/planets/planet-blue-alt.png").convert_alpha(),
    "planet-purple-alt":pygame.image.load("./resources/sprites/planets/planet-purple-alt.png").convert_alpha(),
    "bullet":pygame.image.load("./resources/sprites/bullet.png").convert_alpha()
    }
particleAssets = {
    "expFr0":pygame.image.load("./resources/sprites/animated/explosion/frame0.png").convert_alpha(),
    "expFr1":pygame.image.load("./resources/sprites/animated/explosion/frame1.png").convert_alpha(),
}

for name, frame in particleAssets.items():
    scalex = frame.get_width()*0.3
    scaley = frame.get_height()*0.3
    particleAssets[name] = pygame.transform.scale(frame, (scalex, scaley))

# Play the song indefinitely
pygame.mixer.music.play(loops=-1)


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

class cameraAction():
    cameraShake = 0

class camera():
    def __init__(self):
        self.position = {"x": 0, "y": 0}
        self.cameraActionStart = {"x":0,"y":0}
        self.runningCameraAction = False
        self.camActionType = 0
        self.camActionFramesLeft = 0
    def render(self, gameObjects):
        self.cameraOffset = [0,0]
        if self.runningCameraAction and self.camActionType == cameraAction.cameraShake:
            if self.camActionFramesLeft % 5 == 0:
                self.cameraOffset = [random.randint(-3*self.camActionFramesLeft,3*self.camActionFramesLeft), random.randint(-3*self.camActionFramesLeft,3*self.camActionFramesLeft)]
            self.camActionFramesLeft -= 1
        if self.camActionFramesLeft <= 0:
            self.runningCameraAction = False
        for obj in gameObjects:
            renderedPosition = [obj.rotated_rect.topleft[0]+obj.position["x"]+self.position["x"]+self.cameraOffset[0], obj.rotated_rect.topleft[1]+obj.position["y"]+self.position["y"]+self.cameraOffset[1]]
            scaleX = obj.sprite.get_width()
            scaleY = obj.sprite.get_height()
            if (renderedPosition[0] > -scaleX and renderedPosition[0] < win.get_width()+scaleX and renderedPosition[1] > -scaleY and renderedPosition[1] < win.get_height()+scaleY):
                win.blit(obj.sprite, (renderedPosition[0], renderedPosition[1]))
                obj.rendered = True
            else:
                obj.rendered = False
    def runCameraAction(self, action):
        if not self.runningCameraAction:
            self.runningCameraAction = True
            self.cameraActionStart = self.position
            self.camActionType = action
            self.camActionFramesLeft = 10
            
            
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
    def __init__(self, form = uiForm, scale = tuple, position = tuple, color = pygame.SRCALPHA, fontcolor = tuple, fontsize = int, hovercolor = tuple, text=str, onclick = list):
        font = pygame.font.Font('resources/font/pixel.ttf', fontsize)
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
        self.clicked = False
        if form == uiForm.button:
            presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite
            self.hovered = False
        if form == uiForm.panel:
            presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite
    def frame(self):
        if self.form == uiForm.button and not self.hidden:
            mousex, mousey = pygame.mouse.get_pos()
            if mousex > self.position["x"] and mousex < self.position["x"]+self.scale["x"] and mousey > self.position["y"] and mousey < self.position["y"]+self.scale["y"] or self.hovered:
                font = pygame.font.Font('resources/font/pixel.ttf', self.fontsize)
                presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.hovercolor, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
                presprite.blit(text, text_rect)
                self.sprite = presprite
                
                global globalMenuPressed

                if pygame.mouse.get_pressed()[0] and not self.clicked or globalMenuPressed and not self.clicked:
                    selectsfx.play()
                    for event in self.onclick:
                        event(self)
                    self.clicked = True

                interactBtn = True
                if joystick:
                    joystick.get_button(14)


                if not pygame.mouse.get_pressed()[0] and self.clicked or not interactBtn and self.clicked:
                    self.clicked = False
                    globalMenuPressed = False
            else:
                font = pygame.font.Font('resources/font/pixel.ttf', self.fontsize)
                presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
                presprite.blit(text, text_rect)
                self.sprite = presprite
                self.clicked = False
    def relsprite(self):
        font = pygame.font.Font('resources/font/pixel.ttf', self.fontsize)
        if self.form == uiForm.button:
            presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite
        if self.form == uiForm.panel:
            presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite

class gameObject():
    def gensprite(self):
        presprite = pygame.Surface((500, 500), pygame.SRCALPHA)
        presprite.fill(pygame.SRCALPHA)
        if self.shape == "planet":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet", "planet-alt"]
            choice = random.choice(variations)
            self.pattern = variations.index(choice)
            img = assets[choice]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "planet-red":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet-red", "planet-red-alt"]
            for variant in variations:
                if variations.index(variant) != self.pattern:
                    variations.remove(variant)
            img = assets[random.choice(variations)]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "planet-orange":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet-orange", "planet-orange-alt"]
            for variant in variations:
                if variations.index(variant) != self.pattern:
                    variations.remove(variant)
            img = assets[random.choice(variations)]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "planet-green":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet-green", "planet-green-alt"]
            for variant in variations:
                if variations.index(variant) != self.pattern:
                    variations.remove(variant)
            img = assets[random.choice(variations)]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "planet-blue":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet-blue", "planet-blue-alt"]
            for variant in variations:
                if variations.index(variant) != self.pattern:
                    variations.remove(variant)
            img = assets[random.choice(variations)]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "planet-purple":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            variations = ["planet-purple", "planet-purple-alt"]
            for variant in variations:
                if variations.index(variant) != self.pattern:
                    variations.remove(variant)
            img = assets[random.choice(variations)]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.planet(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif self.shape == "mesh":
            # Load the original image
            img = pygame.image.load('./resources/sprites/player.png').convert_alpha()

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))
        elif self.shape == "bullet":
            # Load the original image
            img = assets["bullet"]

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))
        elif self.shape == "speeder":
            # Load the original image
            img = pygame.image.load('./resources/sprites/enemy.png').convert_alpha()

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))
        elif self.shape == "brute":
            # Load the original image
            img = pygame.image.load('./resources/sprites/brute.png').convert_alpha()

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))
        elif self.shape == "freighter":
            # Load the original image
            img = pygame.image.load('./resources/sprites/freighter.png').convert_alpha()

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))
        elif self.shape == "rect":
            pygame.draw.rect(presprite, (0,0,255), (0,0,500,500))
        elif self.shape == "wormhole":
            # Load the original image
            img = pygame.image.load('./resources/sprites/wormhole.png').convert_alpha()

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*self.scale, 500/2-new_height/2*self.scale))

        # Rotate the presprite
        self.original_sprite = presprite
        self.sprite = pygame.transform.rotate(self.original_sprite, self.angle)
        self.rect = self.sprite.get_rect(center=(0,0))
        self.rotated_rect = self.rect.copy()  # Create a copy of the rectangle
        self.rotated_rect.center = (0,0)     # Set the center
    def __init__(self, x, y, shape, angle, scale, scripts, timer):
        winx, winy = win.get_size()
        self.position = {"x": x, "y": y}
        self.angle = 0
        self.scale = scale
        self.shape = shape
        self.scripts = scripts
        self.timer = timer
        self.xvel = 0
        self.yvel = 0
        self.isEnemy = False
        self.followingPlayer = False
        self.rendered = True
        self.hp = 5
        self.maxhp = 5
        self.lastShotTime = 0
        self.target_angle = 0

        self.gensprite()
    def frame(self):
        for script in self.scripts:
            script(self)

class particleShape():
    explosion = 0
    shockwave = 1


class particle():
    def __init__(self, strt, v, l, s, d):
        self.position = strt
        self.velocity = v
        self.shape = s
        self.remainingTime = l
        self.drag = d
        self.frame = 0
        self.frames = []
        self.lagDelay = 0
        self.animated = False
        
        presprite = pygame.Surface((500,500), pygame.SRCALPHA)
        

        if s == particleShape.explosion:
            self.animated = True
            frame1 = particleAssets["expFr0"]

            frame2 = particleAssets["expFr1"]

            self.frames = [frame1, frame2]

            presprite.blit(frame1, (250,250))
            #pygame.draw.planet(presprite, ((255, 123, 41)), (250,250), 7)
        if s == particleShape.shockwave:
            pygame.draw.planet(presprite, (255,0,0), (250, 250), 1, 5)
        self.sprite = presprite
    def anim_nextFrame(self):
        if self.animated:
            if self.shape == particleShape.explosion:
                if self.frame > len(self.frames)-1:
                    self.frame = 0
                presprite = pygame.Surface((500,500), pygame.SRCALPHA)
                curframe = self.frames[int(self.frame)]
                presprite.blit(curframe, (250,250))
                self.sprite = presprite
                if self.lagDelay >= 10:
                    self.frame += 1
                    self.lagDelay = 0
                self.lagDelay += 1
            if self.shape == particleShape.shockwave:
                presprite = pygame.Surface((500,500), pygame.SRCALPHA)
                presprite.blit(self.frames[int(self.frame)], (250,250))
                pygame.draw.planet(presprite, (255,0,0), (250,250), (frame), 5)
                self.sprite = presprite
                if self.lagDelay >= 10:
                    self.frame += 1
                    self.lagDelay = 0
                self.lagDelay += 1

class particleSystem():
    def __init__(self, sceneCamera):
        self.particles = []
        self.cam = sceneCamera
    def spawnParticle(self, start, velocity, lifetime, shape, drag):
        particleObj = particle({"x":start[0],"y":start[1]}, {"x":velocity[0],"y":velocity[1]}, lifetime, shape, 1-drag)
        self.particles.append(particleObj)
    def render(self):
        for particle in self.particles:
            if particle.remainingTime > 0:
                particle.remainingTime -= 1
                particle.anim_nextFrame()
                particle.position["x"] += particle.velocity["x"]
                particle.position["y"] += particle.velocity["y"]
                particle.velocity["x"] *= particle.drag
                particle.velocity["y"] *= particle.drag

                camx = self.cam.position["x"]
                camy = self.cam.position["y"]

                camoffx = self.cam.cameraOffset[0]
                camoffy = self.cam.cameraOffset[1]

                win.blit(particle.sprite, (particle.position["x"]+camx+camoffx, particle.position["y"]+camy+camoffy))
            else:
                self.particles.pop(self.particles.index(particle))

class inventoryManager():
    def __init__(self):
        self.inventory = {}
    def init_item(self, name = str):
        self.inventory[name] = {"amount":0}
        print(f"Item, {name} initialized")
    def add_item(self, item_name = str, ammt = int):
        self.inventory[item_name]["amount"] += ammt
        print(f"Added, {ammt} of {item_name} to inventory")
    def rem_item(self, item_name = str, ammt = int):
        if (self.inventory[item_name]["amount"] >= ammt):
            self.inventory[item_name]["amount"] -= ammt
            print(f"Removed {ammt} of {item_name}")
            return True
        else:
            print(f"Unable to remove {ammt} of {item_name}")
            return False
    def set_item(self, item_name = str, ammt = int):
        self.inventory[item_name]["amount"] = ammt
        print(f"Set, {item_name} amount to {ammt}")
        

def playerScript(self):
    global paused
    if not paused:
        winx, winy = win.get_size()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.yvel -= 10
        if keys[pygame.K_s]:
            self.yvel += 10
        if keys[pygame.K_d]:
            self.xvel += 10
        if keys[pygame.K_a]:
            self.xvel -= 10

        if self.position["x"] < -7500:
            self.position["x"] = -7500
        if self.position["x"] > 7500:
            self.position["x"] = 7500

        if self.position["y"] < -7500:
            self.position["y"] = -7500
        if self.position["y"] > 7500:
            self.position["y"] = 7500


        self.position["x"] += self.xvel * self.timer.deltaTime
        self.position["y"] += self.yvel * self.timer.deltaTime

        self.xvel *= 0.97
        self.yvel *= 0.97

        gameCamera.position["x"] = -self.position["x"] + winx/2
        gameCamera.position["y"] = -self.position["y"] + winy/2

        angle = 0

        if joystick == False:

            mx, my = pygame.mouse.get_pos()
            mx -= gameCamera.position["x"]
            my -= gameCamera.position["y"]
            vx = mx - self.position["x"]
            vy = my - self.position["y"]
            
            angle_rad = math.atan2(vy, vx)
            angle = math.degrees(angle_rad)
        else:
            mx = joystick.get_axis(0)
            my = joystick.get_axis(1)
            
            angle_rad = math.atan2(my, mx)
            angle = math.degrees(angle_rad)

            if joystick.get_axis(5) > -0.5:  # Adjust threshold as needed
                axis_value = joystick.get_axis(5)
                angle_rad = math.radians(angle-90)  # Convert angle to radians
                self.xvel += math.sin(-angle_rad) * (axis_value + 1) * 10
                self.yvel += math.cos(-angle_rad) * (axis_value + 1) * 10

        self.angle = angle

        self.sprite = pygame.transform.rotate(self.original_sprite, -angle)
        self.rotated_rect = self.sprite.get_rect(center=self.rect.center)

        # Temporary condition for when hp is 0
        if self.hp <= 0:
            self.hp = self.maxhp
            global inventory
            removeCreds = inventory.rem_item("Credit", 10)
            deathsfx.play()
            if not removeCreds:
                gotoTitle(self)
            if removeCreds:
                reset(self)

def speeder(self):
    global paused
    if not paused and self.rendered:

        """Enemy AI"""
        winx, winy = win.get_size()

        self.position["y"] += self.yvel * self.timer.deltaTime
        self.position["x"] += self.xvel * self.timer.deltaTime

        self.xvel *= 0.94
        self.yvel *= 0.94

        hx = self.home["x"]
        hy= self.home["y"]

        hvx = hx-self.position["x"]
        hvy = hy-self.position["y"]

        hdist = math.sqrt(hvx**2 + hvy**2)

        px = gameObjects[len(gameObjects)-1].position["x"]
        py = gameObjects[len(gameObjects)-1].position["y"]
        
        vx = px-self.position["x"]
        vy = py-self.position["y"]

        pdist = math.sqrt(vx**2 + vy**2)

        if hdist < 10 and self.gotoHome:
            self.gotoHome = False
        
        if pdist > 350 and pdist < 680 and not self.followingPlayer:
            angle_rad = math.atan2(vy, vx)
            angle_deg = math.degrees(angle_rad)

            self.angle = angle_deg
        if hdist < 1750 and not self.gotoHome:

            if pdist < 350 and pdist > 100 or self.followingPlayer and pdist > 100:

                # Allow enemy to shoot at player
                if (time.time() - self.lastShotTime > 0.5 and self.angle > self.target_angle - 180 and self.angle < self.target_angle + 180):
                    shootsfx.play()

                    angle = self.angle
                    bullet = gameObject(self.position["x"], self.position["y"], "bullet", -angle, 1, [speederBullet], gameTimer)
                    angle_rad = math.radians(-angle+90)
                    bullet.xvel = math.sin(angle_rad) * 1000
                    bullet.yvel = math.cos(angle_rad) * 1000
                    bullet.angle = -angle
                    gameObjects.insert(len(gameObjects)-2, bullet)
                    self.lastShotTime = time.time()

                angle_rad = math.atan2(vy, vx)
                angle_deg = math.degrees(angle_rad)

                self.target_angle = angle_deg
                rotation_speed = 3

                angle_difference = (self.target_angle - self.angle) % 360
                if angle_difference > 180:
                    angle_difference -= 360

                if abs(angle_difference) < rotation_speed:
                    self.angle = self.target_angle
                else:
                    self.angle += rotation_speed * (1 if angle_difference > 0 else -1)

                self.angle %= 360  # Ensure the angle stays within [0, 360)

                self.xvel += vx/10
                self.yvel += vy/10

                self.sprite = pygame.transform.rotate(self.original_sprite, -self.angle)
                self.rotated_rect = self.sprite.get_rect(center=self.rect.center)
                self.followingPlayer = True
            elif pdist < 100 and self.followingPlayer:
                ivx = self.position["x"]-px
                ivy = self.position["y"]-py

                angle_rad = math.atan2(vy, vx)
                angle_deg = math.degrees(angle_rad)

                self.target_angle = angle_deg
                rotation_speed = 3

                angle_difference = (self.target_angle - self.angle) % 360
                if angle_difference > 180:
                    angle_difference += 360

                if abs(angle_difference) < rotation_speed:
                    self.angle = self.target_angle
                else:
                    self.angle += rotation_speed * (1 if angle_difference > 0 else -1)

                self.angle %= 360  # Ensure the angle stays within [0, 360)

                self.xvel += ivx
                self.yvel += ivy

                self.sprite = pygame.transform.rotate(self.original_sprite, -self.angle)
                self.rotated_rect = self.sprite.get_rect(center=self.rect.center)
                self.followingPlayer = True

            allies = [obj for obj in gameObjects if obj.isEnemy and obj.rendered]
            for ally in allies:
                ax = ally.position["x"]
                ay = ally.position["y"]

                avx = self.position["x"] - ax
                avy = self.position["y"] - ay

                dist = abs(math.sqrt(avx**2 + avy**2))

                if dist < pdist and dist < 100:
                    self.xvel += avx
                    self.yvel += avy
        else:
            self.gotoHome = True
            self.followingPlayer = False
            self.xvel = hvx
            self.yvel = hvy

        """Enemy HP Bar"""

        # Draw health bar
        high_hp = (43, 255, 0)
        med_hp = (252, 152, 3)
        low_hp = (255,0,0)

        hpPercent = self.hp/self.maxhp

        if hpPercent < 1:
            color = (0,0,0)

            if hpPercent < 1:
                color = (med_hp[0] + (high_hp[0] - med_hp[0])*hpPercent, med_hp[1] + (high_hp[1] - med_hp[1])*hpPercent, med_hp[2] + (high_hp[2] - med_hp[2])*hpPercent)
            if hpPercent <= 0.5:
                color = (low_hp[0] + (med_hp[0] - low_hp[0])*hpPercent+0.5, low_hp[1] + (med_hp[1] - low_hp[1])*hpPercent+0.5, low_hp[2] + (med_hp[2] - low_hp[2])*hpPercent+0.5)
            
            renderedPosition = [self.position["x"]+gameCamera.position["x"], self.position["y"]+gameCamera.position["y"]]
            pygame.draw.rect(win, (155, 155, 155), (renderedPosition[0]-40, renderedPosition[1]-50, 80, 20), 0, 10)
            pygame.draw.rect(win, color, (renderedPosition[0]-35, renderedPosition[1]-45, 70*hpPercent, 10), 0, 10)

        # Enemy Death
        if self.hp <= 0 and self in gameObjects:
            # Add 1 to score (temporary)
            global inventory
            inventory.add_item("Credit", 1)
            inventory.add_item("Metal", random.randint(3,7))
            inventory.add_item("Fuel Cell", random.randint(0,2))

            for x in range(5):
                particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (random.randint(-10, 10),random.randint(-10, 10)),100,particleShape.explosion, 0.02)
            #particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (0,0), 100, particleShape.shockwave, 0)
            
            global planetEnemies
            global enemyPlanets

            explodesfx.play()

            gameCamera.runCameraAction(cameraAction.cameraShake)
            planet = enemyPlanets[self]
            planetEnemies[planet].remove(self)
            del enemyPlanets[self]
            gameObjects.pop(gameObjects.index(self)) # Remove enemy

def brute(self):
    global paused
    if not paused and self.rendered:

        """Enemy AI"""
        winx, winy = win.get_size()

        self.position["y"] += self.yvel * self.timer.deltaTime
        self.position["x"] += self.xvel * self.timer.deltaTime

        self.xvel *= 0.94
        self.yvel *= 0.94

        hx = self.home["x"]
        hy= self.home["y"]

        hvx = hx-self.position["x"]
        hvy = hy-self.position["y"]

        hdist = math.sqrt(hvx**2 + hvy**2)

        px = gameObjects[len(gameObjects)-1].position["x"]
        py = gameObjects[len(gameObjects)-1].position["y"]
        
        vx = px-self.position["x"]
        vy = py-self.position["y"]

        pdist = math.sqrt(vx**2 + vy**2)

        if hdist < 10 and self.gotoHome:
            self.gotoHome = False
        
        if pdist > 350 and pdist < 680 and not self.followingPlayer:
            angle_rad = math.atan2(vy, vx)
            angle_deg = math.degrees(angle_rad)

            self.angle = angle_deg
        if hdist < 1750 and not self.gotoHome:

            if pdist < 350 and pdist > 100 or self.followingPlayer and pdist > 100:

                # Allow enemy to shoot at player
                if (time.time() - self.lastShotTime > 2 and self.angle > self.target_angle - 180 and self.angle < self.target_angle + 180):
                    shootsfx.play()

                    angle = self.angle
                    bullet = gameObject(self.position["x"], self.position["y"], "bullet", -angle, 1, [bruteBullet], gameTimer)
                    angle_rad = math.radians(-angle+90)
                    bullet.xvel = math.sin(angle_rad) * 500
                    bullet.yvel = math.cos(angle_rad) * 500
                    bullet.angle = -angle
                    gameObjects.insert(len(gameObjects)-2, bullet)
                    self.lastShotTime = time.time()

                angle_rad = math.atan2(vy, vx)
                angle_deg = math.degrees(angle_rad)

                self.target_angle = angle_deg
                rotation_speed = 0.75

                angle_difference = (self.target_angle - self.angle) % 360
                if angle_difference > 180:
                    angle_difference -= 360

                if abs(angle_difference) < rotation_speed:
                    self.angle = self.target_angle
                else:
                    self.angle += rotation_speed * (1 if angle_difference > 0 else -1)

                self.angle %= 360  # Ensure the angle stays within [0, 360)

                self.xvel += vx/50
                self.yvel += vy/50

                self.sprite = pygame.transform.rotate(self.original_sprite, -self.angle)
                self.rotated_rect = self.sprite.get_rect(center=self.rect.center)
                self.followingPlayer = True
            elif pdist < 100 and self.followingPlayer:
                ivx = self.position["x"]-px
                ivy = self.position["y"]-py

                angle_rad = math.atan2(vy, vx)
                angle_deg = math.degrees(angle_rad)

                self.target_angle = angle_deg
                rotation_speed = 3

                angle_difference = (self.target_angle - self.angle) % 360
                if angle_difference > 180:
                    angle_difference += 360

                if abs(angle_difference) < rotation_speed:
                    self.angle = self.target_angle
                else:
                    self.angle += rotation_speed * (1 if angle_difference > 0 else -1)

                self.angle %= 360  # Ensure the angle stays within [0, 360)

                self.xvel += ivx/5
                self.yvel += ivy/5

                self.sprite = pygame.transform.rotate(self.original_sprite, -self.angle)
                self.rotated_rect = self.sprite.get_rect(center=self.rect.center)
                self.followingPlayer = True

            allies = [obj for obj in gameObjects if obj.isEnemy and obj.rendered]
            for ally in allies:
                ax = ally.position["x"]
                ay = ally.position["y"]

                avx = self.position["x"] - ax
                avy = self.position["y"] - ay

                dist = abs(math.sqrt(avx**2 + avy**2))

                if dist < pdist and dist < 100:
                    self.xvel += avx
                    self.yvel += avy
        else:
            self.gotoHome = True
            self.followingPlayer = False
            self.xvel = hvx
            self.yvel = hvy

        """Enemy HP Bar"""

        # Draw health bar
        high_hp = (43, 255, 0)
        med_hp = (252, 152, 3)
        low_hp = (255,0,0)

        hpPercent = self.hp/self.maxhp

        if hpPercent < 1:
            color = (0,0,0)

            if hpPercent < 1:
                color = (med_hp[0] + (high_hp[0] - med_hp[0])*hpPercent, med_hp[1] + (high_hp[1] - med_hp[1])*hpPercent, med_hp[2] + (high_hp[2] - med_hp[2])*hpPercent)
            if hpPercent <= 0.5:
                color = (low_hp[0] + (med_hp[0] - low_hp[0])*hpPercent+0.5, low_hp[1] + (med_hp[1] - low_hp[1])*hpPercent+0.5, low_hp[2] + (med_hp[2] - low_hp[2])*hpPercent+0.5)
            
            renderedPosition = [self.position["x"]+gameCamera.position["x"], self.position["y"]+gameCamera.position["y"]]
            pygame.draw.rect(win, (155, 155, 155), (renderedPosition[0]-40, renderedPosition[1]-50, 80, 20), 0, 10)
            pygame.draw.rect(win, color, (renderedPosition[0]-35, renderedPosition[1]-45, 70*hpPercent, 10), 0, 10)

        # Enemy Death
        if self.hp <= 0 and self in gameObjects:
            # Add 1 to score (temporary)
            global inventory
            inventory.add_item("Credit", 1)
            inventory.add_item("Metal", random.randint(6,14))
            inventory.add_item("Fuel Cell", random.randint(0,3))

            for x in range(5):
                particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (random.randint(-10, 10),random.randint(-10, 10)),100,particleShape.explosion, 0.02)
            #particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (0,0), 100, particleShape.shockwave, 0)
            
            explodesfx.play()

            gameCamera.runCameraAction(cameraAction.cameraShake)
            planet = enemyPlanets[self]
            planetEnemies[planet].remove(self)
            del enemyPlanets[self]
            gameObjects.pop(gameObjects.index(self)) # Remove enemy

def playerBullet(self):
    global paused
    if not paused:
        self.position["x"] += self.xvel * self.timer.deltaTime
        self.position["y"] += self.yvel * self.timer.deltaTime

        angle = self.angle

        self.sprite = pygame.transform.rotate(self.original_sprite, angle)
        self.rotated_rect = self.sprite.get_rect(center=self.rect.center)


        # Check for collision with enemy and deal damage
        enemies = [enemy for enemy in gameObjects if enemy.isEnemy and enemy.rendered]
        for enemy in enemies:
            if self.position["x"] > enemy.position["x"]-50 and self.position["x"] < enemy.position["x"]+50:
                if self.position["y"] > enemy.position["y"]-50 and self.position["y"] < enemy.position["y"]+50:
                    if enemy in gameObjects:
                        hitsfx.play()
                        enemy.hp -= 1
                        enemy.xvel = self.xvel/3
                        enemy.yvel = self.yvel/3
                        enemy.followingPlayer = True
                        enemy.gotoHome = False
                        if self in gameObjects:
                            gameObjects.pop(gameObjects.index(self))

    # Check if object is being rendered and if not remove object
    if not self.rendered and self in gameObjects:
        gameObjects.pop(gameObjects.index(self))

def speederBullet(self):
    global paused
    if not paused:
        self.position["x"] += self.xvel * self.timer.deltaTime
        self.position["y"] += self.yvel * self.timer.deltaTime

        angle = self.angle

        self.sprite = pygame.transform.rotate(self.original_sprite, angle)
        self.rotated_rect = self.sprite.get_rect(center=self.rect.center)


        # Check for collision with enemy and deal damage
        player = gameObjects[len(gameObjects)-1]
        if self.position["x"] > player.position["x"]-50 and self.position["x"] < player.position["x"]+50:
            if self.position["y"] > player.position["y"]-50 and self.position["y"] < player.position["y"]+50:
                if player.hp > 0:
                    hitsfx.play()
                    player.hp -= 1
                    player.xvel = self.xvel / 3
                    player.yvel = self.yvel / 3
                    #gameCamera.runCameraAction(cameraAction.cameraShake)
                    if self in gameObjects:
                        gameObjects.pop(gameObjects.index(self))

    # Check if object is being rendered and if not remove object
    if not self.rendered and self in gameObjects:
        gameObjects.pop(gameObjects.index(self))

def bruteBullet(self):
    global paused
    if not paused:
        self.position["x"] += self.xvel * self.timer.deltaTime
        self.position["y"] += self.yvel * self.timer.deltaTime

        angle = self.angle

        self.sprite = pygame.transform.rotate(self.original_sprite, angle)
        self.rotated_rect = self.sprite.get_rect(center=self.rect.center)


        # Check for collision with enemy and deal damage
        player = gameObjects[len(gameObjects)-1]
        if self.position["x"] > player.position["x"]-50 and self.position["x"] < player.position["x"]+50:
            if self.position["y"] > player.position["y"]-50 and self.position["y"] < player.position["y"]+50:
                if player.hp > 0:
                    hitsfx.play()
                    player.hp -= 3
                    player.xvel = self.xvel / 3
                    player.yvel = self.yvel / 3
                    #gameCamera.runCameraAction(cameraAction.cameraShake)
                    if self in gameObjects:
                        gameObjects.pop(gameObjects.index(self))

    # Check if object is being rendered and if not remove object
    if not self.rendered and self in gameObjects:
        gameObjects.pop(gameObjects.index(self))


def freight(self):
    global paused
    if not paused:
        self.position["x"] += 100 * self.timer.deltaTime

        if self.position["x"] > 6000:
            self.position["x"] = -6000
        if self.position["x"] < -6000:
            self.position["x"] = 6000

        if self.position["y"] > 6000:
            self.position["y"] = -6000
        if self.position["y"] < -6000:
            self.position["y"] = 6000

        # Draw health bar
        high_hp = (43, 255, 0)
        med_hp = (252, 152, 3)
        low_hp = (255,0,0)

        hpPercent = self.hp/self.maxhp

        if hpPercent < 1:
            color = (0,0,0)

            if hpPercent < 1:
                color = (med_hp[0] + (high_hp[0] - med_hp[0])*hpPercent, med_hp[1] + (high_hp[1] - med_hp[1])*hpPercent, med_hp[2] + (high_hp[2] - med_hp[2])*hpPercent)
            if hpPercent <= 0.5:
                color = (low_hp[0] + (med_hp[0] - low_hp[0])*hpPercent+0.5, low_hp[1] + (med_hp[1] - low_hp[1])*hpPercent+0.5, low_hp[2] + (med_hp[2] - low_hp[2])*hpPercent+0.5)
            
            renderedPosition = [self.position["x"]+gameCamera.position["x"], self.position["y"]+gameCamera.position["y"]]
            pygame.draw.rect(win, (155, 155, 155), (renderedPosition[0]-40, renderedPosition[1]-50, 80, 20), 0, 10)
            pygame.draw.rect(win, color, (renderedPosition[0]-35, renderedPosition[1]-45, 70*hpPercent, 10), 0, 10)

        if self.hp <= 0:
            # Add drops to the player's inventory
            global inventory
            
            inventory.add_item("Metal", random.randint(5, 20))
            inventory.add_item("Credit", random.randint(3, 5))
            inventory.add_item("Fuel Cell", random.randint(4, 6))

            # Spawn Particles

            gameCamera.runCameraAction(cameraAction.cameraShake)

            for x in range(5):
                particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (random.randint(-10, 10),random.randint(-10, 10)),100,particleShape.explosion, 0.02)
            
            explodesfx.play()

            # Destroy object
            global gameObjects
            gameObjects.remove(self)

def enemyInit(self):
    self.followingPlayer = False

def orbit(self):
    self.position["x"] += 5
    self.position["y"] += 5

def gotoTitle(self):
    global ingame
    ingame = False
    global titleScreen
    titleScreen = True

def openSettings(self):
    pass

def reset(self):
    global xvel
    global yvel
    xvel = 0
    yvel = 0
    gameObjects[len(gameObjects)-1].position = {"x": 250, "y": 250}

def fullHeal(self):
    player = gameObjects[len(gameObjects)-1]
    if player.hp < player.maxhp:
        global inventory
        fuelcell = inventory.rem_item("Fuel Cell", 1)
        credit = inventory.rem_item("Credit", 5)
        if fuelcell and credit:
            player.hp += 5
            if player.hp > player.maxhp:
                player.hp = player.maxhp
        else:
            if fuelcell:
                inventory.add_item("Fuel Cell", 1)
            if credit:
                inventory.add_item("Credit", 5)

def hpUpgrade(self):
    player = gameObjects[len(gameObjects)-1]
    global inventory
    fuelcell = inventory.rem_item("Fuel Cell", 3)
    credit = inventory.rem_item("Credit", 7)
    metal = inventory.rem_item("Metal", 20)
    if fuelcell and credit and metal:
        player.maxhp += 1
    else:
        if fuelcell:
            inventory.add_item("Fuel Cell", 3)
        if credit:
            inventory.add_item("Credit", 7)
        if metal:
            inventory.add_item("Metal", 20)

def buyBullets(self):
    global inventory
    metal = inventory.rem_item("Metal", 15)
    if metal:
        global bullets
        bullets += 20

titleScreen = True

def play(self):
    titleRenderer = uiHandler()

    titleUI = [uiElement(uiForm.panel, (350, 50), (win.get_width()/2-350/2, 150), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Loading...", [leave])]

    win.fill((0,0,0))

    titleRenderer.render(titleUI)

    out.fill((255,255,255))
    output = pygame.transform.scale(win, (910,512))
    ox, oy = out.get_size()
    out.blit(pygame.transform.scale(output, (ox,oy)), (0,0))

    pygame.display.flip()


    global titleScreen
    titleScreen = False

def fadeInMusic(fadeInLen = int):
    for x in range(fadeInLen):
        pygame.mixer.music.set_volume((0.2/fadeInLen)*x)
        time.sleep(0.01)

def leave(self):
    pygame.quit()
    sys.exit()
running = True
uiOpen = False

def wormHoleScript(self):
    if player.position["x"] > self.position["x"]-50 and player.position["x"] < self.position["x"]+50:
        if player.position["y"] > self.position["y"]-50 and player.position["y"] < self.position["y"]+50:
            global tutorial
            tutorial = False
            global gameData
            gameData["hasPlayed"] = True
            json_gameData = json.dumps(gameData, indent=4)
            with open("./resources/data/gameData.json", 'w') as dataFile:
                dataFile.write(json_gameData)

def save(self):
    global playerPlanet
    global inventory
    data = ""
    with open("./resources/data/gameData.json", "r") as gameData:
        data = json.load(gameData)
    data["saves"]["save0"] = {}
    data["saves"]["save0"]["objects"] = []
    for obj in gameObjects:
        enemyShapes = ["speeder", "brute"]
        startingPlanet = obj == playerPlanet
        planets = ["planet", "planet-red","planet-orange","planet-green","planet-blue","planet-purple"]
        if not obj.shape in enemyShapes:
            if obj.shape in planets:
                data["saves"]["save0"]["objects"].append({
                    "position":obj.position,
                    "angle":obj.angle,
                    "scale":obj.scale,
                    "shape":obj.shape,
                    "xvel":obj.xvel,
                    "yvel":obj.yvel,
                    "isEnemy":obj.isEnemy,
                    "followingPlayer":obj.followingPlayer,
                    "rendered":obj.rendered,
                    "hp":obj.hp,
                    "maxhp":obj.maxhp,
                    "lastShotTime":obj.lastShotTime,
                    "target_angle":obj.target_angle,
                    "startingPlanet":startingPlanet,
                    "pattern":obj.pattern
                })
            else:
                data["saves"]["save0"]["objects"].append({
                    "position":obj.position,
                    "angle":obj.angle,
                    "scale":obj.scale,
                    "shape":obj.shape,
                    "xvel":obj.xvel,
                    "yvel":obj.yvel,
                    "isEnemy":obj.isEnemy,
                    "followingPlayer":obj.followingPlayer,
                    "rendered":obj.rendered,
                    "hp":obj.hp,
                    "maxhp":obj.maxhp,
                    "lastShotTime":obj.lastShotTime,
                    "target_angle":obj.target_angle,
                    "startingPlanet":startingPlanet,
                })
        else:
            data["saves"]["save0"]["objects"].append({
                "position":obj.position,
                "angle":obj.angle,
                "scale":obj.scale,
                "shape":obj.shape,
                "xvel":obj.xvel,
                "yvel":obj.yvel,
                "isEnemy":obj.isEnemy,
                "followingPlayer":obj.followingPlayer,
                "rendered":obj.rendered,
                "hp":obj.hp,
                "maxhp":obj.maxhp,
                "lastShotTime":obj.lastShotTime,
                "target_angle":obj.target_angle,
                "home":obj.home,
                "startingPlanet":startingPlanet
            })
    data["saves"]["save0"]["planetEnemies"] = {}
    data["saves"]["save0"]["enemyPlanets"] = {}
    for key, objs in planetEnemies.items():
        data["saves"]["save0"]["planetEnemies"][gameObjects.index(key)] = []
        if not objs == False:
            for obj in objs:
                data["saves"]["save0"]["planetEnemies"][gameObjects.index(key)].append(gameObjects.index(obj))
        else:
            data["saves"]["save0"]["planetEnemies"][gameObjects.index(key)] = False
    for key, obj in enemyPlanets.items():
        data["saves"]["save0"]["enemyPlanets"][gameObjects.index(key)] = gameObjects.index(obj)
    
    # Save resources

    data["saves"]["save0"]["inventory"] = {}

    for name, ammt in inventory.inventory.items():
        data["saves"]["save0"]["inventory"][name] = ammt

    data["saves"]["save0"]["bullets"] = bullets


    # Write save data json to file
    with open("./resources/data/gameData.json", "w") as gameData:
        json_data = json.dumps(data, indent=4)
        gameData.write(json_data)

def load(self):
    # Show loading screen
    titleRenderer = uiHandler()

    titleUI = [uiElement(uiForm.panel, (350, 50), (win.get_width()/2-350/2, 150), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Loading...", [leave])]

    win.fill((0,0,0))

    titleRenderer.render(titleUI)

    out.fill((255,255,255))
    output = pygame.transform.scale(win, (910,512))
    ox, oy = out.get_size()
    out.blit(pygame.transform.scale(output, (ox,oy)), (0,0))

    pygame.display.flip()

    # Start loading sequence
    global playerPlanet
    global gameObjects
    global enemyPlanets
    global planetEnemies
    global inventory
    global bullets
    gameObjects = []
    enemyPlanets = {}
    planetEnemies = {}
    objScripts = {
        "planet":[],
        "planet-red":[],
        "planet-orange":[],
        "planet-green":[],
        "planet-blue":[],
        "planet-purple":[],
        "mesh":[playerScript],
        "bullet":[],
        "speeder":[speeder],
        "brute":[brute],
        "freighter":[freight],
        "rect":[],
        "wormhole":[wormHoleScript]
    }
    planets = ["planet","planet-red","planet-orange","planet-green","planet-blue","planet-purple"]
    cPlanets = ["planet-red","planet-orange","planet-green","planet-blue","planet-purple"]
    data = {}
    with open("./resources/data/gameData.json", "r") as gameData:
        data = json.load(gameData)
    for obj in data["saves"]["save0"]["objects"]:
        shape = obj["shape"]
        if shape in cPlanets:
            shape = "planet"
        curObj = gameObject(obj["position"]["x"], obj["position"]["y"], shape, obj["angle"], obj["scale"], [], gameTimer)
        if shape == "planet" and obj["shape"] in cPlanets:
            curObj.shape = obj["shape"]
            curObj.pattern = obj["pattern"]
            curObj.gensprite()
        curObj.isEnemy = obj["isEnemy"]
        curObj.followingPlayer = obj["followingPlayer"]
        curObj.hp = obj["hp"]
        curObj.maxhp = obj["maxhp"]
        curObj.lastShotTime = obj["lastShotTime"]
        curObj.xvel = obj["xvel"]
        curObj.yvel = obj["yvel"]
        curObj.scripts = objScripts[obj["shape"]]
        if obj["startingPlanet"]:
            playerPlanet = curObj
        enemyShapes = ["speeder", "brute"]
        if obj["shape"] in enemyShapes:
            curObj.home = obj["home"]
            curObj.gotoHome = False
        if obj["shape"] in planets:
            curObj.openShop = False
        gameObjects.append(curObj)
    for key, item in data["saves"]["save0"]["planetEnemies"].items():
        planetEnemies[gameObjects[int(key)]] = []
        if item != False:
            for enemy in item:
                planetEnemies[gameObjects[int(key)]].append(gameObjects[int(enemy)])
        else:
            planetEnemies[gameObjects[int(key)]] = False
    for key, item in data["saves"]["save0"]["enemyPlanets"].items():
        enemyPlanets[gameObjects[int(key)]] = gameObjects[int(item)]

    for name, ammt in data["saves"]["save0"]["inventory"].items():
        inventory.set_item(name, ammt["amount"])

    bullets = data["saves"]["save0"]["bullets"]

    gameObjects = [obj for obj in gameObjects if obj.shape != "bullet"]
        

def game():
    """Game"""

    global paused
    global gameObjects
    global gameCamera
    global gameTimer
    global inventory
    global particleManager
    global enemyPlanets
    global planetEnemies
    global bullets
    global ingame

    pygame.mixer.music.fadeout(500)
    time.sleep(0.5)

    planetEnemies = {}
    enemyPlanets = {}

    globalMenuPressed = False

    shopOpen = False

    bullets = 50

    inventory = inventoryManager()
    inventory.init_item("Credit")
    inventory.init_item("Fuel Cell")
    inventory.init_item("Metal")

    gameTimer = timer()
    gameCamera = camera()
    particleManager = particleSystem(gameCamera)
    gameUiHandler = uiHandler()
    gameObjects = []
    
    global playerPlanet
    playerPlanet = gameObject(250, 250, "planet", 0, 5, [], gameTimer)
    planetEnemies[playerPlanet] = []
    gameObjects.append(playerPlanet)


    """Spawn Planets"""

    minPlanetDist = 500

    for x in range(100):
        planetPosition = [random.randint(-5000, 5000), random.randint(-5000, 5000)]
        nearestPlanet = 999999999
        for obj in gameObjects:
                dist = math.sqrt((planetPosition[0] - obj.position["x"])**2 + (planetPosition[1] - obj.position["y"])**2)
                if dist < nearestPlanet:
                    nearestPlanet = dist
        while nearestPlanet < minPlanetDist:
            nearestPlanet = 999999999
            for obj in gameObjects:
                dist = math.sqrt((planetPosition[0] - obj.position["x"])**2 + (planetPosition[1] - obj.position["y"])**2)
                if dist < nearestPlanet:
                    nearestPlanet = dist
            if nearestPlanet < minPlanetDist:
                planetPosition = [random.randint(-5000, 5000), random.randint(-5000, 5000)]
        planet = gameObject(planetPosition[0], planetPosition[1], "planet", 0, 5, [], gameTimer)
        planet.openShop = False
        planet.popup = False
        gameObjects.insert(0, planet)
        planetEnemies[planet] = []
        for i in range(3):
            enemyType = random.choices(["speeder", "brute"], [3, 1])
            enemyType = enemyType[0]
            enemyObj = False
            if enemyType == "speeder":
                enemyObj = gameObject(planetPosition[0]+math.sin((360/3)*i)*10, planetPosition[1]+math.cos((360/3)*i)*10, "speeder", 0, 1, [speeder], gameTimer)
                enemyObj.hp = 5
                enemyObj.maxhp = 5
            if enemyType == "brute":
                enemyObj = gameObject(planetPosition[0]+math.sin((360/3)*i)*10, planetPosition[1]+math.cos((360/3)*i)*10, "brute", 0, 1, [brute], gameTimer)
                enemyObj.hp = 10
                enemyObj.maxhp = 10
            #enemyObj.followingPlayer = False
            enemyObj.isEnemy = True
            enemyObj.gotoHome = True
            enemyObj.home = {"x":planetPosition[0]+math.sin((360/3)*i)*10,"y":planetPosition[1]+math.cos((360/3)*i)*10}
            planetEnemies[gameObjects[0]].append(enemyObj)
            enemyPlanets[enemyObj] = gameObjects[0]
            gameObjects.append(enemyObj)


    for i in range(50):
        freighter = gameObject(random.randint(-5000, 5000),random.randint(-5000,5000), "freighter", 0, 1, [freight], gameTimer)
        freighter.isEnemy = True
        freighter.hp = 20
        freighter.maxhp = 20
        gameObjects.append(freighter)

    player = gameObject(250, 250, "mesh", 0, 1, [playerScript], gameTimer)
    player.hp = 10
    player.maxhp = 10
    gameObjects.append(player)
    score = 0

    uiElements = []

    """Create UI"""
    uiElements.append(uiElement(uiForm.panel, (500, 500), (win.get_width()/2-250, win.get_height()/2-250), (100, 100, 100), (0,0,0), 24, (45,45,45), "", []))
    uiElements.append(uiElement(uiForm.button, (200, 35), (win.get_width()/2-100, 345), (145, 145, 145), (0,0,0), 24, (45,45,45), "Save", [save]))
    uiElements.append(uiElement(uiForm.button, (200, 35), (win.get_width()/2-100, 385), (145, 145, 145), (0,0,0), 24, (45,45,45), "Load", [load]))
    uiElements.append(uiElement(uiForm.button, (200, 35), (win.get_width()/2-100, 425), (145, 145, 145), (0,0,0), 24, (45,45,45), "Reset", [reset]))
    uiElements.append(uiElement(uiForm.button, (200, 35), (win.get_width()/2-100, 465), (145, 145, 145), (0,0,0), 24, (45,45,45), "Home", [gotoTitle]))

    uiElements[0].hidden = True
    uiElements[1].hidden = True
    uiElements[2].hidden = True
    uiElements[3].hidden = True
    uiElements[4].hidden = True

    credUi = uiElement(uiForm.panel, (170, 50), (-5, 75), (145,145,145, 64), (255,255,255), 24, (45,45,45), "0", [])
    fuelUi = uiElement(uiForm.panel, (170, 50), (-5, 150), (145,145,145, 64), (255,255,255), 24, (45,45,45), "0", [])
    metalUi = uiElement(uiForm.panel, (170, 50), (-5, 225), (145,145,145, 64), (255,255,255), 24, (45,45,45), "0", [])
    bulletsUi = uiElement(uiForm.panel, (170, 50), (-5, 300), (145,145,145, 64), (255,255,255), 24, (45,45,45), "0", [])

    uiElements.append(credUi)
    uiElements.append(fuelUi)
    uiElements.append(metalUi)
    uiElements.append(bulletsUi)

    bg = uiElement(uiForm.panel, (500, 55), (-5, -10), (145,145,145), (255,255,255), 48, (45,45,45), "", [])
    fg = uiElement(uiForm.panel, (480, 35), (5, 5), (0,255,0), (255,255,255), 48, (45,45,45), "", [])

    hpui = [bg, fg]

    metalIco = pygame.image.load("./resources/sprites/metal.png").convert_alpha()
    fuelIco = pygame.image.load("./resources/sprites/fuelcell.png").convert_alpha()
    credIco = pygame.image.load("./resources/sprites/cred.png").convert_alpha()
    bulletIco = pygame.image.load("./resources/sprites/bulletico.png").convert_alpha()

    icons = [credIco, fuelIco, metalIco, bulletIco]

    for icon in icons:
        xscale = icon.get_width()*0.25
        yscale = icon.get_height()*0.25
        icons[icons.index(icon)] = pygame.transform.scale(icon, (xscale, yscale))

    """Initialize Shop UI Elements"""

    shopbg = uiElement(uiForm.panel, (500, 500), (win.get_width()/2-250, win.get_height()/2-250), (145,145,145), (255,255,255), 48, (45,45,45), "", [])

    upgradeBtn = uiElement(uiForm.button, (480, 35), (win.get_width()/2-240, win.get_height()/2-240), (125, 125, 125), (0,0,0), 12, (45,45,45), "Heal 5 HP     Price: 5C 1F", [fullHeal])
    upgradeHpBtn = uiElement(uiForm.button, (480, 35), (win.get_width()/2-240, win.get_height()/2-200), (125, 125, 125), (0,0,0), 12, (45,45,45), "+1 MaxHP    Price: 7C 3F 20M", [hpUpgrade])
    buyBulletsBtn = uiElement(uiForm.button, (480, 35), (win.get_width()/2-240, win.get_height()/2-160), (125, 125, 125), (0,0,0), 12, (45,45,45), "+20 Bullets    Price: 15M", [buyBullets])

    shopUi = [shopbg, upgradeBtn, upgradeHpBtn, buyBulletsBtn]

    for uiElem in shopUi:
        uiElements.append(uiElem)

    uiElements.append(bg)
    uiElements.append(fg)

    keybindPopup = uiElement(uiForm.panel, (200, 200), (0,0), pygame.SRCALPHA, (255,255,255), 48, (45,45,45), "", [])

    keybindIco = pygame.image.load("./resources/sprites/key.png").convert_alpha()
    if joystick != False:
        keybindIco = pygame.image.load("./resources/sprites/controllerkey.png").convert_alpha()

    icoWidth = keybindIco.get_width() * 0.5
    icoHeight = keybindIco.get_height() * 0.5

    keybindIco = pygame.transform.scale(keybindIco, (icoWidth, icoHeight))

    keybindPopup.sprite.blit(keybindIco, (100-icoWidth, 100-icoHeight))

    keybindPopup.hidden = True

    uiElements.insert(5, keybindPopup)

    paused = False
    lastShotTime = 0
    ingame = True

    shownBtn = [btn for btn in uiElements if btn.form == uiForm.button and not btn.hidden]
    cur_hovered = 0
    openShop = False

    pygame.mixer.music.load('./resources/audio/project-omikron-bg.wav')
    pygame.mixer.music.set_volume(0)
    pygame.mixer.music.play(loops=-1)
    fadeInMusic(10)
    planetColors = ["planet-red","planet-orange","planet-green","planet-blue", "planet-purple"]

    """Main Game Loop"""
    while ingame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                ingame = False
                titleScreen = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    paused = not paused
                    planets = [obj for obj in gameObjects if obj.shape in planetColors and not obj == playerPlanet]
                    for planet in planets:
                        planet.openShop = False
                    shopOpen = False
                if keys[pygame.K_e]:
                    if not paused:
                        openShop = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                planets = [obj for obj in gameObjects if obj.shape in planetColors and not obj == playerPlanet]
                if not paused and not any(planet for planet in planets if planet.openShop) and pygame.mouse.get_pressed()[0]  and time.time() - lastShotTime > 0.3 and bullets > 0:
                    # Play sfx
                    shootsfx.play()
                    # Spawn a bullet
                    angle = gameObjects[len(gameObjects)-1].angle
                    bullet = gameObject(gameObjects[len(gameObjects)-1].position["x"], gameObjects[len(gameObjects)-1].position["y"], "bullet", -angle, 1, [playerBullet], gameTimer)
                    angle_rad = math.radians(-angle+90)
                    bullet.xvel = math.sin(angle_rad) * 1000
                    bullet.yvel = math.cos(angle_rad) * 1000
                    bullet.angle = -angle
                    gameObjects.insert(len(gameObjects)-2, bullet)
                    lastShotTime = time.time()

                    bullets -= 1
                elif bullets <= 0:
                    # Play sfx
                    noammosfx.play()
            if event.type == pygame.JOYBUTTONDOWN:
                if not paused:
                    if event.button == 0 and not any(planet for planet in planets if planet.openShop)  and time.time() - lastShotTime > 0.3 and bullets > 0:
                        # Play sfx
                        shootsfx.play()
                        # Spawn a bullet
                        angle = gameObjects[len(gameObjects)-1].angle
                        bullet = gameObject(gameObjects[len(gameObjects)-1].position["x"], gameObjects[len(gameObjects)-1].position["y"], "bullet", -angle, 1, [playerBullet], gameTimer)
                        angle_rad = math.radians(-angle+90)
                        bullet.xvel = math.sin(angle_rad) * 1000
                        bullet.yvel = math.cos(angle_rad) * 1000
                        bullet.angle = -angle
                        gameObjects.insert(len(gameObjects)-2, bullet)
                        lastShotTime = time.time()

                        bullets -= 1
                if event.button == 6:
                    paused = not paused
                    uiOpen = paused

                if event.button == 14:
                    globalMenuPressed = True

                if event.button == 3:
                    openShop = True

                # Controller Menu Navigation
                shownBtn = [btn for btn in uiElements if btn.form == uiForm.button and not btn.hidden]
                if event.button == 11:
                    try:
                        if uiElements[uiElements.index(shownBtn[cur_hovered])] in shownBtn:
                            cur_hovered -= 1
                        else:
                            cur_hovered = 0
                    except:
                        cur_hovered = 0
                    if cur_hovered < 0:
                        cur_hovered = len(shownBtn)-1

                    for btn in shownBtn:
                        if btn in uiElements:
                            uiElements[uiElements.index(btn)].hovered = False

                    try:
                        uiElements[uiElements.index(shownBtn[cur_hovered])].hovered = True
                    except:
                        pass
                if event.button == 12:
                    try:
                        if uiElements[uiElements.index(shownBtn[cur_hovered])] in shownBtn:
                            cur_hovered += 1
                        else:
                            cur_hovered = 0
                    except:
                        cur_hovered = 0
                    if cur_hovered > len(shownBtn)-1:
                        cur_hovered = 0

                    for btn in shownBtn:
                        if btn in uiElements:
                            uiElements[uiElements.index(btn)].hovered = False
                    try:
                        uiElements[uiElements.index(shownBtn[cur_hovered])].hovered = True
                    except:
                        pass
                

        if paused:
            uiElements[0].hidden = False
            uiElements[1].hidden = False
            uiElements[2].hidden = False
            uiElements[3].hidden = False
            uiElements[4].hidden = False

            #pygame.mixer.music.pause()
            pygame.mixer.music.set_volume(0.2)
        else:
            uiElements[0].hidden = True
            uiElements[1].hidden = True
            uiElements[2].hidden = True
            uiElements[3].hidden = True
            uiElements[4].hidden = True

            #pygame.mixer.music.unpause()
            pygame.mixer.music.set_volume(0.4)
        
        # Softlock Prevention
        planets = [obj for obj in gameObjects if obj.shape == "planet" and not obj == playerPlanet]
        allShopClosed = all(planet for planet in planets if planetEnemies[planet] != False)
        if bullets <= 0 and inventory.inventory["Metal"]["amount"] < 15 or bullets <= 0 and not allShopClosed:
            deathsfx.play()
            ingame = False
            titleScreen = True

        """Shop"""
        planetRadius = 150
        planets = [obj for obj in gameObjects if obj.shape in planetColors or obj.shape == "planet" and not obj == playerPlanet]
        for planet in planets:
            player = gameObjects[len(gameObjects)-1]
            pvx = player.position["x"] - planet.position["x"]
            pvy = player.position["y"] - planet.position["y"]

            dist = math.sqrt(pvx**2 + pvy**2)

            if planetEnemies[planet] == [] and planetEnemies[planet] != False:
                print(planetEnemies[planet], gameObjects.index(planet))
                color = random.choice(planetColors)
                planet.shape = color
                planet.gensprite()
                planetEnemies[planet] = False
                dingsfx.play()
                print("New Planet Cleared")
            
            keys = pygame.key.get_pressed()
            if dist < planetRadius and planetEnemies[planet] == False and not paused:
                planet.popup = True
                uiElements[uiElements.index(keybindPopup)].position["x"] = planet.position["x"] + gameCamera.position["x"] - icoWidth*0.75
                uiElements[uiElements.index(keybindPopup)].position["y"] = planet.position["y"] + gameCamera.position["y"] - icoHeight*0.75
            else:
                planet.popup = False

            if planet.openShop and dist > planetRadius or planet.openShop and openShop:
                uiOpen = False
                planet.openShop = False
                openShop = False
            if dist < planetRadius and planetEnemies[planet] == False and openShop:
                planet.openShop = True
                uiOpen = True
                openShop = False
        if any(planet for planet in planets if planet.openShop):
            for elem in shopUi:
                uiElements[uiElements.index(elem)].hidden = False
        else:
            for elem in shopUi:
                uiElements[uiElements.index(elem)].hidden = True

        if any(planet for planet in planets if planet.popup):
            uiElements[uiElements.index(keybindPopup)].hidden = False
        else:
            uiElements[uiElements.index(keybindPopup)].hidden = True
        # UI Updates

        uiElements[uiElements.index(credUi)].text = str(inventory.inventory["Credit"]["amount"])
        uiElements[uiElements.index(credUi)].relsprite()

        uiElements[uiElements.index(fuelUi)].text = str(inventory.inventory["Fuel Cell"]["amount"])
        uiElements[uiElements.index(fuelUi)].relsprite()

        uiElements[uiElements.index(metalUi)].text = str(inventory.inventory["Metal"]["amount"])
        uiElements[uiElements.index(metalUi)].relsprite()

        uiElements[uiElements.index(bulletsUi)].text = str(bullets)
        uiElements[uiElements.index(bulletsUi)].relsprite()


        # Player hp bar ui

        hpPercent = gameObjects[len(gameObjects)-1].hp / gameObjects[len(gameObjects)-1].maxhp

        high_hp = (43, 255, 0)
        med_hp = (252, 152, 3)
        low_hp = (255,0,0)

        if hpPercent <= 1:
            color = (med_hp[0] + (high_hp[0] - med_hp[0])*hpPercent, med_hp[1] + (high_hp[1] - med_hp[1])*hpPercent, med_hp[2] + (high_hp[2] - med_hp[2])*hpPercent)
        if hpPercent <= 0.5:
            color = (low_hp[0] + (med_hp[0] - low_hp[0])*hpPercent+0.5, low_hp[1] + (med_hp[1] - low_hp[1])*hpPercent+0.5, low_hp[2] + (med_hp[2] - low_hp[2])*hpPercent+0.5)

        #Foreground
        uiElements[uiElements.index(hpui[1])].scale["x"] = 480*hpPercent
        uiElements[uiElements.index(hpui[1])].color = color
        uiElements[uiElements.index(hpui[1])].relsprite()


        win.fill((0,0,0))

        gameCamera.render(gameObjects)
        particleManager.render()
        gameTimer.frame()

        for obj in gameObjects:
            obj.frame()
        for elem in uiElements:
            if not elem.hidden:
                elem.frame()

        gameUiHandler.render(uiElements)

        win.blit(icons[0], (10, 80))
        win.blit(icons[1], (10, 155))
        win.blit(icons[2], (10, 230))
        win.blit(icons[3], (10, 305))

        out.fill((255,255,255))
        output = pygame.transform.scale(win, (910,512))
        ox, oy = out.get_size()
        out.blit(pygame.transform.scale(output, (ox,oy)), (0,0))

        pygame.display.flip()

    pygame.mixer.music.fadeout(500)
    time.sleep(0.5)
def title():
    
    """Title Screen"""

    global titleScreen
    titleScreen = True

    pygame.mixer.music.load('./resources/audio/project-omikron-menu.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

    globalMenuPressed = False
    titleRenderer = uiHandler()
    titleUI = []

    mouseDown = pygame.mouse.get_pressed()[0]

    titleUI.append(uiElement(uiForm.panel, (win.get_size()[0], 50), (0, win.get_height()/2-150), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Project: Omikron", []))
    titleUI.append(uiElement(uiForm.button, (350, 50), (win.get_width()/2-350/2, win.get_height()/2-75), (115,115,115), (255,255,255), 24, (45,45,45), "Play", [play]))
    titleUI.append(uiElement(uiForm.button, (350, 50), (win.get_width()/2-350/2, win.get_height()/2), (115,115,115), (255,255,255), 24, (45,45,45), "Quit", [leave]))

    shownBtn = [btn for btn in titleUI if btn.form == uiForm.button and not btn.hidden]
    cur_hovered = 0

    win.fill((0,0,0))
    titleRenderer.render(titleUI)
    pygame.display.flip()

    fadeInMusic(10)

    while titleScreen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                titleScreen = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 14:
                    globalMenuPressed = True

                # Controller Menu Navigation
                shownBtn = [btn for btn in titleUI if btn.form == uiForm.button and not btn.hidden]
                if event.button == 11:
                    try:
                        if titleUI[titleUI.index(shownBtn[cur_hovered])] in shownBtn:
                            cur_hovered -= 1
                        else:
                            cur_hovered = 0
                    except:
                        cur_hovered = 0
                    if cur_hovered < 0:
                        cur_hovered = len(shownBtn)-1

                    for btn in shownBtn:
                        if btn in titleUI:
                            titleUI[titleUI.index(btn)].hovered = False

                    try:
                        titleUI[titleUI.index(shownBtn[cur_hovered])].hovered = True
                    except:
                        pass
                if event.button == 12:
                    try:
                        if titleUI[titleUI.index(shownBtn[cur_hovered])] in shownBtn:
                            cur_hovered += 1
                        else:
                            cur_hovered = 0
                    except:
                        cur_hovered = 0
                    if cur_hovered > len(shownBtn)-1:
                        cur_hovered = 0

                    for btn in shownBtn:
                        if btn in titleUI:
                            titleUI[titleUI.index(btn)].hovered = False
                    try:
                        titleUI[titleUI.index(shownBtn[cur_hovered])].hovered = True
                    except:
                        pass

        titleUI[0].scale["x"] = win.get_size()[0]
        titleUI[0].relsprite()

        if not mouseDown:
            titleUI[1].position["x"] = (win.get_width()/2)-(350/2)
            titleUI[1].frame()

            titleUI[2].position["x"] = (win.get_width()/2)-(350/2)
            titleUI[2].frame()

        if not pygame.mouse.get_pressed()[0]:
            mouseDown = False

        if titleScreen:
            win.fill((0,0,0))
            titleRenderer.render(titleUI)
            out.fill((255,255,255))
            output = pygame.transform.scale(win, (910,512))
            ox, oy = out.get_size()
            out.blit(pygame.transform.scale(output, (ox,oy)), (0,0))
            pygame.display.flip()

def tutorialScript():
    """Tutorial Screen"""

    pygame.mixer.fadeout(1000)
    time.sleep(1)
    pygame.mixer.music.load('./resources/audio/project-omikron-tutorial.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

    global tutorial

    tutorial = True

    global gameCamera
    global gameObjects
    global gameTimer
    global paused
    global inventory
    global particleManager
    global enemyPlanets
    global planetEnemies

    gameCamera = camera()
    gameTimer = timer()
    gameObjects = []

    openShop = False

    enemyPlanets = {}
    planetEnemies = {}

    particleManager = particleSystem(gameCamera)
    
    inventory = inventoryManager()
    inventory.init_item("Credit")
    inventory.init_item("Fuel Cell")
    inventory.init_item("Metal")

    playerPlanet = gameObject(250,250,"planet", 0, 1, [], gameTimer)
    playerPlanet.shape = "planet-green"
    playerPlanet.gensprite()
    enemyPlanet = gameObject(1500,250,"planet", 0, 1, [], gameTimer)
    enemyPlanet.openShop = False
    planetEnemies[enemyPlanet] = []
    gameObjects.insert(0,playerPlanet)
    gameObjects.insert(0,enemyPlanet)
    gameObjects.append(gameObject(250,250,"mesh", 0, 1, [playerScript], gameTimer))
    
    enemy001 = gameObject(1500,250,"speeder", 0, 1, [speeder], gameTimer)
    enemy001.isEnemy = True
    enemy001.gotoHome = True
    enemy001.home = {"x":1500, "y":250}
    enemyPlanets[enemy001] = enemyPlanet
    planetEnemies[enemyPlanet].append(enemy001)
    gameObjects.insert(len(gameObjects)-1,enemy001)

    planetColors = ["planet-red","planet-orange","planet-green","planet-blue", "planet-purple"]

    lastShotTime = 0

    paused = False

    #Initialize ui
    uiManager = uiHandler()
    uiElements = []

    uiElements.append(uiElement(uiForm.panel, (1000, 50), (0, 0), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "This is your home...", []))
    uiElements.append(uiElement(uiForm.panel, (1500, 50), (0, 0), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Neighboring planets have been taken over...", []))
    uiElements.append(uiElement(uiForm.panel, (1000, 50), (0, 0), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "You Must Save Them...", []))

    controlsIco = pygame.image.load("./resources/sprites/wasd-ico.png")
    ctrlNewWidth = controlsIco.get_width() * 0.5
    ctrlNewHeight = controlsIco.get_height() * 0.5
    controlsIco = pygame.transform.scale(controlsIco, (ctrlNewWidth, ctrlNewHeight))

    controls = uiElement(uiForm.panel, (1000, 500), (0, 0), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Move with ", [])
    controls.sprite.blit(controlsIco, (650-ctrlNewWidth/2,250-ctrlNewHeight/2))

    uiElements.append(controls)

    shootIco = pygame.image.load("./resources/sprites/lmb.png")
    shtNewWidth = shootIco.get_width() * 0.5
    shtNewHeight = shootIco.get_height() * 0.5
    shootIco = pygame.transform.scale(shootIco, (shtNewWidth, shtNewHeight))

    controls = uiElement(uiForm.panel, (1000, 500), (0, 0), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Shoot with ", [])
    controls.sprite.blit(shootIco, (650-shtNewWidth/2,250-shtNewWidth/2))

    uiElements.append(controls)

    global player
    player = gameObjects[len(gameObjects)-1]

    wormHole = gameObject(2000,250,"wormhole", 0, 1, [wormHoleScript], gameTimer)
    gameObjects.insert(0, wormHole)

    uiElements.append(controls)


    while tutorial:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tutorial = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                planets = [obj for obj in gameObjects if obj.shape in planetColors and not obj == playerPlanet]
                if not paused and not any(planet for planet in planets if planet.openShop) and pygame.mouse.get_pressed()[0]  and time.time() - lastShotTime > 0.3:
                    # Play sfx
                    shootsfx.play()
                    # Spawn a bullet
                    angle = gameObjects[len(gameObjects)-1].angle
                    bullet = gameObject(gameObjects[len(gameObjects)-1].position["x"], gameObjects[len(gameObjects)-1].position["y"], "bullet", -angle, 1, [playerBullet], gameTimer)
                    angle_rad = math.radians(-angle+90)
                    bullet.xvel = math.sin(angle_rad) * 1000
                    bullet.yvel = math.cos(angle_rad) * 1000
                    bullet.angle = -angle
                    gameObjects.insert(len(gameObjects)-1, bullet)
                    lastShotTime = time.time()
        
        win.fill((0,0,0))
        
        
        gameCamera.render(gameObjects)

        uiManager.render(uiElements)

        for obj in gameObjects:
            obj.frame()
        for elem in uiElements:
            elem.frame()

        uiElements[0].position["x"] = gameCamera.position["x"] + 250 + uiElements[0].sprite.get_rect().topleft[0] - uiElements[0].scale["x"]/2
        uiElements[0].position["y"] = gameCamera.position["y"] - 50 + uiElements[0].sprite.get_rect().topleft[1] + uiElements[0].scale["y"]/2

        uiElements[1].position["x"] = gameCamera.position["x"] + 250 + uiElements[1].sprite.get_rect().topleft[0] - uiElements[1].scale["x"]/2
        uiElements[1].position["y"] = gameCamera.position["y"] + 425 + uiElements[1].sprite.get_rect().topleft[1] + uiElements[1].scale["y"]/2

        uiElements[2].position["x"] = gameCamera.position["x"] + 250 + uiElements[2].sprite.get_rect().topleft[0] - uiElements[2].scale["x"]/2
        uiElements[2].position["y"] = gameCamera.position["y"] + 475 + uiElements[2].sprite.get_rect().topleft[1] + uiElements[2].scale["y"]/2

        uiElements[3].position["x"] = gameCamera.position["x"] - 175 + uiElements[3].sprite.get_rect().topleft[0] + uiElements[3].scale["x"]/2
        uiElements[3].position["y"] = gameCamera.position["y"] - 275 + uiElements[3].sprite.get_rect().topleft[1] + uiElements[3].scale["y"]/2

        uiElements[4].position["x"] = gameCamera.position["x"] - 175 + uiElements[4].sprite.get_rect().topleft[0] + uiElements[4].scale["x"]/2
        uiElements[4].position["y"] = gameCamera.position["y"] - 175 + uiElements[4].sprite.get_rect().topleft[1] + uiElements[4].scale["y"]/2

        pygame.time.Clock().tick(6000)
        gameTimer.frame()

        pygame.display.flip()

        planetRadius = 150
        planets = [enemyPlanet]
        for planet in planets:
            player = gameObjects[len(gameObjects)-1]
            pvx = player.position["x"] - planet.position["x"]
            pvy = player.position["y"] - planet.position["y"]

            dist = math.sqrt(pvx**2 + pvy**2)

            if planetEnemies[planet] == []:
                color = random.choice(planetColors)
                planet.shape = color
                planet.gensprite()
                planetEnemies[planet] = False
                dingsfx.play()
                print("New Planet Cleared")

            if planet.openShop and dist > planetRadius or planet.openShop and openShop:
                uiOpen = False
                planet.openShop = False
                openShop = False
            if dist < planetRadius and planetEnemies[planet] == False and openShop:
                planet.openShop = True
                uiOpen = True
                openShop = False

    titleRenderer = uiHandler()

    titleUI = [uiElement(uiForm.panel, (350, 50), (win.get_width()/2-350/2, 150), pygame.SRCALPHA, (255,255,255), 24, (45,45,45), "Loading...", [leave])]

    win.fill((0,0,0))

    titleRenderer.render(titleUI)

    out.fill((255,255,255))
    output = pygame.transform.scale(win, (910,512))
    ox, oy = out.get_size()
    out.blit(pygame.transform.scale(output, (ox,oy)), (0,0))

    pygame.display.flip()


gameData = False
with open("./resources/data/gameData.json", 'r+') as dataFile:
    gameData = json.load(dataFile)

tutorial = not gameData["hasPlayed"]
while running: 
    title()
    if tutorial:
        tutorialScript()
    game()
pygame.quit()
sys.exit()