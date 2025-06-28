"""
Unit tests for entrypoints_params module.
"""
import pytest
import typer
import datetime

from at_bus_load.entrypoints_params import validate_date


class TestValidateDate:
    """Test cases for validate_date function."""

    def test_validate_date_valid_format(self):
        """Test that valid date formats pass validation."""
        valid_dates = [
            "2025-06-29",
            "2024-12-31",
            "2023-01-01",
            "2020-02-29",  # Leap year
            "2021-02-28",  # Non-leap year
            "1999-12-31",
            "2030-01-01"
        ]
        
        for date_str in valid_dates:
            # Should not raise any exception
            validate_date(date_str)
            
            # Verify it's actually a valid date by parsing it
            parsed_date = datetime.date.fromisoformat(date_str)
            assert isinstance(parsed_date, datetime.date)

    def test_validate_date_invalid_format(self):
        """Test that invalid date formats raise BadParameter exception."""
        invalid_dates = [
            "invalid-date",
            "2025/06/29",
            "06-29-2025",
            "29-06-2025",
            "2025-6-29",
            "2025-06-9",
            "2025-13-01",  # Invalid month
            "2025-04-31",  # Invalid day for April
            "2023-02-29",  # Invalid day for non-leap year
            "2025-00-01",  # Invalid month
            "2025-01-00",  # Invalid day
            "2025-06-29T10:30:00",  # ISO format with time
            "2025-06-29 10:30:00",  # Space separated
            "",
            "not-a-date",
            "2025",
            "2025-06",
            "06-29",
            "29/06/2025",
            "2025.06.29",
            "2025_06_29"
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(typer.BadParameter) as exc_info:
                validate_date(date_str)
            
            # Verify the error message contains the expected text
            assert "Invalid date format" in str(exc_info.value)
            assert "Please use YYYY-MM-DD format" in str(exc_info.value)
            assert date_str in str(exc_info.value)

    def test_validate_date_edge_cases(self):
        """Test edge cases for date validation."""
        # Test with None (should raise TypeError from datetime.date.fromisoformat)
        with pytest.raises(TypeError):
            validate_date(None)
        
        # Test with non-string types (should raise TypeError from datetime.date.fromisoformat)
        with pytest.raises(TypeError):
            validate_date(123)
        
        with pytest.raises(TypeError):
            validate_date(2025.06)
        
        with pytest.raises(TypeError):
            validate_date([])
        
        with pytest.raises(TypeError):
            validate_date({})

    def test_validate_date_boundary_values(self):
        """Test boundary values for date validation."""
        # Test very old dates
        validate_date("1900-01-01")
        validate_date("1000-01-01")
        
        # Test future dates
        validate_date("2030-12-31")
        validate_date("2100-01-01")
        
        # Test edge of valid ranges
        validate_date("2025-01-01")  # January 1st
        validate_date("2025-12-31")  # December 31st
        validate_date("2025-01-31")  # January 31st
        validate_date("2025-02-28")  # February 28th (non-leap year)
        validate_date("2024-02-29")  # February 29th (leap year)

    def test_validate_date_leap_year_logic(self):
        """Test leap year validation logic."""
        # Valid leap years
        leap_years = ["2024-02-29", "2020-02-29", "2016-02-29", "2000-02-29"]
        for date_str in leap_years:
            validate_date(date_str)
        
        # Invalid leap year dates (February 29th in non-leap years)
        non_leap_feb_29 = ["2023-02-29", "2022-02-29", "2021-02-29", "2019-02-29"]
        for date_str in non_leap_feb_29:
            with pytest.raises(typer.BadParameter):
                validate_date(date_str)

    def test_validate_date_month_day_combinations(self):
        """Test various month and day combinations."""
        # Test months with 31 days
        months_31_days = ["2025-01-31", "2025-03-31", "2025-05-31", 
                         "2025-07-31", "2025-08-31", "2025-10-31", "2025-12-31"]
        for date_str in months_31_days:
            validate_date(date_str)
        
        # Test months with 30 days
        months_30_days = ["2025-04-30", "2025-06-30", "2025-09-30", "2025-11-30"]
        for date_str in months_30_days:
            validate_date(date_str)
        
        # Test invalid day combinations
        invalid_combinations = [
            "2025-01-32",  # January has 31 days
            "2025-02-30",  # February has max 29 days
            "2025-04-31",  # April has 30 days
            "2025-06-31",  # June has 30 days
            "2025-09-31",  # September has 30 days
            "2025-11-31",  # November has 30 days
        ]
        for date_str in invalid_combinations:
            with pytest.raises(typer.BadParameter):
                validate_date(date_str)

    def test_validate_date_error_message_format(self):
        """Test that error messages are properly formatted."""
        test_date = "invalid-date"
        
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_date(test_date)
        
        error_message = str(exc_info.value)
        
        # Check that the error message contains all expected components
        assert "Invalid date format" in error_message
        assert test_date in error_message
        assert "Please use YYYY-MM-DD format" in error_message
        
        # Check that the message is properly formatted
        expected_format = f"Invalid date format: {test_date}. Please use YYYY-MM-DD format."
        assert error_message == expected_format

    def test_validate_date_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        # Test with leading/trailing whitespace
        with pytest.raises(typer.BadParameter):
            validate_date(" 2025-06-29")
        
        with pytest.raises(typer.BadParameter):
            validate_date("2025-06-29 ")
        
        with pytest.raises(typer.BadParameter):
            validate_date(" 2025-06-29 ")
        
        # Test with tabs and newlines
        with pytest.raises(typer.BadParameter):
            validate_date("\t2025-06-29")
        
        with pytest.raises(typer.BadParameter):
            validate_date("2025-06-29\n")

    def test_validate_date_special_characters(self):
        """Test that special characters are handled correctly."""
        special_char_dates = [
            "2025-06-29!",
            "!2025-06-29",
            "2025-06-29@",
            "2025@06@29",
            "2025#06#29",
            "2025$06$29",
            "2025%06%29",
            "2025^06^29",
            "2025&06&29",
            "2025*06*29",
            "2025(06)29",
            "2025[06]29",
            "2025{06}29",
        ]
        
        for date_str in special_char_dates:
            with pytest.raises(typer.BadParameter):
                validate_date(date_str)


class TestIntegrationScenarios:
    """Integration test scenarios for the validate_date function."""

    def test_validate_date_in_real_world_scenarios(self):
        """Test validate_date with real-world date scenarios."""
        # Common date formats that should be rejected
        real_world_invalid = [
            "06/29/2025",      # US format
            "29/06/2025",      # European format
            "2025.06.29",      # Dot separated
            "2025_06_29",      # Underscore separated
            "June 29, 2025",   # Text format
            "29-Jun-2025",     # Abbreviated month
            "2025-Jun-29",     # Abbreviated month
            "2025-6-29",       # Missing leading zero
            "2025-06-9",       # Missing leading zero
        ]
        
        for date_str in real_world_invalid:
            with pytest.raises(typer.BadParameter):
                validate_date(date_str)
        
        # Valid real-world scenarios
        valid_scenarios = [
            "2025-06-29",      # Standard format
            "2024-12-31",      # End of year
            "2025-01-01",      # Start of year
            "2024-02-29",      # Leap year
        ]
        
        for date_str in valid_scenarios:
            validate_date(date_str)