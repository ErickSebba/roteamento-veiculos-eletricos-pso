import random
import math
import matplotlib.pyplot as plt
import networkx as nx
 
class EVRP:
    def __init__(self, num_cidades=20, num_postos=10, autonomia_max=70):
        self.num_cidades = num_cidades
        self.num_postos = num_postos
        self.autonomia_max = autonomia_max
        self.quantidade_bateria_zerada = 0
        self.gerar_problema()
    
    def gerar_problema(self):
        self.posicoes = {}
        for i in range(self.num_cidades):
            self.posicoes[i] = (random.uniform(0, round(self.autonomia_max*0.9)), random.uniform(0, round(self.autonomia_max*0.9)))
        for i in range(self.num_cidades, self.num_cidades + self.num_postos):
            self.posicoes[i] = (random.uniform(0, round(self.autonomia_max*0.9)), random.uniform(0, round(self.autonomia_max*0.9)))
        self.postos = set(range(self.num_cidades, self.num_cidades + self.num_postos))
        self.calcular_distancias()
    
    def calcular_distancias(self):
        total = self.num_cidades + self.num_postos
        self.distancias = [[0]*total for _ in range(total)]
        for i in range(total):
            for j in range(total):
                if i != j:
                    x1, y1 = self.posicoes[i]
                    x2, y2 = self.posicoes[j]
                    self.distancias[i][j] = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
    def encontrar_posto_viavel(self, origem, destino, autonomia_atual):
        for posto in self.postos:
            dist1 = self.distancias[origem][posto]
            dist2 = self.distancias[posto][destino]
            if dist1 <= autonomia_atual and dist2 <= self.autonomia_max:
                return posto, dist1 + dist2
        return None, float('inf')
    
    def fitness(self, rota):
        if rota[0] != 0 or rota[-1] != 0:
            return float('inf'), []
        
        autonomia = self.autonomia_max
        distancia_total = 0
        recargas = 0
        penalidade = 50
        self.quantidade_bateria_zerada = 0
        rota_detalhada = [rota[0]]
        
        for i in range(len(rota)-1):
            origem = rota_detalhada[-1]
            destino = rota[i+1]
            dist = self.distancias[origem][destino]
            
            if dist > autonomia:
                posto, nova_distancia = self.encontrar_posto_viavel(origem, destino, autonomia)
                if posto is None:
                    penalidade += 1000 * (dist - autonomia)
                    distancia_total += dist
                    autonomia -= dist
                    rota_detalhada.append(destino)
                else:
                    distancia_total += nova_distancia
                    recargas += 1
                    autonomia = self.autonomia_max - self.distancias[posto][destino]
                    rota_detalhada.extend([posto, destino])
            else:
                distancia_total += dist
                autonomia -= dist
                rota_detalhada.append(destino)
            
            if autonomia < 0:
                penalidade += 1000 * abs(autonomia)
                self.quantidade_bateria_zerada += 1
        
        return distancia_total + 50 * recargas + penalidade*self.quantidade_bateria_zerada, rota_detalhada

    def plot_grafo_inicial(self):
        """Plota o grafo completo com todas as conexões"""
        plt.figure(figsize=(14, 10))
        G = nx.Graph()
        for node in self.posicoes:
            tipo = "deposito" if node == 0 else ("posto" if node in self.postos else "cidade")
            G.add_node(node, pos=self.posicoes[node], tipo=tipo)
        
        for i in self.posicoes:
            for j in self.posicoes:
                if i != j:
                    G.add_edge(i, j, weight=self.distancias[i][j])
        
        pos = nx.get_node_attributes(G, 'pos')
        tipos = nx.get_node_attributes(G, 'tipo')
        
        cores = []
        formas = []
        for n in G.nodes:
            if tipos[n] == 'deposito':
                cores.append('red')
                formas.append('s')
            elif tipos[n] == 'posto':
                cores.append('lightgreen')
                formas.append('d')
            else:
                cores.append('lightgray')
                formas.append('o')

        for forma in set(formas):
            nodes_forma = [n for n in G.nodes if formas[n] == forma]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes_forma,
                                   node_shape=forma,
                                   node_color=[cores[n] for n in nodes_forma],
                                   node_size=600, edgecolors='black')
        
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=0.5, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=8)
        plt.title("Grafo Inicial com Todas as Cidades e Postos")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def plot_rota(self, rota):
        """Visualiza a rota como grafo direcionado"""
        plt.figure(figsize=(14, 10))
        G = nx.DiGraph()

        for node in self.posicoes:
            tipo = "deposito" if node == 0 else ("posto" if node in self.postos else "cidade")
            G.add_node(node, pos=self.posicoes[node], tipo=tipo)

        for i in range(len(rota)-1):
            G.add_edge(rota[i], rota[i+1], weight=self.distancias[rota[i]][rota[i+1]], ordem=i)

        pos = nx.get_node_attributes(G, 'pos')

        cores = []
        formas = []
        for n in G.nodes:
            if G.nodes[n]['tipo'] == 'deposito':
                cores.append('red')
                formas.append('s')
            elif G.nodes[n]['tipo'] == 'posto':
                cores.append('green' if n in rota else 'lightgreen')
                formas.append('d')
            else:
                cores.append('skyblue' if n in rota else 'lightgray')
                formas.append('o')

        for forma in set(formas):
            nodes_forma = [n for n in G.nodes if formas[n] == forma]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes_forma,
                                   node_shape=forma,
                                   node_color=[cores[n] for n in nodes_forma],
                                   node_size=600, edgecolors='black')

        edge_colors = ['red' if (u, v) in zip(rota[:-1], rota[1:]) else 'lightgray' for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, arrows=True, arrowsize=15)

        node_labels = {n: f"{i}\n({n})" for i, n in enumerate(rota)}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

        plt.title(f"Melhor Rota Encontrada (Autonomia {self.autonomia_max}km)")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

