import pygame, math, sys, time, random

score = 0
ingame = True

pygame.mixer.pre_init(22050, -16, 1, 512)  # Adjust buffer size as needed
pygame.init()
win = pygame.display.set_mode([1920, 1080], pygame.RESIZABLE)
pygame.display.toggle_fullscreen()
pygame.display.set_caption("Project: Omikron")
icon = pygame.image.load("./resources/icon.png")
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
pygame.mixer.music.load('./resources/audio/Ambient.wav')
pygame.mixer.music.set_volume(0.3)
shootsfx.set_volume(0.4)
deathsfx.set_volume(0.8)
selectsfx.set_volume(0.4)
explodesfx.set_volume(0.8)
hitsfx.set_volume(0.8)

# Play the song indefinitely
pygame.mixer.music.play(loops=-2)


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
                self.cameraOffset = [random.randint(-10,10), random.randint(-10,10)]
            self.camActionFramesLeft -= 1
        if self.camActionFramesLeft <= 0:
            self.runningCameraAction = False
        for obj in gameObjects:
            renderedPosition = [obj.rotated_rect.topleft[0]+obj.position["x"]+self.position["x"]+self.cameraOffset[0], obj.rotated_rect.topleft[1]+obj.position["y"]+self.position["y"]+self.cameraOffset[1]]
            if (renderedPosition[0] > -1000 and renderedPosition[0] < win.get_width()+1000 and renderedPosition[1] > -1000 and renderedPosition[1] < win.get_height()+1000):
                win.blit(obj.sprite, (renderedPosition[0], renderedPosition[1]))
                obj.rendered = True
            else:
                obj.rendered = False
    def runCameraAction(self, action):
        if not self.runningCameraAction:
            self.runningCameraAction = True
            self.cameraActionStart = self.position
            self.camActionType = action
            self.camActionFramesLeft = 20
            
            
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
        self.clicked = False
        if form == uiForm.button:
            presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
            pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
            text = font.render(self.text, True, self.fontcolor)
            text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
            presprite.blit(text, text_rect)
            self.sprite = presprite
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
            if mousex > self.position["x"] and mousex < self.position["x"]+self.scale["x"] and mousey > self.position["y"] and mousey < self.position["y"]+self.scale["y"]:
                font = pygame.font.Font(None, self.fontsize)
                presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.hovercolor, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
                presprite.blit(text, text_rect)
                self.sprite = presprite

                if pygame.mouse.get_pressed()[0] and not self.clicked:
                    selectsfx.play()
                    for event in self.onclick:
                        event(self)
                    self.clicked = True
                
                if not pygame.mouse.get_pressed()[0]:
                    self.clicked = False
            else:
                font = pygame.font.Font(None, self.fontsize)
                presprite = pygame.Surface((self.scale["x"],self.scale["y"]), pygame.SRCALPHA)
                pygame.draw.rect(presprite, self.color, (0,0, self.scale["x"], self.scale["y"]), 0, 10)
                text = font.render(self.text, True, self.fontcolor)
                text_rect = text.get_rect(center=(self.scale["x"]/2, self.scale["y"]/2))
                presprite.blit(text, text_rect)
                self.sprite = presprite
                self.clicked = False
    def relsprite(self):
        font = pygame.font.Font(None, self.fontsize)
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
        self.hp = 3
        self.maxhp = 3
        self.lastShotTime = 0
        self.target_angle = 0

        presprite = pygame.Surface((500, 500), pygame.SRCALPHA)
        presprite.fill(pygame.SRCALPHA)
        if shape == "circle":
            presprite = pygame.Surface((1000, 1000), pygame.SRCALPHA)
            presprite.fill(pygame.SRCALPHA)
            # Load the original image
            img = pygame.image.load('./resources/sprites/planets/planet.png')

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500-new_width/2, 500-new_width/2))
            #pygame.draw.circle(presprite, (random.randint(150,255),random.randint(150,255),random.randint(150,255)), (500, 500), 25*scale)
        elif shape == "mesh":
            # Load the original image
            img = pygame.image.load('./resources/sprites/player.png')

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*scale, 500/2-new_height/2*scale))
        elif shape == "bullet":
            # Load the original image
            img = pygame.image.load('./resources/sprites/bullet.png')

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.1)
            new_height = int(img.get_height() * 0.1)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*scale, 500/2-new_height/2*scale))
        elif shape == "enemy":
            # Load the original image
            img = pygame.image.load('./resources/sprites/enemy.png')

            # Resize the image
            #pygame.draw.rect(presprite, (0, 0, 0), (250-25*scale, 250-25*scale, 50*scale, 50*scale))
            new_width = int(img.get_width() * 0.5)
            new_height = int(img.get_height() * 0.5)
            p = pygame.transform.scale(img, (new_width, new_height))
            presprite.blit(p, (500/2-new_width/2*scale, 500/2-new_height/2*scale))
        elif shape == "rect":
            pygame.draw.rect(presprite, (0,0,255), (0,0,500,500))

        # Rotate the presprite
        self.original_sprite = presprite
        self.sprite = pygame.transform.rotate(self.original_sprite, angle)
        self.rect = self.sprite.get_rect(center=(0,0))
        self.rotated_rect = self.rect.copy()  # Create a copy of the rectangle
        self.rotated_rect.center = (0,0)     # Set the center
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
            frame1 = pygame.image.load("./resources/sprites/animated/explosion/frame0.png")
            scalex = frame1.get_width()*0.3
            scaley = frame1.get_height()*0.3
            frame1 = pygame.transform.scale(frame1, (scalex, scaley))

            frame2 = pygame.image.load("./resources/sprites/animated/explosion/frame1.png")
            scalex = frame2.get_width()*0.3
            scaley = frame2.get_height()*0.3
            frame2 = pygame.transform.scale(frame2, (scalex, scaley))

            self.frames = [frame1, frame2]

            presprite.blit(frame1, (250,250))
            #pygame.draw.circle(presprite, ((255, 123, 41)), (250,250), 7)
        if s == particleShape.shockwave:
            pygame.draw.circle(presprite, (255,0,0), (250, 250), 1, 5)
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
                pygame.draw.circle(presprite, (255,0,0), (250,250), (frame), 5)
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
            global score
            score -= 5
            deathsfx.play()
            reset(self)

        if score < 0:
            gotoTitle(self)

