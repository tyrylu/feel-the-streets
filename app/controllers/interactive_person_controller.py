import wx
from pygeodesy.ellipsoidalVincenty import LatLon
from shared.entities import Road
from ..uimanager import get, menu_command
from ..services import speech
from ..objects_browser import ObjectsBrowserDialog
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..geometry_utils import get_road_section_angle, distance_filter
from ..search import perform_search

class InteractivePersonController: 
    def __init__(self, person):
        self._person = person
        get().register_menu_commands(self)
    
    @menu_command("Informace", "Aktuální souřadnice", "c")
    def do_current_coords(self, evt):
        speech().speak("Zeměpisná délka: %s, zeměpisná šířka: %s."%(self._person.position.lon, self._person.position.lat))
    @menu_command("Informace", "Pozice", "l")
    def do_position(self, evt):
        position_known = False
        for obj in self._person.is_inside_of:
            position_known = True
            speech().speak(str(obj))
        if not position_known:
            speech().speak("Není známo.")
    @menu_command("Informace", "Aktuální pozice podrobně", "shift+l")
    def do_position_detailed(self, evt):
        filtered_inside_of = distance_filter((entity.db_entity for entity in self._person.is_inside_of), self._person.position, float("inf"))
        dlg = get().prepare_xrc_dialog(ObjectsBrowserDialog, title="Aktuální pozice", unsorted_objects=self._person.is_inside_of, person=self._person)
        if dlg.ShowModal() == 1:
            self._person.move_to(dlg.selected_object[2])
        dlg.Destroy()
    @menu_command("Informace", "Nejbližší", "n")
    def do_nearest(self, evt):
        objects = self._person.map.within_distance(self._person.position, 100)
        if not objects:
            speech().speak("Nic.")
            return
        dlg = get().prepare_xrc_dialog(ObjectsBrowserDialog, title="Blízké objekty", person=self._person, unsorted_objects=objects)
        action = dlg.ShowModal()
        if action == 1:
            self._person.move_to(dlg.selected_object[2])
        dlg.Destroy()   
    @menu_command("Pohyb", "Krok vpřed", "up")
    def do_forward(self, evt):
        self._person.step_forward() 
    @menu_command("Pohyb", "Krok vzad", "down")
    def do_backward(self, evt):
        self._person.step_backward() 
    @menu_command("Pohyb", "Otočit o 5 stupňů do prava", "right")
    def turn_right(self, evt):
        self._person.rotate(5)
    @menu_command("Pohyb", "Otočit o 5 stupňů do leva", "left")
    def turn_left(self, evt):
        self._person.rotate(-5)
    @menu_command("Informace", "Aktuální směr", "r")
    def do_current_rotation(self, evt):
        speech().speak("%s stupňů"%self._person.direction)
    @menu_command("Pohyb", "Otočit o 90 stupňů do prava", "ctrl+right")
    def turn_right90(self, evt):
        self._person.rotate(90)
    @menu_command("Pohyb", "Otočit o 90 stupňů do leva", "ctrl+left")
    def turn_left90(self, evt):
        self._person.rotate(-90)
    @menu_command("Pohyb", "Skok na souřadnice...", "j")
    def do_jump(self, evt):
        x = wx.GetTextFromUser("Zadejte zeměpisnou délku", "Souřadnice")
        y = wx.GetTextFromUser("Zadejte zeměpisnou šířku", "Souřadnice")
        self._person.move_to(LatLon(y, x))

    @menu_command("Informace", "Úhel aktuální části cesty", "d")
    def current_road_section_angle(self, evt):
         for obj in self._person.is_inside_of:
            if isinstance(obj, Road) and not obj.area:
                angle = get_road_section_angle(self._person, obj)
                speech().speak("%s: %.2f°"%(obj, angle))

    @menu_command("Informace", "Detaily cesty", "ctrl+d")
    def road_details(self, evt):
        road = self._maybe_select_road()
        if not road or road.area:
            return
        dlg = get().prepare_xrc_dialog(RoadSegmentsBrowserDialog, person=self._person, road=road)
        dlg.ShowModal()
        dlg.Destroy()

    @menu_command("Pohyb", "Otočit se podle cesty", "shift+d")
    def rotate_to_road(self, evt):
        print("Rotate?")
        road = self._maybe_select_road()
        if not road:
            return
        rot = get_road_section_angle(self._person, road)
        self._person.direction = rot

    @menu_command("Pohyb", "Otočit o...", "Ctrl+r")
    def rotate_by(self, evt):
        amount = wx.GetTextFromUser("Zadej úhel", "Údaj")
        self._person.direction += float(amount)
    def _maybe_select_road(self):
        roads = [r for r in self._person.is_inside_of if isinstance(r, Road)]
        if not roads:
            return None
        if len(roads) == 1:
            return roads[0]
        else:
            road_reprs = [str(r) for r in roads]
            road_idx = wx.GetSingleChoice("Zvolte cestu, nad kterou se má operace provést", "Požadavek", aChoices=road_reprs)
            if road_idx is not None:
                return roads[road_reprs.index(road_idx)]
            else:
                return None
            
    @menu_command("Informace", "Hledat...", "ctrl+f")
    def do_search(self, evt):
        results = perform_search(self._person.position)
        if results:
            browser = get().prepare_xrc_dialog(ObjectsBrowserDialog, title="Výsledky vyhledávání", unsorted_objects=results, person=self._person)
            if browser.ShowModal() == 1:
                self._person.move_to(browser.selected_object[2])
                browser.Destroy()
        else:
            wx.MessageBox("Zadaným podmínkám vyhledávání neodpovídá žádný objekt.", "Informace", style=wx.ICON_INFORMATION)