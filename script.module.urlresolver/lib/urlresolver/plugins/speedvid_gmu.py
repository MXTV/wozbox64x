# -*- coding: utf-8 -*-
"""
speedvid urlresolver plugin
Copyright (C) 2017 jsergio

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import re, math, time
from random import *
from lib import helpers, aa_decoder
from urlresolver import common
from urlresolver.resolver import ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

net = common.Net()

def get_media_url(url, media_id):
    headers = {'User-Agent': common.RAND_UA}
    html = net.http_GET(url, headers=headers).content
    
    if html:
        html = html.encode('utf-8')
        packed = helpers.get_packed_data(html)
        aa_text = re.search("""(ﾟωﾟﾉ\s*=\s*/｀ｍ´\s*）ﾉ\s*~┻━┻\s*//\*´∇｀\*/\s*\['_'\]\s*;\s*o\s*=\s*\(ﾟｰﾟ\)\s*=_=3;.+?)</SCRIPT>""", html, re.I)
        if aa_text:
            try:
                aa_decoded = aa_decoder.AADecoder(re.sub('\(+ﾟДﾟ\)+\[ﾟoﾟ\]\)*\+\s*', '(ﾟДﾟ)[ﾟoﾟ]+ ', aa_text.group(1))).decode()
                href = re.search("""href\s*=\s*['"]([^"']+)""", aa_decoded)
                if href:
                    href = href.group(1)
                    if href.startswith("http"): location = href
                    elif href.startswith("//"): location = "http:%s" % href
                    else: location = "http://www.speedvid.net/%s" % href
                    headers.update({'Referer': url, 'Cookie': str((int(math.floor((900-100)*random())+100))*(int(time.time()))*(128/8))})
                    _html = net.http_GET(location, headers=headers).content
                    sources = helpers.scrape_sources(_html, patterns=['''file:["'](?P<url>(?!http://s(?:13|28|35|51|57|58|59|89))[^"']+)'''])
                    if sources:
                        del headers['Cookie']
                        headers.update({'Referer': location})
                        return helpers.pick_source(sources) + helpers.append_headers(headers)
            except Exception as e:
                raise ResolverError(e)
        
    raise ResolverError('File not found')