def plotar_rota(self, rota):
        """Visualiza a rota como grafo direcionado"""
        plt.figure(figsize=(14, 10))
        G = nx.DiGraph()

        for node in self.posicoes:
            tipo = "deposito" if node == 0 else ("posto" if node in self.postos else "cidade")
            G.add_node(node, pos=self.posicoes[node], tipo=tipo)

        for i in range(len(rota)-1):
            G.add_edge(rota[i], rota[i+1], weight=self.distancias[rota[i]][rota[i+1]], ordem=i)

        pos = nx.get_node_attributes(G, 'pos')

        cores = []
        formas = []
        for n in G.nodes:
            if G.nodes[n]['tipo'] == 'deposito':
                cores.append('red')
                formas.append('s')
            elif G.nodes[n]['tipo'] == 'posto':
                cores.append('green' if n in rota else 'lightgreen')
                formas.append('d')
            else:
                cores.append('skyblue' if n in rota else 'lightgray')
                formas.append('o')

        for forma in set(formas):
            nodes_forma = [n for n in G.nodes if formas[n] == forma]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes_forma,
                                   node_shape=forma,
                                   node_color=[cores[n] for n in nodes_forma],
                                   node_size=600, edgecolors='black')

        edge_colors = ['red' if (u, v) in zip(rota[:-1], rota[1:]) else 'lightgray' for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, arrows=True, arrowsize=15)

        node_labels = {n: f"{i}\n({n})" for i, n in enumerate(rota)}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

        plt.title(f"Melhor Rota Encontrada (Autonomia {self.autonomia_max}km)")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

class Particula:
    def __init__(self, dimensao, min_pos, max_pos):
        self.posicao = [random.uniform(min_pos, max_pos) for _ in range(dimensao)]
        self.velocidade = [random.uniform(-1, 1) for _ in range(dimensao)]
        self.melhor_posicao = list(self.posicao)
        self.melhor_fitness = float('inf')
    
    def decodificar(self, num_cidades):
        cidades = list(range(1, num_cidades))
        rota_ordenada = sorted(cidades, key=lambda x: self.posicao[x-1])
        return [0] + rota_ordenada + [0]

def PSO(problema, num_particulas=100, max_iteracoes=200, w=0.5, c1=0.15, c2=1.1):
    dimensao = problema.num_cidades - 1
    enxame = [Particula(dimensao, 0, 1) for _ in range(num_particulas)]
    melhor_global_fitness = float('inf')
    melhor_global_pos = None
    melhor_rota = []
    melhor_rota_detalhada = []
    historico = []

    for g in range(max_iteracoes):
        for particula in enxame:
            rota = particula.decodificar(problema.num_cidades)
            fitness, rota_detalhada = problema.fitness(rota)

            if fitness < particula.melhor_fitness:
                particula.melhor_fitness = fitness
                particula.melhor_posicao = list(particula.posicao)

            if fitness < melhor_global_fitness:
                melhor_global_fitness = fitness
                melhor_global_pos = list(particula.posicao)
                melhor_rota = rota
                melhor_rota_detalhada = rota_detalhada

        for particula in enxame:
            for i in range(dimensao):
                r1 = random.random()
                r2 = random.random()
                c = c1 * r1 * (particula.melhor_posicao[i] - particula.posicao[i])
                s = c2 * r2 * (melhor_global_pos[i] - particula.posicao[i])
                particula.velocidade[i] = w * particula.velocidade[i] + c + s
                particula.posicao[i] += particula.velocidade[i]
        if g % 10 == 0:
            print(f"Iteração {g}: Melhor fitness = {melhor_global_fitness:.2f}")
            historico.append(melhor_global_fitness)

    
    print(f"Quantidade de baterias zeradas na última geração: {problema.quantidade_bateria_zerada}")
    
    return melhor_rota, melhor_rota_detalhada, historico

# Execução
if __name__ == "__main__":
    problema = EVRP(num_cidades=20, num_postos=10, autonomia_max=70)

    print("Plotando grafo inicial completo...")
    problema.plot_grafo_inicial()

    melhor_rota, rota_detalhada, historico = PSO(problema)
    distancia_total = sum(
        problema.distancias[rota_detalhada[i]][rota_detalhada[i+1]] for i in range(len(rota_detalhada)-1)
    )

    print("\nMelhor rota simplificada:", melhor_rota)
    print("Rota detalhada com postos:", rota_detalhada)
    print(f"Distância total percorrida: {distancia_total:.2f} km")
    print(f"Fitness final: {historico[-1]:.2f}")

    problema.plot_rota(rota_detalhada)


    # Plot evolução
    plt.plot(historico, color='blue')
    plt.title("Evolução do Fitness")
    plt.xlabel("Iteração")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
