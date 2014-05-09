from copy import copy
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.vector import Vector


class TapAndHoldWidget(Widget):
    ''' A tap and hold mixIn for widgets '''
    _point = None  # Contains point after trigger
    _sensitivity = 4  # Sensitivity (pixels)
    _hold_length = 1.4  # Seconds
    _event = None  # Outstanding event or none
    triggered = False  # Whether or not the event was triggered

    def _distance(self, touch):
        ''' Calculate distance moved from start '''
        if self._point is not None:
            return Vector(touch.pos).distance(self._point.pos)
        return 0

    def _release_event(self):
        ''' Free up and cancel any outstanding event '''
        if self._event is not None:
            self._event.release()  # stop any outstanding events
        self._event = None

    def _long_hold(self, _dt):
        ''' Comes here after a tap and hold '''
        if self._event is not None:
            self.triggered = True
            self.on_hold(self._point)  # Generate event
            self._release_event()

    def on_touch_down(self, touch):
        ''' touch down event '''
        if self.collide_point(touch.x, touch.y):  # filter touch events
            self.triggered = False
            self._release_event()
            self._point = copy(touch)  # Touch events share an instance
            self._event = Clock.schedule_once(self._long_hold, self._hold_length)

    def on_touch_move(self, touch):
        ''' If there was movement, invalidate the tap+hold '''
        dxy = self._distance(touch)
        if dxy > self._sensitivity:
            self._point = None  # No event triggered
            self._release_event()

    def on_touch_up(self, touch):
        ''' Tap+hold is finished if it was effective '''
        self._point = None
        self._release_event()

    def on_hold(self, touch):
        ''' To be implemented by concrete class '''

        # from kivy.lang import Builder
        # from kivy.app import App
        # from kivy.uix.label import Label
        # from kivy.uix.boxlayout import BoxLayout
        # from kivy.properties import ObjectProperty
        # # from tnhWidget import TapAndHoldWidget
        #
        # Builder.load_string('''
        # <TnHDemo>:
        #     tnh: tnh
        #     wid: wid
        #     orientation: 'vertical'              # Vertically grouped boxes
        #     Label:
        #         id: wid
        #         canvas.before:
        #             Color:
        #                 rgba: .95,.95,.5,1
        #             Rectangle:
        #                 pos: self.pos
        #                 size: self.size
        #         color: 0.2,0.2,0.8,1.0           # Text label colour
        #         text: 'Ordinary Label'
        #
        #     ConcreteTnH:
        #         id: tnh
        #         canvas.before:
        #             Color:
        #                 rgba: .5,.95,.5,1
        #             Rectangle:
        #                 pos: self.pos
        #                 size: self.size
        #         color: 0.2,0.2,0.2,1.0           # Text Colour
        #         text: self.text or 'tap and hold in this area'
        # ''')
        #
        #
        # class ConcreteTnH(Label, TapAndHoldWidget):
        #     ''' Our example Label+TapAndHoldWidget mixIn '''
        #     def on_hold(self, point):
        #         self.text = "Got tap and hold at x:%s,y:%s" % (point.x, point.y)
        #     def on_touch_up(self, touch):
        #         super(ConcreteTnH, self).on_touch_up(touch)
        #         if self.triggered:  # Event was triggered
        #             self.text = "Tap and hold again..."
        #
        # class TnHDemo(BoxLayout):
        #     tnh = ObjectProperty()
        #     wid = ObjectProperty()
        #
        # class TnHApp(App):
        #     def build(self):
        #         return TnHDemo()
        #
        # if __name__ == '__main__':
        #     TnHApp().run()