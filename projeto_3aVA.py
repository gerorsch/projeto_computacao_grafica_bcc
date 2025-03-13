import sys
import math
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# -------------------------------------------------------------------
# Variáveis globais de parâmetros e câmera
# -------------------------------------------------------------------
camera_pos = [0.0, -500.0, 500.0]
view_dir   = [0.0,  1.0,  -1.0]
up_vector  = [0.0, -1.0,  -1.0]

fovy         = 45.0
aspect_ratio = 1.0
near_plane   = 5.0
far_plane    = 10000.0

light_pos      = [0.0, 500.0, 200.0, 1.0]
light_ambient  = [0.4, 0.4, 0.4, 1.0]
light_diffuse  = [0.5, 0.85, 1.0, 1.0]
light_specular = [0.5, 0.85, 1.0, 1.0]

material_ambient   = [0.2, 0.2, 0.2, 1.0]
material_diffuse   = [0.7, 0.5, 0.8, 1.0]
material_specular  = [0.5, 0.5, 0.5, 1.0]
material_emissive  = [0.0, 0.0, 0.0, 1.0]
material_shininess = 100.0

# Lista global de objetos carregados.
# Cada item será um dicionário: {
#    "name": <nome do arquivo>,
#    "vertices": [...],
#    "faces": [...],
#    "normals": [...]
# }
loaded_objects = []

# Índice do objeto atual a ser renderizado
current_object_index = 0

# Variáveis para controle do mouse (rotação)
mouse_left_down = False
mouse_last_x = 0
mouse_last_y = 0

# -------------------------------------------------------------------
# Funções de carregamento de parâmetros e objetos
# -------------------------------------------------------------------
def load_parameters(filename):
    """
    Lê os parâmetros de câmera e iluminação a partir do arquivo de texto.
    Exemplo de formato (params.txt):
        C = 0 -500 500
        N = 0 1 -1
        V = 0 -1 -1
        fovy = 45
        aspect = 1.3333
        near = 5
        far = 10000
        Pl = 0 500 200
        light_ambient = 0.4 0.4 0.4 1.0
        light_diffuse = 0.5 0.85 1.0 1.0
        light_specular = 0.5 0.85 1.0 1.0
        material_ambient = 0.2 0.2 0.2 1.0
        ...
    """
    global camera_pos, view_dir, up_vector
    global fovy, aspect_ratio, near_plane, far_plane
    global light_pos, light_ambient, light_diffuse, light_specular
    global material_ambient, material_diffuse, material_specular, material_emissive, material_shininess

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    parts = value.replace(',', ' ').split()
                    # Tenta converter cada parte em float
                    parts = [float(x) for x in parts if x.strip()]
                    
                    if key == 'c':
                        camera_pos = parts
                    elif key == 'n':
                        view_dir = parts
                    elif key == 'v':
                        up_vector = parts
                    elif key == 'fovy':
                        fovy = parts[0]
                    elif key == 'aspect':
                        aspect_ratio = parts[0]
                    elif key == 'near':
                        near_plane = parts[0]
                    elif key == 'far':
                        far_plane = parts[0]
                    elif key in ['pl', 'ponto pl']:
                        # Coordenada homogênea (w=1.0) para luz pontual
                        light_pos = parts + [1.0] if len(parts) == 3 else parts
                    elif key in ['light_ambient', 'cor ambiental da luz']:
                        light_ambient = parts
                    elif key in ['light_diffuse', 'cor difusa da luz']:
                        light_diffuse = parts
                    elif key in ['light_specular', 'cor especular da luz']:
                        light_specular = parts
                    elif key in ['material_ambient', 'cor ambiental do material']:
                        material_ambient = parts
                    elif key in ['material_diffuse', 'cor difusa do material']:
                        material_diffuse = parts
                    elif key in ['material_specular', 'cor especular do material']:
                        material_specular = parts
                    elif key in ['material_emissive', 'cor emissiva do material']:
                        material_emissive = parts
                    elif key in ['eta', 'η', 'shininess']:
                        material_shininess = parts[0]
    except Exception as e:
        print("Erro ao carregar parâmetros:", e)

