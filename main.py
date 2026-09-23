import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex, platform
from kivy.animation import Animation


FONT_NAME = 'Vazir'
LabelBase.register(name=FONT_NAME, fn_regular='assets/Vazirmatn-Regular.ttf')

BG_COLOR = '#1e1e2e'
DRAWER_COLOR = '#181825'
ITEM_COLOR = '#313244'
BLUE = '#4a90d9'
GREEN = '#a6e3a1'
RED = '#e06c75'
WHITE = '#ffffff'


def fa(text):
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


def format_number(x):
    if float(x).is_integer():
        return str(int(x))
    return f'{x:.2f}'


AREA_UNIT = 'سانتی\u200cمتر مربع'
LEN_UNIT = 'سانتی\u200cمتر'
VOL_UNIT = 'سانتی\u200cمتر مکعب'

# ---------------------------------------------------------------------------
# تعریف همه‌ی محاسبه‌گرها: هر ورودی (برچسب، کلید، مقدار پیش‌فرض)
# kind='combined' یعنی یه فرم واحد که چند نتیجه با هم می‌ده (چون اطلاعات لازم یکیه)
# kind='toggle'   یعنی دو حالت جدا با فیلدهای متفاوت (با دو دکمه بالای صفحه)
# ---------------------------------------------------------------------------

CONFIGS_2D = {
    'dayreh': {
        'screen_title': 'مساحت و محیط دایره',
        'menu_title': 'مساحت و محیط دایره',
        'kind': 'toggle',
        'modes': {
            'masahat': {
                'label': 'مساحت',
                'fields': [('شعاع', 'r', ''), ('عدد پی', 'pi', '3.14')],
                'compute': lambda v: v['r'] * v['r'] * v['pi'],
                'result_label': 'مساحت', 'unit': AREA_UNIT,
            },
            'mohit': {
                'label': 'محیط',
                'fields': [('قطر', 'd', ''), ('عدد پی', 'pi', '3.14')],
                'compute': lambda v: v['d'] * v['pi'],
                'result_label': 'محیط', 'unit': LEN_UNIT,
            },
        },
    },
    'morabae': {
        'screen_title': 'مساحت و محیط مربع',
        'menu_title': 'مساحت و محیط مربع',
        'kind': 'combined',
        'fields': [('ضلع', 'a', '')],
        'results': [
            {'label': 'مساحت', 'compute': lambda v: v['a'] * v['a'], 'unit': AREA_UNIT},
            {'label': 'محیط', 'compute': lambda v: v['a'] * 4, 'unit': LEN_UNIT},
        ],
    },
    'mosalas': {
        'screen_title': 'مساحت و محیط مثلث',
        'menu_title': 'مساحت و محیط مثلث',
        'kind': 'toggle',
        'modes': {
            'masahat': {
                'label': 'مساحت',
                'fields': [('قاعده', 'b', ''), ('ارتفاع', 'h', '')],
                'compute': lambda v: (v['b'] * v['h']) / 2,
                'result_label': 'مساحت', 'unit': AREA_UNIT,
            },
            'mohit': {
                'label': 'محیط',
                'fields': [('ضلع ۱', 's1', ''), ('ضلع ۲', 's2', ''), ('ضلع ۳', 's3', '')],
                'compute': lambda v: v['s1'] + v['s2'] + v['s3'],
                'result_label': 'محیط', 'unit': LEN_UNIT,
            },
        },
    },
    'mostatil': {
        'screen_title': 'مساحت و محیط مستطیل',
        'menu_title': 'مساحت و محیط مستطیل',
        'kind': 'combined',
        'fields': [('طول', 'l', ''), ('عرض', 'w', '')],
        'results': [
            {'label': 'مساحت', 'compute': lambda v: v['l'] * v['w'], 'unit': AREA_UNIT},
            {'label': 'محیط', 'compute': lambda v: 2 * (v['l'] + v['w']), 'unit': LEN_UNIT},
        ],
    },
    'zoozanagheh': {
        'screen_title': 'مساحت و محیط ذوزنقه',
        'menu_title': 'مساحت و محیط ذوزنقه',
        'kind': 'toggle',
        'modes': {
            'masahat': {
                'label': 'مساحت',
                'fields': [('قاعده\u200cی بزرگ', 'a1', ''), ('قاعده\u200cی کوچک', 'a2', ''), ('ارتفاع', 'h', '')],
                'compute': lambda v: (v['a1'] + v['a2']) * (v['h'] / 2),
                'result_label': 'مساحت', 'unit': AREA_UNIT,
            },
            'mohit': {
                'label': 'محیط',
                'fields': [('ضلع ۱', 's1', ''), ('ضلع ۲', 's2', ''), ('ضلع ۳', 's3', ''), ('ضلع ۴', 's4', '')],
                'compute': lambda v: v['s1'] + v['s2'] + v['s3'] + v['s4'],
                'result_label': 'محیط', 'unit': LEN_UNIT,
            },
        },
    },
}

