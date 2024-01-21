#!/bin/bash

APP_NAME="QQ"
LOG_FILE=$0
SHELL_DIR=${0%/*}
if [ $SPECIFY_SHELL_DIR ]; then
    SHELL_DIR=$SPECIFY_SHELL_DIR
fi

PUBLIC_DIR="/var/public"

UsePublicDir()
{
    if [ -z "$USE_PUBLIC_DIR" ]; then
        echo "Don't use public dir"
        return 1
    fi
    if [ ! -d "$PUBLIC_DIR" ];then
        echo "Not found $PUBLIC_DIR"
        return 1
    fi
    if [ ! -r "$PUBLIC_DIR" ];then
        echo "Can't read for $PUBLIC_DIR"
        return 1
    fi
    if [ ! -w "$PUBLIC_DIR" ];then
        echo "Can't write for $PUBLIC_DIR"
        return 1
    fi
    if [ ! -x "$PUBLIC_DIR" ];then
        echo "Can't excute for $PUBLIC_DIR"
        return 1
    fi

    return 0
}

WINE_BOTTLE="$HOME/.deepinwine"

if UsePublicDir;then
    WINE_BOTTLE="$PUBLIC_DIR"
fi

get_wine_by_pid()
{
    wine_path=$(cat /proc/$1/maps | grep -E "\/wine$|\/wine64$|\/wine |\/wine64 " | head -1 | awk '{print $6}')
    if [ -z "$wine_path" ];then
        cat /proc/$1/cmdline| xargs -0 -L1 -I{} echo {} | grep -E "\/wine$|\/wine64$|\/wine |\/wine64 " | head -1
    else
        echo $wine_path
    fi
}

is_wine_process()
{
    wine_module=$(get_wine_by_pid $1)
    if [ -z "$wine_module" ];then
        wine_module=$(cat /proc/$1/maps | grep -E "\/wineserver$" | head -1)
    fi
    echo $wine_module
}

set_emu_by_pid()
{
    emu_cmd=$(xargs -0 printf '%s\n' < /proc/$1/environ | grep ^EMU_CMD=)
    emu_args=$(xargs -0 printf '%s\n' < /proc/$1/environ | grep ^EMU_ARGS=)
    if [ -n "$emu_cmd" ];then
        export "$emu_cmd"
    fi
    if [ -n "$emu_args" ];then
        export "$emu_args"
    fi
    debug_log_to_file "$1 EMU_CMD: $EMU_CMD, EMU_ARGS: $EMU_ARGS"
}

get_prefix_by_pid()
{
    WINE_PREFIX=$(xargs -0 printf '%s\n' < /proc/$1/environ | grep WINEPREFIX)
    WINE_PREFIX=${WINE_PREFIX##*=}
    if [ -z "$WINE_PREFIX" ] && [ -n "$(is_wine_process $1)" ]; then
        #不指定容器的情况用默认容器目录
        WINE_PREFIX="$HOME/.wine"
    fi
    if [ -n "$WINE_PREFIX" ];then
        WINE_PREFIX=$(realpath $WINE_PREFIX)
        echo $WINE_PREFIX
    fi
}

get_wineserver_pid()
{
    if [ -z "$1" ];then
        return
    fi
    targ_prefix=$(realpath $1)
    for server_pid in $(ps -ef | grep wineserver | awk '{print $2}') ;do
        server_prefix=$(get_prefix_by_pid $server_pid)
        debug_log_to_file "get server pid $server_pid, prefix: $server_prefix"

        if [ "$targ_prefix" = "$server_prefix" ];then
	    echo $server_pid
            return
        fi
    done
}

init_log_file()
{
    if [ -d "$DEBUG_LOG" ];then
        LOG_DIR=$(realpath $DEBUG_LOG)
        if [ -d "$LOG_DIR" ];then
            LOG_FILE="${LOG_DIR}/${LOG_FILE##*/}.log"
            echo "" > "$LOG_FILE"
            debug_log "LOG_FILE=$LOG_FILE"
        fi
    fi
}

debug_log_to_file()
{
    if [ -d "$DEBUG_LOG" ];then
        strDate=$(date)
        echo -e "${strDate}:${1}" >> "$LOG_FILE"
    fi
}

debug_log()
{
    strDate=$(date)
    echo "${strDate}:${1}"
}

init_log_file

get_bottle_path_by_process_id()
{
    PID_LIST="$1"
    PREFIX_LIST=""

    for pid_var in $PID_LIST ; do
        WINE_PREFIX=$(get_prefix_by_pid $pid_var)
        #去掉重复项
        for bottle_path in $(echo -e $PREFIX_LIST) ; do
            if [[ $bottle_path == "$WINE_PREFIX" ]]; then
                WINE_PREFIX=""
            fi
        done
        if [ -d "$WINE_PREFIX" ]; then
            debug_log_to_file "found $pid_var : $WINE_PREFIX"
            PREFIX_LIST+="\n$WINE_PREFIX"
        fi
    done
    echo -e $PREFIX_LIST
}

