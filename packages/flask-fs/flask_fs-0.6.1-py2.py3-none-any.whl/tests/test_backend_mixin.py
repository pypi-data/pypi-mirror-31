# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import six

from datetime import datetime


class BackendTestCase(object):

    def b(self, content):
        if isinstance(content, six.string_types):
            content = six.b(content)
        return content

    def put_file(self, filename, content):
        raise NotImplementedError('You must implement this method')

    def get_file(self, filename):
        raise NotImplementedError('You must implement this method')

    def file_exists(self, filename):
        raise NotImplementedError('You must implement this method')

    def assert_bin_equal(self, filename, expected):
        data = self.get_file(filename)
        assert data == self.b(expected)

    def assert_text_equal(self, filename, expected):
        data = self.get_file(filename)
        assert data == six.b(expected)

    def test_exists(self):
        self.put_file('file.test', 'test')
        assert self.backend.exists('file.test')
        assert not self.backend.exists('other.test')

    def test_open_read(self, faker):
        content = six.text_type(faker.sentence())
        self.put_file('file.test', content)

        with self.backend.open('file.test') as f:
            data = f.read()
            assert isinstance(data, six.text_type)
            assert data == content

    def test_open_read_binary(self, faker):
        content = six.binary_type(faker.binary())
        self.put_file('file.test', content)

        with self.backend.open('file.test', 'rb') as f:
            data = f.read()
            assert isinstance(data, six.binary_type)
            assert data == content

    def test_open_write_new_file(self, faker):
        filename = 'test.text'
        content = six.text_type(faker.sentence())

        with self.backend.open(filename, 'w') as f:
            f.write(content)

        self.assert_text_equal(filename, content)

    def test_open_write_new_file_with_prefix(self, faker):
        filename = 'some/new/dir/test.text'
        content = six.text_type(faker.sentence())

        with self.backend.open(filename, 'w') as f:
            f.write(content)

        self.assert_text_equal(filename, content)

    def test_open_write_new_binary_file(self, faker):
        filename = 'test.bin'
        content = six.binary_type(faker.binary())

        with self.backend.open(filename, 'wb') as f:
            f.write(content)

        self.assert_bin_equal(filename, content)

    def test_open_write_existing_file(self, faker):
        filename = 'test.txt'
        content = six.text_type(faker.sentence())
        self.put_file(filename, six.text_type(faker.sentence()))

        with self.backend.open(filename, 'w') as f:
            f.write(content)

        self.assert_text_equal(filename, content)

    def test_read(self, faker):
        content = six.text_type(faker.sentence())
        self.put_file('file.test', content)

        assert self.backend.read('file.test') == six.b(content)

    def test_write_text(self, faker):
        content = six.text_type(faker.sentence())
        self.backend.write('test.txt', content)

        self.assert_text_equal('test.txt', content)

    def test_write_binary(self, faker):
        content = six.binary_type(faker.binary())
        self.backend.write('test.bin', content)

        self.assert_bin_equal('test.bin', content)

    def test_write_file(self, faker, utils):
        content = six.binary_type(faker.binary())
        self.backend.write('test.bin', utils.file(content))

        self.assert_bin_equal('test.bin', content)

    def test_write_with_prefix(self, faker):
        content = six.text_type(faker.sentence())
        self.backend.write('some/path/to/test.txt', content)

        self.assert_text_equal('some/path/to/test.txt', content)

    def test_delete(self, faker):
        content = faker.sentence()
        self.put_file('file.test', content)

        self.backend.delete('file.test')

        assert not self.file_exists('file.test')

    def test_delete_directory(self, faker):
        content = faker.sentence()
        self.put_file('test/file.01', content)
        self.put_file('test/file.02', content)

        self.backend.delete('test')

        assert not self.file_exists('test/file.01')
        assert not self.file_exists('test/file.02')
        assert not self.file_exists('test')

    def test_save_content(self, faker, utils):
        content = six.text_type(faker.sentence())
        storage = utils.filestorage('test.txt', content)
        self.backend.save(storage, 'test.txt')

        self.assert_text_equal('test.txt', content)

    def test_save_from_file(self, faker, utils):
        content = six.binary_type(faker.binary())
        f = utils.file(content)
        self.backend.save(f, 'test.png')

        f.seek(0)

        self.assert_bin_equal('test.png', content)

    def test_save_with_filename(self, faker, utils):
        filename = 'somewhere/test.test'
        content = six.text_type(faker.sentence())
        storage = utils.filestorage('test.txt', content)
        self.backend.save(storage, filename)

        self.assert_text_equal(filename, content)

    def test_list_files(self, faker, utils):
        files = set(['first.test', 'second.test', 'some/path/to/third.test'])
        for f in files:
            content = six.text_type(faker.sentence())
            self.put_file(f, content)

        assert set(self.backend.list_files()) == files

    def test_metadata(self, app, faker):
        content = six.text_type(faker.sentence())
        hasher = getattr(hashlib, self.hasher)
        hashed = hasher(content.encode('utf8')).hexdigest()
        self.put_file('file.txt', content)

        metadata = self.backend.metadata('file.txt')
        assert metadata['checksum'] == '{0}:{1}'.format(self.hasher, hashed)
        assert metadata['size'] == len(content)
        assert metadata['mime'] == 'text/plain'
        assert isinstance(metadata['modified'], datetime)

    def test_metadata_unknown_mime(self, app, faker):
        content = six.text_type(faker.sentence())
        self.put_file('file.whatever', content)

        metadata = self.backend.metadata('file.whatever')
        assert metadata['mime'] in ('application/octet-stream', 'text/plain')

    def test_copy(self, faker):
        content = faker.sentence()
        self.put_file('file.test', content)
        target = 'other/path/to/file.test2'

        self.backend.copy('file.test', target)

        assert self.file_exists('file.test')
        assert self.file_exists(target)
        self.assert_text_equal(target, content)

    def test_move(self, faker):
        content = faker.sentence()
        self.put_file('file.test', content)
        target = 'other/path/to/file.test2'

        self.backend.move('file.test', target)

        assert not self.file_exists('file.test')
        assert self.file_exists(target)
        self.assert_text_equal(target, content)
