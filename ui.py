from kivy.animation import Animation
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble
from kivy.graphics import Color, Line
import kivy
from hold import TapAndHoldWidget
from main import *


def toolbar_on_touch():
    app = APP()
    if app.active_tool == TOOL_LINE:
        if app.aPaint.tool_line.state is not None:
            app.aPaint.tool_line._render_and_reset_state(app.aPaint.fbo, app.aPaint.tool_fbo)
            app.aPaint.fbo.draw()
            app.aPaint.canvas.ask_update()
    if app.active_tool == TOOL_RECT:
        if app.aPaint.tool_rect.state is not None:
            app.aPaint.tool_rect._render_and_reset_state(app.aPaint.fbo, app.aPaint.tool_fbo)
            app.aPaint.fbo.draw()
            app.aPaint.canvas.ask_update()
    if app.active_tool == TOOL_ELLIPSE:
        if app.aPaint.tool_ellipse.state is not None:
            app.aPaint.tool_ellipse._render_and_reset_state(app.aPaint.fbo, app.aPaint.tool_fbo)
            app.aPaint.fbo.draw()
            app.aPaint.canvas.ask_update()


class ToolButton(Button):
    pressed = ListProperty([0, 0])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            toolbar_on_touch()
        if super(ToolButton, self).on_touch_down(touch):
            # print '0 pressed'
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self._do_press()
        self.dispatch('on_press')
        # print 'pressed'
        return True

        # if self.collide_point(*touch.pos):
        #     self.pressed = touch.pos
        #     return True
        # return super(ToolButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ToolButton, self).on_touch_up(touch)

        assert (self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch
        self._do_release()
        self.dispatch('on_release')

        # print 'released'
        # if self.collide_point(*touch.pos):
        #     self.pressed = touch.pos
        # return False
        return True


    def on_pressed(self, instance, pos):
        print ('pressed at {pos}'.format(pos=pos))


class ToolToggleButton(ToggleButton):
    pressed = ListProperty([0, 0])

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            toolbar_on_touch()
        if super(ToggleButton, self).on_touch_down(touch):
            # print '0 pressed'
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self._do_press()
        self.dispatch('on_press')
        # print 'pressed'
        return True

        # if self.collide_point(*touch.pos):
        #     self.pressed = touch.pos
        #     return True
        # return super(ToolButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ToggleButton, self).on_touch_up(touch)

        assert (self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch
        self._do_release()
        self.dispatch('on_release')

        # print 'released'
        # if self.collide_point(*touch.pos):
        #     self.pressed = touch.pos
        # return False
        return True


    def on_pressed(self, instance, pos):
        print ('pressed at {pos}'.format(pos=pos))


class MenuButton(ToolToggleButton):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.sub_item = None


    def _do_press(self):
        self._release_group(self)
        self.state = 'down' if self.state == 'down' else 'down'


class PaletteToggleButton(ToolToggleButton, TapAndHoldWidget):
    _hold_length = 0.4

    def __init__(self, **kwargs):
        super(PaletteToggleButton, self).__init__(**kwargs)
        self.background_down = ""
        self.group = 'pal'

    def on_state(self, *args):
        if self.state == 'down':
            with self.canvas.after:
                Color(0, 0.1, 1)
                Line(rectangle=(self.x + 2, self.y + 2, self.width - 4, self.height - 4), width=2, joint='miter')
        elif self.state == 'normal':
            self.canvas.after.clear()

    # def on_hold(self, touch):
    #     super(PaletteToggleButton, self).on_hold(touch)
    #     print 'holded'

    def on_touch_up(self, touch):
        super(PaletteToggleButton, self).on_touch_up(touch)
        if self.triggered:  # Event was triggered
            # self.text = "A"
            pass

    def _do_press(self):
        self._release_group(self)
        self.state = 'down' if self.state == 'down' else 'down'


class ToolBubble(Bubble):
    callbacks = {}

    @staticmethod
    def set_callback(key, function):
        if callable(function):
            ToolBubble.callbacks[key] = function
        else:
            raise NameError('function not callable')

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.app = kivy.app.App.get_running_app()
        self.pressed = None
        self.size_hint = (None, None)
        self.tool = TOOL_LINE
        self.add_widget(Button(text='line', on_press=self.on_children_press))
        self.add_widget(Button(text='rect', on_press=self.on_children_press))
        self.add_widget(Button(text='ellipse', on_press=self.on_children_press))

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            if self in self.parent.children:
                self.parent.remove_widget(self)
                # print 'hide'
        if super(ToolBubble, self).on_touch_down(touch):
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
        if super(ToolBubble, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_children_press(self, bbutton):
        if bbutton.text == 'rect':
            # self._check_and_call('rect')
            self.app.toolbar.btn_figs.text = bbutton.text
            self.app.active_tool = TOOL_RECT
            self.tool = TOOL_RECT
        elif bbutton.text == 'ellipse':
            # self._check_and_call('circle')
            self.app.toolbar.btn_figs.text = bbutton.text
            self.app.active_tool = TOOL_ELLIPSE
            self.tool = TOOL_ELLIPSE
        elif bbutton.text == 'line':
            # self._check_and_call('line')
            self.app.toolbar.btn_figs.text = bbutton.text
            self.app.active_tool = TOOL_LINE
            self.tool = TOOL_LINE
        self.parent.remove_widget(self)

    def _check_and_call(self, key):
        if ToolBubble.callbacks.has_key(key):
            if callable(ToolBubble.callbacks[key]):
                ToolBubble.callbacks[key]()
            else:
                raise NameError('callback function ' + key + ' not callable')
        else:
            raise NameError(key + ' callback not defined')


Builder.load_string('''
<Toolbar>:
    layout: box_layout.__self__
    btn_pen: button_pen.__self__
    tool_menu: tool_bubble.__self__
    btn_figs: button_figs.__self__
    BoxLayout:
        id: box_layout
        orientation: 'horizontal'
        BoxLayout:
            orientation: 'vertical'
            # ToolButton:
            #     size_hint_y: 0.5
            #     text: '<'
            #     tool: '<'
            #     on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                tool: 'erase'
                group: 'tools'
                text: 'Erase'
                on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                tool: 'fill'
                group: 'tools'
                text: 'Fill'
                on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                tool: 'select'
                group: 'tools'
                text: 'Select'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'zoomx1'
                text: 'Zoom x1'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'empty'
                text: 'Empty'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'zoomin'
                text: 'Zoom +'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'undo'
                text: 'Undo'
                on_press: root.tools_on_button_press(self)
        BoxLayout:
            orientation: 'vertical'
            # Button:
            #     size_hint_y: 0.5
            #     text: '^'
            #     tool: '^'
            #     on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                id: button_pen
                tool: 'pencil'
                group: 'tools'
                text: 'Pen'
                on_press: root.tools_on_button_press(self)
            MenuButton:
                id: button_figs
                tool: 'figures'
                group: 'tools'
                text: 'Line'
                on_press: root.tools_on_button_press(self)

            ToolToggleButton:
                tool: 'picker'
                group: 'tools'
                text: 'Picker'
                on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                tool: 'move'
                group: 'tools'
                text: 'Move'
                on_press: root.tools_on_button_press(self)
            ToolToggleButton:
                id: button_rect
                group: 'tools'
                tool: 'rect'
                text: 'Rect'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'zoomout'
                text: 'Zoom -'
                on_press: root.tools_on_button_press(self)
            ToolButton:
                tool: 'redo'
                text: 'Redo'
                on_press: root.tools_on_button_press(self)
    ToolBubble:
        id: tool_bubble
        height: button_figs.height
        width: self.height*3
        y: button_figs.y
        x: button_figs.right
        arrow_pos: 'left_mid'
        orientation: 'horizontal'
''')


class Toolbar(RelativeLayout):
    # tools_on_button_press = ObjectProperty(None)

    def __init__(self, app, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.app = app
        self.active_tool = None
        self.prev_tool = None
        # self.layout = self.toolbar_create()
        # self.layout = Factory.ToolbarLayout()

        self.pos_in = (0, TOOLBAR_LAYOUT_POS_HINT[1] * Window.height)
        self.pos_out = (-Window.width * TOOLBAR_LAYOUT_SIZE_HINT[0], TOOLBAR_LAYOUT_POS_HINT[1] * Window.height)
        self.side_hiden = False
        self.animation_show = Animation(pos=self.pos_in, transition='in_quad', duration=0.3)
        self.animation_hide = Animation(pos=self.pos_out, transition='in_quad', duration=0.3)
        self.size_hint = TOOLBAR_LAYOUT_SIZE_HINT
        self.pos = (TOOLBAR_LAYOUT_POS_HINT[0] * Window.width, TOOLBAR_LAYOUT_POS_HINT[1] * Window.height)

        self.remove_widget(self.tool_menu)


    def tools_on_button_press(self, button):
        if button.state == 'down':
            self.prev_tool = self.active_tool
            if button.tool == 'pencil':
                self.app.active_tool = TOOL_PENCIL
            if button.tool == 'erase':
                self.app.active_tool = TOOL_ERASE
            if button.tool == 'picker':
                self.app.active_tool = TOOL_PICKER
            if button.tool == 'fill':
                self.app.active_tool = TOOL_FILL
            if button.tool == 'select':
                self.app.active_tool = TOOL_SELECT
            if button.tool == 'move':
                self.app.active_tool = TOOL_MOVE
            if button.tool == 'zoomin':
                self.app.aPaint.scale_canvas(zoom=1.2)
            if button.tool == 'zoomout':
                self.app.aPaint.scale_canvas(zoom=1.0 / 1.2)
            if button.tool == 'zoomx1':
                self.app.aPaint.scale_canvas(zoom=1 / self.app.aPaint.scale)
            if button.tool == 'figures':
                self.show_tool_menu()
                self.app.active_tool = self.tool_menu.tool
            if button.tool == 'undo':
                self.app.aPaint.do_undo()
            if button.tool == 'redo':
                self.app.aPaint.do_redo()
            # if button.tool == '<':
            #     self.animate_hide()
            if button.tool == 'rect':
                self.app.active_tool = TOOL_RECT


        else:
            button._do_press()


    def tools_select(self, tool):
        if tool == TOOL_PENCIL:
            self.btn_pen._do_press()
            self.tools_on_button_press(self.btn_pen)
        elif tool == TOOL_ERASE:
            self.btn_erase._do_press()
            self.tools_on_button_press(self.btn_erase)
        elif tool == TOOL_PICKER:
            self.btn_picker._do_press()
            self.tools_on_button_press(self.btn_picker)
        elif tool == TOOL_FILL:
            self.btn_fill._do_press()
            self.tools_on_button_press(self.btn_fill)
        elif tool == TOOL_SELECT:
            self.tbtn_move._do_press()
            self.tools_on_button_press(self.tbtn_move)
        elif tool == TOOL_MOVE:
            self.btn_move._do_press()
            self.tools_on_button_press(self.btn_move)
        elif tool == TOOL_RECT:
            self.btn_rect._do_press()
            self.tools_on_button_press(self.btn_rect)

    def show_tool_menu(self, *args):
        if self.tool_menu not in self.children:
            self.add_widget(self.tool_menu)
        else:
            self.remove_widget(self.tool_menu)


    def animate_hide(self, *args):
        if not self.side_hiden:
            self.animation_hide.start(self)
            self.side_hiden = True
            #LayerBubble.hide_all()

    def animate_show(self, *args):
        if self.side_hiden:
            self.animation_show.start(self)
            self.side_hiden = False

    def animate_switch(self, *args):
        if not self.side_hiden:
            self.animate_hide()
        else:
            self.animate_show()


class Pallete(RelativeLayout):
    def __init__(self, app, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.app = app

        layout_color = BoxLayout(orientation='horizontal',
                                 size_hint=(PALLETE_LAYOUT_SIZE_HINT[0], PALLETE_LAYOUT_SIZE_HINT[1]),
                                 pos=(Window.width - (PALLETE_LAYOUT_SIZE_HINT[0] * Window.width),
                                      0))

        layout1 = BoxLayout(orientation='vertical', size_hint=PALLETE_LAYOUT_CLMN_SIZE_HINT)
        self.butList1 = [x for x in xrange(0, PALLETECOL_BTNCOUNT)]
        self.butList2 = [x for x in xrange(0, PALLETECOL_BTNCOUNT)]
        self.colorpicker_dialog = dialog.ColorPickerDialog(self.app, (Window.width, Window.height))
        for t in xrange(0, len(self.butList1)):
            self.butList1[t] = PaletteToggleButton()
            self.butList1[t].bind(on_press=partial(self.but_select, self.butList1[t]))
            self.butList1[t].on_hold = partial(self.open_colorpicker, self.butList1[t])
            self.butList1[t].background_normal = ""
            layout1.add_widget(self.butList1[t])
            self.butList1[t].background_color = (1, 0.05 * t, 0.05 * t, 1)
        layout2 = BoxLayout(orientation='vertical', size_hint=PALLETE_LAYOUT_CLMN_SIZE_HINT)
        for t in xrange(0, len(self.butList2)):
            self.butList2[t] = PaletteToggleButton()
            self.butList2[t].bind(on_press=partial(self.but_select, self.butList2[t]))
            self.butList2[t].on_hold = partial(self.open_colorpicker, self.butList2[t])
            self.butList2[t].background_normal = ""
            layout2.add_widget(self.butList2[t])
            self.butList2[t].background_color = (1, 0.05 * t, 0.05 * t, 1)

        self.butList1[0].background_color = (1, 1, 1, 1)
        self.butList1[1].background_color = (195 / 255., 195 / 255., 195 / 255., 1)
        self.butList1[2].background_color = (185 / 255., 122 / 255., 87 / 255., 1)
        self.butList1[3].background_color = (255 / 255., 174 / 255., 201 / 255., 1)
        self.butList1[4].background_color = (255 / 255., 201 / 255., 14 / 255., 1)
        self.butList1[5].background_color = (239 / 255., 228 / 255., 176 / 255., 1)
        self.butList1[6].background_color = (181 / 255., 230 / 255., 29 / 255., 1)
        self.butList1[7].background_color = (153 / 255., 217 / 255., 234 / 255., 1)
        self.butList1[8].background_color = (112 / 255., 146 / 255., 190 / 255., 1)
        self.butList1[9].background_color = (200 / 255., 191 / 255., 231 / 255., 1)

        self.butList2[0].background_color = (0, 0, 0, 1)
        self.butList2[1].background_color = (127 / 255., 127 / 255., 127 / 255., 1)
        self.butList2[2].background_color = (136 / 255., 0 / 255., 21 / 255., 1)
        self.butList2[3].background_color = (237 / 255., 28 / 255., 36 / 255., 1)
        self.butList2[4].background_color = (255 / 255., 127 / 255., 39 / 255., 1)
        self.butList2[5].background_color = (255 / 255., 242 / 255., 0 / 255., 1)
        self.butList2[6].background_color = (34 / 255., 177 / 255., 76 / 255., 1)
        self.butList2[7].background_color = (0 / 255., 162 / 255., 232 / 255., 1)
        self.butList2[8].background_color = (63 / 255., 72 / 255., 204 / 255., 1)
        self.butList2[9].background_color = (163 / 255., 73 / 255., 164 / 255., 1)

        layout_color.add_widget(layout1)
        layout_color.add_widget(layout2)
        self.add_widget(layout_color)

    def open_colorpicker(self, button, *args):
        self.colorpicker_dialog.open(color=button.background_color,
                                     on_close=partial(self.set_but_color, button))


    def set_but_color(self, button, *args):
        c = self.colorpicker_dialog.colorPicker.color
        button.background_color = c
        self.app.aColor = Color(c[0], c[1], c[2], c[3])


    def but_select(self, button, *args):
        c = button.background_color
        self.app.aColor = Color(c[0], c[1], c[2], c[3])


Builder.load_string('''
<MenuPopup>:
    id: MPopup
    title: "Menu"
    size_hint: .3, .7

    BoxLayout:
        size: root.size
        orientation: 'vertical'

        SettingSpacer:

        GridLayout:
            cols: 1
            spacing: [0, 0]
            padding: [0, 0]
            BubbleButton:
                text: "New project"
                on_release: root.new_clbk()
            BubbleButton:
                text: "Open project\image"
                on_release: root.open_clbk()
            BubbleButton:
                text: "Save project"
                on_release: root.save_project_clbk()
            BubbleButton:
                text: "Export to image"
                on_release: root.save_image_clbk()
            BubbleButton:
                text: "Config"
                on_release: root.options_clbk()
            SettingSpacer:
            BubbleButton:
                text: "Exit app"
                on_release: root.exit_clbk()
''')


class Menu(Widget):
    MButton = ObjectProperty(None)

    def __init__(self, new_clbk, open_clbk, save_project_clbk, save_image_clbk, options_clbk, exit_clbk):
        Widget.__init__(self)
        self.new_clbk = lambda: self.call_and_dismiss(new_clbk)
        self.open_clbk = lambda: self.call_and_dismiss(open_clbk)
        self.save_project_clbk = lambda: self.call_and_dismiss(save_project_clbk)
        self.save_image_clbk = lambda: self.call_and_dismiss(save_image_clbk)
        self.exit_clbk = lambda: self.call_and_dismiss(exit_clbk)
        self.options_clbk = lambda: self.call_and_dismiss(options_clbk)

        self.popup = MenuPopup(new_clbk=self.new_clbk, open_clbk=self.open_clbk,
                               save_project_clbk=self.save_project_clbk,
                               save_image_clbk=self.save_image_clbk, exit_clbk=self.exit_clbk,
                               options_clbk=self.options_clbk)

    def open(self):
        self.popup.open()

    def call_and_dismiss(self, clbk):
        if callable(clbk):
            clbk()
        self.popup.dismiss()


class MenuPopup(Popup):
    new_clbk = ObjectProperty(None)
    open_clbk = ObjectProperty(None)
    save_project_clbk = ObjectProperty(None)
    save_image_clbk = ObjectProperty(None)
    options_clbk = ObjectProperty(None)
    exit_clbk = ObjectProperty(None)

    def __init(self):
        Popup.__init__(self)


# Factory.register('MenuPopup', cls=MenuPopup)


