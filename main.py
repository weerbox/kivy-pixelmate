from kivy.config import Config

Config.set('graphics', 'width', '854')
Config.set('graphics', 'height', '480')

from os.path import splitext

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.settings import SettingsWithSidebar
from kivy.core.image import Image
from kivy.graphics import Color

from globals import *
from improc import texture_save, texture_replace_data, texture_flip, textures_list_save_to_zip, textures_list_from_zip
from option import Options
from paint import Paint
import dialog
import layer
import tools
import ui


class PM(App):
    scrollView = None
    aPaint = None
    state = {
        'root': 0, 'menu': 1, 'settings': 2, 'dialog_save': 3, 'dialog_open': 4, 'dialog_new': 5, 'dialog_color': 6
    }

    def __init__(self):
        App.__init__(self)

        self.settings_cls = SettingsWithSidebar
        if USE_KIVY_SETTINGS:
            self.use_kivy_settings = True
        else:
            self.use_kivy_settings = False
        self.dialog_state = PM.state['root']
        self.layer_dialog_enabled = False
        self.layer_ribbon = None
        self.prev_tool = 0
        self.active_tool = 0
        self.bind(on_start=self.post_build_init)
        self.new_dialog = None
        self.open_dialog = None
        self.image_save_dialog = None
        self.project_save_dialog = None
        self.palette = None
        self.toolbar = None
        self.layout_config = None
        self.button_layer = None
        self.button_menu = None

    def post_build_init(self, ev):
        if platform() == 'android':
            import android

            android.map_key(android.KEYCODE_BACK, 1001)
        win = self._app_window
        self.toolbar.tools_select(TOOL_PENCIL)
        self.aPaint.refbo()
        self.layer_ribbon._add_layer(texture_size=DEFAULT_IMAGE_SIZE)
        self.layer_ribbon.activate(0)

    def _key_handler(self, window, *largs):
        key = largs[0]
        if platform() == 'android':
            if key == 1001:
                self.action_key_back()
        if platform() == 'win':
            if key == KEY_ESCAPE:
                self.action_key_back()

    def update(self):
        self.aPaint.canvas_put_drawarea()
        self.layer_ribbon.put_rects_on_canvas()

    def on_stop(self):
        self.dialog_exit()

    def on_pause(self):
        return True

    def open_settings(self, *largs):
        self.dialog_state = self.state['dialog_open']
        super(PM, self).open_settings()

    def close_settings(self, *largs):
        self.dialog_state = self.state['root']
        super(PM, self).close_settings()

    def on_config_change(self, config, section, key, value):
        tools.SelectTool.on_setting_change()
        tools.LineTool.on_setting_change()

    def build_settings(self, settings):
        opt = Options(self.config, settings)

    def build_config(self, config):
        config.setdefaults('editor', {'tools_touch_point_size': '50'})
        config.setdefaults('misc', {'exitconfirm': '1'})
        config.setdefaults('misc', {'layer_delete_confirm': '1'})
        config.setdefaults('misc', {'layer_merge_confirm': '1'})
        config.setdefaults('filechooser', {'open_path': DEF_PATH})
        config.setdefaults('filechooser', {'project_save_path': DEF_PATH})
        config.setdefaults('filechooser', {'image_save_path': DEF_PATH})

    def read_config(self):
        config = self.config

    def dialog_exit(self, *args):
        def exit_callback(answer):
            if answer == "yes":
                sys.exit()

        self.save_config()

        if self.config.getint('misc', 'exitconfirm'):
            dl = dialog.ConfirmDialog("Exit", "Exit app?", exit_callback)
        else:
            sys.exit()

    def save_config(self):
        pass

    def build_tools(self):
        self.aPaint.tool_select = tools.SelectTool(app=self)
        self.aPaint.tool_line = tools.LineTool(app=self)
        self.aPaint.tool_rect = tools.RectTool(app=self)
        self.aPaint.tool_ellipse = tools.EllipseTool(app=self)
        self.aPaint.tool_buffer = tools.BufferTool(app=self)

    def show_menu(self):
        if self.main_menu not in self.root.children:
            self.root.add_widget(self.main_menu)
        else:
            self.root.remove_widget(self.main_menu)

    def hide_menu(self):
        self.root.remove_widget(self.main_menu)

    def mainmenu_show(self, *args):
        self.main_menu.open()

    def hide_tool_menu(self):
        self.root.remove_widget(self.tool_menu)

    def action_key_back(self):
        if self.dialog_state == self.state['root']:
            self.dialog_exit()

    def image_new(self, size):
        self.layer_ribbon.remove_all_layers()
        layer_box = self.layer_ribbon.new_layer(texture_size=size)
        layer_box.set_active()
        self.aPaint.canvas_put_drawarea()
        self.aPaint.scale_canvas(zoom=1 / self.aPaint.scale)

    def image_open(self, path, fullnamelist):
        def add_layers_from_texture_list(textures_list):
            layer_box_list = []
            for tex in textures_list:
                lb = self.layer_ribbon.new_layer(texture_size=tex.size)
                lb.layer.replace_texture(tex)
                layer_box_list.append(lb)
            return layer_box_list

        if splitext(fullnamelist[0])[1] == '.pixelmate':
            textures_list = textures_list_from_zip(fullnamelist[0])
            self.layer_ribbon.remove_all_layers()
            layer_box_list = add_layers_from_texture_list(textures_list)
            layer_box_list[0].set_active()
            self.aPaint.canvas_put_drawarea(texture=layer_box_list[0].layer.texture)
            self.aPaint.scale_canvas(zoom=1 / self.aPaint.scale)
        else:
            try:
                image = Image(arg=fullnamelist[0].encode('utf-8'))
                self.layer_ribbon.remove_all_layers()
                image.texture.flip_vertical()
                texture_flip(image.texture)
                layer_box = self.layer_ribbon.new_layer(image.texture.size)
                layer_box.set_active()
                layer_box.layer.replace_texture(image.texture)
                self.aPaint.canvas_put_drawarea(texture=image.texture)
                self.aPaint.scale_canvas(zoom=1 / self.aPaint.scale)
            except Exception, e:
                print e

    def image_save(self, path, name, format):
        fpath = os.path.join(path, name) + '.' + format.lower()
        active_layer = self.layer_ribbon.get_active_layer()
        texture_replace_data(active_layer.texture, self.aPaint.fbo.texture)
        tex = self.layer_ribbon.blit_layers_to_texture()
        texture_save(tex, fpath, format)

    def project_save(self, path, name, format):
        fpath = os.path.join(path, name) + '.' + format.lower()
        textures_list = app.layer_ribbon.get_textures_list()
        textures_list_save_to_zip(textures_list, fpath)

    def layer_add(self, layer_box, texture_size=None):
        if texture_size is None:
            texture_size = layer_box.layer.texture.size
        self.layer_ribbon._add_layer(texture_size=texture_size)
        self.layer_ribbon.activate(len(layer.LayerBox.boxlist) - 1)
        self.aPaint.fbo_update_pos()

    def layer_clone(self, layer_box):
        self.layer_ribbon.clone_layer(layer_box)
        self.aPaint.fbo_update_pos()

    def layer_merge(self, layer_box, confirmation=True):
        if not self.config.getint('misc', 'layer_merge_confirm'):
            confirmation = False

        def dialog_callback(answer):
            if answer == 'yes':
                self.layer_ribbon.merge_layer(layer_box)
                self.aPaint.fbo_update_pos()
                self.layer_remove(layer_box, confirmation=False)

        if confirmation:
            dialog.ConfirmDialog("Confirmation", "Merge this layer with a lower layer?", dialog_callback)
        else:
            dialog_callback(answer='yes')

    def layer_remove(self, layer_box, confirmation=True):
        if not app.config.getint('misc', 'layer_delete_confirm'):
            confirmation = False

        def dialog_callback(answer):
            if answer == 'yes':
                if self.layer_ribbon.layers_count() > 1:
                    index_active = self.layer_ribbon.get_active_layer_id()
                    self.layer_ribbon.remove_layer(layer_box)
                    layer_count = self.layer_ribbon.layers_count()
                    if index_active >= layer_count:
                        index_active = layer_count - 1
                    self.layer_ribbon.activate(index_active)
                    self.aPaint.fbo_update_pos()

        if confirmation:
            dialog.ConfirmDialog("Confirmation", "Delete this layer?", dialog_callback)
        else:
            dialog_callback(answer='yes')

    def layer_clear(self, layer_box):
        layer_box.layer.clear_texture()
        self.ribbon_on_press_callback()

    def ribbon_on_press_callback(self):
        active_layer = self.layer_ribbon.get_active_layer()
        self.aPaint.fbo_create(active_layer.texture.size, active_layer.texture)
        self.aPaint.fbo.clear()
        self.aPaint.canvas_put_drawarea()
        self.layer_ribbon.put_rects_on_canvas()

    def palette_hidden(self):
        return self.palette.hidden

    def layer_ribbon_hidden(self):
        return self.layer_ribbon.hidden

    def on_palette_hidden(self, *args):
        if self.palette.hidden:
            if not self.layer_ribbon.hidden:
                self.layer_ribbon.animate_move(1)
        if not self.palette.hidden:
            if not self.layer_ribbon.hidden:
                self.layer_ribbon.animate_move(2)

    def on_layer_ribbon_hidden(self, *args):
        if self.layer_ribbon.hidden:
            self.button_layer.state = 'normal'
        else:
            self.button_layer.state = 'down'

    def build(self):
        self.read_config()
        self.new_dialog = dialog.NewImage(callback=self.image_new)
        self.open_dialog = dialog.OpenImage(callback=self.image_open)
        self.image_save_dialog = dialog.SaveImage(callback=self.image_save)
        self.project_save_dialog = dialog.SaveProject(callback=self.project_save)

        self.main_menu = ui.Menu(new_clbk=self.new_dialog.open, open_clbk=self.open_dialog.open,
                                 save_project_clbk=self.project_save_dialog.open,
                                 save_image_clbk=self.image_save_dialog.open,
                                 options_clbk=self.open_settings, exit_clbk=self.dialog_exit)
        self.aColor = Color(0, 0, 0, 255)
        self.root = FloatLayout(size=(Window.width, Window.height))
        PM.aPaint = Paint(self, size=DRAWAREA_SIZE)
        PM.aPaintLayout = RelativeLayout(size_hint=(1, 1), pos=(0, 0))
        PM.aPaintLayout.size = DRAWAREA_SIZE
        PM.aPaintLayout.add_widget(PM.aPaint)
        self.root.add_widget(PM.aPaintLayout)
        self.palette = ui.Palette(self)
        self.build_tools()
        self.toolbar = ui.Toolbar(self)
        PM.aPaint.fbo_update_pos()
        PM.aPaint.scale_canvas(5)
        self.layer_ribbon = layer.LayerRibbon(self)
        self.layer_ribbon.on_press_callback = self.ribbon_on_press_callback
        self.layout_config = BoxLayout(orientation='horizontal',
                                       size_hint=(PALETTE_BTN_SHOW_SIZE_HINT[0], PALETTE_BTN_SHOW_SIZE_HINT[1]),
                                       pos=(Window.width - (PALETTE_BTN_SHOW_SIZE_HINT[0] * Window.width),
                                            Window.height - PALETTE_BTN_SHOW_SIZE_HINT[1] * Window.height))
        self.button_layer = ToggleButton(background_normal=data_path('layer.png'),
                                         pos_hint={'x': 1.0 - 2 * PALETTE_BTN_SHOW_SIZE_HINT[0], 'y': 0},
                                         size_hint=PALETTE_BTN_SHOW_SIZE_HINT,
                                         background_down=data_path('layer_down.png'), border=[0, 0, 0, 0],
                                         on_press=self.layer_ribbon.animate_switch)
        self.button_menu = Button(background_normal=data_path('amenu.png'),
                                  background_down=data_path('amenu_down.png'), border=[0, 0, 0, 0],
                                  on_press=lambda *args: self.mainmenu_show())
        self.root.add_widget(self.layer_ribbon)
        self.root.add_widget(self.layout_config)
        self.layout_config.add_widget(self.button_menu)
        self.root.add_widget(self.toolbar)
        self.root.add_widget(self.palette)
        self.root.add_widget(self.button_layer)
        self.root.add_widget(self.toolbar.btn_show_toolbar)
        self.root.add_widget(self.palette.btn_show_palette)
        self.palette.bind(hidden=self.on_palette_hidden)
        self.layer_ribbon.bind(hidden=self.on_layer_ribbon_hidden)
        self.layer_ribbon.index = self.root.children.index(self.layer_ribbon)
        self.layer_ribbon.but_add.bind(on_press=lambda *args: self.layer_add(layer.LayerBox.active))
        self.layer_ribbon.but_merge.bind(on_press=lambda *args: self.layer_merge(layer.LayerBox.active))
        self.layer_ribbon.but_clone.bind(on_press=lambda *args: self.layer_clone(layer.LayerBox.active))
        self.layer_ribbon.but_remove.bind(on_press=lambda *args: self.layer_remove(layer.LayerBox.active))
        return self.root


if __name__ == '__main__':
    Window.clearcolor = (0.7, 0.7, 0.7, 1)
    Window.clear()
    app = PM()
    app.run()


