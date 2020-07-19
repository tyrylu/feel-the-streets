from PySide2.QtWidgets import QInputDialog, QMessageBox
from pygeodesy.ellipsoidalVincenty import LatLon
from ..humanization_utils import describe_entity
from ..services import speech, map, config
from ..objects_browser import ObjectsBrowserWindow
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..geometry_utils import get_road_section_angle, distance_filter
from ..search import perform_search
from ..services import menu_service
from ..menu_service import menu_command

class InteractivePersonController: 
    def __init__(self, person, main_window):
        self._person = person
        self._main_window = main_window
        self._browser_window = None
        menu_service().register_menu_commands(self)
        menu_service().menu_item_with_name("toggle_disallow_leave_roads").setChecked(config().navigation.disallow_leaving_roads)
    
    @menu_command(_("Information"), _("Current coordinates"), "c")
    def do_current_coords(self, evt):
        lat = round(self._person.position.lat, config().presentation.coordinate_decimal_places)
        lon = round(self._person.position.lon, config().presentation.coordinate_decimal_places)
        speech().speak(_("Longitude: {longitude}, latitude: {latitude}.").format(longitude=lon, latitude=lat))

    def _position_impl(self, objects):    
        if objects:
            for obj in objects:
                speech().speak(describe_entity(obj))
        else:
            speech().speak(_("Not known."))
    
    @menu_command(_("Information"), _("Position"), "l")
    def do_position(self, evt):
        self._position_impl(self._person.is_inside_of)
    
    @menu_command(_("Information"), _("Position - all objects, may be slow"), "ctrl+l")
    def do_position_slow(self, evt):
        self._position_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _position_detailed_impl(self, objects):
        window = ObjectsBrowserWindow(self._main_window, title=_("Current position"), unsorted_objects=self._person.is_inside_of, person=self._person)
        window.show()
        self._browser_window = window
    
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
        self._browser_window = ObjectsBrowserWindow(self._main_window, title=_("Near by objects"), person=self._person, unsorted_objects=objects)
        self._browser_window.show()

    @menu_command(_("Information"), _("Nearest"), "n")
    def do_nearest(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, 100))

    @menu_command(_("Information"), _("Nearest - all objects, may be slow"), "ctrl+n")
    def do_nearest_slow(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, 100, fast=False))
    
    @menu_command(_("Movement"), _("Step forward"), "w")
    def do_forward(self, evt):
        self._person.step_forward() 

    @menu_command(_("Movement"), _("Step backward"), "s")
    def do_backward(self, evt):
        self._person.step_backward() 
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the right"), "d")
    def turn_right(self, evt):
        self._person.rotate(5)
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the left"), "a")
    def turn_left(self, evt):
        self._person.rotate(-5)
    
    @menu_command(_("Information"), _("Current direction"), "r")
    def do_current_rotation(self, evt):
        speech().speak(_("{degrees} degrees").format(degrees=round(self._person.direction, config().presentation.angle_decimal_places)))
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the right"), "ctrl+d")
    def turn_right90(self, evt):
        self._person.rotate(90)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the left"), "ctrl+a")
    def turn_left90(self, evt):
        self._person.rotate(-90)
    
    @menu_command(_("Movement"), _("Coordinate jump..."), "j")
    def do_jump(self, evt):
        x, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the longitude"), decimals=6, minValue=-180, maxValue=180)
        if not ok:
            return
        y, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the latitude"), decimals=6, minValue=-90, maxValue=90)
        if not ok:
            return
        self._person.move_to(LatLon(y, x))

    @menu_command(_("Information"), _("Current road section angle"), "o")
    def current_road_section_angle(self, evt):
        seen_road = False
        for obj in self._person.is_inside_of:
            if obj.discriminator == "Road" and not obj.value_of_field("area"):
                seen_road = True
                angle = get_road_section_angle(self._person, obj)
                angle = round(angle, config().presentation.angle_decimal_places)
                speech().speak(_("{road}: {angle}°").format(road=describe_entity(obj), angle=angle))
        if not seen_road:
            speech().speak(_("You are not on a road."))

    @menu_command(_("Information"), _("Road details"), "ctrl+o")
    def road_details(self, evt):
        road = self._maybe_select_road()
        if not road or road.value_of_field("area"):
            return
        dlg = RoadSegmentsBrowserDialog(self._main_window, person=self._person, road=road)
        dlg.exec_()

    @menu_command(_("Movement"), _("Turn according to a road"), "shift+o")
    def rotate_to_road(self, evt):
        road = self._maybe_select_road()
        if not road:
            return
        rot = get_road_section_angle(self._person, road)
        self._person.set_direction(rot)

    @menu_command(_("Movement"), _("Turn about..."), "Ctrl+r")
    def rotate_by(self, evt):
        amount, ok = QInputDialog.getDouble(self._main_window, _("Data"), _("Enter the angle"), minValue=-360, maxValue=360)
        if not ok:
            return
        self._person.direction += float(amount)
    
    def _maybe_select_road(self):
        roads = [r for r in self._person.is_inside_of if r.discriminator == "Road"]
        if not roads:
            speech().speak(_("You are not on a road."))
            return None
        if len(roads) == 1:
            return roads[0]
        else:
            road_reprs = [describe_entity(r) for r in roads]
            road_repr, ok = QInputDialog.getItem(self._main_window, _("Request"), _("Select the road which should be the target of the operation"), road_reprs, editable=False)
            if not ok:
                return None
            return roads[road_reprs.index(road_repr)]
            
    @menu_command(_("Information"), _("Search..."), "ctrl+f")
    def do_search(self, evt):
        results = perform_search(self._main_window, self._person.position)
        if results:
            browser = ObjectsBrowserWindow(self._main_window, title=_("Search results"), unsorted_objects=results, person=self._person)
            browser.show()
            self._browser_window = browser
        elif isinstance(results, list) and len(results) == 0:
            QMessageBox.information(self._main_window, _("Information"), _("No object matches the given search criteria."))
    
    @menu_command(_("Bookmarks"), _("Add bookmark..."), "ctrl+b")
    def add_bookmark(self, evt):
        name, ok = QInputDialog.getText(self._main_window, _("Data entry"), _("Enter a name for the new bookmark"),)
        if not ok or not name:
            return
        self._person.map.add_bookmark(name, lon=self._person.position.lon, lat=self._person.position.lat)
    
    @menu_command(_("Bookmarks"), _("Go to bookmark..."), "b")
    def go_to_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        names = [b.name for b in bookmarks]
        name, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), names, editable=False)
        if not ok:
            return
        bookmark = bookmarks[names.index(name)]
        self._person.move_to(LatLon(bookmark.latitude, bookmark.longitude))

    @menu_command(_("Bookmarks"), _("Remove bookmark..."), "ctrl+shift+b")
    def remove_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        reprs = [_("{name}: longitude: {longitude}, latitude: {latitude}").format(name=b.name, longitude=b.longitude, latitude=b.latitude) for b in bookmarks]
        repr, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), reprs, editable=False)
        if not ok:
            return
        bookmark = bookmarks[reprs.index(repr)]
        if QMessageBox.question(self._main_window, _("Question"), _("Do you really want to delete the bookmark {name}?").format(name=bookmark.name)) == QMessageBox.Yes:
            map().remove_bookmark(bookmark)

    @menu_command(_("Options"), _("Disallow leaving roads"), "alt+o", checkable=True, name="toggle_disallow_leave_roads")
    def disallow_leaving_roads(self, checked):
        config().navigation.disallow_leaving_roads = bool(checked)
        config().save_to_user_config()