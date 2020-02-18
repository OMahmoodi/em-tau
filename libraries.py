!pip install geosoft==9.2
!pip install geosoft --upgrade
import geosoft
import geosoft.gxpy.gx as gx
gxp = gx.GXpy()
print(gxp.gid)
print(gxp.entitlements)
