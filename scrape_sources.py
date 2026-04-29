import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import DATA_DIR

TOPICS = [
    {
        "title": "EU Blue Card Germany",
        "filename": "eu_blue_card_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/eu-blue-card",
        ],
    },
    {
        "title": "Work Visa Germany",
        "filename": "work_visa_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/work-qualified-professionals",
            "https://www.make-it-in-germany.com/en/looking-for-foreign-professionals/entering/german-work-visa",
        ],
    },
    {
        "title": "Skilled Worker Visa Germany",
        "filename": "skilled_worker_visa.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/work-qualified-professionals",
            "https://service.berlin.de/dienstleistung/305304/en/",
        ],
    },
    {
        "title": "Student Visa Germany",
        "filename": "student_visa_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/studying",
            "https://www.make-it-in-germany.com/en/study-vocational-training/studies-in-germany/requirements",
        ],
    },
    {
        "title": "Vocational Training Visa Germany",
        "filename": "vocational_training_visa.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/training",
            "https://www.make-it-in-germany.com/en/study-vocational-training/training-in-germany/requirements-for-vocational-training",
        ],
    },
    {
        "title": "Opportunity Card Chancenkarte Germany",
        "filename": "opportunity_card_chancenkarte.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/job-search-opportunity-card",
            "https://www.make-it-in-germany.com/en/visa-residence/opportunity-card/questions-answers",
        ],
    },
    {
        "title": "Job Search and Job Seeker Options Germany",
        "filename": "job_seeker_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/job/looking-for-job",
            "https://www.make-it-in-germany.com/en/visa-residence/types/job-search-opportunity-card",
        ],
    },
    {
        "title": "Family Reunion Germany",
        "filename": "family_reunion_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/family-reunification",
        ],
    },
    {
        "title": "Spouse and Children Joining Germany",
        "filename": "bringing_spouse_and_children.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/family-reunification",
            "https://service.berlin.de/dienstleistung/328191/en/",
        ],
    },
    {
        "title": "Settlement Permit Permanent Residence Germany",
        "filename": "settlement_permit_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/living-permanently/settlement-permit",
            "https://service.berlin.de/dienstleistung/326558/en/",
        ],
    },
    {
        "title": "Naturalisation Citizenship Germany",
        "filename": "naturalisation_germany.txt",
        "urls": [
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Einbuergerung/einbuergerung.html",
        ],
    },
    {
        "title": "Job Change on Residence Permit Germany",
        "filename": "job_change_residence_permit.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/326856/en/",
            "https://www.make-it-in-germany.com/en/visa-residence/types/eu-blue-card",
        ],
    },
    {
        "title": "Job Loss or Permit Expiring Soon Germany",
        "filename": "job_loss_blue_card_work_visa.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/326233/en/",
            "https://service.berlin.de/dienstleistung/326856/en/",
        ],
        "note": "Official source coverage is limited for job loss scenarios. The saved text focuses on related official guidance about fictional certificates, valid residence titles, and employment changes.",
    },
    {
        "title": "Visa Extension and Change of Residence Purpose Germany",
        "filename": "visa_extension_change_purpose.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/305304/en/",
            "https://service.berlin.de/dienstleistung/329328/en/",
            "https://service.berlin.de/dienstleistung/326233/en/",
        ],
    },
    {
        "title": "German Language Requirements and Integration Courses",
        "filename": "german_language_requirements.txt",
        "urls": [
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Integrationskurse/integrationskurse-node.html",
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Integrationskurse/Abschlusspruefung/abschlusspruefung-node.html",
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/DeutschBeruf/deutsch-beruf.html",
        ],
    },
    {
        "title": "Finding a Job in Germany",
        "filename": "finding_job_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/job/looking-for-job",
            "https://www.make-it-in-germany.com/en/working-in-germany/job/application",
        ],
    },
    {
        "title": "Employment Contract Probation Notice Vacation Germany",
        "filename": "employment_contract_basics.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/work-contract",
        ],
    },
    {
        "title": "Working Hours Sick Leave Termination Germany",
        "filename": "working_rights_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/work-contract",
        ],
        "note": "This topic has limited English official source coverage in the current source list. The document includes employment contract, working hours, leave, notice period, and related official text where available.",
    },
    {
        "title": "Unemployment Benefits Basics Germany",
        "filename": "unemployment_benefits_basics.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/salary-taxes-social-security",
        ],
    },
    {
        "title": "Recognition of Foreign Qualifications Germany",
        "filename": "recognition_foreign_qualifications.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/recognition/who-needs",
            "https://www.make-it-in-germany.com/en/visa-residence/types/recognition",
        ],
    },
    {
        "title": "Regulated Professions Germany",
        "filename": "regulated_professions_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/recognition/who-needs",
            "https://www.make-it-in-germany.com/en/visa-residence/types/work-qualified-professionals",
        ],
    },
    {
        "title": "Salary Gross Net Taxes Social Security Germany",
        "filename": "salary_gross_net_social_security.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/salary-taxes-social-security",
        ],
    },
    {
        "title": "Income Tax and Tax Return Basics Germany",
        "filename": "income_tax_tax_return_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/salary-taxes-social-security",
            "https://www.bundesfinanzministerium.de/Web/EN/Issues/Taxation/taxation.html",
        ],
    },
    {
        "title": "Tax ID Tax Number Tax Classes Germany",
        "filename": "tax_id_tax_classes_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/salary-taxes-social-security",
            "https://www.make-it-in-germany.com/en/service/glossary/glossar/do/show/lohnsteuerklasse",
        ],
        "note": "Official English source coverage for Steuernummer is limited in this source set; this document focuses on tax classes and employee tax basics from reliable sources.",
    },
    {
        "title": "German Tax ID Steueridentifikationsnummer",
        "filename": "tax_id_germany.txt",
        "urls": [
            "https://online.portal.bzst.de/SharedDocs/Leistungsbeschreibung/EN/erneute_mitteilung_der_ID-Nr.html",
            "https://verwaltung.bund.de/leistungsverzeichnis/EN/leistung/99102044101000/herausgeber/LeiKa-102730390/region/00",
            "https://www.bzst.de/EN/Private_individuals/Tax_identification_number/tax_identification_number.html",
            "https://www.bzst.de/DE/Behoerden/SteuerlicheIdentifikationsnummer/steuerlicheidentifikationsnummer_node.html",
        ],
        "note": "Official BZSt sources explain that new citizens receive a tax identification number automatically after first registration in Germany. BZSt also notes in German that the identification number is intended to replace the tax number for income tax in the long term.",
    },
    {
        "title": "Pension and Social Insurance Germany",
        "filename": "pension_social_security.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/working-in-germany/working-environment/salary-taxes-social-security",
            "https://www.deutsche-rentenversicherung.de/DRV/EN/Versicherung/versicherung_node.html",
        ],
    },
    {
        "title": "Health Insurance Contributions Germany",
        "filename": "health_insurance_contributions.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/money-insurance/health-insurance",
            "https://gesund.bund.de/en/health-insurance",
        ],
    },
    {
        "title": "Anmeldung City Registration Germany",
        "filename": "anmeldung_registration.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/120686/",
        ],
    },
    {
        "title": "Buergeramt Appointment and Registration Certificate Germany",
        "filename": "buergeramt_registration_certificate.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/120686/standort/327761/",
            "https://service.berlin.de/dienstleistung/326233/en/",
        ],
    },
    {
        "title": "Opening a Bank Account Germany",
        "filename": "bank_account_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/money-insurance/bank-account",
        ],
    },
    {
        "title": "Radio Tax Rundfunkbeitrag Germany",
        "filename": "rundfunkbeitrag_germany.txt",
        "urls": [
            "https://www.rundfunkbeitrag.de/welcome/english",
            "https://www.rundfunkbeitrag.de/index.html",
        ],
    },
    {
        "title": "Driving Licence and Car Registration Germany",
        "filename": "driving_licence_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/driving-licence-car",
            "https://www.bmv.de/SharedDocs/EN/Articles/StV/Roadtraffic/validity-foreign-driving-licences-in-germany.html",
        ],
    },
    {
        "title": "Public Transport and Deutschlandticket Germany",
        "filename": "public_transport_germany.txt",
        "urls": [
            "https://int.bahn.de/en/offers/regional/deutschland-ticket",
            "https://int.bahn.de/en/trains/local-transport",
            "https://www.bvg.de/en/subscriptions-and-tickets/all-tickets",
        ],
    },
    {
        "title": "Statutory and Private Health Insurance Germany",
        "filename": "health_insurance_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/money-insurance/health-insurance",
            "https://gesund.bund.de/en/health-insurance",
        ],
    },
    {
        "title": "Doctor Appointments and Emergency Numbers Germany",
        "filename": "doctor_appointments_emergency_numbers.txt",
        "urls": [
            "https://gesund.bund.de/en/choosing-a-doctor-and-finding-an-appointment",
            "https://gesund.bund.de/en/notfallnummern",
        ],
    },
    {
        "title": "Liability and Household Insurance Germany",
        "filename": "liability_household_insurance.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/money-insurance",
        ],
        "note": "Official English source coverage for liability and household insurance is limited in this source set. This document uses reliable overview material where available.",
    },
    {
        "title": "Renting Apartment Germany",
        "filename": "renting_apartment_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/housing-registration",
        ],
        "include_keywords": [
            "Your first accommodation",
            "What types of accommodation are available?",
            "How can I find accommodation?",
            "Viewing a property",
            "What documents do I need to rent a flat?",
            "Rent",
        ],
        "stop_keywords": ["Tenancy agreement"],
    },
    {
        "title": "Rental Contract Deposit Warm Rent Cold Rent Germany",
        "filename": "rental_contract_deposit_warm_cold_rent.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/housing-registration",
        ],
        "include_keywords": [
            "Rent",
            "Tenancy agreement",
        ],
        "stop_keywords": ["House rules and waste sorting"],
    },
    {
        "title": "Tenant Rights Quiet Hours Moving Waste Germany",
        "filename": "tenant_rights_basics.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/housing-registration",
        ],
        "include_keywords": [
            "Tenancy agreement",
            "House rules and waste sorting",
            "Visitors and family reunification",
            "Moving in",
        ],
        "stop_keywords": ["Finding support"],
    },
    {
        "title": "Waste Separation Recycling Germany",
        "filename": "waste_separation_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/housing-registration",
        ],
        "include_keywords": ["House rules and waste sorting"],
        "stop_keywords": ["Visitors and family reunification"],
    },
    {
        "title": "Family Benefits Kindergeld Parental Allowance Germany",
        "filename": "family_benefits_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/family-life/financial-support-families",
            "https://familienportal.de/familienportal/familienleistungen/kindergeld/faq",
            "https://familienportal.de/familienportal/meta/languages/family-benefits/parental-allowance-141952",
        ],
    },
    {
        "title": "Kita School System Family Life Germany",
        "filename": "kita_school_system_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/family-life",
        ],
        "note": "This topic depends heavily on federal state and city rules. The document contains general reliable source material where available.",
    },
    {
        "title": "Maternity Protection Parental Leave Germany",
        "filename": "maternity_parental_leave_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/family-life/financial-support-families",
            "https://familienportal.de/familienportal/meta/languages/family-benefits/parental-allowance-141952",
        ],
    },
    {
        "title": "Studying in Germany",
        "filename": "studying_in_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/study-vocational-training/studies-in-germany/requirements",
            "https://www.make-it-in-germany.com/en/visa-residence/types/studying",
        ],
    },
    {
        "title": "Blocked Account and Student Work Rules Germany",
        "filename": "blocked_account_student_work.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/studying",
        ],
    },
    {
        "title": "Post Study Job Search Permit Germany",
        "filename": "post_study_job_search_permit.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/studying",
            "https://www.make-it-in-germany.com/en/visa-residence/types/job-search-opportunity-card",
        ],
    },
    {
        "title": "Ausbildung Vocational Training Germany",
        "filename": "ausbildung_vocational_training.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/study-vocational-training/training-in-germany/vocational",
            "https://www.make-it-in-germany.com/en/visa-residence/types/training",
        ],
    },
    {
        "title": "Dual Citizenship Integration Course Life in Germany Test",
        "filename": "dual_citizenship_integration_test.txt",
        "urls": [
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Einbuergerung/einbuergerung.html",
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Integrationskurse/Abschlusspruefung/abschlusspruefung-node.html",
        ],
    },
    {
        "title": "Migration Advice Legal Help Official Contacts Germany",
        "filename": "migration_advice_legal_help.txt",
        "urls": [
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/BeratungErwachsene/beratung-erwachsene-node.html",
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/BeratungJungeMenschen/beratung-jungemenschen-node.html",
        ],
    },
    {
        "title": "Lost Passport and Indian Consular Help Germany",
        "filename": "lost_passport_indian_consular_help.txt",
        "urls": [
            "https://indianembassyberlin.gov.in/",
            "https://www.germany.info/us-en/service",
        ],
        "note": "Source coverage may vary by nationality and consular district. This document stores official consular/service pages for later retrieval.",
    },
    {
        "title": "Hobbies Clubs and Vereine Germany",
        "filename": "hobbies_and_vereins_germany.txt",
        "urls": [
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/BeratungErwachsene/beratung-erwachsene-node.html",
            "https://www.berlin.de/events/",
        ],
    },
    {
        "title": "German Festivals Public Holidays Local Events",
        "filename": "german_festivals_public_holidays.txt",
        "urls": [
            "https://www.berlin.de/en/tourism/travel-information/1887651-2862820-public-holidays-school-holidays.en.html",
            "https://www.berlin.de/events/",
        ],
    },
    {
        "title": "Indian Community Germany",
        "filename": "indian_community_germany.txt",
        "urls": [
            "https://www.bharatverein.org/about/",
            "https://indiafederationgermany.de/",
            "https://www.gdiz.de/en/",
        ],
        "note": "Community information is based on established association websites. It is factual and not a personal recommendation.",
    },
    {
        "title": "Indian Festivals Germany",
        "filename": "indian_festivals_germany.txt",
        "urls": [
            "https://www.wedesi.de/",
            "https://kuko-ev.de/ags-projects-and-organisations/ag-ico-indian-culture-organization/?lang=en",
            "https://www.ifv-wolfsburg.de/",
        ],
        "note": "Official government coverage is limited for Indian cultural festivals in Germany. This document uses established community and Verein pages where available.",
    },
    {
        "title": "Renting a Car in Germany",
        "filename": "car_rental_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/housing-mobility/driving-licence-car",
            "https://www.adac.de/verkehr/recht/verkehrsmittel/auto-mieten/",
        ],
    },
    {
        "title": "Electricity Water Internet and Heating Contracts Germany",
        "filename": "electricity_water_internet_heating_contracts.txt",
        "urls": [
            "https://www.verbraucherzentrale.de/energie/so-koennen-sie-ihren-anbieter-von-strom-und-gas-wechseln-88520",
            "https://www.verbraucherzentrale.de/wissen/digitale-welt/mobilfunk-und-festnetz/umzug-die-rechte-der-telefon-und-internetkunden-11034",
        ],
    },
    {
        "title": "Types of Insurance in Germany",
        "filename": "insurance_types_germany.txt",
        "urls": [
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/weitere-versicherungen/zum-start-in-ausbildung-oder-job-welche-versicherungen-brauche-ich-40786",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/weitere-versicherungen/kfzversicherung-pflicht-fuer-alle-halterinnen-von-kraftfahrzeugen-13890",
        ],
    },
    {
        "title": "Pet Rules in Germany",
        "filename": "pet_rules_germany.txt",
        "urls": [
            "https://service.berlin.de/dienstleistung/330785/",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/weitere-versicherungen/haftpflichtversicherung-fuer-haustiere-33442",
            "https://www.tierschutzbund.de/en/animals-topics/animal-emergencies/keeping-pets-in-the-apartment/",
        ],
    },
    {
        "title": "Pregnancy in Germany",
        "filename": "pregnancy_germany.txt",
        "urls": [
            "https://gesund.bund.de/en/prenatal-care",
            "https://familienportal.de/familienportal/familienleistungen/mutterschaftsleistungen",
        ],
    },
    {
        "title": "Kindergeld and Child Benefits Germany",
        "filename": "kindergeld_child_benefits.txt",
        "urls": [
            "https://familienportal.de/familienportal/familienleistungen/kindergeld",
            "https://familienportal.de/familienportal/familienleistungen/elterngeld",
        ],
    },
    {
        "title": "Kita Childcare and School System Germany",
        "filename": "kita_childcare_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/family-life/child-care",
            "https://www.make-it-in-germany.com/en/living-in-germany/family-life/school-system",
        ],
    },
    {
        "title": "Child Health Insurance and Birth Registration Germany",
        "filename": "child_health_birth_registration.txt",
        "urls": [
            "https://gesund.bund.de/en/kinderaerztliche-versorgung",
            "https://service.berlin.de/dienstleistung/318957/",
        ],
    },
    {
        "title": "Unemployment Benefits Germany",
        "filename": "unemployment_benefits_germany.txt",
        "urls": [
            "https://www.arbeitsagentur.de/arbeitslos-arbeit-finden/arbeitslosengeld",
            "https://www.arbeitsagentur.de/arbeitslos-arbeit-finden/arbeitslosengeld/finanzielle-hilfen/arbeitslosengeld-anspruch-hoehe-dauer",
            "https://www.arbeitsagentur.de/en/press/2025-36-avoid-financial-disadvantages-register-as-a-job-seeker-well-in-advance",
        ],
    },
    {
        "title": "Travel in Germany",
        "filename": "travel_in_germany.txt",
        "urls": [
            "https://int.bahn.de/en/trains/local-transport",
            "https://int.bahn.de/en/offers/regional/deutschland-ticket",
            "https://www.germany.travel/en/home.html",
        ],
    },
    {
        "title": "Day Trips in Germany",
        "filename": "day_trips_germany.txt",
        "urls": [
            "https://int.bahn.de/en/trains/local-transport",
            "https://www.germany.travel/en/towns-cities-culture/top-100/germany-travel-attractions.html",
            "https://www.germany.travel/en/inspiring-germany/spectacular-views-germany-at-your-feet.html",
        ],
    },
    {
        "title": "Hiking in Germany",
        "filename": "hiking_germany.txt",
        "urls": [
            "https://www.germany.travel/en/nature-outdoor-activities/goldsteig.html",
            "https://www.germany.travel/en/nature-outdoor-activities/sauerland-rothaargebirge-nature-park.html",
            "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/hiking/index.htm",
        ],
    },
    {
        "title": "Must See Places in Germany",
        "filename": "must_see_places_germany.txt",
        "urls": [
            "https://www.germany.travel/en/towns-cities-culture/top-100/germany-travel-attractions.html",
            "https://www.germany.travel/en/royal-palaces-castles/neuschwanstein-castle.html",
            "https://www.germany.travel/en/cities-culture/must-see-museums.html",
        ],
    },
    {
        "title": "Jobs in Germany",
        "filename": "jobs_in_germany.txt",
        "urls": [
            "https://www.arbeitsagentur.de/int/en/how-to-find-a-job",
            "https://www.arbeitsagentur.de/int/en/professional-qualifications",
            "https://www.make-it-in-germany.com/en/working-in-germany/job/application",
        ],
    },
    {
        "title": "German Language Learning",
        "filename": "german_language_learning.txt",
        "urls": [
            "https://www.goethe.de/ins/de/en/uun/dln/ger.html",
            "https://www.goethe.de/en/spr/prf/kop.html",
            "https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Integrationskurse/Abschlusspruefung/abschlusspruefung-node.html",
        ],
    },
    {
        "title": "Investing in Germany",
        "filename": "investing_in_germany.txt",
        "urls": [
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/sparen-und-anlegen/das-kleine-einmaleins-der-geldanlage-10622",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/sparen-und-anlegen/augenmass-bei-geldanlagen-so-koennen-sie-risiken-streuen-12435",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/sparen-und-anlegen/welche-vorteile-und-nachteile-haben-etfs-16603",
        ],
        "note": "This is general information, not financial advice.",
    },
    {
        "title": "Buying a House in Germany",
        "filename": "buying_house_germany.txt",
        "urls": [
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/bau-und-immobilienfinanzierung/immobilienfinanzierung-so-berechnen-sie-was-sie-sich-leisten-koennen-5822",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/bau-und-immobilienfinanzierung/immobilienfinanzierung-diese-modelle-gibt-es-und-das-sollten-sie-beachten-5801",
            "https://www.verbraucherzentrale.de/wissen/geld-versicherungen/bau-und-immobilienfinanzierung/immobilienfinanzierung-haeufige-fragen-rund-um-hauskauf-und-hauskredit-6992",
        ],
    },
    {
        "title": "German History Basics",
        "filename": "german_history_basics.txt",
        "urls": [
            "https://www.britannica.com/place/Germany",
            "https://www.dw.com/en/german-history/t-66293225",
            "https://www.tatsachen-ueber-deutschland.de/en",
        ],
    },
    {
        "title": "German Culture",
        "filename": "german_culture.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/settling/useful-everyday-knowledge",
            "https://handbookgermany.de/en/faq",
            "https://handbookgermany.de/en/learning-german/",
        ],
    },
    {
        "title": "German Festivals",
        "filename": "german_festivals.txt",
        "urls": [
            "https://www.oktoberfest.de/en/magazine/tradition/the-history-of-oktoberfest",
            "https://www.germany.travel/en/christmas",
            "https://www.germany.travel/en/inspiring-germany/german-carnival-hotspots.html",
        ],
    },
    {
        "title": "German Rules and Etiquette",
        "filename": "german_rules_etiquette.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/settling/useful-everyday-knowledge",
            "https://handbookgermany.de/en/waste-separation",
            "https://service.berlin.de/dienstleistung/327974/en/",
        ],
    },
    {
        "title": "German Public Holidays",
        "filename": "german_public_holidays.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/settling/useful-everyday-knowledge",
            "https://www.berlin.de/en/tourism/travel-information/1740536-2862820-shopping-hours-sunday-shopping.en.html",
            "https://service.berlin.de/dienstleistung/327974/en/",
        ],
    },
    {
        "title": "Weather in Germany",
        "filename": "weather_in_germany.txt",
        "urls": [
            "https://www.germany.travel/en/travelling-to-germany.html",
            "https://www.dwd.de/EN/climate_environment/climateenvironment_node.html",
        ],
        "note": "This document covers general weather and climate basics only. Live weather requires a current weather service or API.",
    },
    {
        "title": "German Work Environment",
        "filename": "german_work_environment.txt",
        "urls": [
            "https://handbookgermany.de/labor-rights",
            "https://handbookgermany.de/en/sick-leave",
            "https://handbookgermany.de/en/work/employment-contract.html",
        ],
    },
    {
        "title": "Day to Day Life Germany",
        "filename": "day_to_day_life_germany.txt",
        "urls": [
            "https://www.make-it-in-germany.com/en/living-in-germany/settling/useful-everyday-knowledge",
            "https://handbookgermany.de/en/money-saving-tips",
            "https://handbookgermany.de/en/waste-separation",
        ],
    },
]


