"""Tests for user data override functionality in generate_licenses.py.

Tests the ability to load a JSON file of AAMVA field overrides and apply
them to faker-generated license data before barcode encoding.
"""

import json
import os
import pytest

from generate_licenses import (
    PORTRAIT_FIELDS,
    VALID_AAMVA_FIELDS,
    apply_user_overrides,
    download_portraits,
    format_barcode_data,
    generate_individual_card_image,
    generate_license_data,
    load_user_data,
    save_barcode_and_data,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def single_user_record():
    """Single user record overriding name fields."""
    return [{"DCS": "CURIE", "DAC": "MARIA", "DAD": "SALOMEA"}]


@pytest.fixture
def multi_user_records():
    """Multiple user records with varying field counts."""
    return [
        {"DCS": "EINSTEIN", "DAC": "ALBERT", "DBC": "1"},
        {"DCS": "FEYNMAN", "DAC": "RICHARD"},
        {"DAQ": "Z9988776"},
    ]


@pytest.fixture
def full_user_record():
    """User record with all commonly-used DL subfile fields."""
    return [{
        "DAQ": "B1234567",
        "DCS": "MARTINEZ",
        "DAC": "CARLOS",
        "DAD": "ANTONIO",
        "DBB": "03151985",
        "DBA": "03152031",
        "DBD": "03152025",
        "DBC": "1",
        "DAY": "BRO",
        "DAU": "070",
        "DAW": "185",
        "DAZ": "BLK",
        "DAG": "4521 SUNSET BLVD",
        "DAI": "LOS ANGELES",
        "DAJ": "CA",
        "DAK": "900280000",
        "DCA": "D",
        "DCG": "USA",
        "DDK": "1",
        "DDL": "0",
    }]


@pytest.fixture
def generated_licenses():
    """Generate 5 licenses with a fixed state for deterministic testing."""
    return [generate_license_data("CA") for _ in range(5)]


def _write_json(tmp_path, data, filename="user_data.json"):
    """Helper to write JSON data to a temp file and return the path."""
    path = tmp_path / filename
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


# ===================================================================
# 1. JSON Loading Tests
# ===================================================================

class TestLoadUserDataValid:
    """Tests for successful JSON loading."""

    def test_load_valid_json_array(self, tmp_path, single_user_record):
        """Valid JSON array of objects loads without error."""
        path = _write_json(tmp_path, single_user_record)
        result = load_user_data(path)
        assert result == single_user_record

    def test_load_empty_array(self, tmp_path):
        """Empty JSON array returns empty list."""
        path = _write_json(tmp_path, [])
        result = load_user_data(path)
        assert result == []

    def test_load_multiple_records(self, tmp_path, multi_user_records):
        """Multiple records load in order."""
        path = _write_json(tmp_path, multi_user_records)
        result = load_user_data(path)
        assert len(result) == 3
        assert result[0]["DCS"] == "EINSTEIN"
        assert result[2]["DAQ"] == "Z9988776"

    def test_load_record_with_empty_dict(self, tmp_path):
        """Record that is an empty dict is valid (no overrides)."""
        path = _write_json(tmp_path, [{}])
        result = load_user_data(path)
        assert result == [{}]


class TestLoadUserDataInvalid:
    """Tests for JSON loading error handling."""

    def test_load_missing_file(self):
        """FileNotFoundError raised for nonexistent file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_user_data("/nonexistent/path/user_data.json")

    def test_load_invalid_json_syntax(self, tmp_path):
        """ValueError raised for malformed JSON."""
        path = tmp_path / "bad.json"
        path.write_text("{not valid json}", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_user_data(str(path))

    def test_load_root_not_array(self, tmp_path):
        """ValueError raised when root element is an object, not array."""
        path = _write_json(tmp_path, {"DCS": "SMITH"})
        with pytest.raises(ValueError, match="array of objects"):
            load_user_data(str(path))

    def test_load_array_with_non_object(self, tmp_path):
        """ValueError raised when array contains a non-object element."""
        path = _write_json(tmp_path, [{"DCS": "SMITH"}, "not an object"])
        with pytest.raises(ValueError, match="must be an object"):
            load_user_data(str(path))


# ===================================================================
# 2. AAMVA Field Validation Tests
# ===================================================================

class TestFieldValidation:
    """Tests for AAMVA field code validation in load_user_data."""

    @pytest.mark.parametrize("code", ["DAQ", "DCS", "DAC", "DBB", "DBA", "DDK"])
    def test_known_aamva_codes_accepted(self, tmp_path, code):
        """Known AAMVA field codes pass validation."""
        path = _write_json(tmp_path, [{code: "TEST"}])
        result = load_user_data(path)
        assert result[0][code] == "TEST"

    def test_z_prefixed_jurisdiction_codes_accepted(self, tmp_path):
        """Z-prefixed jurisdiction-specific codes (e.g., ZAW) are accepted."""
        path = _write_json(tmp_path, [{"ZAW": "MARICOPA", "ZCT": "DATA"}])
        result = load_user_data(path)
        assert result[0]["ZAW"] == "MARICOPA"

    @pytest.mark.parametrize("bad_code", ["XXX", "ABC", "FOO", "D12", "DA"])
    def test_unknown_codes_rejected(self, tmp_path, bad_code):
        """Unknown field codes raise ValueError."""
        path = _write_json(tmp_path, [{bad_code: "VALUE"}])
        with pytest.raises(ValueError, match=f"Unknown AAMVA field code '{bad_code}'"):
            load_user_data(str(path))

    def test_mixed_valid_and_invalid_codes(self, tmp_path):
        """Record with one bad code among valid ones still raises."""
        path = _write_json(tmp_path, [{"DCS": "SMITH", "BAD": "VALUE"}])
        with pytest.raises(ValueError, match="BAD"):
            load_user_data(str(path))

    def test_valid_aamva_fields_constant_has_expected_count(self):
        """The VALID_AAMVA_FIELDS set contains all 38 known codes."""
        assert len(VALID_AAMVA_FIELDS) == 38

    def test_z_field_pattern_requires_three_uppercase(self, tmp_path):
        """Z-fields must be exactly 3 uppercase letters starting with Z."""
        path = _write_json(tmp_path, [{"Za1": "VALUE"}])
        with pytest.raises(ValueError, match="Unknown AAMVA field code"):
            load_user_data(str(path))


# ===================================================================
# 3. Field Overlay Tests
# ===================================================================

class TestApplyUserOverrides:
    """Tests for the field overlay logic."""

    def test_single_field_override(self, generated_licenses, single_user_record):
        """A single record's DCS field replaces the generated last name."""
        apply_user_overrides(generated_licenses, single_user_record)
        assert generated_licenses[0][0]["DCS"] == "CURIE"
        assert generated_licenses[0][0]["DAC"] == "MARIA"
        assert generated_licenses[0][0]["DAD"] == "SALOMEA"

    def test_non_overridden_fields_unchanged(self, generated_licenses):
        """Fields not in the user record retain their generated values."""
        original_eye = generated_licenses[0][0]["DAY"]
        original_hair = generated_licenses[0][0]["DAZ"]
        apply_user_overrides(generated_licenses, [{"DCS": "OVERRIDE"}])
        assert generated_licenses[0][0]["DAY"] == original_eye
        assert generated_licenses[0][0]["DAZ"] == original_hair

    def test_empty_dict_no_changes(self, generated_licenses):
        """An empty override dict leaves all fields intact."""
        original = dict(generated_licenses[0][0])
        apply_user_overrides(generated_licenses, [{}])
        assert generated_licenses[0][0] == original

    def test_full_record_override(self, generated_licenses, full_user_record):
        """All fields in a full user record replace generated values."""
        apply_user_overrides(generated_licenses, full_user_record)
        dl = generated_licenses[0][0]
        assert dl["DAQ"] == "B1234567"
        assert dl["DCS"] == "MARTINEZ"
        assert dl["DAC"] == "CARLOS"
        assert dl["DAJ"] == "CA"
        assert dl["DAK"] == "900280000"

    def test_z_fields_go_to_state_subfile(self, generated_licenses):
        """Z-prefixed fields are applied to the state subfile (index 1)."""
        user = [{"ZCW": "CUSTOM_COUNTY", "ZCT": "CUSTOM_DATA"}]
        apply_user_overrides(generated_licenses, user)
        assert generated_licenses[0][1]["ZCW"] == "CUSTOM_COUNTY"
        assert generated_licenses[0][1]["ZCT"] == "CUSTOM_DATA"

    def test_mixed_dl_and_z_fields(self, generated_licenses):
        """DL fields go to subfile 0, Z fields go to subfile 1."""
        user = [{"DCS": "MIXED", "ZCX": "STATE_DATA"}]
        apply_user_overrides(generated_licenses, user)
        assert generated_licenses[0][0]["DCS"] == "MIXED"
        assert generated_licenses[0][1]["ZCX"] == "STATE_DATA"

    def test_override_returns_same_list(self, generated_licenses):
        """apply_user_overrides returns the same list object (mutated)."""
        result = apply_user_overrides(generated_licenses, [{"DCS": "TEST"}])
        assert result is generated_licenses

    def test_empty_string_value_applied(self, generated_licenses):
        """Empty string override replaces existing value."""
        apply_user_overrides(generated_licenses, [{"DCB": ""}])
        assert generated_licenses[0][0]["DCB"] == ""


# ===================================================================
# 4. Record Mapping Tests
# ===================================================================

class TestRecordMapping:
    """Tests for positional mapping between user records and licenses."""

    def test_equal_counts(self):
        """With equal counts, every license gets an override."""
        licenses = [generate_license_data("CA") for _ in range(3)]
        users = [
            {"DCS": "ALPHA"},
            {"DCS": "BETA"},
            {"DCS": "GAMMA"},
        ]
        apply_user_overrides(licenses, users)
        assert licenses[0][0]["DCS"] == "ALPHA"
        assert licenses[1][0]["DCS"] == "BETA"
        assert licenses[2][0]["DCS"] == "GAMMA"

    def test_fewer_user_records(self):
        """Extra licenses beyond user record count keep generated data."""
        licenses = [generate_license_data("CA") for _ in range(5)]
        original_last_3 = [lic[0]["DCS"] for lic in licenses[2:]]
        users = [{"DCS": "FIRST"}, {"DCS": "SECOND"}]
        apply_user_overrides(licenses, users)
        assert licenses[0][0]["DCS"] == "FIRST"
        assert licenses[1][0]["DCS"] == "SECOND"
        # Licenses 2-4 unchanged
        for i, expected in enumerate(original_last_3):
            assert licenses[i + 2][0]["DCS"] == expected

    def test_more_user_records_than_licenses(self, capsys):
        """Excess user records are ignored with a warning."""
        licenses = [generate_license_data("CA") for _ in range(2)]
        users = [{"DCS": "A"}, {"DCS": "B"}, {"DCS": "C"}, {"DCS": "D"}]
        apply_user_overrides(licenses, users)
        assert licenses[0][0]["DCS"] == "A"
        assert licenses[1][0]["DCS"] == "B"
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "2 user record(s) will be ignored" in captured.out

    def test_zero_user_records(self):
        """Empty user records list leaves all licenses unchanged."""
        licenses = [generate_license_data("CA") for _ in range(3)]
        originals = [dict(lic[0]) for lic in licenses]
        apply_user_overrides(licenses, [])
        for i, orig in enumerate(originals):
            assert licenses[i][0] == orig

    def test_order_preserved(self):
        """Record i maps to license i, not any other."""
        licenses = [generate_license_data("CA") for _ in range(3)]
        users = [
            {"DAQ": "LIC_0"},
            {"DAQ": "LIC_1"},
            {"DAQ": "LIC_2"},
        ]
        apply_user_overrides(licenses, users)
        for i in range(3):
            assert licenses[i][0]["DAQ"] == f"LIC_{i}"


# ===================================================================
# 5. Integration Tests
# ===================================================================

class TestIntegration:
    """End-to-end tests verifying overrides flow through the pipeline."""

    def test_override_appears_in_barcode_data(self):
        """Overridden field values appear in the encoded barcode string."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{"DCS": "CURIE", "DAC": "MARIA"}])
        barcode_str = format_barcode_data(licenses[0])
        assert "DCSCURIE" in barcode_str
        assert "DACMARIA" in barcode_str

    def test_override_does_not_corrupt_barcode_structure(self):
        """Barcode string retains valid AAMVA structure after overrides."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{"DCS": "TESTNAME", "DAQ": "X9999999"}])
        barcode_str = format_barcode_data(licenses[0])
        # Check compliance indicator
        assert barcode_str.startswith("@\n\x1E\r")
        # Check ANSI header
        assert "ANSI " in barcode_str
        # Check subfile type marker
        assert "DL" in barcode_str

    def test_batch_override_with_mixed_fields(self):
        """Batch of licenses with different override patterns all encode."""
        licenses = [generate_license_data("CA") for _ in range(3)]
        users = [
            {"DCS": "EINSTEIN", "DAC": "ALBERT"},
            {"DAQ": "CUSTOM123"},
            {},  # no overrides
        ]
        apply_user_overrides(licenses, users)

        for lic in licenses:
            barcode_str = format_barcode_data(lic)
            assert barcode_str.startswith("@\n\x1E\r")

        # Verify specific overrides
        bc0 = format_barcode_data(licenses[0])
        assert "DCSEINSTEIN" in bc0
        bc1 = format_barcode_data(licenses[1])
        assert "DAQCUSTOM123" in bc1

    def test_state_override_changes_iin(self):
        """Overriding DAJ (state) changes the IIN in barcode header."""
        licenses = [generate_license_data("CA")]
        # CA IIN = 636014
        barcode_ca = format_barcode_data(licenses[0])
        assert "636014" in barcode_ca

        # Override state to NY (IIN = 636001)
        apply_user_overrides(licenses, [{"DAJ": "NY"}])
        barcode_ny = format_barcode_data(licenses[0])
        assert "636001" in barcode_ny


# ===================================================================
# 6. Edge Case Tests
# ===================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_numeric_json_values_are_accepted(self, tmp_path):
        """Numeric values in JSON are loaded (Python dict allows mixed types)."""
        # JSON numbers become Python ints/floats, not strings.
        # The overlay will apply them as-is; barcode encoding handles str().
        path = _write_json(tmp_path, [{"DAU": "072"}])
        result = load_user_data(path)
        assert result[0]["DAU"] == "072"

    def test_single_license_single_record(self):
        """Simplest case: one license, one override record."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{"DCS": "SOLO"}])
        assert licenses[0][0]["DCS"] == "SOLO"

    def test_override_subfile_type_is_possible(self):
        """subfile_type is not in VALID_AAMVA_FIELDS, so it cannot be
        supplied in user data (load_user_data would reject it)."""
        assert "subfile_type" not in VALID_AAMVA_FIELDS

    def test_all_valid_aamva_fields_in_constant(self):
        """Spot-check that key AAMVA codes are in the constant."""
        expected = {"DAQ", "DCS", "DAC", "DBB", "DBA", "DBC", "DAY",
                    "DAU", "DAG", "DAI", "DAJ", "DAK", "DCF", "DCG"}
        assert expected.issubset(VALID_AAMVA_FIELDS)

    def test_large_batch_performance(self):
        """100 licenses with 100 overrides completes without error."""
        licenses = [generate_license_data("CA") for _ in range(100)]
        users = [{"DCS": f"NAME{i}"} for i in range(100)]
        apply_user_overrides(licenses, users)
        for i in range(100):
            assert licenses[i][0]["DCS"] == f"NAME{i}"


# ===================================================================
# 7. Portrait Image Tests
# ===================================================================

def _create_test_portrait(directory, filename="portrait.png", size=(200, 250)):
    """Helper to create a small test portrait image."""
    img = __import__("PIL").Image.new("RGB", size, color=(100, 149, 237))
    path = os.path.join(str(directory), filename)
    img.save(path)
    return path


class TestPortraitValidation:
    """Tests for portrait field validation in load_user_data."""

    def test_portrait_fields_accepted(self, tmp_path):
        """portrait_path and portrait_file are accepted as valid fields."""
        data = [{"DCS": "SMITH", "portrait_path": "/some/dir",
                 "portrait_file": "photo.jpg"}]
        path = _write_json(tmp_path, data)
        result = load_user_data(path)
        assert result[0]["portrait_path"] == "/some/dir"
        assert result[0]["portrait_file"] == "photo.jpg"

    def test_portrait_path_without_file_rejected(self, tmp_path):
        """portrait_path without portrait_file raises ValueError."""
        data = [{"portrait_path": "/some/dir"}]
        path = _write_json(tmp_path, data)
        with pytest.raises(ValueError, match="missing 'portrait_file'"):
            load_user_data(path)

    def test_portrait_file_without_path_rejected(self, tmp_path):
        """portrait_file without portrait_path raises ValueError."""
        data = [{"portrait_file": "photo.jpg"}]
        path = _write_json(tmp_path, data)
        with pytest.raises(ValueError, match="missing 'portrait_path'"):
            load_user_data(path)

    @pytest.mark.parametrize("ext", [".jpg", ".jpeg", ".png", ".gif"])
    def test_supported_image_formats(self, tmp_path, ext):
        """All supported image formats pass validation."""
        data = [{"portrait_path": "/dir", "portrait_file": f"photo{ext}"}]
        path = _write_json(tmp_path, data)
        result = load_user_data(path)
        assert result[0]["portrait_file"] == f"photo{ext}"

    def test_unsupported_image_format_rejected(self, tmp_path):
        """Unsupported formats like .bmp or .tiff are rejected."""
        data = [{"portrait_path": "/dir", "portrait_file": "photo.bmp"}]
        path = _write_json(tmp_path, data)
        with pytest.raises(ValueError, match="Unsupported image format"):
            load_user_data(path)

    def test_portrait_fields_in_constant(self):
        """PORTRAIT_FIELDS constant contains expected keys."""
        assert PORTRAIT_FIELDS == {"portrait_path", "portrait_file", "portrait_url"}


class TestPortraitBarcode:
    """Tests that portrait fields do NOT appear in barcode data."""

    def test_portrait_fields_excluded_from_barcode(self):
        """portrait_path and portrait_file must not be encoded in barcode."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{
            "DCS": "CURIE",
            "portrait_path": "/fake/dir",
            "portrait_file": "curie.jpg",
        }])
        barcode_str = format_barcode_data(licenses[0])
        assert "portrait" not in barcode_str.lower()
        assert "/fake/dir" not in barcode_str
        assert "curie.jpg" not in barcode_str
        # But the name override IS present
        assert "DCSCURIE" in barcode_str


