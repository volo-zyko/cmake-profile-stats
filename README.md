# cmake-profile-stats

This small Python script collects information about the time spent in each call within cmake script and prints nice stack traces sorted according to timing of each call.

Short help about usage of this script:

```
usage: cmake-profile-stat.py [-h] [-f SHELF_FILE] [-r] [-t THRESHOLD]
                             [-d DEPTH] [--ignore-nesting]
                             [-w TRACE_INFO_WIDTH] [-s] [-1]
                             [trace]

Process cmake execution log produced with --trace-format=json-v1 command
line argument.

positional arguments:
  trace                 cmake trace log or stdin

optional arguments:
  -h, --help            show this help message and exit
  -f SHELF_FILE, --shelf-file SHELF_FILE
                        collect stats to the provided shelf file (without
                        printing a report) {default: cmake.traces}
  -r, --report-only     do not collect stats, make a report from the shelved
                        stats instead (stats specified with --shelf-file)
                        {default: False}
  -t THRESHOLD, --threshold THRESHOLD
                        do not report traces with relative time lower than the
                        threshold; for example, 0.01 corresponds to 1% of the
                        whole execution time {default: 0}
  -d DEPTH, --depth DEPTH
                        do not report traces with depth greater than requested
                        (depth=0 is ignored) {default: 0}
  --ignore-nesting      ignore "frame" field provided by cmake and build up
                        "scopes" nesting based on the file names in order of
                        cmake code execution
  -w TRACE_INFO_WIDTH, --trace-info-width TRACE_INFO_WIDTH
                        fixed width in characters of a variable part of cmake
                        trace (file name, line number, nesting) in generated
                        report {default: None}
  -s, --sort-traces     sort subcalls in a trace according to their timings
                        {default: False}
  -1, --one             report only the most expensive stack trace {default:
                        False}

Each trace line in the resulting report has 6 distinct parts:
1) nesting level in square brackets;
2) path to the original cmake script (maybe with dots in the middle and dots at
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
