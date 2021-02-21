import os
import glob
import subprocess as sp


GITHUB_EVENT_NAME = os.environ['GITHUB_EVENT_NAME']

# Set repository
CURRENT_REPOSITORY = os.environ['GITHUB_REPOSITORY']
# TODO: How about PRs from forks?
TARGET_REPOSITORY = os.environ['INPUT_TARGET_REPOSITORY'] or CURRENT_REPOSITORY
PULL_REQUEST_REPOSITORY = os.environ['INPUT_PULL_REQUEST_REPOSITORY'] or TARGET_REPOSITORY
REPOSITORY = PULL_REQUEST_REPOSITORY if GITHUB_EVENT_NAME == 'pull_request' else TARGET_REPOSITORY

# Set branches
GITHUB_REF = os.environ['GITHUB_REF']
GITHUB_HEAD_REF = os.environ['GITHUB_HEAD_REF']
GITHUB_BASE_REF = os.environ['GITHUB_BASE_REF']
CURRENT_BRANCH = GITHUB_HEAD_REF or GITHUB_REF.rsplit('/', 1)[-1]
TARGET_BRANCH = os.environ['INPUT_TARGET_BRANCH'] or CURRENT_BRANCH
PULL_REQUEST_BRANCH = os.environ['INPUT_PULL_REQUEST_BRANCH'] or GITHUB_BASE_REF
BRANCH = PULL_REQUEST_BRANCH if GITHUB_EVENT_NAME == 'pull_request' else TARGET_BRANCH

GITHUB_ACTOR = os.environ['GITHUB_ACTOR']
GITHUB_REPOSITORY_OWNER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_TOKEN = os.environ['INPUT_GITHUB_TOKEN']

# default values
LC_EXTENSIONS = [
    ".c", ".c++", ".cc", ".cpp", ".cxx",
    ".h", ".h++", ".hh", ".hpp", ".hxx",
    ".j", ".jav", ".java",
]

UC_EXTENSIONS = [ext.upper() for ext in LC_EXTENSIONS]

# command related inputs
DO_COMMIT = os.environ['INPUT_COMMIT_REPORT'] or False
FILE_EXTENSIONS = os.environ['INPUT_FILE_EXTENSIONS'] or LC_EXTENSIONS.extend(UC_EXTENSIONS)
SOURCE_DIR = os.environ['INPUT_SOURCE_DIR'] or ""
OUTPUT_DIR = os.environ['INPUT_OUTPUT_DIR'] or 'metrics'
REPORT_TYPE = os.environ['INPUT_REPORT_TYPE'] or 'html'


command = ""
out_dir = ""


def prepare_command():
    global command
    command = command + "cccc "
    command = command + " --outdir=" + OUTPUT_DIR
    source_dir = SOURCE_DIR

    file_exts = FILE_EXTENSIONS
    src_files = [
        f for ext in file_exts for f in glob.glob('**{}/*{}'.format(source_dir, ext),
                                                  recursive=True)
    ]

    file_arg = ""
    for fname in src_files:
        file_arg = file_arg + " " + fname

    command = command + " {}".format(file_arg)


def run_cccc():
    sp.call(command, shell=True)


def rm_unused_rpt():
    """
    We need to remove unused output format.
    """
    file_ext=".xml"
    if REPORT_TYPE == "xml":
        file_ext = ".html"


def commit_changes():
    """Commits changes.
    """
    set_email = 'git config --local user.email "cccc-action@master"'
    set_user = 'git config --local user.name "cccc-action"'

    sp.call(set_email, shell=True)
    sp.call(set_user, shell=True)

    git_checkout = f'git checkout {TARGET_BRANCH}'
    git_add = f'git add {OUTPUT_DIR}'
    git_commit = 'git commit -m "cccc report added"'
    print(f'Committing {OUTPUT_DIR}')

    sp.call(git_checkout, shell=True)
    sp.call(git_add, shell=True)
    sp.call(git_commit, shell=True)


def push_changes():
    """Pushes commit.
    """
    set_url = f'git remote set-url origin https://x-access-token:{GITHUB_TOKEN}@github.com/{TARGET_REPOSITORY}'
    git_push = f'git push origin {TARGET_BRANCH}'
    sp.call(set_url, shell=True)
    sp.call(git_push, shell=True)


def main():

    if (GITHUB_EVENT_NAME == 'pull_request') and (GITHUB_ACTOR != GITHUB_REPOSITORY_OWNER):
        return

    prepare_command()
    run_cccc()
    if DO_COMMIT:
        commit_changes()
        push_changes()


if __name__ == '__main__':
    main()
