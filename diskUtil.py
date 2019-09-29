#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import  isdir
from os import scandir, getcwd
import argparse
import sys
from math import ceil


def ConvertSize(size):
    ''' Function to convert bytes to human readable format
    Function returns string of converted size and suffix from sufix_list
    '''
    size = BlockSizeCalc(size)
    sufix_list = {0 : "",
               1: "K",
               2: "M",
               3: "G",
               4: "T"}
    sufix = 1
    if size == 0:
        return 0, ""
    size = size/1024
    if size <=1 :
            return 1, "K"
    while size > 1000:
        size = size/1024
        sufix +=1
    return "%.1f"%size, sufix_list.get(sufix)

def PPrint(*args):
    ''' Print to console file or directory size, format and path
    '''
    if main_args.hreadable:
        print("%s%s\t%s" %(args[1:4]))
    else:
        print("%s%s\t%s" %(args[0], "" ,args[3]))

def BlockSizeCalc(fsize):
    ''' Function to calculate size on disk (depending on block size)
    '''
    if fsize == 0:
        return 0
    else:
        return ceil(fsize/int(main_args.blsize))*int(main_args.blsize)

def DirRecu(path, MaxDepth, size=0):
    '''Main recursive function to count size for files and directories.
    By default is skipping symlinks
    Even empty folder on linux, has size of 1 block, so script adds
    4K to each directory's size
    DirRecu takes MaxDepth parameter used to call PPrint function
    '''
    if not isdir(path):
        print("Path %s does not exists" %path)
        return False
    else:
        for item in scandir(path):
            if item.is_symlink():
                pass
            elif item.is_file():
                file_size = item.stat().st_size
                size += file_size
                results, suffix = ConvertSize(file_size)
                if MaxDepth > 0 and main_args.all:
                    PPrint(file_size, results, suffix, item.path)
            elif item.is_dir():
                try:
                    dir_size = DirRecu(item.path, MaxDepth=MaxDepth-1)
                    if 'linux' in sys.platform:
                        dir_size += int(main_args.blsize)
                except PermissionError:
                    print("cannot read directory %s Permission denied" %(item.path))
                except OSError:
                    print("The file cannot be accessed by the system %s" %(item.path))
                else:
                    size += dir_size
                    results, suffix = ConvertSize(dir_size)
                    if MaxDepth > 0:
                        PPrint(dir_size, results, suffix, item.path)
        return size

def main(path, MaxDepth):
    '''Main function to start script and prints end result
    Again, for linux function adds 4K to each directory's size
    '''
    total_size = DirRecu(path, MaxDepth=MaxDepth)
    if not total_size:
        return
    else:
        if 'linux' in sys.platform:
            total_size+=int(main_args.blsize)
        results, suffix = ConvertSize(total_size)
        PPrint(total_size, results, suffix, path)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disk Utility")
    argv = sys.argv[1:]
    parser.add_argument('-p', '--path', nargs = '?', default=getcwd(), help='path to be scanned')
    parser.add_argument('-d', '--depth', nargs = '?', default=64, help='print the total for a directory (or file, with --all) only if it is N or fewer levels below the command')
    parser.add_argument('-b', '--blsize', nargs = '?', default=4096, help='block size in byte')
    parser.add_argument('-hr', '--hreadable', action='store_const', const=True, help='print sizes in human readable format (e.g., 1K 234M 2G)')
    parser.add_argument('-a', '--all', action='store_const', const=True, help='print sizes for files and directories')
    main_args = parser.parse_args(argv)
    main(main_args.path, int(main_args.depth))
