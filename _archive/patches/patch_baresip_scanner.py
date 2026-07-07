#!/usr/bin/env python3
import sys

src_path = sys.argv[1] if len(sys.argv) > 1 else "src/ua.c"

with open(src_path, "r") as f:
    content = f.read()

old = """\tua = uag_find(&msg->uri.user);
\tif (!ua) {
\t\tstruct le *le = uag.ual.head;
\t\tif (le) {
\t\t\tua = le->data;
\t\t\tinfo("ua: fallback to first UA for %r\\n",
\t\t\t     &msg->uri.user);
\t\t}
\t}
\tif (!ua) {"""

new = """\tua = uag_find(&msg->uri.user);
\tif (!ua) {
\t\tconst struct sip_hdr *ua_hdr = sip_msg_hdr(msg,
\t\t\t\t\t\t\t\t   SIP_HDR_USER_AGENT);
\t\tif (ua_hdr) {
\t\t\tchar ua[256];
\t\t\t(void)re_snprintf(ua, sizeof(ua), "%r", &ua_hdr->val);
\t\t\tif (strcasestr(ua, "pplsip") ||
\t\t\t    strcasestr(ua, "friendly-scanner") ||
\t\t\t    strcasestr(ua, "sipvicious") ||
\t\t\t    strcasestr(ua, "sipcli") ||
\t\t\t    strcasestr(ua, "sundayddr") ||
\t\t\t    strcasestr(ua, "iwar")) {
\t\t\t\twarning("ua: rejecting scanner: %r\\n",
\t\t\t\t\t&ua_hdr->val);
\t\t\t\t(void)sip_treply(NULL, uag_sip(), msg,
\t\t\t\t\t\t\t 404, "Not Found");
\t\t\t\treturn;
\t\t\t}
\t\t}
\t\tstruct le *le = uag.ual.head;
\t\tif (le) {
\t\t\tua = le->data;
\t\t\tinfo("ua: fallback to first UA for %r\\n",
\t\t\t     &msg->uri.user);
\t\t}
\t}
\tif (!ua) {"""

if old not in content:
    print("OLD STRING NOT FOUND")
    sys.exit(1)

content = content.replace(old, new)
with open(src_path, "w") as f:
    f.write(content)
print("SCANNER PATCH APPLIED")
