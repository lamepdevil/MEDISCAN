from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty
from datetime import datetime
from io import BytesIO
import base64
import os
import json

from mediscan_api import upload_image_and_get_result


class MediScanApp(App):
    config_file = "settings.json"

    def build(self):
        self.load_settings()
        self.theme_colors()

        self.root_panel = TabbedPanel(do_default_tab=False)

        self.build_scan_tab()
        self.build_settings_tab()
        self.build_history_tab()

        return self.root_panel

    def theme_colors(self):
        if self.light_theme:
            self.BG_COLOR = get_color_from_hex("#FFFFFF")
            self.TEXT_COLOR = get_color_from_hex("#000000")
            self.PRIMARY_COLOR = get_color_from_hex("#2196F3")
            self.BUTTON_TEXT_COLOR = get_color_from_hex("#FFFFFF")
        else:
            self.BG_COLOR = get_color_from_hex("#1E1E1E")
            self.TEXT_COLOR = get_color_from_hex("#FFFFFF")
            self.PRIMARY_COLOR = get_color_from_hex("#BB86FC")
            self.BUTTON_TEXT_COLOR = get_color_from_hex("#000000")

    def build_scan_tab(self):
        scan_tab = TabbedPanelItem(text='Scan')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.label = Label(text="Upload Medical Report Image", size_hint=(1, 0.1),
                           color=self.TEXT_COLOR, font_size=20)
        layout.add_widget(self.label)

        self.file_chooser = FileChooserIconView(size_hint=(1, 0.4))
        layout.add_widget(self.file_chooser)

        self.preview_image = Image(size_hint=(1, 0.3))
        layout.add_widget(self.preview_image)

        self.upload_btn = Button(text="Upload and Analyze", size_hint=(1, 0.1),
                                 background_color=self.PRIMARY_COLOR, color=self.BUTTON_TEXT_COLOR)
        self.upload_btn.bind(on_press=self.upload_file)
        layout.add_widget(self.upload_btn)

        self.result_label = Label(text="", size_hint=(1, 0.1), color=self.TEXT_COLOR, font_size=16)
        layout.add_widget(self.result_label)

        self.chart_image = Image(size_hint=(1, 0.4))
        layout.add_widget(self.chart_image)

        scan_tab.add_widget(layout)
        self.root_panel.add_widget(scan_tab)

    def build_settings_tab(self):
        settings_tab = TabbedPanelItem(text='Settings')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.theme_toggle = ToggleButton(text='Light Mode' if self.light_theme else 'Dark Mode',
                                         state='down' if self.light_theme else 'normal')
        self.theme_toggle.bind(on_press=self.toggle_theme)
        layout.add_widget(self.theme_toggle)

        layout.add_widget(Label(text="Alert Threshold"))
        self.pref_slider = Slider(min=0, max=100, value=self.threshold)
        self.pref_slider.bind(value=self.save_settings)
        layout.add_widget(self.pref_slider)

        self.report_type_spinner = Spinner(
            text=self.report_type,
            values=('blood', 'glucose', 'cholesterol'),
            size_hint=(1, 0.2)
        )
        self.report_type_spinner.bind(text=self.save_settings)
        layout.add_widget(self.report_type_spinner)

        settings_tab.add_widget(layout)
        self.root_panel.add_widget(settings_tab)

    def build_history_tab(self):
        history_tab = TabbedPanelItem(text='History')
        self.history_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.history_layout)
        history_tab.add_widget(self.scroll)
        self.root_panel.add_widget(history_tab)

    def upload_file(self, instance):
        selected = self.file_chooser.selection
        if selected:
            image_path = selected[0]
            self.preview_image.source = image_path

            try:
                result = upload_image_and_get_result(image_path)
                report_type = result.get('report_type', 'Unknown')
                self.result_label.text = f"Type: {report_type.title()}"

                chart_data = next(iter(result.get("charts", {}).values()), None)
                if chart_data:
                    self.show_chart_from_base64(chart_data)

                # History entry
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                entry = Label(text=f"[{timestamp}] {report_type.title()} Report", color=self.TEXT_COLOR,
                              size_hint_y=None, height=40, markup=True)
                self.history_layout.add_widget(entry)

            except Exception as e:
                self.result_label.text = f"Error: {str(e)}"
                self.result_label.color = (1, 0, 0, 1)

    def show_chart_from_base64(self, b64_data):
        try:
            img_data = base64.b64decode(b64_data.split(",")[1])
            buf = BytesIO(img_data)
            core_image = CoreImage(buf, ext="png")
            self.chart_image.texture = core_image.texture
        except Exception:
            self.result_label.text = "Failed to load chart image."

    def toggle_theme(self, instance):
        self.light_theme = not self.light_theme
        instance.text = "Light Mode" if self.light_theme else "Dark Mode"
        self.theme_colors()
        self.label.color = self.TEXT_COLOR
        self.result_label.color = self.TEXT_COLOR
        self.save_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                data = json.load(f)
                self.light_theme = data.get("theme", True)
                self.threshold = data.get("threshold", 50)
                self.report_type = data.get("report_type", "blood")
        else:
            self.light_theme = True
            self.threshold = 50
            self.report_type = "blood"

    def save_settings(self, *args):
        data = {
            "theme": self.light_theme,
            "threshold": self.pref_slider.value,
            "report_type": self.report_type_spinner.text
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    MediScanApp().run()
