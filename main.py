import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.relativelayout import RelativeLayout
import random
from datetime import datetime
import os

Window.clearcolor = (0.95, 0.98, 1, 1)

class DrawingWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.line_width = 10
        self.current_color = (1, 0, 0, 1)
        self.mode = 'draw'
        self.bind(size=self.update_rect, pos=self.update_rect)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.mode == 'draw':
            with self.canvas:
                Color(*self.current_color)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if 'line' in touch.ud and self.mode == 'draw':
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

class PuzzlePiece(Scatter):
    def __init__(self, image_source, correct_pos, **kwargs):
        super().__init__(**kwargs)
        self.correct_pos = correct_pos
        self.do_rotation = False
        self.do_scale = False
        self.size_hint = (None, None)
        self.size = (180, 180)
        
        img = Image(source=image_source, size=self.size, allow_stretch=True)
        self.add_widget(img)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # Snap to correct position if close enough
            dx = abs(self.pos[0] - self.correct_pos[0])
            dy = abs(self.pos[1] - self.correct_pos[1])
            if dx < 50 and dy < 50:
                self.pos = self.correct_pos
                self.parent.check_puzzle_complete()
        return super().on_touch_up(touch)

class PuzzleArea(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pieces = []
        self.completed = False
    
    def load_puzzle(self, animal_name):
        self.clear_widgets()
        self.pieces = []
        self.completed = False
        
        # For demo, use placeholder images or colored rectangles if no real images
        piece_positions = [
            (100, 300), (300, 300), (500, 300),
            (100, 100), (300, 100), (500, 100)
        ]
        
        for i, pos in enumerate(piece_positions):
            # Use colored rectangle as placeholder (in real app, use cut images)
            color = (random.random(), random.random(), random.random(), 1)
            piece = PuzzlePiece('placeholder', pos, size=(180, 180))
            
            # Add colored background for demo
            with piece.canvas.before:
                Color(*color)
                Rectangle(pos=(0,0), size=piece.size)
            
            # Random initial position
            piece.pos = (random.randint(50, 600), random.randint(50, 400))
            self.add_widget(piece)
            self.pieces.append(piece)
    
    def check_puzzle_complete(self):
        if all(abs(p.pos[0] - p.correct_pos[0]) < 30 and abs(p.pos[1] - p.correct_pos[1]) < 30 for p in self.pieces):
            if not self.completed:
                self.completed = True
                # Success popup will be handled by parent

class KidsDrawPuzzleApp(App):
    def build(self):
        root = FloatLayout()
        self.drawing = DrawingWidget(size_hint=(0.65, 0.72), pos_hint={'center_x': 0.34, 'y': 0.20})
        root.add_widget(self.drawing)
        
        # Title
        title = Label(text='🎨 儿童绘图益智乐园 🧩', font_size=42, pos_hint={'center_x':0.5, 'y':0.92}, size_hint=(0.8, 0.1), color=(0.1,0.2,0.8,1), bold=True)
        root.add_widget(title)
        
        # Color palette
        colors = [(1,0,0,1),(1,0.65,0,1),(1,1,0,1),(0.2,0.8,0.2,1),(0,0.6,1,1),(0.5,0,1,1),(1,0,0.8,1),(0.3,0.3,0.3,1)]
        color_grid = GridLayout(cols=4, spacing=10, size_hint=(0.28, 0.32), pos_hint={'x': 0.72, 'y': 0.55})
        for col in colors:
            btn = Button(background_color=col, size_hint_y=None, height=60)
            btn.bind(on_press=lambda b, c=col: self.change_color(c))
            color_grid.add_widget(btn)
        root.add_widget(color_grid)
        
        # Tools
        tool_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.27, 0.40), pos_hint={'x':0.73, 'y':0.08})
        
        # Brush size
        self.size_label = Label(text='🖌 粗细: 10', size_hint_y=None, height=45, font_size=22)
        tool_box.add_widget(self.size_label)
        
        sizes = BoxLayout(spacing=6)
        for sz in [5,10,18,28,40]:
            b = Button(text=str(sz), background_color=(0.9,0.9,0.95,1), font_size=20)
            b.bind(on_press=lambda inst, s=sz: self.set_size(s))
            sizes.add_widget(b)
        tool_box.add_widget(sizes)
        
        # Other buttons
        for text, color, func in [
            ('🧼 橡皮擦', (0.95,0.95,0.6,1), self.eraser),
            ('🗑 清空画布', (1,0.5,0.5,1), self.clear_all),
            ('💾 保存作品', (0.4,0.85,0.4,1), self.save_to_gallery),
            ('🧩 开始拼图', (0.4,0.7,1,1), self.start_puzzle)
        ]:
            btn = Button(text=text, background_color=color, size_hint_y=None, height=68, font_size=24)
            btn.bind(on_press=func)
            tool_box.add_widget(btn)
        
        root.add_widget(tool_box)
        
        # Puzzle area (hidden initially)
        self.puzzle_area = PuzzleArea(size_hint=(0.65, 0.72), pos_hint={'center_x': 0.34, 'y': 0.20})
        self.puzzle_area.opacity = 0
        root.add_widget(self.puzzle_area)
        
        # Load sounds (placeholders)
        self.sounds = {}
        # Note: Add real mp3 files for full experience
        
        return root
    
    def change_color(self, color):
        self.drawing.current_color = color
        self.drawing.mode = 'draw'
        self.drawing.opacity = 1
        self.puzzle_area.opacity = 0
    
    def set_size(self, size):
        self.drawing.line_width = size
        self.size_label.text = f'🖌 粗细: {size}'
    
    def eraser(self, *args):
        self.drawing.current_color = (1,1,1,1)
    
    def clear_all(self, *args):
        self.drawing.canvas.clear()
        with self.drawing.canvas.before:
            Color(1,1,1,1)
            self.drawing.bg_rect = Rectangle(pos=self.drawing.pos, size=self.drawing.size)
    
    def save_to_gallery(self, *args):
        filename = f'kids_drawing_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        self.drawing.export_to_png(filename)
        content = Label(text=f'✅ 已保存到本地！\n{filename}\n\n(iPad打包后可集成plyer保存到相册)')
        popup = Popup(title='保存成功 🎉', content=content, size_hint=(0.7, 0.4))
        popup.open()
    
    def start_puzzle(self, *args):
        self.drawing.opacity = 0
        self.puzzle_area.opacity = 1
        self.puzzle_area.load_puzzle('可爱小猫')
        
        popup = Popup(title='🧩 真实拖拽拼图', 
                     content=Label(text='拖动拼图块到正确位置！\n靠近时会自动吸附~', font_size=26),
                     size_hint=(0.75, 0.4))
        popup.open()

if __name__ == '__main__':
    KidsDrawPuzzleApp().run()
