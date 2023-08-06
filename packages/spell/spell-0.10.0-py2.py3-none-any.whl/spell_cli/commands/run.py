# -*- coding: utf-8 -*-
import os
import subprocess

import click
import git

from api_client.runs_client import RunsClient
from api_client.workspaces_client import WorkspacesClient
from spell_cli.api_constants import (
    get_machine_types,
    get_machine_type_default,
    get_frameworks,
)
from spell_cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
    SPELL_INVALID_COMMIT,
    SPELL_BAD_REPO_STATE,
)
from spell_cli.commands.keys import cli_key_path
from spell_cli.commands.logs import logs
from spell_cli.log import logger
from spell_cli.utils import LazyChoice, git_utils, parse_utils
from spell_cli.utils.parse_utils import ParseException


@click.command(name="run",
               short_help="Execute a new run for current repo")
@click.argument("command")
@click.argument("args", nargs=-1)
@click.option("-t", "--machine-type",
              type=LazyChoice(get_machine_types), default=get_machine_type_default,
              help="Machine type to run on")
@click.option("--pip", "pip_packages",
              help="Dependency to install using pip", multiple=True)
@click.option("--apt", "apt_packages",
              help="Dependency to install using apt", multiple=True)
@click.option("--from", "docker_image",
              help="Dockerfile on docker hub to run from")
@click.option("--framework",
              help="Machine learning framework to use",
              type=LazyChoice(get_frameworks))
@click.option("--conda-env", help="Name of conda environment name to activate.")
@click.option("--conda-file",
              help="Path to conda environment file, defaults to ./environment.yml \
                    when --conda-env is specified",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
              default=None)
@click.option("-b", "--background", is_flag=True,
              help="Do not print logs")
@click.option("-c", "--commit-ref", default="HEAD",
              help="Git commit hash to run")
@click.option("-e", "--env", "envvars", multiple=True,
              help="Add an environment variable to the run")
@click.option("-m", "--mount", "raw_resources", multiple=True,
              help="Attach a resource to the run from the result of a previous run. "
                   "Must provide both the id of the previous run and the path to mount, "
                   "e.g. --mount runs/42:/mnt/data")
@click.option("-f", "--force-sync", is_flag=True,
              help="Submit with uncommitted changes")
@click.option("-v", "--verbose", is_flag=True,
              help="Print additional information")
