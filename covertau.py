#!/usr/bin/python3
"""
This file is part of Covertau.

Covertau is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Covertau is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Covertau.  If not, see <https://www.gnu.org/licenses/>.
"""

import subprocess
import utils

def print_help():
    print("""
    Covertau no es un reproductor/sintonizador. Es sólo un wrapper para
    llamar a otros reproductores (diseñado para mpv), y gestionar listas de
    utils de radio. Mientras el reproductor no tenga el control
    (para salir de mpv, basta presionar 'q'), los siguientes comandos
    son válidos (es necesario teclear y hacer Enter):
    \t:help\tMuestra esta ayuda
    \t:play\tLista las utils y pregunta por una estación para escuchar.
             También puede hacerse :play [alias] para escuchar directamente.
    \t:list\tLista las utils almacenadas
    \t:add\tAgrega una nueva estación
    \t:addlist\tAgrega una lista de reproducción manual (muchos recursos)
    \t:edit\tEdita las listas de reproducción
    \t:init\tDefine la estación para reproducir al inicio
    \t:quit\tCierra la aplicación
    """)


def list_sources(config_dict):
    continuous = utils.list_resources(config_dict)
    print('Lista de estaciones: ')
    if len(continuous) == 0:
        print('\t[Vacía]')
    else:
        for i, res in enumerate(continuous):
            name = res.get('name', '[sin nombre]')
            alias = res.get('alias', '')
            if alias:
                alias = '(%s)' % alias
            prefix = ''
            src = res.get('source', [])
            if type(src) == list and len(src) > 1:
                prefix = '(L) ' # lista de reproducción
            print("\t%d) %s - %s%s" % (i, alias, prefix, name))

def play_res(config_dict, res_id):
    if res_id is None:
        list_sources(config_dict)
        res_id = input('Estación a sintonizar: ').strip()
    if not res_id:
        print('77')
        return
    res = utils.get_res_by_alias(config_dict, res_id)
    if res is None:
        try:
            idx = int(res_id)
            res = utils.get_res_by_index(config_dict, idx)
            if res is None:
                raise ValueError
        except ValueError:
            print('Estación no encontrada')
            return
    play_sources(config_dict, res)
    
def play_sources(config_dict, res):
    source = res.get('source', None)
    if source is None:
        print('Recurso %s no tiene fuentes. Abortando.' % res.get('name', res['alias']))
        return
    if type(source) != list:
        source = [source]

    params = res.get('params', '')
    n = len(source)
    for i, src in enumerate(source):
        src_name = None
        if type(src) != str:
            src_name = src.get('source_name', None)
            src = src['source_location']
        if n > 1:
            print('-'*15)
            print('Reproduciendo %d/%d %s' % (i+1,n, '' if src_name is None else '- '+src_name))

        run_player(config_dict, src, params)

def run_player(config_dict, source, local_params):
    player_binary = config_dict.get('default_player','mpv')
    params = config_dict.get('global_params', '')

    process_args= [player_binary, source]
    if params:
        process_args.append(params)
    if local_params:
        process_args.append(local_params)
    #print('process_args: {}'.format(process_args))

    subprocess.run(process_args)

def _ask_name_add_source():
    alias = input('Alias del recurso (nombre corto; vacío para cancelar): ')
    if alias == '':
        return False, None
    name = input('Nombre del recurso/estación: ')
    return alias, name

first_time_protocol = True
def add_source_single(config_dict):
    global first_time_protocol
    alias, name = _ask_name_add_source()
    if not alias:
        return
    if first_time_protocol:
        print('Recuerda! si es una dirección ejemplo.com:9999 o una IP 259.38.7.1, antepon el protocolo (probablemente sea \'http://\')')
        first_time_protocol = False
    source = input('Recurso de la estación (puede empezar con rstp:// o terminar con .m3u): ')
    new_res = {'name': name, 'source': source, 'alias':alias}
    utils.append_resource(config_dict, new_res)
    utils.save_config_file(config_dict)

def add_source_multiple(config_dict):
    print('Registrando una lista de reproducción (múltiples recursos)')
    alias, name = _ask_name_add_source()
    new_res = {'name': name, 'alias': alias}
    sources = []

    i = 0
    while True:
        source = input('Recurso #%d (puede empezar con rstp:// o terminar con .m3u; vacío para terminar): ' % i)
        if not source.strip(): 
            break
        sources.append(source)
        i+=1

    if len(sources) == 0:
        print('No se registraron recursos. Abortando.')
        return

    new_res['source'] = sources
    utils.append_resource(config_dict, new_res)
    utils.save_config_file(config_dict)