get_pid_by_process_name()
{
    PID_LIST=""
    for pid_var in $(ps -ef | grep -E -i "$1" | grep -v grep | awk '{print $2}');do
        #通过判断是否加载wine来判断是不是wine进程
        if [ -n "$(is_wine_process $pid_var)" ];then
            PID_LIST+=" $pid_var"
        fi
    done
    echo "$PID_LIST"
}

get_bottle_path_by_process_name()
{
    PID_LIST=$(get_pid_by_process_name $1)
    debug_log_to_file "get pid list: $PID_LIST"
    get_bottle_path_by_process_id "$PID_LIST"
}

get_bottle_path()
{
    if [ -z "$1" ];then
        return 0
    fi

    if [ -f "$1/user.reg" ]; then
        realpath "$1"
        return 0
    fi

    if [ -f "$WINE_BOTTLE/$1/user.reg" ]; then
        realpath "$WINE_BOTTLE/$1"
        return 0
    fi
    get_bottle_path_by_process_name "$1"
}

get_wineserver_path_by_pid()
{
    server_info=$(ps -ef | grep -E "${1}.*wineserver" | grep -v grep)
    debug_log_to_file "get server info $server_info"
    WINESERVER=$(echo $server_info | awk '{print $NF}')
    if [ ! -f "$WINESERVER" ];then
        WINESERVER=$(echo $server_info | awk '{print $(NF-1)}')
        WINESERVER=${WINESERVER%*.real}
    fi
    debug_log_to_file "get server $WINESERVER"
}

kill_app()
{
    debug_log "try to kill $1"
    for bottle_path in $(get_bottle_path $1); do
        if [ -n "$bottle_path" ];then
            server_pid=$(get_wineserver_pid "$bottle_path")
            if [ -z "$server_pid" ];then
                continue
            fi
            set_emu_by_pid $server_pid

            get_wineserver_path_by_pid $server_pid
            if [ -f "$WINESERVER" ];then
                debug_log "kill $bottle_path by $WINESERVER"
                # 兼容arm版本，通过模拟器运行
                env WINEPREFIX="$bottle_path" $EMU_CMD $EMU_ARGS "$WINESERVER" -k
            fi
        fi
    done

    #Kill defunct process
    ps -ef | grep -E "$USER.*exe.*<defunct>"
    ps -ef | grep -E "$USER.*exe.*<defunct>" | grep -v grep | awk '{print $2}' | xargs -i kill -9 {}
}

get_tray_window()
{
    $SHELL_DIR/get_tray_window | awk -F: '{print $2}'
}

get_stacking_window()
{
    xprop -root _NET_CLIENT_LIST_STACKING | awk -F# '{print $2}' | sed -e 's/, / /g'
}

get_window_pid()
{
    for winid in $(echo "$1" | sed -e 's/ /\n/g') ;
    do
        xprop -id $winid _NET_WM_PID | awk -F= '{print $2}'
    done
}

get_window_bottle()
{
    debug_log_to_file "get_window_bottle $1"
    PID_LIST=$(get_window_pid "$1")
    debug_log_to_file "get_window_bottle pid list: $PID_LIST"
    get_bottle_path_by_process_id "$PID_LIST"
}

get_active_bottles()
{
    TRAYWINDOWS=$(get_tray_window)
    STACKINGWINDOWS=$(get_stacking_window)
    debug_log_to_file "tray window id: $TRAYWINDOWS"
    debug_log_to_file "stacking window id: $STACKINGWINDOWS"
    PID_LIST="$TRAYWINDOWS $STACKINGWINDOWS"
    get_window_bottle "$PID_LIST"
}

kill_exit_block_app()
{
    TAGBOTTLE=$(get_bottle_path $1)
    debug_log "tag bottle: $TAGBOTTLE"
    ACTIVEBOTTLES=$(get_active_bottles)
    debug_log "active bottles: $ACTIVEBOTTLES"

    if [[ "$ACTIVEBOTTLES" != *"$TAGBOTTLE"* ]]; then
         kill_app "$TAGBOTTLE"
    fi
}

#get_active_bottles
#exit

debug_log "kill $1 $2"

if [ -n "$1" ]; then
    APP_NAME="$1"
fi

if [ "$2" = "block" ]; then
    kill_exit_block_app $APP_NAME $3
else
    kill_app $APP_NAME
fi
