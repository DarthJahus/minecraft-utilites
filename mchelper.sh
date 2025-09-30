#!/bin/bash

BASE_DIR="/minecraft"
SERVER_DIR="$BASE_DIR/servers-available"
SERVER_ACTIVE="$BASE_DIR/server"
MOD_DIR="$SERVER_ACTIVE/mods"

# ANSI colors
RED="\e[31m"
GREEN="\e[32m"
GREY="\e[90m"
RESET="\e[0m"

case "$1" in
    mods)
        # List mods sorted by last modified date
        ls -t "$MOD_DIR" | while read -r mod; do
            base="${mod%.jar}"              # strip .jar
            base="${base%.jar.disabled}"    # strip .disabled if present
            if [[ "$mod" == *.disabled ]]; then
                echo -e "[${GREY}DISABLED${RESET}] ${GREY}$base${RESET}"
            else
                echo -e "[${GREEN}ENABLED ${RESET}] $base"
            fi
        done
        ;;

    dismod)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 dismod <mod-base-name>"
            exit 1
        fi
        if [[ -f "$MOD_DIR/$2.jar" ]]; then
            mv "$MOD_DIR/$2.jar" "$MOD_DIR/$2.jar.disabled"
            echo -e "Disabled: ${GREY}$2.jar.disabled${RESET}"
        elif [[ -f "$MOD_DIR/$2.jar.disabled" ]]; then
            echo "Mod already disabled: $2"
        else
            echo "Mod not found: $2"
        fi
        ;;

    enmod)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 enmod <mod-base-name>"
            exit 1
        fi
        if [[ -f "$MOD_DIR/$2.jar.disabled" ]]; then
            mv "$MOD_DIR/$2.jar.disabled" "$MOD_DIR/$2.jar"
            echo -e "Enabled: ${GREEN}$2.jar${RESET}"
        elif [[ -f "$MOD_DIR/$2.jar" ]]; then
            echo "Mod already enabled: $2"
        else
            echo "Mod not found: $2"
        fi
        ;;

    enserv)
        TARGET="$2"
        if [ -z "$TARGET" ]; then
            echo "Usage: $0 enserv <server_name>"
            exit 1
        fi
        if [ ! -d "$SERVER_DIR/$TARGET" ]; then
            echo "[${RED}ERROR${RESET}] $SERVER_DIR/$TARGET does not exist"
            exit 1
        fi
        echo -e "[${RED}WARNING${RESET}] Stopping Minecraft Service"
        systemctl stop minecraft
        ln -sfn "$SERVER_DIR/$TARGET" "$SERVER_ACTIVE"
        echo -e "[INFO] Enabled server: ${GREEN}$TARGET${RESET}"
        echo -e "[${RED}WARNING${RESET}] Please manually start Minecraft Service with ${GREY}systemctl start minecraft${RESET}"
        ;;

    servers)
        echo "Available servers:"
        for srv in "$SERVER_DIR"/*; do
            name=$(basename "$srv")
            if [[ "$(readlink -f "$SERVER_ACTIVE")" == "$(readlink -f "$srv")" ]]; then
                echo -e "[${GREEN}ENABLED ${RESET}] $name"
            else
                echo -e "[${GREY}DISABLED${RESET}] $name"
            fi
        done
        ;;

    *)
        echo "Usage: $0 {mods|dismod <mod>|enmod <mod>|servers|enserv <server>}"
        exit 1
        ;;
esac
