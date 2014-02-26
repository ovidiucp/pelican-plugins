"""
Image Tag
---------
This implements a Liquid-style image tag for Pelican,
based on the octopress image tag [1]_

Syntax
------
{% lightbox [class name(s)] [http[s]:/]/path/to/image [width [height]] [title text | "title text" ["alt text"]] %}

Examples
--------
{% lightbox /images/ninja.png Ninja Attack! %}
{% lightbox left half http://site.com/images/ninja.png Ninja Attack! %}
{% lightbox left half http://site.com/images/ninja.png 150 150 "Ninja Attack!" "Ninja in attack posture" %}

Output
------
<a href="/images/ninja.png" class="example-image-link" data-lightbox="random"><img src="/images/ninja.png"></a>
<img class="left half" src="http://site.com/images/ninja.png" title="Ninja Attack!" alt="Ninja Attack!">
<img class="left half" src="http://site.com/images/ninja.png" width="150" height="150" title="Ninja Attack!" alt="Ninja in attack posture">

[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re
from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% lightbox [class name(s)] [http[s]:/]/path/to/image [width [height]] [title text | "title text" ["alt text"]] %}'

# Regular expression to match the entire syntax
ReImg = re.compile("""(?P<class>\S.*\s+)?(?P<src>(?:https?:\/\/|\/|\S+\/)\S+)(?:\s+(?P<width>\d+))?(?:\s+(?P<height>\d+))?(?P<title>\s+.+)?""")

# Regular expression to split the title and alt text
ReTitleAlt = re.compile("""(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')""")


@LiquidTags.register('lightbox')
def lightbox(preprocessor, tag, markup):
    attrs = None

    # Parse the markup string
    match = ReImg.search(markup)
    if match:
        attrs = dict([(key, val.strip())
                      for (key, val) in match.groupdict().iteritems() if val])
    else:
        raise ValueError('Error processing input. '
                         'Expected syntax: {0}'.format(SYNTAX))

    # Check if alt text is present -- if so, split it from title
    if 'title' in attrs:
        match = ReTitleAlt.search(attrs['title'])
        if match:
            attrs.update(match.groupdict())
        if not attrs.get('alt'):
            attrs['alt'] = attrs['title']

    # Generate a name for all lightbox images in this preprocessor
    # instance.
    if not hasattr(preprocessor, 'lightbox_attribute'):
        import uuid
        name = str(uuid.uuid1())
        preprocessor.lightbox_attribute = name

    link_attrs = {}
    link_attrs['data-lightbox'] = preprocessor.lightbox_attribute
    link_attrs['href'] = attrs['src']

    if attrs.get('title', None):
        link_attrs['title'] = attrs['title']

    link_attrs['class'] = 'example-image-link'
    if attrs.get('class', None):
        link_attrs['class'] = attrs['class'] + ' ' + link_attrs['class']

    attrs['class'] = 'example-image'

    # Return the formatted text
    return '<a {0}><img {1}></a>'.\
        format(' '.join('{0}="{1}"'.format(key, val)
                        for (key, val) in link_attrs.iteritems()),
               ' '.join('{0}="{1}"'.format(key, val)
                        for (key, val) in attrs.iteritems()))

#----------------------------------------------------------------------
# This import allows image tag to be a Pelican plugin
from liquid_tags import register
