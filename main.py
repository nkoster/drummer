import pygame
from pygame import mixer
from ast import literal_eval

pygame.init()

WIDTH = 1400
HEIGHT = 800

BPM_MIN = 10
BPM_MAX = 300
BEATS_MIN = 4
BEATS_MAX = 32

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
dark_gray = (50, 50, 50)
light_gray = (210, 210, 210)
green = (0, 255, 0)
gold = (212, 175, 55)
blue = (0, 255, 255)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Drummer')

label_font = pygame.font.Font('Roboto-Bold.ttf', 32)
medium_font = pygame.font.Font('Roboto-Bold.ttf', 24)

FPS = 60
timer = pygame.time.Clock()
beats = 16
instruments = 6
boxes = []
clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
bpm = 138
playing = False
active_length = 0
active_beat = 0
beat_changed = True
active_list = [1 for _ in range(instruments)]
save_menu = False
load_menu = False
saved_beats = []
pattern_name = 'default.drum'
typing = False

file = open(pattern_name, 'r')
for line in file:
    saved_beats.append(line)

# Load Sounds
hi_hat = mixer.Sound('sounds/hi_hat.wav')
snare = mixer.Sound('sounds/snare.wav')
kick = mixer.Sound('sounds/kick.wav')
clap = mixer.Sound('sounds/clap.wav')
tom = mixer.Sound('sounds/tom.wav')
crash = mixer.Sound('sounds/crash.wav')

# This needs research...
pygame.mixer.set_num_channels(instruments * 3)


def play_notes():
    for _i in range(len(clicked)):
        if clicked[_i][active_beat] == 1 and active_list[_i] == 1:
            if _i == 0:
                hi_hat.play()
            if _i == 1:
                snare.play()
            if _i == 2:
                kick.play()
            if _i == 3:
                crash.play()
            if _i == 4:
                clap.play()
            if _i == 5:
                tom.play()


