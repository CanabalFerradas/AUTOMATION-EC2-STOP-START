import boto3
from datetime import datetime
from pytz import timezone

def lambda_handler(event, context):
    # Lista das contas alvo
    target_accounts = ['AccountID', 'AccountID']

    for target_account in target_accounts:
        # Assume o papel na conta de destino
        role_to_assume_arn = f"arn:aws:iam::{target_account}:role/roleStartStop"
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(RoleArn=role_to_assume_arn, RoleSessionName="AssumeRoleSession")

        # Cria uma nova sessão usando as credenciais temporárias do papel assumido
        assumed_session = boto3.Session(
            aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role['Credentials']['SessionToken']
        )

        # Use a sessão assumida para interagir com recursos na conta de destino
        ec2 = assumed_session.resource('ec2')

        # Procura por instâncias com a Tag ec2-stop-start:true, com status running ou stopped
        filters = [
            {
                'Name': 'tag:ec2-stop-start',
                'Values': ['true']
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running', 'stopped']
            }
        ]

        # Busca as instâncias
        instances = ec2.instances.filter(Filters=filters)

        if len([instance for instance in instances]) > 0:
            print(f"Conta {target_account} possui " + str(len([instance for instance in instances])) + " instâncias para serem gerenciadas!")

            # Ajustando o timezone
            y = datetime.now(timezone('America/Sao_Paulo'))
            y = y.strftime("%H:%M")

            print(" ")
            print("##### Iniciando #####")
            print(" ")
            print(f"Horário: {y}")

            # Funções para o STOP e START das instâncias
            def stop_instance(instance):
                return ec2.Instance(instance.id).stop()

            def start_instance(instance):
                return ec2.Instance(instance.id).start()

            # Realizando o stop ou start, dependendo do horário da chamada da lambda
            if y >= "07:00" and y <= "20:00":                
                print("Entre 07AM e 19:59PM")
                for instance in instances:
                    tags = instance.tags
                    if any(tag['Key'] == 'shutdown' and tag['Value'] == 'never' for tag in tags):
                        print(f"Skipping instance {instance.id} devido a tag shutdown: never")
                        continue
                    start_instance(instance)
                    print(f"Starting instance {instance.id}")
            elif y >= "06:59" and y > "20:00":                
                print("Entre 20PM e 06AM")
                for instance in instances:
                    tags = instance.tags
                    if any(tag['Key'] == 'shutdown' and tag['Value'] == 'never' for tag in tags):
                        print(f"Skipping instance {instance.id} devido a tag shutdown: never")
                        continue
                    stop_instance(instance)
                    print(f"Stopping instance {instance.id}")
        else:
            print(f"Conta {target_account} Não Possui Instâncias com a TAG obrigatória ou com STATUS (running ou stopped)")

    return "Assumed and performed actions in another account(s)"
