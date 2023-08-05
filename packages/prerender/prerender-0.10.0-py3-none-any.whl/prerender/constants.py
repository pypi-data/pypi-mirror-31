import os

from .utils import is_yesish

BLOCKED_URLS = [
    "google-analytics.com",
    "api.mixpanel.com",
    "stats.g.doubleclick.net",
    "mc.yandex.ru",
    "use.typekit.net",
    "beacon.tapfiliate.com",
    "js-agent.newrelic.com",
    "api.segment.io",
    "woopra.com",
    "static.olark.com",
    "static.getclicky.com",
    "fast.fonts.com",
    "youtube.com\/embed",
    "cdn.heapanalytics.com",
    "googleads.g.doubleclick.net",
    "pagead2.googlesyndication.com",
    "fullstory.com/rec",
    "navilytics.com/nls_ajax.php",
    "log.optimizely.com/event",
    "hn.inspectlet.com",
    "tpc.googlesyndication.com",
    "partner.googleadservices.com",
    "hm.baidu.com",
]

if is_yesish(os.getenv('BLOCK_FONTS', '1')):
    BLOCKED_URLS.extend((
        ".ttf",
        ".eot",
        ".otf",
        ".woff",
    ))
