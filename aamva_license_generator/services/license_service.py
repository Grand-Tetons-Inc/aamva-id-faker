"""
License Service - Main License Generation Orchestration

Orchestrates the complete license generation workflow:
- Data generation
- Validation
- Barcode encoding
- Image creation
- Error handling and recovery
"""

import os
import random
import string
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from threading import Lock
import logging

try:
    from faker import Faker
except ImportError:
    Faker = None

# Configure logging
logger = logging.getLogger(__name__)


class LicenseGenerationError(Exception):
    """Raised when license generation fails"""
    pass


class LicenseService:
    """
    Main service for license generation orchestration.

    Provides high-level API for generating realistic driver's license data
    with proper validation, error handling, and progress reporting.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LicenseService.

        Args:
            config: Configuration dictionary with optional keys:
                - seed: Random seed for reproducibility
                - locale: Faker locale (default: 'en_US')
                - validation_enabled: Enable validation (default: True)
                - iin_jurisdictions: Custom IIN mappings
                - state_formats: Custom state format rules
        """
        self.config = config or {}
        self._lock = Lock()  # Thread safety
        self._initialize_faker()
        self._load_iin_jurisdictions()
        self._load_state_formats()

    def _initialize_faker(self):
        """Initialize Faker instance with configured locale and seed."""
        if Faker is None:
            raise ImportError(
                "Faker library is required. Install with: pip install faker"
            )

        locale = self.config.get('locale', 'en_US')
        seed = self.config.get('seed')

        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
            logger.info(f"Initialized with seed: {seed}")

    def _load_iin_jurisdictions(self):
        """Load IIN jurisdiction mappings from config or use defaults."""
        # Default IIN jurisdictions (from generate_licenses.py)
        self.iin_jurisdictions = self.config.get('iin_jurisdictions', {
            "604426": {"jurisdiction": "Prince Edward Island", "abbr": "PE", "country": "Canada"},
            "604427": {"jurisdiction": "American Samoa", "abbr": "AS", "country": "USA"},
            "604428": {"jurisdiction": "Quebec", "abbr": "QC", "country": "Canada"},
            "604429": {"jurisdiction": "Yukon", "abbr": "YT", "country": "Canada"},
            "604430": {"jurisdiction": "Northern Marianna Islands", "abbr": "MP", "country": "USA"},
            "604431": {"jurisdiction": "Puerto Rico", "abbr": "PR", "country": "USA"},
            "604432": {"jurisdiction": "Alberta", "abbr": "AB", "country": "Canada"},
            "604433": {"jurisdiction": "Nunavut", "abbr": "NU", "country": "Canada"},
            "604434": {"jurisdiction": "Northwest Territories", "abbr": "NT", "country": "Canada"},
            "636000": {"jurisdiction": "Virginia", "abbr": "VA", "country": "USA"},
            "636001": {"jurisdiction": "New York", "abbr": "NY", "country": "USA"},
            "636002": {"jurisdiction": "Massachusetts", "abbr": "MA", "country": "USA"},
            "636003": {"jurisdiction": "Maryland", "abbr": "MD", "country": "USA"},
            "636004": {"jurisdiction": "North Carolina", "abbr": "NC", "country": "USA"},
            "636005": {"jurisdiction": "South Carolina", "abbr": "SC", "country": "USA"},
            "636006": {"jurisdiction": "Connecticut", "abbr": "CT", "country": "USA"},
            "636007": {"jurisdiction": "Louisiana", "abbr": "LA", "country": "USA"},
            "636008": {"jurisdiction": "Montana", "abbr": "MT", "country": "USA"},
            "636009": {"jurisdiction": "New Mexico", "abbr": "NM", "country": "USA"},
            "636010": {"jurisdiction": "Florida", "abbr": "FL", "country": "USA"},
            "636011": {"jurisdiction": "Delaware", "abbr": "DE", "country": "USA"},
            "636012": {"jurisdiction": "Ontario", "abbr": "ON", "country": "Canada"},
            "636013": {"jurisdiction": "Nova Scotia", "abbr": "NS", "country": "Canada"},
            "636014": {"jurisdiction": "California", "abbr": "CA", "country": "USA"},
            "636015": {"jurisdiction": "Texas", "abbr": "TX", "country": "USA"},
            "636016": {"jurisdiction": "Newfoundland", "abbr": "NF", "country": "Canada"},
            "636017": {"jurisdiction": "New Brunswick", "abbr": "NB", "country": "Canada"},
            "636018": {"jurisdiction": "Iowa", "abbr": "IA", "country": "USA"},
            "636019": {"jurisdiction": "Guam", "abbr": "GU", "country": "USA"},
            "636020": {"jurisdiction": "Colorado", "abbr": "CO", "country": "USA"},
            "636021": {"jurisdiction": "Arkansas", "abbr": "AR", "country": "USA"},
            "636022": {"jurisdiction": "Kansas", "abbr": "KS", "country": "USA"},
            "636023": {"jurisdiction": "Ohio", "abbr": "OH", "country": "USA"},
            "636024": {"jurisdiction": "Vermont", "abbr": "VT", "country": "USA"},
            "636025": {"jurisdiction": "Pennsylvania", "abbr": "PA", "country": "USA"},
            "636026": {"jurisdiction": "Arizona", "abbr": "AZ", "country": "USA"},
            "636028": {"jurisdiction": "British Columbia", "abbr": "BC", "country": "Canada"},
            "636029": {"jurisdiction": "Oregon", "abbr": "OR", "country": "USA"},
            "636030": {"jurisdiction": "Missouri", "abbr": "MO", "country": "USA"},
            "636031": {"jurisdiction": "Wisconsin", "abbr": "WI", "country": "USA"},
            "636032": {"jurisdiction": "Michigan", "abbr": "MI", "country": "USA"},
            "636033": {"jurisdiction": "Alabama", "abbr": "AL", "country": "USA"},
            "636034": {"jurisdiction": "North Dakota", "abbr": "ND", "country": "USA"},
            "636035": {"jurisdiction": "Illinois", "abbr": "IL", "country": "USA"},
            "636036": {"jurisdiction": "New Jersey", "abbr": "NJ", "country": "USA"},
            "636037": {"jurisdiction": "Indiana", "abbr": "IN", "country": "USA"},
            "636038": {"jurisdiction": "Minnesota", "abbr": "MN", "country": "USA"},
            "636039": {"jurisdiction": "New Hampshire", "abbr": "NH", "country": "USA"},
            "636040": {"jurisdiction": "Utah", "abbr": "UT", "country": "USA"},
            "636041": {"jurisdiction": "Maine", "abbr": "ME", "country": "USA"},
            "636042": {"jurisdiction": "South Dakota", "abbr": "SD", "country": "USA"},
            "636043": {"jurisdiction": "District of Columbia", "abbr": "DC", "country": "USA"},
            "636044": {"jurisdiction": "Saskatchewan", "abbr": "SK", "country": "Canada"},
            "636045": {"jurisdiction": "Washington", "abbr": "WA", "country": "USA"},
            "636046": {"jurisdiction": "Kentucky", "abbr": "KY", "country": "USA"},
            "636047": {"jurisdiction": "Hawaii", "abbr": "HI", "country": "USA"},
            "636048": {"jurisdiction": "Manitoba", "abbr": "MB", "country": "Canada"},
            "636049": {"jurisdiction": "Nevada", "abbr": "NV", "country": "USA"},
            "636050": {"jurisdiction": "Idaho", "abbr": "ID", "country": "USA"},
            "636051": {"jurisdiction": "Mississippi", "abbr": "MS", "country": "USA"},
            "636052": {"jurisdiction": "Rhode Island", "abbr": "RI", "country": "USA"},
            "636053": {"jurisdiction": "Tennessee", "abbr": "TN", "country": "USA"},
            "636054": {"jurisdiction": "Nebraska", "abbr": "NE", "country": "USA"},
            "636055": {"jurisdiction": "Georgia", "abbr": "GA", "country": "USA"},
        })

    def _load_state_formats(self):
        """Load state-specific license number formats."""
        # State-specific license number formats (extracted from generate_licenses.py)
        self.state_formats = self.config.get('state_formats', {
            'AL': lambda: self.faker.bothify(text='#' * random.randint(1, 7)),
            'AK': lambda: self.faker.bothify(text='#' * random.randint(1, 7)),
            'AZ': lambda: random.choice([
                self.faker.bothify(text='?' + ('#' * random.randint(1, 8))),
                self.faker.bothify(text='??' + ('#' * random.randint(2, 5))),
                self.faker.bothify(text='#' * 9)
            ]),
            'AR': lambda: self.faker.bothify(text='#' * random.randint(4, 9)),
            'CA': lambda: self.faker.bothify(text='?' + '#######'),
            'CO': lambda: random.choice([
                self.faker.bothify(text='#########'),
                self.faker.bothify(text='?' + '#' * random.randint(3, 6)),
                self.faker.bothify(text='??' + '#' * random.randint(2, 5))
            ]),
            'CT': lambda: self.faker.bothify(text='#########'),
            'DE': lambda: self.faker.bothify(text='#' * random.randint(1, 7)),
            'DC': lambda: self.faker.bothify(text='#' * random.choice([7, 9])),
            'FL': lambda: self.faker.bothify(text='?' + '############'),
            'GA': lambda: self.faker.numerify(text='%######').zfill(9),
            'HI': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 8),
                self.faker.bothify(text='#' * 9)
            ]),
            'ID': lambda: random.choice([
                self.faker.bothify(text='??######?'),
                self.faker.bothify(text='#' * 9)
            ]),
            'IL': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 11),
                self.faker.bothify(text='?' + '#' * 12)
            ]),
            'IN': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 9),
                self.faker.bothify(text='#' * 9),
                self.faker.bothify(text='#' * 10)
            ]),
            'IA': lambda: random.choice([
                self.faker.bothify(text='#' * 9),
                self.faker.bothify(text='###??####')
            ]),
            'KS': lambda: random.choice([
                self.faker.bothify(text='?#?#?'),
                self.faker.bothify(text='?' + '#' * 8),
                self.faker.bothify(text='#' * 9)
            ]),
            'KY': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 8),
                self.faker.bothify(text='?' + '#' * 9),
                self.faker.bothify(text='#' * 9)
            ]),
            'LA': lambda: self.faker.bothify(text='#' * random.randint(1, 9)),
            'ME': lambda: random.choice([
                self.faker.bothify(text='#' * 7),
                self.faker.bothify(text='#' * 7 + '?'),
                self.faker.bothify(text='#' * 8)
            ]),
            'MD': lambda: self.faker.bothify(text='?' + '#' * 12),
            'MA': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 8),
                self.faker.bothify(text='#' * 9)
            ]),
            'MI': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 10),
                self.faker.bothify(text='?' + '#' * 12)
            ]),
            'MN': lambda: self.faker.bothify(text='?' + '#' * 12),
            'MS': lambda: self.faker.bothify(text='#' * 9),
            'MO': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * random.randint(5, 9)),
                self.faker.bothify(text='?' + '#' * 6 + 'R'),
                self.faker.bothify(text='#' * 8 + '??'),
                self.faker.bothify(text='#' * 9 + '?'),
                self.faker.bothify(text='#' * 9)
            ]),
            'NY': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 7),
                self.faker.bothify(text='?' + '#' * 18),
                self.faker.bothify(text='#' * 8),
                self.faker.bothify(text='#' * 9),
                self.faker.bothify(text='#' * 16),
                self.faker.lexify(text='????????')
            ]),
            'TX': lambda: self.faker.bothify(text='#' * random.choice([7, 8])),
            'VA': lambda: random.choice([
                self.faker.bothify(text='?' + '#' * 9),
                self.faker.bothify(text='?' + '#' * 10),
                self.faker.bothify(text='?' + '#' * 11),
                self.faker.bothify(text='#' * 9)
            ]),
            'WI': lambda: self.faker.bothify(text='?' + '#' * 13),
            'WY': lambda: self.faker.bothify(text='#' * random.randint(9, 10)),
        })

    def get_iin_by_state(self, state_abbr: str) -> Optional[str]:
        """
        Get IIN code for a given state abbreviation.

        Args:
            state_abbr: Two-letter state abbreviation

        Returns:
            IIN code or None if not found
        """
        for iin, info in self.iin_jurisdictions.items():
            if info['abbr'].upper() == state_abbr.upper():
                return iin
        return None

    def generate_state_license_number(self, state: str) -> str:
        """
        Generate a license number conforming to state-specific format.

        Args:
            state: Two-letter state abbreviation

        Returns:
            License number string
        """
        state = state.upper()
        format_func = self.state_formats.get(state)

        if format_func:
            return format_func()
        else:
            # Default format: 9 digits
            return self.faker.bothify(text='#' * 9)

    def format_date(self, date: datetime) -> str:
        """
        Format date as MMDDYYYY for AAMVA standard.

        Args:
            date: Python datetime object

        Returns:
            Formatted date string (MMDDYYYY)
        """
        return date.strftime("%m%d%Y")

    def generate_state_subfile(
        self,
        dlid_data: Dict[str, str],
        custom_fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generate state-specific subfile with custom fields.

        Args:
            dlid_data: DL/ID data dictionary
            custom_fields: Optional custom field mappings

        Returns:
            State subfile data dictionary

        Raises:
            ValueError: If state abbreviation is missing
        """
        state_abbr = dlid_data.get("DAJ", "").upper()
        if not state_abbr:
            raise ValueError("State abbreviation (DAJ) is required in dlid_data")

        # Use first letter of state abbr for subfile label
        z_label = "Z" + state_abbr[0]

        if not custom_fields:
            # Default test fields
            county = self.faker.last_name_male().upper()
            county_label = z_label + "W"
            test_label = z_label + "T"

            subfile_data = {
                "subfile_type": z_label,
                county_label: county,
                test_label: "TEST STRING",
                z_label + "X": self.faker.bothify(text='?' + '#' * random.randint(1, 5)),
            }
        else:
            # Use custom fields (sorted)
            subfile_data = {
                "subfile_type": z_label,
                **{k: v for k, v in sorted(custom_fields.items())}
            }

        return subfile_data

    def generate_license_data(
        self,
        state: Optional[str] = None,
        **overrides
    ) -> List[Dict[str, str]]:
        """
        Generate complete license data with DL and state subfiles.

        Args:
            state: Optional state abbreviation (random if not provided)
            **overrides: Optional field overrides (e.g., DCS="SMITH")

        Returns:
            List containing [DL_data_dict, State_data_dict]

        Raises:
            LicenseGenerationError: If generation fails
        """
        try:
            with self._lock:
                # Determine state
                if state is None:
                    state = self.faker.state_abbr()
                else:
                    state = state.upper()

                # Generate dates
                dob = self.faker.date_of_birth(minimum_age=16, maximum_age=90)
                issue_date = datetime.today()
                exp_date = issue_date + timedelta(days=random.randint(365 * 5, 365 * 10))

                # Generate sex first for gender-appropriate names
                sex = random.choice(["1", "2"])  # 1=male, 2=female

                # Gender-appropriate names
                if sex == "1":  # Male
                    first_name = self.faker.first_name_male().upper()
                    middle_name = self.faker.first_name_male().upper()
                else:  # Female
                    first_name = self.faker.first_name_female().upper()
                    middle_name = self.faker.first_name_female().upper()

                # Physical characteristics
                eye = random.choice(["BLK", "BLU", "BRO", "GRY", "GRN", "HAZ", "MAR", "PNK", "DIC", "UNK"])
                hair = random.choice(["BLK", "BLN", "BRO", "GRY", "RED", "WHI", "SDY", "UNK"])
                race = random.choice(["W", "B", "A", "I", "U"])
                height = str(random.randint(58, 78))
                weight = str(random.randint(115, 275))

                # Flags
                veteran = random.choice(["0", "1"])
                organ_donor = random.choice(["0", "1"])
                truncation_family_name = random.choice(["N", "T", "U"])
                truncation_first_name = random.choice(["N", "T", "U"])
                truncation_middle_name = random.choice(["N", "T", "U"])
                dhs_compliance_type = random.choice(["N", "F"])
                limited_duration_document = random.choice(["1", "0"])

                # License metadata
                country_of_issuance = "USA"
                state_specific_vehicle_class = 'D'
                state_specific_restrictions = ''
                state_specific_endorsements = ''

                # Generate state-specific license number
                license_number = self.generate_state_license_number(state)

                # Build DL subfile
                dlid_data = {
                    "subfile_type": "DL",
                    "DAQ": license_number,
                    "DCA": state_specific_vehicle_class,
                    "DCB": state_specific_restrictions,
                    "DCD": state_specific_endorsements,
                    "DBA": self.format_date(exp_date),
                    "DCS": self.faker.last_name().upper(),
                    "DAC": first_name,
                    "DAD": middle_name,
                    "DBD": self.format_date(issue_date),
                    "DBB": self.format_date(dob),
                    "DBC": sex,
                    "DAY": eye,
                    "DAU": height,
                    "DAW": weight,
                    "DAZ": hair,
                    "DCL": race,
                    "DAG": self.faker.street_address().upper(),
                    "DAI": self.faker.city().upper(),
                    "DAJ": state,
                    "DAK": self.faker.zipcode().replace("-", "").ljust(9, "0"),
                    "DCF": self.faker.unique.bothify(text="DOC#####"),
                    "DCG": country_of_issuance,
                    "DDE": truncation_family_name,
                    "DDF": truncation_first_name,
                    "DDG": truncation_middle_name,
                    "DDA": dhs_compliance_type,
                    "DDB": self.format_date(issue_date),
                    "DDC": self.format_date(exp_date),
                    "DDD": limited_duration_document,
                    "DDK": organ_donor,
                    "DDL": veteran,
                }

                # Apply overrides
                dlid_data.update(overrides)

                # Generate state subfile
                state_data = self.generate_state_subfile(dlid_data, custom_fields={})

                return [dlid_data, state_data]

        except Exception as e:
            logger.error(f"License generation failed: {e}")
            raise LicenseGenerationError(f"Failed to generate license data: {e}") from e

    def generate_multiple(
        self,
        count: int,
        state: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[List[Dict[str, str]]]:
        """
        Generate multiple licenses with progress reporting.

        Args:
            count: Number of licenses to generate
            state: Optional state (random if None)
            progress_callback: Optional callback(current, total)

        Returns:
            List of license data arrays

        Raises:
            LicenseGenerationError: If generation fails
        """
        licenses = []

        for i in range(count):
            try:
                license_data = self.generate_license_data(state=state)
                licenses.append(license_data)

                if progress_callback:
                    progress_callback(i + 1, count)

            except Exception as e:
                logger.error(f"Failed to generate license {i+1}/{count}: {e}")
                raise

        return licenses

    def generate_all_states(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[List[Dict[str, str]]]:
        """
        Generate one license for each US state.

        Args:
            progress_callback: Optional callback(current, total, state)

        Returns:
            List of license data arrays (one per state)
        """
        states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
            'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
            'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
            'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
            'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]

        licenses = []
        total = len(states)

        for i, state in enumerate(states):
            license_data = self.generate_license_data(state=state)
            licenses.append(license_data)

            if progress_callback:
                progress_callback(i + 1, total, state)

        return licenses
