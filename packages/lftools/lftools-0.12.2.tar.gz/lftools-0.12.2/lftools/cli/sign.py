# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Script to GPG sign files."""

__author__ = 'Thanh Ha'


import subprocess
import sys
import tempfile

import click


@click.group()
@click.pass_context
def sign(ctx):
    """GPG sign files."""
    pass


@click.command(name='dir')
@click.argument('directory')
@click.pass_context
def directory(ctx, directory):
    """GPG signs all of the files in a directory."""
    status = subprocess.call(['sign', 'dir', directory])
    sys.exit(status)


@click.command(name='nexus')
@click.argument('nexus-repo-url')
@click.pass_context
def nexus(ctx, nexus_repo_url):
    """Fetch and GPG sign a Nexus repo."""
    status = subprocess.call(['sign', 'nexus', nexus_repo_url])
    sys.exit(status)


@click.command(name='deploy-nexus')
@click.argument('nexus-url', envvar='NEXUS_URL')
@click.argument('nexus-repo', envvar='NEXUS_REPO')
@click.argument('staging-profile-id', envvar='STAGING_PROFILE_ID')
@click.option(
    '-r', '--root-domain', type=str, default='org',
    help='Root download path of staging repo. (default org)')
@click.pass_context
def deploy_nexus(ctx, nexus_url, nexus_repo, staging_profile_id, root_domain):
    """Sign artifacts from a Nexus repo then upload to a staging repo.

    This is a porcelain command that ties the lftools sign and deploy tools
    together for easier use. It calls the sign-nexus command and then the
    deploy-nexus-stage command to create a signed staging repository in Nexus.
    """
    # wget does not appear to like to fully clone the root of a staging repo
    # as a workaround we have to at least give it 1 directory deep. Since most
    # LF projects are 'org' domain default is org but can be override with the
    # -r option.
    nexus_repo_url = "{}/content/repositories/{}/{}".format(nexus_url, nexus_repo, root_domain)
    sign_dir = tempfile.mkdtemp(prefix='gpg-signatures.')

    status = subprocess.call(['sign', 'nexus', '-d', sign_dir, nexus_repo_url])
    if status:
        sys.exit(status)

    status = subprocess.call(['deploy', 'nexus-stage', nexus_url, staging_profile_id, sign_dir])
    sys.exit(status)


sign.add_command(directory)
sign.add_command(nexus)
sign.add_command(deploy_nexus)
