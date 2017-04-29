from solent import SolentQuitException
from solent.eng import engine_new
from solent.log import log

import sys
import sdl2
import sdl2.ext


# --------------------------------------------------------
#   :var
# --------------------------------------------------------
WHITE = sdl2.ext.Color(255, 255, 255)
BLACK = sdl2.ext.Color(0, 0, 0)

MTU = 1490

SDL_RESOURCES = sdl2.ext.Resources(__file__, "_sdl_resources")


# --------------------------------------------------------
#   :game
# --------------------------------------------------------
class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)
    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0

class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False

class EntPlayer(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai

class EntBall(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy
            #
            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)
            #
            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight
            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight

class ScoreSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(ScoreSystem, self).__init__()
        self.componenttypes = (Velocity, sdl2.ext.Sprite)
        self.score = 0
        self.pending_score = 0
    def process(self, world, componentsets):
        pass

class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(CollisionSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.ent_ball = None
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
    def _overlap(self, item):
        (velocity, sprite) = item
        if sprite == self.ent_ball.sprite:
            return False
        #
        left, top, right, bottom = sprite.area
        bleft, btop, bright, bbottom = self.ent_ball.sprite.area
        #
        return (bleft < right and bright > left and
                btop < bottom and bbottom > top)
    def process(self, world, componentsets):
        #
        # Paddle collision detection
        collitems = [comp for comp in componentsets if self._overlap(comp)]
        if collitems:
            (velocity, sprite) = collitems[0]
            #
            # reverse the ball
            self.ent_ball.velocity.vx = -self.ent_ball.velocity.vx
            #
            ballcentery = self.ent_ball.sprite.y + self.ent_ball.sprite.size[1] // 2
            halfheight = sprite.size[1] // 2
            stepsize = halfheight // 10
            degrees = 0.7
            paddlecentery = sprite.y + halfheight
            if ballcentery < paddlecentery:
                factor = (paddlecentery - ballcentery) // stepsize
                self.ent_ball.velocity.vy = -int(round(factor * degrees))
            elif ballcentery > paddlecentery:
                factor = (ballcentery - paddlecentery) // stepsize
                self.ent_ball.velocity.vy = int(round(factor * degrees))
            else:
                self.ent_ball.velocity.vy = - self.ent_ball.velocity.vy
        #
        # Ball bounce against top and bottom
        if (self.ent_ball.sprite.y <= self.miny or
            self.ent_ball.sprite.y + self.ent_ball.sprite.size[1] >= self.maxy):
            self.ent_ball.velocity.vy = - self.ent_ball.velocity.vy
        #
        # Ball touches left or right
        if (self.ent_ball.sprite.x <= self.minx or
            self.ent_ball.sprite.x + self.ent_ball.sprite.size[0] >= self.maxx):
            self.ent_ball.velocity.vx = - self.ent_ball.velocity.vx

class TrackingAIController(sdl2.ext.Applicator):
    def __init__(self, miny, maxy):
        super(TrackingAIController, self).__init__()
        self.componenttypes = PlayerData, Velocity, sdl2.ext.Sprite
        self.miny = miny
        self.maxy = maxy
        self.ent_ball = None
    def process(self, world, componentsets):
        for pdata, vel, sprite in componentsets:
            if not pdata.ai:
                continue
            #
            centery = sprite.y + sprite.size[1] // 2
            #
            # restore this when we move back to two paddles, one
            # ai controlled
            #
            ### if self.ent_ball.velocity.vx < 0:
            ###     # ent_ball is moving away from the AI
            ###     if centery < self.maxy // 2:
            ###         vel.vy = 3
            ###     elif centery > self.maxy // 2:
            ###         vel.vy = -3
            ###     else:
            ###         vel.vy = 0
            ### else:
            ###     bcentery = self.ent_ball.sprite.y + self.ent_ball.sprite.size[1] // 2
            ###     if bcentery < centery:
            ###         vel.vy = -3
            ###     elif bcentery > centery:
            ###         vel.vy = 3
            ###     else:
            ###         vel.vy = 0
            #
            # remove when we move back to two paddles
            #
            bcentery = self.ent_ball.sprite.y + self.ent_ball.sprite.size[1] // 2
            if bcentery < centery:
                vel.vy = -3
            elif bcentery > centery:
                vel.vy = 3
            else:
                vel.vy = 0


# --------------------------------------------------------
#   :bootstrap
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message init
        field title
        field width
        field height
    message arb
        field a
        field b
'''

class CogSdlWorld:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.sdl_world = None
        self.sdl_window = None
        #
        # These need to be kept as class vars, or else they'll
        # get deallocated and our app will get crashy.
        self.ent_player_a = None
        self.ent_player_b = None
        self.ent_player_c = None
        self.ent_ball = None
        #
        sdl2.ext.init()
        sdl2.SDL_Delay(10)
    def orb_turn(self, activity):
        events = sdl2.ext.get_events()
        if events:
            activity.mark(
                l=self,
                s='sdl2 event(s)')
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                raise SolentQuitException()
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    self.ent_player_b.velocity.vy = -3
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    self.ent_player_b.velocity.vy = 3
                elif event.key.keysym.sym == ord('\\'):
                    raise SolentQuitException()
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    self.ent_player_b.velocity.vy = 0
        self.sdl_world.process()
    def orb_close(self):
        sdl2.ext.quit()
    #
    def on_init(self, title, width, height):
        self.sdl_world = sdl2.ext.World()
        #
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        #
        movement = MovementSystem(0, 0, 1000, 600)
        score_system = ScoreSystem()
        collision_system = CollisionSystem(0, 0, 1000, 600)
        aicontroller = TrackingAIController(
            miny=0,
            maxy=600)
        #
        sprite_paddle_a = factory.from_color(WHITE, size=(20, 100))
        self.ent_player_a = EntPlayer(
            world=self.sdl_world,
            sprite=sprite_paddle_a,
            posx=0,
            posy=250,
            ai=True)
        sprite_paddle_b = factory.from_color(WHITE, size=(20, 100))
        self.ent_player_b = EntPlayer(
            world=self.sdl_world,
            sprite=sprite_paddle_b,
            posx=440,
            posy=250,
            ai=False)
        sprite_paddle_c = factory.from_color(WHITE, size=(20, 100))
        self.ent_player_c = EntPlayer(
            world=self.sdl_world,
            sprite=sprite_paddle_c,
            posx=970,
            posy=250,
            ai=True)
        #
        size = (width, height)
        self.sdl_window = sdl2.ext.Window(title, size=size)
        spriterenderer = SoftwareRenderer(
            window=self.sdl_window)
        #
        self.sdl_world.add_system(aicontroller)
        self.sdl_world.add_system(movement)
        self.sdl_world.add_system(score_system)
        self.sdl_world.add_system(collision_system)
        self.sdl_world.add_system(spriterenderer)
        #
        sprite_ball = factory.from_color(WHITE, size=(20, 20))
        self.ent_ball = EntBall(
            world=self.sdl_world,
            sprite=sprite_ball,
            posx=390,
            posy=290)
        self.ent_ball.velocity.vx = -3
        collision_system.ent_ball = self.ent_ball
        aicontroller.ent_ball = self.ent_ball
        #
        self.sdl_window.show()

def main():
    engine = engine_new(
        mtu=MTU)
    engine.set_default_timeout(0.0)
    try:
        orb = engine.init_orb(
            i_nearcast=I_NEARCAST)
        orb.init_cog(CogSdlWorld)
        #
        bridge = orb.init_autobridge()
        bridge.nc_init(
            title='Game',
            width=1000,
            height=600)
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

