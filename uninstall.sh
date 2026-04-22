#!/bin/bash
# Undo Script for go-undercover
# Matches style of original installer

# Colors
b='\033[1m'
u='\033[4m'
bl='\E[30m'
r='\E[31m'
g='\E[32m'
y='\E[33m'
bu='\E[34m'
m='\E[35m'
c='\E[36m'
w='\E[37m'
endc='\E[0m'
enda='\033[0m'

function showlogo {
    clear
echo """
 
    _________           _____  __      _________           _________                         
    __  ____/_____      __  / / /____________  /_____________  ____/________   ______________
    _  / __ _  __ \     _  / / /__  __ \  __  /_  _ \_  ___/  /    _  __ \_ | / /  _ \_  ___/
    / /_/ / / /_/ /     / /_/ / _  / / / /_/ / /  __/  /   / /___  / /_/ /_ |/ //  __/  /    
    \____/  \____/      \____/  /_/ /_/\__,_/  \___//_/    \____/  \____/_____/ \___//_/     
                                Sofiane Hamlaoui | 2019
""";
    echo
}

function checkroot {
  showlogo
  if [[ $(id -u) = 0 ]]; then
    echo -e " Checking For ROOT: ${g}PASSED${endc}"
    echo ""
  else
    echo -e " Checking For ROOT: ${r}FAILED${endc}
 ${y}This Script Needs To Run As ROOT${endc}"
    echo ""
    echo -e " ${g}Go-Undercover Uninstaller${enda} Will Now Exit"
    echo
    sleep 1
    exit
  fi
}

function remove_if_exists {
    TARGET="$1"
    DESC="$2"

    if [ -e "$TARGET" ]; then
        echo -e " ${g}[-] Removing ${DESC}${endc}"
        rm -rf "$TARGET"
    else
        echo -e " ${y}[-] ${DESC} Not Found, Skipping...${endc}"
    fi
}

function uninstall {
    showlogo && checkroot
    clear
    showlogo
    echo ""
    echo -e "\e[31m[-] Uninstalling go-undercover .... !\e[0m"
    echo ""

    # Theme
    remove_if_exists "/usr/share/themes/Windows-10" "Windows-10 Theme"

    # Icons
    remove_if_exists "/usr/share/icons/Windows-10-Icons" "Windows-10 Icons"

    # go-undercover files
    remove_if_exists "/usr/share/go-undercover" "go-undercover directory"
    remove_if_exists "/usr/bin/go-undercover" "go-undercover executable"
    remove_if_exists "/usr/share/icons/go-undercover.svg" "go-undercover icon"
    remove_if_exists "/usr/share/applications/go-undercover.desktop" "desktop entry"

    echo ""
    echo -e "${g}[-] Cleaning icon & desktop cache...${endc}"
    gtk-update-icon-cache /usr/share/icons >/dev/null 2>&1 || true
    update-desktop-database >/dev/null 2>&1 || true

    echo ""
    echo -e "\e[32m[✓] System restored to pre go-undercover state.\e[0m"
    echo ""
}

# main
uninstall