def make_filename(title):
    filename = title.lower()
    filename = re.sub(r"[^a-z0-9]+", "_", filename)
    filename = filename.strip("_")
    return f"{filename}.txt"


def remove_unwanted_elements(soup):
    unwanted_selectors = [
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "button",
        "noscript",
        "svg",
        "iframe",
        "[role='navigation']",
        "[role='banner']",
        "[role='contentinfo']",
    ]

    for tag in soup.select(",".join(unwanted_selectors)):
        tag.decompose()

    unwanted_words = [
        "breadcrumb",
        "cookie",
        "consent",
        "banner",
        "overlay",
        "modal",
        "newsletter",
        "share",
        "social",
        "tracking",
    ]

    for tag in soup.find_all(True):
        if tag.attrs is None:
            continue

        tag_text = " ".join(
            [
                tag.get("id", ""),
                " ".join(tag.get("class", [])),
                tag.get("role", ""),
                tag.get("aria-label", ""),
            ]
        ).lower()

        if any(word in tag_text for word in unwanted_words):
            tag.decompose()


def choose_main_content(soup):
    return (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.body
        or soup
    )


def clean_line(text):
    return " ".join(text.split())


def extract_structured_text(html):
    soup = BeautifulSoup(html, "html.parser")
    remove_unwanted_elements(soup)
    main_content = choose_main_content(soup)

    lines = []
    seen_lines = set()
    useful_tags = ["h1", "h2", "h3", "h4", "p", "li", "th", "td"]

    for tag in main_content.find_all(useful_tags):
        line = clean_line(tag.get_text(" ", strip=True))
        if not line:
            continue

        if len(line) < 3:
            continue

        key = line.lower()
        if key in seen_lines:
            continue
        seen_lines.add(key)

        if tag.name in ["h1", "h2", "h3", "h4"]:
            lines.append("")
            lines.append(line)
        elif tag.name == "li":
            lines.append(f"- {line}")
        else:
            lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_url(url):
    response = requests.get(
        url,
        timeout=25,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ExpatAIAssistantScraper/2.0)"
        },
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def filter_text_by_sections(text, include_keywords, stop_keywords=None):
    stop_keywords = stop_keywords or []
    lines = text.splitlines()
    kept_lines = []
    keep = False

    def matches_heading(line, keywords):
        line_lower = line.strip().lower()
        return any(line_lower == keyword.lower() for keyword in keywords)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if keep and kept_lines and kept_lines[-1] != "":
                kept_lines.append("")
            continue

        if matches_heading(stripped, stop_keywords):
            if keep:
                keep = False
            continue

        if matches_heading(stripped, include_keywords):
            keep = True

        if keep:
            kept_lines.append(line)

    filtered = "\n".join(kept_lines).strip()
    return filtered or text


