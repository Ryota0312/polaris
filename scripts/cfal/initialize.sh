#!/bin/bash

SH_PATH=$(dirname $0)

if [ ! -e "$SH_PATH/config.sh" ]; then
    echo "####### config.sh is not exist #######"
    echo "Please create config.sh by copying config.sample.sh"
    exit 1
fi

if [ ! -x "$SH_PATH/config.sh" ]; then
    chmod +x $SH_PATH/config.sh
fi

source $SH_PATH/config.sh

fswatch_path=`which fswatch`

sed -e "s&your_CFAL_path&${YOUR_CFAL_DIR}&g" $SH_PATH/templates/collect_file_access_log.sh.tpl | sed -e "s&your_home_dir&${YOUR_HOME_DIR}&g" | sed -e "s&your_ignore_list&${YOUR_IGNORE_LIST}&g"  | sed -e "s&FSWATCH_PATH&${fswatch_path}&g" > $SH_PATH/collect_file_access_log.sh

if [ "$(uname -s)" == 'Linux' ]; then
    # for Linux
    sed -e "s&your_CFAL_path&${YOUR_CFAL_DIR}&g" $SH_PATH/templates/collect_file_access_log.service.tpl > $SH_PATH/collect_file_access_log.service
    cp $SH_PATH/collect_file_access_log.service ~/.config/systemd/user/
elif [ "$(uname)" == 'Darwin' ]; then
    # for Mac OS X
    sed -e "s&your_CFAL_path&${YOUR_CFAL_DIR}&g" $SH_PATH/templates/collect_file_access_log.plist.tpl > $SH_PATH/collect_file_access_log.plist
    cp $SH_PATH/collect_file_access_log.plist ~/Library/LaunchAgents/
fi

if [ ! -x "$SH_PATH/collect_file_access_log.sh" ]; then
    chmod +x $SH_PATH/collect_file_access_log.sh
fi

touch $SH_PATH/access_log
touch $SH_PATH/error_log

