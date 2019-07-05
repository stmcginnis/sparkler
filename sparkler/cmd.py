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

from pbr import version as pbr_version
from PIL import Image
from PIL import ImageDraw
import requests
import webcolors

GITHUB_STATS_URL = 'https://api.github.com/repos/%s/stats/%s'
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 100


def get_version():
    """Get the version of this program."""
    version_info = pbr_version.VersionInfo('sparkler')
    return 'sparkler %s' % version_info.version_string()


def get_commit_activity(repo):
    """Gets the raw commit activity from GitHub

    :param repo: The GitHub org/name to query.
    :returns: JSON data per day by week for the last year.
    """
    result = []
    data = requests.get(GITHUB_STATS_URL % (repo, 'commit_activity'))
    data = data.json()
    for week in data:
        result.append(week.get('total', 0))
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
        help='The GitHub org/repo to report on.',
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
        im.save(outfile)


if __name__ == '__main__':
    main()
