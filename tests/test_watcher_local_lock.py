import fcntl,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from watch_jobs import watcher_lock_path


class WatcherLocalLockTests(unittest.TestCase):
    def test_host_scoped_project_specific_lock_and_exclusion(self):
        with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'XDG_RUNTIME_DIR':temp}):
            config={'host':socket.gethostname()}
            path=watcher_lock_path('/project/a',config)
            self.assertEqual(path.parent,Path(temp))
            self.assertNotEqual(path,watcher_lock_path('/project/b',config))
            self.assertEqual(path,watcher_lock_path('/project/a',config))
            self.assertNotEqual(path,watcher_lock_path('/project/a',config,purpose='submit'))
            with path.open('w') as first,path.open('w') as second:
                fcntl.flock(first,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):fcntl.flock(second,fcntl.LOCK_EX|fcntl.LOCK_NB)

    def test_wrong_host_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'another host'):
            watcher_lock_path('/project/a',{'host':'not-the-current-host'})


if __name__=='__main__':unittest.main()
