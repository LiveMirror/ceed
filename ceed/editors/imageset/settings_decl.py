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

def declare(settings):
    category = settings.createCategory(name = "imageset", label = "Imageset editing")

    visual = category.createSection(name = "visual", label = "Visual editing")

    visual.createEntry(name = "overlay_image_labels", type = bool, label = "Show overlay labels of images",
                    help = "Show overlay labels of images.",
                    defaultValue = True, widgetHint = "checkbox",
                    sortingWeight = 1)
    
    visual.createEntry(name = "partial_updates", type = bool, label = "Use partial drawing updates",
                    help = "Will use partial 2D updates using accelerated 2D machinery. The performance of this is very dependent on your platform and hardware. MacOSX handles partial updates much better than Linux it seems. If you have a very good GPU, don't tick this.",
                    defaultValue = False, widgetHint = "checkbox", changeRequiresRestart = True,
                    sortingWeight = 2)