"""Simple tests for pandas-related functions in convert.py."""

from unittest.mock import MagicMock, patch

import pytest
from pytz.exceptions import AmbiguousTimeError

from time_helper.convert import make_aware_pandas


class TestConvertPandasCoverage:
    """Simple tests for pandas functions coverage."""

    def test_make_aware_pandas_without_pandas(self) -> None:
        """Test make_aware_pandas when pandas is not installed."""
        with (
            patch("time_helper.convert.Series", None),
            patch("time_helper.convert.DataFrame", None),
            pytest.raises(ImportError, match="Pandas Library is not installed"),
        ):
            make_aware_pandas(None, "col")  # type: ignore[arg-type]

    def test_make_aware_pandas_with_none_dataframe(self) -> None:
        """Test make_aware_pandas with None dataframe."""
        mock_series = MagicMock()
        mock_df = MagicMock()

        with patch("time_helper.convert.Series", mock_series), patch("time_helper.convert.DataFrame", mock_df):
            result = make_aware_pandas(None, "col")  # type: ignore[arg-type]
            assert result is None

    def test_make_aware_pandas_with_none_column(self) -> None:
        """Test make_aware_pandas with None column name."""
        mock_series = MagicMock()
        mock_df = MagicMock()
        df = MagicMock()

        with (
            patch("time_helper.convert.Series", mock_series),
            patch("time_helper.convert.DataFrame", mock_df),
            pytest.raises(ValueError, match="Expected column name, but got None"),
        ):
            make_aware_pandas(df, None)  # type: ignore[arg-type]

    def test_make_aware_pandas_with_missing_column(self) -> None:
        """Test make_aware_pandas with missing column."""
        mock_series = MagicMock()
        mock_df = MagicMock()
        df = MagicMock()
        df.columns = ["col1", "col2"]
        df.__contains__ = lambda self, key: key in ["col1", "col2"]

        with (
            patch("time_helper.convert.Series", mock_series),
            patch("time_helper.convert.DataFrame", mock_df),
            pytest.raises(RuntimeError, match="The specified column col3 is not available"),
        ):
            make_aware_pandas(df, "col3")

    def test_make_aware_pandas_with_custom_format(self) -> None:
        """Test make_aware_pandas with custom format."""
        mock_series = MagicMock()
        mock_df = MagicMock()
        mock_is_datetime = MagicMock(return_value=False)
        mock_to_datetime = MagicMock()

        df = MagicMock()
        df.columns = ["date_col"]
        df.__contains__ = lambda self, key: key == "date_col"

        # Create a mock column that acts like a pandas Series
        mock_column = MagicMock()
        mock_column.iloc = MagicMock()
        mock_column.iloc.__getitem__ = lambda self, idx: MagicMock(tzinfo=None)
        df.__getitem__ = lambda self, key: mock_column
        df.__setitem__ = lambda self, key, value: None

        with (
            patch("time_helper.convert.Series", mock_series),
            patch("time_helper.convert.DataFrame", mock_df),
            patch("time_helper.convert.is_datetime", mock_is_datetime),
            patch("time_helper.convert.to_datetime", mock_to_datetime),
        ):
            make_aware_pandas(df, "date_col", format="%Y-%m-%d")

            # Check that to_datetime was called
            mock_to_datetime.assert_called()
            call_args = mock_to_datetime.call_args
            assert "%Y-%m-%d" in call_args[1]["format"]

    def test_make_aware_pandas_with_ambiguous_time(self) -> None:
        """Test make_aware_pandas with AmbiguousTimeError."""
        mock_series = MagicMock()
        mock_df = MagicMock()
        mock_is_datetime = MagicMock(return_value=True)

        df = MagicMock()
        df.columns = ["date_col"]
        df.shape = (5, 2)
        df.__contains__ = lambda self, key: key == "date_col"

        # Create a mock column that raises AmbiguousTimeError on first call
        mock_col = MagicMock()
        mock_dt = MagicMock()

        # First call raises AmbiguousTimeError, second succeeds
        call_count = 0

        def tz_localize_side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise AmbiguousTimeError()
            return mock_col

        mock_dt.tz_localize.side_effect = tz_localize_side_effect
        mock_col.dt = mock_dt
        df.__getitem__ = lambda self, key: mock_col
        df.__setitem__ = lambda self, key, value: None

        with (
            patch("time_helper.convert.Series", mock_series),
            patch("time_helper.convert.DataFrame", mock_df),
            patch("time_helper.convert.is_datetime", mock_is_datetime),
            patch("time_helper.convert.current_timezone", return_value="UTC"),
            patch("time_helper.convert.nparray", MagicMock(return_value=[False] * 5)),
        ):
            # Just verify it doesn't raise an exception
            make_aware_pandas(df, "date_col")

    def test_make_aware_pandas_with_timezone_conversion(self) -> None:
        """Test make_aware_pandas with timezone conversion."""
        from zoneinfo import ZoneInfo

        mock_series = MagicMock()
        mock_df = MagicMock()
        mock_is_datetime = MagicMock(return_value=True)

        df = MagicMock()
        df.columns = ["date_col"]
        df.__contains__ = lambda self, key: key == "date_col"

        # Create a mock column
        mock_col = MagicMock()
        mock_dt = MagicMock()
        mock_dt.tz_localize.return_value = mock_col
        mock_dt.tz_convert.return_value = mock_col
        mock_col.dt = mock_dt
        df.__getitem__ = lambda self, key: mock_col
        df.loc = MagicMock()

        with (
            patch("time_helper.convert.Series", mock_series),
            patch("time_helper.convert.DataFrame", mock_df),
            patch("time_helper.convert.is_datetime", mock_is_datetime),
            patch("time_helper.convert.current_timezone", return_value="UTC"),
        ):
            # Test with ZoneInfo object (should extract key)
            tz = ZoneInfo("America/New_York")
            make_aware_pandas(df, "date_col", tz=tz)

            # Check that tz_convert was called with the key
            mock_dt.tz_convert.assert_called_with("America/New_York")
