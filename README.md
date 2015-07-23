# cmake-profile-stats
Automatically exported from code.google.com/p/cmake-profile-stats

This small Python script allows to collect information about time spent in each call within cmake script and print nice stack traces sorted according to timings of each call.

Also currently cmake's trace does not provide timestamp information. However, here you can find a patch for cmake which adds timestamps and nesting level of traced lines. With this information cmake-profile-stats.py reconstructs stack traces from plain log.

Short help about usage of this script:

```
usage: cmake_profile_stat.py [-h] [-f SHELVE_FILE] [-t THRESHOLD]
                             [-w TRACE_INFO_WIDTH] [-s] [-r] [-1]
                             [trace]

positional arguments:
  trace                 cmake trace log or stdin

optional arguments:
  -h, --help            show this help message and exit
  -f SHELVE_FILE, --shelve-file SHELVE_FILE
                        file for shelf container {default: cmake.traces}
  -t THRESHOLD, --threshold THRESHOLD
                        do not report traces with relative time lower than
                        threshold, for example 0.01 corresponds to 1% of the
                        whole execution time {default: 0}
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

Each trace line in a report has 6 distinct parts:
1) nesting level in square brackets;
2) path to original cmake script (maybe with dots in the middle and
   dots at the end if -w option was used) followed by colon;
3) line number of a traced line in the original cmake script
   followed by colon;
4) a line of code as it was traced by cmake;
5) cumulative execution time of a traced line in seconds in brackets;
6) percentage of cumulative execution time of a traced line to
   whole execution time in brackets.
In short format is as follows:
[nesting]file_path:line_number: cmake_code (seconds) (percentage)

During script execution it can output to stderr lines that it
does not recognize as cmake trace lines. Normally such lines
originate from cmake script's messages and this script outputs
those lines starting with "Ignored: " string.
```
