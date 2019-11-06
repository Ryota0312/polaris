#!/bin/bash

SH_PATH=$(dirname $0)

read -p "rm log/* db/* log.pickle OK? (y/N): " yn

case "$yn" in
    [yY]*)
	rm $SH_PATH/../log/*
	rm $SH_PATH/../db/*
	rm $SH_PATH/../log.pickle
	echo "rm log/* db/* log.pickle"
    ;;
    *) echo "Canceled";;
esac