def enemy(self):
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
                if (time.time() - self.lastShotTime > 1 and self.angle > self.target_angle - 5 and self.angle < self.target_angle + 5):
                    shootsfx.play()

                    angle = self.angle
                    bullet = gameObject(self.position["x"], self.position["y"], "bullet", -angle, 1, [enemyBullet], gameTimer)
                    angle_rad = math.radians(-angle+90)
                    bullet.xvel = math.sin(angle_rad) * 1000
                    bullet.yvel = math.cos(angle_rad) * 1000
                    bullet.angle = -angle
                    gameObjects.insert(len(gameObjects)-2, bullet)
                    self.lastShotTime = time.time()

                angle_rad = math.atan2(vy, vx)
                angle_deg = math.degrees(angle_rad)

                self.target_angle = angle_deg
                rotation_speed = 1  # Adjust this value to control the speed of rotation

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
                rotation_speed = 1  # Adjust this value to control the speed of rotation

                angle_difference = (self.target_angle - self.angle) % 360
                if angle_difference > 180:
                    angle_difference -= 360

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
        med_hp = (255, 136, 0)
        low_hp = (255,0,0)

        hpPercent = self.hp/self.maxhp

        if hpPercent < 1:
            color = (0,0,0)

            if hpPercent < 1:
                color = high_hp
            if hpPercent <= 0.66:
                color = med_hp
            if hpPercent <= 0.33:
                color = low_hp
            
            renderedPosition = [self.position["x"]+gameCamera.position["x"], self.position["y"]+gameCamera.position["y"]]
            pygame.draw.rect(win, (155, 155, 155), (renderedPosition[0]-40, renderedPosition[1]-50, 80, 20), 0, 10)
            pygame.draw.rect(win, color, (renderedPosition[0]-35, renderedPosition[1]-45, 70*hpPercent, 10), 0, 10)

        # Check if hp = 0 and remove object
        if self.hp <= 0 and self in gameObjects:
            # Add 1 to score (temporary)
            global score
            score += 1

            for x in range(10):
                particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (random.randint(-10, 10),random.randint(-10, 10)),100,particleShape.explosion, 0.02)
            #particleManager.spawnParticle((self.rotated_rect.topleft[0]+self.position["x"], self.rotated_rect.topleft[1]+self.position["y"]), (0,0), 100, particleShape.shockwave, 0)
            
            explodesfx.play()

            gameCamera.runCameraAction(cameraAction.cameraShake)

            # Add a 33% chance for killing enemy to heal player
            if random.randint(1,3) == 1 and gameObjects[len(gameObjects)-1].hp < gameObjects[len(gameObjects)-1].maxhp:
                gameObjects[len(gameObjects)-1].hp += 1
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

def enemyBullet(self):
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


titleScreen = True

def play(self):
    titleRenderer = uiHandler()

    titleUI = [uiElement(uiForm.panel, (350, 50), (win.get_width()/2-350/2, 150), pygame.SRCALPHA, (255,255,255), 48, (45,45,45), "Loading...", [leave])]

    win.fill((0,0,0))

    titleRenderer.render(titleUI)

    pygame.display.flip()


    global titleScreen
    titleScreen = False



def leave(self):
    pygame.quit()
    sys.exit()
