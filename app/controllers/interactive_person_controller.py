from PySide2.QtWidgets import QInputDialog, QMessageBox, QApplication
from pygeodesy.ellipsoidalVincenty import LatLon
from ..humanization_utils import describe_entity, format_number, describe_angle_as_turn_instructions
from ..services import speech, map, config, menu_service
from ..objects_browser import ObjectsBrowserWindow
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..geometry_utils import get_road_section_angle, distance_filter, distance_between, get_meaningful_turns, bearing_to
from ..search import get_query_from_user, QueryExecutor, SearchIndicator
from ..config_utils import make_config_option_switchable
from ..menu_service import menu_command
from .interesting_entities_controller import interesting_entity_in_range
from .sound_controller import leave_disallowed_sound_played

class InteractivePersonController: 
    def __init__(self, person, main_window):
        self._person = person
        self._main_window = main_window
        self._browser_window = None
        self._search_progress = None
        self._search_executor = None
        menu_service().register_menu_commands(self)
        cfg = config()
        make_config_option_switchable(_("Disallow leaving roads"), cfg.navigation, "disallow_leaving_roads", "alt+o")
        make_config_option_switchable(_("Automatically correct your direction when attempting to exit the last road"), cfg.navigation, "correct_direction_after_leave_disallowed")
        make_config_option_switchable(_("Play sounds for interesting objects"), cfg.presentation, "play_sounds_for_interesting_objects")
        make_config_option_switchable(_("Play crossing sounds"), cfg.presentation, "play_crossing_sounds")
        make_config_option_switchable(_("Announce interesting objects"), cfg.presentation, "announce_interesting_objects")
        make_config_option_switchable(_("Use detailed turn instructions"), cfg.presentation, "use_detailed_turn_directions")
        make_config_option_switchable(_("Announce the current object after leaving other"), cfg.presentation, "announce_current_object_after_leaving_other")
        leave_disallowed_sound_played.connect(self._leave_disalloved_sound_played)

    def _get_current_coordinates_string(self):
        lat = format_number(self._person.position.lat, config().presentation.coordinate_decimal_places)
        lon = format_number(self._person.position.lon, config().presentation.coordinate_decimal_places)
        return _("Longitude: {longitude}, latitude: {latitude}.").format(longitude=lon, latitude=lat)

    @menu_command(_("Information"), _("Current coordinates"), "c")
    def do_current_coords(self, evt):
        speech().speak(self._get_current_coordinates_string(), interrupt=True)

    def _position_impl(self, objects):    
        if objects:
            speech().silence()
            for obj in objects:
                speech().speak(describe_entity(obj), add_to_history=False)
        else:
            speech().speak(_("Not known."), add_to_history=False)
    
    @menu_command(_("Information"), _("Position"), "l")
    def do_position(self, evt):
        self._position_impl(self._person.is_inside_of)
    
    @menu_command(_("Information"), _("Position - all objects, may be slow"), "ctrl+l")
    def do_position_slow(self, evt):
        self._position_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _position_detailed_impl(self, objects):
        window = ObjectsBrowserWindow(self._main_window, title=_("Current position"), unsorted_objects=self._person.is_inside_of, person=self._person)
        self._browser_window = window
    
    @menu_command(_("Information"), _("Detailed current position"), "shift+l")
    def position_detailed(self, evt):
        self._position_detailed_impl(self._person.is_inside_of)

    @menu_command(_("Information"), _("Detailed current position - all objects, may be slow"), "ctrl+shift+l")
    def do_position_detailed_slow(self, evt):
        self._position_detailed_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _nearest_impl(self, objects):
        if not objects:
            speech().speak(_("Nothing."), interrupt=True, add_to_history=False)
            return
        self._browser_window = ObjectsBrowserWindow(self._main_window, title=_("Near by objects"), person=self._person, unsorted_objects=objects)

    @menu_command(_("Information"), _("Nearest"), "n")
    def do_nearest(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, config().presentation.near_by_radius))

    @menu_command(_("Information"), _("Nearest - all objects, may be slow"), "ctrl+n")
    def do_nearest_slow(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, config().presentation.near_by_radius, fast=False))
    
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
        speech().speak(_("{degrees} degrees").format(degrees=format_number(self._person.direction, config().presentation.angle_decimal_places)), interrupt=True, add_to_history=False)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the right"), "ctrl+right")
    def turn_right90(self, evt):
        self._person.rotate(90)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the left"), "ctrl+left")
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
        self._person.move_to(LatLon(y, x), force=True)

    @menu_command(_("Information"), _("Current road section angle"), "o")
    def current_road_section_angle(self, evt):
        seen_road = False
        for obj in self._person.is_inside_of:
            if obj.is_road_like and not obj.value_of_field("area"):
                seen_road = True
                angle = get_road_section_angle(self._person, obj)
                angle = format_number(angle, config().presentation.angle_decimal_places)
                speech().speak(_("{road}: {angle}°").format(road=describe_entity(obj), angle=angle), interrupt=True, add_to_history=False)
        if not seen_road:
            speech().speak(_("You are not on a road."), interrupt=True, add_to_history=False)

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
        self._person.rotate(float(amount))
    
    def _maybe_select_road(self):
        roads = self._person.inside_of_roads
        if not roads:
            speech().speak(_("You are not on a road."), interrupt=True, add_to_history=False)
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
        ret = get_query_from_user(self._main_window, self._person.position)
        if not ret:
            return
        query, distance = ret
        self._search_executor = QueryExecutor(query, self._person.position, distance)
        self._search_executor.results_ready.connect(self._search_results_ready)
        self._search_executor.start()
        self._search_progress = SearchIndicator(self._main_window)
        self._search_progress.show()
    
    def _search_results_ready(self, results):
        if results:
            browser = ObjectsBrowserWindow(self._main_window, title=_("Search results"), unsorted_objects=results, person=self._person, progress_indicator=self._search_progress)
            self._browser_window = browser
        else:
            self._search_progress.hide()
            QMessageBox.information(self._main_window, _("Information"), _("No object matches the given search criteria."))
    
    @menu_command(_("Bookmarks"), _("Add bookmark..."), "ctrl+b")
    def add_bookmark(self, evt):
        name, ok = QInputDialog.getText(self._main_window, _("Data entry"), _("Enter a name for the new bookmark"),)
        if not ok or not name:
            return
        self._person.map.add_bookmark(name, lon=self._person.position.lon, lat=self._person.position.lat)
    
    @menu_command(_("Bookmarks"), _("Go to bookmark..."), "b")
    def go_to_bookmark(self, evt):
        bookmarks = self._person.map.bookmarks
        reprs = []
        for mark in bookmarks:
            point = LatLon(mark.latitude, mark.longitude)
            dist = format_number(distance_between(self._person.position, point), config().presentation.distance_decimal_places)
            bearing = format_number((bearing_to(self._person.position, point) - self._person.direction) % 360, config().presentation.angle_decimal_places)
            reprs.append(_("{name}: distance {distance} meters, {bearing}° relatively").format(name=mark.name, distance=dist, bearing=bearing))
        name, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), reprs, editable=False)
        if not ok:
            return
        bookmark = bookmarks[reprs.index(name)]
        self._person.move_to(LatLon(bookmark.latitude, bookmark.longitude), force=True)

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


    def _go_looking_for_interesting(self, movement_fn):
        found_interesting = False
        initial_position = self._person.position
        def on_interesting(sender, entity):
            nonlocal found_interesting
            if not entity.is_road_like:
                found_interesting = True
        interesting_entity_in_range.connect(on_interesting)
        while not found_interesting:
            movement_fn()
        distance = distance_between(initial_position, self._person.position)
        speech().speak(_("Interesting object found after {} meters.").format(format_number(distance, config().presentation.distance_decimal_places)))

    @menu_command(_("Movement"), _("Go forward looking for an interesting object"), "ctrl+up")
    def do_forward_until_no_interesting(self, evt):
        self._go_looking_for_interesting(self._person.step_forward)

    @menu_command(_("Movement"), _("Go backward looking for an interesting object"), "ctrl+down")
    def do_backward_until_no_interesting(self, evt):
        self._go_looking_for_interesting(self._person.step_backward)

    @menu_command(_("Movement"), _("Turn to a new road"), "t")
    def _turn_to_a_new_road(self, evt):
        roads = self._person.inside_of_roads
        if not roads:
            speech().speak(_("There is no meaningful turn to perform, you are not on a road."), interrupt=True, add_to_history=False)
            return
        # Assume that the last road is the one the user wants to turn to.
        new_road = roads[-1]
        turns = get_meaningful_turns(new_road, self._person)
        if not turns:
            speech().speak(_("There is no meaningful turn to perform, the new road is too short."), interrupt=True, add_to_history=False)
        elif len(turns) == 1:
            self._person.rotate(turns[0][2])
            self._person.move_to_center_of(new_road)
            speech().speak(_("There is only a single meaningful turn, so you've been rotated {}").format(turns[0][0]), interrupt=True, add_to_history=False)
        else:
            angles_mapping = {turn[0]: turn[2] for turn in turns}
            angle_choices = list(angles_mapping.keys())
            angle_desc, ok = QInputDialog.getItem(self._main_window, _("Request"), _("Which turn you want to perform?"), angle_choices, editable=False)
            if not ok: return
            self._person.rotate(angles_mapping[angle_desc])
            self._person.move_to_center_of(new_road)
            speech().speak(_("You've been rotated {}.").format(angle_desc), interrupt=True, add_to_history=False)


    def _leave_disalloved_sound_played(self, sender, because_of):
        if not config().navigation.correct_direction_after_leave_disallowed: return
        last_road = because_of.inside_of_roads[0]
        turn_choices = get_meaningful_turns(last_road, because_of)
        if not turn_choices:
            return
        smaller = min(turn_choices, key=lambda i: abs(i[2]))
        if config().navigation.automatic_direction_corrections < 6:
            speech().speak(_("Because of you settings, you will be turned {}").format(smaller[0]), interrupt=True)
            config().navigation.automatic_direction_corrections += 1
            config().save_to_user_config()
        else:
            speech().speak(_("You will be turned {}").format(smaller[0]), interrupt=True)
        because_of.rotate(smaller[2])
        # Move the colliding entity to wards the road so it can continue in its walk.
        because_of.move_to_center_of(last_road)
        
