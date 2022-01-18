import unittest
import os
from os import path
import shutil
from pathfinder import MissingValueError, Pathfinder, paths_join_normalize


class TestPathfinder(unittest.TestCase):

    def setUp(self) -> None:
        self.test_pathfinder = Pathfinder()
        self.test_dirs_dir = paths_join_normalize('test', 'tests_resources',
                                                  'pathfinder')
        self.created = []

    def tearDown(self) -> None:
        for filepath in self.created:
            if path.exists(filepath):
                if path.isdir(filepath):
                    shutil.rmtree(filepath)
                if path.isfile(filepath) or path.islink(filepath):
                    os.unlink(filepath)

    def test__read(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'new')
        test_file_name = 'file'
        test_file = paths_join_normalize(test_dir, test_file_name)
        written_content = 'abcdefg'
        os.mkdir(test_dir)
        with open(test_file, 'w') as file:
            file.write(written_content)
        self.created.append(test_dir)
        self.created.append(test_file)

        self.test_pathfinder.set_book_dir(test_dir)
        file_content = self.test_pathfinder._read(test_file_name)

        self.assertEqual(written_content, file_content)

    def test_find_renditions_no_META_INF_container_xml(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir,
                                        'META-INF_container.xml_missing')

        self.test_pathfinder.set_book_dir(test_dir)

        with self.assertRaises(FileNotFoundError):
            self.test_pathfinder.find_renditions()

    def test_find_renditions_no_rootfiles(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'no_rootfile')

        self.test_pathfinder.set_book_dir(test_dir)

        with self.assertRaises(MissingValueError):
            self.test_pathfinder.find_renditions()

    def test_find_renditions_single_rootfile(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'single_rootfile')
        opf_file_internal_path = paths_join_normalize('OEBPS', 'content.opf')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()

        self.assertEqual(opf_file_internal_path,
                         path.normcase(path.normpath(
                             self.test_pathfinder._opf_files[0])))

    def test_find_renditions_multiple_rootfiles_single_content_opf(self)\
            -> None:
        # Doesn't check if every file mentioned in rootfiles exists
        test_dir =\
            paths_join_normalize(self.test_dirs_dir,
                                 'multiple_rootfiles;single_content.opf')
        expected_opf_files_internal_paths =\
            ['OEBPS/content1.opf', 'OEBPS/content2.opf']

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()

        self.assertListEqual(expected_opf_files_internal_paths,
                             self.test_pathfinder._opf_files)
        with self.assertRaises(FileNotFoundError):
            self.test_pathfinder.load_rendition(1)

    def test_find_renditions_multiple_rootfiles_multiple_contents_opf(self)\
            -> None:
        test_dir =\
            paths_join_normalize(self.test_dirs_dir,
                                 'multiple_rootfiles;multiple_contents.opf')
        expected_opf_files_internal_paths =\
            ['OEBPS/content1.opf', 'OEBPS/content2.opf']

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()

        self.assertListEqual(expected_opf_files_internal_paths,
                             self.test_pathfinder._opf_files)
        self.test_pathfinder.load_rendition(1)

    def test_load_rendition_opf_file_missing(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir,
                                        'single_rootfile;content.opf_missing')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()

        with self.assertRaises(FileNotFoundError):
            self.test_pathfinder.load_rendition()

    def test__load_manifest(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'single_rootfile')
        expected_items = {
            'stylesheet': 'css/styles.css',
            'Page01': 'Page01.xhtml',
            'Page02': 'Page02.xhtml',
            'Page03': 'Page03.xhtml',
            'nav': 'nav.xhtml',
            'ncx': 'toc.ncx',
            'logo': 'epub-editor-logo.png'}
        expected_stylesheets = ['css/styles.css']

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()
        structure = self.test_pathfinder._parse_xml(
            self.test_pathfinder._read(
                self.test_pathfinder._opf_files[0]))
        items, stylesheets = self.test_pathfinder._load_manifest(structure)

        self.assertDictEqual(expected_items, items)
        self.assertEqual(expected_stylesheets, stylesheets)

    def test__load_spine(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'single_rootfile')
        expected_spine = ['Page01.xhtml', 'Page02.xhtml', 'Page03.xhtml']

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()
        structure = self.test_pathfinder._parse_xml(
            self.test_pathfinder._read(
                self.test_pathfinder._opf_files[0]))
        items, _ = self.test_pathfinder._load_manifest(structure)
        spine = self.test_pathfinder._load_spine(structure, items)

        self.assertListEqual(expected_spine, spine)

    def test_load_rendition(self) -> None:
        test_dir = paths_join_normalize(self.test_dirs_dir, 'single_rootfile')
        expected_opf_file_path = 'OEBPS/content.opf'
        expected_spines = ['Page01.xhtml', 'Page02.xhtml', 'Page03.xhtml']
        expected_stylesheets = ['css/styles.css']

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder.find_renditions()
        self.test_pathfinder.load_rendition()

        opf_file_path, spines, stylesheets =\
            self.test_pathfinder._get_rendition_data()
        self.assertEqual(expected_opf_file_path, opf_file_path)
        self.assertListEqual(expected_spines, spines)
        self.assertListEqual(expected_stylesheets, stylesheets)
