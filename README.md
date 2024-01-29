---

# AUTOMATION-EC2-STOP-START

## Desligamento Automático de Instâncias EC2

![EC2-STOP-START](./img.png)

## Objetivo

Este guia tem como objetivo fornecer um método para automatizar o início e a parada de instâncias EC2 em várias contas da AWS. A automação será baseada em horários específicos e tags aplicadas às instâncias.

## Pré-Requisitos

- Acesso ao repositório do GitHub `CanabalFerradas/AUTOMATION-EC2-STOP-START`, onde os scripts necessários estão disponíveis.

## Passos para Configuração

### 1. Clonagem do Repositório GitHub

Execute o seguinte comando para clonar o repositório:

```sh
git clone https://github.com/CanabalFerradas/AUTOMATION-EC2-STOP-START.git
```

Acesse o diretório do repositório:

```sh
cd AUTOMATION-EC2-STOP-START
```
### Obs: é nesse diretório que definimos a variável file no script, é importante que você defina o caminho completo na variável.

### 2. Preparação do Ambiente

O script `criacao-stack.sh` será utilizado para configurar o ambiente. Este script prepara as dependências necessárias, criando um diretório temporário e instalando bibliotecas Python especificadas no arquivo `requirements.txt`. Após isso, um arquivo ZIP é criado com essas bibliotecas e, por fim, o diretório temporário é removido.

### 3. Deploy com AWS CloudFormation

### Variáveis Definidas no script **criacao-stack.sh**

1. **tmp**: Define um diretório temporário usado para operações intermediárias.
   - **Uso**: Utilizada para criar um diretório temporário (`mkdir layer; cd layer`), armazenar a layer do lambda (`mv ../$layer /tmp/`), e como diretório de trabalho ao enviar arquivos para o S3 (`cd $tmp`).

2. **bucket**: Armazena o nome do seu bucket S3.
   - **Uso**: Usada ao enviar a layer e o arquivo lambda para o S3 (`aws s3 cp $tmp/$layer s3://$bucket/`), e na publicação da layer do lambda (`--content S3Bucket=$bucket,S3Key=$layer`). Também faz parte do URL do template CloudFormation (`S3="https://$bucket.s3.amazonaws.com/$stack"`).

3. **layer**: Nome do arquivo zip da layer lambda.
   - **Uso**: Utilizada para criar o zip da layer (`zip -r9 ../$layer .`) e ao enviá-la para o S3 (`aws s3 cp $tmp/$layer s3://$bucket/`).

4. **lambda**: Nome do arquivo zip da função lambda.
   - **Uso**: Utilizada para mover o arquivo zip da lambda para o diretório temporário (`mv $lambda $tmp`) e ao enviá-lo para o S3 (`aws s3 cp $tmp/$lambda s3://$bucket/`).

5. **temporario**: Variável definida, mas não utilizada no script.

6. **stack**: Nome do arquivo do template CloudFormation.
   - **Uso**: Usada ao enviar o template para o S3 (`aws s3 cp $file/$stack s3://$bucket/`) e na URL do template ao criar a stack (`S3="https://$bucket.s3.amazonaws.com/$stack"`).

7. **S3**: URL do arquivo do template CloudFormation no bucket S3.
   - **Uso**: Utilizada no comando para criar a stack CloudFormation (`--template-url $S3`).

8. **AccountId**: ID da conta AWS que será utilizada, normalmente definimos a conta root principal, onde será executado o scritp, porém ajuste ao seu ambiente.
   - **Uso**: Usada como parâmetro ao criar a stack CloudFormation (`ParameterKey=AccountId,ParameterValue="$AccountId"`).

9. **file**: Caminho onde os arquivos lambda e stack estão localizados.
   - **Uso**: Utilizada para mudar para o diretório onde os arquivos lambda e stack estão localizados antes de criar o zip da lambda (`cd $file`) e ao enviar o arquivo da stack para o S3 (`aws s3 cp $file/$stack s3://$bucket/`). Aqui vale destacar que é o diretório onde você clonou o repo do git, coloque o caminho compelo nessa variável. 

 ### Explicação do restante do script

10. **Criação de Diretório Temporário e Estrutura de Diretórios**:
   - O script navega para o diretório `/tmp`, cria um diretório chamado `layer` e um arquivo `requirements.txt` com dependências Python especificadas.
   - Cria uma estrutura de diretórios dentro de `temp/python` e instala as dependências especificadas no `requirements.txt`.

