from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar, SettingItem, SettingsPanel

from globals import APP_VERSION


class Options():
    def __init__(self, config=None, settings=None):
        if settings is None:
            self.settings_panel = SettingsWithSidebar()
        else:
            self.settings_panel = settings

        self.config = config

        self.settings_panel.add_json_panel('PixelMate', self.config, 'option.json')

        panel = SettingsPanel(title="PixelMate v" + str(APP_VERSION), settings=self)
        item1 = SettingItem(panel=panel, disabled=True,
                            title=" \nJust another pixel art editor program\n\nDeveloped by Plyaskin Anton (werton)\n\nPowered by Python & Kivy",
                            desc=None, settings=self)
        panel.add_widget(item1)
        # self.settings_panel.add_widget(panel)
        if self.settings_panel.interface is not None:
            self.settings_panel.interface.add_panel(panel, "About", panel.uid)

            # self.settings_panel.add_panel(panel)


class SettingsApp(App):
    def build(self):
        opt = Options()
        return opt.settings_panel


if __name__ in ('__android__', '__main__'):
    SettingsApp().run()