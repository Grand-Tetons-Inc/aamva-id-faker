"""
Unit tests for AAMVA barcode formatting.

Tests the formatting of license data into AAMVA-compliant PDF417 barcode format
following the DL/ID-2020 specification.

TDD RED phase - tests written before implementation.
"""

import pytest
from hypothesis import given, strategies as st, settings

# Import will fail initially (TDD RED phase)
# from src.core.barcode_formatter import (
#     format_barcode_data,
#     build_header,
#     build_dl_subfile,
#     build_state_subfile,
#     calculate_offsets,
#     encode_field,
# )

pytestmark = pytest.mark.unit


class TestBarcodeStructure:
    """Tests for overall barcode structure and compliance."""

    def test_compliance_markers_present(self, sample_california_license):
        """Barcode must start with @ LF RS CR compliance markers."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # First 4 bytes: @ \n \x1E \r
        assert result[0] == '@', "Missing @ compliance marker"
        assert result[1] == '\n', "Missing LF after @"
        assert result[2] == '\x1E', "Missing RS (0x1E) record separator"
        assert result[3] == '\r', "Missing CR after RS"

    def test_ansi_file_type_present(self, sample_california_license):
        """Header must contain 'ANSI ' file type identifier."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Positions 4-8: "ANSI "
        header_start = result[4:9]
        assert header_start == 'ANSI ', f"Expected 'ANSI ', got '{header_start}'"

    def test_iin_is_six_digits(self, sample_california_license):
        """IIN (Issuer Identification Number) must be exactly 6 digits."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Positions 9-14: IIN (6 digits)
        iin = result[9:15]
        assert len(iin) == 6, f"IIN should be 6 characters, got {len(iin)}"
        assert iin.isdigit(), f"IIN should be all digits, got '{iin}'"

    def test_california_has_correct_iin(self, sample_california_license, california_iin):
        """California's IIN should be 636014."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        iin = result[9:15]
        assert iin == california_iin, f"Expected CA IIN {california_iin}, got {iin}"

    def test_version_is_10(self, sample_california_license):
        """AAMVA version should be '10' (DL/ID-2020 spec)."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Positions 15-16: Version
        version = result[15:17]
        assert version == '10', f"Expected version '10', got '{version}'"

    def test_jurisdiction_version_is_00(self, sample_california_license):
        """Jurisdiction version should be '00'."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Positions 17-18: Jurisdiction version
        juris_version = result[17:19]
        assert juris_version == '00', f"Expected '00', got '{juris_version}'"

    def test_subfile_count_is_02(self, sample_california_license):
        """Should indicate 2 subfiles (DL + State)."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Positions 19-20: Number of subfiles
        count = result[19:21]
        assert count == '02', f"Expected '02' subfiles, got '{count}'"


class TestSubfileDesignators:
    """Tests for subfile designators in header."""

    def test_dl_subfile_designator_present(self, sample_california_license):
        """DL subfile designator should be in header."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # First designator at position 21-22: "DL"
        designator = result[21:23]
        assert designator == 'DL', f"Expected 'DL', got '{designator}'"

    def test_dl_offset_is_four_digits(self, sample_california_license):
        """DL subfile offset should be 4 digits."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Offset at positions 23-26 (4 digits)
        offset = result[23:27]
        assert len(offset) == 4, f"Offset should be 4 digits, got {len(offset)}"
        assert offset.isdigit(), f"Offset should be numeric, got '{offset}'"

    def test_dl_length_is_four_digits(self, sample_california_license):
        """DL subfile length should be 4 digits."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Length at positions 27-30 (4 digits)
        length = result[27:31]
        assert len(length) == 4, f"Length should be 4 digits, got {len(length)}"
        assert length.isdigit(), f"Length should be numeric, got '{length}'"

    def test_dl_offset_points_to_dl_data(self, sample_california_license):
        """DL offset should point to actual DL data start."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        offset_str = result[23:27]
        offset = int(offset_str)

        # At offset, should find "DL" marker followed by data
        dl_marker = result[offset:offset+2]
        assert dl_marker == 'DL', \
            f"Offset {offset} should point to 'DL', found '{dl_marker}'"


class TestDLSubfileContent:
    """Tests for DL subfile content formatting."""

    def test_dl_subfile_starts_with_dl_marker(self, sample_california_license):
        """DL subfile data should start with 'DL' marker."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Find DL subfile start
        offset_str = result[23:27]
        offset = int(offset_str)

        assert result[offset:offset+2] == 'DL'

    def test_daq_field_comes_first(self, sample_california_license):
        """DAQ (license number) should be first field after DL marker."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Find DL subfile
        offset_str = result[23:27]
        offset = int(offset_str)

        # After "DL", should immediately see "DAQ"
        first_field = result[offset+2:offset+5]
        assert first_field == 'DAQ', \
            f"First field should be DAQ, got '{first_field}'"

    def test_fields_separated_by_newline(self, sample_california_license):
        """Fields should be separated by LF (\\n)."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Should have many newlines (one per field)
        newline_count = result.count('\n')
        # At minimum: compliance LF + ~20 DL fields + state fields
        assert newline_count >= 20, \
            f"Expected at least 20 newlines, got {newline_count}"

    def test_subfile_terminated_by_carriage_return(self, sample_california_license):
        """Each subfile should end with CR (\\r)."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Should have 3 CR: compliance + DL subfile + State subfile
        cr_count = result.count('\r')
        assert cr_count == 3, f"Expected 3 CRs, got {cr_count}"

    def test_all_required_fields_encoded(self, sample_california_license, aamva_required_fields):
        """All required AAMVA fields should appear in barcode."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        for field in aamva_required_fields:
            assert field in result, f"Required field {field} not found in barcode"


