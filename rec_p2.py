"""
Questão - Análise de Complexidade
Para cada algoritmo (A–F), responda:
1. A complexidade temporal no pior caso. Justifique.
2. A complexidade espacial adicional. Justifique.
"""

# ============================================================
def algoritmo_a(x, y):
    """
    Entrada: Dois inteiros x e y de n dígitos
    Saída: Produto x * y
    """
    if x < 10 or y < 10:
        return x * y
    
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    
    divisor = 10 ** m
    a, b = x // divisor, x % divisor
    c, d = y // divisor, y % divisor
    
    ac = algoritmo_a(a, c)
    bd = algoritmo_a(b, d)
    ad_bc = algoritmo_a(a + b, c + d) - ac - bd
    
    return ac * (10 ** (2 * m)) + ad_bc * (10 ** m) + bd


# ============================================================
def algoritmo_b(A, B):
    """
    Entrada: Duas matrizes n×n (n é potência de 2)
    Saída: Matriz produto C = A × B
    """
    n = len(A)
    
    if n == 1:
        return [[A[0][0] * B[0][0]]]
    
    mid = n // 2
    
    A11 = [[A[i][j] for j in range(mid)] for i in range(mid)]
    A12 = [[A[i][j] for j in range(mid, n)] for i in range(mid)]
    A21 = [[A[i][j] for j in range(mid)] for i in range(mid, n)]
    A22 = [[A[i][j] for j in range(mid, n)] for i in range(mid, n)]
    
    B11 = [[B[i][j] for j in range(mid)] for i in range(mid)]
    B12 = [[B[i][j] for j in range(mid, n)] for i in range(mid)]
    B21 = [[B[i][j] for j in range(mid)] for i in range(mid, n)]
    B22 = [[B[i][j] for j in range(mid, n)] for i in range(mid, n)]
    
    M1 = algoritmo_b(soma(A11, A22), soma(B11, B22))
    M2 = algoritmo_b(soma(A21, A22), B11)
    M3 = algoritmo_b(A11, subtrai(B12, B22))
    M4 = algoritmo_b(A22, subtrai(B21, B11))
    M5 = algoritmo_b(soma(A11, A12), B22)
    M6 = algoritmo_b(subtrai(A21, A11), soma(B11, B12))
    M7 = algoritmo_b(subtrai(A12, A22), soma(B21, B22))
    
    C11 = soma(subtrai(soma(M1, M4), M5), M7)
    C12 = soma(M3, M5)
    C21 = soma(M2, M4)
    C22 = soma(subtrai(soma(M1, M3), M2), M6)
    
    return combina(C11, C12, C21, C22)

def soma(X, Y):
    n = len(X)
    return [[X[i][j] + Y[i][j] for j in range(n)] for i in range(n)]

def subtrai(X, Y):
    n = len(X)
    return [[X[i][j] - Y[i][j] for j in range(n)] for i in range(n)]

def combina(C11, C12, C21, C22):
    n = len(C11) * 2
    mid = n // 2
    C = [[0] * n for _ in range(n)]
    for i in range(mid):
        for j in range(mid):
            C[i][j] = C11[i][j]
            C[i][j + mid] = C12[i][j]
            C[i + mid][j] = C21[i][j]
            C[i + mid][j + mid] = C22[i][j]
    return C


# ============================================================
def algoritmo_c(texto, padrao):
    """
    Entrada: String texto de tamanho n, string padrão de tamanho m
    Saída: Lista de índices onde o padrão ocorre
    """
    n, m = len(texto), len(padrao)
    BASE = 256
    MOD = 101
    ocorrencias = []
    
    if m > n:
        return ocorrencias
    
    hash_padrao = 0
    hash_janela = 0
    h = 1
    
    for i in range(m - 1):
        h = (h * BASE) % MOD
    
    for i in range(m):
        hash_padrao = (BASE * hash_padrao + ord(padrao[i])) % MOD
        hash_janela = (BASE * hash_janela + ord(texto[i])) % MOD
    
    for i in range(n - m + 1):
        if hash_padrao == hash_janela:
            match = True
            for j in range(m):
                if texto[i + j] != padrao[j]:
                    match = False
                    break
            if match:
                ocorrencias.append(i)
        
        if i < n - m:
            hash_janela = (BASE * (hash_janela - ord(texto[i]) * h) + 
                          ord(texto[i + m])) % MOD
            if hash_janela < 0:
                hash_janela += MOD
    
    return ocorrencias


