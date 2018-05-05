# cmake-profile-stats

This small Python script collects information about the time spent in each call within cmake script and prints nice stack traces sorted according to timing of each call.

Although currently cmake's trace does not provide timestamp information, here you can find a patch for cmake which adds timestamps for traced lines. With this information `cmake-profile-stats.py` reconstructs stack traces from plain log.

Short help about usage of this script:

```
usage: cmake-profile-stat.py [-h] [-f SHELVE_FILE] [-t THRESHOLD] [-d DEPTH]
                             [-w TRACE_INFO_WIDTH] [-s] [-r] [-1] [-v]
                             [trace]

Process cmake execution log produced with --trace/--trace-expand command line
options.
Note: In order to provide command's timestamps CMake should be patched with
either of the diffs provided alongside this script and compiled from source

positional arguments:
  trace                 cmake trace log or stdin

optional arguments:
  -h, --help            show this help message and exit
  -f SHELVE_FILE, --shelve-file SHELVE_FILE
                        file for shelf container, which is used in subsequent
                        script runs without recurring log processing {default:
                        cmake.traces}
  -t THRESHOLD, --threshold THRESHOLD
                        do not report traces with relative time lower than the
                        threshold, for example 0.01 corresponds to 1% of the
                        whole execution time {default: 0}
  -d DEPTH, --depth DEPTH
                        do not report traces with depth bigger than requested
                        (depth=0 is ignored) {default: 0}
  --ignore-nesting      ignore nesting level field in input cmake log
  -w TRACE_INFO_WIDTH, --trace-info-width TRACE_INFO_WIDTH
                        fixed width in characters of a variable part of cmake
                        trace (file name, line number, nesting) in generated
                        report {default: None}
  -s, --sort-traces     sort subcalls in a trace according to their timings
                        {default: False}
  -r, --report-only     do not collect stats, make a report from shelved stats
                        instead {default: False}
  -1, --one             report only the most expensive stack trace {default:
                        False}
  -v, --verbose         enable verbose output {default: False}

Each trace line in a report has 6 distinct parts:
1) nesting level in square brackets;
2) path to original cmake script (maybe with dots in the middle and dots at
   the end if -w option was used);
3) line number of a traced line in the original cmake script in parentheses;
4) a line of code as it was traced by cmake;
5) cumulative execution time of a traced line in seconds in parentheses;
6) percentage of cumulative execution time of a traced line to whole execution
   time in parentheses.
In short format is as follows:
[nesting]file_path(line_number):  cmake_code (seconds)(percentage)

During script execution it can output to stderr lines which it does not
recognize as cmake trace lines. Normally such lines originate from cmake
script's messages and this script outputs those lines starting with
"Ignored: " string.
```
