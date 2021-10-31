from lxml import etree
from os import path
import io

NAMESPACES = {'XML': 'http://www.w3.org/XML/1998/namespace',
              'EPUB': 'http://www.idpf.org/2007/ops',
              'DAISY': 'http://www.daisy.org/z3986/2005/ncx/',
              'OPF': 'http://www.idpf.org/2007/opf',
              'CONTAINERS': 'urn:oasis:names:tc:opendocument:xmlns:container',
              'DC': 'http://purl.org/dc/elements/1.1/',
              'XHTML': 'http://www.w3.org/1999/xhtml'}

IMAGE_MEDIA_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml']


class Pathfinder:
    '''
    Object finding paths to stylesheets and files in the spine of
    the unpacked .epub file
    '''
    def __init__(self, book_dir=None) -> None:
        self.set_book_dir(book_dir=book_dir)

    def set_book_dir(self, book_dir=None) -> None:
        self.book_dir = book_dir

    def search(self) -> None:
        self.spine = []
        self.stylesheets = []
        self._items = {}
        self._load_container()
        self._load_opf_file()
        for i in range(len(self.spine)):
            self.spine[i] =\
                path.normpath(path.join(self._opf_dir, self.spine[i]))
        for i in range(len(self.stylesheets)):
            self.stylesheets[i] =\
                path.normpath(path.join(self._opf_dir, self.stylesheets[i]))

    def _parse_string(self, str) -> None:
        try:
            tree = etree.parse(io.BytesIO(str.encode('utf-8')))
        except etree.Error:
            tree = etree.parse(io.BytesIO(str))

        return tree

    def _load_container(self) -> None:
        meta_inf = self._read('META-INF/container.xml')
        tree = self._parse_string(meta_inf)

        for root_file in \
            tree.findall('//xmlns:rootfile[@media-type]',
                         namespaces={'xmlns': NAMESPACES['CONTAINERS']}):
            if root_file.get('media-type') == 'application/oebps-package+xml':
                self._opf_file = root_file.get('full-path')
                self._opf_dir = path.dirname(self._opf_file)

    def _read(self, name) -> str:
        file = open(path.join(self.book_dir, name), "r")
        content = file.read()
        file.close()
        return content

    def _load_opf_file(self):
        try:
            content = self._read(self._opf_file)
        except KeyError:
            raise FileNotFoundError(-1, 'Can not find container file')

        self.container = self._parse_string(content)

        #self._load_metadata()
        self._load_manifest()
        self._load_spine()
        #self._load_guide()

    '''def _load_metadata(self):
        container_root = self.container.getroot()

        # get epub version
        self.book.version = container_root.get('version', None)

        # get unique-identifier
        if container_root.get('unique-identifier', None):
            self.book.IDENTIFIER_ID = container_root.get('unique-identifier')

        # get xml:lang
        # get metadata
        metadata = self.container.find('{%s}%s' % (NAMESPACES['OPF'],
                                       'metadata'))

        nsmap = metadata.nsmap
        nstags = dict((k, '{%s}' % v) for k, v in six.iteritems(nsmap))
        default_ns = nstags.get(None, '')

        nsdict = dict((v, {}) for v in nsmap.values())

        def add_item(ns, tag, value, extra):
            if ns not in nsdict:
                nsdict[ns] = {}

            values = nsdict[ns].setdefault(tag, [])
            values.append((value, extra))

        for t in metadata:
            if not etree.iselement(t) or t.tag is etree.Comment:
                continue
            if t.tag == default_ns + 'meta':
                name = t.get('name')
                others = dict((k, v) for k, v in t.items())

                if name and ':' in name:
                    prefix, name = name.split(':', 1)
                else:
                    prefix = None

                add_item(t.nsmap.get(prefix, prefix), name, t.text, others)
            else:
                tag = t.tag[t.tag.rfind('}') + 1:]

                if t.prefix and t.prefix.lower() == 'dc'\
                   and tag == 'identifier':
                    _id = t.get('id', None)

                    if _id:
                        self.book.IDENTIFIER_ID = _id

                others = dict((k, v) for k, v in t.items())
                add_item(t.nsmap[t.prefix], tag, t.text, others)

        self.book.metadata = nsdict

        titles = self.book.get_metadata('DC', 'title')
        if len(titles) > 0:
            self.book.title = titles[0][0]

        for value, others in self.book.get_metadata('DC', 'identifier'):
            if others.get('id') == self.book.IDENTIFIER_ID:
                self.book.uid = value'''

    def _load_manifest(self):
        for r in self.container.find('{%s}%s' % (NAMESPACES['OPF'],
                                     'manifest')):
            if r is not None and r.tag != '{%s}item' % NAMESPACES['OPF']:
                continue
            href = r.get('href')
            self._items[r.get('id')] = href
            if r.get('media-type') == 'text/css':
                self.stylesheets.append(href)

            '''media_type = r.get('media-type')
            _properties = r.get('properties', '')

            if _properties:
                properties = _properties.split(' ')
            else:
                properties = []

            # people use wrong content types
            if media_type == 'image/jpg':
                media_type = 'image/jpeg'

            if media_type == 'application/x-dtbncx+xml':
                ei = EpubNcx(uid=r.get('id'), file_name=parse.unquote(r.get('href')))

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.file_name))
            if media_type == 'application/smil+xml':
                ei = EpubSMIL(uid=r.get('id'), file_name=parse.unquote(r.get('href')))

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.file_name))
            elif media_type == 'application/xhtml+xml':
                if 'nav' in properties:
                    ei = EpubNav(uid=r.get('id'), file_name=parse.unquote(r.get('href')))

                    ei.content = self.read_file(zip_path.join(self.opf_dir, r.get('href')))
                elif 'cover' in properties:
                    ei = EpubCoverHtml()

                    ei.content = self.read_file(zip_path.join(self.opf_dir, parse.unquote(r.get('href'))))
                else:
                    ei = EpubHtml()

                    ei.id = r.get('id')
                    ei.file_name = parse.unquote(r.get('href'))
                    ei.media_type = media_type
                    ei.media_overlay = r.get('media-overlay', None)
                    ei.media_duration = r.get('duration', None)
                    ei.content = self.read_file(zip_path.join(self.opf_dir, ei.get_name()))
                    ei.properties = properties
            elif media_type in IMAGE_MEDIA_TYPES:
                if 'cover-image' in properties:
                    ei = EpubCover(uid=r.get('id'), file_name=parse.unquote(r.get('href')))

                    ei.media_type = media_type
                    ei.content = self.read_file(zip_path.join(self.opf_dir, ei.get_name()))
                else:
                    ei = EpubImage()

                    ei.id = r.get('id')
                    ei.file_name = parse.unquote(r.get('href'))
                    ei.media_type = media_type
                    ei.content = self.read_file(zip_path.join(self.opf_dir, ei.get_name()))
            else:
                # different types
                ei = EpubItem()

                ei.id = r.get('id')
                ei.file_name = parse.unquote(r.get('href'))
                ei.media_type = media_type

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.get_name()))

            self.book.add_item(ei)'''

        # read nav file if found

        '''nav_item = next((item for item in self.book.items if isinstance(item, EpubNav)), None)
        if nav_item:
            if not self.book.toc:
                self._parse_nav(
                    nav_item.content,
                    path.dirname(nav_item.file_name),
                    navtype='toc'
                )
            self._parse_nav(
                nav_item.content,
                path.dirname(nav_item.file_name),
                navtype='pages'
            )'''

    '''def _parse_ncx(self, data):
        tree = parse_string(data)
        tree_root = tree.getroot()

        nav_map = tree_root.find('{%s}navMap' % NAMESPACES['DAISY'])

        def _get_children(elems, n, nid):
            label, content = '', ''
            children = []

            for a in elems.getchildren():
                if a.tag == '{%s}navLabel' % NAMESPACES['DAISY']:
                    label = a.getchildren()[0].text
                if a.tag == '{%s}content' % NAMESPACES['DAISY']:
                    content = a.get('src', '')
                if a.tag == '{%s}navPoint' % NAMESPACES['DAISY']:
                    children.append(_get_children(a, n + 1, a.get('id', '')))

            if len(children) > 0:
                if n == 0:
                    return children

                return (Section(label, href=content),
                        children)
            else:
                return Link(content, label, nid)

        self.book.toc = _get_children(nav_map, 0, '')

    def _parse_nav(self, data, base_path, navtype='toc'):
        html_node = parse_html_string(data)
        if navtype == 'toc':
            # parsing the table of contents
            nav_node = html_node.xpath("//nav[@*='toc']")[0]
        else:
            # parsing the list of pages
            _page_list = html_node.xpath("//nav[@*='page-list']")
            if len(_page_list) == 0:
                return
            nav_node = _page_list[0]

        def parse_list(list_node):
            items = []

            for item_node in list_node.findall('li'):

                sublist_node = item_node.find('ol')
                link_node = item_node.find('a')

                if sublist_node is not None:
                    title = item_node[0].text
                    children = parse_list(sublist_node)

                    if link_node is not None:
                        href = zip_path.normpath(zip_path.join(base_path, link_node.get('href')))
                        items.append((Section(title, href=href), children))
                    else:
                        items.append((Section(title), children))
                elif link_node is not None:
                    title = link_node.text
                    href = zip_path.normpath(zip_path.join(base_path, link_node.get('href')))

                    items.append(Link(href, title))

            return items

        if navtype == 'toc':
            self.book.toc = parse_list(nav_node.find('ol'))
        elif nav_node is not None:
            # generate the pages list if there is one
            self.book.pages = parse_list(nav_node.find('ol'))

            # generate the per-file pages lists
            # because of the order of parsing the files, this can't be done
            # when building the EpubHtml objects
            htmlfiles = dict()
            for htmlfile in self.book.items:
                if isinstance(htmlfile, EpubHtml):
                    htmlfiles[htmlfile.file_name] = htmlfile
            for page in self.book.pages:
                try:
                    (filename, idref) = page.href.split('#')
                except ValueError:
                    filename = page.href
                if filename in htmlfiles:
                    htmlfiles[filename].pages.append(page)'''

    def _load_spine(self):
        spine = self.container.find('{%s}%s' % (NAMESPACES['OPF'], 'spine'))

        '''
        From: https://www.w3.org/publishing/epub3/epub-packages.html#attrdef-itemref-linear
        The linear attribute indicates whether the referenced item contains
        content that contributes to the primary reading order and has to be
        read sequentially ("yes") or auxiliary content that enhances or
        augments the primary content and can be accessed
        out of sequence ("no").
        Examples of auxiliary content include: notes, descriptions and
        answer keys.
        '''
        spine = [(t.get('idref'), t.get('linear', 'yes')) for t in spine]
        self.spine = [self._items[t[0]] for t in spine]

        '''toc = spine.get('toc', '')
        direction = spine.get('page-progression-direction', None)'''

        # should read ncx or nav file
        '''if toc:
            try:
                ncxFile = self.read_file(path.join(self.opf_dir, self.book.get_item_with_id(toc).get_name()))
            except KeyError:
                raise FileNotFoundError(-1, 'Can not find ncx file.')

            self._parse_ncx(ncxFile)'''

    '''def _load_guide(self):
        guide = self.container.find('{%s}%s' % (NAMESPACES['OPF'], 'guide'))
        if guide is not None:
            self._guide = [{'href': t.get('href'), 'title': t.get('title'),
                            'type': t.get('type')} for t in guide]'''


test = Pathfinder(path.join(path.dirname(__file__), 'books', 'niezwyciezony'))
test.search()
print('')
