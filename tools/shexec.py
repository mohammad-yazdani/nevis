import subprocess
import os


class ShellFail(Exception):
    def __init__(self, error_msg: str, returncode: int) -> None:
        super(ShellFail, self).__init__()
        self.error_msg = error_msg
        self.returncode = returncode

    def why(self) -> None:
        print("ERROR: ", self.error_msg)
        print("\t\tCODE: ", str(self.returncode))


class Shell:

    def __init__(self, cwd: str = ".", env=None) -> None:
        super().__init__()
        if env is None:
            env = {}
        self.cwd = cwd
        self.env = env
        self.env.update(os.environ)

    def shell_execute(self, command: str) -> str:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=self.env, cwd=self.cwd)
        output, err = p.communicate()
        if p.returncode != 0:
            raise ShellFail(err.decode("utf-8"), p.returncode)
        self.env.update(os.environ)
        return output.decode("utf-8")
