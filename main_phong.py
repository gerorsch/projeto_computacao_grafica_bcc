import tkinter as tk

###########################################
# Funções Matemáticas e Operações Vetoriais
###########################################

def my_sqrt(x):
    """
    Calcula a raiz quadrada de x utilizando o método de Newton.

    Parâmetros:
        x (float): Valor de entrada.

    Retorna:
        float: Aproximação da raiz quadrada de x.
    """
    if x <= 0:
        return 0
    guess = x / 2.0
    for i in range(20):
        guess = (guess + x / guess) / 2.0
    return guess

def normalize(v):
    """
    Normaliza o vetor v.

    Parâmetros:
        v (list of float): Vetor de entrada.

    Retorna:
        list of float: Vetor normalizado.
    """
    norm = my_sqrt(sum(x * x for x in v))
    if norm == 0:
        return v
    return [x / norm for x in v]

def dot(v1, v2):
    """
    Calcula o produto escalar de dois vetores.

    Parâmetros:
        v1, v2 (list of float): Vetores de entrada.

    Retorna:
        float: Produto escalar.
    """
    return sum(a * b for a, b in zip(v1, v2))

def cross(v1, v2):
    """
    Calcula o produto vetorial entre dois vetores 3D.

    Parâmetros:
        v1, v2 (list of float): Vetores 3D.

    Retorna:
        list of float: Vetor resultante do produto vetorial.
    """
    return [v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0]]

def vec_add(a, b):
    """
    Soma dois vetores de mesmo tamanho.

    Parâmetros:
        a, b (list of float): Vetores.

    Retorna:
        list of float: Soma componente a componente.
    """
    return [a[i] + b[i] for i in range(len(a))]

def vec_sub(a, b):
    """
    Subtrai o vetor b do vetor a.

    Parâmetros:
        a, b (list of float): Vetores.

    Retorna:
        list of float: Resultado da subtração componente a componente.
    """
    return [a[i] - b[i] for i in range(len(a))]

def vec_scalar_mult(a, s):
    """
    Multiplica o vetor a por um escalar s.

    Parâmetros:
        a (list of float): Vetor.
        s (float): Escalar.

    Retorna:
        list of float: Vetor escalado.
    """
    return [a[i] * s for i in range(len(a))]

def vec_mul(a, b):
    """
    Multiplicação componente a componente de dois vetores.

    Parâmetros:
        a, b (list of float): Vetores.

    Retorna:
        list of float: Produto componente a componente.
    """
    return [a[i] * b[i] for i in range(len(a))]

def vec_clamp(a, min_val, max_val):
    """
    Limita cada componente do vetor a entre min_val e max_val.

    Parâmetros:
        a (list of float): Vetor.
        min_val (float): Valor mínimo.
        max_val (float): Valor máximo.

    Retorna:
        list of float: Vetor com valores limitados.
    """
    return [max(min(x, max_val), min_val) for x in a]

###########################################
# Funções de Carregamento de Arquivos
###########################################

def load_mesh(filename):
    """
    Carrega a malha 3D a partir do arquivo mesh.txt.
    
    Formato esperado:
      <número de vértices> <número de triângulos>
      <x> <y> <z>   (para cada vértice)
      <i1> <i2> <i3>   (para cada triângulo, índices 1-indexados)

    Parâmetros:
        filename (str): Caminho para o arquivo mesh.txt.

    Retorna:
        tuple: (vertices, triangles)
          - vertices: lista de listas [x, y, z]
          - triangles: lista de listas [i1, i2, i3] (convertidos para 0-indexados)
    """
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    header = lines[0].split()
    n_vertices = int(header[0])
    n_triangles = int(header[1])
    vertices = []
    # Carrega as coordenadas de cada vértice
    for i in range(1, 1 + n_vertices):
        coords = list(map(float, lines[i].split()))
        vertices.append(coords)
    triangles = []
    # Carrega os triângulos, convertendo índices de 1-indexado para 0-indexado
    for i in range(1 + n_vertices, 1 + n_vertices + n_triangles):
        indices = list(map(int, lines[i].split()))
        triangles.append([idx - 1 for idx in indices])
    return vertices, triangles

