/*
   CEED - Unified CEGUI asset editor

   Copyright (C) 2011-2017   Martin Preisler <martin@preisler.me>
                             and contributing authors (see AUTHORS file)

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef CEED_cegui_ceguitype_editor_properties_
#define CEED_cegui_ceguitype_editor_properties_

#include "CEEDBase.h"

"""Lightweight CEGUI property value types that can parse and write text."""

from ceguitypes import *


/*!
\brief BaseProperty

Base class for all Property types.

    Note that, by default, it expects the components to map
    directly to an attribute of it's value; with the first letter in lower case.

    For example the UDimProperty has two components, 'Scale' and 'Offset' and
    it also uses the UDim type that has the 'scale' and 'offset' attribute values.

*/
class BaseProperty : public properties.Property


    def createComponents(self):
        super(BaseProperty, self).createComponents()

    def getComponents(self):
        return self.components

    @classmethod
    def getAttrName(cls, componentName):
        """Get the attribute name from the component name."""
        return componentName[:1].lower() + componentName[1:]

    def updateComponents(self, reason=properties.Property.ChangeValueReason.Unknown):
        components = self.getComponents()
        if components is not None:
            for compName, compValue in components.items():
                # set component value from attribute value
                compValue.setValue(getattr(self.value, self.getAttrName(compName)), reason)

    def componentValueChanged(self, component, reason):
        # set attribute value from component value
        setattr(self.value, self.getAttrName(component.name), component.value)
        # trigger our value changed event directly because
        # we didn't call 'setValue()' to do it for us.
        self.valueChanged.trigger(self, properties.Property.ChangeValueReason.ComponentValueChanged)


