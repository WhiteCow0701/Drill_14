from pico2d import *
import game_world
import game_framework
from boy import Boy
from birds import BirdFlock
from grass import Grass

boy = None
bird_flock = None


def handle_events():


    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)


def init():
    global bird_flock, boy

    boy = Boy()
    game_world.add_oject(boy)

    bird_flock = BirdFlock()
    game_world.add_oject(bird_flock)

    grass = Grass()
    game_world.add_oject(grass, 0)


def pause():
    boy.pause()


def resume():
    pass


def finish():
    global bird_flock, boy
    game_world.clear()
    boy = None
    bird_flock = None


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()







