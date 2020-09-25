from .services import menu_service, config
from .menu_service import menu_command

def make_config_option_switchable(item_label, config_section, config_attr_name, shortcut=None):
    def handle_trigger(checked):
        setattr(config_section, config_attr_name, bool(checked))
        config().save_to_user_config()
    item_name = f"toggle_{config_attr_name}"
    cmd = menu_command(_("Options", ), item_label, checkable=True, shortcut=shortcut, name=item_name)(handle_trigger)
    menu_service().register_menu_command(cmd)
    menu_service().menu_item_with_name(item_name).setChecked(getattr(config_section, config_attr_name))