"""
License data generation logic.

This module provides the core business logic for generating realistic
AAMVA-compliant license data using the Faker library.
"""

import random
from datetime import datetime, date, timedelta
from typing import Optional
from faker import Faker

from .models import (
    License,
    LicenseSubfile,
    StateSubfile,
    Person,
    Address,
    PhysicalAttributes,
    Sex,
    EyeColor,
    HairColor,
    Race,
    TruncationStatus,
    ComplianceType,
)
from .state_formats import StateFormatRegistry, get_iin_for_state
from .validators import LicenseValidator


class LicenseGenerator:
    """Generator for realistic AAMVA-compliant license data.

    This class uses the Faker library to generate realistic personal
    information and combines it with state-specific license formats
    to create complete, valid license data structures.

    Attributes:
        faker: Faker instance for generating random data
        validator: Validator instance for checking generated data
    """

    def __init__(self, locale: str = "en_US", seed: Optional[int] = None) -> None:
        """Initialize the license generator.

        Args:
            locale: Faker locale for data generation (default: en_US)
            seed: Random seed for reproducible generation (default: None)
        """
        self.faker = Faker(locale)
        self.validator = LicenseValidator()

        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def generate_person(self, sex: Optional[Sex] = None) -> Person:
        """Generate realistic person data.

        Args:
            sex: Specific sex to use, or None for random

        Returns:
            Person object with realistic data
        """
        # Determine sex
        if sex is None:
            sex = random.choice([Sex.MALE, Sex.FEMALE])

        # Generate appropriate names based on sex
        if sex == Sex.MALE:
            first_name = self.faker.first_name_male().upper()
            middle_name = self.faker.first_name_male().upper()
        else:
            first_name = self.faker.first_name_female().upper()
            middle_name = self.faker.first_name_female().upper()

        last_name = self.faker.last_name().upper()

        # Generate date of birth (16-90 years old)
        dob = self.faker.date_of_birth(minimum_age=16, maximum_age=90)

        return Person(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=dob,
            sex=sex,
            first_name_truncated=TruncationStatus.NOT_TRUNCATED,
            middle_name_truncated=TruncationStatus.NOT_TRUNCATED,
            last_name_truncated=TruncationStatus.NOT_TRUNCATED,
        )

    def generate_physical_attributes(self, sex: Sex) -> PhysicalAttributes:
        """Generate realistic physical attributes.

        Args:
            sex: Person's sex (affects height/weight distributions)

        Returns:
            PhysicalAttributes object with realistic measurements
        """
        # Height ranges (in inches)
        if sex == Sex.MALE:
            height = random.randint(66, 76)  # 5'6" to 6'4"
            weight = random.randint(140, 240)  # 140-240 lbs
        else:
            height = random.randint(60, 70)  # 5'0" to 5'10"
            weight = random.randint(110, 180)  # 110-180 lbs

        # Eye color distribution (roughly realistic)
        eye_colors = [
            EyeColor.BROWN,
            EyeColor.BROWN,
            EyeColor.BROWN,  # Most common
            EyeColor.BLUE,
            EyeColor.BLUE,
            EyeColor.GREEN,
            EyeColor.HAZEL,
            EyeColor.GRAY,
        ]
        eye_color = random.choice(eye_colors)

        # Hair color distribution
        hair_colors = [
            HairColor.BROWN,
            HairColor.BROWN,
            HairColor.BROWN,  # Most common
            HairColor.BLACK,
            HairColor.BLACK,
            HairColor.BLOND,
            HairColor.RED,
            HairColor.GRAY,
        ]
        hair_color = random.choice(hair_colors)

        # Race distribution (for testing purposes - not realistic distribution)
        races = [Race.WHITE, Race.BLACK, Race.ASIAN, Race.INDIGENOUS, Race.UNKNOWN]
        race = random.choice(races)

        return PhysicalAttributes(
            height_inches=height,
            weight_pounds=weight,
            eye_color=eye_color,
            hair_color=hair_color,
            race=race,
        )

    def generate_address(self, state_code: Optional[str] = None) -> Address:
        """Generate realistic address.

        Args:
            state_code: Specific state code, or None for random US state

        Returns:
            Address object with realistic data
        """
        if state_code is None:
            state_code = self.faker.state_abbr()
        else:
            state_code = state_code.upper()

        street = self.faker.street_address().upper()
        city = self.faker.city().upper()

        # Generate 9-digit ZIP code
        zip5 = self.faker.zipcode().replace("-", "")[:5]
        zip4 = f"{random.randint(0, 9999):04d}"
        postal_code = zip5 + zip4

        return Address(
            street=street, city=city, state=state_code, postal_code=postal_code
        )

    def generate_license_subfile(
        self,
        person: Person,
        physical: PhysicalAttributes,
        address: Address,
        issue_date: Optional[date] = None,
    ) -> LicenseSubfile:
        """Generate DL subfile data.

        Args:
            person: Person data
            physical: Physical attributes
            address: Address data
            issue_date: Specific issue date, or None for today

        Returns:
            Complete LicenseSubfile object
        """
        if issue_date is None:
            issue_date = date.today()

        # Generate expiration date (5-10 years in future)
        years_valid = random.randint(5, 10)
        expiration_date = issue_date + timedelta(days=years_valid * 365)

        # Generate license number using state format
        license_number = StateFormatRegistry.generate_license_number(address.state)

        # Generate unique document discriminator
        discriminator = self.faker.unique.bothify(text="DOC#####").upper()

        # Random boolean fields
        organ_donor = random.choice([True, False])
        veteran = random.choice([True, False])
        limited_duration = random.choice([True, False])

        # Compliance type (mostly compliant)
        compliance_type = random.choices(
            [ComplianceType.FULLY_COMPLIANT, ComplianceType.NON_COMPLIANT],
            weights=[0.9, 0.1],  # 90% compliant
        )[0]

        return LicenseSubfile(
            license_number=license_number,
            vehicle_class="D",  # Standard driver
            restrictions="",
            endorsements="",
            expiration_date=expiration_date,
            issue_date=issue_date,
            document_discriminator=discriminator,
            country_code="USA",
            compliance_type=compliance_type,
            limited_duration=limited_duration,
            organ_donor=organ_donor,
            veteran=veteran,
            person=person,
            physical=physical,
            address=address,
        )

    def generate_state_subfile(self, state_code: str) -> StateSubfile:
        """Generate state-specific subfile.

        Args:
            state_code: Two-letter state code

        Returns:
            StateSubfile with jurisdiction-specific data
        """
        state_upper = state_code.upper()
        subfile_type = f"Z{state_upper[0]}"

        # Generate some test fields for the state subfile
        custom_fields = {
            f"{subfile_type}W": self.faker.last_name().upper(),  # County
            f"{subfile_type}T": "TEST STRING",
            f"{subfile_type}X": self.faker.bothify(
                text="?" + "#" * random.randint(1, 5)
            ).upper(),
        }

        return StateSubfile(
            state_code=state_upper, subfile_type=subfile_type, custom_fields=custom_fields
        )

    def generate_license(
        self, state_code: Optional[str] = None, sex: Optional[Sex] = None
    ) -> License:
        """Generate complete license data.

        Args:
            state_code: Specific state code, or None for random
            sex: Specific sex, or None for random

        Returns:
            Complete License object with all subfiles

        Raises:
            ValueError: If state_code is invalid
        """
        # Generate sex first (affects name generation)
        if sex is None:
            sex = random.choice([Sex.MALE, Sex.FEMALE])

        # Generate person data
        person = self.generate_person(sex=sex)

        # Generate physical attributes
        physical = self.generate_physical_attributes(sex=sex)

        # Generate address
        address = self.generate_address(state_code=state_code)
        actual_state = address.state

        # Validate state is supported
        if not StateFormatRegistry.is_state_supported(actual_state):
            raise ValueError(
                f"State {actual_state} is not supported. "
                f"Supported states: {', '.join(StateFormatRegistry.get_supported_states())}"
            )

        # Generate license subfile
        dl_subfile = self.generate_license_subfile(person, physical, address)

        # Generate state subfile
        state_subfile = self.generate_state_subfile(actual_state)

        # Get IIN for state
        iin = get_iin_for_state(actual_state)
        if iin is None:
            # Fallback to Arizona IIN if state not found
            iin = "636026"

        # Create complete license
        license_obj = License(
            dl_subfile=dl_subfile, state_subfile=state_subfile, jurisdiction_iin=iin
        )

        # Validate before returning
        self.validator.validate_license(license_obj)

        return license_obj

    def generate_batch(
        self, count: int, state_code: Optional[str] = None
    ) -> list[License]:
        """Generate multiple licenses.

        Args:
            count: Number of licenses to generate
            state_code: Specific state code, or None for random states

        Returns:
            List of License objects

        Raises:
            ValueError: If count is invalid or state_code is invalid
        """
        if count < 1:
            raise ValueError(f"Count must be at least 1, got {count}")

        if count > 10000:
            raise ValueError(
                f"Count {count} is too large (maximum 10000 for safety)"
            )

        licenses = []
        for _ in range(count):
            license_obj = self.generate_license(state_code=state_code)
            licenses.append(license_obj)

        return licenses

    def generate_for_all_states(self) -> dict[str, License]:
        """Generate one license for each supported state.

        Returns:
            Dictionary mapping state codes to License objects
        """
        licenses = {}
        for state_code in StateFormatRegistry.get_supported_states():
            license_obj = self.generate_license(state_code=state_code)
            licenses[state_code] = license_obj

        return licenses


