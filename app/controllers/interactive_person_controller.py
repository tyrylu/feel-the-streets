import wx
from pygeodesy.ellipsoidalVincenty import LatLon
from ..humanization_utils import describe_entity
from ..services import speech, map
from ..objects_browser import ObjectsBrowserFrame
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..geometry_utils import get_road_section_angle, distance_filter
from ..search import perform_search
from uimanager import get, menu_command

class InteractivePersonController: 
    def __init__(self, person):
        self._person = person
        get().register_menu_commands(self)
    
    @menu_command(_("Information"), _("Current coordinates"), "c")
    def do_current_coords(self, evt):
        speech().speak(("Longitude: {longitude}, latitude: {latitude}.").format(longitude=self._person.position.lon, latitude=self._person.position.lat))

    def _position_impl(self, objects):    
        position_known = False
        for obj in self._person.is_inside_of:
            position_known = True
            speech().speak(describe_entity(obj))
        if not position_known:
            speech().speak(_("Not known."))
    
    @menu_command(_("Information"), _("Position"), "l")
    def do_position(self, evt):
        self._position_impl(self._person.is_inside_of)
    
    @menu_command(_("Information"), _("Position - all objects, may be slow"), "ctrl+l")
    def do_position_slow(self, evt):
        self._position_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _position_detailed_impl(self, objects):
        dlg = get().prepare_xrc_frame(ObjectsBrowserFrame, title=_("Current position"), unsorted_objects=self._person.is_inside_of, person=self._person)
        dlg.Show()
    
    @menu_command(_("Information"), _("Detailed current position"), "shift+l")
    def position_detailed(self, evt):
        self._position_detailed_impl(self._person.is_inside_of)

    @menu_command(_("Information"), _("Detailed current position - all objects, may be slow"), "ctrl+shift+l")
    def do_position_detailed_slow(self, evt):
        self._position_detailed_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _nearest_impl(self, objects):
        if not objects:
            speech().speak(_("Nothing."))
            return
        dlg = get().prepare_xrc_frame(ObjectsBrowserFrame, title=_("Near by objects"), person=self._person, unsorted_objects=objects)
        dlg.Show()
    
    @menu_command(_("Information"), _("Nearest"), "n")
    def do_nearest(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, 100))

    @menu_command(_("Information"), _("Nearest - all objects, may be slow"), "ctrl+n")
    def do_nearest_slow(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, 100, fast=False))
    
    @menu_command(_("Movement"), _("Step forward"), "up")
    def do_forward(self, evt):
        self._person.step_forward() 

    @menu_command(_("Movement"), _("Step backward"), "down")
    def do_backward(self, evt):
        self._person.step_backward() 
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the right"), "right")
    def turn_right(self, evt):
        self._person.rotate(5)
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the left"), "left")
    def turn_left(self, evt):
        self._person.rotate(-5)
    
    @menu_command(_("Information"), _("Current direction"), "r")
    def do_current_rotation(self, evt):
        speech().speak(_("{degrees} degrees").format(degrees=self._person.direction))
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the right"), "ctrl+right")
    def turn_right90(self, evt):
        self._person.rotate(90)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the left"), "ctrl+left")
    def turn_left90(self, evt):
        self._person.rotate(-90)
    
    @menu_command(_("Movement"), _("Coordinate jump..."), "j")
    def do_jump(self, evt):
        x = wx.GetTextFromUser(_("Enter the longitude"), _("Coordinate"))
        y = wx.GetTextFromUser(_("Enter the latitude"), _("Coordinate"))
        self._person.move_to(LatLon(y, x))

    @menu_command(_("Information"), _("Current road section angle"), "d")
    def current_road_section_angle(self, evt):
         for obj in self._person.is_inside_of:
            if obj.discriminator == "Road" and not obj.value_of_field("area"):
                angle = get_road_section_angle(self._person, obj)
                speech().speak(_("{road}: {angle:.2f}°").format(road=describe_entity(obj), angle=angle))

    @menu_command(_("Information"), _("Road details"), "ctrl+d")
    def road_details(self, evt):
        road = self._maybe_select_road()
        if not road or road.value_of_field("area"):
            return
        dlg = get().prepare_xrc_dialog(RoadSegmentsBrowserDialog, person=self._person, road=road)
        dlg.ShowModal()
        dlg.Destroy()

    @menu_command(_("Movement"), _("Turn according to a road"), "shift+d")
    def rotate_to_road(self, evt):
        road = self._maybe_select_road()
        if not road:
            return
        rot = get_road_section_angle(self._person, road)
        self._person.direction = rot

    @menu_command(_("Movement"), _("Turn about..."), "Ctrl+r")
    def rotate_by(self, evt):
        amount = wx.GetTextFromUser(_("Enter the angle"), _("Data"))
        self._person.direction += float(amount)
    
    def _maybe_select_road(self):
        roads = [r for r in self._person.is_inside_of if r.discriminator == "Road"]
        if not roads:
            return None
        if len(roads) == 1:
            return roads[0]
        else:
            road_reprs = [describe_entity(r) for r in roads]
            road_idx = wx.GetSingleChoice(_("Select the road which should be the target of the operation"), _("Request"), aChoices=road_reprs)
            if road_idx is not None:
                return roads[road_reprs.index(road_idx)]
            else:
                return None
            
    @menu_command(_("Information"), _("Search..."), "ctrl+f")
    def do_search(self, evt):
        results = perform_search(self._person.position)
        if results:
            browser = get().prepare_xrc_frame(ObjectsBrowserFrame, title=_("Search results"), unsorted_objects=results, person=self._person)
            browser.Show()
        else:
            wx.MessageBox(_("No object matches the given search criteria."), _("Information"), style=wx.ICON_INFORMATION)
    
    @menu_command(_("Bookmarks"), _("Add bookmark..."), "ctrl+b")
    def add_bookmark(self, evt):
        name = wx.GetTextFromUser(_("Enter a name for the new bookmark"), _("Data entry"))
        if not name:
            return
        self._person.map.add_bookmark(name, lon=self._person.position.lon, lat=self._person.position.lat)
    
    @menu_command(_("Bookmarks"), _("Go to bookmark..."), "b")
    def go_to_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        names = [b.name for b in bookmarks]
        name = wx.GetSingleChoice(_("Select a bookmark"), _("Data entry"), aChoices=names)
        if not name:
            return
        bookmark = bookmarks[names.index(name)]
        self._person.move_to(LatLon(bookmark.latitude, bookmark.longitude))

    @menu_command(_("Bookmarks"), _("Remove bookmark..."), "ctrl+shift+b")
    def remove_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        reprs = [_("{name}: longitude: {longitude}, latitude: {latitude}").format(name=b.name, longitude=b.longitude, latitude=b.latitude) for b in bookmarks]
        repr = wx.GetSingleChoice(_("Select a bookmark"), _("Data entry"), aChoices=reprs)
        if not repr:
            return
        bookmark = bookmarks[reprs.index(repr)]
        if wx.MessageBox(_("Do you really want to delete the bookmark {name}?").format(name=bookmark.name), _("Question"), style=wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT) == wx.YES:
            map().remove_bookmark(bookmark)
