*************************************************************************
*                                                                       *
*                         dxfstructure 0.3                              *
*             Structural engineering dxf drawing system                 *
*                                                                       *
*                        (c) 2017-2018 Lukasz Laba                      *
*                                                                       *
*************************************************************************

Dxfstructure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Dxfstructure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

-------------------------------------------------------------------------
* Visible changes:
-------------------------------------------------------------------------
  dxfstructure 0.3.1(beta)
  - check for quite similar bars number option added
  - color system updated
  - bar schedule format updated - shape column added
  - language version option added
  - in meter length element and bar available
  - possibility to define bar quantity as expression e.g 2*2#12-[4]
  - bar with forced straight shape in schedule
  - full backward compatibility
  dxfstructure 0.2.4(alpha)
  - updated to ezdxf 0.8.8
  - full backward compatibility
  dxfstructure 0.2.3(alpha)
  - profil anotation syntax changed to  4x(1)-IPE 300-1200-S235
  - full backward compatibility
  dxfstructure 0.2.2(alpha)
  - bar shape anotation changed to look like e.g. [1] - #12 L=2120
  - steel setion database list updated
  dxfstructure 0.2.1(alpha)
  - main features for steel implemented
  - command feature added
  dxfstructure 0.1(alpha)
  - main features for concrete implemented
  dxfstructure 0.0.2 (alpha)
  - first PyPI version
-------------------------------------------------------------------------
* Prerequisites:
-------------------------------------------------------------------------
  Python 2.7.
  Non-standard Python library needed:
  - strupy
  - ezdxf
  - tabulate
  - strupy
  - mistune
-------------------------------------------------------------------------
* To install dxfstructure:
-------------------------------------------------------------------------
  After the Python and needed libraries  was installed use pip by typing:
  "pip install DxfStructure"
  There is install instruction on project website.
  To run dxfstructure GUI execute dxfstructure.py from installed dxfstructure
  package folder - probably it is "C:\Python27\Lib\site-packages\dxfstructure"
  For easy run make shortcut on your system pulpit to this file.
  https://bitbucket.org/lukaszlaba/dxfstructure/wiki/installing
  Windows (7) and Linux (xubuntu, fedora) tested.
-------------------------------------------------------------------------
* Other information :
-------------------------------------------------------------------------
  - Project website: 
    https://bitbucket.org/lukaszlaba/dxfstructure/wiki/Home
    https://bitbucket.org/struthonteam/struthon
  - E-mail : lukaszlab@o2.pl