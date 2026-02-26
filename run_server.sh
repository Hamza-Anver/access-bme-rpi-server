#!/bin/bash

# Configuration
HOST="0.0.0.0"
PORT="8000"
APP_MODULE="main:app"
PID_FILE="server.pid"
LOG_FILE="server.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            echo "Server appears to be already running (PID: $(cat $PID_FILE))"
        else
            echo "Starting server in background..."
            nohup uvicorn $APP_MODULE --host $HOST --port $PORT > $LOG_FILE 2>&1 &
            echo $! > $PID_FILE
            echo "Server started with PID $(cat $PID_FILE). Logs in $LOG_FILE"
        fi
        ;;
    run)
        if [ -f "$PID_FILE" ]; then
            echo "Warning: A background server might be running (PID: $(cat $PID_FILE))."
            echo "Please stop it first if you encounter port binding errors."
        fi
        echo "Running server in foreground (Press Ctrl+C to stop)..."
        uvicorn $APP_MODULE --host $HOST --port $PORT --reload
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat $PID_FILE)
            echo "Stopping server (PID: $PID)..."
            kill $PID
            rm $PID_FILE
            echo "Server stopped."
        else
            echo "No PID file found. Is the server running?"
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat $PID_FILE)
            if ps -p $PID > /dev/null; then
                echo "Server is running (PID: $PID)"
            else
                echo "PID file exists but process $PID is not running."
            fi
        else
            echo "Server is not running."
        fi
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|run}"
        echo "  start   : Start server in background"
        echo "  stop    : Stop background server"
        echo "  restart : Restart background server"
        echo "  status  : Check status of background server"
        echo "  run     : Run server in foreground (visible output)"
        exit 1
        ;;
esac
