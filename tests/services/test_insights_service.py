import pytest
from unittest.mock import MagicMock, patch
from chalicelib.services.InsightsService import InsightsService
import copy

@pytest.fixture
def service():
    with patch("chalicelib.services.InsightsService.db") as mock_db:
        yield InsightsService(), mock_db


def test_get_insights(service):
    insights_service, mock_db = service

    listing_id = "1"
    # whenever get_item is called on the fake db, sample_data will be returned (create a deepcopy since it is being mutated)
    mock_db.get_applicants.return_value = copy.deepcopy(SAMPLE_APPLICANTS)

    result = insights_service.get_insights_from_listing(listing_id)
    # confirm that database was called once with correct inputs
    mock_db.get_applicants.assert_called_once_with(
        table_name="zap-applications",
        listing_id=listing_id
    )

    assert len(result) == 2
    assert result[0] == SAMPLE_DASHBOARD 
    assert result[1] == SAMPLE_DISTRIBUTION



SAMPLE_DASHBOARD = {
    "applicantCount": 3,
    "avgGpa": 3.8,
    "commonMajor": "Chaos Engineering",
    "avgGradYear": 2025
}

SAMPLE_DISTRIBUTION = {
    "colleges": [
        {
            "name": "CAS",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "Wheelock",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "Sargent",
            "value": 2,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                },
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        },
        {
            "name": "Pardee",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "gpa": [
        {
            "name": "N/A",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "3.99",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                }
            ]
        },
        {
            "name": "3.6",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "gradYear": [
        {
            "name": "2022",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "2026",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                }
            ]
        },
        {
            "name": "2028",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "major": [
        {
            "name": "Culinary Arts",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "Chaos Engineering",
            "value": 2,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                },
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "minor": [
        {
            "name": "Rock Climbing",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                }
            ]
        },
        {
            "name": "N/A",
            "value": 1,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                }
            ]
        },
        {
            "name": "Biology",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "linkedin": [
        {
            "name": "N/A",
            "value": 2,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                },
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                }
            ]
        },
        {
            "name": "True",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ],
    "website": [
        {
            "name": "N/A",
            "value": 2,
            "applicants": [
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": True,
                        "Wheelock": True,
                        "Sargent": True,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "in the Hat",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:57:46.760096-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Rat",
                    "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
                    "minor": "Rock Climbing",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
                    "gpa": "",
                    "hasGpa": False,
                    "gradYear": "2022",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
                    "major": "Culinary Arts",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": "Jay"
                },
                {
                    "website": "",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": False,
                        "Pardee": False,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "Coast",
                    "linkedin": "",
                    "dateApplied": "2024-02-09T14:59:14.575818-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Wes",
                    "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
                    "minor": "",
                    "events": {
                        "infoSession2": False,
                        "professionalPanel": False,
                        "infoSession1": False,
                        "resumeWorkshop": False,
                        "socialEvent": False
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
                    "gpa": "3.99",
                    "hasGpa": True,
                    "gradYear": "2026",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "January",
                    "phone": "2032091600",
                    "preferredName": ""
                }
            ]
        },
        {
            "name": "True",
            "value": 1,
            "applicants": [
                {
                    "website": "https://github.com/wderocco8",
                    "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
                    "colleges": {
                        "COM": False,
                        "QST": False,
                        "CDS": False,
                        "CAS": False,
                        "Wheelock": False,
                        "Sargent": True,
                        "Pardee": True,
                        "SHA": False,
                        "CGS": False,
                        "ENG": False,
                        "CFA": False,
                        "Other": False
                    },
                    "responses": [],
                    "lastName": "The Breaker",
                    "linkedin": "https://www.linkedin.com/in/william-derocco/",
                    "dateApplied": "2024-02-09T14:56:23.066712-05:00",
                    "email": "wergewretr@gmail.com",
                    "firstName": "Bob",
                    "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
                    "minor": "Biology",
                    "events": {
                        "infoSession2": True,
                        "professionalPanel": True,
                        "infoSession1": True,
                        "resumeWorkshop": True,
                        "socialEvent": True
                    },
                    "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
                    "gpa": "3.6",
                    "hasGpa": True,
                    "gradYear": "2028",
                    "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
                    "major": "Chaos Engineering",
                    "gradMonth": "May",
                    "phone": "2032091600",
                    "preferredName": "Bobert"
                }
            ]
        }
    ]
}

