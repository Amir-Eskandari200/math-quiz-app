import random
import time

import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex, platform
from kivy.animation import Animation
from kivy.core.window import Window


FONT_NAME = 'Vazir'
LabelBase.register(name=FONT_NAME, fn_regular='assets/Vazirmatn-Regular.ttf')

BG_COLOR = '#1e1e2e'
DRAWER_COLOR = '#181825'
BLUE = '#4a90d9'
GREEN = '#a6e3a1'
RED = '#e06c75'
WHITE = '#ffffff'


def fa(text):
    """آماده‌سازی متن فارسی برای نمایش درست (چسبیدن حروف + راست‌به‌چپ)."""
    return get_display(arabic_reshaper.reshape(text))


def open_link(url):
    if platform == 'android':
        from jnius import autoclass
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        PythonActivity.mActivity.startActivity(intent)
    else:
        import webbrowser
        webbrowser.open(url)


class ColoredWidget(Widget):
    def __init__(self, color_hex, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex(color_hex))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update, pos=self._update)

    def _update(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class QuizScreen(Screen):
    """صفحه‌ی عمومی برای هر نوع تمرین ضرب."""

    def __init__(self, screen_title, min_val, max_val, fixed_second=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = screen_title
        self.min_val = min_val
        self.max_val = max_val
        self.fixed_second = fixed_second

        root = FloatLayout()
        self.bg = ColoredWidget(BG_COLOR, size_hint=(1, 1))
        root.add_widget(self.bg)

        # دکمه‌ی همبرگری برای باز کردن منو
        self.menu_btn = Button(
            text=fa('منو'),
            font_name=FONT_NAME,
            font_size='16sp',
            size_hint=(0.16, 0.06),
            pos_hint={'x': 0.02, 'top': 0.98},
            background_color=get_color_from_hex(DRAWER_COLOR),
            color=get_color_from_hex(WHITE),
        )
        self.menu_btn.bind(on_press=lambda *_: App.get_running_app().root.toggle_drawer())
        root.add_widget(self.menu_btn)

        # عنوان بخش فعلی
        self.title_label = Label(
            text=fa(screen_title),
            font_name=FONT_NAME,
            font_size='18sp',
            size_hint=(0.7, 0.06),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            color=get_color_from_hex(WHITE),
        )
        root.add_widget(self.title_label)

        self.question_label = Label(
            text='',
            font_size='34sp',
            font_name=FONT_NAME,
            size_hint=(0.9, 0.18),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            color=get_color_from_hex(WHITE),
        )
        root.add_widget(self.question_label)

        self.input_box = TextInput(
            hint_text=fa('جواب رو وارد کن'),
            multiline=False,
            input_filter='int',
            font_size='24sp',
            font_name=FONT_NAME,
            size_hint=(0.8, 0.09),
            pos_hint={'center_x': 0.5, 'top': 0.62},
            halign='center',
            padding=[10, 15, 10, 15],
        )
        root.add_widget(self.input_box)

        self.submit_btn = Button(
            text=fa('بررسی'),
            font_size='20sp',
            font_name=FONT_NAME,
            size_hint=(0.6, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.51},
            background_color=get_color_from_hex(BLUE),
            color=get_color_from_hex(WHITE),
        )
        self.submit_btn.bind(on_press=self.check_answer)
        root.add_widget(self.submit_btn)

        # دکمه‌های دوباره / توقف
        action_row = BoxLayout(
            orientation='horizontal',
            spacing=15,
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.4},
        )
        self.retry_btn = Button(
            text=fa('دوباره'),
            font_name=FONT_NAME,
            font_size='18sp',
            color=get_color_from_hex(WHITE),
            background_normal='',
            background_color=(0, 0, 0, 0),
        )
        with self.retry_btn.canvas.before:
            Color(*get_color_from_hex(BG_COLOR))
            self._retry_bg = Rectangle()
            Color(*get_color_from_hex(GREEN))
            self._retry_border = Rectangle()
        self.retry_btn.bind(pos=self._update_retry_border, size=self._update_retry_border)
        self.retry_btn.bind(on_press=self.retry)

        self.stop_btn = Button(
            text=fa('توقف'),
            font_name=FONT_NAME,
            font_size='18sp',
            color=get_color_from_hex(WHITE),
            background_normal='',
            background_color=(0, 0, 0, 0),
        )
        with self.stop_btn.canvas.before:
            Color(*get_color_from_hex(BG_COLOR))
            self._stop_bg = Rectangle()
            Color(*get_color_from_hex(RED))
            self._stop_border = Rectangle()
        self.stop_btn.bind(pos=self._update_stop_border, size=self._update_stop_border)
        self.stop_btn.bind(on_press=self.stop_quiz)

        action_row.add_widget(self.retry_btn)
        action_row.add_widget(self.stop_btn)
        root.add_widget(action_row)

        self.result_label = Label(
            text='',
            font_size='18sp',
            font_name=FONT_NAME,
            size_hint=(0.9, 0.18),
            pos_hint={'center_x': 0.5, 'top': 0.28},
            color=get_color_from_hex(GREEN),
        )
        root.add_widget(self.result_label)

        self.add_widget(root)
        self.new_question()

    def _update_retry_border(self, *args):
        b = 3
        self._retry_border.pos = self.retry_btn.pos
        self._retry_border.size = self.retry_btn.size
        self._retry_bg.pos = (self.retry_btn.x + b, self.retry_btn.y + b)
        self._retry_bg.size = (self.retry_btn.width - 2 * b, self.retry_btn.height - 2 * b)

    def _update_stop_border(self, *args):
        b = 3
        self._stop_border.pos = self.stop_btn.pos
        self._stop_border.size = self.stop_btn.size
        self._stop_bg.pos = (self.stop_btn.x + b, self.stop_btn.y + b)
        self._stop_bg.size = (self.stop_btn.width - 2 * b, self.stop_btn.height - 2 * b)

    def new_question(self):
        self.do1 = random.randint(self.min_val, self.max_val)
        self.do2 = self.fixed_second if self.fixed_second else random.randint(self.min_val, self.max_val)
        self.start_time = time.time()
        self.question_label.text = f'{self.do1} x {self.do2} = ?'
        self.input_box.text = ''
        self.input_box.disabled = False
        self.submit_btn.disabled = False
        self.result_label.text = ''

    def check_answer(self, instance):
        try:
            sol = int(self.input_box.text)
        except ValueError:
            self.result_label.text = fa('لطفاً یه عدد وارد کن')
            return

        correct = self.do1 * self.do2
        if sol == correct:
            elapsed = int(time.time() - self.start_time)
            self.result_label.text = fa(f'درسته! زمان = {elapsed} ثانیه')
            self.input_box.disabled = True
            self.submit_btn.disabled = True
        else:
            self.result_label.text = fa('غلطه، دوباره امتحان کن.')

    def retry(self, instance):
        self.new_question()

    def stop_quiz(self, instance):
        correct = self.do1 * self.do2
        self.result_label.text = fa(f'متوقف شد. جواب درست: {correct}')
        self.input_box.disabled = True
        self.submit_btn.disabled = True


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        root.add_widget(ColoredWidget(BG_COLOR, size_hint=(1, 1)))

        telegram_label = Label(
            text=fa('Telegram : @BroAmir@2009'),
            font_name=FONT_NAME,
            font_size='20sp',
            halign='center',
            valign='middle',
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            color=get_color_from_hex(WHITE),
        )
        root.add_widget(telegram_label)

        github_label = Label(
            text=fa('GitHub :') + ' [ref=github][u][color=4a90d9]Amir-Eskandari200[/color][/u][/ref]',
            markup=True,
            font_name=FONT_NAME,
            font_size='20sp',
            halign='center',
            valign='middle',
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.42},
            color=get_color_from_hex(WHITE),
        )
        github_label.bind(on_ref_press=lambda instance, ref: open_link('https://github.com/Amir-Eskandari200'))
        root.add_widget(github_label)

        self.add_widget(root)


