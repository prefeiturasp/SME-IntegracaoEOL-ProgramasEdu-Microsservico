# SME-IntegracaoEOL ProgramasEdu

O microsserviço `SME-IntegracaoEOL-ProgramasEdu-Microsservico` é uma aplicação Django/DRF que expõe os contratos do domínio **Programas Educacionais (PAP/PAEE)** da SME-SP.

O serviço opera em modo *read-only* sobre o banco `programas_db` (todos os models declaram `Meta.managed = False`) e responde aos contratos definidos pela SME, preservando caminhos, parâmetros, códigos de status e cabeçalhos (autenticação por `X-API-Key`).

## Escopo e Arquitetura

Este microsserviço é uma unidade autônoma de leitura: recebe requisições HTTP, consulta o banco relacional e devolve a resposta no formato esperado pelos consumidores. Não executa rotinas de ingestão, transformação ou orquestração — sua única responsabilidade é servir os contratos de Programas Educacionais a partir do estado atual do banco.

A documentação é gerada automaticamente pelo Sphinx a partir das docstrings do código e está estruturada da seguinte forma:

```{toctree}
:maxdepth: 2
:caption: Referência de código

api
```
