# Lethal Company Mod Installer

### A super jank quick script to grab modfiles and replace/install them

## Installation:

### Automatic Install
Just run the `installScript/dist/Installer.exe`
<br><br>
### _Manual Install using Python_


1. Install Dependencies:
```
pip install customtkinter==5.2.2
pip install Pillow==10.2.0
pip install pygame==2.5.2
pip install vdf==3.4
```
3. Run `py installScript/main.py`

### _Manual Install_<br>

1. Delete `BepInEx`, `doorstop_config.ini` and `winhttp.dll` folders/files in the game folder.
2. Move all the files from LethalCompany folder to the Game Folder

## To-Do:

-   Download mods from source instead to reduce file size for upload
-   Automatically analyse differences in file structure to optimise updates
-   Potentially skip all the analysis and just keep map files as the rest are tiny filesizes
-   Bypass AV
