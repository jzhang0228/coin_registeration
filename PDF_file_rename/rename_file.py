import os
import sys

def rename_files(directory):
    file_names = os.listdir(directory)
    # only keep pdf file
    file_names = [file_name for file_name in file_names if file_name.endswith('.pdf')]
    file_names.sort()
    for index, old_name in enumerate(file_names):
        remove_part, keep_part = old_name.rsplit('_', 1)
        new_name = '16XB1%04d_%s' % (index + 1, keep_part)
        os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
        print '%s --> %s' % (old_name, new_name)

if __name__ == '__main__':
    try:
        directory = sys.argv[1]
    except IndexError:
        print 'please provide either a relative directory or absolute directory.'
    else:
        rename_files(directory)