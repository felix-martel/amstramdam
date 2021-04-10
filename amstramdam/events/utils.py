from amstramdam import socketio


def safe_cancel(timer):
    if not timer:
        return
    try:
        timer.cancel()
    except AttributeError:
        pass


def wait_and_run(seconds, func, *args, **kwargs):
    def waiter():
        socketio.sleep(seconds)
        func(*args, **kwargs)

    socketio.start_background_task(waiter)
