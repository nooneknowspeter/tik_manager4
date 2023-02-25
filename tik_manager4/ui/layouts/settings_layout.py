"""Settings Layout for auto-creating setting menus directly from Settings object.

Supported types:
    - boolean => QCheckBox
    - string => QLineEdit
    - spinnerInt => QSpinBox
    - spinnerFloat => QDoubleSpinBox
    - combo => QComboBox


"""

import os
import sys
from tik_manager4.core.settings import Settings
#
import re
from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.category_list import CategoryList
# from tik_manager4.ui.widgets import browser
import tik_manager4.ui.widgets.browser
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.Qt import QtWidgets, QtCore


class SettingsLayout(QtWidgets.QFormLayout):
    """Visualizes and edits Setting objects in a vertical layout"""
    widget_dict = {
        "boolean": value_widgets.Boolean,
        "string": value_widgets.String,
        "combo": value_widgets.Combo,
        "integer": value_widgets.Integer,
        "float": value_widgets.Float,
        "spinnerInt": value_widgets.SpinnerInt,
        "spinnerFloat": value_widgets.SpinnerFloat,
        "list": value_widgets.List,
        "categoryList": CategoryList,
        "validatedString": ValidatedString,
        "vector2Int": value_widgets.Vector2Int,
        "vector2Float": value_widgets.Vector2Float,
        "vector3Int": value_widgets.Vector3Int,
        "vector3Float": value_widgets.Vector3Float,
        "pathBrowser": tik_manager4.ui.widgets.browser.PathBrowser,
        "subprojectBrowser": tik_manager4.ui.widgets.browser.SubprojectBrowser
    }

    def __init__(self, ui_definition, settings_data=None, *args, **kwargs):
        # super(SettingsLayout, self).__init__(*args, **kwargs)
        super(SettingsLayout, self).__init__()
        self.ui_definition = ui_definition
        # TODO validate settings data type
        self.settings_data = settings_data or Settings()
        self.validate_settings_data()

        self.widgets = self.populate()
        self.signal_connections(self.widgets)

    def validate_settings_data(self):
        """Make sure all the keys are already present in settings data and all value keys are unique."""
        for key, data in self.ui_definition.items():
            if data["type"] == "multi":
                for sub_key, sub_data in data["value"].items():
                    self.settings_data.add_property(sub_key, sub_data["value"], force=False)
            else:
                self.settings_data.add_property(key, data["value"], force=False) # do not force the value to be set

    def populate(self):
        """Create the widgets."""
        _widgets = []  # flattened list of all widgets
        for name, properties in self.ui_definition.items():
            _display_name = properties.get("display_name", name)
            _label = QtWidgets.QLabel(text=_display_name)
            _tooltip = properties.get("tooltip", "")
            _label.setToolTip(_tooltip)
            _type = properties.get("type", None)
            if _type == "multi":
                multi_properties = properties.get("value", {})
                _layout = QtWidgets.QHBoxLayout()
                _layout.setContentsMargins(0, 0, 0, 0)
                # align the contents to the left
                _layout.setAlignment(QtCore.Qt.AlignLeft)
                for key, data in multi_properties.items():
                    _type = data.get("type", None)
                    _widget_class = self.widget_dict.get(_type)
                    if not _widget_class:
                        continue
                    _widget = _widget_class(key, **data)
                    _layout.addWidget(_widget)
                    _widget.com.valueChanged.connect(
                        # lambda x, n=name, k=key: self.ui_definition.edit_sub_property([n, "value", k, "value"], x))
                        # lambda x, n=name, k=key: self.settings_data.edit_property(k, x)
                        lambda x, k=key: self._test(k, x)
                    )
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            else:
                _widget_class = self.widget_dict.get(_type)
                if not _widget_class:
                    continue
                _widget = _widget_class(name, **properties)
                _widget.com.valueChanged.connect(
                    # lambda x, n=name: self.ui_definition.edit_sub_property([n, "value"], x)
                    # lambda x, n=name: self.settings_data.edit_property(n, x)
                    lambda x, n=name: self._test(n, x)
                )
                self.addRow(_label, _widget)
                _widgets.append(_widget)

        return _widgets

    def _test(self, key, value):
        # print("_test")
        # print(key, value)
        self.settings_data.edit_property(key, value)
        # print(self.settings_data.get_data())
        # print("============")

    def signal_connections(self, widget_list):
        """Creates the enable/disable logic between widgets. This needs to be done after population"""
        for widget in widget_list:
            # get the disable list
            for disable_data in widget.disables:
                # find the target widget / 2nd item in data list is the target
                # Example data: [false, "testString"]
                disable_widget = self.__find_widget(disable_data[1], widget_list)
                condition = disable_data[0]

                if not disable_widget:
                    continue
                widget.com.valueChanged.connect(
                    lambda state, wgt=disable_widget, cnd=condition: self.__toggle_enabled(state, cnd, wgt))
                # widget.com.valueChanged.connect(lambda state, disable_widget, condition: self.__toggle_enabled(state, condition, disable_widget))
                self.__toggle_enabled(widget.value, condition, disable_widget)

    @staticmethod
    def __toggle_enabled(value, condition, widget):
        """Disables the widget if value equals to condition. Else enables"""
        if value == condition:
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)

    @staticmethod
    def __find_widget(object_name, widget_list):
        """Find the widget by given object name inside the widget list"""
        for widget in widget_list:
            if widget.objectName() == object_name:
                return widget
        return None

    def find(self, object_name):
        """Find the widget by given object name inside the widget list"""
        return self.__find_widget(object_name, self.widgets)

    def clear(self):
        """Clear the layout"""
        self._clear_layout(self)
        self.settings_data.reset_settings()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())


def main():
    app = QtWidgets.QApplication(sys.argv)
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_testA.json")

    test_settings = Settings(test_file)
    # test_settings = Settings()
    # test_check = {
    #     "type": "boolean",
    #     "value": True,
    #     "disables": []
    # }
    # test_settings.add_property("testCheck", test_check)

    dialog = QtWidgets.QDialog()
    setting_lay = SettingsLayout(test_settings.get_data())
    # setting_lay.addRow(QtWidgets.QLabel("test"), QtWidgets.QLabel("ASDFASDF"))

    dialog.setLayout(setting_lay)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    # app = QtWidgets.QApplication(sys.argv)
    # test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_test.json")
    #
    # test_settings = Settings(test_file)
    #
    # dialog = QtWidgets.QDialog()
    # setting_lay = SettingsLayout(test_settings)
    # # setting_lay.addRow(QtWidgets.QLabel("test"), QtWidgets.QLabel("ASDFASDF"))
    #
    # dialog.setLayout(setting_lay)
    # dialog.show()
    # sys.exit(app.exec_())

