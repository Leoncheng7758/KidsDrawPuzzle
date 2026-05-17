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
import random
from datetime import datetime

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

class KidsDrawPuzzleApp(App):
    def build(self):
        root = FloatLayout()
        self.drawing = DrawingWidget(size_hint=(0.68, 0.75), pos_hint={'center_x': 0.35, 'y': 0.18})
        root.add_widget(self.drawing)
        
        # Title
        title = Label(text='🎨 儿童绘图益智乐园 🧩', font_size=48, pos_hint={'center_x':0.5, 'y':0.9}, size_hint=(0.8, 0.1), color=(0.1,0.2,0.8,1), bold=True)
        root.add_widget(title)
        
        # Color palette
        colors = [(1,0,0,1),(1,0.65,0,1),(1,1,0,1),(0.2,0.8,0.2,1),(0,0.6,1,1),(0.5,0,1,1),(1,0,0.8,1),(0.3,0.3,0.3,1)]
        color_grid = GridLayout(cols=4, spacing=12, size_hint=(0.28, 0.35), pos_hint={'x': 0.72, 'y': 0.52})
        for col in colors:
            btn = Button(background_color=col, size_hint_y=None, height=65)
            btn.bind(on_press=lambda b, c=col: self.change_color(c))
            color_grid.add_widget(btn)
        root.add_widget(color_grid)
        
        # Tools
        tool_box = BoxLayout(orientation='vertical', spacing=12, size_hint=(0.26, 0.42), pos_hint={'x':0.73, 'y':0.08})
        
        # Brush size
        self.size_label = Label(text='🖌 粗细: 10', size_hint_y=None, height=50, font_size=24)
        tool_box.add_widget(self.size_label)
        
        sizes = BoxLayout(spacing=8)
        for sz in [5,10,18,28]:
            b = Button(text=str(sz), background_color=(0.9,0.9,0.95,1))
            b.bind(on_press=lambda inst, s=sz: self.set_size(s))
            sizes.add_widget(b)
        tool_box.add_widget(sizes)
        
        # Other buttons
        for text, color, func in [
            ('🧼 橡皮', (0.95,0.95,0.6,1), self.eraser),
            ('🗑 清空', (1,0.5,0.5,1), self.clear_all),
            ('💾 保存', (0.4,0.85,0.4,1), self.save_to_gallery),
            ('🧩 动物拼图', (0.5,0.7,1,1), self.start_puzzle)
        ]:
            btn = Button(text=text, background_color=color, size_hint_y=None, height=72, font_size=26)
            btn.bind(on_press=func)
            tool_box.add_widget(btn)
        
        root.add_widget(tool_box)
        
        # Load sounds
        self.sounds = {}
        sound_files = {'click': 'click.mp3', 'success': 'success.mp3', 'bg': 'background.mp3'}
        for key, file in sound_files.items():
            self.sounds[key] = SoundLoader.load(file) if SoundLoader.load(file) else None
        
        if self.sounds['bg']:
            self.sounds['bg'].loop = True
            Clock.schedule_once(lambda dt: self.sounds['bg'].play(), 0.5)
        
        return root
    
    def change_color(self, color):
        self.drawing.current_color = color
        self.drawing.mode = 'draw'
        if self.sounds.get('click'): self.sounds['click'].play()
    
    def set_size(self, size):
        self.drawing.line_width = size
        self.size_label.text = f'🖌 粗细: {size}'
        if self.sounds.get('click'): self.sounds['click'].play()
    
    def eraser(self, *args):
        self.drawing.current_color = (1,1,1,1)
        if self.sounds.get('click'): self.sounds['click'].play()
    
    def clear_all(self, *args):
        self.drawing.canvas.clear()
        with self.drawing.canvas.before:
            Color(1,1,1,1)
            self.drawing.bg_rect = Rectangle(pos=self.drawing.pos, size=self.drawing.size)
        if self.sounds.get('click'): self.sounds['click'].play()
    
    def save_to_gallery(self, *args):
        filename = f'kids_drawing_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        self.drawing.export_to_png(filename)
        
        content = Label(text=f'✅ 已保存！\n文件: {filename}\n\n在 iPad 上可使用 plyer 进一步保存到相册')
        popup = Popup(title='保存成功 🎉', content=content, size_hint=(0.7, 0.4))
        popup.open()
        if self.sounds.get('success'): self.sounds['success'].play()
    
    def start_puzzle(self, *args):
        if self.sounds.get('click'): self.sounds['click'].play()
        
        animals = ['可爱小猫', '忠实小狗', '大熊宝宝', '小兔子', '企鹅宝宝']
        animal = random.choice(animals)
        
        popup = Popup(title='🧩 ' + animal + ' 拼图', 
                     content=Label(text='拖拽拼图块到正确位置！\n\n更多智能拼图和真实图片即将添加~', font_size=26),
                     size_hint=(0.75, 0.55))
        popup.open()
        
        if self.sounds.get('success'): self.sounds['success'].play()

if __name__ == '__main__':
    KidsDrawPuzzleApp().run()