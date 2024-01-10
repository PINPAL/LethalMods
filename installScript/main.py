import eel
import os
import winreg
import vdf
import zipfile
import shutil
import subprocess
from urllib.request import urlopen

# To build the exe run the following command in the terminal
# python -m PyInstaller main.py -y --onefile -n LC-Mod-Installer --add-data "web;web" --icon web/favicon.ico --noconsole --version-file version.txt

# initialize eel
eel.init('web', allowed_extensions=['.js', '.html'])

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def findInstallPath():
    eel.addToConsole("Searching for Steam Install Path", False, True)
    # read the InstallPath key from the registry
    try:
        #connecting to key in registry
        theRegistry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        registryLocation = winreg.OpenKey(theRegistry,r"SOFTWARE\WOW6432Node\Valve\Steam")
        steamInstallPathArray = winreg.QueryValueEx(registryLocation,"InstallPath")
        steamInstallPath = steamInstallPathArray[0]
    except:
        eel.addToConsole("Steam Install Path not found in registry", True)
    # print the value
    eel.addToConsole("Steam is installed at: " + steamInstallPath + "\n")
    eel.updateProgressText("findingSteamPath")

    lethalCompanySteamId = "1966720"

    # Read the libraryfolders.vdf file
    eel.addToConsole("Searching for Lethal Company in Steam Libraries", False, True)
    try:
        vdfFile = vdf.parse(open(steamInstallPath + r"\steamapps\libraryfolders.vdf"))
    except:
        eel.addToConsole("Could not find libraryfolders.vdf", True)
    # loop through the dictionary of dictionaries to libraries
    for libraryKey, libraryValues in vdfFile["libraryfolders"].items():
        # print the path value of the library
        eel.addToConsole("Searching for Lethal Company in: " + libraryValues["path"])
        # loop through the apps dictionary and find the lethal company steam id
        for appKey, appValue in libraryValues["apps"].items():
            if appKey == lethalCompanySteamId:
                lethalCompanyPath = libraryValues["path"] + r"\steamapps\common\Lethal Company"
                eel.addToConsole("--> Found Lethal Company in " + libraryValues["path"])
                eel.updateProgressText("findingLethalCompany")
                break
        else:
            continue

    eel.addToConsole("Checking Installation is Valid", False, True)
    eel.addToConsole("Checking in: " + lethalCompanyPath)
    # Check if Lethal Company.exe exists
    if not (os.path.isfile(lethalCompanyPath + r"\Lethal Company.exe")):
        eel.addToConsole("Lethal Company.exe not found in \n" + lethalCompanyPath, True)
    else:
        eel.addToConsole("Lethal Company.exe found in \n" + lethalCompanyPath)
        eel.updateProgressText("checkingInstallation")
        return lethalCompanyPath

def download(url: str, filename: str):
    readBytes = 0
    chunkSize = 1024
    # Open the URL address.
    with urlopen(url) as r:
        # Tell the window the amount of bytes to be downloaded.
        totalSize = 0
        previousSize = 0
        try:
            totalSize = int(r.info()["Content-Length"])
            eel.addToConsole("Total: " + str(round(totalSize / 1024 / 1024, 2)) + "MB")
        except:
            eel.addToConsole("Could not get Content-Length", True)
            eel.addToConsole("Downloading anyway..")
            totalSize = 0
        with open(filename, "ab") as f:
            while True:
                # Read a piece of the file we are downloading.
                chunk = r.read(chunkSize)
                # If the result is `None`, that means data is not
                # downloaded yet. Just keep waiting.
                if chunk is None:
                    continue
                # If the result is an empty `bytes` instance, then
                # the file is complete.
                elif chunk == b"":
                    break
                # Write into the local file the downloaded chunk.
                f.write(chunk)
                readBytes += chunkSize
                # Check if the last update was more than 1MB ago.
                if (previousSize + 1048576) < readBytes :
                    # Tell the window how many bytes we have received.
                    eel.updateDownloadProgress(readBytes, totalSize)
                    previousSize = readBytes

# ==============================
# main program
# ==============================
@eel.expose
def pythonMain():
    eel.addToConsole("Running Python.." ) 
    if (process_exists("Lethal Company.exe")):
        eel.addToConsole("Lethal Company is running, please close the game and try again", True)
        return
    lethalCompanyPath = findInstallPath()

    eel.updateProgressText("downloadingMods", True)
    eel.addToConsole("Downloading the latest version of Lethal Company Mods", False, True)
    eel.addToConsole("Please wait, this may take a while..")
    pathToZipFile = lethalCompanyPath + r"\LethalMods.zip"
    download("https://codeload.github.com/PINPAL/LethalMods/zip/refs/heads/main", pathToZipFile)
    eel.addToConsole("LethalMods downloaded to: " + pathToZipFile)

    eel.addToConsole("Extracting LethalMods", False, True)
    eel.updateProgressText("downloadingMods")
    # extract the zip file
    try:
        with zipfile.ZipFile(pathToZipFile, 'r') as zip_ref:
            zip_ref.extractall(lethalCompanyPath + r"\LethalMods")
    except:
        eel.addToConsole("Failed to extract LethalMods", True)
    eel.updateProgressText("extractingMods")
    eel.addToConsole("Deleting old LethalMods", False, True)
    # delete BepInEx folder
    try:
        shutil.rmtree(lethalCompanyPath + r"\BepInEx")
        eel.addToConsole("BepInEx deleted")
    except:
        eel.addToConsole("BepInEx Folder not found", True)
    # delete doorstop_config.ini
    try:
        os.remove(lethalCompanyPath + r"\doorstop_config.ini")
        eel.addToConsole("doorstop_config.ini deleted")
    except:
        eel.addToConsole("doorstop_config.ini not found", True)
    # delete winhttp.dll
    try:
        os.remove(lethalCompanyPath + r"\winhttp.dll")
        eel.addToConsole("winhttp.dll deleted")
    except:
        eel.addToConsole("winhttp.dll not found", True) 

    eel.updateProgressText("removingOldMods")
    eel.addToConsole("Moving Mod Files", False, True)
    try:
        # move the new BepInEx folder
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\BepInEx", lethalCompanyPath)
        eel.addToConsole("BepInEx moved")
        # move the new doorstop_config.ini
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\doorstop_config.ini", lethalCompanyPath)
        eel.addToConsole("doorstop_config.ini moved")
        # move the new winhttp.dll
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\winhttp.dll", lethalCompanyPath)
        eel.addToConsole("winhttp.dll moved")
    except:
        eel.addToConsole("Failed to move files", True)

    eel.updateProgressText("movingNewMods")
    eel.addToConsole("Cleaning up LethalMods", False, True)
    try:
        shutil.rmtree(lethalCompanyPath + r"/LethalMods")
        eel.addToConsole("LethalMods deleted")
        os.remove(lethalCompanyPath + r"/LethalMods.zip")
        eel.addToConsole("LethalMods.zip deleted")
    except:
        eel.addToConsole("Failed to delete LethalMods", True)

    # finished
    eel.updateProgressText("cleaningUp")
    eel.updateProgressText("complete")
    eel.addToConsole("LethalMods installed successfully", False, True, True)

# run the GUI
eel.start('main.html', size=(1000, 540), Block=False ) 