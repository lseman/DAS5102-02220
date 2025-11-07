from collections import defaultdict, deque

class Grafo:
    """
    Classe para representar um grafo usando lista de adjacência.
    Suporta grafos direcionados e não direcionados, com pesos nas arestas.
    """

    def __init__(self, direcionado=False):
        self.adjacencias = defaultdict(list)
        self.direcionado = direcionado

    def adicionar_vertice(self, vertice):
        if vertice not in self.adjacencias:
            self.adjacencias[vertice] = []

    def adicionar_aresta(self, u, v, peso=1):
        # garante que os vértices existam na estrutura
        _ = self.adjacencias[u]
        _ = self.adjacencias[v]
        self.adjacencias[u].append((v, peso))
        if not self.direcionado:
            self.adjacencias[v].append((u, peso))

    def obter_vizinhos(self, vertice):
        return self.adjacencias[vertice]

    def obter_vertices(self):
        return list(self.adjacencias.keys())

    def obter_grau(self, vertice):
        return len(self.adjacencias[vertice])

    def tem_aresta(self, u, v):
        return any(vizinho == v for vizinho, _ in self.adjacencias[u])

    def imprimir_grafo(self):
        tipo = "Direcionado" if self.direcionado else "Não Direcionado"
        print(f"Tipo: Grafo {tipo}")
        print("Representação do Grafo:")
        vertices = self.obter_vertices()
        if not vertices:
            print("  Grafo vazio")
            return
        for vertice in sorted(vertices):
            vizinhos = [f"{v}(peso:{p})" for v, p in self.obter_vizinhos(vertice)]
            print(f"  Vértice {vertice}: {vizinhos}")

    def obter_numero_arestas(self):
        total_conexoes = sum(len(vizinhos) for vizinhos in self.adjacencias.values())
        return total_conexoes if self.direcionado else total_conexoes // 2

    def esta_vazio(self):
        return len(self.adjacencias) == 0

    # ──────────────────────────────────────────────────────────────────────
    # NOVO: BFS (Busca em Largura)
    # ──────────────────────────────────────────────────────────────────────
    def bfs(self, origem, alvo=None):
        """
        Executa BFS a partir de `origem`.
        Args:
            origem: vértice inicial
            alvo (opcional): se fornecido, para quando `alvo` é alcançado
        Returns:
            ordem (list): ordem de visita
            pais (dict): pai[v] = predecessor de v (origem tem pai None)
            dist (dict): distâncias em número de arestas a partir de origem
        """
        if origem not in self.adjacencias:
            raise ValueError(f"Origem '{origem}' não pertence ao grafo.")

        visitado = set([origem])
        fila = deque([origem])
        pais = {origem: None}
        dist = {origem: 0}
        ordem = []

        while fila:
            u = fila.popleft()
            ordem.append(u)
            if alvo is not None and u == alvo:
                break
            for v, _peso in self.adjacencias[u]:
                if v not in visitado:
                    visitado.add(v)
                    pais[v] = u
                    dist[v] = dist[u] + 1
                    fila.append(v)

        return ordem, pais, dist

    # ──────────────────────────────────────────────────────────────────────
    # Plotagem do grafo
    # ──────────────────────────────────────────────────────────────────────
    def plotar(self, layout="spring", destacar_caminho=None, figsize=(7, 5),
               mostrar_pesos=True, salvar_como=None, titulo=None, seed=42):
        """
        Plota o grafo. Requer `networkx` + `matplotlib`. Se `networkx` não
        estiver disponível, imprime um esboço ASCII com lista de arestas.

        Args:
            layout (str): 'spring' | 'kamada_kawai' | 'circular' | 'planar' | 'random'
            destacar_caminho (list|tuple|None): sequência de vértices para destacar
            figsize (tuple): tamanho da figura matplotlib
            mostrar_pesos (bool): desenha rótulos de pesos nas arestas
            salvar_como (str|None): caminho de arquivo para salvar a figura
            titulo (str|None): título do gráfico
            seed (int): semente do layout (quando aplicável)
        """
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except Exception:
            # fallback textual
            print("networkx/matplotlib não encontrados. Esboço textual:")
            tipo = "->" if self.direcionado else "--"
            print("Vértices:", sorted(self.obter_vertices()))
            print("Arestas:")
            seen = set()
            for u in self.adjacencias:
                for v, w in self.adjacencias[u]:
                    if self.direcionado or (u, v) not in seen and (v, u) not in seen:
                        print(f"  {u} {tipo} {v} (peso={w})")
                        if not self.direcionado:
                            seen.add((u, v))
            return

        G = nx.DiGraph() if self.direcionado else nx.Graph()
        for u in self.adjacencias:
            for v, w in self.adjacencias[u]:
                if self.direcionado:
                    G.add_edge(u, v, weight=w)
                else:
                    # evita duplicar arestas não direcionadas
                    if not G.has_edge(u, v) and not G.has_edge(v, u):
                        G.add_edge(u, v, weight=w)

        if layout == "spring":
            pos = nx.spring_layout(G, seed=seed)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "planar":
            try:
                pos = nx.planar_layout(G)
            except nx.NetworkXException:
                pos = nx.spring_layout(G, seed=seed)
        elif layout == "random":
            pos = nx.random_layout(G, seed=seed)
        else:
            pos = nx.spring_layout(G, seed=seed)

        plt.figure(figsize=figsize)
        nx.draw_networkx_nodes(G, pos, node_size=900, node_color="#dbeafe", edgecolors="#1e3a8a")
        nx.draw_networkx_labels(G, pos, font_size=10)

        # arestas (com setas se direcionado)
        if self.direcionado:
            nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>", arrowsize=16, width=1.6)
        else:
            nx.draw_networkx_edges(G, pos, width=1.6)

        if mostrar_pesos:
            edge_labels = {(u, v): d.get("weight", 1) for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

        # destacar caminho (se fornecido)
        if destacar_caminho and len(destacar_caminho) >= 2:
            caminho_pares = list(zip(destacar_caminho[:-1], destacar_caminho[1:]))
            # filtra apenas arestas que existem
            caminho_pares = [(u, v) for (u, v) in caminho_pares if G.has_edge(u, v)]
            if caminho_pares:
                # Para grafos direcionados, usa arrows=True (FancyArrowPatch)
                if self.direcionado:
                    nx.draw_networkx_edges(
                        G, pos, edgelist=caminho_pares,
                        width=3.0, edge_color="#ef4444",
                        arrows=True, arrowstyle="-|>", arrowsize=20
                    )
                else:
                    # Para grafos não direcionados, sem parâmetros de seta
                    nx.draw_networkx_edges(
                        G, pos, edgelist=caminho_pares,
                        width=3.0, edge_color="#ef4444"
                    )

        if titulo:
            plt.title(titulo, fontsize=12)
        plt.axis("off")
        if salvar_como:
            plt.tight_layout()
            plt.savefig(salvar_como, dpi=150)
        plt.show()


# ──────────────────────────────────────────────────────────────────────────────
# EXEMPLO RÁPIDO DE USO
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Grafo(direcionado=False)
    g.adicionar_aresta("A", "B", 2)
    g.adicionar_aresta("A", "C", 1)
    g.adicionar_aresta("B", "D", 3)
    g.adicionar_aresta("C", "D", 4)
    g.adicionar_aresta("C", "E", 5)

    # Plot (se networkx/matplotlib instalados)
    g.plotar(layout="spring", titulo="Grafinho")
