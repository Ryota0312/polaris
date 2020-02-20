#!/bin/bash

SH_PATH=$(dirname $0)

echo "You have to disable polaris system before uninstall.(show bellow)"
echo "  $ pipenv run polaris disable"
echo "  $ pipenv run polaris cfal --stop"
read -p "Uninstall polaris system, OK? (y/N): " yn

case "$yn" in
    [yY]*)
	if [ "$(uname -s)" == 'Linux' ]; then
	    # for Linux
	    rm $HOME/.config/systemd/user/collect_file_access_log.service
	    rm $HOME/.config/systemd/user/polaris.service
	    rm $HOME/.config/systemd/user/polaris.timer
	elif [ "$(uname)" == 'Darwin' ]; then
	    # for macOS
	    rm $HOME/Library/LaunchAgent/collect_file_access_log.plist
	    rm $HOME/Library/LaunchAgent/polaris.plist	    
	fi
	echo "Uninstalled. Please remove polaris directory."
    ;;
    *) echo "Canceled";;
esac
