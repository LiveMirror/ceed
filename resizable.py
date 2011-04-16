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

class GraphicsView(QGraphicsView):
    scaleChanged = Signal(float, float)
    
    def __init__(self):
        super(GraphicsView, self).__init__()
        
    def scale(self, sx, sy):
        super(GraphicsView, self).scale(sx, sy)
        
        self.scaleChanged(sx, sy)
        
    def setTransform(self, transform):
        super(GraphicsView, self).setTransform(transform)
        
        sx = transform.m11()
        sy = transform.m22()
        
        self.scaleChanged(sx, sy)
        
    def scaleChanged(self, sx, sy):
        for item in self.scene().items():
            if isinstance(item, ResizableGraphicsRectItem):
                item.scaleChanged(sx, sy)

class ResizingHandle(QGraphicsRectItem):
    def __init__(self, parent):
        super(ResizingHandle, self).__init__()
        
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setParentItem(parent)
        self.setAcceptHoverEvents(True)
        
        self.ignoreGeometryChanges = False
        self.ignoreTransformChanges = False
        self.mouseOver = False
        self.currentView = None

    def adjustParentRect(self, delta_x1, delta_y1, delta_x2, delta_y2):
        parent = self.parentItem()
        newRect = parent.rect().adjusted(delta_x1, delta_y1, delta_x2, delta_y2)
        newRect = parent.constrainResizeRect(newRect)
        
        #print "old rect: ", parent.rect()
        #print "old rect adjusted: ", parent.rect().adjusted(delta_x1, delta_y1, delta_x2, delta_y2)
        #print "min rect: ", minRect
        #print "new rect: ", newRect
        
        # TODO: the rect moves as a whole when it can't be sized any less
        #       this is probably not the behaviour we want!
        
        topLeftDelta = newRect.topLeft() - parent.rect().topLeft()
        bottomRightDelta = newRect.bottomRight() - parent.rect().bottomRight()
        
        parent.setRect(newRect)
        
        return topLeftDelta.x(), topLeftDelta.y(), bottomRightDelta.x(), bottomRightDelta.y()

    def unselectAllSiblingHandles(self):
        assert(self.parentItem())
        
        for item in self.parentItem().childItems():
            if isinstance(item, ResizingHandle) and not self is item:
                item.setSelected(False)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if self.parentItem().isSelected():
                return False
            
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            self.unselectAllSiblingHandles()
        
        elif change == QGraphicsItem.ItemPositionChange:
            if not self.parentItem().resizeInProgress and not self.ignoreGeometryChanges:
                self.parentItem().resizeInProgress = True
                self.parentItem().resizeOldPos = self.parentItem().pos()
                self.parentItem().resizeOldRect = self.parentItem().rect()

                self.parentItem().setPen(self.parentItem().getPenWhileResizing())               
                self.parentItem().hideAllHandles(excluding = self)
                
                self.parentItem().notifyResizeStarted()
                
            if self.parentItem().resizeInProgress:
                newPos = self.parentItem().pos() + self.parentItem().rect().topLeft()
                newRect = QRectF(0, 0, self.parentItem().rect().width(), self.parentItem().rect().height())

                self.parentItem().notifyResizeProgress(newPos, newRect)

        return super(ResizingHandle, self).itemChange(change, value)
    
    def mouseReleaseEvent(self, event):
        super(ResizingHandle, self).mouseReleaseEvent(event)
        
        if self.parentItem().resizeInProgress:
            # resize was in progress and just ended
            self.parentItem().resizeInProgress = False
            self.parentItem().setPen(self.parentItem().getHoverPen() if self.parentItem().mouseOver else self.parentItem().getNormalPen())
            
            newPos = self.parentItem().pos() + self.parentItem().rect().topLeft()
            newRect = QRectF(0, 0, self.parentItem().rect().width(), self.parentItem().rect().height())
            
            self.parentItem().notifyResizeFinished(newPos, newRect)

    def hoverEnterEvent(self, event):
        super(ResizingHandle, self).hoverEnterEvent(event)
        
        self.mouseOver = True
        
    def hoverLeaveEvent(self, event):
        self.mouseOver = False
        
        super(ResizingHandle, self).hoverLeaveEvent(event)

    def scaleChanged(self, sx, sy):
        pass

class EdgeResizingHandle(ResizingHandle):
    def __init__(self, parent):
        super(EdgeResizingHandle, self).__init__(parent)
        
        self.setPen(self.parentItem().getEdgeResizingHandleHiddenPen())

    def hoverEnterEvent(self, event):
        super(EdgeResizingHandle, self).hoverEnterEvent(event)
        
        self.setPen(self.parentItem().getEdgeResizingHandleHoverPen())
        
    def hoverLeaveEvent(self, event):
        self.setPen(self.parentItem().getEdgeResizingHandleHiddenPen())
        
        super(EdgeResizingHandle, self).hoverLeaveEvent(event)

