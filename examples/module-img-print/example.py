"""
Demonstrates pandoraPlugintools.print_img_module: render an image
module as XML, embedding a base64 PNG payload as a data URI.

Note: build the module as a plain dict with only a "value" key. If it
is built with init_module() instead, the template's default "data" key
is copied over "value" by the underlying print_module() call and the
image payload is lost.
"""

import pandoraPlugintools as ppt

# A tiny 1x1 transparent PNG, base64-encoded, used as a stand-in image.
tiny_png_b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)

img_module = {
    "name": "Screenshot",
    "type": "generic_data_string",
    "value": tiny_png_b64,
}

print(ppt.print_img_module(img_module))
