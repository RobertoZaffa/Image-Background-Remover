import PySimpleGUI as sg
from rembg import remove
from PIL import Image
import threading
import time
import os

def removebackground_folder(folder):   
    global done, stopped, task_in_progress
    if task_in_progress or stopped:
        return
    task_in_progress = True 
    try:
        files = os.listdir(folder)
        print('Removing background from image files in:\n', folder, '\ncreating new files')
    except:
        files = []
    else: 
        for file in files:
            if stopped:
                print('\n  Task stopped by user')
                task_in_progress = False
                return
            source_file = os.path.join(folder, file)
            removebackground_single_file(source_file)
    progress_bar.update_bar(0, 100)
    task_in_progress = False
    print('\n===========================')


def removebackground_single_file(source_file):
    global done, stopped, task_in_progress
    if source_file[-10:-4] !='.no_bg' and source_file[-4:].lower()=='.png':
        dest_file = source_file[:-4] + '.no_bg' + '.png'
        print('\n', os.path.basename(source_file))
        if os.path.exists(dest_file):
            print('  File skipped because destination file is already present')
        else:
            print('  Removing background in progress ', end='' )
            print(' Creating', os.path.basename(dest_file), end='')
            done = False    
            thread = threading.Thread(target=remove_bg, args=(source_file, dest_file), daemon=True)
            thread.start()
            file_size = os.path.getsize(source_file)
            coeff = 300000  # average of file_size divide per time consumed for converting. 
            bar = 0
            inc_bar = 100/(file_size/coeff)
            while not done:
                time.sleep(.5)
                bar += inc_bar
                progress_bar.update_bar(bar, 100)
                if stopped:
                    print('\n  Task stopped by user')
                    task_in_progress = False
                    return
    progress_bar.update_bar(0, 100)
    task_in_progress = False



def remove_bg(source_file, dest_file):
    global done
    try:
        input = Image.open(source_file)
        output = remove(input)
        output.save(dest_file)
        done = True
        print(' . Completed')       
    except:
        print(' Skipped cause some errors ->\n')
    progress_bar.update_bar(0, 100)
    done = True

            
def progress_bar(key, iterable, *args, title='', **kwargs):
    """
    Takes your iterable and adds a progress meter onto it
    :param key: Progress Meter key
    :param iterable: your iterable
    :param args: To be shown in one line progress meter
    :param title: Title shown in meter window
    :param kwargs: Other arguments to pass to one_line_progress_meter
    :return:
    """
    sg.one_line_progress_meter(title, 0, len(iterable), key, *args, **kwargs)
    for i, val in enumerate(iterable):
        yield val
        if not sg.one_line_progress_meter(title, i+1, len(iterable), key, *args, **kwargs):
            break

def progress_bar_range(key, start, stop=None, step=1, *args, **kwargs):
    """
    Acts like the range() function but with a progress meter built-into it
    :param key: progess meter's key
    :param start: low end of the range
    :param stop: Uppder end of range
    :param step:
    :param args:
    :param kwargs:
    :return:
    """
    return progress_bar(key, range(start, stop, step), *args, **kwargs)

done = False
stopped = False
task_in_progress = False

sg.theme('DefaultNoMoreNagging')
sg.user_settings_filename(path='.')  # Set the location for the settings file

layout = [  [sg.Image(r'BackgroundRemover.PNG')],
            [sg.Text(' '*40)],

            [sg.Frame(' Single file ',[[sg.InputText(key='-file1-', size=(93, 1)), sg.FileBrowse()],
            [sg.Push(), sg.Button(' Submit Single File '), sg.Push()]])
            ], 
            [sg.Text(' '*40)],
            
            [sg.Frame(' All files in the folder ',[[sg.Input(sg.user_settings_get_entry('-folder-', ''), size=(86, 1), key='-FOLDER-'), sg.FolderBrowse(), sg.B('Store')],   

            [sg.Push(), sg.Button(' Submit Folder '),  sg.Push()]])],
            [sg.Text(' '*40)],
            
            [sg.Push(), sg.ProgressBar(1, orientation='h', size=(60, 20), key='progress'),  sg.Push()],
            [sg.Push(), sg.Button('  Stop  '), sg.Push()],
            
            [sg.Text('Activities Log:')],
            [sg.Output(size=(102,12), key='-OUTPUT-')],
            
            [sg.Push(), sg.FileBrowse(button_text = "Check files", initial_folder='-FOLDER-' ),
             sg.Button('Clear Log'), sg.Exit('Exit'),sg.Push()]]

window = sg.Window('Made by Roby Zaffa', layout)


while True:     # Event Loop
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Clear Log':
        window['-OUTPUT-'].update('')
    if event == 'Store':
        sg.user_settings_set_entry('-folder-', values['-FOLDER-'])
    progress_bar = window['progress']
    progress_bar.update_bar(0, 100)
    folder = values['-FOLDER-']
    file = values['-file1-']
    folder = folder.replace("/", "\\")
    done, stopped = False, False
    if event == ' Submit Single File ' and not task_in_progress:
        window['-OUTPUT-'].update('')
        thread = threading.Thread(target=removebackground_single_file, args=(file,), daemon=True)
        thread.start()   
    if event == ' Submit Folder ' and not task_in_progress:
        window['-OUTPUT-'].update('')
        thread = threading.Thread(target=removebackground_folder, args=(folder,), daemon=True)
        thread.start()        
    if event == '  Stop  ':
        stopped = True
            
window.close()

