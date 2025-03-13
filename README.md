# Renderização 3D com Iluminação de Phong e Z-Buffer

Este repositório contém uma aplicação em Python para renderizar um objeto 3D utilizando o modelo de iluminação de Phong e o algoritmo de visibilidade baseado em z-buffer. Todas as operações (transformações, projeção, rasterização, iluminação, etc.) são implementadas de forma manual, e a exibição dos pixels na tela é feita por meio do Tkinter (usando a função `PhotoImage.put`).

O projeto é requisito para a 2a Avaliação da Disciplina Computação Gráfica Básica, do curso de Bacharelado em Ciência da Computação, da UFRPE, ministrado pelos professores João Lima e Lucas Figueiredo
---

## Arquivos do Projeto

- **main_phong.py**  
  Arquivo principal que executa todo o pipeline de renderização:  
  1. Carrega a malha 3D a partir de um arquivo (`mesh.txt`).  
  2. Carrega os parâmetros de câmera a partir de outro arquivo (`camera.txt`).  
  3. Carrega os parâmetros de iluminação do arquivo (`lighting.txt`).  
  4. Calcula as normais dos vértices da malha.  
  5. Transforma os vértices para o sistema de vista, aplica projeção em perspectiva e converte para coordenadas de tela.  
  6. Inicializa o z-buffer.  
  7. Aplica o modelo de iluminação de Phong durante a rasterização de cada triângulo, resolvendo a visibilidade com z-buffer.  
  8. Desenha o objeto na janela do Tkinter, onde cada pixel é definido por meio da função `draw_pixel`.

  A tecla **r** pode ser pressionada a qualquer momento para recarregar os arquivos de parâmetros e redesenhar o objeto sem precisar fechar a aplicação.

- **mesh.txt**  
  Define os vértices e triângulos do objeto 3D. No formato:

<número de vértices>
<número de triângulos> <x1> <y1> <z1> <x2> <y2> <z2> 
... 
<xn> <yn> <zn> <i1> <i2> <i3> 
...

Observação: Os índices de cada triângulo são 1-indexados e são convertidos internamente para 0-indexados.

- **camera.txt**  
Contém 6 linhas que definem os parâmetros da câmera, seguindo a ordem:
1. Vetor N (ex.: `0 1 -1`)  
2. Vetor V (ex.: `0 -1 -1`)  
3. Escalar d (ex.: `5`)  
4. Escalar hx (ex.: `2`)  
5. Escalar hy (ex.: `2`)  
6. Ponto C (ex.: `0 -500 500`)  

Esses parâmetros permitem configurar o sistema de vista e a projeção em perspectiva.

- **lighting.txt**  
Define os parâmetros de iluminação para o modelo de Phong, com 8 linhas. Cada linha pode ou não conter um rótulo (como `Iamb = 100 100 100` ou simplesmente `100 100 100`). A ordem é:
1. Iamb – Cor ambiente (ex.: `100 100 100`)  
2. Ka – Coeficiente ambiente (ex.: `0.2`)  
3. Il – Intensidade da luz (ex.: `127 213 254`)  
4. Pl – Ponto de luz (ex.: `60 5 -10`)  
5. Kd – Coeficiente difuso (ex.: `0.5 0.3 0.2`)  
6. Od – Cor difusa do objeto (ex.: `0.7 0.5 0.8`)  
7. Ks – Coeficiente especular (ex.: `0.5`)  
8. η – Expoente especular (ex.: `1`)

---

## Requisitos

- **Python 3** instalado.  
- **Tkinter**, que faz parte da biblioteca padrão do Python em distribuições comuns (no Linux, verifique se o pacote `python3-tk` está instalado).

---

## Como Executar

1. **Coloque os Arquivos Juntos**  
 Certifique-se de que `main_phong.py`, `mesh.txt`, `camera.txt` e `lighting.txt` estejam todos no mesmo diretório.

2. **Abra o Terminal**  
 Navegue até o diretório onde estão os arquivos.

3. **Execute o Script**  
 ```bash
 python main_phong.py
```
Uma janela do Tkinter será aberta, exibindo a cena 3D renderizada.

##Interação

Pressione r para recarregar os arquivos de parâmetros e redesenhar o objeto sem precisar fechar a aplicação.

## Funcionamento Interno

### Carregamento de Dados
- **mesh.txt**: Lê e armazena os vértices e triângulos do objeto.  
- **camera.txt**: Ajusta o sistema de vista (vetores N e V, distância d, escalas hx/hy, ponto C).  
- **lighting.txt**: Configura os parâmetros de iluminação de Phong (ambiente, difuso, especular).

### Transformações
Os vértices são convertidos do sistema mundial para o sistema de vista (usando o ponto e vetores da câmera) e, em seguida, projetados em perspectiva para coordenadas de tela, mantendo a profundidade (z) para uso no z-buffer.

### Z-Buffer
É utilizado para resolver a visibilidade. Cada pixel tem um valor de profundidade inicial bem grande (1e9). Quando um triângulo é rasterizado, se o pixel atual estiver mais próximo que o valor no z-buffer, a cor é atualizada e o z-buffer é escrito com essa nova profundidade.

### Iluminação de Phong
Para cada pixel, a cor é calculada combinando componentes ambiente, difusa e especular. O código interpola os vetores normais dos vértices (calculados como médias das normais de cada face) e utiliza as coordenadas baricêntricas para a interpolação dentro de cada triângulo.

---

## Observações Finais
O projeto ilustra como montar um pipeline básico de renderização 3D em Python, com tudo feito "na mão":

- **Transformações**  
- **Projeção em Perspectiva**  
- **Algoritmo de Varredura (scan-line)**  
- **Z-buffer para Visibilidade**  
- **Cálculo de Iluminação de Phong**

O uso exclusivo da função de desenhar pixel (via `PhotoImage.put`) e operações matemáticas próprias satisfaz requisitos de evitar bibliotecas gráficas externas além de Tkinter.

Sinta-se à vontade para adaptar e estender este projeto conforme suas necessidades!