class TestFieldEncoding:
    """Tests for individual field encoding."""

    def test_field_format_is_tag_value_newline(self, sample_california_license):
        """Fields should be encoded as TAG+VALUE+LF."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Find DAQ field
        daq_start = result.find('DAQ')
        assert daq_start > 0, "DAQ field not found"

        # Should be followed by license number, then newline
        daq_end = result.find('\n', daq_start)
        daq_field = result[daq_start:daq_end]

        # Format: DAQ + license number
        assert daq_field.startswith('DAQ'), "Field should start with tag"
        assert len(daq_field) > 3, "Field should have value after tag"

    def test_empty_fields_omitted(self):
        """Fields with empty values should be omitted."""
        from src.core.barcode_formatter import format_barcode_data

        license_data = [{
            'subfile_type': 'DL',
            'DAQ': 'A1234567',
            'DCS': 'DOE',
            'DAC': 'JOHN',
            'DAD': '',  # Empty middle name
            'DBB': '01011990',
            'DBA': '01012030',
            'DBD': '11202025',
            'DAJ': 'CA',
        }]

        result = format_barcode_data(license_data)

        # DAD should not appear (empty)
        assert 'DAD\n' not in result, "Empty fields should be omitted"
        # But DAC and DCS should appear
        assert 'DAC' in result
        assert 'DCS' in result

    def test_field_values_uppercase(self, sample_california_license):
        """Field values should be uppercase."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Extract text portions (skip control characters)
        text_portion = result[21:]  # After header

        # All alpha characters should be uppercase
        for char in text_portion:
            if char.isalpha():
                assert char.isupper(), \
                    f"Found lowercase character: {char}"


class TestStateSubfile:
    """Tests for state-specific subfile encoding."""

    def test_state_subfile_present(self, sample_california_license):
        """State subfile should be present after DL subfile."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Should have ZC (California state subfile marker)
        assert 'ZC' in result, "California state subfile (ZC) not found"

    def test_state_subfile_type_matches_state(self):
        """State subfile type should match state (Z + first letter)."""
        from src.core.barcode_formatter import format_barcode_data

        # California
        ca_data = [{
            'subfile_type': 'DL',
            'DAQ': 'A1234567',
            'DAJ': 'CA',
        }, {
            'subfile_type': 'ZC',
        }]

        result = format_barcode_data(ca_data)
        assert 'ZC' in result, "Should have ZC for California"

        # New York
        ny_data = [{
            'subfile_type': 'DL',
            'DAQ': 'A123456789',
            'DAJ': 'NY',
        }, {
            'subfile_type': 'ZN',
        }]

        result = format_barcode_data(ny_data)
        assert 'ZN' in result, "Should have ZN for New York"


class TestASCIIEncoding:
    """Tests for ASCII encoding compliance."""

    def test_barcode_is_pure_ascii(self, sample_california_license):
        """Barcode should contain only ASCII characters."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Should encode to ASCII without error
        try:
            encoded = result.encode('ascii')
            assert isinstance(encoded, bytes)
        except UnicodeEncodeError as e:
            pytest.fail(f"Barcode contains non-ASCII characters: {e}")

    def test_roundtrip_encoding(self, sample_california_license):
        """Barcode should survive ASCII encode/decode roundtrip."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        encoded = result.encode('ascii')
        decoded = encoded.decode('ascii')

        assert decoded == result, "Roundtrip encoding changed data"

    def test_no_unicode_characters(self, sample_california_license):
        """Barcode should not contain Unicode characters."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        for char in result:
            assert ord(char) < 128, \
                f"Found non-ASCII character: {char} (U+{ord(char):04X})"