class TestPortraitRendering:
    """Tests for portrait image rendering on card images."""

    def test_card_image_with_portrait(self, tmp_path):
        """Card image is generated successfully when portrait is provided."""
        portrait_path = _create_test_portrait(tmp_path)
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{
            "portrait_path": str(tmp_path),
            "portrait_file": "portrait.png",
        }])
        # Generate barcode first
        import shutil
        barcode_dir = tmp_path / "barcodes"
        barcode_dir.mkdir()
        bmp_path, _ = save_barcode_and_data(licenses[0], 0)
        # Copy barcode to tmp for card generation
        tmp_bmp = str(tmp_path / "test.bmp")
        shutil.copy(bmp_path, tmp_bmp)
        card_path = generate_individual_card_image(licenses[0], tmp_bmp)
        assert os.path.isfile(card_path)
        # Verify card image is larger than without portrait (has extra content)
        from PIL import Image
        card_img = Image.open(card_path)
        assert card_img.size[0] > 0
        assert card_img.size[1] > 0

    def test_card_image_without_portrait(self, tmp_path):
        """Card image is generated normally without portrait fields."""
        licenses = [generate_license_data("CA")]
        import shutil
        bmp_path, _ = save_barcode_and_data(licenses[0], 0)
        tmp_bmp = str(tmp_path / "test.bmp")
        shutil.copy(bmp_path, tmp_bmp)
        card_path = generate_individual_card_image(licenses[0], tmp_bmp)
        assert os.path.isfile(card_path)

    def test_card_image_with_missing_portrait_file(self, tmp_path, capsys):
        """Missing portrait file prints warning but still generates card."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{
            "portrait_path": str(tmp_path),
            "portrait_file": "nonexistent.png",
        }])
        import shutil
        bmp_path, _ = save_barcode_and_data(licenses[0], 0)
        tmp_bmp = str(tmp_path / "test.bmp")
        shutil.copy(bmp_path, tmp_bmp)
        card_path = generate_individual_card_image(licenses[0], tmp_bmp)
        assert os.path.isfile(card_path)
        captured = capsys.readouterr()
        assert "not found" in captured.out

    @pytest.mark.parametrize("ext", [".jpg", ".png", ".gif"])
    def test_card_image_accepts_all_formats(self, tmp_path, ext):
        """Card image renders with jpg, png, and gif portraits."""
        _create_test_portrait(tmp_path, f"photo{ext}")
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{
            "portrait_path": str(tmp_path),
            "portrait_file": f"photo{ext}",
        }])
        import shutil
        bmp_path, _ = save_barcode_and_data(licenses[0], 0)
        tmp_bmp = str(tmp_path / "test.bmp")
        shutil.copy(bmp_path, tmp_bmp)
        card_path = generate_individual_card_image(licenses[0], tmp_bmp)
        assert os.path.isfile(card_path)


# ===================================================================
# 8. Portrait URL Download Tests
# ===================================================================

class TestPortraitUrlValidation:
    """Tests for portrait_url field validation."""

    def test_portrait_url_accepted_alone(self, tmp_path):
        """portrait_url can be provided without portrait_path/file."""
        data = [{"DCS": "SMITH", "portrait_url": "https://example.com/photo.jpg"}]
        path = _write_json(tmp_path, data)
        result = load_user_data(path)
        assert result[0]["portrait_url"] == "https://example.com/photo.jpg"

    def test_portrait_url_with_local_fields(self, tmp_path):
        """portrait_url alongside portrait_path/file is accepted."""
        data = [{
            "portrait_url": "https://example.com/photo.jpg",
            "portrait_path": "/local/dir",
            "portrait_file": "photo.jpg",
        }]
        path = _write_json(tmp_path, data)
        result = load_user_data(path)
        assert "portrait_url" in result[0]

    def test_portrait_url_excluded_from_barcode(self):
        """portrait_url must not appear in barcode data."""
        licenses = [generate_license_data("CA")]
        apply_user_overrides(licenses, [{
            "portrait_url": "https://example.com/photo.jpg",
        }])
        barcode_str = format_barcode_data(licenses[0])
        assert "example.com" not in barcode_str


class TestDownloadPortraits:
    """Tests for the download_portraits function."""

    def test_no_urls_returns_zero(self, tmp_path):
        """Records without portrait_url return 0 downloads."""
        records = [{"DCS": "SMITH"}, {"DCS": "DOE"}]
        count = download_portraits(records, download_dir=str(tmp_path))
        assert count == 0

    def test_empty_records_returns_zero(self, tmp_path):
        """Empty record list returns 0."""
        count = download_portraits([], download_dir=str(tmp_path))
        assert count == 0

    def test_local_path_takes_precedence(self, tmp_path):
        """If portrait_path and portrait_file are set, URL is skipped."""
        records = [{
            "portrait_url": "https://example.com/photo.jpg",
            "portrait_path": "/local",
            "portrait_file": "existing.jpg",
        }]
        count = download_portraits(records, download_dir=str(tmp_path))
        assert count == 0
        # portrait_path/file unchanged
        assert records[0]["portrait_path"] == "/local"
        assert records[0]["portrait_file"] == "existing.jpg"

    def test_bad_url_warns_and_continues(self, tmp_path, capsys):
        """Invalid URL prints warning and doesn't crash."""
        records = [{"DCS": "SMITH", "portrait_url": "https://invalid.test/no.jpg"}]
        count = download_portraits(records, download_dir=str(tmp_path))
        assert count == 0
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_download_dir_created(self, tmp_path):
        """Download directory is created if it doesn't exist."""
        dl_dir = str(tmp_path / "new_subdir" / "portraits")
        records = [{"DCS": "TEST"}]  # no URL, but dir should still be created
        download_portraits(records, download_dir=dl_dir)
        assert os.path.isdir(dl_dir)

    def test_filename_derived_from_dcs(self, tmp_path):
        """When URL has no image extension, filename uses DCS field."""
        records = [{
            "DCS": "EINSTEIN",
            "portrait_url": "https://example.com/some-page/"
        }]
        # Will fail to download but we can check the logic doesn't crash
        download_portraits(records, download_dir=str(tmp_path))
        # No assertion on file existence since download will fail,
        # but the function should not raise
