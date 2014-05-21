
from subprocess import check_output
import os
from time import gmtime, strftime
import time
import pickle

cmake_tags = ['csound6_00','csound6_00_1','csound6_01',
  '6.01.00', '6.02.0','6.03.0', '6.03.1','6.03.2']

scons_tags = ['Csound5.07','csound-5.00.0',
  'csound-5.01.0','csound-5.02.0','csound-5.02.1','csound-5.03.0','csound-5.03.01','csound-5.04',
  'csound-5.05','csound5.06','csound5.07','csound5.08','csound5.08.2','csound5.09','csound5.10',
  'csound5.11','csound5.12','csound5.13','csound5.14','csound5_15','csound5_16','csound5_17',
  'csound5_17_1','csound5_17_2','csound5_17_3']

test_csds = ['examples/trapped.csd', 'examples/xanadu.csd']

num_runs = 20 # Number of times to run each example

bench_time =  strftime("%d-%m-%y-%H_%M_%S", gmtime())
runfile_name ='run_data-%s.p'%bench_time
buildfile_name ='build_data-%s.p'%bench_time

hostname = "andres"

run_data = {"host":hostname, "start_time": bench_time, "data": []}
build_data = {"host":hostname, "start_time": bench_time, "data": []}

for tag in cmake_tags:
    if not os.path.isdir("from_git/" + tag):
      check_output(["git", "clone", "-b", tag , "--depth", "1", "git@github.com:csound/csound.git", "from_git/" + tag])
    os.chdir("from_git/" + tag)
    
    build_start_time = time.perf_counter()
    if os.path.isdir("build"):
      os.chdir("build")
      check_output(["make", "clean"])
    else:
      os.mkdir("build")
      os.chdir("build")
      check_output(["cmake", ".."])
    check_output(["make", "-j7"])
    build_end_time = time.perf_counter()
    
    build_data_pass = {"tag": tag, "time": build_end_time - build_start_time}
    
    new_run_data = {"tag": tag, "data" : []}
    
    # TODO set OPCODEDIR before running
    
    for csd in test_csds:
      run_data_pass = {"csd":csd, "times": []}
      for run_pass in range(num_runs):
        pass_start_time = time.perf_counter()
        check_output(["./csound", "../../../" + csd])
        pass_end_time = time.perf_counter()
        run_data_pass["times"].append(pass_end_time - pass_start_time)
      new_run_data["data"].append(run_data_pass)
    
    os.chdir('..') # Back to source root
    
    os.chdir('../..') # Back to benchnmark root
    
    run_data["data"].append(new_run_data)
    build_data["data"].append(build_data_pass)


print("Writing: " +  runfile_name)
with open(runfile_name, 'wb') as fp:
    pickle.dump(run_data, fp, 2)
with open(buildfile_name, 'wb') as fp:
    pickle.dump(build_data, fp, 2)
    
# load data with:
#with open('data.p', 'rb') as fp:
#    data = pickle.load(fp)

    