class TestBarcodeLength:
    """Tests for barcode length constraints."""

    def test_total_length_in_valid_range(self, sample_california_license):
        """Total barcode length should be 200-500 bytes."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        length = len(result.encode('ascii'))
        assert 200 <= length <= 500, \
            f"Barcode length {length} outside valid range 200-500"

    def test_length_not_excessive(self, sample_california_license):
        """Barcode should not be excessively long."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # PDF417 can handle up to 1850 bytes, but typical licenses are <500
        assert len(result) < 1000, "Barcode is excessively long"

    def test_minimum_length_met(self, sample_california_license):
        """Barcode must meet minimum length (header + required fields)."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Minimum: header (31) + minimal DL subfile (100+) + state (20+)
        assert len(result) >= 150, "Barcode is too short"


class TestOffsetCalculation:
    """Tests for offset and length calculation."""

    def test_offset_calculation_accurate(self, sample_california_license):
        """Calculated offset should point to correct location."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Get DL offset from header
        dl_offset = int(result[23:27])

        # Verify it points to "DL"
        marker = result[dl_offset:dl_offset+2]
        assert marker == 'DL', \
            f"Offset {dl_offset} points to '{marker}', not 'DL'"

    def test_length_calculation_accurate(self, sample_california_license):
        """Calculated length should match actual subfile length."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Get DL length from header
        dl_length = int(result[27:31])

        # Get actual DL subfile
        dl_offset = int(result[23:27])
        dl_end = result.find('\r', dl_offset)  # Find CR at end
        actual_length = dl_end - dl_offset

        assert dl_length == actual_length, \
            f"Declared length {dl_length} != actual {actual_length}"


class TestMultipleStates:
    """Tests for different state formats."""

    @pytest.mark.parametrize("state,expected_iin", [
        ('CA', '636014'),
        ('NY', '636001'),
        ('TX', '636015'),
        ('FL', '636010'),
    ])
    def test_correct_iin_for_states(self, state, expected_iin):
        """Each state should have correct IIN in barcode."""
        from src.core.barcode_formatter import format_barcode_data

        license_data = [{
            'subfile_type': 'DL',
            'DAQ': 'TEST123',
            'DAJ': state,
        }]

        result = format_barcode_data(license_data)

        iin = result[9:15]
        assert iin == expected_iin, \
            f"Expected IIN {expected_iin} for {state}, got {iin}"


class TestErrorHandling:
    """Tests for error handling in formatting."""

    def test_missing_subfile_type_raises_error(self):
        """Missing subfile_type should raise error."""
        from src.core.barcode_formatter import format_barcode_data

        invalid_data = [{
            # Missing subfile_type
            'DAQ': 'A1234567',
        }]

        with pytest.raises((KeyError, ValueError)):
            format_barcode_data(invalid_data)

    def test_empty_license_data_raises_error(self):
        """Empty license data should raise error."""
        from src.core.barcode_formatter import format_barcode_data

        with pytest.raises((ValueError, IndexError)):
            format_barcode_data([])

    def test_none_license_data_raises_error(self):
        """None license data should raise error."""
        from src.core.barcode_formatter import format_barcode_data

        with pytest.raises((TypeError, AttributeError)):
            format_barcode_data(None)

    def test_invalid_state_uses_default_iin(self):
        """Invalid/unknown state should use default IIN."""
        from src.core.barcode_formatter import format_barcode_data

        license_data = [{
            'subfile_type': 'DL',
            'DAQ': 'TEST123',
            'DAJ': 'XX',  # Invalid state
        }]

        result = format_barcode_data(license_data)

        # Should complete without error (may use default IIN)
        assert len(result) > 0


# ============================================================================
# PROPERTY-BASED TESTS
# ============================================================================

class TestPropertyBasedFormatting:
    """Property-based tests for barcode formatting."""

    @given(state=st.sampled_from(['CA', 'NY', 'TX', 'FL']))
    @settings(max_examples=20)
    def test_property_barcode_structure_invariants(self, state):
        """Property: Barcode structure is always valid regardless of state."""
        from src.core.barcode_formatter import format_barcode_data

        license_data = [{
            'subfile_type': 'DL',
            'DAQ': 'TEST123',
            'DCS': 'DOE',
            'DAC': 'JOHN',
            'DAJ': state,
        }]

        result = format_barcode_data(license_data)

        # Invariants that must hold
        assert result.startswith("@\n\x1E\r"), "Must start with compliance markers"
        assert "ANSI " in result, "Must contain ANSI marker"
        assert "DL" in result, "Must contain DL subfile"
        assert result.count('\r') >= 2, "Must have at least 2 CRs"

    @given(license_num=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                                min_size=7, max_size=18))
    @settings(max_examples=20)
    def test_property_license_number_encoded(self, license_num):
        """Property: Any valid license number should be encoded."""
        from src.core.barcode_formatter import format_barcode_data

        license_data = [{
            'subfile_type': 'DL',
            'DAQ': license_num,
            'DAJ': 'CA',
        }]

        result = format_barcode_data(license_data)

        # License number should appear after DAQ tag
        assert license_num in result, \
            f"License number {license_num} not found in barcode"


# ============================================================================
# INTEGRATION-STYLE TESTS
# ============================================================================

class TestCompleteFormatting:
    """Tests for complete formatting workflow."""

    def test_format_california_complete_license(self, sample_california_license):
        """Format complete California license without errors."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_california_license)

        # Should complete successfully
        assert len(result) > 0
        assert result.startswith("@\n\x1E\r")
        assert '636014' in result  # CA IIN
        assert 'A1234567' in result  # License number

    def test_format_new_york_complete_license(self, sample_new_york_license):
        """Format complete New York license without errors."""
        from src.core.barcode_formatter import format_barcode_data

        result = format_barcode_data(sample_new_york_license)

        assert len(result) > 0
        assert '636001' in result  # NY IIN

    def test_formatted_barcode_can_be_decoded(self, sample_california_license):
        """Formatted barcode should be decodable (roundtrip test)."""
        from src.core.barcode_formatter import format_barcode_data

        barcode_string = format_barcode_data(sample_california_license)

        # Should be valid ASCII that can be used for PDF417 encoding
        encoded_bytes = barcode_string.encode('ascii')
        decoded_string = encoded_bytes.decode('ascii')

        assert decoded_string == barcode_string, "Roundtrip failed"


class TestUtilityFunctions:
    """Tests for utility functions used in formatting."""

    def test_encode_field_basic(self):
        """Test basic field encoding."""
        from src.core.barcode_formatter import encode_field

        result = encode_field('DAQ', 'A1234567')

        assert result == 'DAQA1234567\n', \
            f"Expected 'DAQA1234567\\n', got '{result}'"

    def test_encode_field_empty_value_returns_empty(self):
        """Empty field values should return empty string."""
        from src.core.barcode_formatter import encode_field

        result = encode_field('DAD', '')

        assert result == '', "Empty values should return empty string"

    def test_build_header_structure(self):
        """Test header building."""
        from src.core.barcode_formatter import build_header

        header = build_header(iin='636014', dl_offset=100, dl_length=200)

        assert header.startswith('@\n\x1E\r'), "Missing compliance markers"
        assert 'ANSI ' in header, "Missing ANSI marker"
        assert '636014' in header, "Missing IIN"
        assert '10' in header, "Missing version"