def load_camera(filename):
    """
    Carrega os parâmetros da câmera a partir do arquivo camera.txt.
    
    Formato (6 linhas):
      1. Vetor N (ex.: "0 1 -1")
      2. Vetor V (ex.: "0 -1 -1")
      3. Escalar d (ex.: "5")
      4. Escalar hx (ex.: "2")
      5. Escalar hy (ex.: "2")
      6. Ponto C (ex.: "0 -500 500")
    
    Parâmetros:
        filename (str): Caminho para o arquivo camera.txt.
    
    Retorna:
        dict: Com chaves 'N', 'V', 'd', 'hx', 'hy' e 'C'.
    """
    params = {}
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) != 6:
        raise ValueError("O arquivo camera.txt deve conter exatamente 6 linhas.")
    params['N'] = list(map(float, lines[0].split()))
    params['V'] = list(map(float, lines[1].split()))
    params['d'] = float(lines[2])
    params['hx'] = float(lines[3])
    params['hy'] = float(lines[4])
    params['C'] = list(map(float, lines[5].split()))
    return params

def parse_line(line):
    """
    Se a linha contiver um '=', extrai a parte após o sinal;
    caso contrário, retorna a linha inalterada.
    
    Parâmetros:
        line (str): Linha do arquivo.
    
    Retorna:
        str: Parte relevante da linha (sem rótulo).
    """
    if "=" in line:
        parts = line.split("=")
        return parts[1].strip()
    return line

def load_lighting(filename):
    """
    Carrega os parâmetros de iluminação a partir do arquivo lighting.txt.
    
    Formato (8 linhas). Cada linha pode conter um rótulo ou não:
      1. Iamb – Cor ambiente (ex.: "Iamb = 100 100 100" ou "100 100 100")
      2. Ka – Coeficiente ambiente (ex.: "Ka = 0.2" ou "0.2")
      3. Il – Intensidade da luz (ex.: "Il = 127 213 254" ou "127 213 254")
      4. Pl – Ponto da fonte de luz (ex.: "Pl = 60 5 -10" ou "60 5 -10")
      5. Kd – Coeficiente difuso (ex.: "Kd = 0.5 0.3 0.2" ou "0.5 0.3 0.2")
      6. Od – Cor difusa do objeto (ex.: "Od = 0.7 0.5 0.8" ou "0.7 0.5 0.8")
      7. Ks – Coeficiente especular (ex.: "Ks = 0.5" ou "0.5")
      8. η – Expoente especular (ex.: "η = 1" ou "1")
    
    Parâmetros:
        filename (str): Caminho para o arquivo lighting.txt.
    
    Retorna:
        dict: Com as chaves 'Iamb', 'Ka', 'Il', 'Pl', 'Kd', 'Od', 'Ks' e 'eta'.
    """
    params = {}
    with open(filename, "r") as f:
        raw_lines = [line.strip() for line in f if line.strip()]
        # Remove rótulos, se presentes
        lines = [parse_line(line) for line in raw_lines]
    if len(lines) != 8:
        raise ValueError("O arquivo lighting.txt deve conter exatamente 8 linhas (após remover cabeçalhos).")
    params['Iamb'] = list(map(float, lines[0].split()))
    params['Ka'] = float(lines[1])
    params['Il'] = list(map(float, lines[2].split()))
    params['Pl'] = list(map(float, lines[3].split()))
    params['Kd'] = list(map(float, lines[4].split()))
    params['Od'] = list(map(float, lines[5].split()))
    params['Ks'] = float(lines[6])
    params['eta'] = float(lines[7])
    return params

###########################################
# Cálculo dos Normais dos Vértices
###########################################

