"""
Workflows - Common Workflow Definitions

Defines high-level workflows that orchestrate multiple services:
- Generation workflows
- Validation workflows
- Export workflows
- Batch workflows
- Full end-to-end workflows
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    """Raised when a workflow fails"""
    pass


class GenerateWorkflow:
    """
    Workflow for license generation operations.

    Orchestrates: Generation → Validation
    """

    def __init__(self, license_service, validation_service):
        """
        Initialize the workflow.

        Args:
            license_service: LicenseService instance
            validation_service: ValidationService instance
        """
        self.license_service = license_service
        self.validation_service = validation_service

    def generate_single(
        self,
        state: Optional[str] = None,
        validate: bool = True,
        **overrides
    ) -> Tuple[List[Dict[str, str]], Optional[Any]]:
        """
        Generate and optionally validate a single license.

        Args:
            state: Optional state
            validate: Whether to validate
            **overrides: Field overrides

        Returns:
            Tuple of (license_data, validation_result)
        """
        try:
            # Generate license
            license_data = self.license_service.generate_license_data(
                state=state,
                **overrides
            )

            # Validate if requested
            validation_result = None
            if validate:
                validation_result = self.validation_service.validate_license_data(
                    license_data
                )

                if not validation_result.is_valid:
                    logger.warning(
                        f"Generated license has validation errors: "
                        f"{len(validation_result.errors)} errors"
                    )

            return license_data, validation_result

        except Exception as e:
            logger.error(f"Generate single workflow failed: {e}")
            raise WorkflowError(f"Failed to generate license: {e}") from e

    def generate_multiple(
        self,
        count: int,
        state: Optional[str] = None,
        validate: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[List[List[Dict[str, str]]], List[Any]]:
        """
        Generate and optionally validate multiple licenses.

        Args:
            count: Number to generate
            state: Optional state
            validate: Whether to validate
            progress_callback: Optional callback(current, total)

        Returns:
            Tuple of (licenses_list, validation_results)
        """
        try:
            licenses = []
            validation_results = []

            for i in range(count):
                license_data = self.license_service.generate_license_data(state=state)
                licenses.append(license_data)

                if validate:
                    validation_result = self.validation_service.validate_license_data(
                        license_data
                    )
                    validation_results.append(validation_result)

                if progress_callback:
                    progress_callback(i + 1, count)

            return licenses, validation_results

        except Exception as e:
            logger.error(f"Generate multiple workflow failed: {e}")
            raise WorkflowError(f"Failed to generate licenses: {e}") from e

    def generate_all_states(
        self,
        validate: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[List[List[Dict[str, str]]], List[Any]]:
        """
        Generate one license for each state.

        Args:
            validate: Whether to validate
            progress_callback: Optional callback(current, total, state)

        Returns:
            Tuple of (licenses_list, validation_results)
        """
        try:
            licenses = self.license_service.generate_all_states(
                progress_callback=progress_callback
            )

            validation_results = []
            if validate:
                for license_data in licenses:
                    validation_result = self.validation_service.validate_license_data(
                        license_data
                    )
                    validation_results.append(validation_result)

            return licenses, validation_results

        except Exception as e:
            logger.error(f"Generate all states workflow failed: {e}")
            raise WorkflowError(f"Failed to generate licenses: {e}") from e


class ValidateWorkflow:
    """
    Workflow for validation operations.

    Orchestrates: Validation → Reporting
    """

    def __init__(self, validation_service):
        """
        Initialize the workflow.

        Args:
            validation_service: ValidationService instance
        """
        self.validation_service = validation_service

    def validate_batch(
        self,
        licenses: List[List[Dict[str, str]]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Validate batch and return detailed report.

        Args:
            licenses: List of license data
            progress_callback: Optional callback

        Returns:
            Validation report dictionary
        """
        results, passed, failed = self.validation_service.validate_batch(
            licenses,
            progress_callback
        )

        report = {
            'total': len(licenses),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(licenses) * 100) if licenses else 0,
            'results': results,
            'errors': [],
            'warnings': []
        }

        # Collect all errors and warnings
        for result in results:
            report['errors'].extend(result.errors)
            report['warnings'].extend(result.warnings)

        return report