def load_single_object(filepath):
    """
    Carrega um objeto 3D no formato BYU a partir de um arquivo.
    Retorna um dicionário com 'vertices', 'faces' e 'normals' (inicialmente vazio).
    
    Formato BYU esperado:
      - Primeira linha: num_vertices num_faces num_boundaries
      - Próximas num_vertices linhas: cada linha com as coordenadas x y z (floats)
      - Em seguida, as faces: índices de vértices (base 1) terminados por -1.
    """
    obj_data = {
        'vertices': [],
        'faces': [],
        'normals': []
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) < 1:
            return None

        # Cabeçalho
        header = lines[0].split()
        if len(header) < 2:
            print(f"Formato inválido em {filepath}")
            return None

        num_vertices = int(header[0])
        num_faces = int(header[1])
        # Se houver um terceiro valor, num_boundaries = int(header[2])

        # Lê vértices
        start_line = 1
        for i in range(num_vertices):
            parts = lines[start_line + i].split()
            v = [float(p) for p in parts]
            obj_data['vertices'].append(v)
        start_line += num_vertices

        # Lê faces
        face_indices = []
        for line in lines[start_line:]:
            parts = line.split()
            for p in parts:
                idx = int(p)
                if idx == -1:
                    if face_indices:
                        face = [fi - 1 for fi in face_indices]  # converte para índice base 0
                        obj_data['faces'].append(face)
                        face_indices = []
                else:
                    face_indices.append(idx)
        # Se sobrou algo (caso não tenha -1 na última face)
        if face_indices:
            face = [fi - 1 for fi in face_indices]
            obj_data['faces'].append(face)

    return obj_data

def compute_normals(obj_data):
    """
    Calcula as normais para cada vértice do objeto, somando as normais
    de cada face adjacente (método Gouraud).
    """
    vertices = obj_data['vertices']
    faces = obj_data['faces']
    normals = [[0.0, 0.0, 0.0] for _ in range(len(vertices))]

    for face in faces:
        if len(face) < 3:
            continue
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]
        # Vetores da face
        edge1 = [v1[i] - v0[i] for i in range(3)]
        edge2 = [v2[i] - v0[i] for i in range(3)]
        # Produto vetorial -> normal da face
        normal = [
            edge1[1]*edge2[2] - edge1[2]*edge2[1],
            edge1[2]*edge2[0] - edge1[0]*edge2[2],
            edge1[0]*edge2[1] - edge1[1]*edge2[0]
        ]
        length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        if length != 0:
            normal = [n / length for n in normal]

        # Soma essa normal em cada vértice da face
        for idx in face:
            if 0 <= idx < len(normals):
                normals[idx] = [normals[idx][j] + normal[j] for j in range(3)]

    # Normaliza as normais
    for i in range(len(normals)):
        length = math.sqrt(sum([normals[i][j]**2 for j in range(3)]))
        if length != 0:
            normals[i] = [normals[i][j] / length for j in range(3)]
        else:
            normals[i] = [0.0, 0.0, 0.0]

    obj_data['normals'] = normals

def load_all_objects(folder):
    """
    Percorre a pasta 'folder', carrega todos os arquivos .byu encontrados
    e armazena cada objeto (com nome) na lista global 'loaded_objects'.
    """
    global loaded_objects
    loaded_objects = []

    if not os.path.isdir(folder):
        print(f"Pasta '{folder}' não encontrada.")
        return

    for filename in os.listdir(folder):
        if filename.lower().endswith('.byu'):
            full_path = os.path.join(folder, filename)
            try:
                obj_data = load_single_object(full_path)
                if obj_data:
                    compute_normals(obj_data)
                    loaded_objects.append({
                        "name": filename,
                        "vertices": obj_data['vertices'],
                        "faces": obj_data['faces'],
                        "normals": obj_data['normals']
                    })
                    print(f"Objeto '{filename}' carregado com sucesso. "
                          f"Vértices: {len(obj_data['vertices'])}, "
                          f"Faces: {len(obj_data['faces'])}")
            except Exception as e:
                print(f"Erro ao carregar {full_path}:", e)

# -------------------------------------------------------------------
# Funções de inicialização e callbacks de OpenGL
# -------------------------------------------------------------------
def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)  # Tonalização Gouraud
    glClearColor(0.0, 0.0, 0.0, 1.0)

def set_lighting():
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT,  light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glMaterialfv(GL_FRONT, GL_AMBIENT,   material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE,   material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR,  material_specular)
    glMaterialfv(GL_FRONT, GL_EMISSION,  material_emissive)
    glMaterialf(GL_FRONT,  GL_SHININESS, material_shininess)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Define a câmera com gluLookAt
    center = [camera_pos[i] + view_dir[i] for i in range(3)]
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              center[0], center[1], center[2],
              up_vector[0], up_vector[1], up_vector[2])

    set_lighting()

    # Se houver objetos carregados, renderiza apenas o 'current_object_index'
    if loaded_objects:
        global current_object_index
        # Garante que o índice esteja dentro do range
        if current_object_index < 0:
            current_object_index = 0
        if current_object_index >= len(loaded_objects):
            current_object_index = len(loaded_objects) - 1

        obj = loaded_objects[current_object_index]
        vertices = obj['vertices']
        faces    = obj['faces']
        normals  = obj['normals']

        # Desenha as faces (triangulação simples)
        glBegin(GL_TRIANGLES)
        for face in faces:
            if len(face) < 3:
                continue
            # Se a face tiver mais de 3 vértices, desenhamos em forma de "fan"
            for i in range(1, len(face) - 1):
                idx0 = face[0]
                idx1 = face[i]
                idx2 = face[i+1]
                # Vértice 0
                if idx0 < len(normals):
                    glNormal3fv(normals[idx0])
                glVertex3fv(vertices[idx0])
                # Vértice i
                if idx1 < len(normals):
                    glNormal3fv(normals[idx1])
                glVertex3fv(vertices[idx1])
                # Vértice i+1
                if idx2 < len(normals):
                    glNormal3fv(normals[idx2])
                glVertex3fv(vertices[idx2])
        glEnd()

    glutSwapBuffers()