def compute_vertex_normals(vertices, triangles):
    """
    Calcula os normais de cada vértice pela média dos normais das faces adjacentes.

    Parâmetros:
        vertices (list): Lista de vértices [x, y, z].
        triangles (list): Lista de triângulos (índices 0-indexados).

    Retorna:
        list: Lista de normais, uma para cada vértice.
    """
    n_vertices = len(vertices)
    normals = [[0, 0, 0] for _ in range(n_vertices)]
    for tri in triangles:
        i0, i1, i2 = tri
        v0 = vertices[i0]
        v1 = vertices[i1]
        v2 = vertices[i2]
        # Calcula os vetores das arestas
        edge1 = vec_sub(v1, v0)
        edge2 = vec_sub(v2, v0)
        # Calcula a normal da face (não normalizada)
        face_normal = cross(edge1, edge2)
        # Acumula a normal em cada vértice do triângulo
        normals[i0] = vec_add(normals[i0], face_normal)
        normals[i1] = vec_add(normals[i1], face_normal)
        normals[i2] = vec_add(normals[i2], face_normal)
    # Normaliza as normais calculadas
    normals = [normalize(n) for n in normals]
    return normals

###########################################
# Transformações: Mundo → Vista → Projeção
###########################################

def world_to_view(vertices, camera):
    """
    Converte os vértices do sistema mundial para o sistema de vista utilizando os parâmetros da câmera.

    Parâmetros:
        vertices (list): Lista de vértices [x, y, z].
        camera (dict): Parâmetros da câmera ('N', 'V', 'd', 'hx', 'hy', 'C').

    Retorna:
        tuple:
          - Lista de vértices transformados (view).
          - Base da câmera (u, v, n) utilizada para a transformação (útil para transformar normais).
    """
    C = camera['C']
    N = normalize(camera['N'])
    V = normalize(camera['V'])
    # Define a base da câmera
    u = normalize(cross(V, N))  # Vetor à direita
    v = V[:]                   # Vetor "up"
    n = N[:]                   # Direção da câmera
    view_vertices = []
    for P in vertices:
        # Translada o vértice em relação a C e projeta na base (u, v, n)
        PC = vec_sub(P, C)
        x_prime = dot(PC, u)
        y_prime = dot(PC, v)
        z_prime = dot(PC, n)
        view_vertices.append([x_prime, y_prime, z_prime])
    return view_vertices, (u, v, n)

def transform_normals(normals, camera_basis):
    """
    Transforma os normais (definidos em coordenadas do mundo) para o sistema de vista.

    Parâmetros:
        normals (list): Lista de normais em mundo.
        camera_basis (tuple): Base da câmera (u, v, n).

    Retorna:
        list: Lista de normais transformadas e normalizadas.
    """
    u, v, n = camera_basis
    normals_view = []
    for Nw in normals:
        nx = dot(Nw, u)
        ny = dot(Nw, v)
        nz = dot(Nw, n)
        normals_view.append(normalize([nx, ny, nz]))
    return normals_view

def perspective_projection(view_vertices, d):
    """
    Aplica a projeção em perspectiva aos vértices no sistema de vista.

    Para cada vértice (x, y, z), calcula:
      xp = d * x / z
      yp = d * y / z

    Parâmetros:
        view_vertices (list): Lista de vértices no sistema de vista.
        d (float): Distância do plano de projeção.

    Retorna:
        list: Lista de tuplas (xp, yp, z), mantendo z para o z-buffer.
    """
    proj = []
    for x, y, z in view_vertices:
        if z != 0:
            xp = d * x / z
            yp = d * y / z
        else:
            xp, yp = x, y
        proj.append((xp, yp, z))
    return proj

def to_normalized(proj_vertices, hx, hy):
    """
    Converte as coordenadas projetadas para um sistema normalizado.

    Parâmetros:
        proj_vertices (list): Lista de tuplas (xp, yp, z).
        hx (float): Escala horizontal.
        hy (float): Escala vertical.

    Retorna:
        list: Lista de tuplas (xn, yn, z) com coordenadas normalizadas.
    """
    norm = []
    for xp, yp, z in proj_vertices:
        xn = xp / hx
        yn = yp / hy
        norm.append((xn, yn, z))
    return norm

