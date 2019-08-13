import boto3

client = boto3.client('mturk')

response = client.create_hit(
    MaxAssignments=123,
    AutoApprovalDelayInSeconds=123,
    LifetimeInSeconds=123,
    AssignmentDurationInSeconds=123,
    Reward='string',
    Title='string',
    Keywords='string',
    Description='string',
    Question='string',
    RequesterAnnotation='string',
    QualificationRequirements=[
        {
            'QualificationTypeId': 'string',
            'Comparator': 'LessThan' | 'LessThanOrEqualTo' | 'GreaterThan' | 'GreaterThanOrEqualTo' | 'EqualTo' | 'NotEqualTo' | 'Exists' | 'DoesNotExist' | 'In' | 'NotIn',
            'IntegerValues': [
                123,
            ],
            'LocaleValues': [
                {
                    'Country': 'string',
                    'Subdivision': 'string'
                },
            ],
            'RequiredToPreview': True | False,
            'ActionsGuarded': 'Accept' | 'PreviewAndAccept' | 'DiscoverPreviewAndAccept'
        },
    ],
    UniqueRequestToken='string',
    AssignmentReviewPolicy={
        'PolicyName': 'string',
        'Parameters': [
            {
                'Key': 'string',
                'Values': [
                    'string',
                ],
                'MapEntries': [
                    {
                        'Key': 'string',
                        'Values': [
                            'string',
                        ]
                    },
                ]
            },
        ]
    },
    HITReviewPolicy={
        'PolicyName': 'string',
        'Parameters': [
            {
                'Key': 'string',
                'Values': [
                    'string',
                ],
                'MapEntries': [
                    {
                        'Key': 'string',
                        'Values': [
                            'string',
                        ]
                    },
                ]
            },
        ]
    },
    HITLayoutId='string',
    HITLayoutParameters=[
        {
            'Name': 'string',
            'Value': 'string'
        },
    ]
)

# TODO...