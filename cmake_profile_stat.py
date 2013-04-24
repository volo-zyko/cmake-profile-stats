#!/usr/bin/env python

from __future__ import print_function

import sys
import re
import os
import fileinput
import shelve
import argparse

def process_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('trace', nargs='?', default=None,
        help='cmake trace log or stdin')
    parser.add_argument('-f', '--shelve-file', default='cmake.traces',
        help='a file for shelf container {default: %(default)s}')
    parser.add_argument('-t', '--threshold',
        default=0, type=float,
        help='don\'t report traces with relative time lower than threshold, '
             'for example 0.01 corresponds to 1%% of the whole execution time '
             '{default: %(default)s}')
    parser.add_argument('-s', '--sort-traces',
        default=False, action='store_true',
        help='sort subcalls in a trace according to their timings '
             '{default: %(default)s}')
    parser.add_argument('-r', '--report-only',
        default=False, action='store_true',
        help='don\'t collect stats, make a report from shelved stats instead '
             '{default: %(default)s}')
    parser.add_argument('-1', '--one',
        default=False, action='store_true',
        help='report only the most expensive stack trace '
             '{default: %(default)s}')

    args = parser.parse_args()
    return args

class CmakeTraceInfo(object):
    def __init__(self, cmakeFile, cmakeLine, cmakeCodeLine):
        self.cmakeFile = cmakeFile
        self.cmakeLine = cmakeLine
        self.cmakeCodeLine = cmakeCodeLine

    def __str__(self):
        return ('%s(%s): %s' %
                (self.cmakeFile, self.cmakeLine, self.cmakeCodeLine))

    def key(self):
        # File name is reversed because it makes string comparison faster.
        return ('%s%s' % (self.cmakeLine, self.cmakeFile[::-1]))

class CmakeTrace(object):
    def __init__(self, duration, ti, parent):
        self.duration = duration
        self.traceInfo = ti
        self.parentTrace = parent
        self.traces = []

        try:
            p = parent
            while True:
                p.duration = p.duration + duration
                p = p.parentTrace
        except AttributeError:
            assert p is None

def update_trace(newTimeval, prevTimeval, prevTi, nestingGrew,
                 appendTrace, traces, startTimeRef):
    try:
        duration = newTimeval - prevTimeval
        assert duration > 0
    except TypeError:
        # This exception can happen only for the very first trace line.
        assert len(startTimeRef) == 0
        startTimeRef.append(newTimeval)
        return appendTrace

    if nestingGrew:
        # Switch to the last trace among children of the current trace,
        # making the nesting deeper.
        appendTrace = appendTrace.traces[-1]

    t = CmakeTrace(duration, prevTi, appendTrace)
    try:
        appendTrace.traces.append(t)
    except AttributeError:
        assert appendTrace is None
        appendTrace = t
    return appendTrace

def parent_trace(trace, levels):
    for x in xrange(0, levels):
        trace = trace.parentTrace
    return trace

def add_new_trace(prevNesting, appendTrace, traces, traceKeys):
    # -2 is because lowest nesting is 1 and even if we work at nesting 2
    # we still hold the trace at level 1 while filling in the level 2.
    p = parent_trace(appendTrace, prevNesting - 2)
    traces[p.traceInfo.key()] = p
    traceKeys[p.traceInfo.key()] = p.duration
    assert len(traces) == len(traceKeys) + 2

def collect_stats(traces, traceKeys):
    matcher = re.compile('^\(([^)]*)\) \(([^)]*)\) ([^(]*)\(([^)]*)\):  (.*)$')

    # Contains one element with start time.
    startTimeRef = []

    prevTi = None
    prevTimeval = None
    prevNesting = 0
    nestingGrew = False
    appendTrace = None
    for line in fileinput.input():
        m = matcher.match(line)
        if m is None:
            # This will log to stderr all lines that didn't match which will
            # provide: 1) control over matching; 2) a filling of progress. :)
            print('Ignore: %s' % line, end='', file=sys.stderr)
            continue

        timeval = float(m.group(1))
        nesting = int(m.group(2))
        cmakeFile = m.group(3)
        cmakeLine = m.group(4)
        cmakeCodeLine = m.group(5)

        # Make sure that cmake trace doesn't miss any lines when nesting
        # increases (if there are bugs in cmake logging). Missing lines when
        # nesting decreases is not important at all.
        assert ((nesting > prevNesting and nesting == prevNesting + 1) or
                nesting <= prevNesting)

        appendTrace = update_trace(timeval, prevTimeval, prevTi, nestingGrew,
                                   appendTrace, traces, startTimeRef)

        if nesting <= prevNesting:
            # Time to finish building current trace and start a new one.
            if nesting == 1:
                add_new_trace(prevNesting, appendTrace, traces, traceKeys)
                # Start a new trace.
                appendTrace = None
            else:
                appendTrace = parent_trace(appendTrace, prevNesting - nesting)

        prevTi = CmakeTraceInfo(cmakeFile, cmakeLine, cmakeCodeLine)
        nestingGrew = (nesting > 2 and nesting > prevNesting)
        prevTimeval = timeval
        prevNesting = nesting

    # Add the last trace line with the smallest duration for completeness.
    # This line shouldn't be important, though.
    appendTrace = update_trace(prevTimeval + 10E-7, prevTimeval, prevTi,
                               nestingGrew, appendTrace, traces, None)
    add_new_trace(prevNesting, appendTrace, traces, traceKeys)

    return prevTimeval - startTimeRef[0]

def print_trace(args, trace, duration, indent):
    if trace.duration / duration < args.threshold:
        return False

    print("%s%s (%f)(%f%%)" % (' ' * indent,
                               str(trace.traceInfo),
                               trace.duration,
                               trace.duration / duration * 100))
    for t in sorted(trace.traces,
                    key=lambda x: x.duration if args.sort_traces
                                  else x.traceInfo.cmakeLine,
                    reverse=True):
        print_trace(args, t, duration, indent + 1)
    return True


TRACE_KEYS_KEY = 'trace.keys'
WHOLE_DURATION_KEY = 'whole.duration'

if __name__ == '__main__':
    args = process_arguments()

    # Adjust sys.argv for fileinput().
    sys.argv = sys.argv[:1]
    if args.trace is not None:
        sys.argv.append(args.trace)

    if os.path.exists(args.shelve_file) and not args.report_only:
        os.remove(args.shelve_file)

    allTraces = shelve.open(args.shelve_file)

    # TODO: allTraceKeys should be a list but for now it's not possible due
    # to bugs in cmake logging.
    allTraceKeys = allTraces.get(TRACE_KEYS_KEY, {})
    wholeDuration = allTraces.get(WHOLE_DURATION_KEY, 0)
    allTraces[TRACE_KEYS_KEY] = allTraceKeys
    allTraces[WHOLE_DURATION_KEY] = wholeDuration

    try:
        if not args.report_only:
            wholeDuration = collect_stats(allTraces, allTraceKeys)
            allTraces[TRACE_KEYS_KEY] = allTraceKeys
            allTraces[WHOLE_DURATION_KEY] = wholeDuration
    except:
        os.remove(args.shelve_file)
        raise

    for (k, d) in sorted(allTraceKeys.iteritems(),
                         key=lambda x: x[1], reverse=True):
        if not print_trace(args, allTraces[k], wholeDuration, 0) or args.one:
            break
        print('')

    allTraces.close()