def to_screen(norm_vertices, width, height):
    """
    Mapeia as coordenadas normalizadas para coordenadas de tela.

    Parâmetros:
        norm_vertices (list): Lista de tuplas (xn, yn, z) com valores entre -1 e 1.
        width (int): Largura da tela.
        height (int): Altura da tela.

    Retorna:
        list: Lista de tuplas (sx, sy, z) com coordenadas de tela.
    """
    screen = []
    for xn, yn, z in norm_vertices:
        sx = int((xn + 1) * width / 2)
        sy = int((1 - yn) * height / 2)  # Inverte o eixo y
        screen.append((sx, sy, z))
    return screen

###########################################
# Cálculo de Coordenadas Baricêntricas
###########################################

def barycentric(p, p0, p1, p2):
    """
    Calcula as coordenadas baricêntricas do ponto p em relação ao triângulo formado por p0, p1 e p2.

    Parâmetros:
        p (tuple): Ponto (x, y) onde se deseja as coordenadas.
        p0, p1, p2 (tuple): Vértices do triângulo (x, y).

    Retorna:
        tuple: (alpha, beta, gamma) coordenadas baricêntricas.
    """
    x, y = p
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2
    denom = ((y1 - y2)*(x0 - x2) + (x2 - x1)*(y0 - y2))
    if denom == 0:
        return (-1, -1, -1)
    alpha = ((y1 - y2)*(x - x2) + (x2 - x1)*(y - y2)) / denom
    beta  = ((y2 - y0)*(x - x2) + (x0 - x2)*(y - y2)) / denom
    gamma = 1 - alpha - beta
    return (alpha, beta, gamma)

###########################################
# Modelo de Iluminação de Phong
###########################################

def compute_phong_color(P, N, lighting, Pl_view):
    """
    Computa a cor final de um ponto P com normal N usando o modelo de iluminação de Phong.

    Componentes:
      - Ambiente: Iamb * Ka
      - Difuso: Il * Kd * (N • L) * Od, onde L é a direção da luz.
      - Especular: Il * Ks * (R • V)^eta, onde R é a reflexão de L em N e V é a direção da visão.

    Parâmetros:
        P (list): Posição do ponto em view ([x, y, z]).
        N (list): Normal interpolada no ponto (normalizada).
        lighting (dict): Parâmetros de iluminação com chaves:
                         'Iamb', 'Ka', 'Il', 'Kd', 'Od', 'Ks', 'eta'.
        Pl_view (list): Posição da luz em view ([x, y, z]).

    Retorna:
        tuple: Cor final (R, G, B) com valores inteiros (0-255).
    """
    # Componente ambiente
    ambient = vec_scalar_mult(lighting['Iamb'], lighting['Ka'])
    
    # Calcula o vetor L (do ponto P até a fonte de luz)
    L = normalize(vec_sub(Pl_view, P))
    ndotl = dot(N, L)
    if ndotl < 0:
        ndotl = 0
    
    # Componente difusa
    diffuse = vec_mul(lighting['Il'], lighting['Kd'])
    diffuse = vec_scalar_mult(diffuse, ndotl)
    diffuse = vec_mul(diffuse, lighting['Od'])
    
    # Vetor V: direção da visão (de P para a origem, que é a posição da câmera em view)
    Vp = normalize(vec_scalar_mult(P, -1))
    
    # Vetor de reflexão R = 2*(N•L)*N - L
    R = vec_sub(vec_scalar_mult(N, 2 * dot(N, L)), L)
    rdotv = dot(R, Vp)
    if rdotv < 0:
        rdotv = 0
    spec_factor = rdotv ** lighting['eta']
    specular = vec_scalar_mult(lighting['Il'], lighting['Ks'] * spec_factor)
    
    # Soma das componentes de iluminação
    color = vec_add(ambient, vec_add(diffuse, specular))
    # Limita os valores para o intervalo [0, 255]
    color = vec_clamp(color, 0, 255)
    return (int(color[0]), int(color[1]), int(color[2]))

###########################################
# Rasterização com Z-Buffer e Iluminação Phong
###########################################

