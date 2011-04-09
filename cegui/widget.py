################################################################################
#   CEED - A unified CEGUI editor
#   Copyright (C) 2011 Martin Preisler <preisler.m@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from PySide.QtCore import *
from PySide.QtGui import *

import PyCEGUI

# This module contains helping classes for CEGUI widget handling

class Manipulator(QGraphicsRectItem):
    """
    This is a rectangle that is synchronised with given CEGUI widget,
    it provides moving and resizing functionality
    """
    
    def __init__(self, widget, recursive = True, skipAutoWidgets = True):
        """
        widget - CEGUI::Widget to wrap
        recursive - if true, even children of given widget are wrapped
        skipAutoWidgets - if true, auto widgets are skipped (only applicable if recursive is True)
        """
        
        super(Manipulator, self).__init__()
        
        self.setFlags(QGraphicsItem.ItemIsFocusable | 
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setPen(QPen(Qt.GlobalColor.transparent))
        
        self.widget = widget
        self.updateFromWidgetData()
        
        if recursive:
            idx = 0
            while idx < self.widget.getChildCount():
                childWidget = self.widget.getChildAtIdx(idx)
                
                if skipAutoWidgets and childWidget.isAutoWindow():
                    # TODO: non auto widgets inside auto widgets?
                    idx += 1
                    continue
                
                child = Manipulator(childWidget, True, skipAutoWidgets)
                child.setParentItem(self)
                
                idx += 1
                
    def updateFromWidgetData(self):
        assert(self.widget is not None)
        
        unclippedOuterRect = self.widget.getUnclippedOuterRect()
        pos = unclippedOuterRect.getPosition()
        size = unclippedOuterRect.getSize()
        
        parentWidget = self.widget.getParent()
        if parentWidget:
            parentUnclippedOuterRect = parentWidget.getUnclippedOuterRect()
            pos -= parentUnclippedOuterRect.getPosition()
        
        self.setPos(QPoint(pos.d_x, pos.d_y))
        self.setRect(QRectF(0, 0, size.d_width, size.d_height))
        
        for item in self.childItems():
            if not isinstance(item, Manipulator):
                continue
            
            item.updateFromWidgetData()
    
    def moveToFront(self):
        parentItem = self.parentItem()
        if parentItem:
            for item in parentItem.childItems():
                if item == self:
                    continue
                
                # For some reason this is the opposite of what (IMO) it should be
                # which is self.stackBefore(item)
                #
                # Is Qt documentation flawed or something?!
                item.stackBefore(self)
                
            parentItem.moveToFront()
            
    def itemChange(self, change, value):    
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.widget.moveToFront()
                self.moveToFront()
                self.setActive(True)
                
            return value
        
        return super(Manipulator, self).itemChange(change, value)
        