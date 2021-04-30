from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.graphics import *
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.screenmanager import FadeTransition
from kivy.utils import platform
txr_size = 33
if platform != 'android':
    from screeninfo import get_monitors
    for m in get_monitors():
        print(str(m.width), str(m.height))
    the_small = m.width if m.width <= m.height else m.height
    the_small = int(the_small*0.9)
    Config.set('graphics', 'width', the_small)
    Config.set('graphics', 'height', the_small)
    window_height = Config.getint('graphics', "height")
    window_width = Config.getint('graphics', "width")
    # size_fixer = window_width / window_height
    size_fixer = 1
else:
    from kivy.core.window import Window
    Window.fullscreen = True
    window_height = Config.getint('graphics', "height")
    window_width = Config.getint('graphics', "width")
    size_fixer = window_width / window_height

inbox_posx = (0.255 * window_width, 0.745 * window_width)
inbox_posy = ((0.1*size_fixer + 0.15 * size_fixer) * window_width,
              (0.1 * size_fixer + 0.64 * size_fixer) * window_width)
Config.set('graphics', 'resizable', False)
# 0:Orange 1:White 2:Blue 3:Green 4:Yellow
color_dic = {0: "Orange", 1: "White", 2: "Blue", 3: "Green", 4: "Yellow"}
camel_color_lst = {0: (0.9, 0.54, 0, 1), 1: (1, 1, 1, 1), 2: (0.1, 0.1, 0.9, 1), 3: (.1, .9, .1, 1), 4: (1, 1, 0, 1)}
camelSelectBtns = []
boardBtns = []
camelSelectionMode = False
diceSelectionMode = False
selectedCamel = -1
camels_order = []
availabledice = []
tgl_btn_state = False
trap = -1
trap_mode = False
trap_list = []
chx_lst = []
sm = ScreenManager(transition=FadeTransition())


def init_vars():
    # 0:Orange 1:White 2:Blue 3:Green 4:Yellow
    global camelSelectBtns, boardBtns, camelSelectionMode, diceSelectionMode, selectedCamel, camels_order, availabledice
    global tgl_btn_state, trap, trap_mode, trap_list, chx_lst
    chx_lst = []
    camelSelectBtns = []
    boardBtns = []
    camelSelectionMode = False
    diceSelectionMode = False
    selectedCamel = -1
    camels_order = []
    availabledice = []
    tgl_btn_state = False
    trap = -1
    trap_mode = False
    trap_list = []


