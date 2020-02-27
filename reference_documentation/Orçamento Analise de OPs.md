# Aplicação para análise de Matérias Primas em Ordens de Produção
**Cliente:** Datateck Indústria e Comércio LTDA

**Data:** 14/02/2020
</br>
</br>

## Escopo:
Sistema que faça a análise de necessidades de matérias primas em uma ou mais ordens de produção indicadas pelo usuário, de modo a sinalizar eventuais rupturas no fluxo de abastecimento e indicar ações a serem tomadas.

- [x] Os usuários poderão indicar uma ou mais ordens de produção;
- [ ] Análise de OPs *vs.* OCs pendentes **na linha do tempo**, devolvendo uma análise de:
  - [x] **Qual(is) item(ns)** irá(ão) faltar;
  - [x] **Quando** ocorrerá a falta;
  - [x] **Para qual(is) OP(s) ocorrerá** a falta;
  - [x] **Para qual(is) cliente(s)** ocorreá a falta;
  - [x] **De quanto** será a falta;
  - [ ] **Ação sugerida** (Antecipar OC, Colocar OC):
    - [ ] Se a sugestão for antecipar => **Qual OC antecipar**;
    - [ ] Se a sugestão for comprar => **Quanto comprar (*buscando respeitar o estoque máximo MRP*)**:
      - [ ] O sistema usará os parâmetros atuais já existentes do MRP para cálculo do estoque máximo;
      - [ ] Alertar o usuário se a sugestão ultrapassar o estoque máximo.
  - [ ] **Alerta** de Lead Time (*Se a necessidade for para um prazo menor que o Lead Time, indicando necessidade de ação emergencial*).
- [ ] Calcular o valor financeiro das compras sugeridas, por item e total da análise;
- [ ] As análises ficarão registradas em banco de dados, com os dados do momento em que foram feitas (Foto da análise);
- [ ] Exportação da análise para excel;
- [ ] Exportação das sugestões de compras para posterior importação no Delphus;
- [ ] No sistema existirá a opção de rodar a mesma análise para os itens do Radar de Compras.


## Características:
- Aplicação em Browser, acessível de qualquer local com internet;
- Interface com banco de dados do Delphus com consulta em tempo real.

## Investimento Líquido
- ### R$ 3.000,00 (Três mil reais)
*Ficará a cargo da Datateck fornecer VPS com acesso remoto para testes, hospedagem do servidor e banco de dados da aplicação ou, se preferir, contratação de serviço de hospedagem cloud (AWS, GCP, Azuew, etc)*

## Forma de pagamento
- ### 34% no deploy completo da aplicação conforme escopo;
- ### 33% 28dd após deploy;
- ### 33% 56dd após deploy.


## Entrega
### Entrega total até 26/02/2020

*Neste período ocorrerão entregas parciais, para validação e testes da aplicação.*

## Validade da Proposta
### 30 dias

<br>

 Atenciosamente,
**Kallico Fróis**