def reshape(width, height):
    global aspect_ratio
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    aspect_ratio = float(width) / float(height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovy, aspect_ratio, near_plane, far_plane)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    """
    Teclas de movimento da câmera:
      W, A, S, D
    Tecla 'r' recarrega os parâmetros.
    Teclas 'n' e 'p' mudam o objeto sendo renderizado.
    ESC sai da aplicação.
    """
    global camera_pos, current_object_index
    step = 10.0

    # Vetor "right" = view_dir x up_vector (normalizado)
    right = [
        view_dir[1]*up_vector[2] - view_dir[2]*up_vector[1],
        view_dir[2]*up_vector[0] - view_dir[0]*up_vector[2],
        view_dir[0]*up_vector[1] - view_dir[1]*up_vector[0]
    ]
    r_length = math.sqrt(sum([r**2 for r in right]))
    if r_length != 0:
        right = [r / r_length for r in right]

    if key == b'w':
        camera_pos = [camera_pos[i] + view_dir[i]*step for i in range(3)]
    elif key == b's':
        camera_pos = [camera_pos[i] - view_dir[i]*step for i in range(3)]
    elif key == b'a':
        camera_pos = [camera_pos[i] - right[i]*step for i in range(3)]
    elif key == b'd':
        camera_pos = [camera_pos[i] + right[i]*step for i in range(3)]
    elif key == b'r':
        # Recarrega parâmetros do arquivo e redesenha
        load_parameters("params.txt")
    elif key == b'n':
        # Próximo objeto
        if loaded_objects:
            current_object_index = (current_object_index + 1) % len(loaded_objects)
    elif key == b'p':
        # Objeto anterior
        if loaded_objects:
            current_object_index = (current_object_index - 1) % len(loaded_objects)
    elif key == b'\x1b':  # ESC
        sys.exit()
    glutPostRedisplay()

def mouse(button, state, x, y):
    global mouse_left_down, mouse_last_x, mouse_last_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_left_down = True
            mouse_last_x = x
            mouse_last_y = y
        else:
            mouse_left_down = False

def motion(x, y):
    """
    Rotação da câmera ao arrastar com botão esquerdo do mouse pressionado.
    """
    global view_dir, mouse_last_x, mouse_last_y
    if mouse_left_down:
        dx = x - mouse_last_x
        dy = y - mouse_last_y
        angle_scale = 0.005

        # Rotação horizontal em torno do vetor 'up_vector'
        view_dir[:] = rotate_vector(view_dir, up_vector, dx * angle_scale)

        # Rotação vertical em torno do vetor 'right'
        right = [
            view_dir[1]*up_vector[2] - view_dir[2]*up_vector[1],
            view_dir[2]*up_vector[0] - view_dir[0]*up_vector[2],
            view_dir[0]*up_vector[1] - view_dir[1]*up_vector[0]
        ]
        view_dir[:] = rotate_vector(view_dir, right, -dy * angle_scale)

        mouse_last_x = x
        mouse_last_y = y
        glutPostRedisplay()

def rotate_vector(vec, axis, angle):
    """
    Rotaciona o vetor 'vec' em torno de 'axis' pelo ângulo 'angle' (fórmula de Rodrigues).
    Normaliza o resultado ao final.
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dot   = sum(vec[i]*axis[i] for i in range(3))
    cross = [
        axis[1]*vec[2] - axis[2]*vec[1],
        axis[2]*vec[0] - axis[0]*vec[2],
        axis[0]*vec[1] - axis[1]*vec[0]
    ]
    rotated = [
        vec[i]*cos_a + cross[i]*sin_a + axis[i]*dot*(1 - cos_a)
        for i in range(3)
    ]
    # Normaliza
    length = math.sqrt(sum(c*c for c in rotated))
    if length != 0:
        rotated = [c / length for c in rotated]
    return rotated

# -------------------------------------------------------------------
# Função principal
# -------------------------------------------------------------------
def main():
    # Carrega parâmetros da câmera e luz
    load_parameters("params.txt")
    # Carrega todos os objetos .byu da pasta 'objetos'
    load_all_objects("objetos")

    # Inicializa GLUT/OpenGL
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Renderizador de Objetos 3D (.byu) - Selecao")
    init()

    # Registra callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

    glutMainLoop()

if __name__ == "__main__":
    main()
