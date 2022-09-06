#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import codecs
import csv
import random
from os.path import join
from statistics import mean

import yaml
from psychopy import visual, event, logging, gui, core

from misc.screen_misc import get_screen_res, get_frame_rate
from itertools import combinations_with_replacement, product

def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert:
    :return: message
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


@atexit.register
#Nie interesuje nas to, ma zosta?: zapisuje wyniki bada?, wywo?uje si? automatycznie jak co? si? zepsuje
def save_beh_results():
    with open(join('results', PART_ID + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'), 'w', encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()

def show_image(win, file_name, size, key='f7'):
    image = visual.ImageStim(win=win, image=file_name,
                             interpolate=True, size=size)
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'return', 'enter'])
    if clicked == [key]:
        logging.critical(
            'Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)
    win.flip()

def check_exit(key='f7'):
    """
    Check (during procedure) if experimentator doesn't want to terminate.
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error(
            'Experiment finished by user! {} pressed.'.format(key))

def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg,
                          height=20, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space', '1', '2', '9', '0'])
    if key == ['f7']:
        abort_with_error(
            'Experiment finished by user on info screen! F7 pressed.')
    win.flip()

def abort_with_error(err):
    logging.critical(err)
    raise Exception(err)

RESULTS = list()
RESULTS.append(['PART_ID', 'Part', 'Block_no', 'Trial_no', 'Stimulus','Stim Color', 'KeyPressed', 'Reaction time', 'Czy Zgodny Bodziec', 'Correctness'])

def main():
    trial_no=0
    global PART_ID

    info={'IDENTYFIKATOR': '', u'P\u0141EC': ['M', "K"], 'WIEK': '20'}
    dictDlg=gui.DlgFromDict(
        dictionary=info, title='Experiment title, fill by your name!')
    if not dictDlg.OK:
        abort_with_error('Info dialog terminated.')

    clock=core.Clock()
    conf=yaml.load(open('config.yaml', encoding='utf-8'))

    win=visual.Window(list(SCREEN_RES.values()), fullscr=False, monitor='testMonitor', units='pix',
                                       screen=0, color=conf['BACKGROUND_COLOR'])
    event.Mouse(visible=False, newPos=None, win=win)
    FRAME_RATE=60

    if FRAME_RATE != conf['FRAME_RATE']:
        dlg=gui.Dlg(title="Critical error")
        dlg.addText(
            'Wrong no of frames detected: {}. Experiment terminated.'.format(FRAME_RATE))
        dlg.show()
        return None

    PART_ID=info['IDENTYFIKATOR'] + info[u'P\u0141EC'] + info['WIEK']
    logging.LogFile(join('results', PART_ID + '.log'),
                    level=logging.INFO)
    logging.info('FRAME RATE: {}'.format(FRAME_RATE))
    logging.info('SCREEN RES: {}'.format(SCREEN_RES.values()))

    fix_cross = visual.TextStim(win, text='+', height=100, color=conf['FIX_CROSS_COLOR'])
    stim = visual.TextStim(win, text='', height=conf['STIM_SIZE'], color=conf['STIM_COLOR'])
    podpowiedz = visual.TextStim(win, text='1=ró\u017Cowy, 2=czerwony, 9=zielony, 0=niebieski',pos=(0.0,-300.0), color='black')

    show_image(win, join('.', 'images', 'instrukcja.png'),1000)

    trial_no += 1
    show_info(win, join('.', 'messages', 'before_training.txt'))
    for csi in range(15):
        keyPressed, rt, kolor, bodziec=run_trial(win, conf, stim, fix_cross, clock,trial_no,podpowiedz)
        if (keyPressed=="1" and kolor=='pink') or (keyPressed=="2" and kolor=='red') or (keyPressed=="9" and kolor=='green') or (keyPressed=="0" and kolor=='blue'):
            corr=1
        else:
            corr=0
        RESULTS.append([PART_ID, 'training', 'x',trial_no,stim.text,kolor, keyPressed,  rt,bodziec,'x'])
        feedb="Poprawnie" if corr==1 else "Niepoprawnie"
        feedb=visual.TextStim(win, text=feedb, height=50, color=conf['FIX_CROSS_COLOR'])
        feedb.draw()
        podpowiedz.draw()
        win.flip()
        core.wait(1)
        podpowiedz.draw()
        win.flip()
        trial_no += 1

    show_info(win, join('.', 'messages', 'before_experiment.txt'))

    for block_no in range(conf['NO_BLOCKS']):
        for _ in range(conf['Trials in block']):
            keyPressed, rt,kolor, bodziec=run_trial(win, conf, stim, fix_cross, clock,trial_no,podpowiedz)
            if (keyPressed == "1" and kolor == 'pink') or (keyPressed == "2" and kolor == 'red') or (keyPressed == "9" and kolor == 'green') or (keyPressed == "0" and kolor == 'blue'):
                corr = 1
            else:
                corr = 0
            RESULTS.append([PART_ID, 'experiment', block_no, trial_no,stim.text,kolor, keyPressed, rt, bodziec, corr])
            trial_no += 1
        if block_no==conf['NO_BLOCKS']-1:
            break
        show_image(win, join('.', 'images', 'break.jpg'), size=(SCREEN_RES['width'], SCREEN_RES['height']))

    save_beh_results()
    logging.flush()
    show_info(win, join('.', 'messages', 'end.txt'))
    win.close()
    core.quit

def run_trial(win, conf, stim, fix_cross, clock,trial_no,podpowiedz):

    dlugosc = conf['NO_BLOCKS'] * conf['Trials in block'] // 2
    zgodnosc = random.sample(range(16, 117), dlugosc)
    trening=random.sample(range(1, 16), 7)

    if trial_no in zgodnosc or trial_no in trening:
        bodziec=1
        kolor, stim.text = random.choice([("pink", "RÓ\u017BOWY"), ("red", "CZERWONY"), ("green", "ZIELONY"), ("blue", "NIEBIESKI")])
        stim.color=kolor

    else:
        bodziec = 0
        stim.text = random.choice(["RÓ\u017BOWY", "CZERWONY", "ZIELONY", "NIEBIESKI"])
        tablicaKolorów=conf['COLORS']
        if stim.text=="RÓ\u017BOWY":
            nowa = tablicaKolorów.remove("pink")
            kolor=random.choice(tablicaKolorów)
            tablicaKolorów.append("pink")
        if stim.text=="CZERWONY":
            nowa = tablicaKolorów.remove("red")
            kolor=random.choice(tablicaKolorów)
            tablicaKolorów.append("red")
        if stim.text=="ZIELONY":
            nowa = tablicaKolorów.remove("green")
            kolor=random.choice(tablicaKolorów)
            tablicaKolorów.append("green")
        if stim.text=="NIEBIESKI":
            nowa = tablicaKolorów.remove("blue")
            kolor=random.choice(tablicaKolorów)
            tablicaKolorów.append("blue")
        stim.color = kolor





    for _ in range(conf['FIX_CROSS_TIME']):
        fix_cross.draw()
        podpowiedz.draw()
        win.flip()

    event.clearEvents()
    win.callOnFlip(clock.reset)

    for _ in range(conf['STIM_TIME']):
        reaction=event.getKeys(keyList=['1', '2', '9', '0'], timeStamped=clock)
        if reaction:
            break
        stim.draw()
        podpowiedz.draw()
        win.flip()

    if not reaction:
        podpowiedz.draw()
        win.flip()
        reaction=event.waitKeys(keyList=['1', '2', '9', '0'], maxWait=conf['REACTION_TIME'], timeStamped=clock)

    if reaction:
        keyPressed, rt=reaction[0]
    else:
        keyPressed='no_key'
        rt=-1.0

    return keyPressed, rt, kolor, bodziec

if __name__ == '__main__':
    PART_ID=''
    SCREEN_RES=get_screen_res()
    main()