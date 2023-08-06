from datapackage_pipelines.generators import slugify
from .utils import extract_names, extract_storage_ids

def normalized_flow(source):

    _, _, resource_name = extract_names(source)
    dataset_id, db_table, _ = extract_storage_ids(source)

    kinds = sorted(set(
        f['osType'].split(':')[0]
        for f in source['fields']
    ) - {'value'})

    resources = [
        slugify(kind, separator='_')
        for kind in kinds
    ]
    db_tables = dict(
        (res, '{}_{}'.format(db_table, i))
        for i, res in enumerate(resources)       
    )
    db_tables[''] = db_table

    deps = [
        './dimension_flow_{}'.format(res)
        for res in resources
        ]

    steps = [
        ('load_metadata', {
            'url': 'dependency://./denormalized_flow',
        }),
    ]
    steps.extend([
        ('load_resource', {
            'url': 'dependency://' + dep,
            'resource': resource
        })
        for resource, dep in zip(resources, deps)
    ])
    steps.extend([
        ('load_resource', {
            'url': 'dependency://./denormalized_flow',
            'resource': resource_name
        }),
        ('fiscal.create_babbage_model', {
            'db-tables': db_tables
        }),
    ])
    for resource, kind in zip(resources, kinds):
        headers = [
            f['header']
            for f in source['fields']
            if f['osType'].startswith(kind+':') or f['osType'] == kind
        ]
        steps.extend([
            ('join', {
                'source': {
                    'name': resource,
                    'key': headers,
                    'delete': True
                },
                'target': {
                    'name': resource_name,
                    'key': headers
                },
                'fields': {
                    resource + '_id': {
                        'name': 'id'
                    }
                }
            }),
            ('delete_fields', {
                'resources': resource_name,
                'fields': headers
            }),
        ])
    steps.extend([
        ('add_metadata', {
            'savedPk': [resource + '_id' for resource in resources]
        }),
        ('fiscal.helpers.load_primarykey', {}, True),
        ('fiscal.update_model_in_registry', {
            'dataset-id': dataset_id,
            'loaded': False
        }),
        ('dump.to_path', {
            'out-path': 'normalized/final'
        })
    ])
    yield steps, deps + ['./denormalized_flow'], ''
