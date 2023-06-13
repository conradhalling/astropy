# Licensed under a 3-clause BSD style license - see LICENSE.rst

# THIRD PARTY
import pytest

# LOCAL
from astropy.cosmology.io.latex import _FORMAT_TABLE, write_latex
from astropy.io.registry.base import IORegistryError
from astropy.table import QTable, Table

from .base import ReadWriteDirectTestBase, ReadWriteTestMixinBase


class WriteLATEXTestMixin(ReadWriteTestMixinBase):
    """
    Tests for a Cosmology[Write] with ``format="latex"``.
    This class will not be directly called by :mod:`pytest` since its name does
    not begin with ``Test``. To activate the contained tests this class must
    be inherited in a subclass. Subclasses must dfine a :func:`pytest.fixture`
    ``cosmo`` that returns/yields an instance of a |Cosmology|.
    See ``TestCosmology`` for an example.
    """

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    def test_to_latex_failed_cls(self, write, tmp_path, format):
        """Test failed table type."""
        fp = tmp_path / "test_to_latex_failed_cls.tex"

        with pytest.raises(TypeError, match="'cls' must be"):
            write(fp, format=format, cls=list)

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    @pytest.mark.parametrize("tbl_cls", [QTable, Table])
    def test_to_latex_cls(self, write, tbl_cls, tmp_path, format):
        fp = tmp_path / "test_to_latex_cls.tex"
        write(fp, format=format, cls=tbl_cls)

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    def test_latex_columns(self, write, tmp_path, format):
        fp = tmp_path / "test_rename_latex_columns.tex"
        write(fp, format=format, latex_names=True)
        tbl = QTable.read(fp)
        # asserts each column name has not been reverted yet
        # For now, Cosmology class and name are stored in first 2 slots
        for column_name in tbl.colnames[2:]:
            assert column_name in _FORMAT_TABLE.values()

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    def test_write_latex_invalid_path(self, write, format):
        """Test passing an invalid path"""
        invalid_fp = ""
        with pytest.raises(FileNotFoundError, match="No such file or directory"):
            write(invalid_fp, format=format)

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    def test_write_latex_false_overwrite(self, write, tmp_path, format):
        """Test to write a LaTeX file without overwriting an existing file"""
        # Test that passing an invalid path to write_latex() raises a IOError
        fp = tmp_path / "test_write_latex_false_overwrite.tex"
        write(fp, format="latex")
        with pytest.raises(OSError, match="overwrite=True"):
            write(fp, format=format, overwrite=False)

    def test_write_latex_unsupported_format(self, write, tmp_path):
        """Test for unsupported format"""
        fp = tmp_path / "test_write_latex_unsupported_format.tex"
        invalid_format = "unsupported"
        with pytest.raises((ValueError, IORegistryError)) as exc_info:
            pytest.raises(ValueError, match="format must be 'latex' or 'ascii.latex'")
            pytest.raises(IORegistryError, match="No writer defined for format")
            write(fp, format=invalid_format)


class TestReadWriteLaTex(ReadWriteDirectTestBase, WriteLATEXTestMixin):
    """
    Directly test ``write_latex``.
    These are not public API and are discouraged from use, in favor of
    ``Cosmology.write(..., format="latex")``, but should be
    tested regardless b/c they are used internally.
    """

    def setup_class(self):
        self.functions = {"write": write_latex}

    @pytest.mark.parametrize("format", ["latex", "ascii.latex"])
    def test_rename_direct_latex_columns(self, write, tmp_path, format):
        """Tests renaming columns"""
        fp = tmp_path / "test_rename_latex_columns.tex"
        write(fp, format=format, latex_names=True)
        tbl = QTable.read(fp)
        # asserts each column name has not been reverted yet
        for column_name in tbl.colnames[2:]:
            # for now, Cosmology as metadata and name is stored in first 2 slots
            assert column_name in _FORMAT_TABLE.values()