class MinimalLicenseGenerator(LicenseGenerator):
    """Generator that creates minimal valid licenses.

    This generator creates licenses with minimal optional data,
    useful for testing edge cases and compact barcode generation.
    """

    def generate_license_subfile(
        self,
        person: Person,
        physical: PhysicalAttributes,
        address: Address,
        issue_date: Optional[date] = None,
    ) -> LicenseSubfile:
        """Generate minimal DL subfile."""
        subfile = super().generate_license_subfile(person, physical, address, issue_date)

        # Create new subfile with minimal fields (empty optionals)
        return LicenseSubfile(
            license_number=subfile.license_number,
            vehicle_class=subfile.vehicle_class,
            restrictions="",  # Empty
            endorsements="",  # Empty
            expiration_date=subfile.expiration_date,
            issue_date=subfile.issue_date,
            document_discriminator=subfile.document_discriminator,
            country_code=subfile.country_code,
            compliance_type=subfile.compliance_type,
            limited_duration=False,  # False
            organ_donor=False,  # False
            veteran=False,  # False
            person=person,
            physical=physical,
            address=address,
        )

    def generate_state_subfile(self, state_code: str) -> StateSubfile:
        """Generate minimal state subfile."""
        state_upper = state_code.upper()
        subfile_type = f"Z{state_upper[0]}"

        # Minimal custom fields
        return StateSubfile(
            state_code=state_upper, subfile_type=subfile_type, custom_fields={}
        )


def create_generator(
    generator_type: str = "standard", **kwargs
) -> LicenseGenerator:
    """Factory function for creating license generators.

    Args:
        generator_type: Type of generator ('standard' or 'minimal')
        **kwargs: Additional arguments passed to generator constructor

    Returns:
        Appropriate generator instance

    Raises:
        ValueError: If generator_type is invalid
    """
    generators = {"standard": LicenseGenerator, "minimal": MinimalLicenseGenerator}

    generator_class = generators.get(generator_type.lower())
    if generator_class is None:
        raise ValueError(
            f"Unknown generator type: {generator_type}. "
            f"Valid types: {', '.join(generators.keys())}"
        )

    return generator_class(**kwargs)
