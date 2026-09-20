import random
import time

import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex


FONT_NAME = 'Vazir'
LabelBase.register(name=FONT_NAME, fn_regular='assets/Vazirmatn-Regular.ttf')


def fa(text):
    """متن فارسی رو برای نمایش درست (راست‌به‌چپ و به‌هم‌چسبیده) آماده می‌کنه."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


class QuizLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.do1 = random.randint(10, 100)
        self.do2 = random.randint(10, 100)
        self.start_time = time.time()

        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex('#1e1e2e'))
            self.bg = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)

        self.question_label = Label(
            text=f'{self.do1} x {self.do2} = ?',
            font_size='36sp',
            font_name=FONT_NAME,
            size_hint=(0.9, 0.25),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            color=get_color_from_hex('#ffffff'),
        )
        self.add_widget(self.question_label)

        self.input_box = TextInput(
            hint_text=fa('جواب رو وارد کن'),
            multiline=False,
            input_filter='int',
            font_size='24sp',
            font_name=FONT_NAME,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.65},
            halign='center',
            padding=[10, 15, 10, 15],
        )
        self.add_widget(self.input_box)

        self.submit_btn = Button(
            text=fa('بررسی'),
            font_size='22sp',
            font_name=FONT_NAME,
            size_hint=(0.6, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.5},
            background_color=get_color_from_hex('#4a90d9'),
        )
        self.submit_btn.bind(on_press=self.check_answer)
        self.add_widget(self.submit_btn)

        self.result_label = Label(
            text='',
            font_size='20sp',
            font_name=FONT_NAME,
            size_hint=(0.9, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.35},
            color=get_color_from_hex('#a6e3a1'),
        )
        self.add_widget(self.result_label)

        self.exit_btn = Button(
            text=fa('خروج از برنامه'),
            font_size='18sp',
            font_name=FONT_NAME,
            size_hint=(0.5, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.03},
            background_color=get_color_from_hex('#e06c75'),
        )
        self.exit_btn.bind(on_press=self.exit_app)
        self.add_widget(self.exit_btn)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def check_answer(self, instance):
        try:
            sol = int(self.input_box.text)
        except ValueError:
            self.result_label.text = fa('لطفاً یه عدد وارد کن')
            return

        correct = self.do1 * self.do2

        if sol == correct:
            elapsed = int(time.time() - self.start_time)
            self.result_label.text = fa(
                f'درسته! زمان = {elapsed} ثانیه'
            )
            self.submit_btn.disabled = True
            self.input_box.disabled = True
        elif sol == 0:
            self.result_label.text = fa('بازی متوقف شد.')
            self.submit_btn.disabled = True
            self.input_box.disabled = True
        else:
            self.result_label.text = fa('غلطه، دوباره امتحان کن.')

    def exit_app(self, instance):
        App.get_running_app().stop()


class QuizApp(App):
    def build(self):
        self.title = 'Quiz'
        return QuizLayout()


if __name__ == '__main__':
    QuizApp().run()
