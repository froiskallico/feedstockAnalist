# Aplicação para análise de Matérias Primas em Ordens de Produção
**Cliente:** Datateck Indústria e Comércio LTDA

**Data:** 11/02/2020
</br>
</br>

## Escopo:
Sistema que faça a análise de necessidades de matérias primas em uma ou mais ordens de produção indicadas pelo usuário, de modo a sinalizar eventuais rupturas no fluxo de abastecimento e indicar ações a serem tomadas.

- Os usuários poderão indicar uma ou mais ordens de produção;
- O sistema usará os parâmetros atuais já existentes do MRP do Sistema para seus cálculos;
- Análise de OPs *vs.* OCs pendentes **na linha do tempo**, devolvendo uma análise de:
  - **Qual(is) item(ns)** irá(ão) faltar;
  - **Quando** ocorrerá a falta;
  - **Para qual(is) OP(s) ocorrerá** a falta;
  - **Para qual(is) cliente(s)** ocorreá a falta;
  - **De quanto** será a falta;
  - **Ação sugerida** (Antecipar OC, Colocar OC);
  - Se a sugestão for antecipar => **Qual OC antecipar**;
  - Se a sugestão for comprar => **Quanto comprar**;
  - **Alerta** de Lead Time (*Se a necessidade for para um prazo menor que o Lead Time, indicando necessidade de ação emergencial*)
- As análises ficarão registradas em banco de dados, com os dados do momento em que foram feitas (Foto da análise).

  
## Características:
- Aplicação em Browser, acessível de qualquer local com internet;
- Login criptografado via email e senha;
- Interface com banco de dados do Delphus com consulta em tempo real.

## Investimento Líquido
- ### R$ 3.640,00 (Três mil seiscentos e quarenta reais) 
*Ficará a cargo da Datateck fornecer VPS com acesso remoto para testes, hospedagem do servidor e banco de dados da aplicação ou, se preferir, contratação de serviço de hospedagem cloud (AWS, GCP, Azuew, etc)*

## Forma de pagamento
- ### 50% no deploy completo da aplicação conforme escopo;
- ### 50% 30dd após deploy.

## Entrega
### 6 dias após aprovação da proposta
*Neste período poderão ocorrer entregas parciais, para validação e testes da aplicação.*

## Validade da Proposta
### 30 dias

<br>

 Atenciosamente,
**Kallico Fróis**
