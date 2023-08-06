# pysbatch

Submit(sbatch) slurm cluster job inside python and avoid shell script for complicated pipeline jobs. For sbatch options, now only supports job name, memory size(in GBs), time limit(in days), dependency and ouput file. But you can use add_option parameter to add more.

## install in linux/unix
```
# now published to PyPI, only support python version >= 3.5
pip install pysbatch
```


## running sbatch() function in python
```
from pysbatch import *
sbatch(wrap="python hello.py") # simplest

jobid=sbatch(wrap="python hello.py").strip("\n").split(" ")[-1] # dependency example
sbatch(job_name="py_job", mem=16, dep="--dependency:afterok:{}".format(jobid), time=3-0, log="submit.out", wrap="python hello.py") # more options

sbatch(job_name="py_job", add_option="--cpus-per-task=1 --nodes=3", wrap="python hello.py") # add more options

```

## running with custormized setting
```
# initialize and edit batch_setting object
x = batch_setting()
x2 = batch_setting(mem="16")

# edit default options contain in this pakcage:
# --ntasks, --cpus-per-task, -N, --job-name, --mem, --time, --out
x.edit_cpus_per_task(8)
x.edit_mem("16") # one at a time
x.edit_default("--cpus-per-task=2 --job-name=lalaland") # all together

# edit dependency, de
x.add_dep(27561)
x.add_dep(27562)
x.reset_dep()

# add aditional
x.add_options("--begin=16:00")

# the settings object can be reused
x.sbatch("python hello.py")

```


## run_cmd()
```
# simplified subprocess.run() of running linux command in python

# in linux
$ ls ..
unrar
var
zlib-1.2.11

#in python
>>>print(run_cmd(['ls', '..']))
unrar
var
zlib-1.2.11
```


## Authors

* **Gan Xu**  - [Ganxu.science](https://ganxu.science)


## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/luptior/pysbatch/blob/master/LICENSE) file for details
