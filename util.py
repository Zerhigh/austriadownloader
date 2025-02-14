import subprocess

def run_cmd(cmd, verbose=True, ret_vals=False):
    if verbose:
        print(cmd)
    if not ret_vals:
        subprocess.run(cmd, shell=True)
    else:
        return subprocess.run(cmd, capture_output=True, text=True).stdout
