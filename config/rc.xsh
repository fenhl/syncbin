import sys

sys.path = list(map(str, [
    p'/opt/py',
    p'~/py',
    p'/opt/git/fenhl.net/syncbin-private/master/python',
    p'~/git/fenhl.net/syncbin-private/master/python',
    p'/opt/git/github.com/fenhl/syncbin/master/python',
    p'~/git/github.com/fenhl/syncbin/master/python',
    p'/usr/local/lib/python3.7/site-packages'
])) + sys.path

import basedir
import gitdir.host.github
import itertools
import more_itertools

# envars

$AUTO_CD = True
$AUTO_SUGGEST = False
#TODO $BOTTOM_TOOLBAR
$CASE_SENSITIVE_COMPLETIONS = True
$DYNAMIC_CWD_ELISION_CHAR = '…'
$EXPAND_ENV_VARS = False
$FUZZY_PATH_COMPLETION = False
$INDENT = '       '
$LANG = 'en_US.UTF-8'
$MULTILINE_PROMPT = '[$...] '
#TODO $PROMPT
#TODO $RIGHT_PROMPT
#TODO $TITLE
$UPDATE_COMPLETIONS_ON_KEYPRESS = True
$UPDATE_OS_ENVIRON = True
$UPDATE_PROMPT_ON_KEYPRESS = True
$XONSH_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
$XONSH_ENCODING = 'utf-8'
$XONSH_ENCODING_ERRORS = 'strict'
#TODO $XONSH_STDERR_PREFIX and $XONSH_STDERR_POSTFIX

# prepending to $PATH
$PATH = [
    '~/bin',
    '/opt/bin',
    '~/git/fenhl.net/syncbin-private/master/bin',
    '/opt/git/fenhl.net/syncbin-private/master/bin',
    '~/git/github.com/fenhl/syncbin/master/bin',
    '/opt/git/github.com/fenhl/syncbin/master/bin',
    '~/berryconda3/bin', # https://github.com/jjhelmus/berryconda
    '/usr/local/bin',
    '/usr/bin',
    '/bin',
    '/usr/local/sbin',
    '/usr/sbin',
    '/sbin',
    '/opt/local/bin',
    '/opt/local/sbin',
    '/opt/night/bin',
    '/opt/wurstmineberg/bin',
    '~/.cargo/bin',
    '~/.multirust/toolchains/stable/cargo/bin',
    '/usr/local/opt/ruby/bin',
    '~/.local/share/go/bin',
    '/Applications/Alice.app/Contents/Resources/bin',
    '/opt/X11/bin',
    '/usr/local/MacGPG2/bin',
    '/usr/texbin',
    '/usr/local/opt/llvm/bin'
    '/Library/Java/JavaVirtualMachines/jdk1.8.0_102.jdk/Contents/Home/bin' #TODO does this ever need to be updated?
] + $PATH
# appending to $PATH
if p'~/Library/Android/sdk'.exists():
    $PATH += [
        '~/Library/Android/sdk/platform-tools',
        '~/Library/Android/sdk/tools'
    ] + g`~/Library/Android/sdk/build-tools/*`
# remove duplicates
$PATH = more_itertools.unique_everseen($PATH)

# locale settings
$LANGUAGE = $LC_ALL = $LC_CTYPE = $LANG = 'en_US.UTF-8'

# Atom config
$ATOM_HOME = basedir.config_dirs('atom').path

# Go config
$GOPATH = ['~/.local/share/go']

# Java config
$JAVA_HOME = p'/Library/Java/JavaVirtualMachines/jdk1.8.0_102.jdk/Contents/Home'
if p'/usr/local/opt/android-sdk'.exists():
    $ANDROID_HOME = p'/usr/local/opt/android-sdk'

# Python config
sys.path = list(more_itertools.unique_everseen(sys.path))
$PYTHONPATH = sys.path
$PYTHONSTARTUP = gitdir.host.github.GitHub().repo('fenhl/syncbin').branch_path() / 'config' / 'pythonstartup.py'
$VIRTUAL_ENV_DISABLE_PROMPT = 1

# Ruby config
$GEM_HOME = p'~/.local/share/gem'

# Rust config
RUST_SRC_PATH = ['/opt/git/github.com/rust-lang/rust/master/src'] # required by racer
