import subprocess
import os


def create_output_dirs(parameters):
    make_dir(parameters['output_dir'])
    make_dir(parameters['output_dir'], name='output_raster_mask')
    make_dir(parameters['output_dir'], name='output_vector')
    return


def run_cmd(cmd, verbose=True, ret_vals=False):
    if verbose:
        print(cmd)
    if not ret_vals:
        subprocess.run(cmd, shell=True)
    else:
        return subprocess.run(cmd, capture_output=True, text=True).stdout


def make_dir(path, name=None, verbose=False):
    if name is None:
        dir_ = path
    else:
        dir_ = os.path.join(path, name)
    if not os.path.exists(dir_):
        os.mkdir(dir_)
        if verbose:
            print(f'created directory {dir_}')
    else:
        if verbose:
            print(f'directory {dir} already existed')
    return
