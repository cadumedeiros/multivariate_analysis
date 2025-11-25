# Relatório de Análise de Calibração

Relatório gerado em: 2025-11-25 14:15:09

Arquivo de entrada: `Uncertain_parameters_and_OF_values.xlsx`

## Resumo das Configurações da Análise

* **Percentil para Melhores Modelos:** 50%
* **Variância Mantida pelo PCA:** 95%
* **Número de Componentes Principais:** 6
* **Número de Clusters (k):** 4

## Seleção dos Melhores Modelos

Total de simulações: 385
Número de modelos selecionados (melhores 50%): 193

![Gráfico de Dispersão OF](grafico_dispersao_OF.png)
*Gráfico 1: Dispersão dos valores da Função Objetivo (OF). Pontos laranjas indicam os modelos selecionados.*

## Determinação do Número de Clusters (k)

Foram analisados valores de k no intervalo: [2, 3, 4, 5, 6, 7, 8, 9, 10]

![Método do Cotovelo](grafico_metodo_cotovelo.png)
*Gráfico 2: Método do Cotovelo (Inércia vs. k). O 'cotovelo' sugere um k ótimo.*

![Pontuação de Silhueta](grafico_pontuacao_silhueta.png)
*Gráfico 3: Pontuação Média de Silhueta vs. k. Valores mais altos indicam melhor separação dos clusters.*

**Número de clusters escolhido (k): 4**

## Visualização e Análise dos Clusters

![Clusters PCA](grafico_clusters_pca.png)
*Gráfico 4: Visualização dos 4 clusters no espaço dos dois primeiros Componentes Principais (Total Var. Explicada: 53.5%).*

### Tamanho dos Clusters

|   Cluster |   Número de Modelos |
|----------:|--------------------:|
|         0 |                  52 |
|         1 |                 138 |
|         2 |                   1 |
|         3 |                   2 |

### Centróides dos Clusters (Valores Médios dos Parâmetros Originais)

|   Cluster |   Carbo_GrainsProdvsTime |   Carbo_MudProdvsTime |   Carbo_RudProdvsTime |   LutitesProdvsTime |   S1Supply0 |   S2Supply0 |   Eustasy0 |
|----------:|-------------------------:|----------------------:|----------------------:|--------------------:|------------:|------------:|-----------:|
|         0 |                   0.5000 |                0.5000 |                0.5000 |              0.5129 |      0.8346 |      0.7542 |     0.7072 |
|         1 |                   0.5000 |                0.5001 |                0.5001 |              0.5001 |      0.6218 |      0.9640 |     0.5387 |
|         2 |                   0.5550 |                0.6524 |                0.5001 |              0.5000 |      0.6847 |      0.9083 |     0.5229 |
|         3 |                   0.5065 |                0.5484 |                0.5545 |              0.5000 |      0.6837 |      0.9094 |     0.5000 |
*Tabela 1: Valores médios dos multiplicadores para cada cluster.*

### Estatísticas da Função Objetivo ('OF Value') por Cluster

|   Cluster |    count |    mean |      std |     min |     25% |     50% |     75% |     max |
|----------:|---------:|--------:|---------:|--------:|--------:|--------:|--------:|--------:|
|         0 |  52.0000 | 20.8217 |   0.3267 | 20.0257 | 20.5782 | 20.8793 | 21.0718 | 21.3186 |
|         1 | 138.0000 | 20.3024 |   0.3332 | 19.7937 | 20.0504 | 20.2684 | 20.4566 | 21.3127 |
|         2 |   1.0000 | 20.9333 | nan      | 20.9333 | 20.9333 | 20.9333 | 20.9333 | 20.9333 |
|         3 |   2.0000 | 20.4708 |   0.1476 | 20.3664 | 20.4186 | 20.4708 | 20.5230 | 20.5752 |
*Tabela 2: Estatísticas descritivas do 'OF Value' para os modelos dentro de cada cluster.*

### Distribuição dos Parâmetros por Cluster

