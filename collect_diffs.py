import argparse
import os
import subprocess


# Runs Clang with specified optimization level on a C or C++ file, emitting assembly or IR.
def collect(source_path, experiment, include_path, cpp=False, opt_level=3):
    clang_path = experiment['clang']
    if cpp:
        clang_path + '++'
    command = [clang_path, source_path,'-I', include_path, '-o', experiment['out'], '-O%d' %  opt_level, '-S']
    if experiment['ir']:
        command.append('-emit-llvm')
    subprocess.call(command)


# Collects the number of different lines in two files and populates `diff_stat` with data.
def collect_diff_stat(diff_stat, file_key, type_key, file1, file2):
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        print('One or both files do not exist, aborting...')
        return

    command = 'diff %s %s | grep -i -c \"^>\"' % (file1, file2)
    proc = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    num_diff_lines = int(output)
    print('Found %d different lines' % num_diff_lines)
    if num_diff_lines in diff_stat[type_key]:
        diff_stat[type_key][num_diff_lines].append(file_key)
    else:
        diff_stat[type_key][num_diff_lines] = [file_key]


# This is a main function that runs 4 experiments: 2 with the trunk version of LLVM and 2
# with changed LLVM. Diffs of these 2 versions are collected in separate files, and the
# size of the diff is estimated.
def run(path, out_dir, clang_trunk, clang_byte):
    diff_stat = {}
    diff_stat['asm'] = {}
    diff_stat['ir'] = {}
    for subdir, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('c') or file.endswith('cpp'):
                is_cpp = file.endswith('cpp')
                if is_cpp:
                    source_name = file.split('.cpp')[0]
                else:
                    source_name = file.split('.c')[0]
                source_path = os.path.join(subdir, file)
                table = [
                    {'clang': clang_trunk, 'out': os.path.join(out_dir, '%s-trunk.ll' % source_name), 'ir': True},
                    {'clang': clang_trunk, 'out': os.path.join(out_dir, '%s-trunk.s' % source_name),  'ir': False},
                    {'clang': clang_byte,  'out': os.path.join(out_dir, '%s-byte.ll' % source_name),  'ir': True},
                    {'clang': clang_byte,  'out': os.path.join(out_dir, '%s-byte.s' % source_name),   'ir': False},
                ]
                print('Collecting diffs for %s' % file)
                for experiment in table:
                    collect(source_path, experiment, path, is_cpp)
                collect_diff_stat(diff_stat, source_name, 'ir', table[0]['out'], table[2]['out'])
                collect_diff_stat(diff_stat, source_name, 'asm', table[1]['out'], table[3]['out'])
    print('Printing ASM diff statistics...')
    for k in sorted(diff_stat['asm'], reverse=True):
        for f in diff_stat['asm'][k]:
            print('%d: %s' % (k, f))
    print('Printing IR diff statistics...')
    for k in sorted(diff_stat['ir'], reverse=True):
        for f in diff_stat['ir'][k]:
            print('%d: %s' % (k, f))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collecting diffs for x264 benchmark')
    parser.add_argument('--dir', action='store')
    parser.add_argument('--clang-trunk-path', action='store')
    parser.add_argument('--clang-byte-path', action='store')
    parser.add_argument('--out-dir', action='store')
    args = parser.parse_args()
    run(args.dir, args.out_dir, args.clang_trunk_path, args.clang_byte_path)
