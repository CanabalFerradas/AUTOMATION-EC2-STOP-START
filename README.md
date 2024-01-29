---

# AUTOMATION-EC2-STOP-START

## Desligamento Automático de Instâncias EC2

![EC2-STOP-START](./img.png)

## Objetivo

Este guia tem como objetivo fornecer um método para automatizar o início e a parada de instâncias EC2 em várias contas da AWS. A automação será baseada em horários específicos e tags aplicadas às instâncias.

## Pré-Requisitos

- Acesso ao repositório do GitHub `CanabalFerradas/EC2-STOP-START`, onde os scripts necessários estão disponíveis.

## Passos para Configuração

### 1. Clonagem do Repositório GitHub

Execute o seguinte comando para clonar o repositório:

```sh
git clone https://github.com/CanabalFerradas/EC2-STOP-START.git
```

Acesse o diretório do repositório:

```sh
cd EC2-STOP-START
```

### 2. Preparação do Ambiente

O script `script.sh` será utilizado para configurar o ambiente. Este script prepara as dependências necessárias, criando um diretório temporário e instalando bibliotecas Python especificadas no arquivo `requirements.txt`. Após isso, um arquivo ZIP é criado com essas bibliotecas e, por fim, o diretório temporário é removido.

### 3. Deploy com AWS CloudFormation

1. **Definição de Variáveis**:
   - Variáveis como `tmp`, `bucket`, `layer`, `lambda`, `temporario`, `stack`, `S3` são definidas para serem utilizadas ao longo do script. Elas armazenam caminhos e nomes de arquivos relevantes para as operações subsequentes.

2. **Função `check_command_status`**:
   - Esta função verifica o status do último comando executado (`$?` retorna o status do último comando). Se o comando foi bem-sucedido (`-eq 0`), imprime uma mensagem de sucesso, caso contrário, imprime uma mensagem de erro e encerra o script (`exit 1`).

3. **Criação de Diretório Temporário e Estrutura de Diretórios**:
   - O script navega para o diretório `/tmp`, cria um diretório chamado `layer` e um arquivo `requirements.txt` com dependências Python especificadas.
   - Cria uma estrutura de diretórios dentro de `temp/python` e instala as dependências especificadas no `requirements.txt`.

4. **Criação e Envio da Layer**:
   - Após instalar as dependências, ele cria um arquivo zip (`$layer`) e o move para `/tmp`.
   - Em seguida, o script faz uma pausa (`sleep 1`) e depois envia o arquivo zip para o bucket S3 especificado.
   - Publica a camada no Lambda com `aws lambda publish-layer-version`, armazenando o ARN da camada na variável `arn`.

5. **Criação e Envio do Arquivo Lambda**:
   - Cria um arquivo zip (`lambda-stop-start.zip`) a partir dos arquivos da função Lambda especificada e o envia para o mesmo bucket S3.

6. **Cópia do Arquivo da Stack para o S3**:
   - Copia um arquivo YAML de stack (`stack-atualizado.yml`) para o bucket S3. Este arquivo é provavelmente um template do CloudFormation para definir recursos na AWS.

7. **Criação da Stack no CloudFormation**:
   - Utiliza o arquivo de stack copiado para criar uma stack no CloudFormation com `aws cloudformation create-stack`, passando o ARN da camada como um parâmetro.

8. **Mensagem Final**:
   - Exibe uma mensagem indicando o fim da execução do script.

Resumindo, este script prepara e envia arquivos necessários para configurar um ambiente no AWS Lambda e no AWS CloudFormation, automatizando a criação de uma camada Lambda, o upload de um arquivo de função Lambda e a criação de uma stack no CloudFormation. É um exemplo de como scripts shell podem ser usados para automatizar tarefas complexas na AWS.

#### Deploy com CloudFormation Stackset

Utilize o template `stackset.yml` para criar as políticas e os papéis necessários em todas as contas da AWS.

### 4. Criação de Regras do EventBridge

Configure regras no EventBridge para executar as funções Lambda de acordo com o cronograma desejado.

### 5. Verificação

Verifique se a função Lambda está operando conforme esperado, examinando os logs e o estado das instâncias EC2.

## Notas Importantes

Assegure-se de ter as permissões necessárias para realizar todos os passos, como clonar repositórios, executar scripts e criar stacks no CloudFormation. Adapte qualquer parte do script ou templates de acordo com as necessidades de sua organização.

## Conclusão

Seguindo este procedimento, você poderá gerenciar o início e a parada automáticos das instâncias EC2, otimizando os custos operacionais nas suas contas AWS.

---