@click.pass_context
@git_utils.get_git_repo
def run(ctx, git_repo, command, args, machine_type, pip_packages, apt_packages,
        docker_image, framework, commit_ref, envvars, raw_resources, background,
        conda_env, conda_file, force_sync, verbose):
    logger.info("starting run command")

    cmd_with_args = " ".join((command,) + args)

    try:
        root_commit = next(git_repo.iter_commits(max_parents=0))
    except ValueError:
        click.echo(click.wrap_text("The current repository has no commits! Please commit all files necessary to run "
                                   "this project before continuing."), err=True)
        raise ExitException("No commits found", SPELL_BAD_REPO_STATE)

    # resolve the commit ref to its sha hash
    try:
        commit_hash = git_repo.commit(commit_ref).hexsha
    except git.BadName:
        raise ExitException('Could not resolve commit "{}"'.format(commit_ref), SPELL_INVALID_COMMIT)

    git_path = git_repo.working_dir
    workspace_name = os.path.basename(git_path)

    # hit the API for new workspace info
    token = ctx.obj["config_handler"].config.token
    workspace_client = WorkspacesClient(token=token, **ctx.obj["client_args"])
    with api_client_exception_handler():
        logger.info("Retrieving new workspace information from Spell")
        workspace = workspace_client.new_workspace(str(root_commit), workspace_name, "")

    workspace_id = workspace.id
    git_remote_url = workspace.git_remote_url
    # fail if staged/unstaged changes, and warn if files are untracked
    if not force_sync and (git_utils.has_staged(git_repo) or git_utils.has_unstaged(git_repo)):
        raise ExitException("Uncommitted changes to tracked files detected -- please commit first",
                            SPELL_BAD_REPO_STATE)
    if not force_sync and git_utils.has_untracked(git_repo):
        click.confirm("There are some untracked files in this repo. They won't be available on this run."
                      "\n{}\nContinue the run anyway?".format(git_utils.get_untracked(git_repo)),
                      default=True, abort=True)

    # use specific SSH key if one is in the spell directory
    gitenv = os.environ.copy()
    ssh_key_path = cli_key_path(ctx.obj["config_handler"])
    if os.path.isfile(ssh_key_path) and "GIT_SSH_COMMAND" not in gitenv:
        ssh_cmd = gitenv.get("GIT_SSH", "ssh")
        gitenv["GIT_SSH_COMMAND"] = "{} -i {}".format(ssh_cmd, ssh_key_path)

    # push to the spell remote
    refspec = "{}:{}".format(git_repo.active_branch, commit_hash)
    git_push = ["git", "push", git_remote_url, refspec]
    try:
        subprocess.check_call(git_push, cwd=git_path, env=gitenv)
    except subprocess.CalledProcessError:
        msg = "Push to Spell remote failed"
        if git_utils.git_version() < (2, 3):
            msg += ", Git 2.3 or newer is required"
        raise ExitException(msg)

    source_spec = sum(1 for x in (framework, docker_image, conda_env) if x is not None)
    if source_spec > 1:
        raise ExitException("Only one of the following options can be specified: --framework, --from, --conda-env",
                            SPELL_INVALID_CONFIG)

    if docker_image is not None and (pip_packages or apt_packages):
        raise ExitException("--apt or --pip cannot be specified when --from is provided."
                            " Please install packages from the specified Dockerfile.",
                            SPELL_INVALID_CONFIG)

    if conda_file is not None and conda_env is None:
        raise ExitException("A conda environment name is required if a conda environment file is specified.",
                            SPELL_INVALID_CONFIG)
    if conda_env is not None and conda_file is None:
        if not os.path.exists("environment.yml"):
            raise ExitException("Default value for \"--conda-file\" invalid: Path \"environment.yml\" does not exist.",
                                SPELL_INVALID_CONFIG)
        conda_file = os.path.relpath(os.path.join(os.getcwd(), "environment.yml"), git_path)
    if conda_env is not None and pip_packages:
        raise ExitException("--pip cannot be specified when using a conda environment. You can include "
                            "the pip installs in the conda environment file instead.")
    # Read the conda environment file
    conda_env_contents = None
    if conda_file is not None:
        with open(conda_file) as conda_f:
            conda_env_contents = conda_f.read()

    # extract envvars into a dictionary
    curr_envvars = parse_utils.parse_env_vars(envvars)

    # extract attached resources
    try:
        attached_resources = parse_utils.parse_attached_resources(raw_resources)
    except ParseException as e:
        raise ExitException(click.wrap_text(
            "Incorrect formatting of mount '{}', it must be <resource_path>[:<mount_path>]".format(e.token)),
            SPELL_INVALID_CONFIG)

    # Get relative path from git-root to CWD.
    relative_path = os.path.relpath(os.getcwd(), git_path)

    # execute the run
    token = ctx.obj["config_handler"].config.token
    runs_client = RunsClient(token=token, **ctx.obj["client_args"])
    logger.info("sending run request to api")
    with api_client_exception_handler():
        run = runs_client.run(machine_type,
                              command=cmd_with_args,
                              workspace_id=workspace_id,
                              commit_hash=commit_hash,
                              cwd=relative_path,
                              pip_packages=pip_packages,
                              apt_packages=apt_packages,
                              docker_image=docker_image,
                              framework=framework,
                              envvars=curr_envvars,
                              attached_resources=attached_resources,
                              conda_file=conda_env_contents,
                              conda_name=conda_env,
                              run_type="user")

    click.echo("✨ Casting spell #{}…".format(run.id))
    if background:
        click.echo("View logs with `spell logs {}`".format(run.id))
    else:
        click.echo("✨ Stop viewing logs with ^C")
        ctx.invoke(logs, run_id=str(run.id), follow=True, verbose=verbose)
