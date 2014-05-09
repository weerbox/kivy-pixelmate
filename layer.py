from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.bubble import Bubble
from kivy.uix.bubble import BubbleButton
from kivy.graphics.fbo import Fbo
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import ListProperty

import improc
from globals import *


class LayerBubble(Bubble):
    callbacks = {}
    item_list = []

    @staticmethod
    def set_callback(key, function):
        if callable(function):
            LayerBubble.callbacks[key] = function
        else:
            raise NameError('function not callable')

    @staticmethod
    def hide_all():
        for bub in LayerBubble.item_list:
            if bub.parent:
                if bub in bub.parent.children:
                    bub.parent.remove_widget(bub)

    def __init__(self, laybox, items, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.layer_box = laybox
        self.size_hint = (None, None)
        self.size = (Window.size[0] * 0.15, Window.size[1] * MENU_ENTRY_HEIGHT_HINT * items)
        self.pos_hint = {'center_x': -0.4, 'y': 0.4}
        self.orientation = 'vertical'
        self.arrow_pos = 'right_bottom'

        self.add_widget(BubbleButton(text='Add new', on_press=self.on_children_press))
        self.add_widget(BubbleButton(text='Clone', on_press=self.on_children_press))
        if items >= 3:
            self.add_widget(BubbleButton(text='Delete', on_press=self.on_children_press))
        if items == 4:
            self.add_widget(BubbleButton(text='Merge', on_press=self.on_children_press))
        self.add_widget(BubbleButton(text='Clear', on_press=self.on_children_press))

        LayerBubble.item_list.append(self)


    def on_touch_down(self, touch):
        if super(LayerBubble, self).on_touch_down(touch):
            return True

        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        #touch.grab(self)
        touch.ud[self] = True

        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            return True
        return True


    def on_touch_move(self, touch):
        #if touch.grab_current is self:
        #    return True
        if super(LayerBubble, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        #if touch.grab_current is self:
        #    touch.ungrab(self)

        if super(LayerBubble, self).on_touch_up(touch):
            return True
        return self in touch.ud


    def on_children_press(self, bbutton):
        if bbutton.text == 'Add new':
            self._check_and_call('addnew')
        elif bbutton.text == 'Clone':
            self._check_and_call('clone')
        elif bbutton.text == 'Delete':
            self._check_and_call('remove')
        elif bbutton.text == 'Merge':
            self._check_and_call('merge')
        elif bbutton.text == 'Clear':
            self._check_and_call('clear')
        self.parent.remove_widget(self)


    def _check_and_call(self, key):
        if LayerBubble.callbacks.has_key(key):
            if callable(LayerBubble.callbacks[key]):
                LayerBubble.callbacks[key](self.layer_box)
            else:
                raise NameError('callback function ' + key + ' not callable')
        else:
            raise NameError(key + ' callback not defined')


class Layer(Widget):
    layer_bg_texture = None
    layer_bg_rect = None

    @staticmethod
    def _create_texture(size):
        texture = Texture.create(size=size, colorfmt='rgba', bufferfmt='ubyte')
        texture.mag_filter = 'nearest'
        texture.min_filter = 'nearest'

        return texture


    @staticmethod
    def create_bg_rect(size):
        if not Layer.layer_bg_texture:
            path = os.path.join(os.getcwd(), '.kivy/data/bg3.png')
            print >> sys.stderr, path
            Layer.layer_bg_texture = Image(path).texture
            Layer.layer_bg_texture.mag_filter = 'nearest'
            Layer.layer_bg_texture.min_filter = 'nearest'
            Layer.layer_bg_texture.wrap = 'repeat'

        Layer.layer_bg_rect = Rectangle(texture=Layer.layer_bg_texture, pos=(0, 0), size=size)

        nb_repeat_x = size[0] / 8
        nb_repeat_y = size[1] / 8
        t = 0
        Layer.layer_bg_rect.tex_coords = (
            -(t * 0.001), 0,
            -(t * 0.001 + nb_repeat_x), 0,
            -(t * 0.001 + nb_repeat_x), -nb_repeat_y,
            -(t * 0.001), -nb_repeat_y
        )
        return Layer.layer_bg_rect


    def __init__(self, app, size, **kwargs):
        Widget.__init__(self, **kwargs)
        self.app = app
        self.is_active = False
        Layer.create_bg_rect(size=size)
        self.texture = Layer._create_texture(size=size)

        self.rect = self._create_textured_rect(self.texture)
        # self.box_texture = improc.texture_copy(self.texture, smooth=True)
        self.textures_array = []  # array of textures for undo
        self._textures_array_index = 0
        self.visible = True
        self.preview_rect = None
        self.texture_locked = False


    def new_texture(self, size):
        self.texture = Layer._create_texture(size=size)
        # self.box_texture = improc.texture_copy(self.texture, smooth=True)
        self.put_texture_on_canvas(self.texture)

    def _create_textured_rect(self, texture):
        Layer.create_bg_rect(size=texture.size)
        self.rect = Rectangle(texture=texture, pos=(0, 0), size=texture.size)
        return self.rect

    def replace_texture(self, texture):
        self.texture = texture
        # self.box_texture = improc.copy_texture(self.texture, smooth=True)
        self.rect = self._create_textured_rect(texture)
        self.put_texture_on_canvas(texture)

    def put_rects_on_canvas(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            bg_tex = Layer.layer_bg_texture.get_region(0, 0, self.size[0], self.size[1])
            self.previewRectBG = Rectangle(texture=bg_tex, pos=(self.x, self.y),
                                           size=(self.size[0], self.size[1]))
            # self.box_texture = improc.texture_copy(self.texture, smooth=True)
            self.preview_rect = Rectangle(texture=self.texture, pos=(self.x, self.y),
                                          size=(self.size[0], self.size[1]))
        self.canvas.ask_update()

    def put_texture_on_canvas(self, texture):
        self.put_rects_on_canvas()


    def switch_visible(self):
        self.visible = not self.visible

    def get_texture(self):
        return self.texture

    def backup_texture(self):
        _texture = improc.texture_copy(self.texture)
        self.textures_array = self.textures_array[:self._textures_array_index + 1]
        self.textures_array.append(_texture)
        self._textures_array_index = len(self.textures_array) - 1

    def texture_from_backup(self, direction):
        if direction == -1:
            if self._textures_array_index > 0:
                self._textures_array_index -= 1
                self.texture = improc.texture_copy(self.textures_array[self._textures_array_index])
                self.replace_texture(self.texture)
        else:
            if self._textures_array_index < len(self.textures_array) - 1:
                self._textures_array_index += 1
                self.texture = improc.texture_copy(self.textures_array[self._textures_array_index])
                self.replace_texture(self.texture)


    def clear_texture(self):
        # self.texture = Texture.create(size=self.app.aPaint.fbo.texture.size, colorfmt='rgba', bufferfmt='ubyte')
        self.texture = Layer._create_texture(size=self.app.aPaint.fbo.texture.size)

        self.rect = Rectangle(texture=self.texture, pos=(0, 0), size=self.texture.size)

    def lock_texture(self):
        self.texture_locked = True

    def switch_lock_texture(self):
        self.texture_locked = not self.texture_locked


class LayerBox(Widget):
    __events__ = ('on_press', 'on_release')
    active = None
    active_id = None
    last_active = None
    boxlist = []
    callbacks = {}
    app = None

    @staticmethod
    def select_rect_update():
        for lay in LayerBox.boxlist:
            lay.remove_selrect()
        if LayerBox.active:
            LayerBox.active.add_selrect()

    @staticmethod
    def activate(id):
        LayerBox.last_active = LayerBox.active
        LayerBox.active = LayerBox.boxlist[id]

        for lb in LayerBox.boxlist:
            if lb is not LayerBox.active:
                lb.layer.is_active = False
                lb._is_active = False
                lb.put_rects_on_canvas()
        LayerBox.active.layer.is_active = True
        LayerBox.active._is_active = True
        LayerBox.active.put_rects_on_canvas()

        if callable(LayerBox.active.on_press_callback):
            LayerBox.active.on_press_callback()

    @staticmethod
    def bubbles_update():
        if LayerBox.boxlist:
            if len(LayerBox.boxlist) == 1:
                lb = LayerBox.boxlist[0]
                lb.bubble = LayerBubble(lb, pos=(lb.x, 0), items=2)
                lb.bubble.x = -lb.bubble.width
            else:
                lb = LayerBox.boxlist[0]
                lb.bubble = LayerBubble(lb, pos=(lb.x, 0), items=3)
                lb.bubble.x = -lb.bubble.width

    def __init__(self, app, texture_size, **kwargs):
        self._is_active = False
        self._bg_rect = None
        self.size_per = 0.19
        self.selrect_w = 0.003 * Window.size[0]
        Widget.__init__(self, orientation='horizontal', **kwargs)

        LayerBox.app = self.app = app
        self.on_press_callback = None
        self.add_new_callback = None
        self.size_hint = (None, None)
        self.layout = RelativeLayout(**kwargs)
        self.btn_view = Button(text='O', size_hint=(0.3, 0.5),
                               on_press=self.switch_visible)
        # self.btn_menu = Button(text='=', pos_hint={'x': 0, 'y': 0},
        #                        on_press=self.show_bubble)
        self.btn_menu = Button(text='=', pos_hint={'x': 0, 'y': 0}, on_press=self.switch_lock)
        self.btn_view.background_color = [1, 1, 1, 0.6]
        self.btn_menu.background_color = [1, 1, 1, 0.6]

        # self.layer = Layer(app, pos_hint={'x': 0.3, 'y': 0})
        self.layer = Layer(app, size=texture_size, pos_hint={'x': 0, 'y': 0})

        self.size = [self.size_per * Window.size[0], self.size_per * Window.size[1]]
        self.btn_view.size = [0.3 * self.size[0], 0.5 * self.size[1]]
        self.btn_menu.size = [0.3 * self.size[0], 0.5 * self.size[1]]
        # self.layer.size = self.calc_layer_size(texture_size)

        self.btn_view.pos = (0, 0.5 * self.height)
        self.btn_menu.pos = (0, 0)
        # self.layer.pos = (self.btn_menu.size[0], (self.size[1]-self.layer.size[1])/2.0)
        self.layer.pos = (0, (self.size[1] - self.layer.size[1]) / 2.0)

        self.layout.add_widget(self.layer)
        self.layout.add_widget(self.btn_view)
        self.layout.add_widget(self.btn_menu)

        self.add_widget(self.layout)

        self._select_line = None

        self.update_size_pos(texture_size)

        LayerBox.boxlist.append(self)

        self.put_rects_on_canvas()

        if len(LayerBox.boxlist) == 1:
            LayerBox.activate(0)


    @property
    def is_active(self):
        return self._is_active

    def get_texture(self):
        return self.layer.get_texture()

    def set_pos(self, pos):
        self.pos = pos
        self.layout.pos = pos

    def switch_visible(self, *args):
        self.layer.switch_visible()
        if self.layer.visible:
            self.btn_view.text = 'O'
        else:
            self.btn_view.text = 'X'

        self.app.update()

    def switch_lock(self, *args):
        self.layer.switch_lock_texture()
        if self.layer.texture_locked:
            self.btn_menu.text = 'L'
        else:
            self.btn_menu.text = '='

        self.app.update()


    def calc_layer_size(self, texture_size):
        k1 = float(self.size[0]) / float(self.size[1])
        k2 = float(texture_size[0]) / float(texture_size[1])
        if k2 > k1:
            # w = 0.7 * self.width
            w = 1.0 * self.width
            h = w / k2
        else:
            h = self.height
            w = h * k2
        return (w, h)

    def update_size_pos(self, texture_size):
        self.layer.size = self.calc_layer_size(texture_size)
        self.layer.pos = ((self.size[0] - self.layer.size[0]) / 2.0,
                          (self.size[1] - self.layer.size[1]) / 2.0)

    def _update_back(self):
        if self._bg_rect:
            self.layout.canvas.before.remove(self._bg_rect)
        with self.layout.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            self._bg_rect = Rectangle(pos=(0, 0), size=(self.size[0], self.size[1]))

    def new_texture(self, size):
        self.layer.new_texture(size)

    def put_rects_on_canvas(self):
        self._update_back()
        self.layer.put_rects_on_canvas()

    def put_texture_on_canvas(self, texture):
        self._update_back()
        self.layer.put_texture_on_canvas(texture)

    def on_touch_down(self, touch):
        if super(LayerBox, self).on_touch_down(touch):
            return True

        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.ud[self] = True
        self.dispatch('on_press')


    def on_touch_move(self, touch):
        #if touch.grab_current is self:
        #    return True
        if super(LayerBox, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        #if touch.grab_current is self:
        #    touch.ungrab(self)
        if super(LayerBox, self).on_touch_up(touch):
            return True
        return self in touch.ud

    def on_press(self):
        LayerBox.last_active = LayerBox.active
        LayerBox.activate(LayerBox.boxlist.index(self))  # kostil
        # LayerBox.active = self

        LayerBox.select_rect_update()

    def set_active(self):
        LayerBox.activate(LayerBox.boxlist.index(self))


    def on_release(self):
        pass

    def add_selrect(self):
        with self.canvas.before:
            Color(0, 0, 1, 1)
            self._select_line = Rectangle(pos=(self.x - self.selrect_w, self.y - self.selrect_w),
                                          size=(self.size[0] + self.selrect_w * 2, self.size[1] + self.selrect_w * 2))


    def remove_selrect(self):
        if self._select_line is not None:
            self.canvas.before.remove(self._select_line)
            self._select_line = None


class LayerRibbon(RelativeLayout):
    __events__ = ('on_press', 'on_release')


    @staticmethod
    def activate(id):
        LayerBox.activate(id)

    @staticmethod
    def bg_texture():
        return Layer.layer_bg_texture

    # @staticmethod
    # def set_callback(key, callback):
    #     LayerBubble.set_callback(key, callback)


    def __init__(self, app, **kwargs):
        pos = ListProperty([0, 0])
        RelativeLayout.__init__(self, **kwargs)
        self.app = app
        self.on_press_callback = None
        self.but_remove = None
        self.but_add = None
        self.but_clone = None
        self.but_merge = None
        self.but_remove = None
        self.button_list = []

        self.offset_y = 0

        self.padding_y_per = 0.01

        self.start_padding = Window.height * LAYER_RIBBON_BUTTON_HEIGHT_HINT + LAYERBOX_PADDING[3]
        self.padding_y = Window.height * self.padding_y_per

        # self.layout_size_per = 0.21
        self.size_child_per = 0.19
        self.size_hint = (LAYER_RIBBON_WIDTH_HINT, 1)
        self.pos = (Window.width, 0)
        self.in_pos = (Window.width - Window.width * (PALLETE_LAYOUT_SIZE_HINT[0] + LAYER_RIBBON_WIDTH_HINT), 0)
        self.index = 0
        self._bg_rect = None
        self.size = (Window.width * LAYER_RIBBON_WIDTH_HINT, Window.height)

        self.layout = RelativeLayout(pos=(0, 0))
        self.layout.bind(children=self._layerbox_layout_on_children)
        # self.layout.pos = (10, 0)

        self.layout.size_hint = (None, None)
        self.layout.size = (Window.width * self.size_child_per, 0)

        self.layout.canvas.ask_update()

        self.scroll_view = ScrollView(size=(Window.width * LAYER_RIBBON_WIDTH_HINT, Window.height))
        self.scroll_view.scroll_y = 0.0

        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)
        self._create_ribbon_buttons()




        # self.layout.size = (Window.width * self.size_child_per, self.size[1])

        self.out_pos = (Window.width, self.pos[1])
        self.side_hidden = True
        self.animation_show = Animation(pos=self.in_pos, transition='in_quad', duration=0.3)
        self.animation_hide = Animation(pos=self.out_pos, transition='in_quad', duration=0.3)

        self.add_to_undo_callback = None

        def print_this(self):
            print self.scroll_view.scroll_y

        self.scroll_view.bind(scroll_y=lambda *args: print_this(self))


    def _layerbox_layout_on_children(self, *args):
        self.layout.height = self.get_layerbox_layout_height()

    def _create_ribbon_buttons(self):

        self.button_layout = BoxLayout(size_hint=(1, LAYER_RIBBON_BUTTON_HEIGHT_HINT), orientation="horizontal",
                                       padding=[0, 0, 0, 0], spacing=2)

        self.but_add = Button(text='Add')
        self.but_clone = Button(text='Cln')
        self.but_merge = Button(text='Mrg')
        self.but_remove = Button(text='Del')
        self.button_list = [self.but_add, self.but_clone, self.but_merge, self.but_remove]

        with self.button_layout.canvas:
            Color(0.5, 0.5, 0.5)
            self.button_layout_rect = Rectangle(pos=(0, 0), size=self.button_layout.size)

        def resize(self):
            self.button_layout_rect.size = self.button_layout.size


        self.button_layout.bind(size=lambda *args: resize(self))

        for but in self.button_list:
            self.button_layout.add_widget(but)

        self.add_widget(self.button_layout)


    def get_layerbox_layout_height(self):
        return self.start_padding + self.offset_y * (len(LayerBox.boxlist))


    def _add_layer(self, texture_size):
        size_hint = (1, self.size_child_per)
        pos = (LAYERBOX_PADDING[0], self.start_padding + self.offset_y * len(LayerBox.boxlist))
        lb = LayerBox(app=self.app, texture_size=texture_size, size_hint=size_hint, pos=pos)

        lb.on_press_callback = self.on_press_callback

        self.offset_y = lb.size[1] + self.padding_y
        lb.put_rects_on_canvas()
        self.layout.add_widget(lb)
        self.canvas.ask_update()

        print self.scroll_view.scroll_y

        return lb

    def update(self):
        self.canvas.ask_update()

    # def update_layer_size_pos(self):
    #     for lb in LayerBox.boxlist:
    #         lb.update_size_pos()

    def new_layer(self, texture_size):
        return self._add_layer(texture_size=texture_size)


    def clone_layer(self, source_lb):
        new_lb = self._add_layer(texture_size=source_lb.layer.texture.size)
        if source_lb.active:
            tex = self.app.aPaint.fbo_get_texture()
        else:
            tex = source_lb.layer.texture
        new_lb.layer.texture = improc.texture_copy(tex)
        new_lb.put_rects_on_canvas()


    def merge_layer(self, source_lb):
        texture1 = source_lb.get_texture()
        upper_id = LayerBox.boxlist.index(source_lb)
        if upper_id > 0:
            lower_lb = LayerBox.boxlist[upper_id - 1]
            texture2 = lower_lb.get_texture()
            restex = improc.texture_merge(texture1, texture2)
            if lower_lb.is_active:
                improc.texture_replace_data(self.app.aPaint.fbo.texture, restex)
            else:
                lower_lb.layer.texture = restex
            lower_lb.put_rects_on_canvas()
            print upper_id, upper_id - 1

    def remove_layer(self, laybox):
        self.layout.remove_widget(laybox)
        LayerBox.boxlist.remove(laybox)
        # del laybox
        LayerBox.bubbles_update()
        self.canvas.ask_update()
        self.update_pos()


    def remove_all_layers(self):

        for laybox in LayerBox.boxlist:
            self.layout.remove_widget(laybox)
            del laybox
            LayerBox.bubbles_update()
            self.canvas.ask_update()
            self.update_pos()
        LayerBox.boxlist[:] = []

    def blit_layers_to_texture(self):
        fbo = Fbo(size=LayerBox.active.layer.texture.size)
        fbo.texture.mag_filter = 'nearest'
        fbo.texture.min_filter = 'nearest'
        with fbo:
            Color(1, 1, 1, 1)
            for lb in LayerBox.boxlist:
                Rectangle(pos=(0, 0), size=lb.layer.texture.size, texture=lb.layer.texture)
        fbo.draw()
        return fbo.texture

    def update_pos(self):
        ind = 0
        for lb in LayerBox.boxlist:
            lb.set_pos((LAYERBOX_PADDING[0], self.start_padding + self.offset_y * ind))
            self.canvas.ask_update()
            ind += 1


    def layers_count(self):
        return len(LayerBox.boxlist)

    def on_touch_down(self, touch):
        if super(LayerRibbon, self).on_touch_down(touch):
            return True

        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.ud[self] = True
        self.dispatch('on_press')
        return True

    def on_touch_move(self, touch):
        #if touch.grab_current is self:
        #    return True
        if super(LayerRibbon, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        #if touch.grab_current is self:
        #    touch.ungrab(self)

        if super(LayerRibbon, self).on_touch_up(touch):
            return True
        return self in touch.ud


    def redraw_back(self):
        if self._bg_rect:
            self.canvas.before.remove(self._bg_rect)
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 0.5)
            self._bg_rect = Rectangle(pos=(0, 0), size=(self.size[0], WIN_HEIGHT * 1))
        self.canvas.ask_update()

    def put_rects_on_canvas(self):
        self.redraw_back()
        LayerBox.active.put_rects_on_canvas()

    def put_texture_on_canvas(self, texture):
        self.redraw_back()
        LayerBox.active.put_texture_on_canvas(texture)

    def get_active_layerbox(self):
        return LayerBox.active

    def get_active_layer_id(self):
        self.active_layer_id = LayerBox.boxlist.index(LayerBox.active)
        return self.active_layer_id

    def get_active_layer(self):
        return LayerBox.active.layer

    def get_last_active_layer(self):
        if LayerBox.last_active is None:
            return LayerBox.active.layer
        return LayerBox.last_active.layer

    def get_textures_list(self):
        return [lbox.layer.texture for lbox in LayerBox.boxlist]

    def on_press(self, touch):
        # RelativeLayout.on_press(self)
        LayerBubble.hide_all()


    # def on_touch_down(self, touch):
    #     # print 'press'
    #     if not self.collide_point(*touch.pos):
    #         # print 'out press'
    #         self.animate_hide()

    def on_release(self):
        RelativeLayout.on_release(self)

    def animate_hide(self, *args):
        if not self.side_hidden:
            self.animation_hide.start(self)
            self.side_hidden = True
            LayerBubble.hide_all()

    def animate_show(self, *args):
        if self.side_hidden:
            self.animation_show.start(self)
            self.side_hidden = False

    def animate_switch(self, *args):
        if not self.side_hidden:
            self.animate_hide()
        else:
            self.animate_show()