#!/bin/bash
#Let's Begin ::
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
    echo -e " ${g}Lockdoor Installer${enda} Will Now Exit"
    echo
    sleep 1
    exit
  fi
}

function install {
    showlogo && checkroot
    clear
    showlogo
    echo ""
    echo -e "\e[32m[-] Installing .... !\e[0m"
    echo ""
    #Theme
    rsync -a --progress Windows-10 /usr/share/themes
    chmod 775 /usr/share/themes/Windows-10
    #Icons
    rsync -a Windows-10-Icons /usr/share/icons
    chmod 775 /usr/share/icons/Windows-10-Icons
    #Files
    rsync -a --progress go-undercover /usr/share
    rsync -a --progress go-undercover.svg /usr/share/icons
    rsync -a --progress go-undercover.sh /usr/bin/go-undercover
    rsync -a --progress go-undercover.desktop /usr/share/applications/
    chmod 755 /usr/share/icons/go-undercover.svg
    chmod 775 /usr/share/go-undercover
    chmod 775 /usr/bin/go-undercover
    chmod 775 /usr/share/applications/go-undercover.desktop
    # Cleaning
    #Kech nhar
    # RUN
    echo ""
    echo -e "\e[32m[-] Run ${g}go-undercover${endc} from terminal or from ${b}Applications Menu${endc} .... !\e[0m"
}

#main
install