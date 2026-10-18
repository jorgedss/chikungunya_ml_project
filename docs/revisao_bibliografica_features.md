# Revisão bibliográfica: preditores de gravidade e óbito em chikungunya

Este documento consolida 10 artigos sobre gravidade, hospitalização e óbito por chikungunya,
priorizando estudos que usaram o SINAN como fonte de dados.
O objetivo é mapear quais preditores a literatura já associou ao desfecho, para informar a
lista `FEATURES` do pipeline de dados (`utils/clean_data.py`), sem copiar features de outro
estudo sem verificação contra o dicionário de dados real do SINAN para chikungunya.

Busca realizada em 2026-10-18, via busca web geral (não é uma revisão sistemática formal).

## Achado geral da busca

Não foi encontrado nenhum estudo publicado que treine um modelo de machine learning para
prever óbito por chikungunya diretamente a partir do SINAN.
A literatura se divide em três grupos: estudos epidemiológicos de fatores de risco para
óbito (sem ML), estudos de ML para diferenciar chikungunya de outras arboviroses (sem
desfecho de óbito), e estudos de mortalidade em excesso (sem features individuais).
Isso sugere que este projeto ocupa uma lacuna real na literatura, e não uma replicação de um
modelo já existente.

## Tabela comparativa

| # | Estudo | Fonte de dados | Desenho | Desfecho modelado | Principais preditores associados |
|---|--------|-----------------|---------|--------------------|-----------------------------------|
| 1 | Oliveira et al., "Chikungunya Death Risk Factors in Brazil, in 2017", PLOS ONE, 2022 (PMC8989201) | Casos confirmados em laboratório, Fortaleza-CE (fonte de notificação consistente com SINAN) | Caso-controle pareado (1:2), 82 óbitos / 164 controles | Óbito por chikungunya | Doença renal crônica (OR 12,77), doença cardíaca crônica (OR 3,80), febre, dor abdominal, apatia, dispneia, glicemia alterada |
| 2 | Mendonça, Silva, Lacerda, "Factors associated with death from dengue and chikungunya virus infection...", Rev Soc Bras Med Trop, 2023 (PMC10238066) | Pernambuco, 2015-2018 | Coorte retrospectiva de casos notificados | Óbito por chikungunya e por dengue | Idade (OR 78,72 para ≥60 anos), cefaleia, náusea, dor nas costas; letalidade de 0,35% para chikungunya |
| 3 | Cerqueira-Silva et al., "Hospitalisation, mortality and years of life lost among chikungunya and dengue cases in Brazil", Lancet Regional Health Americas, 2025 | SINAN nacional, 2015-2024 | Coorte nacional, regressão logística (hospitalização) e Fine-Gray (óbito intra-hospitalar) | Hospitalização e óbito intra-hospitalar | Idade (<1 ou ≥70 anos), sexo masculino, diabetes, doença renal; anos de vida perdidos maiores em população negra |
| 4 | Cerqueira-Silva et al., "Risk of death following chikungunya virus disease in the 100 Million Brazilian Cohort, 2015-18", Lancet Infectious Diseases, 2024 | Coorte linkada CIDACS (inclui notificações do SINAN e óbitos do SIM), 2015-2018 | Coorte pareada e self-controlled case series | Óbito em qualquer causa após infecção | Doença cardíaca isquêmica, doença metabólica, doença renal; risco de óbito 8x maior na primeira semana, 2x maior até 3 meses |
| 5 | Pedí, Porto, Martins, de França, "Epidemiology of Chikungunya Hospitalizations, Brazil, 2014-2024", Emerging Infectious Diseases, 2025 | Registros de internação do SUS (SIH), não o SINAN de notificação | Descritivo, 7.421 internações | Letalidade intra-hospitalar | Idade >90 anos (letalidade 11,5%), admissão em UTI (letalidade 21,1%); usado aqui apenas como referência de magnitude, não de features, por usar fonte de dados diferente do SINAN |
| 6 | Freitas, Cavalcanti, Von Zuben, Donalisio, "Excess Mortality Related to Chikungunya Epidemics...", PLOS Currents Outbreaks, 2017 | Comparação de óbitos notificados (SINAN) vs. mortalidade geral em excesso, Pernambuco, 2015-2016 | Série temporal observacional | Mortalidade em excesso durante epidemia | Idosos e crianças <1 ano mais afetados; reforça subnotificação de óbitos só pelo SINAN |
| 7 | "Arthralgia and fever as dominant predictors of Chikungunya confirmation: an explainable artificial intelligence approach", 2026 (PMID 42051709) | SINAN, 12.709 registros de notificação, 2013-2020 | Classificação ML (XGBoost, LightGBM) com SHAP | Confirmação do caso (não óbito) | Artralgia e febre como preditores dominantes da confirmação diagnóstica |
| 8 | "Machine Learning for Differentiating Dengue from Chikungunya in Northern Brazil" (preprint, Research Square, ainda não revisado por pares) | SINAN, casos confirmados por PCR, 2021-2023, adultos 18-59 anos | Classificação ML, Random Forest como melhor modelo | Diferenciação dengue vs. chikungunya (não óbito) | Não detalhado nos resultados de busca; citado pela fonte de dados (SINAN) e pelo desenho, não pelas features específicas |
| 9 | Estudo brasileiro de gradient boosting para classificação Dengue/Chikungunya/Outras, Frontiers in Tropical Diseases, 2021 | Dados clínicos e sociodemográficos de vigilância brasileira (fonte provável SINAN, a confirmar no texto completo) | Classificação ML, gradient boosting | Diferenciação entre arboviroses (não óbito) | Dados clínicos e sociodemográficos; recall de 76,58% para a classe chikungunya |
| 10 | Sippy et al., "Severity Index for Suspected Arbovirus (SISA)", PLoS Neglected Tropical Diseases, 2020 (PMC7046343) | Vigilância sentinela em Machala, Equador (não é SINAN; incluído por relevância metodológica) | Comparação de 7 algoritmos de ML | Hospitalização por arbovirose suspeita | Dados demográficos e de sintomas de admissão; melhor modelo (gradient boosting) com AUC 0,91 |

## Famílias de preditores identificadas

- **Demografia:** idade (risco cresce a partir dos 40-50 anos e é maior em crianças <1 ano e
  idosos ≥60-70 anos), sexo (masculino associado a maior risco em mais de um estudo), raça/cor
  (anos de vida perdidos maiores em população negra).
- **Comorbidades crônicas:** diabetes mellitus, doença renal crônica, doença cardíaca
  crônica/isquêmica, hipertensão.
- **Sinais e sintomas na notificação:** febre, artralgia/artrite, cefaleia, dor abdominal,
  apatia/letargia, dispneia, náusea, dor nas costas.
- **Tempo:** período desde o início dos sintomas (risco de óbito concentrado na primeira
  semana, mas elevado até cerca de 3 meses).
- **Contexto geográfico e temporal:** unidade federativa e ano, por variação regional e entre
  ondas epidemiológicas.

## Implicação para `utils/clean_data.py`

A lista `FEATURES` da Fase 3 deve, no mínimo, cobrir estas famílias de preditores, verificando
no dicionário de dados do SINAN para chikungunya (`pysus`, disease code `"CHIK"`) quais campos
da ficha de notificação correspondem a cada uma.
Nenhum campo deve ser assumido apenas por existir numa ficha de outro agravo: a confirmação do
dicionário de dados real acontece como primeiro passo da Fase 3, antes de fixar a lista.
