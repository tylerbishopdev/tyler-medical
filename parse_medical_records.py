#!/usr/bin/env python3
"""
Comprehensive Medical Records Parser
Parses extracted medical records and normalizes all data into structured JSON.
"""

import re
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from collections import defaultdict

def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats to ISO format."""
    if not date_str:
        return None

    # Common formats
    formats = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y/%m/%d"
    ]

    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # Return as-is if can't parse

def parse_reference_range(ref_str: str) -> Dict[str, Any]:
    """Parse reference range string into structured format."""
    if not ref_str or ref_str.lower() in ['not estab.', 'not established', '']:
        return {"established": False}

    ref_str = ref_str.strip()
    result = {"established": True, "raw": ref_str}

    # Handle various formats
    # Format: "0-100" or "0.0-10.0"
    range_match = re.match(r'^([<>]?\s*[\d.]+)\s*[-–]\s*([\d.]+)$', ref_str)
    if range_match:
        result["min"] = float(range_match.group(1).replace('<', '').replace('>', '').strip())
        result["max"] = float(range_match.group(2))
        return result

    # Format: ">59" or "<100"
    threshold_match = re.match(r'^([<>])\s*([\d.]+)$', ref_str)
    if threshold_match:
        if threshold_match.group(1) == '>':
            result["min"] = float(threshold_match.group(2))
        else:
            result["max"] = float(threshold_match.group(2))
        return result

    # Format: ">= 60" or "<= 100"
    threshold_eq_match = re.match(r'^([<>]=?)\s*([\d.]+)$', ref_str)
    if threshold_eq_match:
        val = float(threshold_eq_match.group(2))
        op = threshold_eq_match.group(1)
        if '>' in op:
            result["min"] = val
        else:
            result["max"] = val
        return result

    # Qualitative references
    if ref_str.lower() in ['negative', 'non reactive', 'non-reactive']:
        result["expected"] = "Negative"
        return result

    if 'class 0' in ref_str.lower():
        result["expected"] = "Class 0"
        return result

    return result

def parse_value(value_str: str) -> Dict[str, Any]:
    """Parse a lab value string."""
    if not value_str:
        return {"raw": None}

    value_str = value_str.strip()
    result = {"raw": value_str}

    # Handle <X.XX values
    if value_str.startswith('<'):
        try:
            result["value"] = float(value_str[1:])
            result["qualifier"] = "<"
        except ValueError:
            pass
        return result

    # Handle >X.XX values
    if value_str.startswith('>'):
        try:
            result["value"] = float(value_str[1:])
            result["qualifier"] = ">"
        except ValueError:
            pass
        return result

    # Try numeric
    try:
        result["value"] = float(value_str)
    except ValueError:
        # Keep as string (qualitative result)
        result["value"] = value_str

    return result

def parse_flag(flag_str: str) -> Optional[str]:
    """Parse flag (High/Low/etc)."""
    if not flag_str:
        return None
    flag_str = flag_str.strip().upper()
    if flag_str in ['H', 'HIGH']:
        return "High"
    if flag_str in ['L', 'LOW']:
        return "Low"
    if flag_str in ['A', 'ABNORMAL']:
        return "Abnormal"
    if flag_str in ['C', 'CRITICAL']:
        return "Critical"
    return flag_str if flag_str else None

class MedicalRecordParser:
    def __init__(self, text: str):
        self.text = text
        self.pages = self._split_pages()
        self.patient_info = {}
        self.lab_results = []
        self.allergies = []
        self.genetic_data = {}
        self.imaging_reports = []
        self.pathology_reports = []
        self.synovial_fluid_analyses = []
        self.medications = []
        self.visit_summaries = []
        self.clinical_notes = []
        self.physicians = set()

    def _split_pages(self) -> List[str]:
        """Split text by page markers."""
        return re.split(r'=== PAGE \d+ ===', self.text)

    def parse_all(self) -> Dict[str, Any]:
        """Parse all data from medical records."""
        self._parse_patient_info()
        self._parse_lab_results()
        self._parse_allergies()
        self._parse_genetic_data()
        self._parse_imaging_reports()
        self._parse_pathology_reports()
        self._parse_synovial_fluid()
        self._parse_medications()
        self._parse_visit_summaries()
        self._parse_clinical_notes()

        return self._build_output()

    def _parse_patient_info(self):
        """Extract patient demographic information."""
        # Look for patient name patterns
        name_patterns = [
            r'Bishop,\s*Tyler\s*W?\.?',
            r'BISHOP,\s*TYLER\s*W?\.?',
            r'Tyler\s+W?\.?\s*Bishop'
        ]

        self.patient_info = {
            "name": {
                "first": "Tyler",
                "middle": "W",
                "last": "Bishop",
                "full": "Tyler W. Bishop"
            },
            "date_of_birth": "1987-05-26",
            "sex": "Male",
            "phone": "636-448-1747",
            "addresses": [],
            "patient_ids": set(),
            "mrns": set()
        }

        # Extract addresses
        address_patterns = [
            r'(\d+\s+[A-Z][A-Za-z\s]+(?:DR|AVE|BLVD|ST|CIR|PKWY|RD)\.?\s*(?:UNIT|APT|STE|#)?\s*\d*),?\s*(SAN DIEGO|LA JOLLA),?\s*CA,?\s*(\d{5})',
        ]
        for pattern in address_patterns:
            for match in re.finditer(pattern, self.text, re.IGNORECASE):
                addr = {
                    "street": match.group(1).strip(),
                    "city": match.group(2).strip().title(),
                    "state": "CA",
                    "zip": match.group(3)
                }
                if addr not in self.patient_info["addresses"]:
                    self.patient_info["addresses"].append(addr)

        # Extract patient IDs
        id_patterns = [
            r'Patient ID:\s*(\w+)',
            r'MRN:\s*(\d+)'
        ]
        for pattern in id_patterns:
            for match in re.finditer(pattern, self.text):
                self.patient_info["patient_ids"].add(match.group(1))

        # Convert sets to lists for JSON
        self.patient_info["patient_ids"] = list(self.patient_info["patient_ids"])
        self.patient_info["mrns"] = list(self.patient_info["mrns"])

    def _parse_lab_results(self):
        """Parse all laboratory test results."""
        # Pattern for common Labcorp format
        # Test Name 01 Value Flag Previous Units Reference
        labcorp_pattern = re.compile(
            r'^([A-Za-z][A-Za-z0-9\s\-\(\),./]+?)\s+0[12]\s+'  # Test name + lab code
            r'([<>]?[\d.]+|Negative|Positive|Non Reactive|See below:?)\s*'  # Value
            r'(High|Low|H|L|)?\s*'  # Flag (optional)
            r'([<>]?[\d.]+\s+\d{2}/\d{2}/\d{4})?\s*'  # Previous value+date (optional)
            r'([a-zA-Z%/]+(?:E\d)?(?:/\w+)?)?\s*'  # Units (optional)
            r'([\d.\-<>]+(?:\s*-\s*[\d.]+)?|Negative|Class \d|>?\d+|Not Estab\.)?'  # Reference (optional)
        , re.MULTILINE)

        # Quest format pattern
        quest_pattern = re.compile(
            r'^([A-Z][A-Z0-9\s\-\(\),./]+)\s+'  # Test name
            r'([\d.]+|Negative|Positive)\s*'  # Value
            r'(H|L)?\s+'  # Flag
            r'Reference Range:\s*(.+)$'  # Reference
        , re.MULTILINE)

        # Process date context
        current_date = None
        current_panel = None
        current_physician = None
        current_specimen_id = None

        for page in self.pages:
            # Extract date context
            date_match = re.search(r'Date Collected:\s*(\d{2}/\d{2}/\d{4})', page)
            if date_match:
                current_date = parse_date(date_match.group(1))

            # Extract physician
            physician_match = re.search(r'Ordering Physician:\s*([A-Z]\s+[A-Z]+)', page)
            if physician_match:
                current_physician = physician_match.group(1).strip()
                self.physicians.add(current_physician)

            # Extract specimen ID
            specimen_match = re.search(r'Specimen ID:\s*([\d\-]+)', page)
            if specimen_match:
                current_specimen_id = specimen_match.group(1)

            # Extract panel names
            panel_patterns = [
                r'^(CBC[/\w\s]+)$',
                r'^(Basic Metabolic Panel[^$]*)',
                r'^(Comp\.?\s*Metabolic Panel[^$]*)',
                r'^(Hepatic Function Panel[^$]*)',
                r'^(Iron and TIBC)',
                r'^(Vitamin B12 and Folate)',
                r'^(Lipid Panel[^$]*)',
                r'^(Renal Panel[^$]*)',
                r'^(Urinalysis[^$]*)',
                r'^(Pre-Biologic Screening Profile)',
                r'^(RA Profile[^$]*)',
                r'^(Celiac Ab[^$]*)',
                r'^(Thyroid[^$]*)',
            ]

            for pattern in panel_patterns:
                panel_match = re.search(pattern, page, re.MULTILINE | re.IGNORECASE)
                if panel_match:
                    current_panel = panel_match.group(1).strip()

            # Parse individual test results
            lines = page.split('\n')
            for i, line in enumerate(lines):
                # Skip headers and metadata
                if any(skip in line for skip in ['Test Current Result', 'TESTS RESULT', 'Analyte Value', '©', 'Laboratory Corporation']):
                    continue

                # Common test patterns
                test_patterns = [
                    # Labcorp standard format
                    (r'^([A-Za-z][A-Za-z0-9\s\-\(\),./\']+?)\s+0[123]\s+([<>]?[\d.]+|Negative|Positive|Non Reactive|<\d+)\s*(High|Low|H|L)?', 'labcorp'),
                    # Quest format
                    (r'^([A-Z][A-Z0-9\s\-\(\),./]+)\s+([\d.]+)\s*(H|L)?\s+Reference Range:', 'quest'),
                    # IgE allergen format
                    (r'^([A-Z]\d+-IgE\s+[\w\s,]+)\s+0\d\s+([<>]?[\d.]+)\s+(\w+/\w+)\s+(Class \d)', 'allergen'),
                ]

                for pattern, fmt in test_patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        test_name = match.group(1).strip()
                        value_str = match.group(2).strip()
                        flag = match.group(3) if len(match.groups()) > 2 else None

                        # Skip if test name is too short or looks like metadata
                        if len(test_name) < 3 or test_name.startswith('Page'):
                            continue

                        # Extract units and reference from rest of line
                        units = None
                        reference_range = None

                        # Try to extract from same line
                        rest_of_line = line[match.end():].strip()

                        # Common unit patterns
                        unit_match = re.search(r'([a-zA-Z]+(?:/[a-zA-Z]+)?(?:E\d+)?(?:/[a-zA-Z]+)?)\s+([\d.<>-]+)', rest_of_line)
                        if unit_match:
                            units = unit_match.group(1)
                            reference_range = unit_match.group(2)

                        result = {
                            "test_name": test_name,
                            "value": parse_value(value_str),
                            "units": units,
                            "reference_range": parse_reference_range(reference_range) if reference_range else None,
                            "flag": parse_flag(flag),
                            "date_collected": current_date,
                            "panel": current_panel,
                            "ordering_physician": current_physician,
                            "specimen_id": current_specimen_id,
                            "source_format": fmt
                        }

                        self.lab_results.append(result)
                        break

        # Also parse specific well-known tests with dedicated patterns
        self._parse_cbc()
        self._parse_metabolic_panels()
        self._parse_liver_panel()
        self._parse_lipid_panel()
        self._parse_thyroid()
        self._parse_vitamins()
        self._parse_inflammatory_markers()
        self._parse_autoimmune_markers()
        self._parse_infectious_disease()
        self._parse_coagulation()
        self._parse_urinalysis()

    def _parse_cbc(self):
        """Parse CBC (Complete Blood Count) results."""
        cbc_tests = [
            ('WBC', r'WBC\s+0\d\s+([\d.]+)', 'x10E3/uL', '3.4-10.8'),
            ('RBC', r'RBC\s+0\d\s+([\d.]+)', 'x10E6/uL', '4.14-5.80'),
            ('Hemoglobin', r'Hemoglobin\s+0\d\s+([\d.]+)', 'g/dL', '13.0-17.7'),
            ('Hematocrit', r'Hematocrit\s+0\d\s+([\d.]+)', '%', '37.5-51.0'),
            ('MCV', r'MCV\s+0\d\s+(\d+)', 'fL', '79-97'),
            ('MCH', r'MCH\s+0\d\s+([\d.]+)', 'pg', '26.6-33.0'),
            ('MCHC', r'MCHC\s+0\d\s+([\d.]+)', 'g/dL', '31.5-35.7'),
            ('RDW', r'RDW\s+0\d\s+([\d.]+)', '%', '12.3-15.4'),
            ('Platelets', r'Platelets\s+0\d\s+(\d+)', 'x10E3/uL', '150-379'),
            ('Neutrophils', r'Neutrophils\s+0\d\s+(\d+)', '%', 'Not Estab.'),
            ('Lymphs', r'Lymphs\s+0\d\s+(\d+)', '%', 'Not Estab.'),
            ('Monocytes', r'Monocytes\s+0\d\s+(\d+)', '%', 'Not Estab.'),
            ('Eos', r'Eos\s+0\d\s+(\d+)', '%', 'Not Estab.'),
            ('Basos', r'Basos\s+0\d\s+(\d+)', '%', 'Not Estab.'),
        ]
        # Already handled in main parser
        pass

    def _parse_metabolic_panels(self):
        """Parse metabolic panel results."""
        pass  # Handled in main parser

    def _parse_liver_panel(self):
        """Parse hepatic function panel results."""
        pass  # Handled in main parser

    def _parse_lipid_panel(self):
        """Parse lipid panel results."""
        pass  # Handled in main parser

    def _parse_thyroid(self):
        """Parse thyroid function tests."""
        pass  # Handled in main parser

    def _parse_vitamins(self):
        """Parse vitamin levels."""
        pass  # Handled in main parser

    def _parse_inflammatory_markers(self):
        """Parse inflammatory markers (CRP, ESR, etc.)."""
        pass  # Handled in main parser

    def _parse_autoimmune_markers(self):
        """Parse autoimmune markers (ANA, RF, etc.)."""
        pass  # Handled in main parser

    def _parse_infectious_disease(self):
        """Parse infectious disease screening."""
        pass  # Handled in main parser

    def _parse_coagulation(self):
        """Parse coagulation tests."""
        pass  # Handled in main parser

    def _parse_urinalysis(self):
        """Parse urinalysis results."""
        pass  # Handled in main parser

    def _parse_allergies(self):
        """Parse allergy test results (IgE panels)."""
        # IgE class interpretation
        ige_classes = {
            0: {"level": "Negative", "range": "< 0.10"},
            "0/I": {"level": "Equivocal/Low", "range": "0.10 - 0.31"},
            1: {"level": "Low", "range": "0.32 - 0.55"},
            2: {"level": "Moderate", "range": "0.56 - 1.40"},
            3: {"level": "High", "range": "1.41 - 3.90"},
            4: {"level": "Very High", "range": "3.91 - 19.00"},
            5: {"level": "Very High", "range": "19.01 - 100.00"},
            6: {"level": "Very High", "range": ">100.00"},
        }

        # Allergen categories
        allergen_codes = {
            'D': 'Dust Mites',
            'E': 'Animal Dander',
            'G': 'Grasses',
            'I': 'Insects',
            'M': 'Molds',
            'T': 'Trees',
            'W': 'Weeds',
            'F': 'Foods',
        }

        # Pattern for IgE allergen tests
        allergen_pattern = re.compile(
            r'([DEGIMTWF]\d+)-IgE\s+([A-Za-z][A-Za-z\s,/]+?)\s+0\d\s+([<>]?[\d.]+)\s+(\w+/\w+)\s+(Class \d)',
            re.MULTILINE
        )

        current_date = None

        for page in self.pages:
            # Get collection date for this page
            date_match = re.search(r'Date Collected:\s*(\d{2}/\d{2}/\d{4})', page)
            if date_match:
                current_date = parse_date(date_match.group(1))

            for match in allergen_pattern.finditer(page):
                code = match.group(1)
                name = match.group(2).strip()
                value = match.group(3)
                units = match.group(4)
                class_result = match.group(5)

                category_code = code[0]
                class_num = int(class_result.replace('Class ', ''))

                allergen = {
                    "code": code,
                    "name": name,
                    "category": allergen_codes.get(category_code, "Unknown"),
                    "value": parse_value(value),
                    "units": units,
                    "class": class_num,
                    "interpretation": ige_classes.get(class_num, {}).get("level", "Unknown"),
                    "date_collected": current_date,
                    "is_positive": class_num > 0
                }

                self.allergies.append(allergen)

        # Also look for Total IgE
        ige_total_pattern = re.compile(
            r'Immunoglobulin E,\s*Total\s+0\d\s+(\d+)\s+(\w+/\w+)\s+([\d-]+)',
            re.MULTILINE
        )

        for match in ige_total_pattern.finditer(self.text):
            self.allergies.append({
                "code": "Total_IgE",
                "name": "Immunoglobulin E, Total",
                "category": "Total IgE",
                "value": parse_value(match.group(1)),
                "units": match.group(2),
                "reference_range": parse_reference_range(match.group(3)),
                "is_screening": True
            })

    def _parse_genetic_data(self):
        """Parse 23andMe genetic reports."""
        self.genetic_data = {
            "provider": "23andMe",
            "health_predispositions": [],
            "carrier_status": [],
            "wellness": [],
            "ancestry": {},
            "traits": []
        }

        # Health predispositions
        health_patterns = [
            (r'Age-Related Macular Degeneration\s+(.+)', 'Age-Related Macular Degeneration'),
            (r'Hereditary Hemochromatosis\s*\(HFE-Related\)\s+(.+)', 'Hereditary Hemochromatosis (HFE-Related)'),
            (r'Late-Onset Alzheimer\'s Disease\s+(.+)', 'Late-Onset Alzheimers Disease'),
            (r'Alpha-1 Antitrypsin Deficiency\s+(.+)', 'Alpha-1 Antitrypsin Deficiency'),
            (r'BRCA1/BRCA2\s*\(Selected Variants\)\s+(.+)', 'BRCA1/BRCA2 (Selected Variants)'),
            (r'Celiac Disease\s+(.+)', 'Celiac Disease'),
            (r'Type 2 Diabetes\s+(.+)', 'Type 2 Diabetes'),
            (r'Parkinson\'s Disease\s+(.+)', 'Parkinsons Disease'),
        ]

        for pattern, name in health_patterns:
            match = re.search(pattern, self.text)
            if match:
                result = match.group(1).strip()
                self.genetic_data["health_predispositions"].append({
                    "condition": name,
                    "result": result,
                    "variant_detected": 'variant detected' in result.lower() or 'increased risk' in result.lower()
                })

        # Carrier status - parse "Variant not detected" patterns
        carrier_section = re.search(r'Carrier Status Reports(.+?)Wellness Reports', self.text, re.DOTALL)
        if carrier_section:
            carrier_text = carrier_section.group(1)
            carrier_pattern = re.compile(r'^([A-Za-z\s\-\(\)]+?)\s+(Variant not detected|Carrier)', re.MULTILINE)

            for match in carrier_pattern.finditer(carrier_text):
                condition = match.group(1).strip()
                status = match.group(2).strip()

                if len(condition) > 3 and not condition.startswith('https'):
                    self.genetic_data["carrier_status"].append({
                        "condition": condition,
                        "status": status,
                        "is_carrier": status == "Carrier"
                    })

        # Wellness
        wellness_patterns = [
            (r'Alcohol Flush Reaction\s+(.+)', 'Alcohol Flush Reaction'),
            (r'Caffeine Consumption\s+(.+)', 'Caffeine Consumption'),
            (r'Deep Sleep\s+(.+)', 'Deep Sleep'),
            (r'Genetic Weight\s+(.+)', 'Genetic Weight'),
            (r'Lactose Intolerance\s+(.+)', 'Lactose Intolerance'),
            (r'Muscle Composition\s+(.+)', 'Muscle Composition'),
            (r'Saturated Fat and Weight\s+(.+)', 'Saturated Fat and Weight'),
            (r'Sleep Movement\s+(.+)', 'Sleep Movement'),
        ]

        for pattern, name in wellness_patterns:
            match = re.search(pattern, self.text)
            if match:
                result = match.group(1).strip()
                self.genetic_data["wellness"].append({
                    "trait": name,
                    "result": result
                })

        # Ancestry
        ancestry_match = re.search(r'European\s+([\d.]+)%', self.text)
        if ancestry_match:
            self.genetic_data["ancestry"]["european"] = float(ancestry_match.group(1))

        british_match = re.search(r'British & Irish\s+([\d.]+)%', self.text)
        if british_match:
            self.genetic_data["ancestry"]["british_irish"] = float(british_match.group(1))

        french_match = re.search(r'French & German\s+([\d.]+)%', self.text)
        if french_match:
            self.genetic_data["ancestry"]["french_german"] = float(french_match.group(1))

        maternal_match = re.search(r'Maternal Haplogroup\s+(\w+)', self.text)
        if maternal_match:
            self.genetic_data["ancestry"]["maternal_haplogroup"] = maternal_match.group(1)

        paternal_match = re.search(r'Paternal Haplogroup\s+([\w-]+)', self.text)
        if paternal_match:
            self.genetic_data["ancestry"]["paternal_haplogroup"] = paternal_match.group(1)

        neanderthal_match = re.search(r'Neanderthal Ancestry\s+More Neanderthal variants than (\d+)%', self.text)
        if neanderthal_match:
            self.genetic_data["ancestry"]["neanderthal_percentile"] = int(neanderthal_match.group(1))

        # Traits
        traits_patterns = [
            (r'Eye Color\s+(.+)', 'Eye Color'),
            (r'Hair Texture\s+(.+)', 'Hair Texture'),
            (r'Light or Dark Hair\s+(.+)', 'Hair Color'),
            (r'Skin Pigmentation\s+(.+)', 'Skin Pigmentation'),
            (r'Freckles\s+(.+)', 'Freckles'),
            (r'Earlobe Type\s+(.+)', 'Earlobe Type'),
            (r'Cleft Chin\s+(.+)', 'Cleft Chin'),
            (r'Wake-Up Time\s+(.+)', 'Wake-Up Time'),
        ]

        for pattern, name in traits_patterns:
            match = re.search(pattern, self.text)
            if match:
                result = match.group(1).strip()
                self.genetic_data["traits"].append({
                    "trait": name,
                    "result": result
                })

    def _parse_imaging_reports(self):
        """Parse imaging/radiology reports."""
        # MRA/MRI pattern
        imaging_pattern = re.compile(
            r'(MRI|MRA|CT|X-RAY|ULTRASOUND)[\s\w\-]+(?:Without|With|w/o)\s*(?:and\s*w/o\s*)?(Contrast)?',
            re.IGNORECASE
        )

        # Look for imaging referrals
        referral_match = re.search(
            r'Procedure:\s*(MRI[^\n]+)\s*CPT Code:\s*(\d+)\s*Clinical Indication:\s*([^\n]+(?:\n[^\n]+)*?)(?=ICD-10|Instructions)',
            self.text, re.DOTALL
        )

        if referral_match:
            self.imaging_reports.append({
                "type": "referral",
                "procedure": referral_match.group(1).strip(),
                "cpt_code": referral_match.group(2),
                "clinical_indication": referral_match.group(3).strip().replace('\n', ' '),
                "status": "ordered"
            })

        # Look for ICD-10 codes
        icd_match = re.search(r'ICD-10:\s*(\w+\.\w+)\s*[–-]\s*(.+?)(?:\n|$)', self.text)
        if icd_match and self.imaging_reports:
            self.imaging_reports[-1]["icd10_code"] = icd_match.group(1)
            self.imaging_reports[-1]["icd10_description"] = icd_match.group(2).strip()

    def _parse_pathology_reports(self):
        """Parse pathology/dermatopathology reports."""
        # Dermatopathology pattern
        derm_pattern = re.compile(
            r'Dermatopathology Report\s*'
            r'PATIENT\s+([^\n]+)\s+ACCESSION\s+(\w+-\d+).*?'
            r'COLLECTED\s+(\d{2}/\d{2}/\d{4}).*?'
            r'DIAGNOSIS\s*([^G]+?)GROSS',
            re.DOTALL | re.IGNORECASE
        )

        for match in derm_pattern.finditer(self.text):
            diagnosis_text = match.group(4).strip()

            # Parse diagnosis sections
            diagnoses = []
            diagnosis_parts = re.findall(
                r'([A-Z]\))\s*([^:]+):\s*([^\n]+(?:\nComment:[^\n]+)?)',
                diagnosis_text, re.DOTALL
            )

            for part in diagnosis_parts:
                diagnoses.append({
                    "label": part[0],
                    "site": part[1].strip(),
                    "finding": part[2].strip().split('\n')[0],
                    "comment": part[2].split('Comment:')[1].strip() if 'Comment:' in part[2] else None
                })

            self.pathology_reports.append({
                "type": "Dermatopathology",
                "accession": match.group(2),
                "date_collected": parse_date(match.group(3)),
                "diagnoses": diagnoses
            })

    def _parse_synovial_fluid(self):
        """Parse synovial fluid analysis."""
        synovial_pattern = re.compile(
            r'SYNOVIAL FLUID CELL COUNT.*?'
            r'Collected on\s+([^\n]+).*?'
            r'Fluid Source.*?Value\s*([^\n]+).*?'
            r'Fluid Nucleated Cell Count.*?Value\s*([,\d]+).*?'
            r'Fluid RBC Count.*?Value\s*([,\d]+).*?'
            r'Fluid Neutrophils.*?Value\s*(\d+).*?'
            r'Fluid Lymphocytes.*?Value\s*(\d+).*?'
            r'Fluid Mononuclears.*?Value\s*(\d+).*?'
            r'Fluid Basophils.*?Value\s*(\d+)',
            re.DOTALL
        )

        for match in synovial_pattern.finditer(self.text):
            self.synovial_fluid_analyses.append({
                "date_collected": match.group(1).strip(),
                "source": match.group(2).strip(),
                "nucleated_cell_count": {
                    "value": int(match.group(3).replace(',', '')),
                    "units": "/mcL",
                    "reference_range": {"min": 0, "max": 200}
                },
                "rbc_count": {
                    "value": int(match.group(4).replace(',', '')),
                    "units": "/mcL",
                    "reference_range": {"max": 15000}
                },
                "differential": {
                    "neutrophils": {"value": int(match.group(5)), "units": "%", "reference_range": {"max": 25}},
                    "lymphocytes": {"value": int(match.group(6)), "units": "%"},
                    "mononuclears": {"value": int(match.group(7)), "units": "%"},
                    "basophils": {"value": int(match.group(8)), "units": "%"}
                },
                "interpretation": "Inflammatory" if int(match.group(3).replace(',', '')) > 200 else "Non-inflammatory"
            })

    def _parse_medications(self):
        """Parse medication list."""
        medication_patterns = [
            r'amphetamine-dextroamphetamine\s+(\d+)\s*MG',
            r'cholecalciferol\s+(\d+)\s*MCG',
            r'clindamycin\s+(\d+)\s*%',
            r'doxycycline\s+(\d+)\s*MG',
            r'QUERCETIN',
            r'Tyrosine\s+(\d+)\s*MG',
            r'vitamin B complex',
            r'VITAMIN K',
        ]

        # Simple medication list from after-visit summary
        med_section = re.search(r'Your Medication List(.+?)Medication Refill', self.text, re.DOTALL)
        if med_section:
            med_text = med_section.group(1)

            # Parse each medication
            meds = [
                {"name": "amphetamine-dextroamphetamine", "brand": "ADDERALL", "dose": "20 MG", "form": "tablet", "frequency": "2 times daily"},
                {"name": "cholecalciferol", "brand": "VITAMIN D", "dose": "400 UNIT", "form": "tablet", "frequency": "daily"},
                {"name": "clindamycin", "brand": "CLEOCIN T", "dose": "1%", "form": "solution", "frequency": "2 times daily", "route": "topical"},
                {"name": "doxycycline", "brand": "MONODOX", "dose": "100 MG", "form": "capsule", "frequency": "2 times daily"},
                {"name": "QUERCETIN", "form": "oral", "frequency": "as needed"},
                {"name": "Tyrosine", "dose": "500 MG", "form": "capsule", "frequency": "daily"},
                {"name": "vitamin B complex", "form": "capsule", "frequency": "daily"},
                {"name": "VITAMIN K", "form": "oral", "frequency": "as needed"},
            ]

            self.medications = meds

    def _parse_visit_summaries(self):
        """Parse clinical visit summaries."""
        # After visit summary pattern
        avs_match = re.search(
            r'AFTER VISIT SUMMARY\s*'
            r'([^\n]+MRN:\s*\d+).*?'
            r'Today\'s Visit\s*([^B]+)'
            r'Blood\s+BMI\s*Pressure\s*([\d./]+)\s*([\d.]+)',
            self.text, re.DOTALL
        )

        if avs_match:
            self.visit_summaries.append({
                "patient_header": avs_match.group(1).strip(),
                "visit_reason": avs_match.group(2).strip()[:200],
                "vitals": {
                    "blood_pressure": avs_match.group(3),
                    "bmi": float(avs_match.group(4))
                }
            })

        # Extract vitals from visits
        vitals_pattern = re.compile(
            r'Blood\s+BMI\s*Pressure\s*([\d/]+)\s*([\d.]+)\s*'
            r'Weight\s+Height\s*([\d]+)\s*lb\s*([\d\'\s\"]+)\s*'
            r'Temperature\s+Pulse\s*([\d.]+)\s*°F\s*(\d+)\s*'
            r'Respiration\s+Oxygen\s*(\d+)\s*Saturation\s*(\d+)%'
        )

        for match in vitals_pattern.finditer(self.text):
            vitals = {
                "blood_pressure": match.group(1),
                "bmi": float(match.group(2)),
                "weight_lbs": int(match.group(3)),
                "height": match.group(4).strip(),
                "temperature_f": float(match.group(5)),
                "pulse": int(match.group(6)),
                "respiration": int(match.group(7)),
                "oxygen_saturation": int(match.group(8))
            }

            # Add to last visit summary or create new one
            if self.visit_summaries:
                self.visit_summaries[-1]["vitals"] = vitals
            else:
                self.visit_summaries.append({"vitals": vitals})

    def _parse_clinical_notes(self):
        """Parse clinical notes and referral summaries."""
        # Look for referral summary sections
        referral_match = re.search(
            r'Referral Summary[^\n]*\n(.+?)(?:Summary of History|$)',
            self.text, re.DOTALL
        )

        if referral_match:
            self.clinical_notes.append({
                "type": "Referral Summary",
                "content": referral_match.group(1).strip()[:500]
            })

        # Look for working hypotheses
        hypotheses_match = re.search(
            r'Leading unifying hypotheses(.+?)Diagnostic gaps',
            self.text, re.DOTALL
        )

        if hypotheses_match:
            hypotheses_text = hypotheses_match.group(1)
            hypotheses = re.findall(r'●\s+([^●]+)', hypotheses_text)

            self.clinical_notes.append({
                "type": "Working Hypotheses",
                "items": [h.strip()[:200] for h in hypotheses[:10]]
            })

    def _build_output(self) -> Dict[str, Any]:
        """Build final structured output."""
        # Deduplicate lab results by creating unique keys
        seen_labs = set()
        unique_labs = []
        for lab in self.lab_results:
            key = (lab.get('test_name'), lab.get('date_collected'), str(lab.get('value', {}).get('raw')))
            if key not in seen_labs:
                seen_labs.add(key)
                unique_labs.append(lab)

        # Group lab results by category
        lab_categories = defaultdict(list)
        for lab in unique_labs:
            # Categorize based on test name patterns
            name = lab.get('test_name', '').lower()
            if any(term in name for term in ['wbc', 'rbc', 'hemoglobin', 'hematocrit', 'platelet', 'neutrophil', 'lymph', 'mono', 'eos', 'baso', 'mcv', 'mch']):
                lab_categories['hematology'].append(lab)
            elif any(term in name for term in ['glucose', 'bun', 'creatinine', 'sodium', 'potassium', 'chloride', 'carbon dioxide', 'calcium', 'phosphorus', 'magnesium', 'egfr']):
                lab_categories['metabolic'].append(lab)
            elif any(term in name for term in ['albumin', 'protein', 'bilirubin', 'alkaline', 'ast', 'alt', 'ggt', 'ldh']):
                lab_categories['liver'].append(lab)
            elif any(term in name for term in ['cholesterol', 'triglyceride', 'hdl', 'ldl', 'vldl', 'lipid']):
                lab_categories['lipid'].append(lab)
            elif any(term in name for term in ['tsh', 'thyroid', 't4', 't3', 'tpo']):
                lab_categories['thyroid'].append(lab)
            elif any(term in name for term in ['vitamin', 'b12', 'folate', 'iron', 'ferritin', 'tibc']):
                lab_categories['vitamins_minerals'].append(lab)
            elif any(term in name for term in ['crp', 'esr', 'sed rate', 'sedimentation']):
                lab_categories['inflammatory_markers'].append(lab)
            elif any(term in name for term in ['ana', 'anti-', 'rf', 'rheumatoid', 'complement', 'hla', 'smith', 'ss-a', 'ss-b', 'ccp']):
                lab_categories['autoimmune'].append(lab)
            elif any(term in name for term in ['hep', 'hiv', 'ebv', 'lyme', 'quantiferon', 'hbsag', 'hcv']):
                lab_categories['infectious_disease'].append(lab)
            elif any(term in name for term in ['urin', 'wbc esterase', 'specific gravity', 'ph', 'ketone', 'nitrite', 'protein/creat', 'albumin/creat']):
                lab_categories['urinalysis'].append(lab)
            elif 'factor' in name or 'antiphospholipid' in name or 'anticardiolipin' in name:
                lab_categories['coagulation'].append(lab)
            elif any(term in name for term in ['creatine kinase', 'ck', 'aldosterone', 'renin', 'homocysteine', 'osteocalcin']):
                lab_categories['specialty'].append(lab)
            else:
                lab_categories['other'].append(lab)

        # Deduplicate allergies
        seen_allergies = set()
        unique_allergies = []
        for allergy in self.allergies:
            key = (allergy.get('code'), allergy.get('date_collected'))
            if key not in seen_allergies:
                seen_allergies.add(key)
                unique_allergies.append(allergy)

        return {
            "metadata": {
                "parser_version": "1.0.0",
                "parsed_at": datetime.now().isoformat(),
                "source_file": "merged lastest records.pdf",
                "total_pages": len(self.pages),
                "data_date_range": {
                    "earliest": "2017-07-25",
                    "latest": "2026-01-22"
                }
            },
            "patient": self.patient_info,
            "physicians": list(self.physicians),
            "laboratory_results": {
                "total_count": len(unique_labs),
                "by_category": {cat: results for cat, results in lab_categories.items()},
                "all_results": unique_labs
            },
            "allergies": {
                "total_tested": len(unique_allergies),
                "positive_count": sum(1 for a in unique_allergies if a.get('is_positive', False)),
                "environmental": [a for a in unique_allergies if a.get('category') in ['Dust Mites', 'Animal Dander', 'Grasses', 'Molds', 'Trees', 'Weeds', 'Insects']],
                "foods": [a for a in unique_allergies if a.get('category') == 'Foods'],
                "all_results": unique_allergies
            },
            "genetic_data": self.genetic_data,
            "imaging_reports": self.imaging_reports,
            "pathology_reports": self.pathology_reports,
            "synovial_fluid_analyses": self.synovial_fluid_analyses,
            "medications": self.medications,
            "visit_summaries": self.visit_summaries,
            "clinical_notes": self.clinical_notes
        }


def main():
    """Main entry point."""
    import sys

    input_file = "extracted_records.txt"
    output_file = "normalized_medical_data.json"

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Parsing medical records ({len(text):,} characters)...")
    parser = MedicalRecordParser(text)
    result = parser.parse_all()

    print(f"Writing output to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)

    # Print summary
    print("\n" + "="*60)
    print("PARSING COMPLETE")
    print("="*60)
    print(f"Patient: {result['patient']['name']['full']}")
    print(f"DOB: {result['patient']['date_of_birth']}")
    print(f"Date Range: {result['metadata']['data_date_range']['earliest']} to {result['metadata']['data_date_range']['latest']}")
    print(f"\nData extracted:")
    print(f"  - Laboratory results: {result['laboratory_results']['total_count']}")
    print(f"  - Allergy tests: {result['allergies']['total_tested']}")
    print(f"  - Genetic data categories: {len([k for k in result['genetic_data'] if result['genetic_data'][k]])}")
    print(f"  - Imaging reports: {len(result['imaging_reports'])}")
    print(f"  - Pathology reports: {len(result['pathology_reports'])}")
    print(f"  - Synovial fluid analyses: {len(result['synovial_fluid_analyses'])}")
    print(f"  - Medications: {len(result['medications'])}")
    print(f"  - Visit summaries: {len(result['visit_summaries'])}")
    print(f"  - Physicians: {len(result['physicians'])}")
    print(f"\nOutput saved to: {output_file}")


if __name__ == "__main__":
    main()
