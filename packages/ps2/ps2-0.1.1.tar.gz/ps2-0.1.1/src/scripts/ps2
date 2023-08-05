#!/usr/bin/env python
import time
import shlex
import click
import psutil

def show_process_info(process, output):
    info = process.as_dict()
    info["elapsed_time"] = time.time() - info["create_time"]
    info["commands"] = info["cmdline"]
    info["cmdline"] = ' '.join(shlex.quote(arg) for arg in info["commands"])
    line = output.format(**info)
    click.echo(line)

@click.command()
@click.argument("output", required=False)
def main(output):
    """The keywords can be used in output template:

    cmdline
    commands
    connections
    cpu_percent
    cpu_times
    create_time
    cwd
    elapsed_time
    environ
    exe
    gids
    memory_full_info
    memory_info
    memory_maps
    memory_percent
    name
    nice
    num_ctx_switches
    num_fds
    num_threads
    open_files
    pid
    ppid
    status
    terminal
    threads
    uids
    username

    The default output template is:

    "{pid}\\t{name}"

    """
    if output is None:
        output = "{pid}\t{name}"
    else:
        output = eval('"'+output+'"')
    for process in psutil.process_iter():
        try:
            show_process_info(process, output)
        except:
            pass


if __name__ == "__main__":
    main()