CONFIGS_3D = {
    'dayreh': {
        'screen_title': 'حجم و مساحت جانبی دایره',
        'menu_title': 'حجم و مساحت جانبی دایره',
        'kind': 'combined',
        'fields': [('شعاع', 'r', ''), ('ارتفاع', 'h', ''), ('عدد پی', 'pi', '3.14')],
        'results': [
            {'label': 'حجم', 'compute': lambda v: v['pi'] * v['r'] * v['r'] * v['h'], 'unit': VOL_UNIT},
            {'label': 'مساحت جانبی', 'compute': lambda v: 2 * v['pi'] * v['r'] * v['h'], 'unit': AREA_UNIT},
        ],
    },
    'morabae': {
        'screen_title': 'حجم و مساحت جانبی مربع',
        'menu_title': 'حجم و مساحت جانبی مربع',
        'kind': 'combined',
        'fields': [('ضلع', 'a', ''), ('ارتفاع', 'h', '')],
        'results': [
            {'label': 'حجم', 'compute': lambda v: v['a'] * v['a'] * v['h'], 'unit': VOL_UNIT},
            {'label': 'مساحت جانبی', 'compute': lambda v: 4 * v['a'] * v['h'], 'unit': AREA_UNIT},
        ],
    },
    'mosalas': {
        'screen_title': 'حجم و مساحت جانبی مثلث',
        'menu_title': 'حجم و مساحت جانبی مثلث',
        'kind': 'toggle',
        'modes': {
            'hajm': {
                'label': 'حجم',
                'fields': [('قاعده\u200cی مثلث', 'b', ''), ('ارتفاع مثلث', 'th', ''), ('ارتفاع', 'h', '')],
                'compute': lambda v: ((v['b'] * v['th']) / 2) * v['h'],
                'result_label': 'حجم', 'unit': VOL_UNIT,
            },
            'janebi': {
                'label': 'مساحت جانبی',
                'fields': [('ضلع ۱', 's1', ''), ('ضلع ۲', 's2', ''), ('ضلع ۳', 's3', ''), ('ارتفاع', 'h', '')],
                'compute': lambda v: (v['s1'] + v['s2'] + v['s3']) * v['h'],
                'result_label': 'مساحت جانبی', 'unit': AREA_UNIT,
            },
        },
    },
    'mostatil': {
        'screen_title': 'حجم و مساحت جانبی مستطیل',
        'menu_title': 'حجم و مساحت جانبی مستطیل',
        'kind': 'combined',
        'fields': [('طول', 'l', ''), ('عرض', 'w', ''), ('ارتفاع', 'h', '')],
        'results': [
            {'label': 'حجم', 'compute': lambda v: v['l'] * v['w'] * v['h'], 'unit': VOL_UNIT},
            {'label': 'مساحت جانبی', 'compute': lambda v: 2 * (v['l'] + v['w']) * v['h'], 'unit': AREA_UNIT},
        ],
    },
    'zoozanagheh': {
        'screen_title': 'حجم و مساحت جانبی ذوزنقه',
        'menu_title': 'حجم و مساحت جانبی ذوزنقه',
        'kind': 'toggle',
        'modes': {
            'hajm': {
                'label': 'حجم',
                'fields': [
                    ('قاعده\u200cی بزرگ', 'a1', ''), ('قاعده\u200cی کوچک', 'a2', ''),
                    ('ارتفاع ذوزنقه', 'th', ''), ('ارتفاع', 'h', ''),
                ],
                'compute': lambda v: ((v['a1'] + v['a2']) * (v['th'] / 2)) * v['h'],
                'result_label': 'حجم', 'unit': VOL_UNIT,
            },
            'janebi': {
                'label': 'مساحت جانبی',
                'fields': [
                    ('ضلع ۱', 's1', ''), ('ضلع ۲', 's2', ''),
                    ('ضلع ۳', 's3', ''), ('ضلع ۴', 's4', ''), ('ارتفاع', 'h', ''),
                ],
                'compute': lambda v: (v['s1'] + v['s2'] + v['s3'] + v['s4']) * v['h'],
                'result_label': 'مساحت جانبی', 'unit': AREA_UNIT,
            },
        },
    },
}

