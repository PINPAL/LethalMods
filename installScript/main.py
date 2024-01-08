import os
import sys
import winreg
import vdf
import ctypes
import logging
import zipfile
import shutil
import urllib.request

logging.basicConfig(filename="errorlog.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)

# function to print a nice header
def printHeader(headerText):
    print("\n======================================================================================")
    print(headerText)
    print("======================================================================================")

# function to print an error message
def printMessage(messageContent, isError):
    ICON_ERROR = 0x30
    ICON_INFO = 0x40
    if (isError):
        messageHeader = "Error!"
        messageContent = messageContent + "\n\n Tell Josh the script is broken!"
        icon = ICON_ERROR
    else:
        messageHeader = "Success!"
        icon = ICON_INFO
    ctypes.windll.user32.MessageBoxW(0, messageContent, messageHeader, 0x0 | icon)
    # crash the program
    if (isError):
        sys.exit()

def findInstallPath():
    printHeader("Searching for Steam Install Path")
    # read the InstallPath key from the registry
    try:
        #connecting to key in registry
        theRegistry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        registryLocation = winreg.OpenKey(theRegistry,r"SOFTWARE\WOW6432Node\Valve\Steam")
        steamInstallPathArray = winreg.QueryValueEx(registryLocation,"InstallPath")
        steamInstallPath = steamInstallPathArray[0]
    except:
        printMessage("Steam Install Path not found in registry", True)
    # print the value
    print("Steam is installed at: " + steamInstallPath + "\n")

    lethalCompanySteamId = "1966720"

    # Read the libraryfolders.vdf file
    printHeader("Searching for Lethal Company in Steam Libraries")
    try:
        vdfFile = vdf.parse(open(steamInstallPath + r"\steamapps\libraryfolders.vdf"))
    except:
        printMessage("Could not find libraryfolders.vdf", True)
    # loop through the dictionary of dictionaries to libraries
    for libraryKey, libraryValues in vdfFile["libraryfolders"].items():
        # print the path value of the library
        print("Searching for Lethal Company in: " + libraryValues["path"])
        # loop through the apps dictionary and find the lethal company steam id
        for appKey, appValue in libraryValues["apps"].items():
            if appKey == lethalCompanySteamId:
                lethalCompanyPath = libraryValues["path"] + r"\steamapps\common\Lethal Company"
                print("--> Found Lethal Company in " + libraryValues["path"])
                break
        else:
            continue

    printHeader("Checking Installation is Valid")
    print("Checking in: " + lethalCompanyPath)
    # Check if Lethal Company.exe exists
    if not (os.path.isfile(lethalCompanyPath + r"\Lethal Company.exe")):
        printMessage("Lethal Company.exe not found in \n" + lethalCompanyPath, True) 
    else:
        return lethalCompanyPath

# main program
# ==============================
try:
    lethalCompanyPath = findInstallPath()
    print("Lethal Company is installed at: " + lethalCompanyPath)

    printHeader("Downloading the latest version of LethalMods")
    pathToZipFile = lethalCompanyPath + "/LethalMods.zip"
    urllib.request.urlretrieve("https://codeload.github.com/PINPAL/LethalMods/zip/refs/heads/main", pathToZipFile)

    printHeader("Extracting LethalMods")
    # extract the zip file
    with zipfile.ZipFile(pathToZipFile, 'r') as zip_ref:
        zip_ref.extractall(lethalCompanyPath + "/LethalMods")

    printHeader("Deleting old LethalMods")
    # delete BepInEx folder
    try:
        shutil.rmtree(lethalCompanyPath + "/BepInEx")
        os.remove(lethalCompanyPath + "/doorstop_config.ini")
        os.remove(lethalCompanyPath + "/winhttp.dll")
    except:
        print("BepInEx,doorstop_config or winhttp not found")
    
    printHeader("Moving new LethalMods")
    try:
        # move the new BepInEx folder
        shutil.move(lethalCompanyPath + "/LethalMods/LethalMods-main/Lethal Company/BepInEx", lethalCompanyPath)
        # move the new doorstop_config.ini
        shutil.move(lethalCompanyPath + "/LethalMods/LethalMods-main/Lethal Company/doorstop_config.ini", lethalCompanyPath)
        # move the new winhttp.dll
        shutil.move(lethalCompanyPath + "/LethalMods/LethalMods-main/Lethal Company/winhttp.dll", lethalCompanyPath)
    except:
        printMessage("Failed to move files", True)

    printHeader("Cleaning up LethalMods")
    try:
        shutil.rmtree(lethalCompanyPath + "/LethalMods")
        os.remove(lethalCompanyPath + "/LethalMods.zip")
    except:
        printMessage("Failed to delete LethalMods", True)

    # finished
    printMessage("LethalMods installed successfully", False)
    sys.exit()
except:
    logging.exception("Something awful happened!")