import boto3

# By default, HITs are created in the free-to-use Sandbox
create_hits_in_live = False

environments = {
    "live": {
        "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
        "preview": "https://www.mturk.com/mturk/preview",
        "manage": "https://requester.mturk.com/mturk/manageHITs",
        "reward": "0.00"
    },
    "sandbox": {
        "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
        "preview": "https://workersandbox.mturk.com/mturk/preview",
        "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
        "reward": "0.11"
    },
}
mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]

# add access key id & secret access key for the use (tengo le chiavi nel file chiavi.txt nel desktop)
region_name = 'us-east-1'
aws_access_key_id = 'AKIAR6AXQDP6N6PUYYGU'
aws_secret_access_key = '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'

endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Test that you can connect to the API by checking your account balance
user_balance = client.get_account_balance()
# In Sandbox this always returns $10,000. In live, it will be your acutal balance.
print "Your account balance is {}".format(user_balance['AvailableBalance'])

# The question we ask the workers is contained in this file, please execute in background first the module app.py
question_sample = open("question.xml", "r").read()

# Example of using qualification to restrict responses to Workers who have had
# at least 80% of their assignments approved. See:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html#ApiReference_QualificationType-IDs
worker_requirements = [{
    'QualificationTypeId': '000000000000000000L0',
    'Comparator': 'GreaterThanOrEqualTo',
    'IntegerValues': [80],
    'RequiredToPreview': True,
}]

# Create the HIT
response = client.create_hit(
    MaxAssignments=10,
    LifetimeInSeconds=600,
    AssignmentDurationInSeconds=600,
    Reward=mturk_environment['reward'],
    Title='Evaluate the quality of the images',
    Keywords='question, answer, research, quality, images, AI',
    Description='Give a vote (from 0 to 100) about the quality of the images',
    Question=question_sample,
    QualificationRequirements=worker_requirements,
)

# The response included several fields that will be helpful later
hit_type_id = response['HIT']['HITTypeId']
hit_id = response['HIT']['HITId']
print "\nCreated HIT: {}".format(hit_id)

print "\nYou can work the HIT here:"
print mturk_environment['preview'] + "?groupId={}".format(hit_type_id)

print "\nAnd see results here:"
print mturk_environment['manage']
