"""
State-specific license number format generators.

This module provides a registry pattern for generating license numbers
that conform to each state's specific format requirements.
"""

import random
import string
from typing import Callable, Optional
from abc import ABC, abstractmethod


class LicenseNumberGenerator(ABC):
    """Abstract base class for state-specific license number generators."""

    @abstractmethod
    def generate(self) -> str:
        """Generate a license number conforming to state format.

        Returns:
            Valid license number for the state
        """
        pass

    @staticmethod
    def random_letter() -> str:
        """Generate a random uppercase letter."""
        return random.choice(string.ascii_uppercase)

    @staticmethod
    def random_digit() -> str:
        """Generate a random digit."""
        return random.choice(string.digits)

    @staticmethod
    def random_letters(n: int) -> str:
        """Generate n random uppercase letters."""
        return "".join(random.choices(string.ascii_uppercase, k=n))

    @staticmethod
    def random_digits(n: int) -> str:
        """Generate n random digits."""
        return "".join(random.choices(string.digits, k=n))


class CaliforniaGenerator(LicenseNumberGenerator):
    """California: 1 letter + 7 digits (e.g., A1234567)."""

    def generate(self) -> str:
        return self.random_letter() + self.random_digits(7)


class NewYorkGenerator(LicenseNumberGenerator):
    """New York: Multiple formats allowed."""

    def generate(self) -> str:
        formats = [
            lambda: self.random_letter() + self.random_digits(7),  # A1234567
            lambda: self.random_letter() + self.random_digits(18),  # A123456789012345678
            lambda: self.random_digits(8),  # 12345678
            lambda: self.random_digits(9),  # 123456789
            lambda: self.random_digits(16),  # 1234567890123456
            lambda: self.random_letters(8),  # ABCDEFGH
        ]
        return random.choice(formats)()


class TexasGenerator(LicenseNumberGenerator):
    """Texas: 7 or 8 digits."""

    def generate(self) -> str:
        length = random.choice([7, 8])
        return self.random_digits(length)


class FloridaGenerator(LicenseNumberGenerator):
    """Florida: 1 letter + 12 digits (e.g., A123456789012)."""

    def generate(self) -> str:
        return self.random_letter() + self.random_digits(12)


class ArizonaGenerator(LicenseNumberGenerator):
    """Arizona: Multiple formats allowed."""

    def generate(self) -> str:
        formats = [
            lambda: self.random_letter() + self.random_digits(random.randint(1, 8)),
            lambda: self.random_letters(2) + self.random_digits(random.randint(2, 5)),
            lambda: self.random_digits(9),
        ]
        return random.choice(formats)()


class ColoradoGenerator(LicenseNumberGenerator):
    """Colorado: Multiple formats allowed."""

    def generate(self) -> str:
        formats = [
            lambda: self.random_digits(9),
            lambda: self.random_letter() + self.random_digits(random.randint(3, 6)),
            lambda: self.random_letters(2) + self.random_digits(random.randint(2, 5)),
        ]
        return random.choice(formats)()


class IllinoisGenerator(LicenseNumberGenerator):
    """Illinois: 1 letter + 11 or 12 digits."""

    def generate(self) -> str:
        length = random.choice([11, 12])
        return self.random_letter() + self.random_digits(length)


class PennsylvaniaGenerator(LicenseNumberGenerator):
    """Pennsylvania: 8 digits."""

    def generate(self) -> str:
        return self.random_digits(8)


class OhioGenerator(LicenseNumberGenerator):
    """Ohio: 2 letters + 6 digits (e.g., AB123456)."""

    def generate(self) -> str:
        return self.random_letters(2) + self.random_digits(6)


class MichiganGenerator(LicenseNumberGenerator):
    """Michigan: 1 letter + 10 or 12 digits."""

    def generate(self) -> str:
        length = random.choice([10, 12])
        return self.random_letter() + self.random_digits(length)


class GeorgiaGenerator(LicenseNumberGenerator):
    """Georgia: 7-9 digits (zero-padded to 9)."""

    def generate(self) -> str:
        num = random.randint(1, 999999999)
        return str(num).zfill(9)


class NorthCarolinaGenerator(LicenseNumberGenerator):
    """North Carolina: 1-12 digits."""

    def generate(self) -> str:
        length = random.randint(1, 12)
        return self.random_digits(length)


class MarylandGenerator(LicenseNumberGenerator):
    """Maryland: 1 letter + 12 digits."""

    def generate(self) -> str:
        return self.random_letter() + self.random_digits(12)