11. **Criação e Envio da Layer**:
   - Após instalar as dependências, ele cria um arquivo zip (`$layer`) e o move para `/tmp`.
   - Em seguida, o script faz uma pausa (`sleep 1`) e depois envia o arquivo zip para o bucket S3 especificado.
   - Publica a camada no Lambda com `aws lambda publish-layer-version`, armazenando o ARN da camada na variável `arn`.

12. **Criação e Envio do Arquivo Lambda**:
   - Cria um arquivo zip (`lambda-stop-start.zip`) a partir dos arquivos da função Lambda especificada e o envia para o mesmo bucket S3.

13. **Cópia do Arquivo da Stack para o S3**:
   - Copia um arquivo YAML de stack (`stack-atualizado.yml`) para o bucket S3. Este arquivo é provavelmente um template do CloudFormation para definir recursos na AWS.

14. **Criação da Stack no CloudFormation**:
   - Utiliza o arquivo de stack copiado para criar uma stack no CloudFormation com `aws cloudformation create-stack`, passando o ARN da camada como um parâmetro.

15. **Mensagem Final**:
   - Exibe uma mensagem indicando o fim da execução do script.

### Função `check_command_status`

- Esta função verifica se o último comando executado foi bem-sucedido. É uma maneira de garantir que cada etapa do script seja bem-sucedida antes de prosseguir para a próxima.

### Importância das Variáveis

- **Organização**: As variáveis ajudam a organizar o script, tornando-o mais legível e fácil de manter.
- **Reutilização**: Permitem reutilizar valores em várias partes do script, evitando a necessidade de digitar o mesmo valor várias vezes.
- **Flexibilidade**: Facilitam a modificação do script para diferentes ambientes ou configurações, apenas alterando os valores das variáveis.

Resumindo, este script prepara e envia arquivos necessários para configurar um ambiente no AWS Lambda e no AWS CloudFormation, automatizando a criação de uma camada Lambda, o upload de um arquivo de função Lambda e a criação de uma stack no CloudFormation. É um exemplo de como scripts shell podem ser usados para automatizar tarefas complexas na AWS.


#### Deploy com CloudFormation Stackset

Utilize o template `role-stackset.yml` para criar as políticas e os papéis necessários em todas as contas da AWS.

### 5. Modificação do arquivo lambda-stop-start.py

Neste segmento do código da função Lambda `lambda_handler`, definimos uma lista chamada `target_accounts`. Essa lista deve conter os IDs das contas AWS alvo nas quais a função Lambda será executada. A função será configurada para interagir com múltiplas contas da AWS, permitindo a automação de tarefas em todas elas. 

```python
def lambda_handler(event, context):
    # Lista das contas alvo
    target_accounts = ['AccountID', 'AccountID']
```

Para um ambiente com várias contas AWS, é crucial utilizar o AWS CloudFormation StackSets. Esta ferramenta permite o deploy de recursos, como roles IAM necessárias, em várias contas AWS simultaneamente. Essa abordagem é ideal quando se opera a partir de uma conta master na AWS Organizations, que possui acesso administrativo a todas as contas membros da organização. 

Ao configurar a função Lambda, insira os IDs das contas alvo na lista `target_accounts`. Estes IDs correspondem às contas AWS nas quais você deseja que a Lambda execute as operações automatizadas. 

- **Para ambientes com várias contas**: Inclua na lista `target_accounts` os IDs de todas as contas que você deseja gerenciar com esta função Lambda. Isso permite que a função opere em um ambiente multi-conta, centralizando a gestão e automação das tarefas.
  
- **Para um único ambiente de conta**: Se a função Lambda for utilizada em apenas uma conta AWS, inclua somente o ID dessa conta na lista `target_accounts`. Isso simplifica o processo, pois a função irá operar apenas dentro do contexto desta única conta.

Em ambos os casos, a eficácia da função Lambda dependerá do correto provisionamento das permissões necessárias através de roles IAM e políticas. Certifique-se de que a função Lambda tenha as permissões adequadas para executar as tarefas desejadas em todas as contas listadas.

### 6. Criação de Regras do EventBridge

Configure regras no EventBridge para executar as funções Lambda de acordo com o cronograma desejado.

### 7. Verificação

Verifique se a função Lambda está operando conforme esperado, examinando os logs e o estado das instâncias EC2.

## Notas Importantes

Assegure-se de ter as permissões necessárias para realizar todos os passos, como clonar repositórios, executar scripts e criar stacks no CloudFormation. Adapte qualquer parte do script ou templates de acordo com as necessidades de sua organização.

## Conclusão

Seguindo este procedimento, você poderá gerenciar o início e a parada automáticos das instâncias EC2, otimizando os custos operacionais nas suas contas AWS.

---