class Gdl(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 8
        self.rows = 6

    def add_views(self, last_pos, all_moves_count):
        first_r_list = ["Back", "1st", "2nd", "last", "won", "2P", "3P", "5p"]
        all_lbls = []
        for i in range(5):
            temp = []
            result = last_pos[i]
            for j in range(7):
                if j < 4:
                    txt = str(round(100 * (result[j] / all_moves_count), 4)) + " %"
                else:
                    firsts = result[0]
                    seconds = result[1]
                    multi = 1
                    if j == 4: multi = 2
                    if j == 5: multi = 3
                    if j == 6: multi = 5
                    txt = str(round((firsts * multi + seconds - (all_moves_count - firsts - seconds))
                                    /all_moves_count, 3))
                temp.append(Button(text=txt,font_size=txr_size, color=(0, 0, 0, 1), background_normal="",
                                   background_color=camel_color_lst.get(i)))
            all_lbls.append(temp)

        for i in range(6):
            for j in range(8):
                if i == 0:
                    clr = 0.9 if j == 0 else 0.1
                    btn = Button(text=first_r_list[j],font_size=txr_size, color=(1, 1, 1, 1),
                                 background_normal="", background_color=(clr, 0.1, 0.1, 1))
                    if j == 0: btn.bind(on_press=self.on_prev_page)
                    self.add_widget(btn)
                else:
                    if j == 0:
                        self.add_widget(Button(text=color_dic.get(i - 1),font_size=txr_size,
                                               color=(0, 0, 0, 1), background_normal="",
                                               background_color=camel_color_lst.get(i - 1)))
                    else:
                        self.add_widget(all_lbls[i - 1][j - 1])

    def on_prev_page(self, elem):
        sm.current = "1"


class Flt(FloatLayout):
    global size_fixer, camelSelectBtns, boardBtns, selectedCamel, camelSelectionMode, camel_color_lst
    global camels_order, chx_lst
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tgl_btn = None
        self.last_pos = []
        showlist = [0, 4]
        counter = 1
        for i in range(0, 5):
            if i == 4:
                rng = range(4, 0, -1)
            else:
                rng = range(1, 5)
            for j in rng:
                if i in showlist or j == 4:
                    bts = Button(
                        size_hint=(0.15, 0.15 * size_fixer), font_size=txr_size,
                        text=str(int(counter)),
                        pos_hint={"x": 0.745 - j * 0.16, "y": 0.1*size_fixer + i * 0.16 * size_fixer},
                        background_color=(0.75, 0.75, 0.75, 1),
                        background_normal="",
                        color=(0, 0, 0, 1)
                    )
                    bts.bind(on_press=self.on_board_select)
                    bts.tag = counter
                    counter = counter + 1
                    boardBtns.append(bts)
                    self.add_widget(bts)
        for i in range(4, -1, -1):
            bts = Button(
                size_hint=(0.15, 0.15 * size_fixer), font_size=txr_size,
                text=str(int(counter)),
                pos_hint={"x": 0.745, "y": 0.1 * size_fixer + i * 0.16 * size_fixer},
                background_color=(0.75, 0.75, 0.75, 1),
                background_normal="",
                color=(0, 0, 0, 1)
            )
            # bts.bind(on_press=lambda elem:self.on_board_select(elem,num=counter))
            bts.bind(on_press=self.on_board_select)
            bts.tag = counter
            counter = counter + 1
            boardBtns.append(bts)
            self.add_widget(bts)

        self.midlbl = Label(
            text="Put the camels on the board", size_hint=(0.2, 0.05 * size_fixer),
            pos_hint={"x": 0.405, "y": 0.1*size_fixer + 0.58 * size_fixer}, font_size=txr_size,
        )
        self.add_widget(self.midlbl)
        for i in range(5):
            if i < 3:
                onedown = 0
                toleft = 0
            else:
                onedown = -0.156 * size_fixer
                toleft = -0.39

            camel = Button(
                background_color=camel_color_lst[i], size_hint=(0.146, 0.146 * size_fixer),
                pos_hint={"x": 0.27 + toleft + i * 0.156, "y": 0.1*size_fixer + onedown + 0.40 * size_fixer},
                background_normal='', font_size=txr_size,
            )
            camel.tag = i
            camel.bind(on_press=self.on_camel_select)
            camelSelectBtns.append(camel)
            self.add_widget(camel)
            self.enable_board_btns(False)
        # 0.265- 0.745

    @staticmethod
    def enable_board_btns(bl):
        for btn in boardBtns:
            btn.disabled = not bl

    @staticmethod
    def enable_camle_btns(bl):
        for btn in camelSelectBtns:
            btn.disabled = not bl

    def on_board_select(self, elem):
        global chx_lst
        inx = elem.tag
        global camelSelectionMode, diceSelectionMode
        if camelSelectionMode:
            # tile = 1
            # for i in camels_order:
            #     if i[0]  tile:
            #         tile = i[0]
            # # if inx < tile:
            # #     return
            if len(camelSelectBtns) != 0:
                self.enable_board_btns(False)
                self.enable_camle_btns(True)
            else:
                diceSelectionMode = True
                camelSelectionMode = False
            didntadd = True
            for i in camels_order:
                if i[0] == inx:
                    i.append(selectedCamel)
                    with elem.canvas:
                        *z, a = camel_color_lst[selectedCamel]
                        Color(*z, a)
                        Rectangle(pos=(elem.pos[0], elem.pos[1] + elem.size[1] / 5 * (len(i) - 2)),
                                  size=(elem.size[0] / 3, elem.size[1] / 5))
                    didntadd = False
            if didntadd:
                camels_order.append([inx, selectedCamel])
                with elem.canvas:
                    *z, a = camel_color_lst[selectedCamel]
                    Color(*z, a)
                    Rectangle(pos=(elem.pos[0], elem.pos[1]),
                              size=(elem.size[0] / 3, elem.size[1] / 5))
        if diceSelectionMode:
            self.midlbl.text = "Choose remaining dice"
            for i in range(5):
                if i < 3:
                    onedown = 0
                    toleft = 0
                else:
                    onedown = -0.1 * size_fixer
                    toleft = -0.26
                objx = 0.365 + toleft + i * 0.1
                objy = 0.1 + onedown + 0.45 * size_fixer
                obj_size = 0.08
                chx = CheckBox(
                    size_hint=(obj_size, obj_size),
                    pos_hint={"x": objx, "y": objy},
                    color=(0, 0, 0, 1),
                )
                chx.tag = i
                chx.bind(active=self.on_chx_select)
                objy *= window_width
                objx *= window_width
                obj_size *= window_width
                with self.canvas:
                    *z, a = camel_color_lst[i]
                    Color(*z, a)
                    Rectangle(pos=(objx, objy),
                              size=(obj_size, obj_size))
                self.add_widget(chx)
                chx_lst.append(chx)

            objx = 0.405
            objy = 0.1 + 0.2 * size_fixer
            nxtbtn = Button(
                text="Next", size_hint=(.2, .08 * size_fixer),
                pos_hint={"x": objx, "y": objy},
                background_normal="", color=(0, 0, 0, 1),
                background_color=(0.9, 0.9, .9, 1),font_size=txr_size,
            )
            nxtbtn.bind(on_press=self.on_next_button)
            self.add_widget(nxtbtn)
            self.enable_board_btns(False)
        if trap_mode:
            for i in camels_order:
                if i[0] == elem.tag:
                    return
            for i in trap_list:
                if i[0] == elem.tag - 1 or i[0] == elem.tag + 1:
                    return
            for i in trap_list:
                if i[0] == elem.tag:
                    trap_list.remove(i)
                    break
            trap_list.append([elem.tag, trap])
            if trap == 1:
                strtrap = "+1"
            else:
                strtrap = "-1"
            elem.text = "{} \n {}".format(str(elem.tag), strtrap)
            return

    def on_chx_select(self, elem, value):
        if value:
            availabledice.append(elem.tag)
        else:
            availabledice.remove(elem.tag)

    def on_next_button(self, elem):
        global diceSelectionMode, trap_mode, chx_lst
        if diceSelectionMode:
            self.enable_board_btns(True)
            diceSelectionMode = False
            trap_mode = True
            for i in chx_lst:
                self.remove_widget(i)
            self.remove_widget(elem)
            with self.canvas:
                Color(0, 0, 0, 1)
                Rectangle(pos=(inbox_posx[0], inbox_posy[0]),
                          size=(inbox_posx[1] - inbox_posx[0], inbox_posy[1] - inbox_posy[0]))
            self.remove_widget(self.midlbl)
            self.add_widget(self.midlbl)
            self.add_widget(elem)
            self.midlbl.text = "Place traps (click to change)"
            self.tgl_btn = ToggleButton(
                text="-1", font_size=txr_size,
                pos_hint={
                    "x": (inbox_posx[0] + (inbox_posx[1] - inbox_posx[0] - 0.15 * window_width) / 2) / window_width,
                    "y": inbox_posy[1] / window_width - 0.2 * size_fixer},
                size_hint=(0.15, 0.075)
            )
            self.tgl_btn.bind(on_press=self.on_tgl_btn)
            self.add_widget(self.tgl_btn)
            return
        if trap_mode:
            trap_mode = False
            self.remove_widget(elem)
            self.remove_widget(self.tgl_btn)
            self.midlbl.text = "Calculation Completed"
            self.enable_board_btns(False)
            calc = Calculations()
            self.last_pos = calc.move_camels(calc.all_moves(availabledice))
            all_moves_count = len(self.last_pos)
            self.last_pos = calc.analise_orders(self.last_pos)
            button_width = (inbox_posx[1] - inbox_posx[0]) / 3 / window_width
            next_page_btn = Button(text="Calculation page", size_hint=(button_width, button_width / 1.7),
                                   pos_hint={"x": inbox_posx[0] / window_width + button_width,
                                             "y": self.midlbl.pos_hint.get("y") - self.midlbl.size_hint[
                                                 1] - button_width / 1.5}, font_size=txr_size,
                                   background_color=(.2, 1, 1, 1))
            redo_btn = Button(text="Redo", size_hint=(button_width, button_width / 1.7),
                              pos_hint={"x": inbox_posx[0] / window_width + button_width,
                                        "y": self.midlbl.pos_hint.get("y") - self.midlbl.size_hint[
                                            1] - button_width / 1.5 - button_width},
                              background_color=(1, .2, .2, 1),font_size=txr_size,
                              )
            next_page_btn.bind(on_press=self.on_next_page_pressed)
            redo_btn.bind(on_press=self.on_redo_pressed)
            self.add_widget(redo_btn)
            self.add_widget(next_page_btn)
            screen2: Screen = sm.get_screen(name="2")
            with self.canvas:
                Color(0, 0, 0.1, 0.5)
            Rectangle(size=self.size, pos=self.pos)
            grid_l = Gdl()
            screen2.add_widget(grid_l)
            grid_l.add_views(self.last_pos, all_moves_count)

    def on_redo_pressed(self, elem):
        CmlApp.stop()
        init_vars()
        CmlApp.run()

    def on_next_page_pressed(self, elem):
        sm.current = "2"

    def on_tgl_btn(self, tgl):
        global trap
        if tgl.state == "down":
            tgl.text = "+1"
            trap = +1
        else:
            tgl.text = "-1"
            trap = -1

    def on_camel_select(self, elem):
        global camelSelectionMode, selectedCamel
        camelSelectionMode = True
        selectedCamel = elem.tag
        self.enable_camle_btns(False)
        self.remove_widget(elem)
        camelSelectBtns.remove(elem)
        self.enable_board_btns(True)


class Calculations:

    def __init__(self):
        self.shuffled_dice_list = []

    def all_moves(self, dicelst: list):
        self.__shuffle_dice__(dicelst)
        return self.roll_dice(self.shuffled_dice_list)

    def __shuffle_dice__(self, dicelst: list, shuffling_lst=None):
        if shuffling_lst is None:
            shuffling_lst = []
        for i in dicelst:
            temp_shuffling_lst = shuffling_lst.copy()
            temp_shuffling_lst.append(i)
            temp_dice_list = dicelst.copy()
            temp_dice_list.remove(i)
            if len(temp_dice_list) == 0:
                self.shuffled_dice_list.append(temp_shuffling_lst)
                return
            self.__shuffle_dice__(temp_dice_list, temp_shuffling_lst)

    @staticmethod
    def roll_dice(shuflled_dice):
        all_moves = []
        for dice_order in shuflled_dice:
            rolled_dice = [[]]
            for each_dice in dice_order:
                temp_rolled_dice = []
                for item in rolled_dice:
                    for num in range(1, 4):
                        new = item.copy()
                        new.append(each_dice)
                        new.append(num)
                        temp_rolled_dice.append(new)
                rolled_dice = temp_rolled_dice.copy()
                temp_rolled_dice.clear()
            all_moves = all_moves + rolled_dice
        return all_moves

    @staticmethod
    def move_camels(all_moves: list):
        global camels_order, trap_list
        all_last_positions = []
        for single_move in all_moves:
            neworder = []
            for orders in camels_order:
                temp = orders.copy()
                neworder.append(temp)
            for i in range(0, len(single_move), 2):
                dice_color = single_move[i]
                dice_number = single_move[i + 1]
                camels_to_move = []
                camel_found = False
                for tile_with_camel in neworder:
                    if camel_found:
                        break
                    j = 1
                    while j < len(tile_with_camel):
                        camel_in_tile = tile_with_camel[j]
                        if camel_in_tile == dice_color:
                            camel_found = True
                            camels_first_tile = tile_with_camel[0]
                        if camel_found:
                            camels_to_move.append(tile_with_camel.pop(j))
                            j -= 1
                        j += 1
                    if len(tile_with_camel) == 1:
                        neworder.remove(tile_with_camel)

                trap_in_dest = 0
                for tp in trap_list:
                    if tp[0] == camels_first_tile + dice_number:
                        trap_in_dest = tp[1]
                        break

                if trap_in_dest == -1:
                    minustrap = True
                else:
                    minustrap = False
                camels_final_tile = camels_first_tile + dice_number + trap_in_dest
                final_tile_has_camel = False
                for tile_with_camel in neworder:
                    if tile_with_camel[0] == camels_final_tile:
                        final_tile_has_camel = True
                        if minustrap:
                            for j in range(len(camels_to_move)):
                                tile_with_camel.insert(j + 1, camels_to_move[j])
                        else:
                            for cml in camels_to_move:
                                tile_with_camel.append(cml)
                        break

                if not final_tile_has_camel:
                    new_tile_with_camel = [camels_final_tile] + camels_to_move
                    neworder.append(new_tile_with_camel)
                if camels_final_tile > 16:
                    break
            all_last_positions.append(neworder)
        return all_last_positions

    @staticmethod
    def analise_orders(all_orders):
        first_second_last_won = []
        for i in range(5):
            temp = []
            for j in range(4):
                temp.append(0)
            first_second_last_won.append(temp)
        for each_order in all_orders:
            first = [0]
            second = [0]
            last = [100]
            for tile_with_camel in each_order:
                if tile_with_camel[0] > first[0]:
                    first = tile_with_camel
                if tile_with_camel[0] < last[0]:
                    last = tile_with_camel
            for tile_with_camel in each_order:
                if second[0] < tile_with_camel[0] < first[0]:
                    second = tile_with_camel

            firt_leghth = len(first)
            indx = first[firt_leghth - 1]
            temp = first_second_last_won[indx]
            temp[0] = temp[0] + 1
            if first[0] > 16:
                temp[3] = temp[3] + 1
            if firt_leghth > 2:
                indx = first[firt_leghth - 2]
                temp = first_second_last_won[indx]
                temp[1] = temp[1] + 1
            else:
                indx = second[len(second) - 1]
                temp = first_second_last_won[indx]
                temp[1] = temp[1] + 1

            indx = last[1]
            temp = first_second_last_won[indx]
            temp[2] = temp[2] + 1
        return first_second_last_won


class CamelUpStimulator(App):
    def __init__(self):
        super().__init__()
        self.lt = None

    def build(self):
        sm.clear_widgets()
        screen1 = Screen(name="1")
        screen2 = Screen(name="2")
        sm.add_widget(screen1)
        screen1.add_widget(Flt())
        sm.add_widget(screen2)
        sm.current = "1"
        return sm


if __name__ == '__main__':
    CmlApp = CamelUpStimulator()
    CmlApp.run()
