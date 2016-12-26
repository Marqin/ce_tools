#!python3
"""
This script combines the required engine and project files into a single directory.
It does not package the assets into .pak files, it simply collects the files that are present.
"""
import os
import shutil
import fnmatch
import subprocess

dll_name = 'Game.dll'


def copy_engine_binaries(engine_path, export_path, rel_dir):
    """
    Copy a directory to its corresponding location in the export directory.
    :param engine_path: Current location of the files (project_path or engine_path).
    :param export_path: Path to which the binaries should be exported.
    :param rel_dir: Path of the directory to copy, relative to *source_dir*.
    """
    copypaths = []

    excludes = ['imageformats**',
                'ToolkitPro*',
                'platforms**',
                'Qt*',
                'mfc*',
                'CryGame*',
                'Sandbox*',
                'ShaderCacheGen*',
                'smpeg2*',
                'icu*',
                'python27*',
                'LuaCompiler*',
                'Editor**']

    pwd = os.getcwd()
    os.chdir(engine_path)
    for root, _, filenames in os.walk(rel_dir):
        for filename in filenames:
            copypaths.append(os.path.normpath(os.path.join(root, filename)))
    os.chdir(pwd)

    for path in copypaths:
        excluded = False
        for pattern in excludes:
            excluded = excluded or fnmatch.fnmatch(path, os.path.join(rel_dir, pattern))
        if excluded:
            print('Excluding path: {}'.format(path))
            continue
        destpath = os.path.normpath(os.path.join(export_path, path))
        if not os.path.exists(os.path.dirname(destpath)):
            os.makedirs(os.path.dirname(destpath))
        shutil.copy(os.path.join(engine_path, path), destpath)


def copy_levels(project_path, export_path):
    """
    Copy required level files to the export directory.
    """
    pwd = os.getcwd()
    os.chdir(os.path.join(project_path, 'Assets'))

    level_files = ['filelist.xml', 'terraintexture.pak', 'level.pak']

    for root, _, filenames in os.walk('levels'):
        for filename in filenames:
            if filename not in level_files:
                continue
            path = os.path.normpath(os.path.join(root, filename))
            destpath = os.path.normpath(os.path.join(export_path, 'Assets', path))
            if not os.path.exists(os.path.dirname(destpath)):
                os.makedirs(os.path.dirname(destpath))
            shutil.copy(os.path.join(project_path, 'Assets', path), destpath)

    os.chdir(pwd)
    return


def package_assets(project_path, export_path):
    """
    Create .pak files from the loose assets, which are placed in the exported directory.
    """
    assetpath = os.path.join(project_path, 'Assets')
    for itemname in os.listdir(assetpath):
        itempath = os.path.join(project_path, 'Assets', itemname)
        if 'levels' in itempath.lower():
            continue

        if os.path.isfile(itempath):
            shutil.copyfile(itempath, os.path.join(export_path, 'Assets', itemname))
        else:
            zip_file = os.path.join(export_path, 'Assets', itemname)
            path_to_zip = os.path.join(assetpath, 'Assets', itempath)
            
            shutil.make_archive(zip_file, "zip", path_to_zip, ".")
            os.replace("{}.zip".format(zip_file), "{}.pak".format(zip_file))
    return


def create_config(export_path):
    with open(os.path.join(export_path, 'system.cfg'), 'w') as fd:
        fd.write('sys_game_folder=Assets\n')
        fd.write('sys_dll_game={}\n'.format(dll_name))


def copy_game_dll(project_path, export_path):
    """
    Search the project's bin/win_x64 directory for a game DLL.
    When one is found, set this globally (so that it can be added to the system.cfg).
    """
    global dll_name

    binpath = os.path.join(project_path, 'bin', 'win_x64')
    for filename in os.listdir(binpath):
        # Ignore any .pdb, .ilk, .manifest, or any other files that aren't DLLs.
        if not fnmatch.fnmatch(os.path.join(binpath, filename), '*.dll'):
            continue

        dll_name = filename
        shutil.copyfile(os.path.join(binpath, filename),
                        os.path.join(export_path, 'bin', 'win_x64', filename))


def main():
    engine_version = '5.2'
    engine_path = r'C:\Program Files (x86)\Crytek\CRYENGINE Launcher\Crytek\CRYENGINE_{}'.format(engine_version)

    # Path to the project as created by the launcher.
    project_path = os.path.join(engine_path, 'Templates', 'cpp', 'RollingBall')

    # Path to which the game is to be exported.
    export_path = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], 'Desktop', 'ce_game')

    # Copy engine (common) files.
    shutil.copytree(os.path.join(engine_path, 'engine'), os.path.join(export_path, 'engine'))
    copy_engine_binaries(engine_path, export_path, os.path.join('bin', 'win_x64'))

    # Copy project-specific files.
    package_assets(project_path, export_path)
    copy_levels(project_path, export_path)
    copy_game_dll(project_path, export_path)
    create_config(export_path)


if __name__ == '__main__':
    main()
