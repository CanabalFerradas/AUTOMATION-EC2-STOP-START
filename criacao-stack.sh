#!/bin/zsh

# Definindo variáveis
tmp="/tmp"
bucket="COLOQUE-AQUI-SEU-BUCKET"
layer="layer.zip"
lambda="lambda-stop-start.zip"
temporario="temp"
stack="stack-atualizado.yml"
S3="https://$bucket.s3.amazonaws.com/$stack"
AccountId="Coloquei sua conta root aqui ou sua conta que vai receber automação"
file="Aqui coloque o caminho onde os arquivos lambda, stack, estaram."

check_command_status() {
if [ $? -eq 0 ]; then
  echo "rodou com sucesso. "
else
  echo "Erro ao criar o StackSet."
  exit 1
fi
}

# Cria o diretório temporário e a estrutura de diretórios
cd /tmp; mkdir layer; cd layer
touch requirements.txt
echo "requests==2.28.1\npytz" > requirements.txt
mkdir -p temp/python && cd temp/python
pip3 install -r ../../requirements.txt -t .
cd ..
zip -r9 ../$layer .
mv ../$layer /tmp/
rm -r /tmp/layer/

check_command_status


# Espera 1 segundo para preparar a layer
sleep 1

# Envia a layer para o S3
cd $tmp
aws s3 cp $tmp/$layer s3://$bucket/
check_command_status

# Cria a layer no Lambda
arn=$(aws lambda publish-layer-version \
  --layer-name stop-start \
  --description "Layer stop/start" \
  --content S3Bucket=$bucket,S3Key=$layer \
  --compatible-runtimes python3.8 \
  --output json | jq -r '.LayerVersionArn')
  
check_command_status

# Cria o arquivo zip da lambda
cd $file
zip -r lambda-stop-start.zip lambda-stop-start.py  
mv $lambda $tmp
check_command_status

# Copia o arquivo para o S3
aws s3 cp $tmp/$lambda s3://$bucket/
check_command_status


# Copia o arquivo da stack para s3
aws s3 cp $file/$stack s3://$bucket/
check_command_status

# Cria a stack no CloudFormation
aws cloudformation create-stack \
  --stack-name start-stop \
  --template-url $S3 \
  --parameters \
      ParameterKey=LayerArn,ParameterValue="$arn" \
      ParameterKey=AccountId,ParameterValue="$AccountId" \
  --capabilities CAPABILITY_NAMED_IAM


check_command_status  

# Mensagem final
echo "Agora seja feliz e marcha."
