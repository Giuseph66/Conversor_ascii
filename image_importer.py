#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Importação de Imagem para Conversor ASCII
Converte imagens para se encaixar no painel de desenho 8x8, 16x16, etc.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import os
from pixel_analyzer import analyze_image_pixels

class ImageImporter:
    def __init__(self, parent_gui):
        """
        Inicializa o importador de imagem
        parent_gui: Referência para a GUI principal
        """
        self.parent_gui = parent_gui
        self.original_image = None
        self.processed_image = None
        self.image_path = None
        
        # Canvas de prévia (será configurado quando a janela for criada)
        self.preview_canvas = None
        self.original_preview_canvas = None 
    def import_image(self):
        """Abre diálogo para selecionar e importar uma imagem"""
        try:
            # Abrir diálogo de seleção de arquivo
            file_path = filedialog.askopenfilename(
                title="Selecionar Imagem",
                filetypes=[
                    ("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("BMP", "*.bmp"),
                    ("GIF", "*.gif"),
                    ("TIFF", "*.tiff"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if file_path:
                self.image_path = file_path
                self.load_and_process_image()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar imagem: {str(e)}")
            
    def load_and_process_image(self):
        """Carrega e processa a imagem selecionada"""
        try:
            # Carregar imagem com OpenCV
            self.original_image = cv2.imread(self.image_path)
            self.imagem_processada = analyze_image_pixels(self.image_path, show_details=False, show_terminal_preview=False)
            # Verificar se a imagem foi carregada
            if self.original_image is None:
                raise Exception("Não foi possível carregar a imagem")
            
            # Converter BGR para RGB (OpenCV usa BGR por padrão)
            if len(self.original_image.shape) == 3:  # Se for colorida
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                
            # Mostrar prévia e opções de processamento
            self.show_import_dialog()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {str(e)}")
            
    def show_import_dialog(self):
        """Mostra diálogo com opções de importação"""
        # Criar janela de diálogo
        dialog = tk.Toplevel()
        dialog.title("Importar Imagem")
        dialog.geometry("1000x800")  # Tamanho inicial otimizado
        dialog.resizable(True, True)  # Permitir redimensionamento
        dialog.transient(self.parent_gui.root)
        dialog.grab_set()
        
        # Permitir maximizar
        try:
            dialog.state('zoomed')  # Windows
        except:
            try:
                dialog.attributes('-zoomed', True)  # Linux
            except:
                pass
        
        # Centralizar na tela (opcional, já que será maximizada)
        dialog.geometry("+%d+%d" % (
            self.parent_gui.root.winfo_rootx() + 50,
            self.parent_gui.root.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="15")  # Padding reduzido
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Armazenar referência para o preview ASCII
        self.dialog_main_frame = main_frame
        
        # Configurar grid weights para expansão
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Prévia expande
        
        # Título (mais compacto)
        ttk.Label(main_frame, text="Importar Imagem").grid(
            row=0, column=0, columnspan=2, pady=(0, 20)  # Reduzido padding
        )
        
        # Informações da imagem (mais compacto)
        info_frame = ttk.LabelFrame(main_frame, text="📊 Informações da Imagem", padding="10")  # Padding reduzido
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))  # Reduzido padding
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        
        # Frame esquerdo - Informações textuais
        info_left_frame = ttk.Frame(info_frame)
        info_left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Nome do arquivo
        filename = os.path.basename(self.image_path)
        ttk.Label(info_left_frame, text=f"📁 Arquivo: {filename}").grid(row=0, column=0, sticky=tk.W)
        
        # Dimensões originais
        width, height = self.original_image.shape[:2]
        ttk.Label(info_left_frame, text=f"📐 Dimensões: {width}x{height} pixels").grid(row=1, column=0, sticky=tk.W)
        
        # Tamanho da grade de destino
        target_size = f"{self.parent_gui.grid_width}x{self.parent_gui.grid_height}"
        ttk.Label(info_left_frame, text=f"🎯 Grade de destino: {target_size}").grid(row=2, column=0, sticky=tk.W)
        
        # Estatísticas da análise pixel a pixel (mais compacto)
        if hasattr(self, 'imagem_processada') and self.imagem_processada:
            stats = self.imagem_processada
            ttk.Label(info_left_frame, text="").grid(row=3, column=0, sticky=tk.W)  # Espaçamento
            ttk.Label(info_left_frame, text="🔍 Análise:").grid(row=4, column=0, sticky=tk.W, pady=(5, 2))  # Reduzido padding
            ttk.Label(info_left_frame, text=f"• Coloridos: {stats.get('colored', 0):,}").grid(row=5, column=0, sticky=tk.W, padx=(15, 0))  # Reduzido padding
            ttk.Label(info_left_frame, text=f"• Brancos: {stats.get('white', 0):,}").grid(row=6, column=0, sticky=tk.W, padx=(15, 0))
            if stats.get('transparent', 0) > 0:
                ttk.Label(info_left_frame, text=f"• Transparentes: {stats.get('transparent', 0):,}").grid(row=7, column=0, sticky=tk.W, padx=(15, 0))
            ttk.Label(info_left_frame, text=f"• Total: {stats.get('total', 0):,} pixels").grid(row=8, column=0, sticky=tk.W, padx=(15, 0))
        
        # Configurar grid weights para o frame de informações
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        
        # Controles de processamento (mais compacto)
        control_frame = ttk.LabelFrame(main_frame, text="⚙️ Processamento", padding="10")  # Padding reduzido
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))  # Reduzido padding
        control_frame.columnconfigure(0, weight=1)
        
        # Explicação da conversão (mais compacto)
        ttk.Label(control_frame, text="🎯 Conversão Inteligente:").grid(row=0, column=0, sticky=tk.W, pady=(0, 8))  # Reduzido padding
        ttk.Label(control_frame, text="• Pixels com cor → Preto (#)").grid(row=1, column=0, sticky=tk.W, padx=(15, 0))
        ttk.Label(control_frame, text="• Pixels transparentes/brancos → Branco (.)").grid(row=2, column=0, sticky=tk.W, padx=(15, 0))
        ttk.Label(control_frame, text="• Mapeamento preciso usando análise pixel a pixel").grid(row=3, column=0, sticky=tk.W, padx=(15, 0))
        
        # Estatísticas de conversão (mais compacto)
        if hasattr(self, 'imagem_processada') and self.imagem_processada:
            stats = self.imagem_processada
            conversion_stats = ttk.LabelFrame(control_frame, text="📈 Estatísticas de Conversão", padding="8")  # Padding reduzido
            conversion_stats.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))  # Reduzido padding
            conversion_stats.columnconfigure(0, weight=1)
            
            # Calcular estatísticas para a grade de destino
            target_pixels = self.parent_gui.grid_width * self.parent_gui.grid_height
            colored_ratio = stats.get('colored', 0) / stats.get('total', 1)
            estimated_colored = int(colored_ratio * target_pixels)
            estimated_white = target_pixels - estimated_colored
            
            ttk.Label(conversion_stats, text=f"Grade {target_size}: {target_pixels} pixels").grid(row=0, column=0, sticky=tk.W)
            ttk.Label(conversion_stats, text=f"Estimativa de pixels pretos (#): {estimated_colored}").grid(row=1, column=0, sticky=tk.W, padx=(15, 0))
            ttk.Label(conversion_stats, text=f"Estimativa de pixels brancos (.): {estimated_white}").grid(row=2, column=0, sticky=tk.W, padx=(15, 0))
            ttk.Label(conversion_stats, text=f"Taxa de preenchimento: {colored_ratio*100:.1f}%").grid(row=3, column=0, sticky=tk.W, padx=(15, 0))
        
        # Frame para prévia (mais compacto)
        preview_frame = ttk.LabelFrame(main_frame, text=f"🖼️ Prévia da Imagem Processada {self.parent_gui.grid_width}x{self.parent_gui.grid_height}", padding="10")  # Padding reduzido
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))  # Reduzido padding
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Canvas para prévia (menor para caber melhor)
        self.preview_canvas = tk.Canvas(preview_frame, width=500, height=300, bg='white')  # Canvas menor
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para preview ASCII (mais compacto)
        ascii_preview_frame = ttk.LabelFrame(main_frame, text="🔤 Preview ASCII", padding="10")  # Padding reduzido
        ascii_preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))  # Reduzido padding
        ascii_preview_frame.columnconfigure(0, weight=1)
        
        # Centralizar o título do frame
        ascii_preview_frame.configure(text="🔤 Preview ASCII da Conversão")
        
        # Mostrar preview ASCII neste frame
        self.show_ascii_preview_in_frame(ascii_preview_frame)
        
        # Botões (mais compacto)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 15))  # Reduzido padding
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="❌ Cancelar", command=dialog.destroy).grid(row=0, column=0, padx=10, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="✅ Importar", command=lambda: self.apply_import(dialog)).grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E))
        
        # Gerar prévia inicial
        self.update_preview()
        
        # Mostrar prévia da imagem original
        self.show_original_preview()
        
    def show_original_preview(self):
        """Mostra a prévia da imagem original no canvas de informações"""
        try:
            if not self.original_preview_canvas:
                return
                
            # Redimensionar imagem original para o canvas de prévia
            preview_size = (120, 80)  # Reduzido para caber melhor
            preview_img = cv2.resize(self.original_image, preview_size, interpolation=cv2.INTER_AREA)
            
            # Converter para formato compatível com PhotoImage
            if len(preview_img.shape) == 3:  # Se for colorida
                preview_img_rgb = cv2.cvtColor(preview_img, cv2.COLOR_RGB2BGR)
            else:
                preview_img_rgb = cv2.cvtColor(preview_img, cv2.COLOR_GRAY2BGR)
                
            # Converter para PhotoImage
            photo = tk.PhotoImage(data=cv2.imencode('.ppm', preview_img_rgb)[1].tobytes())
            
            # Atualizar canvas
            self.original_preview_canvas.delete("all")
            self.original_preview_canvas.create_image(60, 40, image=photo)  # Centralizado no canvas menor
            self.original_preview_canvas.image = photo  # Manter referência
            
        except Exception as e:
            if self.original_preview_canvas:
                self.original_preview_canvas.delete("all")
                self.original_preview_canvas.create_text(60, 40, text=f"Erro: {str(e)}", fill="red")
        
    def update_preview(self):
        """Atualiza a prévia da imagem processada"""
        # Verificar se o canvas existe
        if not self.preview_canvas:
            return
            
        try:
            # Processar imagem com configurações atuais
            processed = self.process_image()
            
            # Redimensionar para prévia (usar todo o espaço disponível)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Se o canvas ainda não foi renderizado, usar tamanho padrão
            if canvas_width <= 1:
                canvas_width = 500
            if canvas_height <= 1:
                canvas_height = 300
                
            preview_size = (canvas_width, canvas_height)
            preview_img = cv2.resize(processed, preview_size, interpolation=cv2.INTER_AREA)
            
            # Converter para formato compatível com PhotoImage
            # Como processed é um array de valores únicos (0 ou 255), converter para BGR
            preview_img_bgr = cv2.cvtColor(preview_img, cv2.COLOR_GRAY2BGR)
                
            # Converter para PhotoImage
            photo = tk.PhotoImage(data=cv2.imencode('.ppm', preview_img_bgr)[1].tobytes())
            
            # Atualizar canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.preview_canvas.image = photo  # Manter referência
            
        except Exception as e:
            if self.preview_canvas:
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(250, 150, text=f"Erro: {str(e)}", fill="red")
            
    def process_image(self):
        """Processa a imagem com as configurações atuais usando análise pixel a pixel"""
        try:
            # Usar os dados já analisados pelo pixel_analyzer
            if not hasattr(self, 'imagem_processada') or self.imagem_processada is None:
                # Fallback: analisar novamente se necessário
                self.imagem_processada = analyze_image_pixels(
                    self.image_path, 
                    show_details=False, 
                    show_terminal_preview=False
                )
            
            # Obter dimensões da grade de destino
            target_width = self.parent_gui.grid_width
            target_height = self.parent_gui.grid_height
            
            # Criar array de resultado (0 = branco, 255 = preto)
            result_array = np.zeros((target_height, target_width), dtype=np.uint8)
            
            # Se temos dados analisados, usar para conversão inteligente
            if self.imagem_processada and 'colored_positions' in self.imagem_processada:
                # Usar as posições dos pixels coloridos para mapeamento preciso
                colored_positions = self.imagem_processada.get('colored_positions', [])
                white_positions = self.imagem_processada.get('white_positions', [])
                transparent_positions = self.imagem_processada.get('transparent_positions', [])
                
                # Obter dimensões da imagem original
                original_height, original_width = self.original_image.shape[:2]
                
                # Mapear cada pixel da grade de destino
                for grid_y in range(target_height):
                    for grid_x in range(target_width):
                        # Calcular posição correspondente na imagem original
                        orig_x = int((grid_x + 0.5) * original_width / target_width)
                        orig_y = int((grid_y + 0.5) * original_height / target_height)
                        
                        # Verificar se esta posição tem pixel colorido
                        if (orig_x, orig_y) in colored_positions:
                            result_array[grid_y, grid_x] = 255  # Preto
                        else:
                            result_array[grid_y, grid_x] = 0    # Branco
                            
            else:
                # Fallback: método anterior de conversão
                # Redimensionar para o tamanho da grade
                target_size = (target_width, target_height)
                resized = cv2.resize(self.original_image, target_size, interpolation=cv2.INTER_AREA)
                
                # Processar pixel a pixel com lógica corrigida
                height, width = resized.shape[:2]
                channels = resized.shape[2] if len(resized.shape) > 2 else 1
                
                for y in range(height):
                    for x in range(width):
                        if channels == 1:
                            # Imagem em escala de cinza
                            pixel_value = resized[y, x]
                            # Se é quase branco (> 240), fica branco (0), senão fica preto (255)
                            result_array[y, x] = 0 if pixel_value > 240 else 255
                            
                        elif channels == 3:
                            # Imagem RGB
                            b, g, r = resized[y, x]
                            # Converter para escala de cinza
                            gray_value = int(0.299 * r + 0.587 * g + 0.114 * b)
                            # Se é quase branco (> 240), fica branco (0), senão fica preto (255)
                            result_array[y, x] = 0 if gray_value > 240 else 255
                            
                        elif channels == 4:
                            # Imagem RGBA
                            b, g, r, a = resized[y, x]
                            if a < 128:  # Pixel transparente
                                result_array[y, x] = 0  # Branco
                            else:  # Pixel visível (alpha >= 128)
                                # Converter para escala de cinza
                                gray_value = int(0.299 * r + 0.587 * g + 0.114 * b)
                                # Se é quase branco (> 240), fica branco (0), senão fica preto (255)
                                result_array[y, x] = 0 if gray_value > 240 else 255
            
            # Retornar array de valores únicos (0 ou 255)
            return result_array
            
        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")
            
    def apply_import(self, dialog):
        """Aplica a imagem processada à grade de desenho"""
        try:
            # Processar imagem final
            processed = self.process_image()
            
            # Converter para formato da grade ('.' para branco, '#' para preto)
            # 0 = branco (deve virar '.'), 255 = preto (deve virar '#')
            self.parent_gui.grid_data = []
            for row in processed:
                grid_row = []
                for pixel in row:
                    # Se o pixel é 0 (branco), coloca '.' (branco na grade)
                    # Se o pixel é 255 (preto), coloca '#' (preto na grade)
                    grid_row.append('#' if pixel == 255 else '.')
                self.parent_gui.grid_data.append(grid_row)
                
            # Atualizar interface
            self.parent_gui.fill_cells()
            self.parent_gui.save_state()  # Salvar no histórico
            self.parent_gui.update_status()
            
            # Fechar diálogo
            dialog.destroy()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", "Imagem importada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar imagem: {str(e)}")

    def show_ascii_preview_in_frame(self, parent_frame):
        """Mostra um preview da conversão ASCII no frame especificado"""
        try:
            if not hasattr(self, 'imagem_processada') or not self.imagem_processada:
                # Mostrar mensagem de que não há dados para preview
                ttk.Label(parent_frame, text="⚠️ Carregando análise da imagem...").grid(row=0, column=0, sticky=tk.W)
                return
                
            # Mostrar grade ASCII pequena (máximo 20x20 para caber no diálogo)
            #max_display_size = self.parent_gui.grid_width
            display_width =self.parent_gui.grid_width
            display_height =self.parent_gui.grid_height
            
            # Calcular escala para mostrar
            scale_x = display_width / self.parent_gui.grid_width
            scale_y = display_height / self.parent_gui.grid_height
            scale = min(scale_x, scale_y)
            
            if scale < 1.0:
                # Redimensionar para mostrar
                target_size = (display_width, display_height)
                resized = cv2.resize(self.original_image, target_size, interpolation=cv2.INTER_AREA)
                
                # Converter para ASCII
                ascii_grid = []
                for y in range(display_height):
                    ascii_line = ""
                    for x in range(display_width):
                        if len(resized.shape) == 3:
                            if resized.shape[2] == 4:  # RGBA
                                b, g, r, a = resized[y, x]
                                if a < 128:  # Transparente
                                    ascii_line += " "
                                else:
                                    gray_value = int(0.299 * r + 0.587 * g + 0.114 * b)
                                    ascii_line += "#" if gray_value <= 240 else "."
                            else:  # RGB
                                b, g, r = resized[y, x]
                                gray_value = int(0.299 * r + 0.587 * g + 0.114 * b)
                                ascii_line += "#" if gray_value <= 240 else "."
                        else:  # Grayscale
                            pixel_value = resized[y, x]
                            ascii_line += "#" if pixel_value <= 240 else "."
                    ascii_grid.append(ascii_line)
                
                # Mostrar preview ASCII
                ttk.Label(parent_frame, text=f"Preview {display_width}x{display_height}:", 
                         anchor="center").grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
                
                # Canvas para preview ASCII (centralizado)
                ascii_canvas = tk.Canvas(parent_frame, width=display_width*8, height=display_height*8, 
                                       bg='white', relief='sunken', bd=1)
                ascii_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
                
                # Centralizar o canvas horizontalmente
                parent_frame.columnconfigure(0, weight=1)
                
                # Desenhar grade ASCII
                cell_size = 8
                for y, line in enumerate(ascii_grid):
                    for x, char in enumerate(line):
                        x_pos = x * cell_size
                        y_pos = y * cell_size
                        if char == "#":
                            ascii_canvas.create_rectangle(x_pos, y_pos, x_pos + cell_size, y_pos + cell_size, 
                                                        fill='black', outline='lightgray')
                        else:
                            ascii_canvas.create_rectangle(x_pos, y_pos, x_pos + cell_size, y_pos + cell_size, 
                                                        fill='white', outline='lightgray')
                
                # Legenda (centralizada)
                legend_frame = ttk.Frame(parent_frame)
                legend_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
                legend_frame.columnconfigure(0, weight=1)
                
                # Título da legenda centralizado
                ttk.Label(legend_frame, text="🔤 Legenda:", 
                         anchor="center").grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
                
                # Itens da legenda centralizados
                legend_items = [
                    "'#' = Preto (pixel com cor)",
                    "'.' = Branco (espaço vazio)",
                    "' ' = Transparente"
                ]
                
                for i, item in enumerate(legend_items):
                    ttk.Label(legend_frame, text=item, 
                             anchor="center").grid(row=i+1, column=0, sticky=(tk.W, tk.E), pady=2)
                
        except Exception as e:
            # Em caso de erro, mostrar mensagem
            ttk.Label(parent_frame, text=f"⚠️ Erro no preview ASCII: {str(e)}").grid(row=0, column=0, sticky=tk.W)

def create_import_button(parent_gui, button_frame, row, column):
    """Cria um botão de importação na interface principal"""
    import_btn = ttk.Button(button_frame, text="Importar Imagem", 
                           command=lambda: ImageImporter(parent_gui).import_image())
    import_btn.grid(row=row, column=column, padx=5, sticky=(tk.W, tk.E))
    return import_btn 