class WashingtonGenerator(LicenseNumberGenerator):
    """Washington: 7 alphanumeric characters."""

    def generate(self) -> str:
        # Pattern: LLLLLNN where L=letter, N=number
        return self.random_letters(5) + self.random_digits(2) + self.random_letter()


class MassachusettsGenerator(LicenseNumberGenerator):
    """Massachusetts: 1 letter + 8 digits or 9 digits."""

    def generate(self) -> str:
        if random.choice([True, False]):
            return self.random_letter() + self.random_digits(8)
        else:
            return self.random_digits(9)


class DefaultGenerator(LicenseNumberGenerator):
    """Default generator for states without specific format: 9 digits."""

    def generate(self) -> str:
        return self.random_digits(9)


class StateFormatRegistry:
    """Registry for state-specific license number generators.

    This class manages the mapping between state codes and their
    corresponding license number format generators.
    """

    _generators: dict[str, type[LicenseNumberGenerator]] = {
        "AL": DefaultGenerator,  # Alabama: 1-7 digits
        "AK": DefaultGenerator,  # Alaska: 1-7 digits
        "AZ": ArizonaGenerator,
        "AR": DefaultGenerator,  # Arkansas: 4-9 digits
        "CA": CaliforniaGenerator,
        "CO": ColoradoGenerator,
        "CT": DefaultGenerator,  # Connecticut: 9 digits
        "DE": DefaultGenerator,  # Delaware: 1-7 digits
        "DC": DefaultGenerator,  # DC: 7 or 9 digits
        "FL": FloridaGenerator,
        "GA": GeorgiaGenerator,
        "HI": DefaultGenerator,  # Hawaii: 1 letter + 8 digits or 9 digits
        "ID": DefaultGenerator,  # Idaho: 2 letters + 6 digits + 1 letter or 9 digits
        "IL": IllinoisGenerator,
        "IN": DefaultGenerator,  # Indiana: 1 letter + 9 digits or 9-10 digits
        "IA": DefaultGenerator,  # Iowa: 9 digits or 3 digits + 2 letters + 4 digits
        "KS": DefaultGenerator,  # Kansas: Various formats
        "KY": DefaultGenerator,  # Kentucky: 1 letter + 8-9 digits or 9 digits
        "LA": DefaultGenerator,  # Louisiana: 1-9 digits
        "ME": DefaultGenerator,  # Maine: 7-8 digits
        "MD": MarylandGenerator,
        "MA": MassachusettsGenerator,
        "MI": MichiganGenerator,
        "MN": DefaultGenerator,  # Minnesota: 1 letter + 12 digits
        "MS": DefaultGenerator,  # Mississippi: 9 digits
        "MO": DefaultGenerator,  # Missouri: Various formats
        "MT": DefaultGenerator,  # Montana: Various formats
        "NE": DefaultGenerator,  # Nebraska: 1 letter + 6-8 digits
        "NV": DefaultGenerator,  # Nevada: 9-10 digits or 12 digits
        "NH": DefaultGenerator,  # New Hampshire: 2 digits + 3 letters + 5 digits
        "NJ": DefaultGenerator,  # New Jersey: 1 letter + 14 digits
        "NM": DefaultGenerator,  # New Mexico: 8-9 digits
        "NY": NewYorkGenerator,
        "NC": NorthCarolinaGenerator,
        "ND": DefaultGenerator,  # North Dakota: 9 digits or 3 letters + 6 digits
        "OH": OhioGenerator,
        "OK": DefaultGenerator,  # Oklahoma: 1 letter + 9 digits or 9 digits
        "OR": DefaultGenerator,  # Oregon: 1-9 digits
        "PA": PennsylvaniaGenerator,
        "RI": DefaultGenerator,  # Rhode Island: 7 digits or 1 letter + 6 digits
        "SC": DefaultGenerator,  # South Carolina: 5-11 digits
        "SD": DefaultGenerator,  # South Dakota: 6-10 digits or 12 digits
        "TN": DefaultGenerator,  # Tennessee: 7-9 digits
        "TX": TexasGenerator,
        "UT": DefaultGenerator,  # Utah: 4-10 digits
        "VT": DefaultGenerator,  # Vermont: 8 digits or 7 digits + letter
        "VA": DefaultGenerator,  # Virginia: 1 letter + 8-11 digits or 9 digits
        "WA": WashingtonGenerator,
        "WV": DefaultGenerator,  # West Virginia: 7 digits or 1-2 letters + 5-6 digits
        "WI": DefaultGenerator,  # Wisconsin: 1 letter + 13 digits
        "WY": DefaultGenerator,  # Wyoming: 9-10 digits
    }

    @classmethod
    def generate_license_number(cls, state_code: str) -> str:
        """Generate a license number for the specified state.

        Args:
            state_code: Two-letter state abbreviation (e.g., 'CA', 'NY')

        Returns:
            License number conforming to state format

        Raises:
            ValueError: If state code is invalid
        """
        state_upper = state_code.upper()

        if state_upper not in cls._generators:
            raise ValueError(
                f"Unknown state code: {state_code}. "
                f"Valid codes: {', '.join(sorted(cls._generators.keys()))}"
            )

        generator_class = cls._generators[state_upper]
        generator = generator_class()
        return generator.generate()

    @classmethod
    def register_generator(
        cls, state_code: str, generator_class: type[LicenseNumberGenerator]
    ) -> None:
        """Register a custom generator for a state.

        Args:
            state_code: Two-letter state abbreviation
            generator_class: Generator class to use for this state
        """
        state_upper = state_code.upper()
        cls._generators[state_upper] = generator_class

    @classmethod
    def get_supported_states(cls) -> list[str]:
        """Get list of supported state codes.

        Returns:
            Sorted list of two-letter state codes
        """
        return sorted(cls._generators.keys())

    @classmethod
    def is_state_supported(cls, state_code: str) -> bool:
        """Check if a state code is supported.

        Args:
            state_code: Two-letter state abbreviation

        Returns:
            True if state is supported, False otherwise
        """
        return state_code.upper() in cls._generators


