# -*- coding: utf-8 -*-
""" Copyright (c) 2008 Martin Scharrer <martin@scharrer-online.de>
    v0.1 - Oct 2008
    This is Free Software under the GPL v3!

    $Id: macro.py 17137 2018-04-16 19:58:39Z rjollos $
"""

from trac.config import Option
from trac.core import Component, implements
from trac.util.html import html as tag
from trac.wiki.api import IWikiMacroProvider
from trac.web.href import Href

from tracadvparseargs import parse_args


class GoogleStaticMapMacro(Component):
    """ Provides a static Google Map as HTML image.

Website: http://trac-hacks.org/wiki/GoogleStaticMapMacro

`$Id: macro.py 17137 2018-04-16 19:58:39Z rjollos $`

== Description ==

This macro uses the
[http://code.google.com/apis/maps/documentation/staticmaps/ Google Map API] to
include '''static''' images of maps.
'''Static''' means that is is only a simple image without any user interaction
not the usual feature-rich dynamic map on http://maps.google.com/. The positive
side is that no javascript is needed to display the map image.

For a dynamic Google map use
[http://trac-hacks.org/wiki/GoogleMapMacro GoogleMapMacro].

The maximum size supported by Google is 640x640 pixels. If a bigger width or
height is requested it will be reduced to 640px.

'''Important:''' A different Google Map API key is needed for every web domain
which can be
[http://code.google.com/apis/maps/signup.html get for free from Google].

== Usage & Examples ==
=== Parameters ===
See http://code.google.com/apis/maps/documentation/staticmaps/#URL_Parameters
for all supported arguments.
In addition the image title can be set using a `title` argument.

The map location must be given in geographic coordinates, not as address.
Please note that the format `center=X:Y` must be used, not `center=X,Y` as
described in the above web site, due to the way trac parses the macro.

For example:
{{{
[[GoogleStaticMap(center=50.805935:10.349121,zoom=5,size=400x400)]]
}}}

will result in the following map image:

[[Image(http://maps.google.com/staticmap?center=50.805935%2C10.349121&zoom=5&size=400x400&key=ABQIAAAAMwTA9mkyZbDS6QMcxvwm2BQk7JAK84r7ycdvlw9atwcq_yt-SxQd58w7cbhU8Fvb5JRRi4sH8vpPEQ,nolink)]]


=== Markers ===
You can add markers to the static map using the '`markers`' argument.
The format is
'`markers={latitude}:{longitude}:{size}{color}{alphanumeric-character}`',
e.g.: `markers=50.805935:10.349121:bluea`, creates a blue marker labeled with
'A' at 50.805935,10.349121.
Multiple marker declarations are separated using the '`|`' letter.

So,
{{{
[[GoogleStaticMap(center=50.805935:10.349121,zoom=5,size=400x400,markers=50.805935:10.349121:bluea|50.000000:10.000000:greenb|49.046195:12.117577:yellowc)]]
}}}
will result in the following map image:

[[Image(http://maps.google.com/staticmap?center=50.805935%2C10.349121&zoom=5&size=400x400&markers=50.805935%2c10.349121%2cbluea|50.000000%2c10.000000%2cgreenb|49.046195%2c12.117577%2cyellowc&key=ABQIAAAAMwTA9mkyZbDS6QMcxvwm2BQk7JAK84r7ycdvlw9atwcq_yt-SxQd58w7cbhU8Fvb5JRRi4sH8vpPEQ,nolink)]]

    """
    implements(IWikiMacroProvider)

    key = Option('googlestaticmap', 'api_key', None, "Google Maps API key")

    size = Option('googlestaticmap', 'default_size',
                  "300x300", "Default size for map")

    hl = Option('googlestaticmap', 'default_language',
                "en", "Default language for map")

    api = Option('googlestaticmap', 'default_api_version', "2",
                 "Default version of Google Static Map API to be used")

    allowed_args = ['center', 'zoom', 'size', 'format', 'maptype',
                    'markers', 'path', 'span', 'frame', 'hl', 'key',
                    'sensor', 'visible']

    google_url = {
        '1': 'http://maps.google.com/staticmap',
        '2': 'http://maps.google.com/maps/api/staticmap',
    }

    def get_macros(self):
        yield 'GoogleStaticMap'

    def get_macro_description(self, name):
        return self.__doc__

    def expand_macro(self, formatter, name, content, args=None):
        content = content.replace('\n', ',')
        args, kwargs = parse_args(
            content, multi=['markers', 'path', 'visible'])

        # HTML arguments used in Google Maps URL
        hargs = {
            'center': "50.805935,10.349121",
            # 'zoom'   : "6",
            'key': self.key,
            'size': self.size,
            'hl': self.hl,
            'sensor': 'false',
        }

        # Set API version
        api = kwargs.get('api', self.api)
        if api not in self.google_url:
            api = self.api

        # Delete default zoom if user provides 'span' argument:
        if 'span' in kwargs:
            del hargs['zoom']

        # Copy given macro arguments to the HTML arguments
        for k, v in kwargs.iteritems():
            if k in self.allowed_args and v:
                hargs[k] = v

        # Check if API key exists. TODO: check if old API still needs the key
        if 'key' not in hargs and api == '1':
            raise TracError("No Google Maps API key given!\n")

        # Get height and width
        try:
            if 'x' not in hargs['size']:
                hargs['size'] = hargs['size'] + 'x' + hargs['size']
            width, height = hargs['size'].split('x')
            if int(height) < 1:
                height = "1"
            elif int(height) > 640:
                height = "640"
            if int(width) < 1:
                width = "1"
            elif int(width) > 640:
                width = "640"
            hargs['size'] = "%sx%s" % (width, height)
        except:
            raise TracError(
                "Invalid `size` argument. Should be `<width>x<height>`.")

        if api == '1':
            # Correct separator for 'center' argument because comma isn't
            # allowed in macro arguments.
            hargs['center'] = hargs['center'].replace(':', ',')
            if 'markers' in hargs:
                hargs['markers'] = [marker.replace(
                    ':', ',') for marker in hargs['markers']]

        # Build URL
        src = Href(self.google_url.get(api, ''))(**hargs)

        title = alt = "Google Static Map at %s" % hargs['center']
        # TODO: provide sane alternative text and image title

        if 'title' in kwargs:
            title = kwargs['title']

        return tag.img(
            class_="googlestaticmap",
            src=src,
            title=title,
            alt=alt,
            height=height,
            width=width,
        )
