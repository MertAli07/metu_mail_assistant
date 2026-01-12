import boto3
from botocore.config import Config
import json
import pandas as pd
from tqdm import tqdm

config = Config(read_timeout=600)
client = boto3.client(service_name='bedrock-agent-runtime', config=config)

results = []

df = pd.read_csv('METU TEST DATA TRAIN.csv', usecols=['BASE QUESTION'], encoding='utf-8')

for question in tqdm(df['BASE QUESTION']):
    response = client.invoke_flow(
        flowIdentifier='GSKXHK5TOZ',
        flowAliasIdentifier='LO4CCL57VR',
        inputs=[
            {
                'content': {'document': question},
                'nodeName': 'FlowInputNode',
                'nodeOutputName': 'document'
            }
        ]
    )
    
    # Process streaming response
    result = ""
    for event in response['responseStream']:
        if 'flowOutputEvent' in event:
            result += event['flowOutputEvent']['content']['document']
    
    results.append({
        'question': question,
        'response': result
    })

# Save to file
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)