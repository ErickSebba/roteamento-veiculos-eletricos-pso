# Roteamento de veículos elétricos com PSO (EVRP)

Otimização por enxame de partículas (PSO) para o problema de roteamento de veículos elétricos: encontrar uma rota que passe pelas cidades respeitando a autonomia da bateria, com paradas em postos de recarga. Trabalho final da disciplina de Projeto e Análise de Algoritmos (UFMT, 2025).

## Estrutura
- `evrp_pso.py`: versão final. Gera cidades e postos, monta o grafo, roda o PSO e plota o grafo inicial, a melhor rota e a evolução do fitness.
- `prototipos/`: versões anteriores e testes feitos durante o trabalho (interfaces em Tkinter, visualização 2D/3D e o primeiro grafo de cidades e postos).

## Como executar
```
pip install matplotlib networkx
python evrp_pso.py
```
Os protótipos rodam do mesmo jeito (`python prototipos/<arquivo>.py`); alguns precisam também do `numpy`, e os que têm interface usam o Tkinter, que já vem com o Python.
