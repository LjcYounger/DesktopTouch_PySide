def get_fps(default_fps = 60):
    import time
    t = None
    def fps():
        nonlocal t
        if t:
            t0 = t
            t = time.time()
            return 1/(t - t0+0.000000001)
        else:
            t = time.time()
            return default_fps
    return fps