def scrape_topic(topic):
    print(f"Scraping topic: {topic['title']}")

    successful_sources = []
    content_parts = []

    if topic.get("note"):
        content_parts.append(f"Limited coverage note: {topic['note']}")

    for url in topic["urls"]:
        try:
            print(f"  Downloading: {url}")
            html = fetch_url(url)
            text = extract_structured_text(html)
            if topic.get("include_keywords"):
                text = filter_text_by_sections(
                    text,
                    topic["include_keywords"],
                    topic.get("stop_keywords"),
                )

            if not text:
                print(f"  Failed: no readable text found for {url}")
                continue

            successful_sources.append(url)
            domain = urlparse(url).netloc
            content_parts.append(f"Source section: {domain}\n{text}")
        except Exception as error:
            print(f"  Failed: {url} - {error}")

    if not successful_sources:
        print(f"  Skipped: no source text saved for {topic['title']}")
        return

    DATA_DIR.mkdir(exist_ok=True)
    output_path = DATA_DIR / topic.get("filename", make_filename(topic["title"]))

    source_lines = "\n".join(f"Source: {url}" for url in successful_sources)
    if not source_lines:
        source_lines = "Source: Limited reliable source coverage available"

    content_text = "\n\n".join(content_parts)
    output = (
        f"Title: {topic['title']}\n"
        f"{source_lines}\n"
        "Content:\n\n"
        f"{content_text}\n"
    )

    output_path.write_text(output, encoding="utf-8")
    print(f"  Saved: {output_path}")


def main():
    for topic in TOPICS:
        scrape_topic(topic)

    print("\nDone. Rebuild the vector database with: python ingest.py")


if __name__ == "__main__":
    main()
