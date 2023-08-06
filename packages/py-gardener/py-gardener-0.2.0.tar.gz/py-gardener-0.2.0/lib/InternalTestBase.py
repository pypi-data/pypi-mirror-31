import re
import fnmatch
from os import path, walk


class InternalTestBase(object):
    ROOT_DIR = None
    TEST_DIR = None
    LIB_DIR = None

    def list_project_files(self, exclude=None):
        """ List python project files """
        if exclude is None:
            exclude = ["env"]

        # compile asterisks to regular expressions
        exclude_regex = []
        for excluded in [path.join(self.ROOT_DIR, excluded) for excluded in
                         exclude]:
            escaped = re.escape(excluded)
            escaped = escaped.replace(
                "\\*\\*", ".*")  # pylint: disable=W1401
            escaped = escaped.replace(
                "\\*", "[^\\/]*")  # pylint: disable=W1401
            exclude_regex.append(re.compile(escaped))

        result = []
        for root, _, files in walk(self.ROOT_DIR):
            for file_ in fnmatch.filter(files, "*.py"):
                abs_path = path.join(root, file_)
                include = True
                for excluded in exclude_regex:
                    if excluded.match(abs_path):
                        include = False
                        break
                if include:
                    result.append(abs_path)

        return result