def fill_triangle_phong(photo, z_buffer, tri, lighting, Pl_view):
    """
    Preenche um triângulo aplicando o modelo de Phong e usando z-buffer para visibilidade.

    Parâmetros:
        photo (tk.PhotoImage): Objeto de desenho.
        z_buffer (list of list): Matriz de profundidade.
        tri (dict): Contém:
                   'p' : Lista de 3 vértices em coordenadas de tela [(x,y), ...].
                   'v' : Lista de 3 vértices em view ([x,y,z]).
                   'n' : Lista de 3 normais em view ([nx,ny,nz]).
        lighting (dict): Parâmetros de iluminação.
        Pl_view (list): Posição da luz em view.
    """
    p0, p1, p2 = tri['p']
    v0, v1, v2 = tri['v']
    n0, n1, n2 = tri['n']
    
    # Determina a caixa delimitadora do triângulo para limitar o processamento
    xs = [p0[0], p1[0], p2[0]]
    ys = [p0[1], p1[1], p2[1]]
    x_min = max(min(xs), 0)
    x_max = min(max(xs), photo.width() - 1)
    y_min = max(min(ys), 0)
    y_max = min(max(ys), photo.height() - 1)
    
    # Percorre os pixels dentro da caixa delimitadora
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            bc = barycentric((x, y), p0, p1, p2)
            alpha, beta, gamma = bc
            # Se qualquer coordenada baricêntrica for negativa, o ponto está fora do triângulo
            if alpha < 0 or beta < 0 or gamma < 0:
                continue
            # Interpola a profundidade z
            z = alpha * v0[2] + beta * v1[2] + gamma * v2[2]
            if z < z_buffer[y][x]:
                z_buffer[y][x] = z
                # Interpola a posição em view
                P = [alpha * v0[i] + beta * v1[i] + gamma * v2[i] for i in range(3)]
                # Interpola a normal e a normaliza
                N_interp = [alpha * n0[i] + beta * n1[i] + gamma * n2[i] for i in range(3)]
                N_interp = normalize(N_interp)
                # Calcula a cor do pixel utilizando o modelo de Phong
                color = compute_phong_color(P, N_interp, lighting, Pl_view)
                draw_pixel(photo, x, y, color)

def draw_mesh(photo, z_buffer, vertices_screen, vertices_view, normals_view, triangles, lighting, Pl_view):
    """
    Desenha a malha 3D triângulo a triângulo, aplicando a interpolação de valores e iluminação Phong.

    Parâmetros:
        photo (tk.PhotoImage): Objeto para desenho.
        z_buffer (list of list): Matriz de profundidade.
        vertices_screen (list): Lista de vértices em coordenadas de tela (sx, sy, z).
        vertices_view (list): Lista de vértices em view ([x,y,z]).
        normals_view (list): Lista de normais transformadas para o sistema de view.
        triangles (list): Lista de triângulos (índices 0-indexados).
        lighting (dict): Parâmetros de iluminação.
        Pl_view (list): Posição da luz em view.
    """
    for tri in triangles:
        i0, i1, i2 = tri
        # Extrai as coordenadas dos vértices de tela
        p0 = (vertices_screen[i0][0], vertices_screen[i0][1])
        p1 = (vertices_screen[i1][0], vertices_screen[i1][1])
        p2 = (vertices_screen[i2][0], vertices_screen[i2][1])
        # Extrai as coordenadas dos vértices em view
        v0 = vertices_view[i0]
        v1 = vertices_view[i1]
        v2 = vertices_view[i2]
        # Extrai as normais em view
        n0 = normals_view[i0]
        n1 = normals_view[i1]
        n2 = normals_view[i2]
        tri_data = {'p': [p0, p1, p2],
                    'v': [v0, v1, v2],
                    'n': [n0, n1, n2]}
        fill_triangle_phong(photo, z_buffer, tri_data, lighting, Pl_view)

###########################################
# Função de Desenho de Pixel
###########################################

def draw_pixel(photo, x, y, color):
    """
    Desenha um único pixel no objeto PhotoImage.

    Parâmetros:
        photo (tk.PhotoImage): Objeto de desenho.
        x, y (int): Coordenadas do pixel.
        color (tuple): Cor do pixel no formato (R, G, B).
    """
    hex_color = "#%02x%02x%02x" % color
    photo.put(hex_color, (x, y))

###########################################
# Classe Principal da Aplicação
###########################################