SAMPLE_APPLICANTS = [
    {
        "website": "",
        "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
        "colleges": {
            "COM": False,
            "QST": False,
            "CDS": False,
            "CAS": True,
            "Wheelock": True,
            "Sargent": True,
            "Pardee": False,
            "SHA": False,
            "CGS": False,
            "ENG": False,
            "CFA": False,
            "Other": False
        },
        "responses": [],
        "lastName": "in the Hat",
        "linkedin": "",
        "dateApplied": "2024-02-09T14:57:46.760096-05:00",
        "email": "wergewretr@gmail.com",
        "firstName": "Rat",
        "applicantId": "9d5c3489-6535-447a-8696-c35eec239c0d",
        "minor": "Rock Climbing",
        "events": {
            "infoSession2": False,
            "professionalPanel": True,
            "infoSession1": True,
            "resumeWorkshop": False,
            "socialEvent": False
        },
        "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.jpg",
        "gpa": "",
        "hasGpa": False,
        "gradYear": "2022",
        "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/in the Hat_Rat_9d5c3489-6535-447a-8696-c35eec239c0d.pdf",
        "major": "Culinary Arts",
        "gradMonth": "January",
        "phone": "2032091600",
        "preferredName": "Jay"
    },
    {
        "website": "",
        "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
        "colleges": {
            "COM": False,
            "QST": False,
            "CDS": False,
            "CAS": False,
            "Wheelock": False,
            "Sargent": False,
            "Pardee": False,
            "SHA": False,
            "CGS": False,
            "ENG": False,
            "CFA": False,
            "Other": False
        },
        "responses": [],
        "lastName": "Coast",
        "linkedin": "",
        "dateApplied": "2024-02-09T14:59:14.575818-05:00",
        "email": "wergewretr@gmail.com",
        "firstName": "Wes",
        "applicantId": "db3a4d5e-7480-4ef4-83c3-8abd1373764c",
        "minor": "",
        "events": {
            "infoSession2": False,
            "professionalPanel": False,
            "infoSession1": False,
            "resumeWorkshop": False,
            "socialEvent": False
        },
        "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.png",
        "gpa": "3.99",
        "hasGpa": True,
        "gradYear": "2026",
        "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/Coast_Wes_db3a4d5e-7480-4ef4-83c3-8abd1373764c.pdf",
        "major": "chAos EngInEering",
        "gradMonth": "January",
        "phone": "2032091600",
        "preferredName": ""
    },
    {
        "website": "https://github.com/wderocco8",
        "listingId": "a6612ed3-6d48-45c4-ab39-fbd946b8cbe8",
        "colleges": {
            "COM": False,
            "QST": False,
            "CDS": False,
            "CAS": False,
            "Wheelock": False,
            "Sargent": True,
            "Pardee": True,
            "SHA": False,
            "CGS": False,
            "ENG": False,
            "CFA": False,
            "Other": False
        },
        "responses": [],
        "lastName": "The Breaker",
        "linkedin": "https://www.linkedin.com/in/william-derocco/",
        "dateApplied": "2024-02-09T14:56:23.066712-05:00",
        "email": "wergewretr@gmail.com",
        "firstName": "Bob",
        "applicantId": "e6522255-8853-484e-ba9a-d6687fbc2bce",
        "minor": "Biology",
        "events": {
            "infoSession2": True,
            "professionalPanel": True,
            "infoSession1": True,
            "resumeWorkshop": True,
            "socialEvent": True
        },
        "image": "https://whyphi-zap.s3.amazonaws.com/dev/image/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.jpg",
        "gpa": "3.6",
        "hasGpa": True,
        "gradYear": "2028",
        "resume": "https://whyphi-zap.s3.amazonaws.com/dev/resume/a6612ed3-6d48-45c4-ab39-fbd946b8cbe8/The Breaker_Bob_e6522255-8853-484e-ba9a-d6687fbc2bce.pdf",
        "major": "Chaos Engineering",
        "gradMonth": "May",
        "phone": "2032091600",
        "preferredName": "Bobert"
    }
]