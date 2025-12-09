#!/bin/bash -e

THIS_DIR="$(dirname "$(readlink -f "$BASH_SOURCE")")"
# macOS realpath errors if target path does not exist yet.
DEFAULT_VENV="$(realpath $THIS_DIR/..)/venv"
VENV="${1:-$DEFAULT_VENV}"
DEV_MODE="${DEV:-0}"
PY="${2:-}"  # Allow for explicitly set Python version

# If no Python specified as parameter, auto-detect
if [ -z "$PY" ]; then
    # Check if Python 3.12 exists, otherwise use Python 3.10
    if [ -f "/usr/local/bin/python3.12" ]; then
        PY="/usr/local/bin/python3.12"
    else
        PY="/usr/local/bin/python3.10"
    fi
fi

TRUSTED='--trusted-host pypi.org --trusted-host files.pythonhosted.org'

# From: https://stackoverflow.com/a/4024263
verlte() {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}
verlt() {
    [ "$1" = "$2" ] && return 1 || verlte $1 $2
}

make_venv() {
    mkdir -p "$(dirname "$VENV")"
    "$PY" -m venv "$VENV"
    "$VENV/bin/pip" install -U $TRUSTED pip wheel  # Support modern packages
}

echo "Script path: $THIS_DIR"
echo " Virtualenv: $VENV"
echo " Using Python: $PY"

if [ ! -d "$VENV" ]; then
    make_venv
elif [ -f "$VENV/bin/python" ]; then
    desired_py_vers=$($PY --version | cut -d' ' -f2)
    venv_py_vers=$($VENV/bin/python --version | cut -d' ' -f2)
    if [ "$venv_py_vers" != "$desired_py_vers" ]; then
        echo "'$venv_py_vers' != '$desired_py_vers'"
        rm -rf "$VENV"
        make_venv
    fi
fi

if [ "$DEV_MODE" = "1" ]; then
    reqfile="$THIS_DIR/requirements-dev.txt"
else
    reqfile="$THIS_DIR/requirements.txt"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    if type brew; then
        # From: https://stackoverflow.com/a/75473525
        HOMEBREW_NO_INSTALL_UPGRADE=1 brew install libssh
        CFLAGS="-I $(brew --prefix)/include -I ext -L $(brew --prefix)/lib -lssh" "$VENV/bin/pip" install ansible-pylibssh
    else
        echo "Script expects macOS to have homebrew installed"
        exit 1
    fi
fi

"$VENV/bin/pip" install -r "$reqfile" $TRUSTED
"$VENV/bin/ansible-galaxy" collection install -r "$THIS_DIR/requirements.yml"
