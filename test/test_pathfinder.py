import unittest
import os
import os.path
import shutil
from os.path import join as join_paths, isfile, islink, isdir,\
                    exists as path_exists, normpath
from pathfinder import MissingValueError, Pathfinder


def norm_join_paths(path: str, *paths: str) -> str:
    for addition in paths:
        path = join_paths(path, addition)
    return normpath(path)


class TestPathfinder(unittest.TestCase):

    def setUp(self) -> None:
        self.test_pathfinder = Pathfinder()
        self.test_dirs_dir = norm_join_paths('test', 'tests_resources',
                                             'pathfinder')
        self.created = []

    def tearDown(self) -> None:
        for path in self.created:
            if path_exists(path):
                if isdir(path):
                    shutil.rmtree(path)
                if isfile(path) or islink(path):
                    os.unlink(path)

    def test__read(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir, 'new')
        test_file_name = 'file'
        test_file = norm_join_paths(test_dir, test_file_name)
        written_content = 'abcdefg'
        os.mkdir(test_dir)
        with open(test_file, 'w') as file:
            file.write(written_content)
        self.created.append(test_dir)
        self.created.append(test_file)

        self.test_pathfinder.set_book_dir(test_dir)
        file_content = self.test_pathfinder._read(test_file_name)
        self.assertEqual(file_content, written_content)

    def test__load_container_no_META_INF_container_xml(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir,
                                   'META-INF_container.xml_missing')

        self.test_pathfinder.set_book_dir(test_dir)
        with self.assertRaises(FileNotFoundError):
            self.test_pathfinder._load_container()

    def test__load_container_no_rootfiles(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir, 'no_rootfile')

        self.test_pathfinder.set_book_dir(test_dir)
        with self.assertRaises(MissingValueError):  # subclass ValueError
            self.test_pathfinder._load_container()

    def test__load_container_single_rootfile(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir, 'single_rootfile')
        opf_file_internal_path = norm_join_paths('OEBPS', 'content.opf')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        self.assertEqual(norm_join_paths(test_dir,
                                         self.test_pathfinder._opf_file[0]),
                         norm_join_paths(test_dir, opf_file_internal_path))

    def test__load_container_multiple_rootfiles_single_content_opf(self)\
            -> None:
        test_dir = norm_join_paths(self.test_dirs_dir,
                                   'multiple_rootfiles;single_content.opf')
        opf_file_internal_path = norm_join_paths('OEBPS', 'content.opf')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        self.assertEqual(norm_join_paths(test_dir,
                                         self.test_pathfinder._opf_file[0]),
                         norm_join_paths(test_dir, opf_file_internal_path))

    def test__load_container_multiple_rootfiles_multiple_contents_opf(self)\
            -> None:
        test_dir = norm_join_paths(self.test_dirs_dir,
                                   'multiple_rootfiles;multiple_contents.opf')
        opf_files_internal_paths = (norm_join_paths('OEBPS', 'content1.opf'),
                                    norm_join_paths('OEBPS', 'content2.opf'))

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        self.assertEqual(norm_join_paths(test_dir,
                                         self.test_pathfinder._opf_file[0]),
                         norm_join_paths(test_dir,
                                         opf_files_internal_paths[0]))
        self.assertEqual(norm_join_paths(test_dir,
                                         self.test_pathfinder._opf_file[1]),
                         norm_join_paths(test_dir,
                                         opf_files_internal_paths[1]))

    def test__load_opf_file_opf_file_missing(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir,
                                   'single_rootfile;content.opf_missing')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        with self.assertRaises(FileNotFoundError):
            self.test_pathfinder._load_opf_file()

    def test__load_manifest(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir, 'single_rootfile')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        self.test_pathfinder._load_manifest()

        self.assertEqual(self.test_pathfinder._items['stylesheet'], 'css/styles.css')
        self.assertEqual(self.test_pathfinder._items['Page01'], 'Page01.xhtml')
        self.assertEqual(self.test_pathfinder._items['Page02'], 'Page02.xhtml')
        self.assertEqual(self.test_pathfinder._items['Page03'], 'Page03.xhtml')
        self.assertEqual(self.test_pathfinder._items['nav'], 'nav.xhtml')
        self.assertEqual(self.test_pathfinder._items['ncx'], 'toc.ncx')
        self.assertEqual(self.test_pathfinder._items['logo'], 'epub-editor-logo.png')
        self.assertEqual(self.test_pathfinder.stylesheets[0], 'css/styles.css')

    def test__load_spine(self) -> None:
        test_dir = norm_join_paths(self.test_dirs_dir, 'single_rootfile')

        self.test_pathfinder.set_book_dir(test_dir)
        self.test_pathfinder._load_container()
        self.test_pathfinder._load_manifest()
        self.test_pathfinder._load_spine()

        self.assertEqual(self.test_pathfinder.spine[0], 'Page01.xhtml')
        self.assertEqual(self.test_pathfinder.spine[1], 'Page02.xhtml')
        self.assertEqual(self.test_pathfinder.spine[2], 'Page03.xhtml')
