from PySide6 import QtCore
from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QGroupBox, QFormLayout

from Src.DTOs.AdditionalKeysCollection import AdditionalKeysCollection
from Src.DTOs.ButtonToPress import ButtonToPress
from Src.GUI.Components.BaseWidget import BaseWidget
from Src.Helpers.ArrayHelper import Array


class AdditionalKeysArea(BaseWidget):
    changed = QtCore.Signal(AdditionalKeysCollection)

    def __init__(self, parent=None):
        super(AdditionalKeysArea, self).__init__(parent)
        self.additional_btns_layout = QVBoxLayout()
        self.additionalKeys = AdditionalKeysCollection()
        self.keygroups = []
        self.groupbox = QGroupBox("Additional keys")
        self.form = QFormLayout()
        self.groupbox.setLayout(self.form)
        scroll = QScrollArea()
        scroll.setWidget(self.groupbox)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(100)
        self.addAnotherKeyButton = self.AddAdditionalKeys()
        self.additional_btns_layout.addWidget(scroll)
        self.form.addRow(self.addAnotherKeyButton)

    def AddAdditionalKeys(self):
        btn = self.GetButton("+")
        btn.clicked.connect(self.addAnotherKey)
        return btn

    def addAnotherKey(self, keyText="", timeText=""):
        self.form.removeRow(self.addAnotherKeyButton)
        keygroup = KeyGroup(keyText, timeText)
        self.form.addRow(keygroup)
        self.addAnotherKeyButton = self.AddAdditionalKeys()
        self.form.addRow(self.addAnotherKeyButton)
        keygroup.added.connect(self.keygroup_changed)
        keygroup.removed.connect(self.keygroup_removed)
        self.keygroups.append(keygroup)

    def keygroup_removed(self, keygroup: ButtonToPress):
        keyToRemove = Array.find(self.keygroups, lambda x: x.buttonToPress.key == keygroup.key)
        self.additionalKeys.Remove(keygroup.key)
        self.keygroups.remove(keyToRemove)
        self.form.removeRow(keyToRemove)
        self.changed.emit(self.additionalKeys)

    def keygroup_changed(self, keygroup: ButtonToPress):
        if self.findInArray(keygroup.key):
            self.additionalKeys.Remove(keygroup.key)
        self.additionalKeys.Add(keygroup)
        self.changed.emit(self.additionalKeys)

    def findInArray(self, key):
        for el in self.additionalKeys.Get():
            if el.key == key:
                return True
        return False

    def LoadState(self, state: AdditionalKeysCollection):
        if state is None or type(state) is not AdditionalKeysCollection:
            return
        for el in state.Get():
            self.additionalKeys.Add(el)
            self.addAnotherKey(el.key, el.time)

    def GetLayout(self):
        return self.additional_btns_layout


class KeyGroup(BaseWidget):
    added = QtCore.Signal(ButtonToPress)
    removed = QtCore.Signal(ButtonToPress)
    buttonToPress = None

    def __init__(self, keyEntryText="", timeEntryText="", parent=None):
        super(KeyGroup, self).__init__(parent)
        addKeyLabel = self.GetLabel("Key")
        self.addKeyEntry = self.GetEntry()
        self.addKeyEntry.setText(keyEntryText)
        addKeyTimeLabel = self.GetLabel("Every (s)")
        self.addKeyTimeEntry = self.GetNumberOnlyEntry()
        self.addKeyTimeEntry.setText(str(timeEntryText))
        removeKeyButton = self.GetButton("-")
        addKeyButton = self.GetButton("Add")
        removeKeyButton.clicked.connect(self.RemoveButtonCick)
        addKeyButton.clicked.connect(self.NewAdditionalButtonAdded)
        self.buttonToPress = ButtonToPress(self.addKeyEntry.text(), self.addKeyTimeEntry.text())
        self.layout = self.GroupHorizontally([removeKeyButton, addKeyLabel, self.addKeyEntry, addKeyTimeLabel, self.addKeyTimeEntry, addKeyButton])

    def RemoveButtonCick(self):
        self.removed.emit(self.buttonToPress)

    def NewAdditionalButtonAdded(self):
        self.buttonToPress = ButtonToPress(self.addKeyEntry.text(), self.addKeyTimeEntry.text())
        self.added.emit(self.buttonToPress)