# ============================================================
def algoritmo_d(grafo):
    """
    Entrada: Grafo dirigido G representado por lista de adjacência
    Saída: Lista de componentes fortemente conexas
    """
    n = len(grafo)
    visitado = [False] * n
    pilha = []
    
    def dfs1(v):
        visitado[v] = True
        for u in grafo[v]:
            if not visitado[u]:
                dfs1(u)
        pilha.append(v)
    
    for v in range(n):
        if not visitado[v]:
            dfs1(v)
    
    grafo_t = [[] for _ in range(n)]
    for v in range(n):
        for u in grafo[v]:
            grafo_t[u].append(v)
    
    visitado = [False] * n
    componentes = []
    
    def dfs2(v, componente):
        visitado[v] = True
        componente.append(v)
        for u in grafo_t[v]:
            if not visitado[u]:
                dfs2(u, componente)
    
    while pilha:
        v = pilha.pop()
        if not visitado[v]:
            componente = []
            dfs2(v, componente)
            componentes.append(componente)
    
    return componentes


# ============================================================
def algoritmo_e(grafo):
    """
    Entrada: Grafo dirigido G com V vértices (lista de adjacência)
    Saída: Lista de componentes fortemente conexas
    """
    n = len(grafo)
    ids = [-1] * n
    low = [0] * n
    on_stack = [False] * n
    pilha = []
    componentes = []
    contador = [0]
    
    def dfs(v):
        ids[v] = contador[0]
        low[v] = contador[0]
        contador[0] += 1
        pilha.append(v)
        on_stack[v] = True
        
        for u in grafo[v]:
            if ids[u] == -1:
                dfs(u)
                low[v] = min(low[v], low[u])
            elif on_stack[u]:
                low[v] = min(low[v], ids[u])
        
        if ids[v] == low[v]:
            componente = []
            while True:
                u = pilha.pop()
                on_stack[u] = False
                componente.append(u)
                if u == v:
                    break
            componentes.append(componente)
    
    for v in range(n):
        if ids[v] == -1:
            dfs(v)
    
    return componentes


# ============================================================
def algoritmo_f(grafo, pesos):
    """
    Entrada: Grafo G com V vértices, dicionário de pesos das arestas
    Saída: Matriz de distâncias mínimas entre todos os pares
    """
    n = len(grafo)
    INF = float('inf')
    
    grafo_ext = [lista[:] for lista in grafo]
    grafo_ext.append(list(range(n)))
    pesos_ext = pesos.copy()
    for v in range(n):
        pesos_ext[(n, v)] = 0
    
    h = [INF] * (n + 1)
    h[n] = 0
    
    for _ in range(n):
        for u in range(n + 1):
            for v in grafo_ext[u]:
                if h[u] + pesos_ext[(u, v)] < h[v]:
                    h[v] = h[u] + pesos_ext[(u, v)]
    
    for u in range(n + 1):
        for v in grafo_ext[u]:
            if h[u] + pesos_ext[(u, v)] < h[v]:
                return None
    
    pesos_rep = {}
    for u in range(n):
        for v in grafo[u]:
            pesos_rep[(u, v)] = pesos[(u, v)] + h[u] - h[v]
    
    dist = [[INF] * n for _ in range(n)]
    
    for s in range(n):
        d = [INF] * n
        d[s] = 0
        visitado = [False] * n
        
        for _ in range(n):
            u = -1
            for v in range(n):
                if not visitado[v] and (u == -1 or d[v] < d[u]):
                    u = v
            
            if d[u] == INF:
                break
            
            visitado[u] = True
            
            for v in grafo[u]:
                if d[u] + pesos_rep[(u, v)] < d[v]:
                    d[v] = d[u] + pesos_rep[(u, v)]
        
        for v in range(n):
            if d[v] < INF:
                dist[s][v] = d[v] - h[s] + h[v]
    
    return dist
