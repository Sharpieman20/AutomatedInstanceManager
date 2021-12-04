import random
from contextlib import contextmanager
from pathlib import Path

'''
in directory
    listener waits for a file with its name on it on in directory
        when it shows up, that means it has been renamed
        then we can read from it all we want
out directory
    when a hotkey is pressed
        create a new file in out directory
        when you're done with the file, rename it into in directory
        use atomic file create to guarantee we're the only one
    main thread
        writes into out directory
        when we're done with it, rename it into in directory
'''

@contextmanager
def create_tempfile(outpath, mode):
    temp_num = random.randint(0, 999999)
    tmp_pipe = None
    pipe_dir = Path.cwd() / '.pipes'
    if not pipe_dir.exists():
        pipe_dir.mkdir()
    while tmp_pipe is None or tmp_pipe.exists():
        tmp_pipe = Path.cwd() / '.pipes' / '.tmp.{}'.format(temp_num)
    tmp_pipe.touch()
    try:
        yield open(tmp_pipe, 'w')
    finally:
        tmp_pipe.rename(outpath)

class Pipe:
    def __init__(self, name):

        self.name = name
        self.outfile = Path.cwd() / '.pipes' / '.{}.aimpipe.out'.format(name)
        self.infile = Path.cwd() / '.pipes' / '.{}.aimpipe.in'.format(name)

    def write(self, text):
        with create_tempfile(self.outfile) as fil:
            fil.write(text)

    def read(self):
        with open(self.file, 'r') as fil:
            return fil.read()

    def append(self, text):
        with open(self.file, 'a') as fil:
            fil.write(text)

class LockablePipe(Pipe):
    def __init__(self, name):
        super().__init__(name)
        self.pipelock = Pipe('{}.lock'.format(name))

    def force_acquire(self):
        while self.pipelock.exists():
            sleep(0.1)
        acquire_successful = self.try_acquire()
        if not acquire_successful:
            self.force_acquire()
        return self.acquire()

    def try_acquire(self):
        if self.pipelock.exists():
            return False
        rand_text = str(random.rand())
        self.pipelock.touch()
        self.pipelock.append(rand_text)
        if self.pipelock.read().strip() != rand_text:
            return False
        return True

    def release(self):
        self.pipelock.unlink()

    def try_release(self):
        if self.pipelock.exists():
            self.release()

class IoLockablePipe(LockablePipe):
    def __init__(self, name):
        super().__init__(name)

    def force_write(self, text):
        self.force_acquire()
        self.write(text)
        self.try_release()

    def force_write_async(self, text):
        forced_write_thread = threading.Thread(target=self.force_write(), args=(text,))
        forced_write_thread.start()

    def try_read(self):
        if not lockedpipe.try_acquire():
            return None
        result = lockedpipe.read()
        lockedpipe.try_release()
        return result

