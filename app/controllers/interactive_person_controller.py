from PySide6.QtWidgets import QInputDialog, QMessageBox, QApplication
from pygeodesy.ellipsoidalVincenty import LatLon
from ..entities import entity_post_enter
from ..humanization_utils import describe_entity, format_number, format_relationship
from ..services import speech, map, config, menu_service
from ..objects_browser import ObjectsBrowserWindow, ObjectsSorter, tracked_object_changed
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..bookmarks import BookmarksDialog
from ..geometry_utils import get_road_section_angle, get_meaningful_turns, get_smaller_turn
from ..search import get_query_from_user, QueryExecutor, create_query_for_name_search, create_query_for_address_search
from ..search_indicator import SearchIndicator
from ..config_utils import make_config_option_switchable
from ..entity_utils import get_last_important_road, filter_important_roads
from ..menu_service import menu_command
from .interesting_entities_controller import interesting_entity_in_range, request_interesting_entities
from .sound_controller import leave_disallowed_sound_played

def describe_turn(turn, use_detailed_description):
    if use_detailed_description:
        return _("{turn_description} to {target_description}").format(turn_description=turn[0], target_description=describe_entity(turn[3]))
    else:
        return turn[0]

class InteractivePersonController: 
    def __init__(self, person, main_window):
        self._person = person
        self._main_window = main_window
        self._browser_window = None
        self._search_progress = None
        self._search_executor = None
        self._tracked_object = None
        menu_service().register_menu_commands(self)
        cfg = config()
        make_config_option_switchable(_("Disallow leaving roads"), cfg.navigation, "disallow_leaving_roads", "alt+o")
        make_config_option_switchable(_("Try avoid sidewalks"), cfg.navigation, "try_avoid_sidewalks")
        make_config_option_switchable(_("Automatically correct your direction when attempting to exit the last road"), cfg.navigation, "correct_direction_after_leave_disallowed")
        make_config_option_switchable(_("Play sounds for interesting objects"), cfg.presentation, "play_sounds_for_interesting_objects")
        make_config_option_switchable(_("Play crossing sounds"), cfg.presentation, "play_crossing_sounds")
        make_config_option_switchable(_("Announce interesting objects"), cfg.presentation, "announce_interesting_objects")
        make_config_option_switchable(_("Use detailed turn instructions"), cfg.presentation, "use_detailed_turn_directions")
        make_config_option_switchable(_("Announce the current object after leaving other"), cfg.presentation, "announce_current_object_after_leaving_other")
        make_config_option_switchable(_("Represent bearings as clock positions"), cfg.presentation, "represent_bearings_as_clock_position")
        leave_disallowed_sound_played.connect(self._leave_disalloved_sound_played)
        tracked_object_changed.connect(self._tracked_object_changed)

    def _get_current_coordinates_string(self):
        lat = format_number(self._person.position.lat, config().presentation.coordinate_decimal_places)
        lon = format_number(self._person.position.lon, config().presentation.coordinate_decimal_places)
        return _("Longitude: {longitude}, latitude: {latitude}.").format(longitude=lon, latitude=lat)

    @menu_command(_("Information"), _("Current coordinates"), "c")
    def do_current_coords(self):
        speech().speak(self._get_current_coordinates_string(), interrupt=True)

    def _position_impl(self, objects):    
        if objects:
            speech().silence()
            for obj in objects:
                speech().speak(describe_entity(obj), add_to_history=False)
        else:
            speech().speak(_("Not known."), add_to_history=False)
    
    @menu_command(_("Information"), _("Position"), "l")
    def do_position(self):
        self._position_impl(self._person.is_inside_of)
    
    @menu_command(_("Information"), _("Position - all objects, may be slow"), "ctrl+l")
    def do_position_slow(self):
        self._position_impl(map().intersections_at_position(self._person.position, self._person.current_effective_width, fast=False))
    
    def _position_detailed_impl(self, objects):
        window = ObjectsBrowserWindow(title=_("Current position"), unsorted_objects=objects, person=self._person)
        self._browser_window = window
    
    @menu_command(_("Information"), _("Detailed current position"), "shift+l")
    def position_detailed(self):
        self._position_detailed_impl(self._person.is_inside_of)

    @menu_command(_("Information"), _("Detailed current position - all objects, may be slow"), "ctrl+shift+l")
    def do_position_detailed_slow(self):
        self._position_detailed_impl(map().intersections_at_position(self._person.position, self._person.current_effective_width, fast=False))
    
    def _show_list_of_objects(self, title, objects):
        if not objects:
            speech().speak(_("Nothing."), interrupt=True, add_to_history=False)
            return
        self._browser_window = ObjectsBrowserWindow(title=title, person=self._person, unsorted_objects=objects)

    @menu_command(_("Information"), _("Nearest"), "n")
    def do_nearest(self):
        self._show_list_of_objects(_("Nearby objects"), self._person.map.within_distance(self._person.position, config().presentation.near_by_radius))

    @menu_command(_("Information"), _("Nearest - all objects, may be slow"), "ctrl+n")
    def do_nearest_slow(self):
        self._show_list_of_objects(_("Nearby objects"), self._person.map.within_distance(self._person.position, config().presentation.near_by_radius, fast=False))
    
    @menu_command(_("Information"), _("Interesting objects"), "i")
    def _do_interesting(self):
        self._show_list_of_objects(_("Interesting objects"), request_interesting_entities.send(self)[0][1])

    @menu_command(_("Movement"), _("Step forward"), "up")
    def do_forward(self):
        self._person.step_forward() 

    @menu_command(_("Movement"), _("Step backward"), "down")
    def do_backward(self):
        self._person.step_backward() 
    
    @menu_command(_("Movement"), _("Step left"), "alt+left")
    def do_left(self):
        self._person.step_left() 
    
    @menu_command(_("Movement"), _("Step right"), "alt+right")
    def do_right(self):
        self._person.step_right() 

    @menu_command(_("Movement"), _("Turn 5 degrees to the right"), "right")
    def turn_right(self):
        self._person.rotate(5)
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the left"), "left")
    def turn_left(self):
        self._person.rotate(-5)
    
    @menu_command(_("Information"), _("Current direction"), "r")
    def do_current_rotation(self):
        speech().speak(_("{degrees} degrees").format(degrees=format_number(self._person.direction, config().presentation.angle_decimal_places)), interrupt=True, add_to_history=False)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the right"), "ctrl+right")
    def turn_right90(self):
        self._person.rotate(90)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the left"), "ctrl+left")
    def turn_left90(self):
        self._person.rotate(-90)
    
    @menu_command(_("Movement"), _("Turn 180 degrees"), "alt+down")
    def turn_180(self):
        self._person.rotate(180)
    
    @menu_command(_("Movement"), _("Coordinate jump..."), "j")
    def do_jump(self):
        x, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the longitude"), decimals=config().presentation.coordinate_decimal_places, minValue=-180, maxValue=180, value=self._person.position.lon)
        if not ok:
            return
        y, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the latitude"), decimals=config().presentation.coordinate_decimal_places, minValue=-90, maxValue=90, value=self._person.position.lat)
        if not ok:
            return
        self._person.move_to(LatLon(y, x), force=True)

    @menu_command(_("Information"), _("Current road section angle"), "o")
    def current_road_section_angle(self):
        seen_road = False
        for obj in self._person.is_inside_of:
            if obj.is_road_like and not obj.value_of_field("area"):
                seen_road = True
                angle = get_road_section_angle(self._person, obj)
                diff = (angle - self._person.direction)%360
                if 90 < diff < 270:
                    angle = (angle + 180) % 360
                angle = format_number(angle, config().presentation.angle_decimal_places)
                speech().speak(_("{road}: {angle}°").format(road=describe_entity(obj), angle=angle), interrupt=True, add_to_history=False)
        if not seen_road:
            speech().speak(_("You are not on a road."), interrupt=True, add_to_history=False)

    @menu_command(_("Information"), _("Road details"), "ctrl+o")
    def road_details(self):
        road = self._maybe_select_road()
        if not road or road.value_of_field("area"):
            return
        dlg = RoadSegmentsBrowserDialog(self._main_window, person=self._person, road=road)
        dlg.exec_()

    @menu_command(_("Movement"), _("Turn according to a road"), "shift+o")
    def rotate_to_road(self):
        road = self._maybe_select_road()
        if not road:
            return
        turns = get_meaningful_turns(road, self._person)
        self._maybe_perform_turn(turns, False, _("There is no meaningful turn, the road is too short."))

    @menu_command(_("Movement"), _("Set direction..."), "Ctrl+r")
    def set_direction(self):
        amount, ok = QInputDialog.getDouble(self._main_window, _("Data"), _("Enter the angle"), minValue=0, maxValue=359)
        if not ok:
            return
        self._person.set_direction(float(amount))
    
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
            
    @menu_command(_("Information"), _("Search by name..."), "ctrl+f")
    def do_search_by_name(self):
        name, ok = QInputDialog.getText(self._main_window, _("Enter name"), _("Enter the name or its part"))
        if not ok:
            return
        query = create_query_for_name_search(name)
        self._handle_search(query, float("inf"))

    @menu_command(_("Information"), _("Search by address..."), "alt+f")
    def do_search_by_address(self):
        address, ok = QInputDialog.getText(self._main_window, _("Enter address"), _("Enter the address"))
        if not ok:
            return
        query = create_query_for_address_search(address)
        self._handle_search(query, float("inf"))

    @menu_command(_("Information"), _("Advanced search..."), "ctrl+shift+f")
    def do_search(self):
        ret = get_query_from_user(self._main_window, self._person.position)
        if not ret:
            return
        query, distance = ret
        self._handle_search(query, distance)
        
   
    def _handle_search(self, query, distance):
        self._search_executor = QueryExecutor(query, self._person.position, distance)
        self._search_executor.results_ready.connect(self._search_results_ready)
        self._search_executor.start()
        self._search_progress = SearchIndicator()
        self._search_progress.show()
    
    def _search_results_ready(self, results):
        if results:
            browser = ObjectsBrowserWindow(title=_("Search results"), unsorted_objects=results, person=self._person, progress_indicator=self._search_progress)
            self._browser_window = browser
        else:
            self._search_progress.hide()
            QMessageBox.information(self._main_window, _("Information"), _("No object matches the given search criteria."))
    
    @menu_command(_("Bookmarks"), _("Add bookmark..."), "ctrl+b")
    def add_bookmark(self):
        while True:
            name, ok = QInputDialog.getText(self._main_window, _("Data entry"), _("Enter a name for the new bookmark"),)
            if not ok or not name:
                return
            if name.startswith("."):
                QMessageBox.warning(self._main_window, _("Error"), _("The bookmark name can not start with a dot, please enter a different name."))
            else:
                break
        self._person.map.add_bookmark(name, lon=self._person.position.lon, lat=self._person.position.lat, direction=self._person.direction)
    
    @menu_command(_("Bookmarks"), _("Manage bookmarks"), "b")
    def manage_bookmarks(self):
        bookmarks = self._person.map.bookmarks
        dialog = BookmarksDialog(self._main_window, bookmarks, self._person)
        if dialog.exec_() == dialog.DialogCode.Rejected:
            return
        bookmark = dialog.selected_bookmark
        self._person.move_to(LatLon(bookmark.latitude, bookmark.longitude), force=True)
        self._person.set_direction(bookmark.direction)

    @menu_command(_("Bookmarks"), _("Remove bookmark..."), "ctrl+shift+b")
    def remove_bookmark(self):
        bookmarks = list(self._person.map.bookmarks)
        reprs = [_("{name}: longitude: {longitude}, latitude: {latitude}").format(name=b.name, longitude=b.longitude, latitude=b.latitude) for b in bookmarks]
        repr, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), reprs, editable=False)
        if not ok:
            return
        bookmark = bookmarks[reprs.index(repr)]
        if QMessageBox.question(self._main_window, _("Question"), _("Do you really want to delete the bookmark {name}?").format(name=bookmark.name)) == QMessageBox.Yes:
            map().remove_bookmark(bookmark)


    def _go_looking_for_interesting(self, movement_fn):
        self._search_for_interesting = True
        found_interesting = False
        step_length = config().navigation.step_length
        stop_after = config().navigation.stop_interesting_object_search_after
        distance = 0
        def on_interesting(_sender, entity):
            nonlocal found_interesting
            if not entity.is_road_like:
                found_interesting = True
        def _on_post_enter(_sender, enters):
            nonlocal found_interesting
            found_interesting = True
        interesting_entity_in_range.connect(on_interesting)
        entity_post_enter.connect(_on_post_enter)
        while self._search_for_interesting and (not found_interesting) and (distance < stop_after):
            movement_fn()
            distance += step_length
            QApplication.processEvents()
        if found_interesting:
            speech().speak(_("Interesting object found after {} meters.").format(format_number(distance, config().presentation.distance_decimal_places)))
        else:
            speech().speak(_("No interesting object found after {} meters.").format(format_number(distance, config().presentation.distance_decimal_places)))

    @menu_command(_("Movement"), _("Go forward looking for an interesting object"), "ctrl+up")
    def do_forward_until_no_interesting(self):
        self._go_looking_for_interesting(self._person.step_forward)

    @menu_command(_("Movement"), _("Go backward looking for an interesting object"), "ctrl+down")
    def do_backward_until_no_interesting(self):
        self._go_looking_for_interesting(self._person.step_backward)

    @menu_command(_("Movement"), _("Stop looking for an interesting object"), "ctrl+s")
    def stop_search_for_interesting(self):
        self._search_for_interesting = False

    @menu_command(_("Movement"), _("Turn to a new road"), "t")
    def _turn_to_a_new_road(self):
        roads = self._person.inside_of_roads
        if not roads:
            speech().speak(_("There is no meaningful turn to perform, you are not on a road."), interrupt=True, add_to_history=False)
            return
        roads = filter_important_roads(self._person.inside_of_roads)
        describe_roads_in_turns = False
        if len(roads) > 2: # A current road and two new - likely a crossing of more roads
            describe_roads_in_turns = True
        turns = []
        stayed_on_roads = [e for e in self._person.was_inside_of if e in roads]
        if stayed_on_roads:
            # Assume that the first road is the one which the user is on, e. g. does not want to be taken into account when getting new turn possibilities
            roads.remove(stayed_on_roads[0])
        for road in roads:
            current_turns = get_meaningful_turns(road, self._person)
            turns.extend(current_turns)
        self._maybe_perform_turn(turns, describe_roads_in_turns, _("There is no meaningful turn to perform, you aren't on a new road."))

    def _maybe_perform_turn(self, turns, describe_roads_in_turns, no_turns_message):
        if not turns:
            speech().speak(no_turns_message, interrupt=True, add_to_history=False)
        elif len(turns) == 1:
            self._person.rotate(turns[0][2])
            self._person.move_to_center_of(turns[0][3])
            speech().speak(_("There is only a single meaningful turn, so you've been rotated {}").format(turns[0][0]), interrupt=True, add_to_history=False)
        else:
            turn = self._select_turn(turns, describe_roads_in_turns)
            if not turn:
                return
            self._person.rotate(turn[2])
            self._person.move_to_center_of(turn[3])
            speech().speak(_("You've been rotated {}.").format(turn[0]), interrupt=True, add_to_history=False)


    def _select_turn(self, turns, describe_roads_in_turns):
        mapping = {describe_turn(turn, describe_roads_in_turns): turn for turn in turns}
        angle_choices = list(mapping.keys())
        angle_desc, ok = QInputDialog.getItem(self._main_window, _("Request"), _("Which turn you want to perform?"), angle_choices, editable=False)
        if not ok: return
        return mapping[angle_desc]
            
    @menu_command(_("Information"), _("Nearest address"), "a")
    def _nearest_address(self):
        unsorted = [o for o in map().within_distance(self._person.position, config().presentation.near_by_radius, fast=True) if o.value_of_field("address")]
        sorter = ObjectsSorter(unsorted, self._person)
        rels = sorter.perform_sorting()
        self._report_single_relationship(next(iter(rels), None))
    
    @menu_command(_("Information"), _("Nearest named road"), "d")
    def _nearest_named_road(self):
        unsorted = [entity for entity in map().within_distance(self._person.position, config().presentation.near_by_radius, fast=True) if entity.is_road_like and entity.value_of_field("name")]
        sorter = ObjectsSorter(unsorted, self._person)
        rels = sorter.perform_sorting()
        self._report_single_relationship(next(iter(rels), None))
    
    def _report_single_relationship(self, relationship):
        if not relationship:
            speech().speak(_("Not found."), add_to_history=False)
        else:
            speech().speak(format_relationship(relationship), add_to_history=False)

    @menu_command(_("Information"), _("Tracked object information"), "k")
    def tracked_object_info(self):
        if self._tracked_object:
            rel = self._person.spatial_relationship_to(self._tracked_object)
            speech().speak(format_relationship(rel), interrupt=True)
        else:
            speech().speak(_("No tracked object."), interrupt=True, add_to_history=False)

    @menu_command(_("Program"), _("Stop tracking the currently tracked object"), index=0)
    def stop_tracking(self):
        self._tracked_object = None
        speech().speak(_("Stopped tracking the current object."), interrupt=True, add_to_history=False)

    def _leave_disalloved_sound_played(self, _sender, because_of):
        if not config().navigation.correct_direction_after_leave_disallowed: return
        last_road = get_last_important_road(because_of.inside_of_roads)
        turn_choices = get_meaningful_turns(last_road, because_of)
        if not turn_choices:
            return
        smaller = get_smaller_turn(turn_choices)
        if smaller[2] < 3:
            turn_message = _("your direction was corrected")
        else:
            turn_message = _("you will be turned {}").format(smaller[0])
        if config().navigation.automatic_direction_corrections < 6:
            speech().speak(_("Because of your settings, {0}").format(turn_message), interrupt=True)
            config().navigation.automatic_direction_corrections += 1
            config().save_to_user_config()
        else:
            speech().speak(turn_message.capitalize(), interrupt=True)
        because_of.rotate(smaller[2])
        # Move the colliding entity to wards the road so it can continue in its walk.
        because_of.move_to_center_of(last_road)
        
    def reset(self, person):
        self._person = person
        self._tracked_object = None

    def _tracked_object_changed(self, sender, entity):
        self._tracked_object = entity