SHAPE_ORDER = ['dayreh', 'morabae', 'mosalas', 'mostatil', 'zoozanagheh']


def enable_wrap(widget):
    widget.halign = 'center'
    widget.valign = 'middle'

    def _sync(instance, *_):
        instance.text_size = (instance.width - 16, None)

    widget.bind(width=_sync, height=_sync)
    _sync(widget)


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


class Scrim(Widget):
    def __init__(self, root_ref, **kwargs):
        super().__init__(**kwargs)
        self.root_ref = root_ref
        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            self._rect = Rectangle()
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_touch_down(self, touch):
        if self.root_ref.drawer_open and self.collide_point(*touch.pos):
            self.root_ref.close_drawer()
            return True
        return False


class RoundedButton(Button):
    def __init__(self, bg_hex, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._color = Color(*get_color_from_hex(bg_hex))
            self._rect = RoundedRectangle(radius=[radius])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_bg(self, hex_color):
        self._color.rgba = get_color_from_hex(hex_color)


class TopBar:
    """میکسین کوچک برای ساخت دکمه‌ی منو و عنوان بالای صفحه (کد مشترک)."""

    def build_top_bar(self, root, title_fa):
        self.menu_btn = RoundedButton(
            bg_hex=DRAWER_COLOR, text='\u00bb\u00bb', font_size='18sp', bold=True,
            size_hint=(0.14, 0.06), pos_hint={'x': 0.03, 'top': 0.97},
            color=get_color_from_hex(WHITE), radius=14,
        )
        self.menu_btn.bind(on_press=lambda *_: App.get_running_app().root.toggle_drawer())
        root.add_widget(self.menu_btn)

        self.title_label = Label(
            text=fa(title_fa), font_name=FONT_NAME, font_size='16sp',
            size_hint=(0.65, 0.06), pos_hint={'center_x': 0.53, 'top': 0.97},
            color=get_color_from_hex(WHITE),
        )
        root.add_widget(self.title_label)


class CalcScreen(Screen, TopBar):
    """صفحه‌ی عمومی محاسبه: هم برای مساحت/محیط دوبعدی، هم حجم/مساحت جانبی."""

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.kind = config['kind']
        self.input_widgets = {}
        if self.kind == 'toggle':
            self.mode = list(config['modes'].keys())[0]
            self.mode_buttons = {}

        root = FloatLayout()
        root.add_widget(ColoredWidget(BG_COLOR, size_hint=(1, 1)))
        self.build_top_bar(root, config['screen_title'])

        content_top = 0.87
        if self.kind == 'toggle':
            mode_row = BoxLayout(
                orientation='horizontal', spacing=10, size_hint=(0.85, 0.07),
                pos_hint={'center_x': 0.5, 'top': 0.87},
            )
            for key, m in config['modes'].items():
                btn = RoundedButton(
                    bg_hex=BLUE if key == self.mode else ITEM_COLOR,
                    text=fa(m['label']), font_name=FONT_NAME, font_size='16sp',
                    color=get_color_from_hex(WHITE), radius=14,
                )
                enable_wrap(btn)
                btn.bind(on_press=lambda inst, k=key: self.set_mode(k))
                self.mode_buttons[key] = btn
                mode_row.add_widget(btn)
            root.add_widget(mode_row)
            content_top = 0.77

        content = BoxLayout(
            orientation='vertical', spacing=12,
            size_hint=(0.88, content_top - 0.05),
            pos_hint={'center_x': 0.5, 'top': content_top},
        )

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.inputs_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[0, 5, 0, 5])
        self.inputs_box.bind(minimum_height=self.inputs_box.setter('height'))
        scroll.add_widget(self.inputs_box)
        content.add_widget(scroll)

        self.compute_btn = RoundedButton(
            bg_hex=GREEN, text=fa('محاسبه'), font_name=FONT_NAME, font_size='18sp',
            color=get_color_from_hex('#1e1e2e'), radius=16, size_hint_y=None, height=54,
        )
        self.compute_btn.bind(on_press=self.compute)
        content.add_widget(self.compute_btn)

        self.result_label = Label(
            text='', font_name=FONT_NAME, font_size='18sp',
            size_hint_y=None, height=90, halign='center', valign='top',
            color=get_color_from_hex(WHITE),
        )
        self.result_label.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))
        content.add_widget(self.result_label)

        root.add_widget(content)
        self.add_widget(root)

        self.build_inputs()

    def set_mode(self, key):
        self.mode = key
        for k, btn in self.mode_buttons.items():
            btn.set_bg(BLUE if k == key else ITEM_COLOR)
        self.build_inputs()

    def current_fields(self):
        if self.kind == 'toggle':
            return self.config['modes'][self.mode]['fields']
        return self.config['fields']

    def build_inputs(self):
        self.inputs_box.clear_widgets()
        self.input_widgets = {}
        self.result_label.text = ''

        for label_fa, key, default in self.current_fields():
            row = BoxLayout(orientation='vertical', spacing=4, size_hint_y=None, height=70)
            lbl = Label(
                text=fa(label_fa), font_name=FONT_NAME, font_size='14sp',
                size_hint_y=None, height=22, color=get_color_from_hex(WHITE),
            )
            ti = TextInput(
                text=default, multiline=False, input_filter='float', font_size='18sp',
                size_hint_y=None, height=44, halign='center', padding=[10, 10, 10, 10],
            )
            self.input_widgets[key] = ti
            row.add_widget(lbl)
            row.add_widget(ti)
            self.inputs_box.add_widget(row)

    def compute(self, instance):
        values = {}
        for key, widget in self.input_widgets.items():
            try:
                values[key] = float(widget.text)
            except ValueError:
                self.result_label.text = fa('لطفاً همه\u200cی مقادیر رو درست وارد کن')
                return

        if self.kind == 'combined':
            lines = []
            for r in self.config['results']:
                val = r['compute'](values)
                lines.append(f"{fa(r['label'])} : {format_number(val)} {fa(r['unit'])}")
            self.result_label.text = '\n'.join(lines)
        else:
            m = self.config['modes'][self.mode]
            val = m['compute'](values)
            self.result_label.text = f"{fa(m['result_label'])} : {format_number(val)} {fa(m['unit'])}"


