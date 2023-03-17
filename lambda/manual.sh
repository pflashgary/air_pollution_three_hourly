mkdir -p package && cd package
python3 -m venv myenv
source myenv/bin/activate
pip3 install --target . -r ../requirements.txt


cp ../main.py .
cp -r ../airpollution .

zip -r9 function.zip .
aws s3 cp function.zip s3://openaq-pegah/

#  We won't need 15 minutes
aws sqs set-queue-attributes --queue-url https://sqs.eu-west-1.amazonaws.com/<account>/openaq-pegah --attributes VisibilityTimeout=900

aws lambda create-function \
--function-name openaq-pegah \
--runtime python3.8 \
--handler main.handler \
--code S3Bucket=openaq-pegah,S3Key=function.zip \
--role arn:aws:iam::<account>:role/LambdaFunctionInterviewPolicyRole \
--timeout 900 \ # We won't need 15 minutes
--memory-size 128 \

# It didn't work with this;not sure if we need the lambda in the same vpc we can test
# --vpc-config SubnetIds=<IDs>,SecurityGroupIds=sg-<number>

aws lambda update-function-configuration \
  --function-name openaq-pegah \
  --environment Variables="{DB_MIN=1,DB_MAX=5,DB_HOST=<URL>,DB_PORT=5432,DB_USER=<user>,DB_PASS=<password>,DB_NAME=air_pollution}"


aws lambda create-event-source-mapping \
  --function-name openaq-pegah \
  --event-source-arn arn:aws:sqs:eu-west-1:<account>:openaq-pegah  \
  --batch-size 1 \