running = True
while running: 

    titleRenderer = uiHandler()
    titleUI = []

    titleUI.append(uiElement(uiForm.panel, (win.get_size()[0], 50), (0, win.get_height()/2-150), pygame.SRCALPHA, (255,255,255), 48, (45,45,45), "Project: Omikron", []))
    titleUI.append(uiElement(uiForm.button, (350, 50), (win.get_width()/2-350/2, win.get_height()/2-75), (115,115,115), (255,255,255), 48, (45,45,45), "Play", [play]))
    titleUI.append(uiElement(uiForm.button, (350, 50), (win.get_width()/2-350/2, win.get_height()/2), (115,115,115), (255,255,255), 48, (45,45,45), "Quit", [leave]))

    while titleScreen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                titleScreen = False
                pygame.quit()
                sys.exit()

        titleUI[0].scale["x"] = win.get_size()[0]
        titleUI[0].relsprite()

        titleUI[1].position["x"] = (win.get_width()/2)-(350/2)
        titleUI[1].frame()

        titleUI[2].position["x"] = (win.get_width()/2)-(350/2)
        titleUI[2].frame()

        if titleScreen:
            win.fill((0,0,0))
            titleRenderer.render(titleUI)
            pygame.display.flip()


    gameTimer = timer()
    gameCamera = camera()
    particleManager = particleSystem(gameCamera)
    gameUiHandler = uiHandler()
    gameObjects = []

    gameObjects.append(gameObject(250, 250, "circle", 0, 5, [], gameTimer))


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
        gameObjects.insert(0, gameObject(planetPosition[0], planetPosition[1], "circle", 0, 5, [], gameTimer))
        for i in range(3):
            enemyObj = gameObject(planetPosition[0]+math.sin((360/3)*i)*10, planetPosition[1]+math.cos((360/3)*i)*10, "enemy", 0, 1, [enemy], gameTimer)
            #enemyObj.followingPlayer = False
            enemyObj.isEnemy = True
            enemyObj.gotoHome = True
            enemyObj.home = {"x":planetPosition[0]+math.sin((360/3)*i)*10,"y":planetPosition[1]+math.cos((360/3)*i)*10}
            gameObjects.append(enemyObj)

    player = gameObject(250, 250, "mesh", 0, 1, [playerScript], gameTimer)
    player.hp = 10
    player.maxhp = 10
    gameObjects.append(player)
    score = 0

    uiElements = []

    """Create UI"""
    uiElements.append(uiElement(uiForm.panel, (75, 1000), (0, -5), (100, 100, 100), (0,0,0), 24, (45,45,45), "", []))
    uiElements.append(uiElement(uiForm.button, (100, 35), (5, 45), (145, 145, 145), (0,0,0), 24, (45,45,45), "Null", []))
    uiElements.append(uiElement(uiForm.button, (100, 35), (5, 85), (145, 145, 145), (0,0,0), 24, (45,45,45), "Reset", [reset]))
    uiElements.append(uiElement(uiForm.button, (100, 35), (5, 125), (145, 145, 145), (0,0,0), 24, (45,45,45), "Settings", [openSettings]))
    uiElements.append(uiElement(uiForm.button, (100, 35), (5, 165), (145, 145, 145), (0,0,0), 24, (45,45,45), "Home", [gotoTitle]))

    uiElements[0].hidden = True
    uiElements[1].hidden = True
    uiElements[2].hidden = True
    uiElements[3].hidden = True
    uiElements[4].hidden = True

    uiElements.append(uiElement(uiForm.panel, (75, 50), (0, 0), pygame.SRCALPHA, (255,255,255), 48, (45,45,45), "0", []))
    uiElements.append(uiElement(uiForm.panel, (500, 55), (win.get_width()/2, -10), (145,145,145), (255,255,255), 48, (45,45,45), "", []))
    uiElements.append(uiElement(uiForm.panel, (480, 35), (win.get_width()/2, 5), (0,255,0), (255,255,255), 48, (45,45,45), "", []))

    paused = False
    lastShotTime = 0
    ingame = True
    while ingame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                ingame = False
                titleScreen = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not paused and pygame.mouse.get_pressed()[0]  and time.time() - lastShotTime > 0.6:
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
            if event.type == pygame.JOYBUTTONDOWN:
                if not paused:
                    if joystick.get_button(0) and time.time() - lastShotTime > 0.6:
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
                if joystick.get_button(6):
                    paused = not paused

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

        uiElements[5].text = str(score)
        uiElements[5].relsprite()


        # Player hp bar ui

        hpPercent = gameObjects[len(gameObjects)-1].hp / gameObjects[len(gameObjects)-1].maxhp

        uiElements[6].position["x"] = (win.get_size()[0]/2)-uiElements[6].scale["x"]/2
        uiElements[6].relsprite()

        uiElements[7].position["x"] = (win.get_size()[0]/2)-uiElements[6].scale["x"]/2+10
        uiElements[7].scale["x"] = 480*hpPercent
        uiElements[7].relsprite()

        #inCombat = any(obj for obj in gameObjects if obj.followingPlayer == True)

        win.fill((0,0,0))

        gameCamera.render(gameObjects)
        particleManager.render()

        pygame.time.Clock().tick(6000)
        gameTimer.frame()

        for obj in gameObjects:
            obj.frame()
        for elem in uiElements:
            elem.frame()

        gameUiHandler.render(uiElements)

        pygame.display.flip()

pygame.quit()
sys.exit()