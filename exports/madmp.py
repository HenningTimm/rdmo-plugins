import json

from django.http import HttpResponse

from rdmo.projects.exports import Export


class MaDMPExport(Export):

    currency_codes = [
        "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
        "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
        "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
        "COP", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD",
        "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "GBP", "GEL", "GGP", "GHS",
        "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
        "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
        "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT",
        "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD",
        "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", "MZN",
        "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK",
        "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
        "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLL", "SOS", "SPL*","SRD",
        "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY",
        "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VEF",
        "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR",
        "ZMW", "ZWD"
    ]

    data_access_options = {
        'dataset_sharing_options/69 ': 'open',
        'dataset_sharing_options/68': 'shared',
        'dataset_sharing_options/67': 'shared',
        'dataset_sharing_options/70': 'closed'
    }

    certified_with_options = {
        # '': 'din31644',
        # '': 'dini-zertifikat',
        # '': 'dsa',
        # '': 'iso16363',
        # '': 'iso16919',
        # '': 'trac',
        # '': 'wds',
        # '': 'coretrustseal'
    }

    pid_system_options = {
        'pid_types/124': 'ark',
        # '': 'arxiv',
        # '': 'bibcode',
        'pid_types/123': 'doi',
        # '': 'ean13',
        # '': 'eissn',
        # '': 'handle',
        # '': 'igsn',
        # '': 'isbn',
        # '': 'issn',
        # '': 'istc',
        # '': 'lissn',
        # '': 'lsid',
        # '': 'pmid',
        'pid_types/122': 'purl',
        # '': 'upc',
        # '': 'url',
        'pid_types/120': 'urn',
        'pid_types/154': 'other',
        'pid_types/121': 'other'
    }

    license_ref_options = {
        'dataset_license_types/71': 'https://creativecommons.org/licenses/by/4.0/',
        'dataset_license_types/73': 'https://creativecommons.org/licenses/by-nc/4.0/',
        'dataset_license_types/74': 'https://creativecommons.org/licenses/by-nd/4.0/',
        'dataset_license_types/75': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'dataset_license_types/cc0': 'https://creativecommons.org/publicdomain/zero/1.0/deed.de'
    }

    def render(self):
        self.values = self.project.values.filter(snapshot=self.snapshot)

        dmp = {
            'title': 'maDMP for {}'.format(self.project.title),
            'created': self.project.created.isoformat(),
            'modified': self.project.updated.isoformat(),
            # 'language': self.project.language
        }

        contact_name = self.get_value('project/dmp/contact/name')
        if contact_name:
            dmp['contact'] = {
                'name': contact_name,
                'mbox': self.get_text('project/dmp/contact/mbox'),
                'contact_id': {
                    'identifier': self.get_text('project/dmp/contact/identifier'),
                    'type': self.get_text('project/dmp/contact/identifier_type')
                }
            }

        dmp['contributor'] = []
        for role, attribute in [
            ('Contact person', 'project/partner/contact_person'),
            ('Responsible for backup', 'project/dataset/data_security/backup_responsible'),
            ('Responsible for metadata', 'project/dataset/metadata/responsible_person'),
            ('Responsible for PIDs', 'project/dataset/pids/responsible_person'),
            ('Responsible for preservation', 'project/preservation/responsible_person')
        ]:
            name = self.get_text(attribute + '/name')
            if name:
                contributor = {
                    'role': role,
                    'name': name
                }

                mbox = self.get_text(attribute + '/mbox')
                if mbox:
                    contributor['mbox'] = mbox

                identifier = self.get_text(attribute + '/identifier')
                if identifier:
                    contributor['contributor_id'] = {
                        'identifier': identifier,
                        'type': self.get_text(attribute + '/identifier_type') or 'orcid'
                    }

                dmp['contributor'].append(contributor)

        dmp['cost'] = []
        for title, attribute in [
            ('Personal costs for data creation', 'project/costs/creation/personnel'),
            ('Non personal costs for data creation', 'project/costs/creation/non_personnel'),
            ('Personal costs for data usage', 'project/costs/usage/personnel'),
            ('Non personal costs for data creation', 'project/costs/usage/non_personnel'),
            ('Personal costs for data storage', 'project/costs/storage/personnel'),
            ('Non personal costs for data storage', 'project/costs/storage/non_personnel'),
            ('Personal costs for metadata curation', 'project/costs/metadata/personnel'),
            ('Non personal costs for metadata curation', 'project/costs/metadata/non_personnel'),
            ('Personal costs for PID curation', 'project/costs/pid/personnel'),
            ('Non personal costs for PID curation', 'project/costs/pid/non_personnel'),
            ('Personal costs for data anonymization', 'project/costs/sensitive_data/anonymization/personnel'),
            ('Non personal costs for data anonymization', 'project/costs/sensitive_data/anonymization/non_personnel'),
            ('Personal costs for data security', 'project/costs/sensitive_data/security/personnel'),
            ('Non personal costs  for data security', 'project/costs/sensitive_data/security/non_personnel'),
            ('Personal costs for interlectual property rights', 'project/costs/ipr/personnel'),
            ('Non personal costs for interlectual property rights', 'project/costs/ipr/non_personnel'),
            ('Personal costs for preservation', 'project/costs/preservation/personnel'),
            ('Non personal costs for preservation', 'project/costs/preservation/non_personnel')
        ]:
            value = self.get_value(attribute)
            if value:
                cost = {
                    'title': title,
                    'value': value.text
                }

                if value.unit:
                    cost['description'] = '{} in {}'.format(title, value.unit)

                # this is a hack to make 'Euro' work
                if value.unit.upper()[:3] in self.currency_codes:
                    cost['currency_code'] = value.unit.upper()[:3]

                dmp['cost'].append(cost)

        dmp['dataset'] = []
        for dataset in self.get_set('project/dataset/id'):
            dmp_dataset = {
                'title': self.get_text('project/dataset/id', dataset.set_index)
            }

            description = self.get_text('project/dataset/description', dataset.set_index)
            if description:
                dmp_dataset['description'] = description

            data_quality_assurance = self.get_text('project/dataset/quality_assurance', dataset.set_index)
            if data_quality_assurance:
                dmp_dataset['data_quality_assurance'] = data_quality_assurance

            dataset_identifier = self.get_text('project/dataset/dataset_identifier', dataset.set_index)
            if dataset_identifier:
                dmp_dataset['dataset_id'] = {
                    'identifier': dataset_identifier,
                    'type': self.get_text('project/dataset/dataset_identifier', dataset.set_index)
                }
            else:
                dmp_dataset['dataset_id'] = {
                    'identifier': self.get_text('project/dataset/id', dataset.set_index),
                    'type': 'other'
                }

            # distribution during the project
            distribution_during = {}

            distribution_during_access_url = self.get_text('project/dataset/storage/uri', dataset.set_index)
            if distribution_during_access_url:
                distribution_during['access_url'] = distribution_during_access_url

            distribution_during_data_access = self.get_value('project/dataset/sharing/yesno', dataset.set_index)
            if distribution_during_data_access:
                option_path = distribution_during_data_access.option.path
                distribution_during['data_access'] = self.data_access_options[option_path]

            value = self.get_value('project/dataset/format', dataset.set_index)
            if value:
                distribution_during['format'] = value.text

            if distribution_during:
                if 'distribution' not in dmp_dataset:
                    dmp_dataset['distribution'] = []

                dmp_dataset['distribution'].append({
                    'title': 'Storage during the project',
                    **distribution_during
                })

            # distribution after the project
            distribution_after = {}

            certified_with = self.get_value('project/dataset/preservation/certification', dataset.set_index)
            if certified_with and certified_with.option:
                distribution_after['certified_with'] = self.certified_with_options[certified_with.option.path]

            pid_system = self.get_value('project/dataset/pids/system', dataset.set_index)
            if pid_system and pid_system.option:
                distribution_after['pid_system'] = self.pid_system_options[pid_system.option.path]

            host_title = self.get_value('project/dataset/preservation/repository', dataset.set_index)
            if host_title:
                distribution_after['host'] = {
                    'title': host_title.value
                }

            license_ref = self.get_value('project/dataset/sharing/conditions', dataset.set_index)
            if license_ref and license_ref.option and license_ref.option.path in self.license_ref_options:
                distribution_after['license'] = {
                    'license_ref': self.license_ref_options[license_ref.option.path]
                }

                start_date = self.get_value('project/dataset/data_publication_date', dataset.set_index)
                if start_date.value:
                    distribution_after['license']['start_date'] = start_date.value.isoformat()

            if distribution_after:
                if 'distribution' not in dmp_dataset:
                    dmp_dataset['distribution'] = []

                dmp_dataset['distribution'].append({
                    'title': 'Preservation after the project',
                    **distribution_after
                })

            issued = self.get_value('project/dataset/data_publication_date', dataset.set_index)
            if issued.value:
                dmp_dataset['issued'] = issued.value.isoformat()

            keywords = [value.text for value in self.get_values('project/research_question/keywords')]
            if keywords:
                dmp_dataset['keyword'] = ', '.join(keywords)

            personal_data = self.get_value('project/dataset/sensitive_data/personal_data_yesno/yesno', dataset.set_index)
            if personal_data:
                dmp_dataset['personal_data'] = 'yes' if personal_data.text == '1' else 'No'
            else:
                dmp_dataset['personal_data'] = 'unknown'

            sensitive_data = self.get_value('project/dataset/sensitive_data/personal_data/bdsg_3_9', dataset.set_index)
            if sensitive_data:
                dmp_dataset['sensitive_data'] = 'yes' if sensitive_data.text == '1' else 'no'
            else:
                dmp_dataset['sensitive_data'] = 'unknown'

            preservation_statement = self.get_value('project/dataset/preservation/purpose', dataset.set_index)
            if preservation_statement and preservation_statement.text:
                dmp_dataset['preservation_statement'] = preservation_statement.text

            dmp['dataset'].append(dmp_dataset)

        dmp['project'] = [
            {
                'title': self.project.title,
                'description': self.project.description,
                'start': self.get_timestamp('project/schedule/project_start'),
                'end': self.get_timestamp('project/schedule/project_end')
            }
        ]

        return HttpResponse(json.dumps({
            'dmp': dmp
        }, indent=2), content_type='application/json')

    def get_set(self, path):
        return self.values.filter(attribute__path=path)

    def get_values(self, path, set_index=0):
        return self.values.filter(attribute__path=path, set_index=set_index)

    def get_value(self, path, set_index=0, collection_index=0):
        try:
            return self.get_values(path, set_index)[collection_index]
        except IndexError:
            return None

    def get_text(self, path, set_index=0, collection_index=0):
        try:
            return self.get_values(path, set_index)[collection_index].text
        except IndexError:
            return ''

    def get_timestamp(self, path, set_index=0, collection_index=0):
        try:
            return self.get_values(path, set_index)[collection_index].value.isoformat()
        except IndexError:
            return ''