class AboutScreen(Screen, TopBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        root.add_widget(ColoredWidget(BG_COLOR, size_hint=(1, 1)))
        self.build_top_bar(root, 'درباره\u200cی برنامه')

        telegram_label = Label(
            text=fa('Telegram : @BroAmir@2009'), font_name=FONT_NAME, font_size='20sp',
            halign='center', valign='middle', size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.58}, color=get_color_from_hex(WHITE),
        )
        root.add_widget(telegram_label)

        github_label = Label(
            text=fa('GitHub :') + ' [ref=github][u][color=4a90d9]Amir-Eskandari200[/color][/u][/ref]',
            markup=True, font_name=FONT_NAME, font_size='20sp',
            halign='center', valign='middle', size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.42}, color=get_color_from_hex(WHITE),
        )
        github_label.bind(on_ref_press=lambda instance, ref: open_link('https://github.com/Amir-Eskandari200'))
        root.add_widget(github_label)

        self.add_widget(root)


class NavDrawer(BoxLayout):
    def __init__(self, sm, entries, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.sm = sm
        self.padding = [15, 20, 15, 15]
        self.spacing = 10

        with self.canvas.before:
            Color(*get_color_from_hex(DRAWER_COLOR))
            self._bg = Rectangle()
        self.bind(pos=self._update_bg, size=self._update_bg)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        items_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=[0, 0, 0, 10])
        items_box.bind(minimum_height=items_box.setter('height'))

        for label_fa, screen_name in entries:
            btn = RoundedButton(
                bg_hex=ITEM_COLOR, text=fa(label_fa), font_name=FONT_NAME, font_size='14sp',
                size_hint_y=None, height=50, color=get_color_from_hex(WHITE), radius=14,
            )
            enable_wrap(btn)
            btn.bind(on_press=lambda inst, sn=screen_name: self.go_to(sn))
            items_box.add_widget(btn)

        scroll.add_widget(items_box)
        self.add_widget(scroll)

        about_btn = RoundedButton(
            bg_hex=BLUE, text=fa('درباره\u200cی برنامه'), font_name=FONT_NAME, font_size='16sp',
            size_hint=(1, None), height=50, color=get_color_from_hex(WHITE), radius=14,
        )
        about_btn.bind(on_press=lambda *_: self.go_to('about'))
        self.add_widget(about_btn)

        exit_btn = RoundedButton(
            bg_hex=RED, text=fa('خروج'), font_name=FONT_NAME, font_size='16sp',
            size_hint=(1, None), height=50, color=get_color_from_hex(WHITE), radius=14,
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

        self.drawer_width = 0.75
        self.drawer_open = False

        self.sm = ScreenManager(transition=NoTransition())
        entries = []
        for key in SHAPE_ORDER:
            cfg = CONFIGS_2D[key]
            self.sm.add_widget(CalcScreen(cfg, name=f'calc_{key}'))
            entries.append((cfg['menu_title'], f'calc_{key}'))
        for key in SHAPE_ORDER:
            cfg = CONFIGS_3D[key]
            self.sm.add_widget(CalcScreen(cfg, name=f'vol_{key}'))
            entries.append((cfg['menu_title'], f'vol_{key}'))

        self.sm.add_widget(AboutScreen(name='about'))
        self.sm.current = f'calc_{SHAPE_ORDER[0]}'
        self.add_widget(self.sm)

        self.scrim = Scrim(self, size_hint=(1, 1))
        self.scrim.opacity = 0
        self.add_widget(self.scrim)

        self.drawer = NavDrawer(self.sm, entries, size_hint=(None, 1))
        self.drawer.width = max(self.width, 1) * self.drawer_width
        self.drawer.x = -self.drawer.width
        self.drawer.y = 0
        self.add_widget(self.drawer)

        self.bind(size=self._on_root_resize)

    def _on_root_resize(self, *args):
        self.drawer.width = max(self.width, 1) * self.drawer_width
        if not self.drawer_open:
            self.drawer.x = -self.drawer.width

    def toggle_drawer(self):
        if self.drawer_open:
            self.close_drawer()
        else:
            self.open_drawer()

    def open_drawer(self):
        self.drawer_open = True
        Animation(opacity=1, d=0.2, t='out_quad').start(self.scrim)
        Animation(x=0, d=0.28, t='out_cubic').start(self.drawer)

    def close_drawer(self):
        self.drawer_open = False
        Animation(opacity=0, d=0.18, t='in_quad').start(self.scrim)
        Animation(x=-self.drawer.width, d=0.22, t='in_cubic').start(self.drawer)


class MathQuizApp(App):
    def build(self):
        self.title = 'Math Quiz'
        return RootWidget()


if __name__ == '__main__':
    MathQuizApp().run()
