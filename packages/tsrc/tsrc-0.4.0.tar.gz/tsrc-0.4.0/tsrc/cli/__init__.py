""" Common tools for tsrc commands """

import os

from path import Path

import tsrc
import tsrc.workspace


def find_workspace_path():
    """ Look for a workspace root somewhere in the upper directories
    hierarchy

    """
    head = os.getcwd()
    tail = True
    while tail:
        tsrc_path = os.path.join(head, ".tsrc")
        if os.path.isdir(tsrc_path):
            return Path(head)

        else:
            head, tail = os.path.split(head)
    raise tsrc.Error("Could not find current workspace")


def get_workspace(args):
    if args.workspace_path:
        workspace_path = Path(args.workspace_path)
    else:
        workspace_path = find_workspace_path()
    return tsrc.workspace.Workspace(workspace_path)
