import web


def append_headers(fn):
    def new(*args):
        web.header('Content-Type', 'application/json')
        return fn(*args)
    return new