def define_on_start(config_dict, res_id):
    if res_id is None:
        list_sources(config_dict)
        on_start = config_dict.get('on_start', False)
        on_start_current = ' ['+on_start+']' if on_start else ''
        to_remove = ' [\'rm\' para quitar]' if on_start else ''
        res_id = input('Recurso a sintonizar al incio%s%s: ' % (on_start_current, to_remove)).strip()
    if not res_id:
        return
    if res_id == 'rm':
        utils.remove_on_start(config_dict)
        utils.save_config_file(config_dict)
        return

    res = utils.get_res_by_alias(config_dict, res_id)
    if res is None:
        print('No se encontró el alias. Abortando.')
        return
    alias = res.get('alias', False)
    if not alias:
        print('El recurso no tiene alias. ¡No hagas eso!. '
              '¿Te gustaría tener una base de datos sin llave primaria?')
        return

    utils.set_on_start(config_dict, alias)
    utils.save_config_file(config_dict)
    print("Recurso '%s' programado al inicio." % alias)

def parse_command(command, config_dict):
    command = command.strip()
    if len(command) == 0:
        print("':quit' o ':q' para salir")
        return True
    elif command[0] != ':':
        print('Me gusta Vim. Los comandos empiezan con \':\' :P')
        return True
    
    command_args = command.split()
    command = command_args[0]

    if command in [':quit', ':q']:
        return False
    else:
        if command in [':list', ':l']:
            list_sources(config_dict)
        elif command in [':help', ':h']:
            print_help()
        elif command in [':play', ':p']:
            res_id = None
            if len(command_args) > 1:
                res_id = command_args[1]
            play_res(config_dict, res_id)
        elif command in [':add', ':a']:
            add_source_single(config_dict)
        elif command in [':addlist', ':al']:
            add_source_multiple(config_dict)
        elif command in [':init', ':i']:
            res_id = None
            if len(command_args) > 1:
                res_id = command_args[1]
            define_on_start(config_dict, res_id) 
        elif command in [':edit', ':e']:
            print('Qué paaaja, edita tú mismo el archivo %s' % utils.get_config_filepath())
        else:
            print('No entendí :/')
        return True

def create_defaults():
    config_dict = {'default_player': 'mpv', 'global_params': '--no-video'}
    #un recurso simple debe tener a lo menos una fuente (source)
    estacion_prueba = {'name': 'Universidad de Santiago',
                       'alias': 'usach',
                       'source': 'http://158.170.20.250:8000/usach1'}
    #un recurso múltiple tiene una lista de fuentes
    lista_prueba = {'name': 'mayor tom',
                    'alias': 'bowie',
                    'source': ['https://www.youtube.com/watch?v=iYYRH4apXDo',
    #una fuente puede también ser un diccionario (nombre y ubicación)
                              {'source_name': 'Ashes to Ashes',
                              'source_location': 'https://www.youtube.com/watch?v=CMThz7eQ6K0'
                              },
                               'https://www.youtube.com/watch?v=EHSe4N1tRQU']
                    }
    config_dict['resources'] = [estacion_prueba, lista_prueba]
    utils.save_config_file(config_dict)
    return config_dict

if __name__ == '__main__':
    config_dict = utils.read_config_file()
    if len(config_dict) == 0:
        print("Archivo %s vacío. No hay utils ni configuraciones por defecto. " % utils.get_config_filepath())
        set_defaults = input('¿Crear un archivo con configuración por defecto (y de prueba)? [S/n]: ').strip().lower()
        if set_defaults in ['n', 'no']:
            pass
        elif set_defaults in ['', 's', 'si', 'sí', 'sip', 'sep', 'seh']:
            config_dict = create_defaults()

    if config_dict.get('show_help', True):
        print_help()

    on_start = config_dict.get('on_start', False)
    if on_start:
        print('On start: \'%s\'' % on_start) 
        play_res(config_dict, on_start)
    
    run = True
    while run:
        try:
            command = input('\n\r> ')
        except KeyboardInterrupt:
            print('\nChau!')
            exit()
        run = parse_command(command, config_dict)
