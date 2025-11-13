from AbstractGraph import AbstractGraph

class AdjacencyListGraph(AbstractGraph):
    """
    Implementação de grafo direcionado utilizando listas de adjacência.
    Grafo simples: não permite laços nem múltiplas arestas.
    """
    
    def __init__(self, num_vertices: int):
        """
        Construtor do grafo com listas de adjacência.
        
        Args:
            num_vertices: Número de vértices do grafo
        """
        super().__init__(num_vertices)
        
        # Inicializa as listas de adjacência (lista de listas)
        # _adj_list[i] contém os vértices para os quais existe aresta de i
        self._adj_list = []
        for i in range(num_vertices):
            self._adj_list.append([])  # Lista vazia para cada vértice
        
        self._edge_count = 0
    
    def getVertexCount(self) -> int:
        """Retorna o número de vértices do grafo."""
        return self._num_vertices
    
    def getEdgeCount(self) -> int:
        """Retorna o número de arestas do grafo."""
        return self._edge_count
    
    def hasEdge(self, u: int, v: int) -> bool:
        """
        Verifica se existe uma aresta entre os vértices u e v.
        
        Args:
            u: Vértice origem
            v: Vértice destino
            
        Returns:
            True se a aresta existir, False caso contrário
        """
        self._validate_edge(u, v)
        return v in self._adj_list[u]
    
    def addEdge(self, u: int, v: int) -> None:
        """
        Adiciona uma aresta entre os vértices u e v.
        Operação idempotente: não duplica arestas existentes.
        
        Args:
            u: Vértice origem
            v: Vértice destino
        """
        self._validate_edge(u, v)
        
        # Verifica se a aresta já existe (idempotência)
        if v not in self._adj_list[u]:
            self._adj_list[u].append(v)
            self._edge_count += 1
    
    def removeEdge(self, u: int, v: int) -> None:
        """
        Remove a aresta entre os vértices u e v.
        
        Args:
            u: Vértice origem
            v: Vértice destino
        """
        self._validate_edge(u, v)
        
        if v in self._adj_list[u]:
            self._adj_list[u].remove(v)
            self._edge_count -= 1
    
    def isSucessor(self, u: int, v: int) -> bool:
        """
        Verifica se v é sucessor de u (existe aresta u -> v).
        
        Args:
            u: Vértice origem
            v: Vértice destino
            
        Returns:
            True se v for sucessor de u, False caso contrário
        """
        return self.hasEdge(u, v)
    
    def isPredessor(self, u: int, v: int) -> bool:
        """
        Verifica se v é predecessor de u (existe aresta v -> u).
        
        Args:
            u: Vértice de referência
            v: Possível predecessor
            
        Returns:
            True se v for predecessor de u, False caso contrário
        """
        return self.hasEdge(v, u)
    
    def getVertexInDegree(self, u: int) -> int:
        """
        Retorna o grau de entrada do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Número de arestas que chegam ao vértice u
        """
        self._validate_vertex(u)
        
        in_degree = 0
        for i in range(self._num_vertices):
            if u in self._adj_list[i]:
                in_degree += 1
        
        return in_degree
    
    def getVertexOutDegree(self, u: int) -> int:
        """
        Retorna o grau de saída do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Número de arestas que saem do vértice u
        """
        self._validate_vertex(u)
        return len(self._adj_list[u])
    
    def isConnected(self) -> bool:
        """
        Verifica se o grafo é conectado (versão para grafo direcionado: fracamente conectado).
        Um grafo direcionado é fracamente conectado se o grafo não direcionado subjacente é conectado.
        
        Returns:
            True se o grafo for conectado, False caso contrário
        """
        if self._num_vertices <= 1:
            return True
        
        if self.isEmptyGraph():
            return False
        
        # DFS para verificar conectividade fraca
        visited = [False] * self._num_vertices
        
        # Encontra o primeiro vértice com pelo menos uma aresta
        start = -1
        for i in range(self._num_vertices):
            if self.getVertexInDegree(i) > 0 or self.getVertexOutDegree(i) > 0:
                start = i
                break
        
        if start == -1:
            return False
        
        # DFS considerando o grafo como não direcionado
        self._dfs_undirected(start, visited)
        
        # Verifica se todos os vértices com arestas foram visitados
        for i in range(self._num_vertices):
            if (self.getVertexInDegree(i) > 0 or self.getVertexOutDegree(i) > 0) and not visited[i]:
                return False
        
        return True
    
    def _dfs_undirected(self, vertex: int, visited) -> None:
        """
        DFS auxiliar para verificar conectividade tratando o grafo como não direcionado.
        
        Args:
            vertex: Vértice atual
            visited: Lista de vértices visitados
        """
        visited[vertex] = True
        
        # Verifica sucessores (arestas de saída)
        for neighbor in self._adj_list[vertex]:
            if not visited[neighbor]:
                self._dfs_undirected(neighbor, visited)
        
        # Verifica predecessores (arestas de entrada)
        for i in range(self._num_vertices):
            if not visited[i] and vertex in self._adj_list[i]:
                self._dfs_undirected(i, visited)
    
    def isEmptyGraph(self) -> bool:
        """
        Verifica se o grafo é vazio (não possui arestas).
        
        Returns:
            True se o grafo não possuir arestas, False caso contrário
        """
        return self._edge_count == 0
    
    def isCompleteGraph(self) -> bool:
        """
        Verifica se o grafo é completo.
        Um grafo direcionado completo possui uma aresta para cada par ordenado de vértices distintos.
        
        Returns:
            True se o grafo for completo, False caso contrário
        """
        if self._num_vertices <= 1:
            return True
        
        # Um grafo completo direcionado com n vértices tem n*(n-1) arestas
        expected_edges = self._num_vertices * (self._num_vertices - 1)
        
        if self._edge_count != expected_edges:
            return False
        
        # Verifica se cada vértice tem arestas para todos os outros vértices
        for i in range(self._num_vertices):
            if len(self._adj_list[i]) != self._num_vertices - 1:
                return False
            
            # Verifica se contém todos os vértices exceto ele mesmo
            for j in range(self._num_vertices):
                if i != j and j not in self._adj_list[i]:
                    return False
        
        return True
    
    def getSuccessors(self, u: int):
        """
        Retorna o conjunto de sucessores do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Lista dos sucessores de u
        """
        self._validate_vertex(u)
        # Retorna uma cópia da lista de sucessores
        successors = []
        for vertex in self._adj_list[u]:
            successors.append(vertex)
        return successors
    
    def getPredecessors(self, u: int):
        """
        Retorna o conjunto de predecessores do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Lista dos predecessores de u
        """
        self._validate_vertex(u)
        predecessors = []
        
        for i in range(self._num_vertices):
            if u in self._adj_list[i]:
                predecessors.append(i)
        
        return predecessors
    
    def __str__(self) -> str:
        """
        Representação string das listas de adjacência.
        
        Returns:
            String representando as listas de adjacência
        """
        result = "Listas de Adjacência:\n"
        
        for i in range(self._num_vertices):
            # Ordena os sucessores manualmente
            successors = self._adj_list[i].copy()
            successors.sort()
            result += f"Vértice {i}: {successors}\n"
        
        return result