![Boxplots Parâmetros](grafico_boxplots_parametros.png)
*Gráfico 5: Boxplots mostrando a distribuição dos valores de cada parâmetro (multiplicador) dentro de cada cluster.*

## Validação dos Clusters e Análises Avançadas

### Métricas de Validação dos Clusters

#### Kmeans

| Métrica | Valor |
|:--|--:|
| Silhouette | 0.418 |
| Calinski-Harabasz | 87.432 |
| Davies-Bouldin | 0.838 |

#### Hierarchical

| Métrica | Valor |
|:--|--:|
| Silhouette | 0.418 |
| Calinski-Harabasz | 81.013 |
| Davies-Bouldin | 0.868 |

### Clusterização Hierárquica (Método de Ward)

![Dendrograma](grafico_dendrograma.png)
*Gráfico 6: Dendrograma mostrando a hierarquia entre os clusters. Alturas menores indicam grupos mais semelhantes.*

### Análise Discriminante Linear (LDA)

A análise discriminante linear identifica os parâmetros com maior poder de separação entre os clusters formados. Coeficientes positivos e negativos indicam a direção da influência de cada parâmetro.

|                        |   Coeficiente |
|:-----------------------|--------------:|
| Carbo_MudProdvsTime    |     4070.7993 |
| S2Supply0              |       14.2150 |
| S1Supply0              |        0.4496 |
| LutitesProdvsTime      |       -0.2984 |
| Eustasy0               |       -4.8528 |
| Carbo_RudProdvsTime    |     -952.4253 |
| Carbo_GrainsProdvsTime |    -1327.0609 |
*Tabela 4: Coeficientes discriminantes médios por parâmetro.*

![Coeficientes LDA](grafico_coeficientes_LDA.png)
*Gráfico 7: Importância relativa dos parâmetros na separação dos clusters segundo a LDA.*

### Teste Estatístico de Diferenças entre Clusters (ANOVA)

A ANOVA testa se as médias do valor da Função Objetivo (ou outras variáveis) diferem significativamente entre os clusters.

|            |   sum_sq |       df |        F |   PR(>F) |
|:-----------|---------:|---------:|---------:|---------:|
| C(Cluster) |  10.4220 |   3.0000 |  31.7657 |   0.0000 |
| Residual   |  20.6696 | 189.0000 | nan      | nan      |
*Tabela 5: Resultado da ANOVA aplicada sobre a variável 'OF Value'. p-values inferiores a 0.05 indicam diferença estatisticamente significativa.*

## Seleção dos Modelos Representativos ('Campeões' por Cluster)

A tabela abaixo mostra a simulação com o menor 'OF Value' dentro de cada um dos clusters identificados.

| Simulation_ID   |   Carbo_GrainsProdvsTime |   Carbo_MudProdvsTime |   Carbo_RudProdvsTime |   LutitesProdvsTime |   S1Supply0 |   S2Supply0 |   Eustasy0 |   OF Value |   Simulation |   Cluster |   Cluster_H |
|:----------------|-------------------------:|----------------------:|----------------------:|--------------------:|------------:|------------:|-----------:|-----------:|-------------:|----------:|------------:|
| Sim261          |                   0.5000 |                0.5000 |                0.5000 |              0.5000 |      0.7887 |      0.8509 |     0.6471 |    20.0257 |     261.0000 |    0.0000 |      2.0000 |
| Sim349          |                   0.5000 |                0.5000 |                0.5000 |              0.5000 |      0.6676 |      0.8983 |     0.5000 |    19.7937 |     349.0000 |    1.0000 |      1.0000 |
| Sim163          |                   0.5548 |                0.6530 |                0.5000 |              0.5000 |      0.6847 |      0.9083 |     0.5229 |    20.9333 |     163.0000 |    2.0000 |      4.0000 |
| Sim302          |                   0.5000 |                0.5373 |                0.5430 |              0.5000 |      0.6788 |      1.0508 |     0.5000 |    20.3664 |     302.0000 |    3.0000 |      3.0000 |
*Tabela 3: Melhores simulações representativas de cada cluster.*

