#!/usr/bin/env python3
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#    implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import os

from pbr import version as pbr_version
from PIL import Image
from PIL import ImageDraw
import requests
import webcolors

GITHUB_STATS_URL = 'https://api.github.com/repos/%s/stats/%s'
GITHUB_ORG_REPOS_URL = 'https://api.github.com/orgs/%s/repos'
GITHUB_USER_REPOS_URL = 'https://api.github.com/users/%s/repos'
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 200


def get_version():
    """Get the version of this program."""
    version_info = pbr_version.VersionInfo('sparkler')
    return 'sparkler %s' % version_info.version_string()


def _send_request(url):
    """Sends an HTTP request and adds auth info if available.

    Set the environment variables GH_USER and GH_TOKEN to use authentication
    with API calls to help avoid unauthenticated rate limiting.
    """
    user = os.environ.get('GH_USER')
    token = os.environ.get('GH_TOKEN')

    if user and token:
        return requests.get(url, auth=(user, token))

    return requests.get(url)


def get_commit_activity(repo):
    """Gets the raw commit activity from GitHub

    :param repo: The GitHub org or org/name to query.
    :returns: JSON data per day by week for the last year.
    """
    result = [0 for i in range(52)]
    repos = []
    try:
        if '/' in repo:
            # We're getting a specific repo
            repos = [repo]
        else:
            # We need to get the list of org's repos
            r = _send_request(GITHUB_ORG_REPOS_URL % repo)
            if r.status_code != 200:
                # Must be a user and not an org
                r = _send_request(GITHUB_USER_REPOS_URL % repo)
                if r.status_code != 200:
                    # Well, we tried
                    return result
            for rep in r.json():
                if not rep['fork']:
                    repos.append(rep['full_name'])

        for rep in repos:
            r = _send_request(GITHUB_STATS_URL % (rep, 'commit_activity'))
            data = r.json()
            for i in range(len(data)):
                result[i] += data[i].get('total', 0)
    except Exception as e:
        print('Error getting repo stats: %s' % e)

    return result


def generate_image(bg, line, data):
    """Generates the sparkline graph.

    This will create a 400x100 image with the data laid out inside that space.
    :param bg: The background color to use.
    :param line: The line color to use.
    :param data: A list of data points.
    :returns: The created image.
    """
    # We want a 10px buffer on the ends
    x_increment = (IMAGE_WIDTH - 20) / (len(data) - 1)
    low = 999999999
    high = 0
    for datum in data:
        if datum > high:
            high = datum
        if datum < low:
            low = datum

    # Create our image
    im = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), (
                   bg.red, bg.green, bg.blue))
    draw = ImageDraw.Draw(im)

    line_color = (line.red, line.green, line.blue)
    last = 0
    pos = 10
    for point in data:
        # Calculate the position within the height accounting for the top and
        # bottom buffers.
        if high == low:
            percent_in_range = .5
        else:
            percent_in_range = (point - low) / (high - low)
        y = ((IMAGE_HEIGHT - 20) * percent_in_range) + 10
        if last > 0:
            draw.line([pos, IMAGE_HEIGHT - last, pos + x_increment,
                       IMAGE_HEIGHT - y],
                      width=5, fill=line_color)
            pos += x_increment
        last = y

    return im


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        action='version',
        version=get_version(),
    )
    parser.add_argument(
        '--background',
        default='white',
        help='The background color of the sparkline image.',
    )
    parser.add_argument(
        '--line',
        default='black',
        help='The sparkline image line color.',
    )
    parser.add_argument(
        'repo',
        help='The GitHub org/repo to report on. ("org/repo" will get '
             'stats for a specific repo, "org" will get the combined '
             'stats for all of the orgs repos)',
    )
    parser.add_argument(
        'outfile',
        help='The file name for the generated image.\n'
             'Note: Due to current library issues, this must be a jpg.',
    )
    args = parser.parse_args()

    line_color = webcolors.name_to_rgb(args.line)
    bg_color = webcolors.name_to_rgb(args.background)
    data = get_commit_activity(args.repo)
    im = generate_image(bg_color, line_color, data)

    with open(args.outfile, 'w') as outfile:
        # Scale down with antialiasing to smooth the image
        im.thumbnail((400, 400), Image.ANTIALIAS)
        im.save(outfile)


if __name__ == '__main__':
    main()
