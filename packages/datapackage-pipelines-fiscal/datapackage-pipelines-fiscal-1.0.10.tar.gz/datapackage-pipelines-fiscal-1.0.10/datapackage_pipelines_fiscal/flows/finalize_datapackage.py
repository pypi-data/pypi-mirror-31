import os
import logging

from .utils import extract_names, extract_storage_ids

BUCKET = os.environ.get('S3_BUCKET_NAME')
logging.info('DUMPING results to BUCKET %s', BUCKET)


def finalize_datapackage_flow(source):

    _, _, resource_name = extract_names(source)
    dataset_id, _, dataset_path = extract_storage_ids(source)

    pipeline_steps = [
                         (
                             'load_metadata',
                             {
                                 'url': 'dependency://./denormalized_flow',
                             }
                         ),
                         (
                             'load_resource',
                             {
                                 'url': 'dependency://./denormalized_flow',
                                 'resource': resource_name
                             }
                         ),
                         (
                             'fiscal.split_per_fiscal_year'
                         ),
                         (
                             'dump.to_path',
                             {
                                 'out-path': 'final'
                             }
                         )
                     ]

    yield pipeline_steps, ['./denormalized_flow'], 'splitter'

    pipeline_steps = [
                        (
                            'load_metadata',
                            {
                                'url': 'dependency://./finalize_datapackage_flow_splitter',
                            }
                        ),
                        (
                            'load_resource',
                            {
                                'url': 'dependency://./finalize_datapackage_flow_splitter',
                                'resource': '.+'
                            }
                        )
                    ]

    if BUCKET is not None:
        pipeline_steps.extend([
            (
                'aws.dump.to_s3',
                {
                    'bucket': BUCKET,
                    'path': '{}/final'.format(dataset_path),
                    'pretty-descriptor': True
                }
            ),
        ])
    else:
        pipeline_steps.extend([
            (
                'dump.to_zip',
                {
                    'out-file': '{}_final.zip'.format(dataset_id),
                    'pretty-descriptor': True
                }
            ),
        ])

    pipeline_steps.extend([
            ('fiscal.update_model_in_registry', {
                'dataset-id': dataset_id,
                'datapackage-url': 'https://{}/{}/final/datapackage.json'.format(BUCKET, dataset_path)
            }),
        ])

    yield pipeline_steps, ['./finalize_datapackage_flow_splitter'], ''
