"""Tests for the ECCS Source-to-Expanse mapping runtime."""
from src.eccs_mapping_runtime.candidate_mapping import (
    build_candidates,
    select_top_candidate,
)


def test_candidate_ranking():
    """Validate candidate ranking by weighted score."""
    source = {
        "Facility": "COCAG",
        "Mnemonic": "ABSCESS",
        "NameDescription": "Abscess",
        "PASecondaryKey": "123",
        "Active": "Y",
        "SourceRowId": "1",
    }

    targets = [
        {
            "Facility": "COCAG",
            "Mnemonic": "ABSCESS",
            "NameDescription": "Abscess",
            "PASecondaryKey": "123",
            "Active": "Y",
        },
        {
            "Facility": "OTHER",
            "Mnemonic": "OTHER",
            "NameDescription": "Other",
            "PASecondaryKey": "999",
            "Active": "N",
        },
    ]

    candidates = build_candidates(
        source_row=source,
        target_rows=targets,
    )

    assert len(candidates) == 2
    assert candidates[0]["rank"] == 1
    assert candidates[0]["score"] == 100
    assert candidates[0]["grade"] == "Complete"
    assert candidates[0]["sourceRowId"] == "1"


def test_select_top_candidate():
    """Validate selection of the highest-ranked candidate."""
    candidates = [
        {
            "rank": 1,
            "score": 80,
            "grade": "Complete",
        },
        {
            "rank": 2,
            "score": 60,
            "grade": "Tertiary",
        },
    ]

    selected = select_top_candidate(candidates)

    assert selected is not None
    assert selected["rank"] == 1
    assert selected["score"] == 80
    
from src.eccs_mapping_runtime.csv_mapping import (
    REQUIRED_COLUMNS,
    read_upload_csv,
)
from src.eccs_mapping_runtime.matcher import (
    MatchWeights,
    calculate_match_score,
    grade_for_score,
)


def test_primary_grade_boundaries():
    """Validate the Primary grade score boundaries."""
    assert grade_for_score(0) == "Primary"
    assert grade_for_score(25) == "Primary"


def test_secondary_grade_boundaries():
    """Validate the Secondary grade score boundaries."""
    assert grade_for_score(26) == "Secondary"
    assert grade_for_score(50) == "Secondary"


def test_tertiary_grade_boundaries():
    """Validate the Tertiary grade score boundaries."""
    assert grade_for_score(51) == "Tertiary"
    assert grade_for_score(75) == "Tertiary"


def test_complete_grade_boundaries():
    """Validate the Complete grade score boundaries."""
    assert grade_for_score(76) == "Complete"
    assert grade_for_score(100) == "Complete"


def test_complete_weighted_match():
    """Validate a complete five-field weighted match."""
    source = {
        "Facility": "COCAG",
        "Mnemonic": "ABSCESS",
        "NameDescription": "Abscess",
        "PASecondaryKey": "123",
        "Active": "Y",
    }

    target = {
        "Facility": "COCAG",
        "Mnemonic": "ABSCESS",
        "NameDescription": "Abscess",
        "PASecondaryKey": "123",
        "Active": "Y",
    }

    result = calculate_match_score(source, target)

    assert result.score == 100
    assert result.grade == "Complete"
    assert result.matched_fields == (
        "Facility",
        "Mnemonic",
        "NameDescription",
        "PASecondaryKey",
        "Active",
    )


def test_facility_only_match():
    """Validate a facility-only match score."""
    source = {
        "Facility": "COCAG",
        "Mnemonic": "SOURCE",
        "NameDescription": "Source",
        "PASecondaryKey": "1",
        "Active": "Y",
    }

    target = {
        "Facility": "COCAG",
        "Mnemonic": "TARGET",
        "NameDescription": "Target",
        "PASecondaryKey": "2",
        "Active": "N",
    }

    result = calculate_match_score(source, target)

    assert result.score == 30
    assert result.grade == "Secondary"


def test_custom_weights():
    """Validate custom field weights."""
    weights = MatchWeights(
        facility=50,
        mnemonic=20,
        name_description=10,
        secondary_key=10,
        active=10,
    )

    source = {
        "Facility": "A",
        "Mnemonic": "B",
        "NameDescription": "C",
        "PASecondaryKey": "D",
        "Active": "Y",
    }

    target = {
        "Facility": "A",
        "Mnemonic": "X",
        "NameDescription": "X",
        "PASecondaryKey": "X",
        "Active": "N",
    }

    result = calculate_match_score(
        source,
        target,
        weights,
    )

    assert result.score == 50
    assert result.grade == "Secondary"


def test_upload_template_required_columns():
    """Validate the required upload CSV columns."""
    expected = {
        "Domain",
        "SourceSystem",
        "Facility_Source",
        "Mnemonic_Source",
        "Name_Source",
        "Active_Source",
        "Target_Environment",
        "Requested_Action",
        "Source_Row_Id",
    }

    assert expected.issubset(set(REQUIRED_COLUMNS))


def test_upload_template_reads_first_row():
    """Validate the first row of the ECCS upload template."""
    rows = read_upload_csv(
        "workbooks/incoming/ECCS_UPLOAD/templates/ECCS_Bulk_Mapping_Upload_Template.csv"
    )

    assert len(rows) >= 1
    assert rows[0]["Domain"] == "Registration"
    assert rows[0]["SourceSystem"] == "Source System"
    assert rows[0]["Facility"] == "COCAG"
    assert rows[0]["Mnemonic"] == "ABSCESS"
    assert rows[0]["NameDescription"] == "Abscess"
    assert rows[0]["Active"] == "Y"
    assert rows[0]["TargetEnvironment"] == "DR"
    assert rows[0]["RequestedAction"] == "Review"
    assert rows[0]["SourceRowId"] == "1"
    
from src.eccs_mapping_runtime.result_builder import (
    build_mapping_result,
)


def test_build_mapping_result():
    """Validate construction of a candidate mapping result."""
    source = {
        "SourceRowId": "1",
    }

    candidate = {
        "rank": 1,
        "score": 100,
        "grade": "Complete",
        "target": {
            "Facility": "COCAG",
        },
        "matchedFields": [
            "Facility",
            "Mnemonic",
        ],
    }

    result = build_mapping_result(
        source_row=source,
        candidate=candidate,
    )

    assert result["SourceRowId"] == "1"
    assert result["Status"] == "Candidate"
    assert result["Score"] == 100
    assert result["Grade"] == "Complete"
    assert result["TargetFound"] is True
    assert result["RequiresReview"] is True
    assert result["RequiresApproval"] is True
    
from src.eccs_mapping_runtime.pipeline import (
    process_upload,
)


def test_process_upload_pipeline():
    """Validate CSV upload through candidate mapping and results."""
    targets = [
        {
            "Facility": "COCAG",
            "Mnemonic": "ABSCESS",
            "NameDescription": "Abscess",
            "PASecondaryKey": "",
            "Active": "Y",
        }
    ]

    results = process_upload(
        csv_path=(
            "workbooks/incoming/ECCS_UPLOAD/"
            "templates/ECCS_Bulk_Mapping_Upload_Template.csv"
        ),
        target_rows=targets,
    )

    assert len(results) == 1
    assert results[0]["SourceRowId"] == "1"
    assert results[0]["Score"] == 90
    assert results[0]["Grade"] == "Complete"
    assert results[0]["CandidateCount"] == 1
    
    
    
