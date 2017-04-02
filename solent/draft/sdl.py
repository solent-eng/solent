from solent.eng import engine_new

import sys
import sdl2.ext

MTU = 1490

SDL_RESOURCES = sdl2.ext.Resources(__file__, "_sdl_resources")

I_NEARCAST = '''
    i message h
    i field h

    message init
    message arb
        field a
        field b
'''

class CogSdl:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.sdl_window = None
        #
        sdl2.ext.init()
    def orb_turn(self, activity):
        log('turn')
    def orb_close(self):
        sdl2.ext.quit()
    #
    def on_init(self):
        sdl_window = sdl2.ext.Window("Hello World!", size=(640, 480))
        sdl_window.show()
        #
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.from_image(SDL_RESOURCES.get_path("hello.png"))
        sprite.position = (0, 0)
        #
        spriterenderer = factory.create_sprite_render_system(sdl_window)
        spriterenderer.render(sprite)
        processor = sdl2.ext.TestEventProcessor()
        processor.run(sdl_window)

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self):
        self.nearcast.init()

def main():
    engine = engine_new(
        mtu=MTU)
    try:
        orb = engine.init_orb(
            i_nearcast=I_NEARCAST)
        orb.init_cog(CogSdl)
        #
        bridge = orb.init_bridge()
        bridge.nc_init()
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

