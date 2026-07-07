#!/usr/bin/env python3
import sys

src_path = sys.argv[1] if len(sys.argv) > 1 else "src/ua.c"

with open(src_path, "r") as f:
    content = f.read()

old = """\tua = uag_find(&msg->uri.user);
\tif (!ua) {
\t\twarning("ua: %r: UA not found: %r\\n",
\t\t\t&msg->from.auri, &msg->uri.user);
\t\t(void)sip_treply(NULL, uag_sip(), msg, 404, "Not Found");
\t\treturn;
\t}"""

new = """\tua = uag_find(&msg->uri.user);
\tif (!ua) {
\t\tstruct le *le = uag.ual.head;
\t\tif (le) {
\t\t\tua = le->data;
\t\t\tinfo("ua: fallback to first UA for %r\\n",
\t\t\t     &msg->uri.user);
\t\t}
\t}
\tif (!ua) {
\t\twarning("ua: %r: UA not found: %r\\n",
\t\t\t&msg->from.auri, &msg->uri.user);
\t\t(void)sip_treply(NULL, uag_sip(), msg, 404, "Not Found");
\t\treturn;
\t}"""

if old not in content:
    print("OLD STRING NOT FOUND")
    sys.exit(1)

content = content.replace(old, new)
with open(src_path, "w") as f:
    f.write(content)
print("PATCHED")
