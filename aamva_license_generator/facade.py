"""
AAMVA License Generator - Facade API

Provides a simple, unified API for all license generation operations.
Hides the complexity of service orchestration behind a clean interface.

This is the main entry point for GUI and CLI applications.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
import logging

from .services import (
    LicenseService,
    ValidationService,
    ExportService,
    ImportService,
    BatchService
)
from .workflows import (
    GenerateWorkflow,
    ValidateWorkflow,
    ExportWorkflow,
    BatchWorkflow
)

# Configure logging
logger = logging.getLogger(__name__)


class AAMVALicenseGenerator:
    """
    Facade for AAMVA License Generator.

    Provides a simple, high-level API that orchestrates all services
    and workflows for license generation, validation, and export.

    Example usage:
        # Create generator
        generator = AAMVALicenseGenerator()

        # Generate single license
        license_data = generator.generate_license(state="CA")

        # Generate and export batch
        result = generator.generate_batch(
            count=10,
            export_formats=['pdf', 'docx', 'json']
        )

        # Import and validate
        imported = generator.import_licenses("licenses.json")
        validation_result = generator.validate_licenses(imported)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AAMVA License Generator.

        Args:
            config: Optional configuration dictionary with keys:
                - output_dir: Output directory (default: 'output')
                - seed: Random seed for reproducibility
                - locale: Faker locale (default: 'en_US')
                - validation_enabled: Enable validation (default: True)
                - iin_jurisdictions: Custom IIN mappings
                - state_formats: Custom state formats
                - fail_fast: Stop on first error (default: False)
                - max_retries: Maximum retry attempts (default: 0)
        """
        self.config = config or {}

        # Initialize services
        self.license_service = LicenseService(config)
        self.validation_service = ValidationService(
            strict_mode=config.get('strict_validation', False)
        )
        self.export_service = ExportService(
            output_dir=config.get('output_dir', 'output')
        )
        self.import_service = ImportService()
        self.batch_service = BatchService(
            fail_fast=config.get('fail_fast', False),
            max_failures=config.get('max_failures'),
            retry_attempts=config.get('max_retries', 0),
            rollback_on_failure=config.get('rollback_on_failure', False)
        )

        # Initialize workflows
        self.generate_workflow = GenerateWorkflow(
            self.license_service,
            self.validation_service
        )
        self.validate_workflow = ValidateWorkflow(self.validation_service)
        self.export_workflow = ExportWorkflow(self.export_service)
        self.batch_workflow = BatchWorkflow(
            self.license_service,
            self.validation_service,
            self.export_service,
            self.batch_service
        )

        logger.info("AAMVALicenseGenerator initialized")

    # ========================================================================
    # GENERATION API
    # ========================================================================

    def generate_license(
        self,
        state: Optional[str] = None,
        validate: bool = True,
        **overrides
    ) -> Tuple[List[Dict[str, str]], Optional[Any]]:
        """
        Generate a single license.

        Args:
            state: Optional state abbreviation (random if None)
            validate: Whether to validate generated data
            **overrides: Optional field overrides

        Returns:
            Tuple of (license_data, validation_result)

        Example:
            license, validation = generator.generate_license(
                state="CA",
                DCS="SMITH",  # Override last name
                validate=True
            )
        """
        return self.generate_workflow.generate_single(
            state=state,
            validate=validate,
            **overrides
        )

    def generate_multiple(
        self,
        count: int,
        state: Optional[str] = None,
        validate: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[List[List[Dict[str, str]]], List[Any]]:
        """
        Generate multiple licenses.

        Args:
            count: Number of licenses to generate
            state: Optional state (random if None)
            validate: Whether to validate each license
            progress_callback: Optional callback(current, total)

        Returns:
            Tuple of (licenses_list, validation_results)
        """
        return self.generate_workflow.generate_multiple(
            count=count,
            state=state,
            validate=validate,
            progress_callback=progress_callback
        )

    def generate_all_states(
        self,
        validate: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[List[List[Dict[str, str]]], List[Any]]:
        """
        Generate one license for each US state.

        Args:
            validate: Whether to validate each license
            progress_callback: Optional callback(current, total, state)

        Returns:
            Tuple of (licenses_list, validation_results)
        """
        return self.generate_workflow.generate_all_states(
            validate=validate,
            progress_callback=progress_callback
        )

    # ========================================================================
    # VALIDATION API
    # ========================================================================

    def validate_license(
        self,
        license_data: List[Dict[str, str]]
    ) -> Any:
        """
        Validate a single license.

        Args:
            license_data: License data array

        Returns:
            ValidationResult object
        """
        return self.validation_service.validate_license_data(license_data)

    def validate_licenses(
        self,
        licenses: List[List[Dict[str, str]]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[List[Any], int, int]:
        """
        Validate multiple licenses.

        Args:
            licenses: List of license data arrays
            progress_callback: Optional callback(current, total)

        Returns:
            Tuple of (results, passed_count, failed_count)
        """
        return self.validation_service.validate_batch(
            licenses,
            progress_callback
        )

    # ========================================================================
    # EXPORT API
    # ========================================================================

    def export_barcode(
        self,
        license_data: List[Dict[str, str]],
        index: int = 0,
        format: str = "bmp"
    ) -> Tuple[str, str]:
        """
        Export license as barcode.

        Args:
            license_data: License data array
            index: File index
            format: Image format ('bmp' or 'png')

        Returns:
            Tuple of (image_path, data_path)
        """
        return self.export_service.export_barcode(license_data, index, format)

    def export_json(
        self,
        licenses: List[List[Dict[str, str]]],
        filename: str = "licenses.json"
    ) -> str:
        """
        Export licenses as JSON.

        Args:
            licenses: List of license data arrays
            filename: Output filename

        Returns:
            Output file path
        """
        return self.export_service.export_json(licenses, filename)

    def export_csv(
        self,
        licenses: List[List[Dict[str, str]]],
        filename: str = "licenses.csv"
    ) -> str:
        """
        Export licenses as CSV.

        Args:
            licenses: List of license data arrays
            filename: Output filename

        Returns:
            Output file path
        """
        return self.export_service.export_csv(licenses, filename)

    def export_pdf(
        self,
        records: List[Tuple[str, List[Dict[str, str]]]],
        filename: str = "licenses.pdf",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Export licenses as PDF with Avery layout.

        Args:
            records: List of (barcode_path, license_data) tuples
            filename: Output filename
            progress_callback: Optional callback(current, total)

        Returns:
            Output file path
        """
        return self.export_service.export_pdf(records, filename, progress_callback)

    def export_docx(
        self,
        records: List[Tuple[str, List[Dict[str, str]]]],
        filename: str = "licenses.docx",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Export licenses as DOCX.

        Args:
            records: List of (barcode_path, license_data) tuples
            filename: Output filename
            progress_callback: Optional callback(current, total)

        Returns:
            Output file path
        """
        return self.export_service.export_docx(records, filename, progress_callback)

    # ========================================================================
    # IMPORT API
    # ========================================================================

    def import_json(self, filepath: str) -> Any:
        """
        Import licenses from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            ImportResult object
        """
        return self.import_service.import_json(filepath)

    def import_csv(self, filepath: str) -> Any:
        """
        Import licenses from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            ImportResult object
        """
        return self.import_service.import_csv(filepath)

    def import_aamva(self, filepath: str) -> Any:
        """
        Import license from AAMVA text file.

        Args:
            filepath: Path to AAMVA file

        Returns:
            ImportResult object
        """
        return self.import_service.import_aamva_file(filepath)

    def import_auto(self, filepath: str) -> Any:
        """
        Auto-detect format and import.

        Args:
            filepath: Path to file

        Returns:
            ImportResult object
        """
        return self.import_service.import_auto(filepath)

    # ========================================================================
    # BATCH API
    # ========================================================================

    def generate_batch(
        self,
        count: int,
        state: Optional[str] = None,
        validate: bool = True,
        export_formats: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Any:
        """
        Generate a batch of licenses with optional export.

        Args:
            count: Number of licenses
            state: Optional state
            validate: Whether to validate
            export_formats: List of formats to export ('barcode', 'json', 'csv', 'pdf', 'docx')
            progress_callback: Optional callback(current, total, status)

        Returns:
            BatchResult object with generated licenses and export paths

        Example:
            result = generator.generate_batch(
                count=50,
                state="CA",
                export_formats=['pdf', 'json'],
                progress_callback=lambda c, t, s: print(f"{c}/{t}: {s}")
            )
        """
        return self.batch_workflow.generate_and_export_batch(
            count=count,
            state=state,
            validate=validate,
            export_formats=export_formats or [],
            progress_callback=progress_callback
        )

    def generate_all_states_batch(
        self,
        validate: bool = True,
        export_formats: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Any:
        """
        Generate one license per state with optional export.

        Args:
            validate: Whether to validate
            export_formats: List of formats to export
            progress_callback: Optional callback(current, total, status)

        Returns:
            BatchResult object
        """
        return self.batch_workflow.generate_all_states_and_export(
            validate=validate,
            export_formats=export_formats or [],
            progress_callback=progress_callback
        )

    # ========================================================================
    # WORKFLOW API
    # ========================================================================

    def full_workflow(
        self,
        count: int,
        state: Optional[str] = None,
        export_formats: Optional[List[str]] = None,
        validate_before_export: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete workflow: generate → validate → export.

        Args:
            count: Number of licenses
            state: Optional state
            export_formats: Export formats
            validate_before_export: Validate before exporting
            progress_callback: Optional callback(stage, current, total)

        Returns:
            Dictionary with results:
                - licenses: Generated license data
                - validation_results: Validation results
                - export_paths: Dictionary of format -> path
                - summary: Summary statistics

        Example:
            result = generator.full_workflow(
                count=100,
                export_formats=['pdf', 'docx', 'json'],
                progress_callback=lambda stage, c, t: print(f"{stage}: {c}/{t}")
            )
        """
        return self.batch_workflow.full_workflow(
            count=count,
            state=state,
            export_formats=export_formats or ['pdf', 'json'],
            validate_before_export=validate_before_export,
            progress_callback=progress_callback
        )

    # ========================================================================
    # UTILITY API
    # ========================================================================

    def get_supported_states(self) -> List[str]:
        """
        Get list of supported state abbreviations.

        Returns:
            List of state codes
        """
        return sorted(self.license_service.iin_jurisdictions.values(),
                     key=lambda x: x['abbr'])

    def get_iin_for_state(self, state: str) -> Optional[str]:
        """
        Get IIN code for a state.

        Args:
            state: State abbreviation

        Returns:
            IIN code or None
        """
        return self.license_service.get_iin_by_state(state)

    def get_statistics(self, licenses: List[List[Dict[str, str]]]) -> Dict[str, Any]:
        """
        Get statistics about generated licenses.

        Args:
            licenses: List of license data arrays

        Returns:
            Statistics dictionary
        """
        stats = {
            'total_licenses': len(licenses),
            'states': {},
            'sex_distribution': {'male': 0, 'female': 0},
            'veteran_count': 0,
            'organ_donor_count': 0,
            'dhs_compliant_count': 0,
        }

        for license_data in licenses:
            dl_data = license_data[0]

            # Count by state
            state = dl_data.get('DAJ', 'Unknown')
            stats['states'][state] = stats['states'].get(state, 0) + 1

            # Sex distribution
            if dl_data.get('DBC') == '1':
                stats['sex_distribution']['male'] += 1
            elif dl_data.get('DBC') == '2':
                stats['sex_distribution']['female'] += 1

            # Flags
            if dl_data.get('DDL') == '1':
                stats['veteran_count'] += 1
            if dl_data.get('DDK') == '1':
                stats['organ_donor_count'] += 1
            if dl_data.get('DDA') == 'F':
                stats['dhs_compliant_count'] += 1

        return stats

    def cleanup(self):
        """
        Cleanup resources and temporary files.
        """
        logger.info("Cleaning up resources")
        # Placeholder for cleanup logic


# Convenience function for quick usage
def create_generator(
    output_dir: str = "output",
    seed: Optional[int] = None
) -> AAMVALicenseGenerator:
    """
    Create a configured generator instance.

    Args:
        output_dir: Output directory
        seed: Random seed for reproducibility

    Returns:
        AAMVALicenseGenerator instance

    Example:
        generator = create_generator(output_dir="my_licenses", seed=42)
        licenses, _ = generator.generate_multiple(10)
    """
    config = {
        'output_dir': output_dir,
        'seed': seed,
    }
    return AAMVALicenseGenerator(config)
