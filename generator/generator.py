#!/usr/bin/env python3
import os
import re
import glob
import subprocess

generator_path = os.path.dirname(os.path.realpath(__file__))
opendbc_root = os.path.join(generator_path, '../')
include_pattern = re.compile(r'CM_ "IMPORT (.*?)";\n')
generated_suffix = '_generated.dbc'


def read_dbc(src_dir: str, filename: str) -> str:
  with open(os.path.join(src_dir, filename), encoding='utf-8') as file_in:
    return file_in.read()


def replace_includes_recursively(src_dir, filename, dbc_file_in, is_root=False):
  includes = include_pattern.findall(dbc_file_in)

  out = ""

  for include_filename in includes:
    include_file_header = '\n\nCM_ "Imported file %s starts here";\n' % include_filename
    out += include_file_header

    include_file = read_dbc(src_dir, include_filename)
    out += replace_includes_recursively(src_dir, filename, include_file)
  
  if is_root:
    out += '\nCM_ "%s starts here";\n' % filename
  
  core_dbc = include_pattern.sub('', dbc_file_in)
  out += core_dbc

  return out


def create_dbc(src_dir: str, filename: str, output_path: str):
  dbc_file_in = read_dbc(src_dir, filename)

  output_filename = filename.replace('.dbc', generated_suffix)
  output_file_location = os.path.join(output_path, output_filename)

  with open(output_file_location, 'w', encoding='utf-8') as dbc_file_out:
    dbc_file_out.write('CM_ "AUTOGENERATED FILE, DO NOT EDIT";\n')

    dbc_file_out.write(replace_includes_recursively(src_dir, filename, dbc_file_in, is_root=True))


def create_all(output_path: str):
  # clear out old DBCs
  for f in glob.glob(f"{output_path}/*{generated_suffix}"):
    os.remove(f)

  # run python generator scripts first
  for f in glob.glob(f"{generator_path}/*/*.py"):
    subprocess.check_call(f)

  for src_dir, _, filenames in os.walk(generator_path):
    if src_dir == generator_path:
      continue

    #print(src_dir)
    for filename in filenames:
      if filename.startswith('_') or not filename.endswith('.dbc'):
        continue

      #print(filename)
      create_dbc(src_dir, filename, output_path)

if __name__ == "__main__":
  create_all(opendbc_root)
