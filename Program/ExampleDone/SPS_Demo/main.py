import os
import random
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, control:tuple, speed:int):
        Player.player_font = pygame.font.Font(pygame.font.get_default_font(), 20) # Player. pro třídní (ne instanční) proměnnou
        pygame.sprite.Sprite.__init__(self)
        
        self.up, self.left, self.down, self.right = control
       
        self.speed = speed
        self.score = 0
        
        self.redraw_image(position=(0,0))
        
        self.previous_rect = self.rect.copy()
        
    def redraw_image(self, position:tuple=None):
        if position is None:
            position = self.rect.topleft
        # obrázek s uloženým alfa kanálem - pokud nepotřebujeme využít průhlednost, pouze vynecháme .convert_alpha()
        self.image = pygame.image.load(os.path.join('img_dir', 'img_player.png')).convert_alpha()
        self.image.blit(Player.player_font.render(f"{self.score}", True, pygame.Color('brown')),
                        dest=(0,20))
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
    def update(self, keys_state):
        self.previous_rect = self.rect.copy()
        
        if keys_state[self.up]:
            self.rect.y -= self.speed
        if keys_state[self.down]:
            self.rect.y += self.speed
        if keys_state[self.left]:
            self.rect.x -= self.speed
        if keys_state[self.right]:
            self.rect.x += self.speed
    
class Coin(pygame.sprite.Sprite):
    
    def __init__(self, position:tuple, price:int, color:pygame.Color):
        Coin.coin_font = pygame.font.Font(pygame.font.get_default_font(), 15)
        pygame.sprite.Sprite.__init__(self)
        
        self.price = price
        
        self.image = pygame.Surface([self.price, self.price]) # velikost žetonu odpovídá jeho ceně
        pygame.draw.circle(self.image, color, (self.price // 2, self.price // 2), self.price // 2, 0)
        # nastaví černou na průhlednou
        self.image.set_colorkey( pygame.Color('black') ) # barvy je možné brát ze seznamu v https://github.com/pygame/pygame/blob/main/src_py/colordict.py
        
        self.rect = self.image.get_rect()
        self.rect.center = position
    
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_rectangle:pygame.Rect, color:pygame.Color):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([obstacle_rectangle.width, obstacle_rectangle.height])
        self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = obstacle_rectangle.topleft

class Game():
    EVENT_ADDOBSTACLE = 1
    def __init__(self, size):
        self.screen = pygame.display.set_mode( size )
        pygame.display.set_caption('Uteč zelené smrti')
        
        self.clock = pygame.time.Clock()

        pygame.time.set_timer(pygame.event.Event(Game.EVENT_ADDOBSTACLE), 1000) #  vlastní událost a jak často se událost vyvolá
        
        self.players = pygame.sprite.GroupSingle()
        self.players.add( Player(control=(pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d), speed=10) )
        
        self.coins = pygame.sprite.Group()
        for i in range(1, 21):
            self.coins.add( Coin((random.randint(0, self.screen.get_width()),
                                  random.randint(0, self.screen.get_height())), 2*i, pygame.Color('yellow') ))
            
        self.obstacles = pygame.sprite.Group()
        self.obstacles.add( Obstacle(pygame.Rect(100, 100, 50, 150), pygame.Color('blue')) )
        
    def run(self, fps:int=25):
        runnig = True
        while runnig:
            # zpracování událostí
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runnig = False
                if event.type == Game.EVENT_ADDOBSTACLE:
                    self.obstacles.add( Obstacle(pygame.Rect(random.randint(0, self.screen.get_width()-50),
                                                             random.randint(0, self.screen.get_width()-50),
                                                             50, 50), pygame.Color('green')) )
            self.players.update(pygame.key.get_pressed())
        
            # výpočty
            touched_coin = pygame.sprite.spritecollideany(self.players.sprite, self.coins)
            if touched_coin is not None:
                self.players.sprite.score += touched_coin.price
                self.players.sprite.redraw_image()
                touched_coin.kill()

            if pygame.sprite.spritecollideany(self.players.sprite, self.obstacles) is not None:
                self.players.sprite.rect = self.players.sprite.previous_rect.copy()
        
            # zobrazení
            self.screen.fill(pygame.Color('white'))
        
            self.obstacles.draw(self.screen)
            self.coins.draw(self.screen)
            self.players.draw(self.screen)
        
            pygame.display.update()
            self.clock.tick(fps)
    
if __name__ == "__main__":
    pygame.init()
    game = Game(size=(400, 300))
    game.run()
    pygame.quit()