"""main/model.py

Store the plugin model classes (such as the code checkers).
"""

import abc
import re
from io import StringIO
from subprocess import PIPE
from subprocess import Popen


class CheckerError(object):
    """Class model for code check errors."""

    DEFAULT_CASE = "E"

    def __init__(self, code, line, column, message):
        """Return a new instance of CheckerError"""

        self.case = self.DEFAULT_CASE
        self.code = self.fit_to_string(code)
        self.line = self.fit_to_unsigned_integer(line)
        self.column = self.fit_to_unsigned_integer(column)
        self.message = self.fit_to_string(message)

    @staticmethod
    def fit_to_string(x):
        """Parse variable to its equivalent string."""

        x = str(x)
        try:
            return x.replace(x[0], x[0].upper(), 1)
        except IndexError:
            return ""

    @staticmethod
    def fit_to_unsigned_integer(x):
        """Parse variable to its equivalent unsigned integer."""

        try:
            return max(int(x), 1)
        except ValueError:
            return 1


class Checker(object):
    """Abstract class for Python code checkers."""

    __metacls__ = abc.ABCMeta

    REGEX = r"({}\w\d*):({}\d*):({}\d*):({}.*)".format(
        "?P<code>", "?P<line>", "?P<column>", "?P<message>")

    @abc.abstractmethod
    def call_checker(self, filepath):
        """Abstract method with specific instructions for check_file."""

        pass

    def check_file(self, filepath):
        """Generic method to check Python code."""

        # Call to the specific checker and store the output log.
        out_result = self.call_checker(filepath)
        out_result.seek(0)
        out_result = list(l.strip("\n") for l in out_result.readlines())

        # Transcript the error messages using a regular expression.
        matches = (re.match(self.REGEX, l) for l in out_result)
        matches = (m for m in matches if m)

        # Yield every CheckerError instance.
        for match in sorted(matches, key=lambda m: int(m.group("line"))):
            yield self._new_error(**match.groupdict())

    def check_list_of_files(self, filelist):
        """Check Python code from a list of file names."""

        for filepath in filelist:
            for error in self.check_file(filepath):
                yield filepath, error

    def _new_error(self, **kwargs):
        """Return new instance of CheckError."""

        error = CheckerError(**kwargs)
        self._set_error_case(error)
        return error

    @staticmethod
    def _set_error_case(error):
        """Extract error case from CheckError code attribute."""

        error.case = error.code[0]


class CheckerPep8(Checker):
    """Python code checker based on Pep8 style guide."""

    NAME = "Pep8"

    def __init__(self):
        """Create a new instance of CheckerPep8."""

        self.args = [
            "--format=%(code)s:%(row)d:%(col)d:%(text)s",
            "--ignore=W391",
        ]

    def call_checker(self, filepath):
        """Call Pep8 in another thread and catch the output."""

        # Complete the list of arguments.
        self.args.insert(0, "pep8")
        self.args.insert(1, filepath)

        # Call pep8 routine, catch the results into a buffer and return.
        out_result = StringIO()
        call = Popen(self.args, stdout=PIPE, stderr=PIPE)
        try:
            out_result.write(call.communicate()[0].decode(encoding="UTF-8"))
        except BrokenPipeError:
            call.kill()
        return out_result

    def _call_checker_deprecated(self, filepath):
        """Deprecated version of call_checker for CheckerPep8."""

        import sys
        import pep8

        # Parse arguments from CheckerPep8.
        custom_format = self.args[0].split("--format=", 1)[-1]
        custom_ignore = self.args[1].split("--ignore=", 1)[-1].split(",")

        # Add custom report format and fill ignore list.
        pep8.REPORT_FORMAT["default"] = custom_format
        opts = pep8.StyleGuide().options
        opts.ignore += tuple(custom_ignore)

        # Save sys.stderr and sys.stdout in temporary variables.
        old_stderr, sys.stderr = sys.stderr, StringIO()
        old_stdout, sys.stdout = sys.stdout, StringIO()

        # Call the pep8 routine.
        with open(filepath, "r") as fileobj:
            content = fileobj.read().splitlines(True)
        pep8.Checker(filepath, content, opts).check_all()

        # Catch the results from sys.stderr and sys.stdout and restore
        # their original values.
        err_result, sys.stderr = sys.stderr, old_stderr
        out_result, sys.stdout = sys.stdout, old_stdout
        del err_result

        return out_result

    @staticmethod
    def _set_error_case(error):
        """Extract error case from error code."""

        code = error.code
        error.case = code[0] if (code[:2] == "E9") or (code[0] == "W") else "C"


class CheckerPyLint(Checker):
    """Python code checker based on PyLint library."""

    NAME = "PyLint"

    def __init__(self):
        """Create a new instance of CheckerPyLint."""

        self.args = [
            "--msg-template='{msg_id}:{line}:{column}:{msg}'",
            "--extension-pkg-whitelist=gi.repository,numpy,scipy",
            "--good-names=i,j,k,r,c,x,y,z,t,_",
            "--reports=n",
        ]

    def call_checker(self, filepath):
        """Call PyLint in another thread and catch the output."""

        # Complete the list of arguments.
        self.args.insert(0, "pylint")
        self.args.insert(1, filepath)

        # Call pylint routine, catch the results into a buffer and return.
        out_result = StringIO()
        call = Popen(self.args, stdout=PIPE, stderr=PIPE)
        try:
            out_result.write(call.communicate()[0].decode(encoding="UTF-8"))
        except BrokenPipeError:
            call.kill()
        return out_result

    def _call_checker_deprecated(self, filepath):
        """Deprecated version of call_checker for CheckerPyLint."""

        from pylint.lint import Run
        from pylint.reporters.text import TextReporter

        out_result = StringIO()

        self.args.insert(0, filepath)
        Run(self.args, reporter=TextReporter(out_result), exit=False)

        return out_result

