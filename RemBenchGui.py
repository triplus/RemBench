# Remember workbench for FreeCAD
# Copyright (C) 2020 triplus @ FreeCAD
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""Remember workbench for FreeCAD - Gui."""


from PySide import QtGui
from PySide import QtCore
import FreeCAD as App
import FreeCADGui as Gui


ids = {}
mw = Gui.getMainWindow()
mdi = mw.centralWidget()
p = App.ParamGet("User parameter:BaseApp/RemBench")


def onWorkbench():
    """Store subwindow and workbench info."""
    if p.GetBool("Checked", True):
        win = mdi.activeSubWindow()
        wb = Gui.activeWorkbench().__class__.__name__
        if win and wb:
            ids[id(win)] = wb


def onWindow():
    """Activate workbench on subwindow selection."""
    # Clean up
    lst = list(ids)
    for win in mdi.subWindowList():
        if id(win) in lst:
            lst.remove(id(win))
    for i in lst:
        del ids[i]
    # Activate
    if p.GetBool("Checked", True):
        win = id(mdi.activeSubWindow())
        wb = Gui.activeWorkbench().__class__.__name__
        if win in ids and ids[win] is not wb:
            Gui.activateWorkbench(ids[win])


def onEnabled(b):
    """Enable or disable remember workbench."""
    p.SetBool("Checked", b)
    if not b:
        ids.clear()


def accessoriesMenu():
    """Add remember workbench to accessories menu."""
    pref = QtGui.QAction(mw)
    pref.setText("Remember workbench")
    pref.setObjectName("RememberWorkbench")
    pref.setCheckable(True)
    pref.setChecked(p.GetBool("Checked", True))
    pref.toggled.connect(onEnabled)
    try:
        import AccessoriesMenu
        AccessoriesMenu.addItem("RememberWorkbench")
    except ImportError:
        a = mw.findChild(QtGui.QAction, "AccessoriesMenu")
        if a:
            a.menu().addAction(pref)
        else:
            mb = mw.menuBar()
            action = QtGui.QAction(mw)
            action.setObjectName("AccessoriesMenu")
            action.setIconText("Accessories")
            menu = QtGui.QMenu()
            action.setMenu(menu)
            menu.addAction(pref)

            def addMenu():
                """Add accessories menu to the menu bar."""
                mb.addAction(action)
                action.setVisible(True)

            addMenu()
            mw.workbenchActivated.connect(addMenu)


def onStart():
    """Start the remember workbench."""
    start = False
    try:
        mw.workbenchActivated
        mdi.subWindowActivated
        start = True
    except AttributeError:
        pass
    if start:
        t.stop()
        t.deleteLater()
        accessoriesMenu()
        mdi.subWindowActivated.connect(onWindow)
        mw.workbenchActivated.connect(onWorkbench)


t = QtCore.QTimer()
t.timeout.connect(onStart)
t.start(500)
