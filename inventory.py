# coding: utf-8
import pygame
import pygame.camera
import os.path
import time
from pygame.locals import *

DEVICE = '/dev/video0'
SIZE = (640, 480)
FILENAME = 'inventory.csv'


# Function defined to open csv file the proper way.
def open_inventory_file():
    if os.path.isfile(FILENAME):
        inventory_file = open('inventory.csv', 'a')
    else:
        inventory_file = open('inventory.csv', 'w+')
        inventory_file.write('Nombre, Función, Regularidad, Proyecto,\
                             Ubicación')
    return inventory_file


# Questionary made for filling inventory file.
def fill_inventory(inventory_file):
    while True:
        try:
            name = input('Agregue el nombre del objeto: \n')
            function = input('\nAgregue la función del objeto:\n')
            use = input('\nAgregue la regularidad de uso del objeto:\n')
            project = input('\nAgregue el proyecto del objeto: \n')
            location = input('\nAgregue la ubicación del objeto: \n')
            inventory_file.write('\n'+name+','+function+','+use+','+project+','
                                 + location)
            break
        except TypeError:
            print('\nEl tipo de dato ingresado no es válido. \n')
    return name


# Function for taking photo.
def take_photo(name):
    save_name = 'img/'+name+'.png'
    pygame.init()
    pygame.camera.init()
    cam = pygame.camera.Camera(DEVICE, SIZE)
    cam.start()
    image = cam.get_image()
    if os.path.isfile(save_name):
        pygame.image.save(image, 'img/'+name+str(int(time.time()))+'.png')
    else:
        pygame.image.save(image, save_name)
    cam.stop()
    pygame.quit()


# Presents live stream from webcam.
def camstream():
    pygame.init()
    pygame.camera.init()
    display = pygame.display.set_mode(SIZE, 0)
    camera = pygame.camera.Camera(DEVICE, SIZE)
    camera.start()
    screen = pygame.surface.Surface(SIZE, 0, display)
    capture = True
    while capture:
        screen = camera.get_image(screen)
        display.blit(screen, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_q:
                pygame.quit()
                capture = False
            elif event.type == KEYDOWN and event.key == K_s:
                pygame.image.save(screen, 'capture.png')
    camera.stop()
    pygame.quit()
    return


if __name__ == '__main__':
    while True:
        # To avoid wrong data type entered.
        try:
            stop = int(input('Inventariar\t[0]\nSalir\t\t[1]\n'))
        except ValueError:
            print('\nDato ingresado incorrecto\n\n')
            continue
        if stop == 1:
            break
        # To avoid other number than 0 or 1.
        elif stop is not 0 and 1:
            print('\nDato ingresado incorrecto\n\n')
            continue
        inventory_file = open_inventory_file()
        name = fill_inventory(inventory_file)
        print('\nPresione \'KEYDOWN + q\' para tomar una fotografía. \n')
        camstream()
        take_photo(name)
