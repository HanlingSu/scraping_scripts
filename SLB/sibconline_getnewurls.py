

# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'sibconline.com.sb'
direct_URLs = []
# sitemap_base = 'https://www.sibconline.com.sb/post-sitemap'

# for i in range(1, 2): # smaller numbered-sitemaps host the more recent stuff.
#     sitemap = sitemap_base + str(i) + '.xml'
#     print('Scraping from ', sitemap, ' ...')
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('td')

#     for i in item:
#         direct_URLs.append(i.find('a')['href'])

#     print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')
text = """
https://www.sibconline.com.sb/solomon-ports-commissions-new-state-of-the-art-domestic-seaport-terminal-building/

https://www.sibconline.com.sb/nori-elected-as-deputy-speaker/

https://www.sibconline.com.sb/pm-manele-conveys-sympathy-to-his-vanuatu-counterpart/

https://www.sibconline.com.sb/msg-prime-ministers-cup-2024-to-observe-minute-of-silence-for-vanuatu-earthquake-victims/

https://www.sibconline.com.sb/wale-urges-gov-to-withdraw-constitution-amendment-constituent-assembly-sitting-bill-2024/

https://www.sibconline.com.sb/australian-supported-malaita-south-road-emergency-road-repairs-completed/

https://www.sibconline.com.sb/lack-of-support-forces-hon-gordon-darcy-lilo-to-withdraw-no-confidence-motion-against-pm-manele/

https://www.sibconline.com.sb/sade-new-minister-for-public-service/

https://www.sibconline.com.sb/young-solomon-islander-turns-interest-to-business/

https://www.sibconline.com.sb/lands-commissioner-defends-dodo-creek-land-sale/

https://www.sibconline.com.sb/lands-commissioner-defends-dodo-creek-land-sale/

https://www.sibconline.com.sb/prime-minister-manele-to-face-no-confidence-vote-on-december-16/

https://www.sibconline.com.sb/western-province-day-marked-in-gizo/

https://www.sibconline.com.sb/year-6-primary-to-7-junior-secondary-placement/

https://www.sibconline.com.sb/mrd-wraps-up-cdf-act-awareness-for-south-guadalcanal-constituency/

https://www.sibconline.com.sb/rsipf-urged-public-to-stay-calm-and-respect-democratic-processes-ahead-of-no-confidence-motion/

https://www.sibconline.com.sb/central-bank-of-solomon-islands-to-launch-a-new-1-dollar-coin-featuring-king-charles-iii-effigy-in-2025/

https://www.sibconline.com.sb/western-day-celebration-kicks-off-in-gizo/

https://www.sibconline.com.sb/pm-manele-received-pngs-former-pm-oneil/

https://www.sibconline.com.sb/30-blind-and-visually-impaired-youths-celebrate-their-remarkable-achievements/

https://www.sibconline.com.sb/30-blind-and-visually-impaired-youths-celebrate-their-remarkable-achievements/

https://www.sibconline.com.sb/constituent-assembly-sitting-bill-2024-goes-through-second-reading/

https://www.sibconline.com.sb/kacific-highlights-satellite-services-at-business-after-five-event/

https://www.sibconline.com.sb/prime-minister-bids-farewell-to-uk-ambassador-h-e-coward/

https://www.sibconline.com.sb/solomon-islands-calls-for-urgent-financial-and-technical-aid-to-tackle-desertification-challenges/

https://www.sibconline.com.sb/asia-pacific-region-reaffirms-commitment-to-unccd-cop16-at-preliminary-meetings/

https://www.sibconline.com.sb/solomon-islands-high-commissioner-to-papua-new-guinea-hosts-onetox-band/

https://www.sibconline.com.sb/pm-manele-suggests-soccer-collaboration-with-spain/

https://www.sibconline.com.sb/solomon-islands-attends-unccd-cop16/

https://www.sibconline.com.sb/pm-manele-meet-ocean-champions/

https://www.sibconline.com.sb/7-new-cases-of-hiv-aids-recorded-in-the-country/

https://www.sibconline.com.sb/australia-supports-oceania-rugby-sevens/

https://www.sibconline.com.sb/spbd-solomon-islands-celebrates-milestone-of-usd-5-million-crowdfunded-through-kiva-partnership/

https://www.sibconline.com.sb/sevens-hosting-golden-opportunity-for-si-sport-tourism-potential/

https://www.sibconline.com.sb/gnut-committed-to-ensure-safety-and-wellbeing-of-all-women-and-girls/

https://www.sibconline.com.sb/prime-minister-meets-with-spc-director-on-geoscience-energy-and-maritime-issues/

https://www.sibconline.com.sb/mataniko-clean-up-campaign-conducted/

https://www.sibconline.com.sb/beijing-30-review-concludes-in-bangkok-with-draft-decisions-to-accelerate-efforts-to-achieving-gender-equality/

https://www.sibconline.com.sb/solomon-islands-assures-beijing-30-conference-of-its-commitment-to-addressing-gender-based-violence/

https://www.sibconline.com.sb/miwa-congratulates-grantees-for-official-approval-of-projects/

https://www.sibconline.com.sb/east-central-guadalcanal-constituency-launches-citrec-programme/

https://www.sibconline.com.sb/solomon-islands-loses-approximately-usd-15-1-million-in-productivity-due-to-violence-against-women-and-girls-in-2021-study-shows/

https://www.sibconline.com.sb/solomon-islands-loses-approximately-usd-15-1-million-in-productivity-due-to-violence-against-women-and-girls-in-2021-study-shows/

https://www.sibconline.com.sb/vaea-highlights-pacific-womens-progress-in-business-leadership-and-education-at-beijing-30-review-conference/

https://www.sibconline.com.sb/miss-solomon-presents-donation-to-the-nrh-cancer-unit/

https://www.sibconline.com.sb/conference-on-beijing-30-review-kicks-off-with-a-strong-call-for-collective-actions-on-achieving-gender-equality/

https://www.sibconline.com.sb/asia-pacific-representatives-gathered-in-bangkok-a-show-of-solidarity-towards-achieving-the-beijing-declaration-and-platform-for-action-towards-gender-equality/

https://www.sibconline.com.sb/malau-lalos-strive-for-mpa-status-leads-to-discovery-of-the-worlds-largest-coral/

https://www.sibconline.com.sb/hon-minister-choylin-yim-douglas-champions-gender-equality-at-inaugural-pacific-talanoa-for-women-in-tourism/

https://www.sibconline.com.sb/sicci-hosts-prestigious-8th-business-excellence-awards/

https://www.sibconline.com.sb/seif-ples-launches-comprehensive-database-to-enhance-safenet-helpline-management/

https://www.sibconline.com.sb/prime-minister-manele-visited-gold-ridge-mining-limited/

https://www.sibconline.com.sb/solomon-islands-voices-need-for-more-data-policies-on-gender-equality-ahead-of-asia-pacific-ministerial-conference-on-the-beijing30-review/

https://www.sibconline.com.sb/pacific-civil-society-and-government-to-advocate-for-gender-equality-at-asia-pacific-ministerial-conference-in-bangkok/

https://www.sibconline.com.sb/numbu-chs-receives-new-classroom-building-from-japan/

https://www.sibconline.com.sb/australia-and-new-zealand-handover-a-new-science-lab-to-reginald-chapman-nicholson-college/

https://www.sibconline.com.sb/bethesda-disability-training-and-support-centre-graduation/

https://www.sibconline.com.sb/a-76-year-old-grandfather-was-arrested-for-raping-three-girls-in-choiseul-province/

https://www.sibconline.com.sb/cplt-5-paid-final-courtesy-call-to-pm-manele/

https://www.sibconline.com.sb/new-discovery-largest-coral-in-the-world-found-in-the-solomon-islands/

https://www.sibconline.com.sb/visit-from-australias-ambassador-for-gender-equality/

https://www.sibconline.com.sb/visit-from-australias-ambassador-for-gender-equality/

https://www.sibconline.com.sb/tabaka-rtc-takes-delivery-of-new-girls-dormitory-and-ablution-block/

https://www.sibconline.com.sb/un-resident-coordinator-undertook-brief-courtesy-visit-to-pm-manele/

https://www.sibconline.com.sb/siec-prepares-for-tandai-ward-by-election-on-wednesday/

https://www.sibconline.com.sb/199m-discretionary-exemptions-granted-in-2024/

https://www.sibconline.com.sb/govt-will-amend-the-anti-corruption-law/

https://www.sibconline.com.sb/gnuts-multimillion-betrayal-wale-slams-fresh-reports-of-a-29m-exemption/

https://www.sibconline.com.sb/china-and-solomon-islands-sign-visa-exemption-agreement-for-ordinary-passport-holders/

https://www.sibconline.com.sb/eu-pledges-to-support-bina-harbour-tuna-processing-plant/

https://www.sibconline.com.sb/world-bank-country-director-paid-courtesy-call-on-pm-manele/

https://www.sibconline.com.sb/education-leaders-attend-change-leadership-training-in-australia/

https://www.sibconline.com.sb/gavi-ceo-meets-health-minister-and-visits-nrh-nms-and-hq-epi/

https://www.sibconline.com.sb/introduction-of-pay-as-you-throw-household-waste-collection-service-pilot-project-in-honiara/

https://www.sibconline.com.sb/three-local-nurses-pilot-labour-mobility-scheme-between-solomon-islands-and-niue/

https://www.sibconline.com.sb/ministry-of-health-and-world-bank-launches-tulagi-hospital-improvement-incinerator-facility-projects/

https://www.sibconline.com.sb/three-permanent-secretaries-reshuffled/

https://www.sibconline.com.sb/govt-values-relationship-with-eu/

https://www.sibconline.com.sb/wale-calls-for-sacking-of-ps-viulu/

https://www.sibconline.com.sb/minister-ramofafia-meets-us-ambassador-to-png-solomon-islands-and-vanuatu-ms-anne-marie-yastishock/

https://www.sibconline.com.sb/university-of-the-south-pacific-establishes-historic-agreement-with-solomon-islands-ministry-of-justice-and-legal-affairs/

https://www.sibconline.com.sb/young-girls-urged-to-notify-family-members-before-going-out/

https://www.sibconline.com.sb/series-of-cdf-act-awareness-underway-in-hkh-constituency/

https://www.sibconline.com.sb/opmc-responds-to-wale-on-west-papua-and-alleged-kidnappings/

https://www.sibconline.com.sb/wale-blasts-pm-on-false-accusations-and-betrayal-of-west-papua/

https://www.sibconline.com.sb/ambassador-walegerea-presents-credentials-as-solomon-islands-permanent-representative-to-irena/

https://www.sibconline.com.sb/pm-manele-presides-over-the-commencement-ceremony-for-the-new-ffa-regional-fisheries-surveillance-centre/

https://www.sibconline.com.sb/joint-announcement-solomon-islands-government-and-oceania-rugby-announce-historic-oceania-rugby-7s-tournament-in-honiara/

https://www.sibconline.com.sb/pm-manele-congratulates-the-ambassador-of-finland-to-solomon-islands/

https://www.sibconline.com.sb/australian-alumna-empowers-her-community-through-fashion/

https://www.sibconline.com.sb/immigration-delegation-attends-high-level-discussions-on-border-management-systems-in-australia/

https://www.sibconline.com.sb/mhms-minister-highlighhts-national-interventions-at-who-75th-rcm/

https://www.sibconline.com.sb/florence-young-ece-centre-students-smiles-onboard-solomon-airlines-to-mark-school-excursion/

https://www.sibconline.com.sb/rsipf-and-oag-discuss-esp-audit-report/

https://www.sibconline.com.sb/mhms-minister-attends-his-first-who-regional-committee-meeting-for-western-pacific/

https://www.sibconline.com.sb/wale-pms-diplomatic-hopscotch-lacks-priorities/

https://www.sibconline.com.sb/solomon-islands-australia-alumni-association-gala-2024/

https://www.sibconline.com.sb/police-receives-two-reports-of-attempted-abduction-incidents-warns-of-spreading-false-information-on-social-media/

https://www.sibconline.com.sb/wale-presses-rsipf-for-updates-on-esp-investigations/

https://www.sibconline.com.sb/pm-manele-among-leaders-who-witnessed-the-inauguration-of-indonesias-president/

https://www.sibconline.com.sb/masi-congratulates-kekea-on-her-selection-to-commonwealth-elections-observer-mission/

https://www.sibconline.com.sb/ministry-of-home-affairs-and-guadalcanal-province-progress-discussion-on-g-province-sporting-facility/

https://www.sibconline.com.sb/foreign-minister-hon-peter-shanel-agovaka-will-lead-solomon-islands-delegation-to-chogm-2024/

https://www.sibconline.com.sb/foreign-minister-hon-peter-shanel-agovaka-will-lead-solomon-islands-delegation-to-chogm-2024/

https://www.sibconline.com.sb/tovosia-education-a-central-pillar-of-gnuts-2024-2028-policy-and-translation-document/

https://www.sibconline.com.sb/mrd-conducts-awareness-on-cdf-act-2023-for-east-kwaio-constituents/

https://www.sibconline.com.sb/public-demands-justice-after-police-arrest-person-and-seize-suspicious-vehicle-linked-to-alleged-abduction-incidents-in-honiara/

https://www.sibconline.com.sb/advice-on-security-measures-to-all-parents-teachers-school-leaders-and-education-providers-in-honiara-guadalcanal-and-all-provinces/

https://www.sibconline.com.sb/pm-invited-to-indonesian-president-inauguration/

https://www.sibconline.com.sb/kiluufi-improvement-project-kick-starts-with-groundbreaking-ceremony/

https://www.sibconline.com.sb/women-in-central-guadalcanal-celebrates-world-food-day/

https://www.sibconline.com.sb/police-arrest-suspect-in-20s-for-alleged-murder-in-honiara/

https://www.sibconline.com.sb/prime-minister-launches-samasodu-communication-tower/

https://www.sibconline.com.sb/mara-top-officials-visit-sape-farm-discuss-potential-areas-of-collaboration/

https://www.sibconline.com.sb/mal-minister-thanks-new-zealand-for-100k-funding-support/

https://www.sibconline.com.sb/pm-manele-attributes-partnership-as-key-to-opening-tarekukure-buying-centre/

https://www.sibconline.com.sb/pm-applauded-los-as-govt-opens-new-buying-center-in-choiseul/

https://www.sibconline.com.sb/minister-leokana-high-commissioner-soaki-opens-waneagu-medical-centre-in-port-moresby/

https://www.sibconline.com.sb/appointment-of-siwa-board-is-lawful/

https://www.sibconline.com.sb/sig-prc-signed-auki-road-project/

https://www.sibconline.com.sb/potentially-polluting-wrecks-a-threat-to-marine-ecosystems-in-solomon-islands/

https://www.sibconline.com.sb/acting-pm-tovosia-receives-courtesy-call-from-sinomach-officials/

https://www.sibconline.com.sb/sinso-deploy-hies-enumerators-for-pilot-test/

https://www.sibconline.com.sb/police-awaits-referral-from-oag-before-investigating-esp-audit-report/

https://www.sibconline.com.sb/manele-says-use-of-esp-is-regrettable-not-fully-to-its-purpose/

https://www.sibconline.com.sb/premier-salini-refuses-to-resign-amid-political-instability/

https://www.sibconline.com.sb/strengthening-marine-pollution-incident-resilience-workshop-kicks-off-in-honiara/

https://www.sibconline.com.sb/australia-awards-short-course-launched/

https://www.sibconline.com.sb/prc-donates-livelihood-materials-to-isabel-province/

https://www.sibconline.com.sb/61147-2/

https://www.sibconline.com.sb/police-investigate-suspicious-death-in-west-honiara/

https://www.sibconline.com.sb/mehrd-officially-opens-kgvi-national-secondary-school-lecture-theatre/

https://www.sibconline.com.sb/urgent-call-to-strengthen-government-grants-regime-after-esp-audit-reveals-major-fraud-risk-weak-administration-and-poor-transparency/

https://www.sibconline.com.sb/61128-2/

https://www.sibconline.com.sb/58-year-old-male-arrested-over-stabbing-incident/

https://www.sibconline.com.sb/acting-pm-calls-for-increased-partnership-with-ngos/

https://www.sibconline.com.sb/mehrd-on-track-to-implement-new-teachers-salary-structure/

https://www.sibconline.com.sb/prime-minister-manele-commends-uaes-abrahamic-family-house-icon-of-harmonious-coexistence/

https://www.sibconline.com.sb/sictu-congratulate-the-auditor-general-and-his-officers-for-the-successful-release-of-the-covid-stimulus-package-funding-audit-report/

https://www.sibconline.com.sb/world-teachers-day-celebrated-in-honiara/

https://www.sibconline.com.sb/our-students-in-israel-are-safe-and-secure/

https://www.sibconline.com.sb/malaita-leader-arrested-for-allegedly-masterminding-unlawful-assemblies/

https://www.sibconline.com.sb/pm-manele-honours-founder-and-late-president-of-the-united-arab-emirates/

https://www.sibconline.com.sb/auditors-office-recommends-the-release-of-10-esp-evaluation-reports/

https://www.sibconline.com.sb/tovosia-usp-honiara-campus-a-pillar-of-transformation/

https://www.sibconline.com.sb/47-year-old-suspect-arrested-for-alleged-allegation-of-false-pretense/

https://www.sibconline.com.sb/office-of-the-auditor-general-uncovers-concerning-fraud-risks-in-relation-to-esp/

https://www.sibconline.com.sb/pm-bilateral-consultation-with-abfd-and-irena/

https://www.sibconline.com.sb/agribusiness-producers-in-malaita-province-hailed/

https://www.sibconline.com.sb/5-to-contest-tandai-ward-by-election/

https://www.sibconline.com.sb/sictu-commends-npf-for-4-percent-crediting-rate/

https://www.sibconline.com.sb/police-arrest-man-in-30s-for-causing-serious-injury/

https://www.sibconline.com.sb/cocoa-sector-getting-sweeter-in-solomon-islands/

https://www.sibconline.com.sb/prime-minister-manele-inaugurates-solomon-islands-new-embassy-in-abu-dhabi/

https://www.sibconline.com.sb/police-arrest-a-38-year-old-male-teacher-for-the-allegation-of-rape-in-western-province/

https://www.sibconline.com.sb/uk-cocoa-buyers-undertake-successful-trade-mission-to-solomon-islands/

https://www.sibconline.com.sb/eye-care-professionals-prepare-for-annual-national-eye-conference/

https://www.sibconline.com.sb/solomon-islands-tourism-industry-join-the-global-community-in-celebrating-world-tourism-day-2024/

https://www.sibconline.com.sb/agovaka-paris-agreement-a-failure/

https://www.sibconline.com.sb/pm-has-left-for-uae-and-saudi-arabia/

https://www.sibconline.com.sb/the-australian-and-new-zealand-governments-handover-new-classrooms-to-lambi-community-high-school/

https://www.sibconline.com.sb/solomon-islands-holds-bilateral-meeting-with-the-republic-of-estonia-at-the-side-events-of-79th-session-of-unga/

https://www.sibconline.com.sb/sicci-launches-2024-business-excellence-awards/

https://www.sibconline.com.sb/solomon-islands-calls-for-urgent-action-to-address-global-antimicrobial-resistance/

https://www.sibconline.com.sb/minister-vokia-outdated-global-institutions-created-to-deal-with-conflicts-must-be-reformed/

https://www.sibconline.com.sb/foreign-minister-agovaka-delivers-national-statement-un-general-assembly/

https://www.sibconline.com.sb/solomon-islands-reaffirms-its-supports-for-the-implementation-of-the-united-nations-fourth-decade-for-the-eradication-of-colonialism/

https://www.sibconline.com.sb/solomon-islands-china-5th-anniversary-reception-held-in-beijing/

https://www.sibconline.com.sb/sia-set-for-the-junior-world-taekwondo-championship-in-korea/

https://www.sibconline.com.sb/minister-of-foreign-affairs-and-external-trade-hon-peter-shanel-agovaka-signed-and-ratified-the-treaty-on-the-prohibition-of-nuclear-weapon/

https://www.sibconline.com.sb/accelerated-action-needed-on-addressing-existential-sea-level-rise-threats/

https://www.sibconline.com.sb/proposed-si-us-development-cooperation-framework-remains-undecided/

https://www.sibconline.com.sb/ministry-of-education-took-delivery-of-a-new-forklift/

https://www.sibconline.com.sb/minister-agovaka-held-talks-with-indonesias-minister-of-foreign-affairs-on-expanding-solomon-islands-and-indonesia-bilateral-cooperation/

https://www.sibconline.com.sb/a-9-year-old-girl-tragically-killed-in-a-burning-home/

https://www.sibconline.com.sb/solomon-islands-and-rwanda-formalize-diplomatic-relations/

https://www.sibconline.com.sb/sibcs-fm-96-3-and-abc-radio-australias-fm-107-now-in-auki-and-surrounding-communities/

https://www.sibconline.com.sb/7th-pacific-media-summit-officially-opens-in-niue/

https://www.sibconline.com.sb/premier-veo-reshuffles-two-ministers-and-welcomes-new-minister-into-executive/

https://www.sibconline.com.sb/police-arrest-suspect-in-relation-to-panatina-campus-zebra-crossing-accident/

https://www.sibconline.com.sb/solomon-islands-calls-for-urgent-global-financial-reforms-at-un-summit/

https://www.sibconline.com.sb/prime-minister-manele-scheduled-to-visit-the-united-arab-emirates-uae-and-saudi-arabia/

https://www.sibconline.com.sb/sibc-celebrates-72-years-of-broadcasting/

https://www.sibconline.com.sb/honiara-sets-ambitious-goal-for-100-percent-renewable-energy-by-2030/

https://www.sibconline.com.sb/police-urges-landing-craft-operators-to-ensure-their-boats-are-sea-worthy/

https://www.sibconline.com.sb/pm-manele-forego-unga-to-focus-on-important-legislations/

https://www.sibconline.com.sb/makira-ulawa-pursues-aviation-expansion-for-tourism-development/

https://www.sibconline.com.sb/sinu-mourns-tragic-loss-of-a-student-and-calls-for-immediate-road-safety-measures/

https://www.sibconline.com.sb/pm-manele-asserts-confidence-in-gnuts-unity-amid-political-tension/

https://www.sibconline.com.sb/government-delegation-heads-to-79th-unga-as-pm-manele-focuses-on-key-domestic-legislation/

https://www.sibconline.com.sb/minister-wasi-says-there-is-huge-potential-for-coconut-and-cocoa/

https://www.sibconline.com.sb/health-ministry-and-world-bank-launches-safe-green-and-climate-proof-healthcare-facility-initiative/

https://www.sibconline.com.sb/australia-to-provide-record-breaking-scholarships-to-solomon-islands/

https://www.sibconline.com.sb/mtgpea-celebrates-world-international-peace-day/

https://www.sibconline.com.sb/mal-secures-usd19-8m-funding-from-ifad-to-support-rural-farmers/

https://www.sibconline.com.sb/pm-manele-opens-national-energy-summit/

https://www.sibconline.com.sb/working-together-for-a-healthier-solomon-islands/

https://www.sibconline.com.sb/solomon-airlines-celebrates-first-commercial-flights-to-santo-and-auckland-to-santo-via-port-vila/

https://www.sibconline.com.sb/mnpdc-thanks-undp-gov4res-project-for-supporting-the-ministrys-communication-efforts/

https://www.sibconline.com.sb/png-community-in-honiara-celebrates-independence-day/

https://www.sibconline.com.sb/premier-salini-takes-bold-action-amid-political-turmoil/

https://www.sibconline.com.sb/minister-kuma-says-special-economic-zone-policy-remains-top-priority/

https://www.sibconline.com.sb/fisheries-ministry-boosts-seaweed-tilapia-and-sea-cucumber-farming/

https://www.sibconline.com.sb/woodford-international-school-students-off-to-singapore-for-2023-first-global-challenge/

https://www.sibconline.com.sb/govt-begins-review-to-re-establish-public-works-department-pwd/

https://www.sibconline.com.sb/woodford-international-school-to-represent-country-at-2024-first-global-challenge-in-greece/

https://www.sibconline.com.sb/minister-of-education-assures-members-of-parliament-that-the-scholarship-grants-is-ready-to-be-released-to-them/

https://www.sibconline.com.sb/new-zealand-festival-held-in-honiara/

https://www.sibconline.com.sb/police-investigates-death-of-female-deceased-found-at-mataniko-river/

https://www.sibconline.com.sb/ors-successfully-disposed-more-than-2700-bombs/

https://www.sibconline.com.sb/discussions-underway-with-mpg-on-relocation-of-vulnerable-communities/

https://www.sibconline.com.sb/pm-manele-reminds-parl-it-is-state-responsibility-to-house-the-pm/

https://www.sibconline.com.sb/building-bridges-for-safety-the-solomon-islands-vision-for-cooperative-security/

https://www.sibconline.com.sb/solomon-islands-high-commissioner-to-png-meets-pope-francis-in-port-moresby/

https://www.sibconline.com.sb/australian-government-delivers-school-books-to-temotu-province/

https://www.sibconline.com.sb/opposition-discloses-pms-1-7m-housing-rental-to-foreigner/

https://www.sibconline.com.sb/bina-habor-project-important-sicci/

https://www.sibconline.com.sb/nati-in-fote-redevelopment-plan-progressing/

https://www.sibconline.com.sb/japan-conducts-tour-of-project-sites/

https://www.sibconline.com.sb/nrh-operating-theatre-set-to-resume-normal-operations-this-week/

https://www.sibconline.com.sb/pm-manele-discloses-cost-of-four-official-visits-overseas/

https://www.sibconline.com.sb/his-excellency-makabo-presents-credentials-to-the-hon-president-of-india/

https://www.sibconline.com.sb/solomon-islands-and-hong-kong-renew-mou-on-aviation-meteorological-services/

https://www.sibconline.com.sb/solomon-islands-and-australia-open-new-biomolecular-laboratory-in-lata/

https://www.sibconline.com.sb/citizenship-by-investment-bill/

https://www.sibconline.com.sb/wale-encourage-ministers-to-take-responsibility-seriously/

https://www.sibconline.com.sb/the-uk-awards-a-record-seven-chevening-scholarships-to-solomon-islanders/

https://www.sibconline.com.sb/ministers-of-health-of-solomon-islands-and-republic-of-vanuatu-sign-health-workers-south-south-cooperation-mou/

https://www.sibconline.com.sb/dpm-tovosia-pledges-to-push-pacific-water-agenda-at-pifs-in-2025/

https://www.sibconline.com.sb/minister-bosawai-ordered-immediate-termination-of-certain-health-staff-found-to-have-stolen-medicines/

https://www.sibconline.com.sb/new-zealand-championing-the-fight-against-the-spread-of-coconut-rhinoceros-beetle-in-the-solomon-islands/

https://www.sibconline.com.sb/ministry-of-lands-welcomes-high-court-ruling-against-pari-development/

https://www.sibconline.com.sb/sig-roundtable-meeting-with-development-partners-to-strengthen-development-partnerships-set-for-wednesday/

https://www.sibconline.com.sb/finance-minister-launches-2025-budget-strategy/

https://www.sibconline.com.sb/lets-set-the-records-right/

https://www.sibconline.com.sb/urgent-search-for-missing-man-in-sea-tragedy-continues/

https://www.sibconline.com.sb/two-children-sustain-broken-legs-and-arms-in-the-latest-traffic-accident-in-makira-ulawa-province/

https://www.sibconline.com.sb/agriculture-sector-needs-more-support/

https://www.sibconline.com.sb/mehrd-leads-strategic-workshop-on-education-data-management-with-support-from-australia-and-new-zealand/

https://www.sibconline.com.sb/minister-of-health-and-chair-of-parliamentary-health-committee-attend-8th-asia-pacific-parliamentarian-forum-on-global-health/

https://www.sibconline.com.sb/wale-probes-trip-never-sanctioned-by-cabinet/

https://www.sibconline.com.sb/solomon-islands-and-united-states-sign-bilateral-explosive-ordnance-agreement/

https://www.sibconline.com.sb/mhms-conducts-investigations-in-wagina/
"""

direct_URLs = text.split('\n')
final_result = [i for i in direct_URLs if "http" in i]
#  pd.read_csv("/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/SLB/sibconline.csv")['0']
print('Total number of urls found: ', len(final_result))



url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        # we need to modify the url since there is a typo in scraped urls.
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            

            ## Implementing blacklisting using category info:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('div', {'class' : 'crumbs'}).text.strip()
            except:
                category = "News"

            print(category)

            blacklist = ['Sports', 'Entertainment', 'Arts and Culture', 'Culture', 'Boxing', 'Pacific Games']
            if any(substr in category for substr in blacklist):
                article['date_publish'] = None
                article['title'] = "From uninterested category"
                article['maintext'] = None

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            
            if "by" in article['maintext'][:3]:
                article['maintext'] = '\n'.join(article['maintext'].split('\n')[1:])
                print("newsplease maintext: ", article['maintext'][:50])

                


      
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! UPDATED.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

print("Done inserting", url_count, "manually collected urls from",  source, "into the db.")