class App:
    """
    Gerencia a aplicação: carrega os arquivos de malha, parâmetros da câmera e de iluminação,
    realiza as transformações e renderiza a malha com z-buffer e modelo de iluminação de Phong.
    
    Pressione 'r' para recarregar os arquivos e redesenhar sem fechar a aplicação.
    """
    def __init__(self, master, width=800, height=600):
        self.master = master
        self.width = width
        self.height = height

        # Cria o canvas e o objeto PhotoImage para desenhar pixel a pixel.
        self.canvas = tk.Canvas(master, width=self.width, height=self.height)
        self.canvas.pack()
        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas.create_image((self.width // 2, self.height // 2), image=self.photo, state="normal")

        # Define os arquivos de entrada
        self.mesh_file = "mesh.txt"
        self.camera_file = "camera.txt"
        self.lighting_file = "lighting.txt"

        # Carrega os arquivos e renderiza a cena
        self.load_files()
        self.render()

        # Associa o evento de tecla para recarregar os parâmetros (tecla 'r')
        master.bind("<Key>", self.on_key)

    def load_files(self):
        """
        Carrega a malha 3D, os parâmetros da câmera e os parâmetros de iluminação.
        Também calcula os normais dos vértices da malha.
        """
        self.vertices, self.triangles = load_mesh(self.mesh_file)
        self.camera = load_camera(self.camera_file)
        self.lighting = load_lighting(self.lighting_file)
        self.normals = compute_vertex_normals(self.vertices, self.triangles)

    def clear_screen(self):
        """
        Limpa a tela, preenchendo todos os pixels com a cor preta.
        """
        for x in range(self.width):
            for y in range(self.height):
                draw_pixel(self.photo, x, y, (0, 0, 0))

    def render(self):
        """
        Executa o pipeline de renderização:
          1. Transforma os vértices do mundo para o sistema de view.
          2. Transforma os normais.
          3. Aplica a projeção em perspectiva e mapeia para coordenadas de tela.
          4. Inicializa o z-buffer.
          5. Transforma a posição da luz para o sistema de view.
          6. Desenha a malha utilizando rasterização com z-buffer e iluminação Phong.
        """
        self.clear_screen()
        cam = self.camera  # Parâmetros da câmera: N, V, d, hx, hy, C
        # Transforma os vértices para o sistema de view
        vertices_view, cam_basis = world_to_view(self.vertices, cam)
        # Transforma os normais para o sistema de view usando a mesma base da câmera
        normals_view = transform_normals(self.normals, cam_basis)
        # Aplica a projeção em perspectiva
        proj = perspective_projection(vertices_view, cam['d'])
        # Converte as coordenadas projetadas para normalizadas
        norm_coords = to_normalized(proj, cam['hx'], cam['hy'])
        # Mapeia as coordenadas normalizadas para coordenadas de tela
        vertices_screen = to_screen(norm_coords, self.width, self.height)

        # Inicializa o z-buffer com valores grandes
        z_buffer = [[1e9 for _ in range(self.width)] for _ in range(self.height)]
        
        # Configura os parâmetros de iluminação
        lighting = self.lighting
        # Transforma a posição da luz para o sistema de view
        C = cam['C']
        Pl_world = lighting['Pl']
        Pl_rel = vec_sub(Pl_world, C)
        u, v, n = cam_basis
        Pl_view = [dot(Pl_rel, u), dot(Pl_rel, v), dot(Pl_rel, n)]
        
        # Desenha a malha com z-buffer e iluminação Phong
        draw_mesh(self.photo, z_buffer, vertices_screen, vertices_view, normals_view,
                  self.triangles, lighting, Pl_view)
        self.master.update_idletasks()

    def on_key(self, event):
        """
        Trata eventos de tecla.
        
        Se a tecla 'r' for pressionada, recarrega os arquivos de parâmetros e redesenha a cena.
        """
        if event.char.lower() == 'r':
            self.load_files()
            self.render()
            print("Parâmetros recarregados e objeto redesenhado.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Renderização 3D com Iluminação de Phong e Z-Buffer")
    app = App(root)
    root.mainloop()