class ExportWorkflow:
    """
    Workflow for export operations.

    Orchestrates: Export → Verification
    """

    def __init__(self, export_service):
        """
        Initialize the workflow.

        Args:
            export_service: ExportService instance
        """
        self.export_service = export_service

    def export_licenses(
        self,
        licenses: List[List[Dict[str, str]]],
        formats: List[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, str]:
        """
        Export licenses to multiple formats.

        Args:
            licenses: List of license data
            formats: List of format names
            progress_callback: Optional callback(format, current, total)

        Returns:
            Dictionary mapping format to output path
        """
        try:
            output_paths = {}
            total = len(formats)

            # Generate barcodes first (needed for PDF/DOCX)
            records = []
            if any(fmt in ['pdf', 'docx', 'barcode'] for fmt in formats):
                for i, license_data in enumerate(licenses):
                    img_path, txt_path = self.export_service.export_barcode(
                        license_data, i
                    )
                    records.append((img_path, license_data))

            # Export each format
            for i, fmt in enumerate(formats):
                if fmt == 'json':
                    path = self.export_service.export_json(licenses)
                    output_paths['json'] = path

                elif fmt == 'csv':
                    path = self.export_service.export_csv(licenses)
                    output_paths['csv'] = path

                elif fmt == 'pdf':
                    path = self.export_service.export_pdf(records)
                    output_paths['pdf'] = path

                elif fmt == 'docx':
                    path = self.export_service.export_docx(records)
                    output_paths['docx'] = path

                elif fmt == 'barcode':
                    # Already generated
                    output_paths['barcode'] = self.export_service.barcode_dir

                if progress_callback:
                    progress_callback(fmt, i + 1, total)

            return output_paths

        except Exception as e:
            logger.error(f"Export workflow failed: {e}")
            raise WorkflowError(f"Failed to export licenses: {e}") from e


class BatchWorkflow:
    """
    Workflow for batch operations.

    Orchestrates: Generation → Validation → Export
    """

    def __init__(
        self,
        license_service,
        validation_service,
        export_service,
        batch_service
    ):
        """
        Initialize the workflow.

        Args:
            license_service: LicenseService instance
            validation_service: ValidationService instance
            export_service: ExportService instance
            batch_service: BatchService instance
        """
        self.license_service = license_service
        self.validation_service = validation_service
        self.export_service = export_service
        self.batch_service = batch_service

    def generate_and_export_batch(
        self,
        count: int,
        state: Optional[str] = None,
        validate: bool = True,
        export_formats: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Generate, validate, and export a batch of licenses.

        Args:
            count: Number of licenses
            state: Optional state
            validate: Whether to validate
            export_formats: List of export formats
            progress_callback: Optional callback(current, total, status)

        Returns:
            Dictionary with results and export paths
        """
        try:
            # Generate licenses
            logger.info(f"Generating {count} licenses...")
            licenses = []

            for i in range(count):
                license_data = self.license_service.generate_license_data(state=state)
                licenses.append(license_data)

                if progress_callback:
                    progress_callback(i + 1, count, "Generating")

            # Validate if requested
            validation_results = []
            if validate:
                logger.info("Validating licenses...")
                for i, license_data in enumerate(licenses):
                    result = self.validation_service.validate_license_data(license_data)
                    validation_results.append(result)

                    if progress_callback:
                        progress_callback(i + 1, count, "Validating")

            # Export if formats specified
            export_paths = {}
            if export_formats:
                logger.info(f"Exporting to formats: {export_formats}")

                # Generate barcodes
                records = []
                for i, license_data in enumerate(licenses):
                    img_path, txt_path = self.export_service.export_barcode(
                        license_data, i
                    )
                    records.append((img_path, license_data))

                    if progress_callback:
                        progress_callback(i + 1, count, "Creating barcodes")

                # Export each format
                for fmt in export_formats:
                    if fmt == 'json':
                        export_paths['json'] = self.export_service.export_json(licenses)
                    elif fmt == 'csv':
                        export_paths['csv'] = self.export_service.export_csv(licenses)
                    elif fmt == 'pdf':
                        export_paths['pdf'] = self.export_service.export_pdf(records)
                    elif fmt == 'docx':
                        export_paths['docx'] = self.export_service.export_docx(records)

            return {
                'licenses': licenses,
                'validation_results': validation_results,
                'export_paths': export_paths,
                'summary': {
                    'total': count,
                    'validated': len(validation_results),
                    'passed_validation': sum(1 for r in validation_results if r.is_valid),
                    'exported_formats': list(export_paths.keys())
                }
            }

        except Exception as e:
            logger.error(f"Batch workflow failed: {e}")
            raise WorkflowError(f"Failed to process batch: {e}") from e

    def generate_all_states_and_export(
        self,
        validate: bool = True,
        export_formats: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Generate one license per state and export.

        Args:
            validate: Whether to validate
            export_formats: List of export formats
            progress_callback: Optional callback(current, total, status)

        Returns:
            Dictionary with results and export paths
        """
        return self.generate_and_export_batch(
            count=51,  # 50 states + DC
            state=None,  # Will use all states
            validate=validate,
            export_formats=export_formats,
            progress_callback=progress_callback
        )

    def full_workflow(
        self,
        count: int,
        state: Optional[str] = None,
        export_formats: Optional[List[str]] = None,
        validate_before_export: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete workflow with all stages.

        Workflow stages:
        1. Generation
        2. Validation (optional)
        3. Export
        4. Summary reporting

        Args:
            count: Number of licenses
            state: Optional state
            export_formats: Export formats
            validate_before_export: Validate before exporting
            progress_callback: Optional callback(stage, current, total)

        Returns:
            Complete workflow result dictionary
        """
        try:
            result = {
                'licenses': [],
                'validation_results': [],
                'export_paths': {},
                'summary': {},
                'errors': []
            }

            # Stage 1: Generation
            logger.info(f"Stage 1/3: Generating {count} licenses...")
            for i in range(count):
                try:
                    license_data = self.license_service.generate_license_data(state=state)
                    result['licenses'].append(license_data)

                    if progress_callback:
                        progress_callback("Generation", i + 1, count)

                except Exception as e:
                    result['errors'].append(f"Generation {i}: {e}")
                    logger.error(f"Failed to generate license {i}: {e}")

            # Stage 2: Validation
            if validate_before_export and result['licenses']:
                logger.info("Stage 2/3: Validating licenses...")
                total = len(result['licenses'])

                for i, license_data in enumerate(result['licenses']):
                    try:
                        validation_result = self.validation_service.validate_license_data(
                            license_data
                        )
                        result['validation_results'].append(validation_result)

                        if progress_callback:
                            progress_callback("Validation", i + 1, total)

                    except Exception as e:
                        result['errors'].append(f"Validation {i}: {e}")
                        logger.error(f"Failed to validate license {i}: {e}")

            # Stage 3: Export
            if export_formats and result['licenses']:
                logger.info(f"Stage 3/3: Exporting to {len(export_formats)} formats...")

                # Generate barcodes
                records = []
                for i, license_data in enumerate(result['licenses']):
                    try:
                        img_path, txt_path = self.export_service.export_barcode(
                            license_data, i
                        )
                        records.append((img_path, license_data))
                    except Exception as e:
                        result['errors'].append(f"Barcode {i}: {e}")
                        logger.error(f"Failed to create barcode {i}: {e}")

                # Export each format
                for fmt in export_formats:
                    try:
                        if fmt == 'json':
                            result['export_paths']['json'] = self.export_service.export_json(
                                result['licenses']
                            )
                        elif fmt == 'csv':
                            result['export_paths']['csv'] = self.export_service.export_csv(
                                result['licenses']
                            )
                        elif fmt == 'pdf':
                            result['export_paths']['pdf'] = self.export_service.export_pdf(
                                records
                            )
                        elif fmt == 'docx':
                            result['export_paths']['docx'] = self.export_service.export_docx(
                                records
                            )

                        if progress_callback:
                            progress_callback("Export", len(result['export_paths']), len(export_formats))

                    except Exception as e:
                        result['errors'].append(f"Export {fmt}: {e}")
                        logger.error(f"Failed to export {fmt}: {e}")

            # Generate summary
            result['summary'] = {
                'total_requested': count,
                'total_generated': len(result['licenses']),
                'total_validated': len(result['validation_results']),
                'passed_validation': sum(
                    1 for r in result['validation_results'] if r.is_valid
                ),
                'failed_validation': sum(
                    1 for r in result['validation_results'] if not r.is_valid
                ),
                'exported_formats': list(result['export_paths'].keys()),
                'total_errors': len(result['errors']),
                'success': len(result['errors']) == 0
            }

            logger.info(f"Workflow completed: {result['summary']}")
            return result

        except Exception as e:
            logger.error(f"Full workflow failed: {e}")
            raise WorkflowError(f"Workflow execution failed: {e}") from e


class ImportWorkflow:
    """
    Workflow for import operations.

    Orchestrates: Import → Validation → Processing
    """

    def __init__(self, import_service, validation_service):
        """
        Initialize the workflow.

        Args:
            import_service: ImportService instance
            validation_service: ValidationService instance
        """
        self.import_service = import_service
        self.validation_service = validation_service

    def import_and_validate(
        self,
        filepath: str,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Import and optionally validate licenses.

        Args:
            filepath: Path to import file
            validate: Whether to validate

        Returns:
            Dictionary with import and validation results
        """
        try:
            # Import
            import_result = self.import_service.import_auto(filepath)

            if not import_result.success:
                return {
                    'success': False,
                    'errors': import_result.errors,
                    'licenses': []
                }

            # Validate
            validation_results = []
            if validate:
                for license_data in import_result.data:
                    result = self.validation_service.validate_license_data(license_data)
                    validation_results.append(result)

            return {
                'success': True,
                'licenses': import_result.data,
                'validation_results': validation_results,
                'summary': {
                    'total_imported': import_result.count,
                    'passed_validation': sum(1 for r in validation_results if r.is_valid),
                    'failed_validation': sum(1 for r in validation_results if not r.is_valid)
                }
            }

        except Exception as e:
            logger.error(f"Import workflow failed: {e}")
            raise WorkflowError(f"Failed to import: {e}") from e
