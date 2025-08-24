from os import walk
import pygame

def import_folder(path, req_scale="0", as_dict=False):
    surf_dict = {}
    surf_list = []

    for _, __, img_files in walk(path):
        for img in sorted(img_files):
            full_path = path + "/" + img
            surf = pygame.image.load(full_path).convert_alpha()

            if req_scale == "32":
                surf = pygame.transform.scale(surf, (32,32))
            elif req_scale == "64":
                surf = pygame.transform.scale(surf, (64,64))
            elif req_scale == "24":
                surf = pygame.transform.scale(surf, (24,24))
            
            if as_dict:
                surf_dict[img[:img.index('.')]] = surf
            else:
                surf_list.append(surf)
                

    if as_dict:
        return surf_dict
    else:
        return surf_list
    

def import_sounds(path):
    sound_dict = {}
    for _, __, sound_files in walk(path):
        print(sound_files)
        for sound_effect in sorted(sound_files):
            full_path = path + "/" + sound_effect
            sound = pygame.mixer.Sound(full_path)
            sound_dict[sound_effect[:sound_effect.index('.')]] = sound
    
    return sound_dict