class NavDrawer(BoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.sm = sm
        self.padding = [15, 20, 15, 20]
        self.spacing = 12

        with self.canvas.before:
            Color(*get_color_from_hex(DRAWER_COLOR))
            self._bg = Rectangle()
        self.bind(pos=self._update_bg, size=self._update_bg)

        def make_menu_button(text_fa, target_screen):
            btn = Button(
                text=fa(text_fa),
                font_name=FONT_NAME,
                font_size='16sp',
                size_hint=(1, 0.13),
                background_color=get_color_from_hex('#313244'),
                color=get_color_from_hex(WHITE),
            )
            btn.bind(on_press=lambda *_: self.go_to(target_screen))
            return btn

        self.add_widget(make_menu_button('ضرب اعداد دورقمی در ۱۱', 'quiz_11'))
        self.add_widget(make_menu_button('ضرب اعداد دورقمی در اعداد دورقمی', 'quiz_2digit'))
        self.add_widget(make_menu_button('ضرب اعداد سه رقمی در اعداد سه رقمی', 'quiz_3digit'))

        self.add_widget(Widget())  # فاصله‌انداز

        about_btn = Button(
            text=fa('درباره‌ی برنامه'),
            font_name=FONT_NAME,
            font_size='16sp',
            size_hint=(1, 0.12),
            background_color=get_color_from_hex(BLUE),
            color=get_color_from_hex(WHITE),
        )
        about_btn.bind(on_press=lambda *_: self.go_to('about'))
        self.add_widget(about_btn)

        exit_btn = Button(
            text=fa('خروج'),
            font_name=FONT_NAME,
            font_size='16sp',
            size_hint=(1, 0.12),
            background_color=get_color_from_hex(RED),
            color=get_color_from_hex(WHITE),
        )
        exit_btn.bind(on_press=lambda *_: App.get_running_app().stop())
        self.add_widget(exit_btn)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def go_to(self, screen_name):
        if self.sm.current != screen_name:
            self.sm.current = screen_name
        App.get_running_app().root.close_drawer()


class RootWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(QuizScreen(fa('ضرب اعداد دورقمی در ۱۱'), 10, 99, fixed_second=11, name='quiz_11'))
        self.sm.add_widget(QuizScreen(fa('ضرب اعداد دورقمی در اعداد دورقمی'), 10, 99, name='quiz_2digit'))
        self.sm.add_widget(QuizScreen(fa('ضرب اعداد سه رقمی در اعداد سه رقمی'), 100, 999, name='quiz_3digit'))
        self.sm.add_widget(AboutScreen(name='about'))
        self.sm.current = 'quiz_11'
        self.add_widget(self.sm)

        self.drawer_width = 0.72  # نسبت به عرض صفحه

        self.scrim = ColoredWidget('#00000099', size_hint=(1, 1))
        self.scrim.opacity = 0
        self.scrim.disabled = True
        self.scrim.bind(on_touch_down=self._on_scrim_touch)
        self.add_widget(self.scrim)

        self.drawer = NavDrawer(self.sm, size_hint=(self.drawer_width, 1))
        self.drawer.pos_hint = {'x': -self.drawer_width, 'top': 1}
        self.add_widget(self.drawer)

        self.drawer_open = False

    def _on_scrim_touch(self, instance, touch):
        if self.scrim.collide_point(*touch.pos) and self.drawer_open:
            self.close_drawer()
            return True
        return False

    def toggle_drawer(self):
        if self.drawer_open:
            self.close_drawer()
        else:
            self.open_drawer()

    def open_drawer(self):
        self.drawer_open = True
        self.scrim.disabled = False
        Animation(opacity=1, d=0.15).start(self.scrim)
        Animation(x=0, d=0.2, t='out_quad').start(self.drawer)

    def close_drawer(self):
        self.drawer_open = False
        Animation(opacity=0, d=0.15).start(self.scrim)
        anim = Animation(x=-self.drawer_width * self.width, d=0.2, t='in_quad')
        anim.bind(on_complete=lambda *_: setattr(self.scrim, 'disabled', True))
        anim.start(self.drawer)


class QuizApp(App):
    def build(self):
        self.title = 'Math Quiz'
        return RootWidget()


if __name__ == '__main__':
    QuizApp().run()
