"""Utilities for building up Singularity commands...

...using common defaults and configuration mechanisms.
"""
import os

from six.moves import shlex_quote

from .commands import argv_to_str

DEFAULT_DOCKER_COMMAND = "docker"
DEFAULT_SINGULARITY_COMMAND = "singularity"
DEFAULT_SUDO = True
DEFAULT_SUDO_COMMAND = "sudo"
DEFAULT_HOST = None
DEFAULT_VOLUME_MOUNT_TYPE = "rw"
DEFAULT_WORKING_DIRECTORY = None
DEFAULT_NET = None
DEFAULT_MEMORY = None
DEFAULT_VOLUMES_FROM = None
DEFAULT_AUTO_REMOVE = True
DEFAULT_SET_USER = "$UID"
DEFAULT_RUN_EXTRA_ARGUMENTS = None


class DockerVolume(object):

    def __init__(self, path, to_path=None, how=DEFAULT_VOLUME_MOUNT_TYPE):
        self.from_path = path
        self.to_path = to_path or path
        if not DockerVolume.__valid_how(how):
            raise ValueError("Invalid way to specify docker volume %s" % how)
        self.how = how

    @staticmethod
    def volumes_from_str(volumes_as_str):
        if not volumes_as_str:
            return []
        volume_strs = [v.strip() for v in volumes_as_str.split(",")]
        return [DockerVolume.volume_from_str(_) for _ in volume_strs]

    @staticmethod
    def volume_from_str(as_str):
        if not as_str:
            raise ValueError("Failed to parse docker volume from %s" % as_str)
        parts = as_str.split(":", 2)
        kwds = dict(path=parts[0])
        if len(parts) == 2:
            if DockerVolume.__valid_how(parts[1]):
                kwds["how"] = parts[1]
            else:
                kwds["to_path"] = parts[1]
        elif len(parts) == 3:
            kwds["to_path"] = parts[1]
            kwds["how"] = parts[2]
        return DockerVolume(**kwds)

    @staticmethod
    def __valid_how(how):
        return how in ["ro", "rw"]

    def __str__(self):
        return ":".join([self.from_path, self.to_path, self.how])

def build_pull_command(
    tag,
    **kwds
):
    return command_list("pull", [tag], **kwds)


def build_singularity_exec_command(
    container_command,
    image,
    interactive=False,
    terminal=False,
    tag=None,
    binds="",
    contain="",
    containall="",
    home_directory="",
    ipc="",
    pid="",
    scratch_directory="",
    writable="",
    memory=DEFAULT_MEMORY,
    env_directives=[],
    working_directory=DEFAULT_WORKING_DIRECTORY,
    name=None,
    net=DEFAULT_NET,
    run_extra_arguments=DEFAULT_RUN_EXTRA_ARGUMENTS,
    singularity_cmd=DEFAULT_SINGULARITY_COMMAND,
    sudo=DEFAULT_SUDO,
    sudo_cmd=DEFAULT_SUDO_COMMAND,
    auto_rm=DEFAULT_AUTO_REMOVE,
    set_user=DEFAULT_SET_USER,
    host=DEFAULT_HOST,
):


    command_parts = _singularity_prefix(
        singularity_cmd=singularity_cmd,
    )
    command_parts.append("exec")
    #for bind in binds:
    #    command_parts.extend(["-B", shlex_quote(str(bind))])
    if contain:
        command_parts.append("-c")
    if containall:
        command_parts.append("-C")
    if home_directory:
        command_parts.extend(["-H",shlex_quote(home_directory)])
    if ipc:
        command_parts.append("-i")
    if pid:
        command_parts.append("-p")
    if scratch_directory:
        command_parts.extend(["-S",shlex_quote(scratch_directory)])
    if working_directory:
        command_parts.extend(["-W",shlex_quote(working_directory)])
    if writable:
        command_parts.append("-w")

    command_parts.append(shlex_quote(image))
    command_parts.append(container_command)

    return " ".join(command_parts)


def command_list(command, command_args=[], **kwds):
    """Return Docker command as an argv list."""
    command_parts = _singularity_prefix(**kwds)
    command_parts.append(command)
    command_parts.extend(command_args)
    return command_parts


def command_shell(command, command_args=[], **kwds):
    """Return Singularity command as a string for a shell."""
    return argv_to_str(command_list(command, command_args, **kwds))

def _singularity_prefix(
    singularity_cmd=DEFAULT_SINGULARITY_COMMAND,
    **kwds
):
    """Prefix to issue a singularity command."""
    command_parts = []
    command_parts.append(singularity_cmd)
    return command_parts
