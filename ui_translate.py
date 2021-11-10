#!/usr/bin/python3
# coding: utf-8

import time
import gi
from api import translate
import config

gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk


VERSION = '0.0.1'


class Translate(Gtk.Window):

    n = 0

    is_hide = False

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_icon_from_file('./ui/icon.png')
        self.set_keep_above(True)

        self._create_bar()
        self._create_content()

        self.connect("delete-event", self.close)

        self.currency_combo.set_active(0)
        self.currency_combo.set_entry_text_column(0)

    def start(self):
        self.is_hide = False

        self.show_all()
        print("2活着么？ " + str(self.is_hide))

    def close(self, a=None, b=None):
        self.is_hide = True
        print("关闭")
        self.hide()
        print("3活着么？ " + str(self.is_hide))

    def _create_bar(self):

        # 定义HeaderBar
        self.hb = Gtk.HeaderBar()
        # 隐藏原有的工具按钮
        self.hb.set_show_close_button(False)
        self.hb.props.title = "兰译"
        self.set_titlebar(self.hb)

        self.btn_setting = Gtk.Button.new_with_label("设置")
        self.hb.pack_start(self.btn_setting)

        btn_update = Gtk.Button.new_with_label("翻译")
        btn_update.connect("clicked", self.update_translate_view)
        self.hb.pack_end(btn_update)

    def _create_content(self):

        self.set_border_width(10)
        self.set_default_size(400, 360)

        self.box = Gtk.Box(spacing=8, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.scroll_from = Gtk.ScrolledWindow()
        self.text_view_from = Gtk.TextView()
        self.text_view_from.set_wrap_mode(wrap_mode=Gtk.WrapMode.CHAR)
        self.scroll_from.add(self.text_view_from)
        self.box.pack_start(self.scroll_from, True, True, 0)

        self._create_language_menu()

        self.scroll_to = Gtk.ScrolledWindow()
        self.text_view_to = Gtk.TextView()
        self.text_view_to.set_wrap_mode(wrap_mode=Gtk.WrapMode.CHAR)
        self.scroll_to.add(self.text_view_to)
        self.box.pack_start(self.scroll_to, True, True, 0)

        # 选中即可，但是有时候会出现一些问题，因为选中期间，每次间断，都会回调
        # clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        # 复制以后才回调，比如快捷键复制、右键复制
        self.getClipboard().connect("owner-change", self.copy_auto_translate)

    def _create_language_menu(self):

        self.box_center = Gtk.Box(spacing=8,
                                  orientation=Gtk.Orientation.HORIZONTAL)

        self.currency_combo = Gtk.ComboBoxText()
        self.currency_combo.connect("changed", self.on_currency_combo_changed)
        for currency in config.translate_to_language_zh:
            self.currency_combo.append_text(currency)

        self.box_center.pack_start(self.currency_combo, False, False, 0)

        self.spinner = Gtk.Spinner()
        self.box_center.pack_start(self.spinner, False, True, 0)

        self.cbtn_add_old = Gtk.CheckButton.new_with_label("追加模式")
        self.box_center.pack_end(self.cbtn_add_old, False, True, 0)

        self.box.pack_start(self.box_center, False, True, 0)

    def on_currency_combo_changed(self, combo):
        text = combo.get_active_text()
        if text is None:
            text = config.translate_to_language_zh[0]
        translate.set_to_language(text)
        self.copy_translate()
        return text

    def copy_auto_translate(self, cb, event=None):
        s_from = ""
        self.spinner.start()

        image_pixbuf = cb.wait_for_image()
        if image_pixbuf is not None:
            img_path = "data/copy"
            image_pixbuf.savev(img_path, "png", "", "")
            s_from = translate.ocr(open(img_path, 'rb').read())
        else:
            s_from = cb.wait_for_text()

        self.translate_by_s(s_from)

    def copy_translate(self, view=None):
        self.copy_auto_translate(cb=self.getClipboard())

    def update_translate_view(self, view=None):

        textbuffer_from = self.text_view_from.get_buffer()

        start_iter = textbuffer_from.get_start_iter()
        end_iter = textbuffer_from.get_end_iter()
        s = textbuffer_from.get_text(start_iter, end_iter, True)

        self.translate_by_s(s_from=s)

    def translate_by_s(self, s_from):

        self.n += 1

        textbuffer_from = self.text_view_from.get_buffer()
        textbuffer_to = self.text_view_to.get_buffer()

        if(s_from is None):
            s_from = "复制即可翻译"
            s_to = "Alt Q 快捷键、或状态栏图标可隐藏"
        else:
            s_from, s_to = translate.text(
                s_from.strip(), add_old=self.cbtn_add_old.get_active())

        textbuffer_from.set_text(s_from.strip())
        textbuffer_to.set_text(s_to.strip())
        self.spinner.stop()

    def getClipboard(self):
        if(config.translate_select):
            return Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        else:
            return Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)


# win = Translate()

# Gtk.main()