class TopEdgeResizingHandle(EdgeResizingHandle):
    def __init__(self, parent):
        super(TopEdgeResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeVerCursor)
        
    def itemChange(self, change, value):
        ret = super(TopEdgeResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(0, delta, 0, 0)

            return QPointF(self.pos().x(), dy1 + self.pos().y())
            
        return ret  

    def scaleChanged(self, sx, sy):
        super(TopEdgeResizingHandle, self).scaleChanged(sx, sy)

        transform = self.transform()
        transform = QTransform(1.0, transform.m12(), transform.m13(),
                               transform.m21(), 1.0 / sy, transform.m23(),
                               transform.m31(), transform.m32(), transform.m33())
        self.setTransform(transform)

class BottomEdgeResizingHandle(EdgeResizingHandle):
    def __init__(self, parent):
        super(BottomEdgeResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeVerCursor)
        
    def itemChange(self, change, value):
        ret = super(BottomEdgeResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(0, 0, 0, delta)
            
            return QPointF(self.pos().x(), dy2 + self.pos().y())
            
        return ret

    def scaleChanged(self, sx, sy):
        super(BottomEdgeResizingHandle, self).scaleChanged(sx, sy)

        transform = self.transform()
        transform = QTransform(1.0, transform.m12(), transform.m13(),
                               transform.m21(), 1.0 / sy, transform.m23(),
                               transform.m31(), transform.m32(), transform.m33())
        self.setTransform(transform)

class LeftEdgeResizingHandle(EdgeResizingHandle):
    def __init__(self, parent):
        super(LeftEdgeResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeHorCursor)
        
    def itemChange(self, change, value):
        ret = super(LeftEdgeResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta = value.x() - self.pos().x()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(delta, 0, 0, 0)
            
            return QPointF(dx1 + self.pos().x(), self.pos().y())
            
        return ret

    def scaleChanged(self, sx, sy):
        super(LeftEdgeResizingHandle, self).scaleChanged(sx, sy)

        transform = self.transform()
        transform = QTransform(1.0 / sx, transform.m12(), transform.m13(),
                               transform.m21(), 1.0, transform.m23(),
                               transform.m31(), transform.m32(), transform.m33())
        self.setTransform(transform)

class RightEdgeResizingHandle(EdgeResizingHandle):
    def __init__(self, parent):
        super(RightEdgeResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeHorCursor)
        
    def itemChange(self, change, value):
        ret = super(RightEdgeResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta = value.x() - self.pos().x()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(0, 0, delta, 0)
            
            return QPointF(dx2 + self.pos().x(), self.pos().y())
            
        return ret

    def scaleChanged(self, sx, sy):
        super(RightEdgeResizingHandle, self).scaleChanged(sx, sy)

        transform = self.transform()
        transform = QTransform(1.0 / sx, transform.m12(), transform.m13(),
                               transform.m21(), 1.0, transform.m23(),
                               transform.m31(), transform.m32(), transform.m33())
        self.setTransform(transform)

class CornerResizingHandle(ResizingHandle):
    def __init__(self, parent):
        super(CornerResizingHandle, self).__init__(parent)
        
        self.setPen(self.parentItem().getCornerResizingHandleHiddenPen())
        self.setFlags(self.flags() |
                      QGraphicsItem.ItemIgnoresTransformations)
        
        self.setZValue(1)

    def counterScale(self):
        x, y = self.getCounteringScale()
        
        self.setScale(x, y)

    def hoverEnterEvent(self, event):
        super(CornerResizingHandle, self).hoverEnterEvent(event)
        
        self.setPen(self.parentItem().getCornerResizingHandleHoverPen())
        
    def hoverLeaveEvent(self, event):
        self.setPen(self.parentItem().getCornerResizingHandleHiddenPen())
        
        super(CornerResizingHandle, self).hoverLeaveEvent(event)

class TopRightCornerResizingHandle(CornerResizingHandle):
    def __init__(self, parent):
        super(TopRightCornerResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeBDiagCursor)
        
    def itemChange(self, change, value):
        ret = super(TopRightCornerResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta_x = value.x() - self.pos().x()
            delta_y = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(0, delta_y, delta_x, 0)

            return QPointF(dx2 + self.pos().x(), dy1 + self.pos().y())
            
        return ret  

class BottomRightCornerResizingHandle(CornerResizingHandle):
    def __init__(self, parent):
        super(BottomRightCornerResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeFDiagCursor)
        
    def itemChange(self, change, value):
        ret = super(BottomRightCornerResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta_x = value.x() - self.pos().x()
            delta_y = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(0, 0, delta_x, delta_y)
            
            return QPointF(dx2 + self.pos().x(), dy2 + self.pos().y())
            
        return ret 

class BottomLeftCornerResizingHandle(CornerResizingHandle):
    def __init__(self, parent):
        super(BottomLeftCornerResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeBDiagCursor)
        
    def itemChange(self, change, value):
        ret = super(BottomLeftCornerResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta_x = value.x() - self.pos().x()
            delta_y = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(delta_x, 0, 0, delta_y)
            
            return QPointF(dx1 + self.pos().x(), dy2 + self.pos().y())
            
        return ret

class TopLeftCornerResizingHandle(CornerResizingHandle):
    def __init__(self, parent):
        super(TopLeftCornerResizingHandle, self).__init__(parent)
        
        self.setCursor(Qt.SizeFDiagCursor)
        
    def itemChange(self, change, value):
        ret = super(TopLeftCornerResizingHandle, self).itemChange(change, value)

        if change == QGraphicsItem.ItemPositionChange and not self.ignoreGeometryChanges:
            delta_x = value.x() - self.pos().x()
            delta_y = value.y() - self.pos().y()
            dx1, dy1, dx2, dy2 = self.adjustParentRect(delta_x, delta_y, 0, 0)
            
            return QPointF(dx1 + self.pos().x(), dy1 + self.pos().y())
            
        return ret

class ResizableGraphicsRectItem(QGraphicsRectItem):
    def __init__(self, parentItem = None):
        super(ResizableGraphicsRectItem, self).__init__(parentItem)
        
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setAcceptsHoverEvents(True)
        self.mouseOver = False
        
        self.topEdgeHandle = TopEdgeResizingHandle(self)
        self.bottomEdgeHandle = BottomEdgeResizingHandle(self)
        self.leftEdgeHandle = LeftEdgeResizingHandle(self)
        self.rightEdgeHandle = RightEdgeResizingHandle(self)
        
        self.topRightCornerHandle = TopRightCornerResizingHandle(self)
        self.bottomRightCornerHandle = BottomRightCornerResizingHandle(self)
        self.bottomLeftCornerHandle = BottomLeftCornerResizingHandle(self)
        self.topLeftCornerHandle = TopLeftCornerResizingHandle(self)
        
        self.handlesDirty = True
        self.currentScaleX = 1
        self.currentScaleY = 1
        self.resizeInProgress = False
        
        self.hideAllHandles()
        
        self.setOuterHandleSize(20)
        self.setInnerHandleSize(15)
    
        self.setCursor(Qt.ArrowCursor)
        self.setPen(self.getNormalPen())
    
    def getMinSize(self):
        ret = QSizeF(1, 1)
        
        return ret
        
    def getMaxSize(self):
        return None
        
    def getNormalPen(self):
        ret = QPen()
        ret.setColor(QColor(255, 255, 255, 255))
        ret.setStyle(Qt.DotLine)
        
        return ret
    
    def getHoverPen(self):
        ret = QPen()
        ret.setColor(QColor(0, 255, 255, 255))
        
        return ret
    
    def getPenWhileResizing(self):
        ret = QPen(QColor(255, 0, 255, 255))
        
        return ret
    
    def getEdgeResizingHandleHoverPen(self):
        ret = QPen()
        ret.setColor(QColor(0, 255, 255, 255))
        ret.setWidth(2)
        ret.setCosmetic(True)
        
        return ret
    
    def getEdgeResizingHandleHiddenPen(self):
        ret = QPen()
        ret.setColor(Qt.transparent)
        
        return ret
    
    def getCornerResizingHandleHoverPen(self):
        ret = QPen()
        ret.setColor(QColor(0, 255, 255, 255))
        ret.setWidth(2)
        ret.setCosmetic(True)
        
        return ret    
    
    def getCornerResizingHandleHiddenPen(self):
        ret = QPen()
        ret.setColor(Qt.transparent)
        
        return ret
    
    def setOuterHandleSize(self, size):
        self.outerHandleSize = size
        self.handlesDirty = True
        
    def setInnerHandleSize(self, size):
        self.innerHandleSize = size
        self.handlesDirty = True
        
    def setRect(self, rect):
        super(ResizableGraphicsRectItem, self).setRect(rect)

        self.handlesDirty = True
        self.ensureHandlesUpdated()
        
    def constrainResizeRect(self, rect):
        minSize = self.getMinSize()
        maxSize = self.getMaxSize()
        
        if minSize:
            minRect = QRectF(rect.center() - QPointF(0.5 * minSize.width(), 0.5 * minSize.height()), minSize)
            rect = rect.united(minRect)
        if maxSize:
            maxRect = QRectF(rect.center() - QPointF(0.5 * maxSize.width(), 0.5 * maxSize.height()), maxSize)
            rect.intersected(maxRect)
            
        return rect
        
    def hideAllHandles(self, excluding = None):
        for item in self.childItems():
            if isinstance(item, ResizingHandle) and item is not excluding:
                if isinstance(item, EdgeResizingHandle):
                    item.setPen(self.getEdgeResizingHandleHiddenPen())
                    
                elif isinstance(item, CornerResizingHandle):
                    item.setPen(self.getCornerResizingHandleHiddenPen())
    
    def unselectAllHandles(self):
        for item in self.childItems():
            if isinstance(item, ResizingHandle):
                item.setSelected(False)
        
    def ensureHandlesUpdated(self):        
        if self.handlesDirty and not self.resizeInProgress:
            self.updateHandles()
        
    def absoluteXToRelative(self, value, transform):
            x_scale = transform.m11()

            # this works in this special case, not in generic case!
            # I would have to undo rotation for this to work generically            
            return value / x_scale if x_scale != 0 else 1
    
    def absoluteYToRelative(self, value, transform):
            y_scale = transform.m22()
            
            # this works in this special case, not in generic case!
            # I would have to undo rotation for this to work generically   
            return value / y_scale if y_scale != 0 else 1
    
    def updateHandles(self):
        """Updates all the handles according to geometry"""
        
        absoluteWidth = self.currentScaleX * self.rect().width()
        absoluteHeight = self.currentScaleY * self.rect().height()
        
        if absoluteWidth < 4 * self.outerHandleSize or absoluteHeight < 4 * self.outerHandleSize:
            self.topEdgeHandle.ignoreGeometryChanges = True
            self.topEdgeHandle.setPos(0, 0)
            self.topEdgeHandle.setRect(0, -self.innerHandleSize,
                                       self.rect().width(),
                                       self.innerHandleSize)
            self.topEdgeHandle.ignoreGeometryChanges = False
            
            self.bottomEdgeHandle.ignoreGeometryChanges = True
            self.bottomEdgeHandle.setPos(0, self.rect().height())
            self.bottomEdgeHandle.setRect(0, 0,
                                       self.rect().width(),
                                       self.innerHandleSize)
            self.bottomEdgeHandle.ignoreGeometryChanges = False
            
            self.leftEdgeHandle.ignoreGeometryChanges = True
            self.leftEdgeHandle.setPos(0, 0)
            self.leftEdgeHandle.setRect(-self.innerHandleSize, 0,
                                       self.innerHandleSize,
                                       self.rect().height())
            self.leftEdgeHandle.ignoreGeometryChanges = False
            
            self.rightEdgeHandle.ignoreGeometryChanges = True
            self.rightEdgeHandle.setPos(QPointF(self.rect().width(), 0))
            self.rightEdgeHandle.setRect(0, 0,
                                       self.innerHandleSize,
                                       self.rect().height())
            self.rightEdgeHandle.ignoreGeometryChanges = False
            
            self.topRightCornerHandle.ignoreGeometryChanges = True
            self.topRightCornerHandle.setPos(self.rect().width(), 0)
            self.topRightCornerHandle.setRect(0, -self.innerHandleSize,
                                       self.innerHandleSize,
                                       self.innerHandleSize)
            self.topRightCornerHandle.ignoreGeometryChanges = False

            self.bottomRightCornerHandle.ignoreGeometryChanges = True
            self.bottomRightCornerHandle.setPos(self.rect().width(), self.rect().height())
            self.bottomRightCornerHandle.setRect(0, 0,
                                       self.innerHandleSize,
                                       self.innerHandleSize)
            self.bottomRightCornerHandle.ignoreGeometryChanges = False
            
            self.bottomLeftCornerHandle.ignoreGeometryChanges = True
            self.bottomLeftCornerHandle.setPos(0, self.rect().height())
            self.bottomLeftCornerHandle.setRect(-self.innerHandleSize, 0,
                                       self.innerHandleSize,
                                       self.innerHandleSize)
            self.bottomLeftCornerHandle.ignoreGeometryChanges = False

            self.topLeftCornerHandle.ignoreGeometryChanges = True
            self.topLeftCornerHandle.setPos(0, 0)
            self.topLeftCornerHandle.setRect(-self.innerHandleSize, -self.innerHandleSize,
                                       self.innerHandleSize,
                                       self.innerHandleSize)
            self.topLeftCornerHandle.ignoreGeometryChanges = False
            
        else:
            self.topEdgeHandle.ignoreGeometryChanges = True
            self.topEdgeHandle.setPos(0, 0)
            self.topEdgeHandle.setRect(0, 0,
                                       self.rect().width(),
                                       self.outerHandleSize)
            self.topEdgeHandle.ignoreGeometryChanges = False
            
            self.bottomEdgeHandle.ignoreGeometryChanges = True
            self.bottomEdgeHandle.setPos(0, self.rect().height())
            self.bottomEdgeHandle.setRect(0, -self.outerHandleSize,
                                       self.rect().width(),
                                       self.outerHandleSize)
            self.bottomEdgeHandle.ignoreGeometryChanges = False
            
            self.leftEdgeHandle.ignoreGeometryChanges = True
            self.leftEdgeHandle.setPos(QPointF(0, 0))
            self.leftEdgeHandle.setRect(0, 0,
                                       self.outerHandleSize,
                                       self.rect().height())
            self.leftEdgeHandle.ignoreGeometryChanges = False
            
            self.rightEdgeHandle.ignoreGeometryChanges = True
            self.rightEdgeHandle.setPos(QPointF(self.rect().width(), 0))
            self.rightEdgeHandle.setRect(-self.outerHandleSize, 0,
                                       self.outerHandleSize,
                                       self.rect().height())
            self.rightEdgeHandle.ignoreGeometryChanges = False
            
            self.topRightCornerHandle.ignoreGeometryChanges = True
            self.topRightCornerHandle.setPos(self.rect().width(), 0)
            self.topRightCornerHandle.setRect(-self.outerHandleSize, 0,
                                       self.outerHandleSize,
                                       self.outerHandleSize)
            self.topRightCornerHandle.ignoreGeometryChanges = False
            
            self.bottomRightCornerHandle.ignoreGeometryChanges = True
            self.bottomRightCornerHandle.setPos(self.rect().width(), self.rect().height())
            self.bottomRightCornerHandle.setRect(-self.outerHandleSize, -self.outerHandleSize,
                                       self.outerHandleSize,
                                       self.outerHandleSize)
            self.bottomRightCornerHandle.ignoreGeometryChanges = False
            
            self.bottomLeftCornerHandle.ignoreGeometryChanges = True
            self.bottomLeftCornerHandle.setPos(0, self.rect().height())
            self.bottomLeftCornerHandle.setRect(0, -self.outerHandleSize,
                                       self.outerHandleSize,
                                       self.outerHandleSize)
            self.bottomLeftCornerHandle.ignoreGeometryChanges = False
            
            self.topLeftCornerHandle.ignoreGeometryChanges = True
            self.topLeftCornerHandle.setPos(0, 0)
            self.topLeftCornerHandle.setRect(0, 0,
                                       self.outerHandleSize,
                                       self.outerHandleSize)
            self.topLeftCornerHandle.ignoreGeometryChanges = False
        
        self.handlesDirty = False
    
    def notifyResizeStarted(self):
        pass
    
    def notifyResizeProgress(self, newPos, newRect):
        pass
        
    def notifyResizeFinished(self, newPos, newRect):
        self.setRect(newRect)
        self.setPos(newPos)
        
    def scaleChanged(self, sx, sy):
        self.currentScaleX = sx
        self.currentScaleY = sy
        
        for childItem in self.childItems():
            if isinstance(childItem, ResizingHandle):
                childItem.scaleChanged(sx, sy)
                
            elif isinstance(childItem, ResizableGraphicsRectItem):
                childItem.scaleChanged(sx, sy)
                
        self.handlesDirty = True
        self.ensureHandlesUpdated()
        
    def itemChange(self, change, value):
        ret = super(ResizableGraphicsRectItem, self).itemChange(change, value)
        
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.unselectAllHandles()
            else:
                self.hideAllHandles()
        
        return ret
        
    def hoverEnterEvent(self, event):
        super(ResizableGraphicsRectItem, self).hoverEnterEvent(event)
        
        self.setPen(self.getHoverPen())
        self.mouseOver = True
        
    def hoverLeaveEvent(self, event):
        self.mouseOver = False
        self.setPen(self.getNormalPen())
    
        super(ResizableGraphicsRectItem, self).hoverLeaveEvent(event)
        