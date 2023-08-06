#!/usr/bin/env python3
"""Delete all repos in the Github <user>-shadow org."""

from codekit.codetools import error
from codekit import codetools
from codekit import pygithub
from time import sleep
import argparse
import github
import logging
import os
import progressbar
import sys
import textwrap

logging.basicConfig()
logger = logging.getLogger('codekit')


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        prog='github-delete-shadow',
        description=textwrap.dedent("""Delete all repos in the GitHub
            <username>-shadow org"""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Part of codekit: https://github.com/lsst-sqre/sqre-codekit')
    parser.add_argument(
        '--org',
        required=True,
        help='GitHub Organization')
    parser.add_argument(
        '--token-path',
        default='~/.sq_github_token_delete',
        help='Use a token (made with github-auth) in a non-standard loction')
    parser.add_argument(
        '--token',
        default=None,
        help='Literal github personal access token string')
    parser.add_argument(
        '--limit',
        default=None,
        type=int,
        help='Maximum number of repos to delete')
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        default=os.getenv('DM_SQUARE_DEBUG'),
        help='Debug mode')
    parser.add_argument('-v', '--version', action=codetools.ScmVersionAction)
    return parser.parse_args()


def countdown_timer():
    """Show countdown bar"""
    widgets = ['Pause for panic: ', progressbar.ETA(), ' ', progressbar.Bar()]
    pbar = progressbar.ProgressBar(widgets=widgets, max_value=200).start()
    for i in range(200):
        pbar.update(i)
        sleep(0.1)
    pbar.finish()


def main():
    """Delete Github shadow org"""
    args = parse_args()
    orgname = args.org

    if args.debug:
        print('org:', orgname)

    g = pygithub.login_github(token_path=args.token_path, token=args.token)
    org = g.get_organization(orgname)
    # get all the repos
    repos = list(org.get_repos())[0:args.limit]

    print('Deleting all repos in', orgname)
    print('Now is the time to panic and Ctrl-C')

    countdown_timer()

    print('Here goes:')

    if args.debug:
        delay = 5
        print(delay, 'second gap between deletions')

    work = 0
    nowork = 0
    problems = []
    for r in repos:
        print('Next deleting:', r.full_name, '...',)

        if args.debug:
            sleep(delay)

        try:
            r.delete()
            work += 1
            print('ok')
        except github.GithubException as e:
            yikes = pygithub.CaughtGitError(r, e)
            problems.append(yikes)
            nowork += 1
            print('FAILED - does your token have delete_repo scope?')

    print('Done - Succeed:', work, 'Failed:', nowork)
    if problems:
        error("ERROR: {n} failures".format(n=str(len(problems))))

        for e in problems:
            error(e)

        sys.exit(1)

    if work:
        print('Consider deleting your privileged auth token', args.token_path)


if __name__ == '__main__':
    main()
