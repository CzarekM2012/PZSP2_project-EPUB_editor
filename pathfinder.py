from lxml import etree
from pathlib import Path
import io
import random
import datetime

NAMESPACES = {'XML': 'http://www.w3.org/XML/1998/namespace',
              'EPUB': 'http://www.idpf.org/2007/ops',
              'DAISY': 'http://www.daisy.org/z3986/2005/ncx/',
              'OPF': 'http://www.idpf.org/2007/opf',
              'CONTAINERS': 'urn:oasis:names:tc:opendocument:xmlns:container',
              'DC': 'http://purl.org/dc/elements/1.1/',
              'XHTML': 'http://www.w3.org/1999/xhtml'}

IMAGE_MEDIA_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml']


class MissingValueError(ValueError):
    pass


class Pathfinder:
    """
    Object finding paths to stylesheets and files in the spine of
    the unpacked .epub file
    """
    def __init__(self, book_dir: str = None) -> None:
        self._rendition = (-1,
                           {'spine': list[str](),
                            'stylesheets': list[str]()},
                           None)
        self._opf_files = list[str]()
        self.set_book_dir(book_dir=book_dir)

    def set_book_dir(self, book_dir: str = None) -> None:
        self.book_dir = book_dir

    def find_renditions(self) -> None:
        self._rendition = (-1,
                           {'spine': list[str](),
                            'stylesheets': list[str]()},
                           None)
        self._opf_files.clear()
        self._load_container()

    def load_rendition(self, index: int = 0) -> None:
        self.save_rendition_file()
        index = min(index, len(self._opf_files) - 1)
        spine, stylesheets, opf_file_tree = self._load_opf_file(index)
        self._rendition = (index,
                           {'spine': spine,
                            'stylesheets': stylesheets},
                           opf_file_tree)

    def get_rendition_paths(self)\
            -> tuple[list[Path], list[Path]]:
        opf_file_path, spine, stylesheets, _ = self._get_rendition_data()
        opf_file_dirname = opf_file_path.parent
        spine_files_paths =\
            [Path(self.book_dir) / opf_file_dirname / spine_file
             for spine_file in spine]
        stylesheets_paths =\
            [Path(self.book_dir) / opf_file_dirname / stylesheet
             for stylesheet in stylesheets]
        return spine_files_paths, stylesheets_paths

    def get_opf_file_path(self):
        return self._get_rendition_data()[0]

    def get_opf_folder_path(self):
        return self.get_opf_file_path().parent

    def get_font_folder_path(self):
        return self.get_opf_folder_path() / 'Fonts'

    def add_item_to_rendition_manifest(self, item_attributes:
                                       list[str, str, str]) -> bool:
        """
        Works if `item_attributes[0]` is unique id and `item_attributes[1]`
        refers to a file not added to manifest already
        """
        item_id, item_path, item_media_type = item_attributes
        opf_file_path, _, _, opf_file_tree = self._get_rendition_data()
        manifest = opf_file_tree.find(f'{{{NAMESPACES["OPF"]}}}manifest')
        opf_file_path = Path(self.book_dir) / opf_file_path
        opf_file_dirname = opf_file_path.parent
        item_href = Path(item_path).relative_to(opf_file_dirname)
        if manifest.find(f'{{{NAMESPACES["OPF"]}}}item[@href="{item_href}"]')\
           is not None:  # file already added
            return False

        item_id =\
            self._generate_not_present_id(manifest, item_id)
        item = manifest.makeelement(f'{{{NAMESPACES["OPF"]}}}item',
                                    attrib={'id': item_id,
                                            'href': str(item_href),
                                            'media-type': item_media_type})
        item.tail = manifest[-1].tail
        manifest[-1].tail = manifest.text
        manifest.extend([item])

        return item_id, item_path

    def remove_item_from_rendition_manifest(
            self, ids: tuple[str, str] = (None, None)) -> tuple[bool, bool]:
        """
        Removes item with both id and href or at leas one of them matching
        given values(scenario dependent on given set of values)\n
        First bool from returned tuple is `True` if item was removed,
        second - if file itself can be removed because it is not mentioned
        in manifests of other renditions
        """
        item_id, item_path = ids
        if item_id is None and item_path is None:
            return False, False
        opf_file_path, _, _, opf_file_tree = self._get_rendition_data()
        manifest = opf_file_tree.find(f'{{{NAMESPACES["OPF"]}}}manifest')
        if len(manifest) <= 2:  # at least 1 item in manifest at all times
            return False, False
        opf_file_path = Path(self.book_dir) / opf_file_path
        opf_file_dirname = opf_file_path.parent
        item_href = item_path
        if item_href is not None:
            item_href = Path(item_href).relative_to(opf_file_dirname)

        if item_id is not None and item_href is not None:
            ids = manifest.findall(f'{{{NAMESPACES["OPF"]}}}item\
[@id="{item_id}"]')
            hrefs = manifest.findall(f'{{{NAMESPACES["OPF"]}}}item\
[@href="{item_href}"]')
            matches = list(set(ids) & set(hrefs))
        elif item_id is not None:
            matches = manifest.findall(f'{{{NAMESPACES["OPF"]}}}item\
[@id="{item_id}"]')
        else:
            matches = manifest.findall(f'{{{NAMESPACES["OPF"]}}}item\
[@href="{item_href}"]')
        if len(matches) != 1:
            return False, False

        match = matches[0]
        if match == manifest[-1]:
            manifest[-2].tail = manifest[-1].tail
        item_path = Path(opf_file_dirname) / match.get('href')
        manifest.remove(match)

        for i in range(len(self._opf_files)):
            if i == self._rendition[0]:
                continue
            if self._is_file_in_rendition_manifest(item_path, i):
                return True, False
        return True, True

    def save_rendition_file(self):
        try:
            opf_file_path, _, _, opf_file_tree = self._get_rendition_data()
        except RuntimeError:
            return
        opf_file_path = self.book_dir / opf_file_path
        metadata = opf_file_tree.find(f'{{{NAMESPACES["OPF"]}}}metadata')
        last_edited =\
            metadata.find(f'{{{NAMESPACES["OPF"]}}}meta[@property="dcterms:modified"]')
        if last_edited is None:
            last_edited =\
                metadata.makeelement(f'{{{NAMESPACES["OPF"]}}}meta',
                                     attrib={'property': "dcterms:modified"})
            last_edited.tail = metadata[-1].tail
            metadata[-1].tail = metadata.text
            metadata.extend([last_edited])
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        last_edited.text = str(now)
        serialized = etree.tostring(opf_file_tree, encoding='utf-8',
                                    xml_declaration=True)
        with open(opf_file_path, 'wb') as file:
            file.write(serialized)

    def _generate_not_present_id(self, manifest, base_id: str) -> str:
        # Very simple id generation. Replace with something decent if need be
        new_id = base_id
        while manifest.find(f'{{{NAMESPACES["OPF"]}}}item[@id="{new_id}"]')\
                is not None:
            new_id += str(random.randint(0, 9))
        return new_id

    def _is_file_in_rendition_manifest(self, filepath: str,
                                       rendition_id: int) -> bool:
        _, _, rendition_tree = self._load_opf_file(rendition_id)
        rendition_rel_path = self._opf_files[rendition_id]
        opf_file_dirname = (Path(self.book_dir) / rendition_rel_path).parent
        href = Path(filepath).relative_to(opf_file_dirname)
        manifest = rendition_tree.find(f'{{{NAMESPACES["OPF"]}}}manifest')
        if manifest.find(f'{{{NAMESPACES["OPF"]}}}item[@href="{href}"]')\
           is not None:
            return True
        return False

    def get_rendition_manifest_items_attributes(self, rendition_id: int = 0)\
            -> list[tuple[str, str, str]]:
        content = self._read(self.renditions[rendition_id]['opf_file'])
        tree = self._parse_xml(content)
        manifest = tree.find(f'{{{NAMESPACES["OPF"]}}}manifest')
        children = manifest.getchildren()
        attributes =\
            [(child.get('id'), child.get('href'), child.get('media-type'))
             for child in children]
        return attributes

    def _parse_xml(self, xml: str) -> None:
        try:
            tree = etree.parse(io.BytesIO(xml.encode('utf-8')))
        except etree.Error:
            tree = etree.parse(io.BytesIO(xml))

        return tree

    def _get_rendition_data(self):
        if self._rendition[0] == -1:
            raise RuntimeError('No rendition has been loaded yet, \
use load_rendition() method first')
        return Path(self._opf_files[self._rendition[0]]),\
            self._rendition[1]['spine'],\
            self._rendition[1]['stylesheets'],\
            self._rendition[2]

    def _load_container(self) -> None:
        try:
            meta_inf = self._read('META-INF/container.xml')
        except FileNotFoundError as e:
            raise FileNotFoundError('This ".epub" file does not \
contain the \"META-INF/container.xml\", which is required by the \
standard and therefore cannot be read') from e

        tree = self._parse_xml(meta_inf)

        views = tree.findall('//xmlns:rootfile[@media-type]',
                             namespaces={'xmlns': NAMESPACES['CONTAINERS']})
        if len(views) == 0:
            raise MissingValueError('\"META-INF/container.xml\" in this epub \
contains no referrence to file describing structure of the book view, \
and therefore book cannot be read')
        for root_file in views:
            if root_file.get('media-type') == 'application/oebps-package+xml':
                self._opf_files.append(root_file.get('full-path'))
        if len(self._opf_files) == 0:
            raise MissingValueError('None of book rendition references \
in \"META-INF/container.xml\" is marked with proper media-type and therefore, \
file is non-compliant with the standard')

    def _read(self, name: str) -> str:
        with open(Path(self.book_dir) / name, "r") as file:
            content = file.read()
        return content

    def _load_opf_file(self, opf_file_index: int)\
            -> tuple[list[str], list[str], None]:
        opf_file_internal_path = self._opf_files[opf_file_index]
        try:
            content = self._read(opf_file_internal_path)
        except FileNotFoundError:
            raise FileNotFoundError(-1, 'Can not find container file')

        opf_file_tree = self._parse_xml(content)

        id_to_href, stylesheets = self._load_manifest(opf_file_tree)
        spine = self._load_spine(opf_file_tree, id_to_href)

        return spine, stylesheets, opf_file_tree

    def _load_manifest(self, container) -> tuple[dict[str, str], list[str]]:
        items = dict[str, str]()
        stylesheets = list[str]()
        assignments = {
            'text/css': lambda href: stylesheets.append(href),
        }
        for entry in container.find(f'{{{NAMESPACES["OPF"]}}}manifest'):
            if entry is not None and\
               entry.tag != f'{{{NAMESPACES["OPF"]}}}item':
                continue
            href = entry.get('href')
            items[entry.get('id')] = href
            try:
                assignments[entry.get('media-type')](href)
            except KeyError:
                pass
        return items, stylesheets

    def _load_spine(self, container, id_to_href: dict[str, str]) -> list[str]:
        spine = container.find(f'{{{NAMESPACES["OPF"]}}}spine')

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
        content = [[], []]  # value of linear 'yes' and 'no'
        for entry in spine:
            id_ref = entry.get('idref')
            index = 0
            if entry.get('linear', 'yes') != 'yes':
                index = 1
            content[index].append(id_ref)
        for i in range(len(content)):
            for j in range(len(content[i])):
                content[i][j] = id_to_href[content[i][j]]
        return content[0] + content[1]
