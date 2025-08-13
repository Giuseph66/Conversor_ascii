 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Pixels - Verifica cada pixel da imagem
Mostra se o pixel tem cor, é branco ou transparente
"""

import cv2
import numpy as np
import os
import sys

def analyze_pixel_color(r, g, b, a=None):
    """
    Analisa um pixel e retorna sua classificação
    Retorna: 'colorido', 'branco', 'transparente'
    """
    # Verificar transparência (se alpha disponível)
    if a is not None:
        if a < 128:  # Alpha muito baixo = transparente
            return 'transparente'
    
    # Verificar se é branco (RGB muito alto)
    if r > 240 and g > 240 and b > 240:
        return 'branco'
    
    # Verificar se tem cor significativa
    # Calcular diferença entre os canais RGB
    rgb_diff = max(r, g, b) - min(r, g, b)
    
    if rgb_diff > 30:  # Diferença significativa entre canais = tem cor
        return 'colorido'
    elif r > 200 and g > 200 and b > 200:  # Quase branco
        return 'branco'
    else:
        return 'colorido'  # Qualquer outra coisa é considerada colorida

def show_image_in_terminal(image_path, max_width=80, max_height=40):
    """
    Mostra a imagem no terminal usando caracteres ASCII
    """
    print(f"\n🖼️ VISUALIZAÇÃO DA IMAGEM NO TERMINAL")
    print("=" * 60)
    
    # Carregar imagem
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print("❌ Erro ao carregar imagem")
        return
    
    # Obter dimensões
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) > 2 else 1
    
    print(f"📐 Imagem original: {width}x{height} pixels")
    print(f"🎨 Canais: {channels}")
    
    # Calcular escala para caber no terminal
    scale_x = max_width / width
    scale_y = max_height / height
    scale = min(scale_x, scale_y, 1.0)  # Não aumentar a imagem
    
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    print(f"📱 Escala: {scale:.2f} -> {new_width}x{new_height} caracteres")
    print("=" * 60)
    
    # Redimensionar imagem
    if scale < 1.0:
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        resized = image
    
    # Caracteres para representar diferentes intensidades
    # Do mais escuro (preto) ao mais claro (branco)
    ascii_chars = [' ', '.', ':', ';', 'o', 'O', '8', '@', '#']
    
    # Mostrar imagem no terminal
    for y in range(new_height):
        line = ""
        for x in range(new_width):
            if channels == 1:
                # Imagem em escala de cinza
                gray_value = resized[y, x]
                char_index = int((gray_value / 255) * (len(ascii_chars) - 1))
                line += ascii_chars[char_index]
            elif channels == 3:
                # Imagem RGB
                b, g, r = resized[y, x]
                gray_value = 0.299 * r + 0.587 * g + 0.114 * b  # Fórmula padrão
                char_index = int((gray_value / 255) * (len(ascii_chars) - 1))
                line += ascii_chars[char_index]
            elif channels == 4:
                # Imagem RGBA
                b, g, r, a = resized[y, x]
                if a < 128:  # Transparente
                    line += ' '
                else:
                    # Pixel visível - converter para escala de cinza
                    gray_value = 0.299 * r + 0.587 * g + 0.114 * b
                    char_index = int((gray_value / 255) * (len(ascii_chars) - 1))
                    line += ascii_chars[char_index]
        
        print(line)
    
    print("=" * 60)
    print("📊 LEGENDA:")
    print("' ' = Transparente")
    print("'.' = Muito escuro")
    print("':' = Escuro")
    print("';' = Médio-escuro")
    print("'o' = Médio")
    print("'O' = Médio-claro")
    print("'8' = Claro")
    print("'@' = Muito claro")
    print("'#' = Branco")
    
    # Mostrar estatísticas da visualização
    visible_pixels = sum(1 for y in range(new_height) for x in range(new_width) 
                        if channels != 4 or resized[y, x][3] >= 128)
    total_pixels = new_width * new_height
    
    print(f"\n📈 ESTATÍSTICAS DA VISUALIZAÇÃO:")
    print(f"Pixels visíveis: {visible_pixels:,} ({visible_pixels/total_pixels*100:.1f}%)")
    print(f"Pixels transparentes: {total_pixels - visible_pixels:,} ({(total_pixels - visible_pixels)/total_pixels*100:.1f}%)")

def show_ascii_conversion_preview(image_path, grid_width=16, grid_height=16):
    """
    Mostra como a imagem ficaria convertida para ASCII na grade especificada
    """
    print(f"\n🎯 PREVIEW DA CONVERSÃO ASCII ({grid_width}x{grid_height})")
    print("=" * 60)
    
    # Carregar e processar imagem
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print("❌ Erro ao carregar imagem")
        return
    
    # Redimensionar para o tamanho da grade
    resized = cv2.resize(image, (grid_width, grid_height), interpolation=cv2.INTER_AREA)
    
    # Converter para escala de cinza se necessário
    if len(resized.shape) == 3:
        if resized.shape[2] == 4:  # RGBA
            # Processar cada pixel considerando transparência
            gray = np.zeros((grid_height, grid_width), dtype=np.uint8)
            for y in range(grid_height):
                for x in range(grid_width):
                    b, g, r, a = resized[y, x]
                    if a >= 128:  # Pixel visível
                        gray[y, x] = int(0.299 * r + 0.587 * g + 0.114 * b)
                    else:  # Pixel transparente
                        gray[y, x] = 255  # Branco
        else:  # RGB
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized
    
    # Mostrar grade ASCII
    print(f"📐 Grade: {grid_width}x{grid_height}")
    print("=" * (grid_width + 2))
    
    colored_count = 0
    transparent_count = 0
    
    for y in range(grid_height):
        line = "|"
        for x in range(grid_width):
            pixel_value = gray[y, x]
            
            # Converter para ASCII
            if pixel_value > 240:  # Quase branco (transparente ou branco)
                line += "."
                transparent_count += 1
            else:  # Tem cor
                line += "#"
                colored_count += 1
        
        line += "|"
        print(line)
    
    print("=" * (grid_width + 2))
    print("📊 LEGENDA:")
    print("'.' = Branco/Transparente (espaço vazio)")
    print("'#' = Preto (pixel com cor)")
    print(f"Total: {grid_width * grid_height} pixels")
    print(f"Pixels coloridos: {colored_count} ({colored_count/(grid_width*grid_height)*100:.1f}%)")
    print(f"Pixels transparentes/brancos: {transparent_count} ({transparent_count/(grid_width*grid_height)*100:.1f}%)")

def analyze_image_pixels(image_path, show_details=True, show_terminal_preview=True):
    """
    Analisa todos os pixels de uma imagem
    """
    print(f"🔍 Analisando imagem: {image_path}")
    print("=" * 60)
    
    # Carregar imagem
    if not os.path.exists(image_path):
        print(f"❌ Erro: Arquivo não encontrado: {image_path}")
        return
    
    # Tentar carregar com OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        print(f"❌ Erro: Não foi possível carregar a imagem: {image_path}")
        return
    
    # Informações da imagem
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) > 2 else 1
    
    print(f"📐 Dimensões: {width}x{height} pixels")
    print(f"🎨 Canais: {channels}")
    
    if channels == 1:
        print("ℹ️  Imagem em escala de cinza")
    elif channels == 3:
        print("ℹ️  Imagem RGB")
    elif channels == 4:
        print("ℹ️  Imagem RGBA (com transparência)")
    
    print("=" * 60)
    
    # Contadores
    total_pixels = width * height
    colored_pixels = 0
    white_pixels = 0
    transparent_pixels = 0
    
    # Listas para armazenar posições
    colored_positions = []
    white_positions = []
    transparent_positions = []
    
    # Analisar cada pixel
    print("🔍 Analisando pixels...")
    
    for y in range(height):
        for x in range(width):
            if channels == 1:
                # Imagem em escala de cinza
                gray_value = image[y, x]
                if gray_value > 240:
                    pixel_type = 'branco'
                    white_pixels += 1
                    white_positions.append((x,y))
                else:
                    pixel_type = 'colorido'
                    colored_pixels += 1
                    colored_positions.append((x,y))
                    
            elif channels == 3:
                # Imagem RGB
                b, g, r = image[y, x]  # OpenCV usa BGR
                pixel_type = analyze_pixel_color(r, g, b)
                
                if pixel_type == 'branco':
                    white_pixels += 1
                    white_positions.append((x,y))
                else:
                    colored_pixels += 1
                    colored_positions.append((x,y))
                    
            elif channels == 4:
                # Imagem RGBA
                b, g, r, a = image[y, x]  # OpenCV usa BGRA
                if a < 128:  # Transparente (alpha muito baixo)
                    pixel_type = 'transparente'
                    transparent_pixels += 1
                    transparent_positions.append((x,y))
                else:  # Pixel visível (alpha >= 128)
                    pixel_type = 'colorido'
                    colored_pixels += 1
                    colored_positions.append((x,y))
            
            # Mostrar detalhes do pixel (opcional)
            if show_details and (x < 10 or y < 10):  # Mostrar apenas primeiros pixels
                print(f"Pixel ({x},{y}): {pixel_type} - RGB: {r if 'r' in locals() else 'N/A'},{g if 'g' in locals() else 'N/A'},{b if 'b' in locals() else 'N/A'}{f', A: {a}' if 'a' in locals() else ''}")
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS FINAIS:")
    print(f"Total de pixels: {total_pixels:,}")
    print(f"Pixels coloridos: {colored_pixels:,} ({colored_pixels/total_pixels*100:.1f}%)")
    print(f"Pixels brancos: {white_pixels:,} ({white_pixels/total_pixels*100:.1f}%)")
    if channels == 4:
        print(f"Pixels transparentes: {transparent_pixels:,} ({transparent_pixels/total_pixels*100:.1f}%)")
    
    # Resumo para conversão ASCII
    print("\n🎯 RESUMO PARA CONVERSÃO ASCII:")
    print(f"Pixels para converter para preto (#): {colored_pixels:,}")
    print(f"Pixels para converter para branco (.): {white_pixels + transparent_pixels:,}")
    
    # Mostrar preview no terminal se solicitado
    if show_terminal_preview:
        show_image_in_terminal(image_path)
        show_ascii_conversion_preview(image_path, 16, 16)  # Preview 16x16
    
    return {
        'total': total_pixels,
        'colored': colored_pixels,
        'white': white_pixels,
        'transparent': transparent_pixels if channels == 4 else 0,
        'colored_positions': colored_positions,
        'white_positions': white_positions,
        'transparent_positions': transparent_positions if channels == 4 else []
    }

def analyze_specific_region(image_path, x1, y1, x2, y2):
    """
    Analisa uma região específica da imagem
    """
    print(f"🔍 Analisando região ({x1},{y1}) a ({x2},{y2})")
    print("=" * 40)
    
    # Carregar imagem
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print("❌ Erro ao carregar imagem")
        return
    
    # Verificar limites
    height, width = image.shape[:2]
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
        print("❌ Região fora dos limites da imagem")
        return
    
    # Analisar região
    region = image[y1:y2, x1:x2]
    region_height, region_width = region.shape[:2]
    channels = region.shape[2] if len(region.shape) > 2 else 1
    
    print(f"📐 Região: {region_width}x{region_height} pixels")
    print(f"🎨 Canais: {channels}")
    
    # Contadores para região
    colored = 0
    white = 0
    transparent = 0
    
    for y in range(region_height):
        for x in range(region_width):
            if channels == 1:
                gray_value = region[y, x]
                if gray_value > 240:
                    white += 1
                else:
                    colored += 1
            elif channels == 3:
                b, g, r = region[y, x]
                pixel_type = analyze_pixel_color(r, g, b)
                if pixel_type == 'branco':
                    white += 1
                else:
                    colored += 1
            elif channels == 4:
                b, g, r, a = region[y, x]
                if a < 128:  # Transparente
                    transparent += 1
                else:  # Pixel visível
                    colored += 1
    
    total_region = region_width * region_height
    
    print(f"\n📊 ESTATÍSTICAS DA REGIÃO:")
    print(f"Total: {total_region:,}")
    print(f"Coloridos: {colored:,} ({colored/total_region*100:.1f}%)")
    print(f"Brancos: {white:,} ({white/total_region*100:.1f}%)")
    if channels == 4:
        print(f"Transparentes: {transparent:,} ({transparent/total_region*100:.1f}%)")

def main():
    """
    Função principal
    """
    if len(sys.argv) < 2:
        print("📖 USO:")
        print("python3 pixel_analyzer.py <caminho_da_imagem> [opções]")
        print("\n🔧 OPÇÕES:")
        print("--details     : Mostra detalhes de cada pixel")
        print("--no-preview  : Não mostra preview no terminal")
        print("--region x1 y1 x2 y2 : Analisa região específica")
        print("--grid WxH    : Especifica tamanho da grade para preview")
        print("\n📝 EXEMPLOS:")
        print("python3 pixel_analyzer.py wifi.png")
        print("python3 pixel_analyzer.py wifi.png --details")
        print("python3 pixel_analyzer.py wifi.png --no-preview")
        print("python3 pixel_analyzer.py wifi.png --grid 32x32")
        print("python3 pixel_analyzer.py wifi.png --region 0 0 16 16")
        return
    
    image_path = sys.argv[1]
    show_details = '--details' in sys.argv
    show_preview = '--no-preview' not in sys.argv
    
    # Verificar se é análise de região
    if '--region' in sys.argv:
        try:
            region_index = sys.argv.index('--region')
            if len(sys.argv) >= region_index + 5:
                x1, y1, x2, y2 = map(int, sys.argv[region_index+1:region_index+5])
                analyze_specific_region(image_path, x1, y1, x2, y2)
            else:
                print("❌ Erro: Coordenadas da região não fornecidas")
        except ValueError:
            print("❌ Erro: Coordenadas da região devem ser números inteiros")
        return
    
    # Verificar tamanho da grade para preview
    grid_width, grid_height = 16, 16  # Padrão
    if '--grid' in sys.argv:
        try:
            grid_index = sys.argv.index('--grid')
            if len(sys.argv) > grid_index + 1:
                grid_str = sys.argv[grid_index + 1]
                if 'x' in grid_str:
                    grid_width, grid_height = map(int, grid_str.split('x'))
                else:
                    grid_width = grid_height = int(grid_str)
        except ValueError:
            print("❌ Erro: Formato da grade deve ser WxH (ex: 16x16)")
    
    # Análise completa da imagem
    try:
        resultado = analyze_image_pixels(image_path, show_details, show_preview)
        
        # Se preview está ativado, mostrar também com grade personalizada
        if show_preview:
            show_ascii_conversion_preview(image_path, grid_width, grid_height)
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()