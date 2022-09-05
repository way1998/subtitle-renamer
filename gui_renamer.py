# subtitle_renamer.py

from faulthandler import disable
from pydoc import visiblename
import PySimpleGUI as sg
import os.path


# helper functions

# get lists of parent and child files with corresponding extensions
def get_files(directory, parent, child):
    parents = []
    children = []
    # print(parent)
    # print(child)
    for file in os.listdir(directory):
        if file.endswith("." + parent):
            parents.append(os.path.join(directory, file))
        elif file.endswith("." + child):
            children.append(os.path.join(directory, file))

    return parents, children

# match parent with child files and rename child files
def match_and_rename(parents, children, match, number):
    # print(parents)
    # print(children)
    # print(match)
    # print(number)
    for child in children:
        # get index
        i = child.find(match[1]) + len(match[1])
        index = child[i:i+int(number)]
        parent_substr = match[0] + index

        # find corresponding parent
        for parent in parents:
            if parent_substr in parent:
                i_ep = parent.rfind(".")
                i_ec = child.rfind(".")
                new_child_path = parent[:i_ep] + child[i_ec:]

                # rename child file
                os.rename(child, new_child_path)

# GUI

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Select the folder where video and subtitle files are located")
    ],
    [
        sg.In(size=(43, 1), enable_events=True, key="_FOLDER_"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(50, 18), key="_FILE_LIST_"
        )
    ],
]

# For now will only show the name of the file that was chosen
parameter_column = [
    [sg.Text("1. Select a sample video file from list on left")],
    [sg.Text("2. Keep only the substring before the episode number, ")],
    [sg.Text("    and delete everything after:")],
    [
        sg.Text(" "), 
        sg.Input("e.g. 'Season 02 Episode '", size=(50, 1), key='_PT_VIDEO_'),
        sg.Button(button_text="Ok", size=(5, 1), enable_events=True, key="_V_OK_"),
        sg.Button(button_text="Reset", size=(5, 1), enable_events=True, key="_V_RESET_", visible=False)
    ],
    [sg.Text("3. Select a sample subtitle file from list on left")],
    [sg.Text("4. Keep only the substring before the episode number, ")],
    [sg.Text("    and delete everything after:")],
    [
        sg.Text(" "), 
        sg.Input("e.g. 'S01E'", size=(50, 1), key='_PT_SUB_'),
        sg.Button(button_text="Ok", size=(5, 1), enable_events=True, key="_S_OK_"),
        sg.Button(button_text="Reset", size=(5, 1), enable_events=True, key="_S_RESET_", visible=False)
    ],
    [sg.Text("5. Select the number of digits of an episode number:")],
    [
        sg.Text(" "), 
        sg.Combo(["1", "2", "3", "4", "5"], default_value="2", size=(10, 1), enable_events=True, key="_DIGITS_LIST_")
    ],
    [sg.Text(" ")],
    [
        sg.Button(button_text="Let's Go!", size=(55, 2), enable_events=True, key="_GO_"), 
        sg.Button(size=(55, 2), enable_events=True, key="_START_OVER_", visible=False)
    ],
]


# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(parameter_column),
    ]
]

window = sg.Window("Subtitle Renamer", layout)

step = "v"

folder = ""
video_filepath = ""
sub_filepath = ""
video_pattern = ""
sub_pattern = ""
video_ext = ""
sub_ext = ""
digits = 2

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder name was filled in, make a list of files in the folder
    if event == "_FOLDER_":
        folder = values["_FOLDER_"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
        ]
        window["_FILE_LIST_"].update(fnames)

    elif event == "_FILE_LIST_":  # A file was chosen from the listbox
        filename = values["_FILE_LIST_"][0]
        if step == "v":
            try:
                window["_PT_VIDEO_"].update(filename)
            except:
                pass
        elif step == "s":
            try:
                window["_PT_SUB_"].update(filename)
            except:
                pass
        else:
            pass

    elif event == "_V_OK_":
        step = "s"
        video_filepath = os.path.join(
            values["_FOLDER_"], values["_FILE_LIST_"][0]
        )
        video_pattern = values["_PT_VIDEO_"]
        video_ext = video_filepath[video_filepath.rfind(".")+1:]
        window["_PT_VIDEO_"].update(disabled=True, text_color="BLUE")
        window["_V_OK_"].update(visible=False)
        window["_V_RESET_"].update(visible=True)
        
    elif event == "_S_OK_":
        step = "n"
        sub_filepath = os.path.join(
            values["_FOLDER_"], values["_FILE_LIST_"][0]
        )
        sub_pattern = values["_PT_SUB_"]
        sub_ext = sub_filepath[sub_filepath.rfind(".")+1:]
        window["_PT_SUB_"].update(disabled=True, text_color="BLUE")
        window["_S_OK_"].update(visible=False)
        window["_S_RESET_"].update(visible=True)

    elif event == "_V_RESET_":
        step = "v"
        window["_PT_VIDEO_"].update(disabled=False, text_color="BLACK")
        window["_V_OK_"].update(visible=True)
        window["_V_RESET_"].update(visible=False)

    elif event == "_S_RESET_":
        step = "s"
        window["_PT_SUB_"].update(disabled=False, text_color="BLACK")
        window["_S_OK_"].update(visible=True)
        window["_S_RESET_"].update(visible=False)

    elif event == "_DIGITS_LIST_":
        digits = values["_DIGITS_LIST_"][0]

    elif event == "_GO_":
        if step != "n":
            window["_GO_"].update("Inputs unconfirmed. Check and try again")
        else:
            window["_GO_"].update(visible=False)

            # rename files
            try:
                parents, children = get_files(folder, video_ext, sub_ext)
                match = [video_pattern, sub_pattern]
                match_and_rename(parents, children, match, digits)
                window["_START_OVER_"].update("Success! Continue to rename other files", visible=True)
            except:
                window["_START_OVER_"].update("Failed! Check inputs and try again", visible=True)

    elif event == "_START_OVER_":
        window["_FOLDER_"].update("")
        window["_FOLDER_"].set_focus()
        window["_FILE_LIST_"].update([])
        window["_PT_VIDEO_"].update("", disabled=False, text_color="BLACK")
        window["_PT_SUB_"].update("", disabled=False, text_color="BLACK")
        window["_V_OK_"].update(visible=True)
        window["_S_OK_"].update(visible=True)
        window["_V_RESET_"].update(visible=False)
        window["_S_RESET_"].update(visible=False)
        window["_GO_"].update(visible=True)
        window["_START_OVER_"].update(visible=False)

        step = "v"
        folder = ""
        video_filepath = ""
        sub_filepath = ""
        video_pattern = ""
        sub_pattern = ""
        video_ext = ""
        sub_ext = ""
        digits = 2

window.close()