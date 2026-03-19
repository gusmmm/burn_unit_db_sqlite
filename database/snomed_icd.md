SNOMED-CT:

SNOMED-CT FHIR API — Limited free tier available through some countries' health systems
BioPortal SNOMED-CT — https://bioportal.bioontology.org (free registration, API access)
UK SNOMED-CT — If you're in UK/EU, SNOMED-CT is free via NHS; use their API https://termbrowser.nhs.uk/
NLM's UMLS — US National Library of Medicine provides SNOMED-CT mappings (free, requires registration)
ICD-10/ICD-11:

WHO ICD-11 API — https://icd.who.int/icdapi (free, public access)
Can map SNOMED-CT → ICD-11 via this API
2. Script to Fetch Data (Example)

Here's a practical approach using WHO ICD-11 API:

#!/bin/bash
# Fetch ICD-11 entity by search term, extract code and definition

curl -s "https://id.who.int/icd/entity/search?q=burn%20wound&autoexpand=true" \
  | jq '.destinationEntities[] | 
    {icd11_id: .id, name: .title, definition: .definition}'


For SNOMED-CT, use BioPortal:
# BioPortal API (requires free API key)
API_KEY="your_bioportal_api_key"
curl -s "https://data.bioontology.org/search?q=burn&ontologies=SNOMEDCT" \
  -H "Authorization: apikey token=$API_KEY" \
  | jq '.collection[] | {snomed_id: .id, name: .prefLabel}'