# IIN (Issuer Identification Number) registry
# Source: AAMVA official IIN list
IIN_REGISTRY: dict[str, str] = {
    "AL": "636033",  # Alabama
    "AK": "636059",  # Alaska
    "AZ": "636026",  # Arizona
    "AR": "636021",  # Arkansas
    "CA": "636014",  # California
    "CO": "636020",  # Colorado
    "CT": "636006",  # Connecticut
    "DE": "636011",  # Delaware
    "DC": "636043",  # District of Columbia
    "FL": "636010",  # Florida
    "GA": "636055",  # Georgia
    "HI": "636047",  # Hawaii
    "ID": "636050",  # Idaho
    "IL": "636035",  # Illinois
    "IN": "636037",  # Indiana
    "IA": "636018",  # Iowa
    "KS": "636022",  # Kansas
    "KY": "636046",  # Kentucky
    "LA": "636007",  # Louisiana
    "ME": "636041",  # Maine
    "MD": "636003",  # Maryland
    "MA": "636002",  # Massachusetts
    "MI": "636032",  # Michigan
    "MN": "636038",  # Minnesota
    "MS": "636051",  # Mississippi
    "MO": "636030",  # Missouri
    "MT": "636008",  # Montana
    "NE": "636054",  # Nebraska
    "NV": "636049",  # Nevada
    "NH": "636039",  # New Hampshire
    "NJ": "636036",  # New Jersey
    "NM": "636009",  # New Mexico
    "NY": "636001",  # New York
    "NC": "636004",  # North Carolina
    "ND": "636034",  # North Dakota
    "OH": "636023",  # Ohio
    "OK": "636058",  # Oklahoma
    "OR": "636029",  # Oregon
    "PA": "636025",  # Pennsylvania
    "RI": "636052",  # Rhode Island
    "SC": "636005",  # South Carolina
    "SD": "636042",  # South Dakota
    "TN": "636053",  # Tennessee
    "TX": "636015",  # Texas
    "UT": "636040",  # Utah
    "VT": "636024",  # Vermont
    "VA": "636000",  # Virginia
    "WA": "636045",  # Washington
    "WV": "636061",  # West Virginia
    "WI": "636031",  # Wisconsin
    "WY": "636060",  # Wyoming
}


def get_iin_for_state(state_code: str) -> Optional[str]:
    """Get the IIN (Issuer Identification Number) for a state.

    Args:
        state_code: Two-letter state abbreviation

    Returns:
        6-digit IIN code, or None if state not found
    """
    return IIN_REGISTRY.get(state_code.upper())


def get_state_for_iin(iin: str) -> Optional[str]:
    """Get the state code for an IIN.

    Args:
        iin: 6-digit IIN code

    Returns:
        Two-letter state code, or None if IIN not found
    """
    for state, state_iin in IIN_REGISTRY.items():
        if state_iin == iin:
            return state
    return None
