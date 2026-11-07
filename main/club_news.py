"""Bounded public-source import. No football API, article text or image copying."""
import json
import logging
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

import requests
from django.db import transaction
from django.utils import timezone
from .models import ClubNews, ClubNewsSync

OFFICIAL = 'https://www.amedspor.com.tr/news'
RSS = 'https://www.aspor.com.tr/rss/amed-sportif-faaliyetler.xml'
log = logging.getLogger(__name__)


def allowed_url(url, official=False):
    parsed = urlsplit(url)
    hosts = {'www.amedspor.com.tr', 'amedspor.com.tr'} if official else {'www.aspor.com.tr'}
    return parsed.scheme == 'https' and parsed.hostname in hosts and not parsed.username and not parsed.password and parsed.port in (None, 443)


def clean(text, limit=200):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]*>', '', text or ''))).strip()[:limit]


def parse_rss(body, now):
    if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
        raise ValueError('unsupported_xml')
    result = []
    for item in ElementTree.fromstring(body).findall('./channel/item')[:60]:
        url = (item.findtext('link') or '').strip()
        title = clean(item.findtext('title'))
        try:
            published = parsedate_to_datetime(item.findtext('pubDate') or '')
            if published.tzinfo is None:
                continue
        except (ValueError, TypeError):
            continue
        if not title or not allowed_url(url) or published > now or published < now - timedelta(days=120):
            continue
        # An RSS headline can contain a transfer rumour. It always stays press news.
        result.append(dict(source_url=url, source='A Spor', title=title,
            summary='A Spor’un Amedspor gündemindeki haberi. Açıklamalar ve ayrıntılar kaynak sayfasında.',
            kind='news', published_at=published, is_official=False))
    return result


class OfficialIndex(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            url = urljoin(OFFICIAL, dict(attrs).get('href', ''))
            if allowed_url(url, True) and urlsplit(url).path.startswith('/news/') and url not in self.links:
                self.links.append(url)


class ArticleMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.in_json = False
        self.json_parts = []
        self.texts = []
        self.in_heading = False
        self.heading = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta[attrs.get('property', attrs.get('name', ''))] = attrs.get('content', '')
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_json = True
        if tag == 'h1':
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_json = False
        if tag == 'h1':
            self.in_heading = False

    def handle_data(self, data):
        if self.in_json:
            self.json_parts.append(data)
        elif clean(data):
            self.texts.append(clean(data, 300))
            if self.in_heading:
                self.heading += data


def parse_official(url, html, now):
    if not allowed_url(url, True):
        return None
    parser = ArticleMetadata()
    parser.feed(html)
    title = parser.meta.get('og:title', '')
    date = parser.meta.get('article:published_time', '')
    section = parser.meta.get('article:section', '').lower()
    for part in parser.json_parts:
        try:
            data = json.loads(part)
            entries = data if isinstance(data, list) else data.get('@graph', [data])
            for entry in entries:
                if not isinstance(entry, dict) or entry.get('@type') not in ('NewsArticle', 'Article'):
                    continue
                title = title or entry.get('headline', '')
                date = date or entry.get('datePublished', '')
                section = section or str(entry.get('articleSection', '')).lower()
        except (ValueError, AttributeError):
            continue
    title = title or parser.heading
    # The official site also publishes a visible, explicitly year-stamped date.
    if not date:
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        for text in parser.texts:
            match = re.fullmatch(r'(\d{1,2}) (\w+) (\d{4}), (\d{2}):(\d{2})', text)
            if match and match[2] in months:
                try:
                    date = datetime(int(match[3]), months.index(match[2]) + 1, int(match[1]), int(match[4]), int(match[5]), tzinfo=dt_timezone(timedelta(hours=3))).isoformat()
                except ValueError:
                    pass
                break
    if not section and clean(parser.heading) in parser.texts:
        index = parser.texts.index(clean(parser.heading))
        if index > 0:
            section = parser.texts[index - 1].lower()
    try:
        published = datetime.fromisoformat(date.replace('Z', '+00:00'))
        if published.tzinfo is None:
            return None
    except (ValueError, TypeError):
        return None
    if not clean(title) or published > now or published < now - timedelta(days=365):
        return None
    # Only explicit official categories or explicit departure announcements classify.
    kind = 'transfer' if section == 'transfer' else 'news'
    if section in ('ayrilik', 'ayrılık'):
        kind = 'departure'
    summary = {'transfer': 'Amedspor’un resmî transfer duyurusu. Açıklamanın ayrıntıları kulübün sitesinde.',
        'departure': 'Amedspor’un resmî ayrılık duyurusu. Açıklamanın ayrıntıları kulübün sitesinde.',
        'news': 'Amedspor’un resmî kulüp duyurusu. Açıklamanın ayrıntıları kulübün sitesinde.'}[kind]
    return dict(source_url=url, source='Amedspor', title=clean(title), summary=summary,
        kind=kind, published_at=published, is_official=True)


def download(url):
    # All URLs are fixed or validated before calling; redirects cannot escape allowlist.
    with requests.get(url, headers={'User-Agent': 'Rumep-News-Link-Reader/1.0 (+https://rumep.net)'},
            timeout=(5, 12), allow_redirects=False, stream=True) as response:
        response.raise_for_status()
        if response.is_redirect:
            raise ValueError('source_redirect')
        chunks, length = [], 0
        for chunk in response.iter_content(32768):
            length += len(chunk)
            if length > 1500000:
                raise ValueError('source_too_large')
            chunks.append(chunk)
        return b''.join(chunks)


def sync_news(fetch=download):
    now = timezone.now()
    with transaction.atomic():
        state, _ = ClubNewsSync.objects.get_or_create(key='public-news', defaults={'next_attempt_at': now})
        state = ClubNewsSync.objects.select_for_update().get(pk=state.pk)
        if state.next_attempt_at > now:
            return 0
        state.next_attempt_at = now + timedelta(minutes=30)
        state.save(update_fields=['next_attempt_at'])
    total, successes, errors = 0, 0, []
    def store(records):
        nonlocal total
        for record in records:
            url = record.pop('source_url')
            ClubNews.objects.update_or_create(source_url=url, defaults=record)
            total += 1
    try:
        store(parse_rss(fetch(RSS), now))
        successes += 1
    except Exception as exc:
        errors.append('rss:' + type(exc).__name__)
    try:
        index = OfficialIndex()
        index.feed(fetch(OFFICIAL).decode('utf-8', errors='replace'))
        # Scan only a bounded first page. Existing old links are not repeatedly downloaded.
        urls = index.links[:20]
        known = set(ClubNews.objects.filter(source_url__in=urls).values_list('source_url', flat=True))
        candidates = [url for url in urls if url not in known][:6]
        for url in candidates:
            try:
                record = parse_official(url, fetch(url).decode('utf-8', errors='replace'), now)
                if record:
                    store([record])
            except Exception as exc:
                errors.append('official_article:' + type(exc).__name__)
        successes += 1
    except Exception as exc:
        errors.append('official:' + type(exc).__name__)
    ClubNewsSync.objects.filter(pk='public-news').update(
        last_success_at=now if successes else state.last_success_at,
        last_error=','.join(errors)[:100])
    # A bounded metadata archive; never store source images or full article bodies.
    keep = list(ClubNews.objects.order_by('-published_at').values_list('pk', flat=True)[:300])
    ClubNews.objects.exclude(pk__in=keep).delete()
    if errors:
        log.warning('club_news partial sync: %s', ','.join(errors))
    return total
