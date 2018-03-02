import csv

inreader = None
inputs = []
doe = []

with open('tmp/org-sync/corrected-pre.tsv', 'rU') as file:
    inreader = csv.DictReader(file, dialect='excel-tab')

    for row in inreader:
        inputs.append(row)


with open('tmp/org-sync/doe-list.csv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel')

    for row in reader:
        doe.append(row)


header = []

for f in inreader.fieldnames:
    header.append(f)

print('\t'.join(header))

for line in inputs:
    if len(line['ATS_CODE']):
        line['HEATHER_DID_IT_FIRST'] = ''

        for record in doe:
            if line['ATS_CODE'].strip() == record['ATS System Code'].strip():
                managed_by = record.get('Managed By Name')

                if managed_by == 'DOE':
                    managed_by = 'NYC Public'

                line['DOE_NAME'] = record['Location Name']
                line['NYCOD_NAME'] = ''
                line['HEATHER_DID_IT_FIRST'] = 'corrected'
                line['TYPE_OF_SCHOOL'] = managed_by
                line['ADDRESS_1'] = record.get('Primary Address', '')
                line['NEIGHBORHOOD'] = record.get('NTA_Name', '')
                line['CITY'] = record.get('City', '')
                line['STATE'] = record.get('State Code', '')
                line['ZIP'] = record.get('Zip', '')
                line['COMMUNITY_BOARD'] = record.get('Community District', '')
                line['COUNCIL_DISTRICT'] = record.get('Council District', '')
                line['PRINCIPAL'] = record.get('Principal Name', '')
                line['PRINCIPAL_PHONE'] = record.get('Principal Phone Number', '')

    outline = []

    for f in inreader.fieldnames:
        outline.append(line.get(f))

    print('\t'.join(outline))