def draw_grid(clicks, beat, actives):
    pygame.draw.rect(screen, gray, [0, 0, 200, HEIGHT - 200], 5)
    pygame.draw.rect(screen, gray, [0, HEIGHT - 200, WIDTH, 200], 5)
    _boxes = []
    colors = [gray, white, gray]
    hi_hat_text = label_font.render('Hi Hat', True, colors[actives[0]])
    screen.blit(hi_hat_text, (30, 30))
    snare_text = label_font.render('Snare', True, colors[actives[1]])
    screen.blit(snare_text, (30, 130))
    kick_text = label_font.render('Kick', True, colors[actives[2]])
    screen.blit(kick_text, (30, 230))
    crash_text = label_font.render('Crash', True, colors[actives[3]])
    screen.blit(crash_text, (30, 330))
    clap_text = label_font.render('Clap', True, colors[actives[4]])
    screen.blit(clap_text, (30, 430))
    tom_text = label_font.render('Tom', True, colors[actives[5]])
    screen.blit(tom_text, (30, 530))
    for _i in range(instruments):
        pygame.draw.line(screen, gray, (0, (_i * 100) + 100), (200, (_i * 100) + 100), 3)
    for _i in range(beats):
        for j in range(instruments):
            if clicks[j][_i] == -1:
                color = gray
            else:
                if actives[j] == -1:
                    color = dark_gray
                else:
                    color = green
            _rect = pygame.draw.rect(screen, color, [
                _i * ((WIDTH - 200) // beats) + 205, (j * 100) + 5,
                ((WIDTH - 200) // beats) - 10, ((HEIGHT - 200) // instruments) - 10
            ], 0, 3)
            pygame.draw.rect(screen, gold, [
                _i * ((WIDTH - 200) // beats) + 200, (j * 100),
                (WIDTH - 200) // beats, ((HEIGHT - 200) // instruments)
            ], 5, 5)
            pygame.draw.rect(screen, black, [
                _i * ((WIDTH - 200) // beats) + 200, (j * 100),
                (WIDTH - 200) // beats, ((HEIGHT - 200) // instruments)
            ], 2, 5)
            _boxes.append((_rect, (_i, j)))
        pygame.draw.rect(screen, blue, [
            beat * ((WIDTH - 200) // beats) + 200, 0,
            ((WIDTH - 200) // beats), instruments * 100
        ], 5, 3)
    return _boxes


def draw_exit_button():
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH - 200, HEIGHT - 100, 180, 90], 0, 5)
    exit_btn_text = label_font.render('close', True, black)
    screen.blit(exit_btn_text, (WIDTH - 160, HEIGHT - 70))
    return exit_btn


def draw_save_menu(_pattern_name, _typing):
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('Enter name for current pattern:', True, white)
    screen.blit(menu_text, (400, 40))
    saving_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT * 0.75, 400, 100], 0, 5)
    saving_btn_text = label_font.render('save pattern', True, black)
    screen.blit(saving_btn_text, (WIDTH // 2 - 50, HEIGHT * 0.75 + 30))
    if typing:
        _input_box = pygame.draw.rect(screen, dark_gray, [400, 200, 600, 200], 0, 5)
    _input_box = pygame.draw.rect(screen, dark_gray, [400, 200, 600, 200], 2, 5)
    input_box_text = label_font.render(f'{_pattern_name}', True, white)
    screen.blit(input_box_text, (430, 250))
    return draw_exit_button(), saving_btn, _input_box


def draw_load_menu(_index):
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('select from disk', True, white)
    screen.blit(menu_text, (400, 40))
    loading_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 - 200, HEIGHT - 80, 200, 70], 0, 5)
    loading_btn_text = label_font.render('load', True, white)
    screen.blit(loading_btn_text, (WIDTH // 2 - 130, HEIGHT - 64))
    delete_btn = pygame.draw.rect(screen, gray, [WIDTH // 2 + 20, HEIGHT - 80, 200, 70], 0, 5)
    delete_btn_text = label_font.render('delete', True, white)
    screen.blit(delete_btn_text, (WIDTH // 2 + 70, HEIGHT - 64))
    _patterns_box = pygame.draw.rect(screen, gray, [190, 100, 1000, 600], 2, 5)
    if 0 <= _index < len(saved_beats):
        pygame.draw.rect(screen, light_gray, [190, 100 + _index * 50, 1000, 50])
    _info = []
    for pattern in range(len(saved_beats)):
        if pattern < 10:
            row_text = medium_font.render(f'{pattern + 1}', True, white)
            screen.blit(row_text, (200, 100 + pattern * 50))
            splitter = saved_beats[pattern].split('| ')
            _name = splitter[0].split(': ')[1]
            _beats = int(splitter[1].split(': ')[1])
            _bpm = int(splitter[2].split(': ')[1])
            _selected = literal_eval(splitter[3].split(': ')[1])
            _name_text = medium_font.render(_name, True, gray)
            screen.blit(_name_text, (240, 100 + pattern * 50))
            if pattern == _index:
                _info = [_name, _beats, _bpm, _selected]
    return draw_exit_button(), loading_btn, delete_btn, _patterns_box, _info


run = True
index = 100

while run:

    delta = timer.tick(FPS)

    screen.fill(black)

    boxes = draw_grid(clicked, active_beat, active_list)

    # The Play Button
    play_button = pygame.draw.rect(screen, gray, [50, HEIGHT - 150, 200, 100], 0, 5)
    play_button_text = label_font.render('Play/Pause', True, white)
    screen.blit(play_button_text, (70, HEIGHT - 130))
    if playing:
        play_button_text2 = medium_font.render('Playing', True, dark_gray)
    else:
        play_button_text2 = medium_font.render('Paused', True, dark_gray)
    screen.blit(play_button_text2, (70, HEIGHT - 100))

    # The BPM Box
    bpm_box = pygame.draw.rect(screen, gray, [300, HEIGHT - 150, 200, 100], 5, 5)
    bpm_box_text = medium_font.render('BPM', True, white)
    screen.blit(bpm_box_text, (340, HEIGHT - 130))
    bpm_box_text2 = label_font.render(f'{bpm}', True, white)
    screen.blit(bpm_box_text2, (340, HEIGHT - 100))
    bpm_plus_button = pygame.draw.rect(screen, gray, [510, HEIGHT - 150, 48, 48], 0, 5)
    bpm_plus_button_text = label_font.render('+', True, black)
    screen.blit(bpm_plus_button_text, (525, HEIGHT - 145))
    bpm_minus_button = pygame.draw.rect(screen, gray, [510, HEIGHT - 98, 48, 48], 0, 5)
    bpm_minus_button_text = label_font.render('-', True, black)
    screen.blit(bpm_minus_button_text, (525, HEIGHT - 94))

    # The Beats
    beats_box = pygame.draw.rect(screen, gray, [600, HEIGHT - 150, 200, 100], 5, 5)
    beats_box_text = medium_font.render('Beats', True, white)
    screen.blit(beats_box_text, (640, HEIGHT - 130))
    beats_box_text2 = label_font.render(f'{beats}', True, white)
    screen.blit(beats_box_text2, (640, HEIGHT - 100))
    beats_plus_button = pygame.draw.rect(screen, gray, [810, HEIGHT - 150, 48, 48], 0, 5)
    beats_plus_button_text = label_font.render('+', True, black)
    screen.blit(beats_plus_button_text, (825, HEIGHT - 145))
    beats_minus_button = pygame.draw.rect(screen, gray, [810, HEIGHT - 98, 48, 48], 0, 5)
    beats_minus_button_text = label_font.render('-', True, black)
    screen.blit(beats_minus_button_text, (825, HEIGHT - 94))

    # The Instruments ON/OFF Table
    instruments_rect = []
    for i in range(instruments):
        rect = pygame.rect.Rect((0, i * 100), (200, 100))
        instruments_rect.append(rect)

    # Save and Load Stuff
    save_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 150, 200, 48], 0, 5)
    save_button_text = label_font.render('save', True, black)
    screen.blit(save_button_text, (960, HEIGHT - 146))
    load_button = pygame.draw.rect(screen, gray, [900, HEIGHT - 98, 200, 48], 0, 5)
    load_button_text = label_font.render('load', True, black)
    screen.blit(load_button_text, (963, HEIGHT - 94))

    # Clear Pattern
    clear_button = pygame.draw.rect(screen, gray, [1140, HEIGHT - 98, 200, 48], 0, 5)
    clear_button_text = label_font.render('clear', True, black)
    screen.blit(clear_button_text, (1200, HEIGHT - 94))

    # Draw Menu
    if save_menu:
        exit_button, saving_button, input_box = draw_save_menu(pattern_name, typing)
    if load_menu:
        exit_button, loading_button, delete_button, patterns_box, info = draw_load_menu(index)

    if beat_changed:
        play_notes()
        beat_changed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu:
            for i in range(len(boxes)):
                if boxes[i][0].collidepoint(event.pos):
                    coords = boxes[i][1]
                    clicked[coords[1]][coords[0]] *= -1
        elif event.type == pygame.MOUSEBUTTONUP and not save_menu and not load_menu:
            if play_button.collidepoint(event.pos):
                if playing:
                    playing = False
                elif not playing:
                    playing = True
            elif bpm_plus_button.collidepoint(event.pos):
                if bpm < BPM_MAX:
                    bpm += 1
            elif bpm_minus_button.collidepoint(event.pos):
                if bpm > BPM_MIN:
                    bpm -= 1
            elif beats_plus_button.collidepoint(event.pos):
                if beats < BEATS_MAX:
                    beats += 1
                    for i in range(len(clicked)):
                        clicked[i].append(-1)
            elif beats_minus_button.collidepoint(event.pos):
                if beats > BEATS_MIN:
                    beats -= 1
                    for i in range(len(clicked)):
                        clicked[i].pop(-1)
            elif clear_button.collidepoint(event.pos):
                clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
            elif save_button.collidepoint(event.pos):
                save_menu = True
            elif load_button.collidepoint(event.pos):
                load_menu = True
            for i in range(len(instruments_rect)):
                if instruments_rect[i].collidepoint(event.pos):
                    active_list[i] *= -1
        elif event.type == pygame.MOUSEBUTTONUP:
            if exit_button.collidepoint(event.pos):
                typing = False
                save_menu = False
                load_menu = False
                # playing = True
            if load_menu:
                if patterns_box.collidepoint(event.pos):
                    index = (event.pos[1] - 100) // 50
                if delete_button.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        saved_beats.pop(index)
                if loading_button.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        beats = info[1]
                        bpm = info[2]
                        clicked = info[3]
                        load_menu = False
                        index = 100
                        pygame.display.set_caption('Drummer: ' + info[0])
            if save_menu:
                if input_box.collidepoint(event.pos):
                    print('aap')
                    if typing:
                        typing = False
                    elif not typing:
                        typing = True
                if saving_button.collidepoint(event.pos):
                    file = open('default.drum', 'w')
                    saved_beats.append(f'name: {pattern_name}| beats: {beats}| bpm: {bpm}| selected: {clicked}\n')
                    for i in range(len(saved_beats)):
                        file.write(str(saved_beats[i]))
                    file.close()
                    save_menu = False
                    typing = False
        if event.type == pygame.TEXTINPUT and typing:
            pattern_name += event.text
        if event.type == pygame.KEYDOWN and typing:
            if event.key == pygame.K_BACKSPACE and len(pattern_name) > 0:
                pattern_name = pattern_name[:-1]

    # 0.94444444
    # read https://toolstud.io/music/bpm.php?bpm=138&bpm_unit=4%2F4
    # beat_length = (FPS * 60 / 4 * .93703148425787106446) // bpm
    beat_length = ((FPS * 60 + delta) / 4) // bpm
    # print(dt)
    # .93 is
    # beat_length = 6.96
    # beat_length = 6.8

    if playing:
        if active_length < beat_length:
            active_length += 1
        else:
            active_length = 0
            if active_beat < beats - 1:
                active_beat += 1
                beat_changed = True
            else:
                active_beat = 0
                beat_changed = True
    pygame.display.flip()

pygame.quit()