/*!
\brief UDimProperty

Property for UDim values.
*/
class UDimProperty : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()
        self.components["Scale"] = properties.Property(name="Scale", value=self.value.scale, defaultValue=self.defaultValue.scale,
                                                       readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Offset"] = properties.Property(name="Offset", value=self.value.offset, defaultValue=self.defaultValue.offset,
                                                        readOnly=self.readOnly, editorOptions=self.editorOptions)

        super(UDimProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return UDim.tryParse(strValue)


/*!
\brief USizeProperty

Property for USize values.
*/
class USizeProperty : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()
        self.components["Width"] = UDimProperty(name="Width", value=self.value.width, defaultValue=self.defaultValue.width,
                                                readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Height"] = UDimProperty(name="Height", value=self.value.height, defaultValue=self.defaultValue.height,
                                                 readOnly=self.readOnly, editorOptions=self.editorOptions)

        super(USizeProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return USize.tryParse(strValue)


/*!
\brief UVector2Property

Property for UVector2 values.
*/
class UVector2Property : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()
        self.components["X"] = UDimProperty(name="X", value=self.value.x, defaultValue=self.defaultValue.x,
                                            readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Y"] = UDimProperty(name="Y", value=self.value.y, defaultValue=self.defaultValue.y,
                                            readOnly=self.readOnly, editorOptions=self.editorOptions)

        super(UVector2Property, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return UVector2.tryParse(strValue)


/*!
\brief URectProperty

Property for URect values.
*/
class URectProperty : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()
        self.components["Left"] = UDimProperty(name="Left", value=self.value.left, defaultValue=self.defaultValue.left,
                                               readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Top"] = UDimProperty(name="Top", value=self.value.top, defaultValue=self.defaultValue.top,
                                              readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Right"] = UDimProperty(name="Right", value=self.value.right, defaultValue=self.defaultValue.right,
                                                readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Bottom"] = UDimProperty(name="Bottom", value=self.value.bottom, defaultValue=self.defaultValue.bottom,
                                                 readOnly=self.readOnly, editorOptions=self.editorOptions)

        super(URectProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return URect.tryParse(strValue)


/*!
\brief QuaternionProperty

Property for Quaternion values.
*/
class QuaternionProperty : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()

        # TODO: Set min/max/step for W, X, Y, Z. See how it's done on XYZRotationProperty.
        self.components["W"] = properties.Property(name="W", value=self.value.w, defaultValue=self.defaultValue.w,
                                                   readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["X"] = properties.Property(name="X", value=self.value.x, defaultValue=self.defaultValue.x,
                                                   readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Y"] = properties.Property(name="Y", value=self.value.y, defaultValue=self.defaultValue.y,
                                                   readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["Z"] = properties.Property(name="Z", value=self.value.z, defaultValue=self.defaultValue.z,
                                                   readOnly=self.readOnly, editorOptions=self.editorOptions)

        self.components["Degrees"] = XYZRotationProperty(name="Degrees",
                                                         value=XYZRotation.fromQuaternion(self.value),
                                                         defaultValue=XYZRotation.fromQuaternion(self.defaultValue),
                                                         readOnly=self.readOnly,
                                                         editorOptions=self.editorOptions)

        super(QuaternionProperty, self).createComponents()

    def updateComponents(self, reason=properties.Property.ChangeValueReason.Unknown):
        components = self.getComponents()
        if components is not None:
            components["W"].setValue(self.value.w, reason)
            components["X"].setValue(self.value.x, reason)
            components["Y"].setValue(self.value.y, reason)
            components["Z"].setValue(self.value.z, reason)
            components["Degrees"].setValue(XYZRotation.fromQuaternion(self.value), reason)

    def componentValueChanged(self, component, reason):
        if component.name == "Degrees":
            (wv, xv, yv, zv) = Quaternion.convertEulerDegreesToQuaternion(component.value.x, component.value.y, component.value.z)
            self.components["W"].setValue(wv)
            self.components["X"].setValue(xv)
            self.components["Y"].setValue(yv)
            self.components["Z"].setValue(zv)
            self.valueChanged.trigger(self, properties.Property.ChangeValueReason.ComponentValueChanged)
        else:
            super(QuaternionProperty, self).componentValueChanged(component, reason)

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return Quaternion.tryParse(strValue)


/*!
\brief XYZRotationProperty

Property for XYZRotation values.
*/
class XYZRotationProperty : public BaseProperty


    def createComponents(self):
        editorOptions = {"numeric": {"min": -360, "max": 360, "wrapping": True}}

        self.components = OrderedDict()

        self.components["X"] = properties.Property(name="X", value=self.value.x, defaultValue=self.defaultValue.x,
                                                   readOnly=self.readOnly, editorOptions=editorOptions)
        self.components["Y"] = properties.Property(name="Y", value=self.value.y, defaultValue=self.defaultValue.y,
                                                   readOnly=self.readOnly, editorOptions=editorOptions)
        self.components["Z"] = properties.Property(name="Z", value=self.value.z, defaultValue=self.defaultValue.z,
                                                   readOnly=self.readOnly, editorOptions=editorOptions)

        super(XYZRotationProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return XYZRotation.tryParse(strValue)


/*!
\brief ColourProperty

Property for Colour values.
*/
class ColourProperty : public BaseProperty


    def createComponents(self):
        editorOptions = {"numeric": {"min": 0, "max": 255}}

        self.components = OrderedDict()

        self.components["Alpha"] = properties.Property(name="Alpha", value=self.value.alpha, defaultValue=self.defaultValue.alpha,
                                                       readOnly=self.readOnly, editorOptions=editorOptions)
        self.components["Red"] = properties.Property(name="Red", value=self.value.red, defaultValue=self.defaultValue.red,
                                                     readOnly=self.readOnly, editorOptions=editorOptions)
        self.components["Green"] = properties.Property(name="Green", value=self.value.green, defaultValue=self.defaultValue.green,
                                                       readOnly=self.readOnly, editorOptions=editorOptions)
        self.components["Blue"] = properties.Property(name="Blue", value=self.value.blue, defaultValue=self.defaultValue.blue,
                                                      readOnly=self.readOnly, editorOptions=editorOptions)

        super(ColourProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return Colour.tryParse(strValue)


/*!
\brief ColourRectProperty

Property for ColourRect values.
*/
class ColourRectProperty : public BaseProperty


    def createComponents(self):
        self.components = OrderedDict()

        self.components["TopLeft"] = ColourProperty(name="TopLeft", value=self.value.topLeft, defaultValue=self.defaultValue.topLeft,
                                                    readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["TopRight"] = ColourProperty(name="TopRight", value=self.value.topRight, defaultValue=self.defaultValue.topRight,
                                                     readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["BottomLeft"] = ColourProperty(name="BottomLeft", value=self.value.bottomLeft, defaultValue=self.defaultValue.bottomLeft,
                                                       readOnly=self.readOnly, editorOptions=self.editorOptions)
        self.components["BottomRight"] = ColourProperty(name="BottomRight", value=self.value.bottomRight, defaultValue=self.defaultValue.bottomRight,
                                                        readOnly=self.readOnly, editorOptions=self.editorOptions)

        super(ColourRectProperty, self).createComponents()

    def isStringRepresentationEditable(self):
        return True

    def tryParse(self, strValue):
        return ColourRect.tryParse(strValue)
#endif
